# Round 437 — REJECTED: the cross-instrument lead-lag backtest-only prototype loses on all 24 cells (2 leader/follower directions × 2 k × 2 hypotheses × 3 splits), and the failure mode is overtrading, not a directional miss

Classification: **REJECTED**. This round executes round434's named next step for
the last open item in `research/quant/index.md` section 0.5 (item 2,
cross-instrument lead-lag): implement the as-of-aligned, backtest-only
prototype in `finance-research` (never touching the production engine), unit
test the no-lookahead alignment logic in isolation, then get one honest
train/validation/holdout read on whether a leader instrument's recent return
predicts a follower instrument's next move.

## What was implemented

`CrossInstrumentLeadLagStrategy` + `cross_instrument_leadlag_candidates`
(`crates/finance-research/src/strategies.rs`, finance-live-action) and CLI
wiring (`--leader-broker`/`--leader-market-type`/`--leader-base-asset`/
`--leader-quote-asset`, `crates/finance-research/src/main.rs`), finance-live-action
commit `8e6e5a25622c97c73f6604c6328816e126c23dc5`, pushed and confirmed at
`origin/main` (local `HEAD` and `origin/main` matched via `git fetch` +
`git rev-parse` before this round ends).

Design, matching round434's named next step exactly:

- The CLI loads a second instrument's (`--leader-*`) klines at the same
  `--interval` and merges them with the primary instrument's klines using the
  **same** `merge_multi_timeframe_klines` function already used for
  same-instrument multi-timeframe candidates (chronological, `close_time`
  order, `finance-api::historical_replay::replay_order`-compatible
  tie-break). Nothing in `finance-core::Kline`, `Strategy::evaluate`, or the
  replay bootstrap/ledger-keying code round434 identified as the real blocker
  was touched — this stays entirely inside `finance-research`.
- `CrossInstrumentLeadLagStrategy` tells the two instruments apart by
  `kline.instrument.key()` (not `kline.timeframe`, which is identical for
  both since they share one interval — the same-interval merge can legally
  produce exact `close_time` ties, unlike the base/higher-timeframe case).
- No-lookahead is enforced twice: the strategy never trusts merge order at a
  tie, and the stored leader feature carries its own `close_time`; a
  follower bar only reads it when that stored timestamp is **strictly**
  before the follower bar's own `close_time`.
- Grid: k ∈ {1, 3} leader bars, hypothesis ∈ {follow (same direction as
  leader), fade (opposite)}, `minimum_cumulative_move = 0.0` — the same
  bare-baseline convention round433 used for `KBarReturnReversalStrategy`
  (react to any nonzero signal before tuning any threshold).

## Unit tests (before any backtest number was trusted)

7 new tests in `strategies.rs`, all green together with the pre-existing 143
(150 total in that module; `cargo test --workspace --exclude finance-redis`
also green, 32/32 `test result: ok` blocks, 0 failures):

- a leader bar never itself produces a signal;
- a follower bar strictly after a leader bar reads the seeded feature and
  follows its direction;
- the fade variant reads the same feature and flips the side;
- **the as-of guard is strictly-before**: a follower bar at the exact same
  `close_time` as the leader bar that set the feature reads nothing, and
  a follower bar timestamped earlier than the leader bar also reads
  nothing (covers the exact failure class round434 named: a same-interval
  merge tie, and an out-of-order/stale feed);
- a kline from neither leader nor follower instrument is ignored;
- the 4-candidate grid produces 4 distinct names (no silent aliasing in the
  score table, the same check `every_candidate_carries_a_unique_name`
  already runs for the rest of the file).

First implementation attempt of the strictly-before tests failed for an
unrelated reason (k=1 needs **two** leader closes to produce one bar-to-bar
return; the first draft fed only one) — caught immediately by the test
itself, fixed before any container ran. Recorded here because it is exactly
the kind of self-catching failure the unit-test-first ordering exists to
produce.

## Backtest — two containers, `--days 500`, plain sweep (no `--daily-profit-gate`)

SSH tunnel `ssh -f -N -L 18086:localhost:8086 my` opened, confirmed listening
via `ss -tlnp`, closed at the end of the round. Docker image rebuilt
(`docker build -f docker/Dockerfile-research`) after the source change, per
the standing rule. Two detached containers, `--cpus=2 --network host`,
confirmed `docker ps -a` shows nothing left afterward:

1. `finance-research-r437-btc-follower` — primary/follower `binance BTC/USDT`
   perpetual, leader `exness XAU/USD` cfd (tests "XAU leads BTC").
2. `finance-research-r437-xau-follower` — primary/follower `exness XAU/USD`
   cfd, leader `binance BTC/USDT` perpetual (tests "BTC leads XAU").

**Validity gate, checked before reading any score** (playbook: never compare
two runs without checking `candle_count`): both runs report **identical**
`cross_instrument_leadlag.merged_candle_count = 241470`
(143998 primary BTC candles + 97472 primary XAU candles, exactly), so both
directions loaded and merged the same two underlying series — no partial
window, no drift between the two launches. Primary-instrument candle counts
match established baselines exactly: BTC `candle_count=143998`
(train/validation/holdout 86399/28800/28799, matches rounds 360-367's
recorded value for the same route/window), XAU `candle_count=97472`
(train/validation/holdout 58483/19494/19495, 359 verified session gaps /
46526 candles — a CFD's weekend closures, not a data defect, consistent with
every prior XAU run in this corpus).

## Results — holdout, all 8 named candidates (4 per direction)

