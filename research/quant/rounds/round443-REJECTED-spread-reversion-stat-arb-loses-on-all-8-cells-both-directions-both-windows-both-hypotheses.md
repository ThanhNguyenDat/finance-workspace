# Round 443 — REJECTED: statistical-arbitrage spread-reversion loses on all 8 cells (2 leader/follower directions × 2 windows × 2 hypotheses), with the losing hypothesis ordering itself arguing against the mechanism

Classification: **REJECTED**. This round executes round442's named next step for
`research/quant/index.md` section 0.5 item 5 (statistical-arbitrage spread
trading): implement the backtest-only prototype in `finance-research` (never
touching the production engine), unit test the no-lookahead alignment and
z-score logic in isolation, then get one honest train/validation/holdout read
on whether a rolling log-price-ratio spread between two same-asset routes
reverts to its own mean.

## Continuation context

Launcher-recorded iteration read `243` at round start
(`quant-research-state state`) — the coordinator's own per-session attempt
counter, distinct from the round-file sequence per the playbook's documented
divergence (round413/424-426/440/441/442). `git status --short` was clean in
both `finance-workspace` (HEAD `395c464`) and `finance-live-action` (HEAD
`5bd2634`, round439's CLI commit) at round start, and `git fetch` +
`git rev-parse HEAD origin/main` confirmed both matched their remotes before
any work began. No recovery work needed. `begin-iteration` not called.

## What was implemented

`SpreadReversionStrategy` + `spread_reversion_candidates`
(`crates/finance-research/src/strategies.rs`, finance-live-action) and a
~15-line `main.rs` wiring block that reuses round437's existing
`--leader-*`-flag merge infra byte-for-byte — no new CLI flags, no new
loading code. finance-live-action commit `917f00d88010c0edb6ba152c1426a9d63fbcd0a6`,
pushed and confirmed at `origin/main` (`git fetch` + `git rev-parse` matched
before this round ends).

Design, matching round442's design survey exactly:

- Reads the same leader/follower merged, `close_time`-ordered stream
  `CrossInstrumentLeadLagStrategy` uses (`main.rs`'s `leader_instrument` /
  `cross_instrument_windows`), told apart by `kline.instrument.key()`.
- Computes `spread = ln(leader_close) - ln(follower_close)` on every follower
  bar, using the most recent leader close whose `close_time` is **strictly
  before** the follower bar's own `close_time` (identical strictly-before
  guard to `CrossInstrumentLeadLagStrategy`, needed for the same reason: a
  same-interval merge can legally produce exact `close_time` ties).
- Maintains a rolling window of **prior** spread values (the current bar's
  spread is scored against the window, then pushed into it afterward — a bar
  is never compared to a baseline that includes itself). Once the window is
  full, computes `z = (spread - mean) / std_dev` over that window.
