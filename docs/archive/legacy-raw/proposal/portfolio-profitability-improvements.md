# Proposal: practices to drive Portfolio toward profitability

Status: proposal, not applied. Written by Claude (system review), for Codex to
prioritize and implement. This is a living document — re-visit and append new
rounds of proposals each time Portfolio's measured performance is checked and
still isn't where it needs to be, rather than replacing it wholesale.

## Where this comes from

Grounded in a fresh read of `finance-live-action`'s trading crates (not
re-derived from memory) plus three existing docs, now archived since all
three shipped (`docs/archive/legacy-raw/archive/closed-2026-08/portfolio-strategy-attribution.md`,
`docs/archive/legacy-raw/archive/closed-2026-08/portfolio-rule-trade-count-imbalance.md`,
`docs/archive/legacy-raw/archive/closed-2026-08/system-review-strategy-optimization.md`). Exact
citations kept inline so this survives code drift better than a narrative
summary would.

## Headline finding: the profitability machinery already exists, it's just not wired in

- Portfolio's live interval/strategy weights are **hardcoded**, not
  performance-driven: `MultiTimeframePortfolioPolicy::survival_first_default`
  (`finance-live-action/crates/finance-core/src/trading_modes.rs:408-441`)
  sets fixed weights per interval (5m:0.08 … 1d:0.10) regardless of which
  intervals or strategies have actually been working.
- A real performance-weighting function already exists —
  `reweight_from_alpha_performance` (`trading_modes.rs:455-491`) — and runs on
  every closed kline (`trading_api.rs:1528-1530` realtime,
  `trading_api.rs:2103-2105` replay), scoring each ledger by
  `win_rate × clamp(profit_factor, 1..3)/3 × (1 − drawdown_ratio)` with a
  20-trade confidence shrinkage. But per
  `docs/archive/legacy-raw/archive/closed-2026-08/system-review-strategy-optimization.md`, its output isn't what
  `survival_first_default`'s constants are built from at the top level — the
  wiring stops short of actually replacing the hardcoded weights in
  production.
- A weighted-decision engine (`PortfolioDecisionPolicy::decide`,
  `trading_modes.rs:267-336`) and a research scoring pipeline
  (`finance-research/src/sweep.rs`) also already exist, plus a CI gate
  (`portfolio-research.yaml`) that asserts a known-losing config gets
  rejected — but none of this reaches the live path either.

**Implication for every proposal below**: before adding new signals/intervals/
rules, it's worth first closing the gap between "the scoring math exists" and
"the scoring math actually decides what's live" — otherwise new inputs just
sit next to `reweight_from_alpha_performance`, unused, the same way the
existing ones do today.

## Prerequisite fixes — do these before trusting any profitability measurement

Two confirmed bugs currently make it impossible to honestly measure whether
Portfolio (or any one of its execution rules) is profitable:

1. **Strategy attribution is destroyed at write time.** Every Portfolio trade
   is recorded with `strategy: "weighted-strategies"` literally
   (`trading_api.rs:737,746`), discarding the real per-strategy contribution
   scores that are computed live (`role_scores`, `trading_modes.rs:747-774`).
   Until this is fixed, "which alpha signal is actually making Portfolio
   money" is unanswerable from the ledger — any signal-level proposal below
   is unverifiable without it.
2. **`risk-2pct` is silently starved by an un-scaled risk cap.** Its notional
   formula (`equity_fraction`-independent: `equity * risk_fraction / stop` ≈
   $40,000 at defaults) blows through the shared
   `PortfolioRiskPolicy::default()` caps (`max_order_notional: $1,000`,
   `max_order_equity_fraction: 0.10`) — only `max_leverage` is overridden per
   rule, not the notional caps. This rule has near-zero trades not because
   it's a bad rule, but because it's rejected before it can execute. Any
   "which sizing rule wins" comparison is invalid while this stands.

Recommended order: fix #1 and #2 first (both are narrow, already root-caused
in the linked docs), get one clean measurement cycle of real per-rule,
per-strategy performance, *then* decide which of the practices below to try
first based on that data rather than guessing.

## Proposed practices, grouped by the categories the user asked for

### 1. New setups (execution rules / position sizing)