| Direction | Candidate | Holdout trades | Holdout PF | Holdout win rate | Holdout PnL |
|---|---|---:|---:|---:|---:|
| XAU leads BTC | `cross_instrument_leadlag_k1_follow` | 9965 | 0.139 | 14.6% | −70.09 |
| XAU leads BTC | `cross_instrument_leadlag_k1_fade` | 9965 | 0.134 | 15.0% | −69.42 |
| XAU leads BTC | `cross_instrument_leadlag_k3_follow` | 5328 | 0.225 | 19.3% | −37.04 |
| XAU leads BTC | `cross_instrument_leadlag_k3_fade` | 5328 | 0.206 | 20.4% | −37.56 |
| BTC leads XAU | `cross_instrument_leadlag_k1_follow` | 10037 | 0.056 | 7.5% | −69.81 |
| BTC leads XAU | `cross_instrument_leadlag_k1_fade` | 10037 | 0.049 | 7.7% | −70.71 |
| BTC leads XAU | `cross_instrument_leadlag_k3_follow` | 5491 | 0.101 | 11.4% | −38.97 |
| BTC leads XAU | `cross_instrument_leadlag_k3_fade` | 5491 | 0.096 | 11.9% | −37.90 |

Train and validation splits (not tabulated in full — see the raw JSON, both
kept under `/tmp/r437-*.json` this round only, not committed) show the same
magnitude and ordering on every cell; there is no train-good/holdout-bad
overfitting shape anywhere in the 24 cells (4 candidates × 2 directions × 3
splits) — every split is uniformly, catastrophically unprofitable.

## Why this is a clean rejection, not an inconclusive one

Three independent structural signals agree, not just a below-1.0 PF:

1. **Both directions fail, by comparable relative margins.** Neither
   "XAU leads BTC" (PF 0.13-0.23) nor "BTC leads XAU" (PF 0.05-0.10) shows
   the other's near-scale performance — if anything BTC-leads-XAU is worse,
   opposite of what "BTC is the larger, more liquid market so it should lead"
   would predict, which is itself evidence against a real transmission
   mechanism rather than for one direction over the other.
2. **Fade and follow are near-mirror-image losers, not opposites.** Every
   fade/follow pair at the same (direction, k) has nearly identical trade
   count and closely matched PF (e.g. XAU-leads-BTC k=1: 0.134 fade vs 0.139
   follow). A real directional edge would make one side of the pair
   materially better than the other; this pattern — both sides losing by
   about the same amount — is the same "noise dominates transaction cost
   regardless of direction" signature round72 already found for raw
   order-flow imbalance on this program's cost structure, not a new failure
   mode.
3. **The magnitude is far below anything else recorded in this arc.** PF
   0.05-0.23 is below round433's already-closed `KBarReturnReversalStrategy`
   bare baseline (PF up to 0.82) and below nearly every closed candidate in
   index.md section 3 — only Two-candle Engulfing (PF 0.16-0.42, round103)
   and OBV/Elder Ray (PF ~0.09-0.37, rounds 113/119) are in the same range,
   and those are this program's two prior examples of the same underlying
   cause: **a signal that fires on almost every eligible bar**. Here,
   `minimum_cumulative_move = 0.0` means any nonzero leader return is enough,
   and a leader bar's return is essentially never exactly zero — combined
   with the feature persisting ("as-of held") until the next leader bar,
   9965-10037 holdout trades on a ~14-week holdout (≈700/week) means the
   strategy is trading on close to every eligible follower candle, not
   reacting to a rare, meaningful leader move. That is a materially
   different, noisier construction than `KBarReturnReversalStrategy`'s
   k-consecutive-same-sign-run requirement, which is naturally rare.

## What remains open, honestly

`minimum_cumulative_move` was never swept above 0.0 (this round's grid varied
only k and direction, matching round433's own precedent of never sweeping a
magnitude threshold before closing its own direction). A large-enough
threshold would filter to only the leader's rare, larger moves and could in
principle change this outcome — the same caveat this program has recorded
for several other "bare, k varied, threshold untested" closures (index.md
section 3, several rows note exactly this same scope limit). Given the
current bare grid's PF is roughly 4-16x further from break-even than
round433's already-closed KBarReversal baseline, and the failure mode
(near-100%-of-bars trading, fade≈follow) is structural rather than magnitude-
sensitive, a threshold sweep is not expected to change the conclusion, but is
not proven not to — recorded here rather than asserted away, per this
program's no-fabrication rule. Re-open only with a magnitude-thresholded
follow-up that reports honest train/validation/holdout, not by re-running the
bare grid again.

## Cross-instrument lead-lag direction status

**CLOSED** at the bare-threshold rigor level this program uses to close
other directions (round433 precedent). `research/quant/index.md` section
0.5 item 2 and section 3's closed-directions table updated accordingly. This
was the last open item from round432's post-audit proposal list — see
index.md's "Trạng thái sau Round 437" note for the full current state of
section 0.5.

## Housekeeping

Two Docker containers this round, launched detached (`-d`, no `--rm` on the
second launch after the first pair's `--rm` removed them before their logs
could be captured — logs pulled via `docker logs` before `docker rm -f` on
the retry), both confirmed removed via `docker ps -a --filter
"ancestor=finance-research-local:latest"` (empty) before this round ends.
One SSH tunnel opened and closed, confirmed via `ss -tlnp` (empty for port
18086) after teardown. `finance-live-action` local checks this round:
`cargo check -p finance-research`, `cargo test -p finance-research` (150/150
in `strategies::tests`, plus the rest of the crate), `cargo fmt -p
finance-research`, `cargo clippy -p finance-research --all-targets -- -D
warnings` (9 pre-existing findings unrelated to this round's diff — `split.rs`
dead code, a `daily_profit_gate.rs` lint, generated proto enum names,
`klines.rs` large-Err-variant — left untouched per scope discipline), full
`cargo test --workspace --exclude finance-redis` (32/32 `test result: ok`
blocks, 0 failures).
