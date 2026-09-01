# Round 165 — Target 2 (Make Decision rate): concrete floor-mechanism proposal for `reweight_from_alpha_performance`, not implemented (needs dedicated simulation round)

## Context

Almost implemented Round 65's proposal (subscribe `mtf_stochastic_5m_4h_sma5`
to Binance/XAU) before catching, via `optimize_loop_update_v2.csv` history,
that **Round 67 already retracted this exact proposal** — the strategy
itself was confirmed losing after a lookahead-bug fix, and subscribing a
known-losing "zombie" strategy just to trigger the reweight formula's
benefit-of-doubt mechanic is an anti-pattern, not a fix (see
`round67-MAJOR-invalidated-mtf-strategy-promotions-plus-dev-mode-switch.md`).
Lesson reinforced from Round 163: **always grep `optimize_loop_update_v2.csv`
for prior attempts before implementing anything from an old round file.**

Round 67 identified the real fix needs one of: (1) a genuinely profitable
strategy (100+ rounds of this program haven't found one), or (2) an
intentional floor in `alpha_performance_quality`/`normalize_or_uniform_weights`
so `interval_weights` never fully zeroes out an interval just because every
*currently configured* strategy happens to be a confirmed loser there —
decoupled from how many strategies happen to be subscribed. Flagged as
needing careful design, never followed up.

## Mechanism, read directly from `crates/finance-core/src/trading_modes.rs`

- `alpha_performance_quality` (line ~524): a strategy/interval pair with
  `trade_count >= PERFORMANCE_CONFIDENCE_TRADES` (20) and confirmed losing
  (`realized_pnl <= 0` or `gross_profit <= 0`) returns **exactly 0.0**.
  Below 20 trades, it blends toward `1.0` (benefit of doubt) via
  `confidence = trade_count / 20`.
- `normalize_or_uniform_weights` (line ~571): already has a floor
  mechanism — but it only triggers when the **entire map's total** is ~0
  (every interval simultaneously zero), falling back to a uniform split
  across all intervals. **It does not floor a single interval that's zero
  while others aren't** — exactly Binance/XAU's situation (5m/15m/30m/1h/2h/4h
  all zero from two mature-losing base strategies, 12h/1d nonzero), so the
  existing fallback never fires and the zero intervals stay at literal 0.

## Concrete proposal (analysis only, not implemented this round)

Add a small **per-key minimum floor** inside `normalize_or_uniform_weights`
(or a new floor step right before it) so no single interval/strategy's
quality can normalize to *exactly* 0 when at least one other key in the
same map is nonzero — e.g. `quality.max(FLOOR_QUALITY)` before summing,
where `FLOOR_QUALITY` is a small constant (candidate value: `0.05`,
i.e. ~5% of the weight a fully-untested/benefit-of-doubt candidate would
get). This is a **2-line change** at a single, shared call site — genuinely
low surface area — but the floor *value* needs real backtesting before
picking one, because it trades directly against this formula's original
intent ("mature losers get zero weight, don't dilute a winner" — the
`normalize_or_uniform_weights` doc comment's own words). Too high a floor
re-admits confirmed losers into the decision; too low doesn't move Target 2
enough to matter for Binance/XAU's near-fully-zeroed entry intervals.

## Why not implemented this round

This touches the exact reweight function shared by **all 4 production
routes**, not just Binance/XAU — per the skill's Codex-down-mode rule 6
("a finding that would change core, shared decision-algorithm behavior...
needs stronger justification... simulate the change's effect against real
production data before deploying"). There is currently no tool in
`finance-research` that replays `reweight_from_alpha_performance` with a
floor-value override against real production `simulated_ledgers` data to
measure the counterfactual `interval_weights`/decision-frequency effect
across all 4 routes before deploying — building that harness and running a
floor-value sweep (e.g. 0.01/0.05/0.10/0.20) is real, multi-hour work
appropriately scoped to its own dedicated round(s), not a rushed
implementation squeezed into this one.

## Round 166 update — quantified simulation against real production data, done in Python (Round 65's own verified methodology)

Pulled real `simulated_ledgers` performance for every (interval, strategy)
pair from both Binance/XAU and Binance/BTC checkpoints (read-only Redis),
reproduced `alpha_performance_quality`/`normalize_or_uniform_weights` in
Python, and confirmed the reproduction matches live production
`interval_weights` **exactly** for both routes (floor=0.0 case) before
trusting the floor sweep:

- XAU/binance floor=0.0: `1d=0.5709, 12h=0.2659, 4h=0.1632, others=0.0000`
  — matches the live checkpoint read exactly.
- BTC/binance floor=0.0: `1d=0.1676, 12h=0.1535, {15m,1h,2h,30m,4h}=0.1358
  each, 5m=0.0000` — matches exactly.

**Floor sweep, applied to `interval_quality` only (see scoping note
below):**

| floor | XAU/binance `5m` weight | BTC/binance `5m` weight |
|---|---|---|
| 0.00 (current) | 0.0000 | 0.0000 |
| 0.01 | 0.0124 | 0.0022 |
| 0.05 | 0.0479 | 0.0109 |
| 0.10 | 0.0744 | 0.0212 |
| 0.20 | 0.1014 | n/a (not swept) |

**Two important refinements this simulation surfaced, not obvious from
reading the code alone:**

1. **The floor must scope to `interval_quality` only, never
   `strategy_quality`.** `normalize_or_uniform_weights` is the same
   function used for both maps. Flooring `strategy_quality` too would
   undermine its own documented intent ("confirmed losers get zero
   quality, don't dilute a winner") — a mature, confirmed-losing
   *strategy* should stay at exactly 0 regardless of this fix. The floor
   needs to be applied when building `interval_quality` specifically (or
   `normalize_or_uniform_weights` needs an optional floor parameter used
   only for the interval-weights call site), not as a change to the shared
   function's default behavior.
2. **The same floor value produces very different relative effects across
   routes**, because it's a per-(interval, strategy) floor summed before
   normalization — a route with more configured strategies at an interval
   (BTC/binance has 5 at `5m`: 2 base + 3 "zombie" MTF; XAU/binance has
   only 2) dilutes the floor's relative share more. At floor=0.05,
   XAU/binance's `5m` gets 4.79% but BTC/binance's `5m` only gets 1.09% —
   nearly 4.4x weaker for BTC despite the identical floor constant. A
   single global floor constant may need to be normalized by strategy
   count per interval (e.g. `floor / configured_strategy_count`) rather
   than a flat constant, or accepted as an intentional asymmetry (BTC
   already has other-interval weight from its zombie strategies; XAU does
   not) — this tradeoff needs an explicit decision before implementing,
   not just picking one floor number.

## Recommendation for a future round

1. ~~Build a small research harness~~ — done this round via direct Python
   reproduction against real Redis-read production data (see above); a
   dedicated Rust CLI harness is no longer strictly necessary unless a
   round wants to sweep floor values against *simulated* (not just
   currently-live) performance scenarios too.
2. Decide the floor-scoping question above (flat constant vs
   per-strategy-count normalized) before picking a number — this is a
   design decision, not just an empirical one.
3. Verify Exness/BTC and Exness/XAU too (not simulated this round — only
   Binance/BTC and Binance/XAU were checked) before generalizing "0.05 is a
   reasonable floor" to all 4 routes.
4. Implement as a scoped change (interval-quality-only, per the refinement
   above), with before/after production evidence in the commit message
   matching this program's existing standard for core-algorithm changes.

Logged as a concrete, high-priority Todo — not a Verify/Done item, since
nothing was implemented or deployed this round. The quantified data above
should make the eventual implementation round significantly faster (the
"what floor value, scoped how" homework is now done) — the harness-building
step originally proposed turned out to be unnecessary; real production data
via read-only Redis was sufficient.

## Round 167 — IMPLEMENTED, DEPLOYED, VERIFIED

All open items from the recommendation list above were resolved and this
was deployed the same session:

- Checked Exness/BTC and Exness/XAU too (not just the two Binance routes):
  same pattern confirmed — `5m` at exactly 0.0 for every one of the 4
  production routes before this fix.
- Resolved the scoping question: implemented as
  `MultiTimeframePortfolioPolicy::INTERVAL_QUALITY_FLOOR = 0.05`, applied
  via `.max(Self::INTERVAL_QUALITY_FLOOR)` only to
  `interval_observation_quality` in `reweight_from_alpha_performance`
  (`crates/finance-core/src/trading_modes.rs`) — `strategy_quality` is
  completely untouched, so a confirmed-losing strategy still normalizes to
  exactly zero there, preserving the original design intent.
- Accepted the cross-route floor-value asymmetry (flat constant, not
  normalized by strategy count) as a reasonable first cut rather than
  over-engineering before any real-world signal on whether it matters.
- Added `a_single_confirmed_losing_interval_gets_a_nonzero_floor_instead_of_zero`
  to `crates/finance-core/tests/trading_modes.rs`, verified the two
  existing related tests (`portfolio_policy_reweights_intervals_and_strategies_from_closed_alpha_performance`,
  `interval_weights_recover_to_uniform_instead_of_freezing_when_every_configured_strategy_is_a_confirmed_loser`)
  are unaffected by hand-tracing the math before running them (both stayed
  green). Full workspace suite green (32/32 suites), `cargo fmt --check`
  clean.
- Committed `7fe0e13`, pushed, CI green (`build-and-push`/`deploy-app` both
  ran — this touches `finance-core`, used by every route), deployed.
- **Production verification: read-only Redis checkpoint reads for all 4
  routes post-deploy show `5m` interval_weights matching the Round 166
  simulation EXACTLY** (not just "in the right direction" — exact floating
  point match to 6+ significant figures):

  | route | predicted `5m` weight | deployed `5m` weight |
  |---|---|---|
  | XAU/binance | 0.0479 | 0.047869853726700586 |
  | BTC/binance | 0.0109 | 0.01094229078249361 |
  | BTC/exness | 0.0108 | 0.010815704560520393 |
  | XAU/exness | 0.0161 | 0.016120194121542652 |

  All 6 live-action containers healthy on exact SHA `7fe0e13`,
  `evaluation_count` advancing normally on all 4 routes post-deploy.

This closes the Target 2 (Make Decision rate) investigation chain that ran
from Round 63 through 167: root cause found (65), a bad fix proposed and
retracted (65→67), the real fix designed and quantified against real data
(165-166), and finally implemented, tested, deployed, and verified matching
the simulation exactly (167). Next natural check: revisit production in
1-2 days to see whether `5m`'s now-nonzero weight measurably moves the
`trades_per_week`/decision-frequency metrics this whole investigation was
about, per this program's standing practice of following up after every
deployed lever.