- **Per-rule risk caps, not one shared cap.** `PortfolioRiskPolicy` currently
  applies the same `max_order_notional`/`max_order_equity_fraction` to all
  three rules regardless of their sizing formula. Scale the cap to each
  rule's own sizing math (or express the cap itself as an equity fraction
  consistently) so `risk-2pct` gets a fair trial instead of being rejected by
  construction.
- **Try the already-scaffolded but undeployed variants.**
  `finance-research/src/execution_rules.rs:44-88` already defines
  `fixed-atr` and `compounding-atr` candidates (ATR-based stop/take instead of
  the current fixed 0.5%/1.0% fractional stop/take shared by all three live
  rules). Volatility-scaled stops are a standard next step once fixed-fraction
  sizing has a clean baseline — deploy one ATR-based rule alongside the
  existing three and compare on equal footing.
- **A fourth "confidence-scaled" rule**, sized directly off
  `alpha_performance_quality`'s per-scope confidence score (already computed,
  see prerequisite fixes above) rather than a fixed fraction — effectively
  sizing up when the feeding strategies are in a demonstrated good patch and
  down when they aren't, instead of every rule always risking the same
  fraction regardless of current signal quality.

### 2. Interval changes

- **Feed `reweight_from_alpha_performance`'s per-interval scores back into
  `interval_weights`, replacing the hardcoded constants**, rather than
  proposing a specific new interval mix. The current 5m:0.08…1d:0.10 split in
  `survival_first_default` was presumably reasonable when first set, but
  there's no mechanism keeping it correct as strategies age or market regime
  shifts. This is the single highest-leverage interval change: it turns every
  future interval question into something the system answers from data
  instead of something a human guesses once and never revisits.
- Only after that wiring exists: consider whether `EVALUATED_INTERVALS`
  (`trading_api.rs:34-35`) — currently every finance-mw interval except `1m`
  — should include `1m`. Sub-5-minute noise-vs-signal tradeoffs are
  strategy-dependent; this is a genuine open question, not a known win, and
  should be evaluated with the same weighting framework once it's live rather
  than added speculatively.

### 3. "Model" changes

No ML model exists anywhere in the decision path today (confirmed by direct
grep across both repos' trading code — only a design doc,
`docs/specs/rl-agent-integration-design.md`, references one). Two distinct
things could be meant by "đổi model" here, worth pursuing in this order:

- **Rule-based decision-policy variants first.** `PortfolioDecisionPolicy`
  (`trading_modes.rs:267-336`) is itself swappable — try alternate weighting
  functions (e.g. Kelly-fraction-inspired sizing off the existing quality
  score, or a regime filter that down-weights all signals during confirmed
  high-volatility/low-liquidity windows) before reaching for a trained model.
  This is strictly cheaper to build, test, and explain than an ML model, and
  the existing no-lookahead framework (below) already knows how to validate
  it.
- **A real trained model is a much bigger, separate initiative** — new
  training data pipeline, point-in-time-correct feature engineering, model
  versioning/rollback, and its own no-lookahead guarantees. Worth scoping
  properly as its own proposal once the rule-based system has a clean,
  measured baseline to beat; not a near-term item to bundle into this list.

### 4. New alpha signals

Only 2 strategies exist today — `candle_momentum` and `rsi_mean_reversion`
(`crates/finance-strategy/src/engine.rs:85-94`, configured in
`deployment_rules.rs:118-133`). The `StrategyKind` enum and
`configured_alpha_strategies()` are both structured to accept more without
architecture changes — adding a signal is a legitimately low-friction change
here. Concrete candidates, roughly in order of how differentiated they'd be
from the existing pair (momentum + mean-reversion already cover two classic
archetypes):

- **Volatility breakout** (e.g. Donchian/Bollinger-band breakout) — a third
  archetype distinct from both existing signals, likely to be
  lowly-correlated with them, which is what actually helps
  `reweight_from_alpha_performance`'s ensemble (correlated signals don't add
  much diversification benefit even if each is individually decent).
- **Cross-timeframe confirmation signal** — not a new indicator, but a new
  `StrategyKind` that only fires when 2+ of the 8 `EVALUATED_INTERVALS` agree
  in direction. Cheap to build (reuses existing evidence plumbing), and
  directly exercises the multi-timeframe evidence system that's otherwise
  only consumed by Portfolio's synchronization gate.