- Fires when `|z| >= 1.5` (a standard stat-arb entry level, used bare/
  unswept per round433/437's convention): `EnterLong` the follower on a high
  positive spread (convergence hypothesis: the leader pulled away, follower
  should catch up) or `EnterShort` on a low/negative spread — with a mirror
  `fade`/diverge variant testing the opposite sign, exactly as round437's
  follow/fade pair tested lead-lag's sign.
- Hedge ratio assumed at 1.0 (both instruments are gold priced in USD; a
  regression/Kalman-estimated beta was explicitly deferred per round442's
  design note as unnecessary before validating the cheap first cut).
- Grid: window ∈ {20, 60} bars, hypothesis ∈ {converge, diverge},
  `entry_z = 1.5` fixed — 4 candidates per leader/follower direction, 8 cells
  total across both directions.

## Unit tests (before any backtest number was trusted)

8 new tests in `strategies.rs`, all green together with the pre-existing 150
(158 total `strategies::tests`, 75 pass when filtered to `strategies::`
alone in the first isolated run; full crate `cargo test -p finance-research`
and `cargo test --workspace --exclude finance-redis` both green — 157 passed
in `finance-research`'s own unittest binary, no failures anywhere):

- a leader bar never itself produces a signal;
- the wide-positive-spread case is unambiguous by construction (three
  near-zero spreads seed the rolling window, then a sharply wider fourth
  spread is scored against that near-zero baseline, so the resulting z is
  large without needing to hand-verify the exact mean/std arithmetic):
  `converge` goes long the follower, `diverge` takes the opposite (short);
- fewer than `window` prior spreads never scores a signal (covers the
  window-fill gate, the direct analogue of round437's leader-needs-two-closes
  self-catching bug — caught here by the same discipline, no rework needed);
- the as-of guard is strictly-before: a follower bar at the exact same
  `close_time` as the only leader bar seen so far reads nothing, and a bar
  timestamped earlier than that leader bar also reads nothing;
- a kline from neither leader nor follower instrument is ignored;
- the 4-candidate grid produces 4 distinct names.

`cargo fmt --check -p finance-research` clean (after fixing one
clippy-flagged doc-comment formatting issue introduced by this round's own
diff — a doc-comment line starting with `- ` was misread as an unindented
markdown list continuation; reworded, not suppressed). `cargo clippy -p
finance-research --all-targets -- -D warnings` shows only the same 9
pre-existing findings round437 already noted as unrelated to this round's
diff (`split.rs` dead code, a `filter_map`/`bool::then` lint, generated
proto enum variant names, `klines.rs` large-`Err`-variant, one pre-existing
`nonminimal_bool` at `strategies.rs:1523` in an unrelated strategy) — left
untouched per scope discipline.

## Backtest — two containers, `--days 500`, plain sweep (no `--daily-profit-gate`)

SSH tunnel `ssh -f -N -L 18086:localhost:8086 my` opened, confirmed listening
via `ss -tlnp`, closed at the end of the round (confirmed via `ss -tlnp`
showing nothing on 18086 afterward). Docker image rebuilt (`docker build -f
docker/Dockerfile-research`) after the source change, per the standing rule.
Two detached containers, `--cpus=2 --network host`, logs captured via
`docker logs -f <name>` to a file (stdout carries only the pretty-printed
`--json` payload; ECS application logs go to stderr, captured separately) —
both containers used `--rm` and self-removed on completion, confirmed via
`docker ps -a --filter "ancestor=finance-research-local:latest"` (empty)
before this round ends:

1. `finance-research-r443-xau-follower` — primary/follower `exness XAU/USD`
   cfd, leader `bybit XAUT/USDT` spot (tests "bybit XAUT leads exness XAU").
2. `finance-research-r443-xaut-follower` — primary/follower `bybit
   XAUT/USDT` spot, leader `exness XAU/USD` cfd (tests "exness XAU leads
   bybit XAUT").

**Validity gate, checked before reading any score** (playbook: never compare
two runs without checking `candle_count`): both runs report **identical**
`spread_reversion.merged_candle_count = 241472` (97473 primary XAU candles +
143999 primary XAUT candles, exactly), so both directions loaded and merged
the same two underlying series — no partial window, no drift between the two
launches. This is 2 candles more than round437's `241470` measured on a
different (BTC/XAU) pair three rounds earlier — consistent with this
program's documented per-route candle-count jitter (playbook: session/24-7
routes drift a few candles across hours-to-days-apart runs), not a validity
failure.

## Results — holdout, all 8 named candidates (4 per direction)

| Direction | Candidate | Holdout trades | Holdout PF | Holdout win rate | Holdout PnL |
|---|---|---:|---:|---:|---:|
| XAUT leads XAU | `spread_reversion_w20_converge` | 1450 | 0.239 | 27.6% | −10.25 |
| XAUT leads XAU | `spread_reversion_w20_diverge` | 1450 | 0.330 | 21.9% | −10.05 |
| XAUT leads XAU | `spread_reversion_w60_converge` | 942 | 0.279 | 35.0% | −7.00 |
| XAUT leads XAU | `spread_reversion_w60_diverge` | 942 | 0.416 | 24.0% | −6.19 |
| XAU leads XAUT | `spread_reversion_w20_converge` | 1916 | 0.202 | 21.0% | −13.03 |
| XAU leads XAUT | `spread_reversion_w20_diverge` | 1916 | 0.242 | 20.3% | −13.79 |
| XAU leads XAUT | `spread_reversion_w60_converge` | 1165 | 0.268 | 26.4% | −8.30 |
| XAU leads XAUT | `spread_reversion_w60_diverge` | 1165 | 0.341 | 23.9% | −8.01 |

Train and validation splits (captured in `/tmp/r443-*.json`, both this round
only, not committed) show the same magnitude and ordering as holdout on
every cell — no train-good/holdout-bad shape anywhere: e.g.
`spread_reversion_w60_diverge` on the XAU-follower run reads PF 0.326 (train)
/ 0.435 (validation) / 0.416 (holdout), and the XAUT-follower run reads 0.307
/ 0.375 / 0.341 — flat across all three splits, both directions.

## Why this is a clean rejection, not an inconclusive one

Three independent structural signals agree, the same pattern round437 used
to close cross-instrument lead-lag:

1. **Both directions fail, in the same narrow band.** "XAUT leads XAU"
   (PF 0.24-0.42) and "XAU leads XAUT" (PF 0.20-0.34) land within ~20% of
   each other on every matched (window, hypothesis) cell — no direction is
   anywhere close to viable, and neither shows the kind of asymmetry a real,
   one-sided transmission mechanism would produce.
2. **The "wrong" hypothesis wins on every single cell, and that is itself
   evidence, not a shrug.** `diverge` (bet the spread keeps widening) beats
   `converge` (bet it reverts) on all 4 window/direction combinations —
   e.g. window 60, XAUT-follower: 0.416 (diverge) vs 0.279 (converge). If
   this pair had a real mean-reverting cointegration relationship, the
   *reversion* side should win, not lose to its own mirror on every cell.
   A momentum-style edge that consistently beats a reversion-style edge on a
   spread constructed specifically to bet on reversion is the sign the
   z-score is tracking transient noise around a spread that does not
   actually mean-revert on this timeframe/window, not a signal that the
   "diverge" direction is secretly the real edge (its best PF, 0.416, is
   still far below 1.0 on every split).
3. **The magnitude sits in the same structurally-noisy band round437 found
   for cross-instrument lead-lag.** PF 0.20-0.42 here vs round437's
   PF 0.05-0.23 — both are well below round433's already-closed
   `KBarReturnReversalStrategy` bare baseline (PF up to 0.82) and in the same
   range as this program's other examples of "a signal that fires on almost
   every eligible bar drowning in transaction cost" (Two-candle Engulfing,
   OBV/Elder Ray). At `entry_z = 1.5` on a rolling 20-60 bar window, roughly
   1 in 3-4 follower bars crosses the threshold (942-1916 holdout trades
   over a 68-100 day holdout, i.e. roughly 80-140 trades/week) — this is a
   frequent, not rare, trigger condition, the same overtrading failure mode
   round437 diagnosed for its bare `minimum_cumulative_move = 0.0` grid.

## What remains open, honestly

`entry_z` was never swept above 1.5 (this round's grid varied only window
and hypothesis, matching round433/437's own precedent of never sweeping a
magnitude threshold before closing a bare-grid direction). A materially
higher threshold (e.g. 2.5-3.0, filtering to rarer, larger spread deviations)
would reduce trade count and could in principle change the cost-to-edge
ratio — the same caveat this program has recorded for several other
"bare-threshold, never swept" closures (index.md section 3, several rows
note exactly this same scope limit). Given the diverge-beats-converge
inversion is a *sign* problem, not merely a magnitude problem, and a rarer
trigger does not fix a mechanism whose reversion hypothesis loses to its own
mirror, a threshold sweep is not expected to change the conclusion but is
not proven not to — recorded here rather than asserted away, per this
program's no-fabrication rule. A rolling OLS/Kalman-estimated hedge ratio
(instead of the 1.0 assumption used here) is the other unswept axis; given
`exness XAU`/`bybit XAUT` correlate at +0.996 in raw price (round342/436), a
hedge ratio near 1.0 was expected to be close to optimal, but this was not
verified empirically before closing. Re-open only with a
magnitude-thresholded or hedge-ratio-estimated follow-up that reports honest
train/validation/holdout, not by re-running the bare grid again.

## Statistical-arbitrage spread-reversion direction status

**CLOSED** at the bare-threshold rigor level this program uses to close
other directions (round433/437 precedent). `research/quant/index.md`
section 0.5 item 5 and section 3's closed-directions table updated
accordingly. Item 6 (Hurst-exponent regime filter, round442's other named
next step) remains open for a future round.

## Housekeeping

Two Docker containers this round, both launched detached (`-d --rm`), logs
captured via `docker logs -f` before their `--rm` self-removed them on
completion — confirmed via `docker ps -a --filter
"ancestor=finance-research-local:latest"` (empty) before this round ends.
One SSH tunnel opened and closed, confirmed via `ss -tlnp` (empty for port
18086) after teardown. `finance-live-action` local checks this round:
`cargo test -p finance-research` (157/157 in the crate's unittest binary,
0 failures), `cargo fmt --check -p finance-research` (clean, after a
doc-comment fix), `cargo clippy -p finance-research --all-targets -- -D
warnings` (9 pre-existing findings unrelated to this round's diff, left
untouched per scope discipline), full `cargo test --workspace --exclude
finance-redis` (all `test result: ok` blocks, 0 failures). Commit
`917f00d` pushed to `origin/main` and confirmed via `git fetch` +
`git rev-parse HEAD origin/main` match. `gh run list` shows a
research-only-path CI run queued for this commit; `finance-research` has
no `finance-strategy`/`finance-api` dependency change, so `deploy=false` is
expected (round437's documented precedent) — no production verification
needed for this commit.