- Whatever signal is added, **respect the no-lookahead contract**:
  `NoLookaheadObservation::is_violation` (`trading_modes.rs:564-566`) flags
  any evidence whose `input_at` exceeds the deciding `as_of` timestamp. A new
  signal must ingest with `event_at` no later than the kline close it
  contributes evidence to, or every evaluation using it will start tripping
  the no-lookahead alert (the same class of bug just fixed in the recent
  incident chain — see `raw/handoff_codex.md` Done section, "no-lookahead
  alert" entries).

## Suggested sequencing

1. Fix strategy-attribution write-through and the `risk-2pct` cap (both
   narrow, already root-caused).
2. Run one full measurement cycle with the fix in place — get real per-rule,
   per-strategy win rate / profit factor / drawdown numbers from production,
   not assumptions.
3. Wire `reweight_from_alpha_performance`'s scores into
   `survival_first_default`'s interval/strategy weights, replacing the
   hardcoded constants — highest-leverage single change, makes every
   subsequent change self-correcting instead of another one-off guess.
4. Only then: add the ATR-based/confidence-scaled execution rule, add one new
   alpha signal (volatility breakout is the most differentiated pick), and
   re-measure.
5. Revisit `EVALUATED_INTERVALS` and rule-based decision-policy variants once
   steps 1-4 give a real baseline to compare against. Treat a trained model as
   a separate, later-scoped initiative, not part of this iteration.

## How "until profitable" gets tracked

This proposal can't itself prove profitability — that requires implementing,
deploying, and measuring. The practice going forward: each time this file is
revisited (loop cycle), pull the latest Portfolio win rate / profit factor /
drawdown from production (once attribution is fixed, per-rule and
per-strategy too), compare against the last recorded baseline, and append a
dated "Round N" section below with what was tried, what the numbers did, and
what to try next — rather than rewriting this document from scratch each
time.

### Round 1 — 2026-08-15

Baseline not yet established (attribution bug still open as of this writing;
see Prerequisite fixes above). No production performance numbers included
here to avoid fabricating a baseline — first action for whoever picks this up
is steps 1-2 above.

### Round 2 — 2026-08-20

The headline and prerequisite status above are now stale relative to current
`finance-live-action/main` and production:

- Strategy attribution is persisted end-to-end by `33f95b1`; Portfolio
  decisions, positions, closed trades, JSON history and Kafka publication all
  retain signed `contributing_strategies`.
- Per-rule risk limits were scaled in `8d31ac1`, `52a2b0f`, `5156074` and
  `bdeaa06`; `risk-2pct` is no longer rejected by construction.
- Performance weighting is already live, not disconnected. Commit `40fdfa3`
  invokes `reweight_from_alpha_performance` on both realtime closed-klines and
  historical replay. `survival_first_default` now starts from neutral uniform
  weights; `cf35652` prevents unobserved or mature-losing strategies from
  diluting a mature profitable strategy.

The production checkpoint/API capture at `2026-08-20T12:11:26Z` showed all
four workers healthy and replay-complete on contract v25. BTC Portfolio had
1,293 Backtest trades and 1,295 continuous Realtime trades for each execution
rule. The scoped fixed-notional Realtime ledger reported 1,295 trades,
realized PnL `-9.904643901554516`, 392 wins, 903 losses and profit factor
`0.6327140785530052`. Current strategy weights were
`candle_momentum=0.3189766863614304` and
`rsi_mean_reversion=0.6810233136385696`; three configured MTF candidates were
zero-weight with `update_count=2529`.

Conclusion: do not implement the proposal's old step 3 again; the adaptive
weighting path is already active and measured. The baseline remains
unprofitable despite it. Volatility breakout is also no longer an untested
next step: Bollinger/ATR breakout families were swept across the full BTC
history and did not earn promotion; the later MTF ATR candidate was profitable
but stayed below the standing win-rate target on every split. The next
implementation candidate must therefore add genuinely new Alpha evidence and
prove it via the honest research gate before production. The current distinct
candidates are session-aware VWAP mean reversion and Opening Range Breakout,
especially on Exness XAU; do not change live weights manually or add an
ATR/confidence sizing rule as a substitute for signal quality.
