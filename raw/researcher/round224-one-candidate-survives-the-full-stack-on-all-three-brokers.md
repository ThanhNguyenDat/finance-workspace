# Round 224 — Cross-broker: one candidate survives the full stack on all three brokers, the other is falsified. The strongest result this program has recorded

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps. Not a
PROMOTE, and the reason is stated precisely below rather than hedged.

## The test

Round 223 surfaced two candidates clearing every accumulated filter on exness
BTC 4h+1d, and named the missing check: the program's central rule, cross-broker
validation. Round 205 falsified four binance XAU candidates on exness; Round 210
calibrated bybit as a falsifier for exactly this purpose.

Both survivors re-run on **binance BTC/USDT** and **bybit BTC/USDT**, 4h with a
1d trend filter, 1,800 days, production cost.

## Result — the test worked in both directions

### `mtf_candle_momentum_10bps_sma10_trend_filtered` — holds everywhere

| broker | trades t/v/h | PF t/v/h | PnL t/v/h | full stack |
|---|---|---|---|---|
| exness | 193/58/62 | 1.07 / 1.14 / 1.08 | +1.42 / +0.59 / +0.40 | **PASS** |
| binance | 187/58/62 | 1.10 / 1.17 / 1.12 | +2.01 / +0.72 / +0.53 | **PASS** |
| bybit | 187/58/64 | 1.13 / 1.16 / 1.11 | +2.54 / +0.68 / +0.50 | **PASS** |

Nine broker-split cells. Every PF between **1.07 and 1.17**. Every split above the
30-trade floor. Every PnL positive. Trade counts nearly identical across brokers
(187-193 / 58 / 62-64), which is what the same signal firing on the same bars
should look like.

**This is the first candidate in this session to survive the full accumulated
stack on all three brokers.** For contrast, the population holdout edge/friction
median on the exness run was 0.087; this candidate reads 2.00-2.23 across splits
(Round 223).

### `candle_momentum_rv_regime_filter_10_50_1.3` — falsified

| broker | PF t/v/h | PnL t/v/h | full stack |
|---|---|---|---|
| exness | 1.02 / 1.39 / 1.05 | +0.60 / +2.78 / +0.18 | pass |
| binance | **0.86** / 1.35 / 1.29 | **−3.79** / +2.42 / +1.59 | **fail** |
| bybit | **0.79** / 1.20 / **0.99** | **−6.23** / +1.49 / **−0.21** | **fail** |

Passes on the source that found it and inverts on both others — the exact Round
205 signature. Rejected.

Also noted: `three_candle_continuation` clears the stack on **binance only**,
another single-broker artifact. The cross-broker rule removed two of three
candidates it was given.

## Why this is not a PROMOTE

The gate requires defensible OOS evidence and understood risk. Two robustness
axes this program has *measured* as treacherous have not been tested for this
candidate:

1. **Partition.** Round 211: 48% of cells flip their PF>1 verdict when the
   partition moves, even at large samples. This candidate has one 60/20/20 cut.
2. **Window.** Round 219: the same metric moved 38% between a 365-day and an
   1,800-day window on the same source. This candidate has one window.

Both are one container each and are the natural next round. Promoting on a single
window and a single partition — after measuring exactly those two things as the
main sources of false positives — would be the Round 67 zombie-strategy mistake
committed with full knowledge.

Two further points that temper the result honestly:

- **The edge is thin.** Train PF is 1.07-1.13 and net PnL is +0.40 to +2.54 on a
  10,000 starting equity. Real but small.
- **Deployment would not do much soon.** Round 223/207: a newly registered
  strategy carries `strategy_weight = 0` until 20 trades
  (`PERFORMANCE_CONFIDENCE_TRADES`), and this candidate trades roughly 62 times
  per 360-day holdout, so maturity is months away even after deployment.

## Incident note

The first invocation timed out at two minutes with the bybit container still
running — the exact failure mode the loop skill warns about, where a killed
foreground `docker run` leaves a container holding the single-slot kline gate. It
was checked immediately, found still running, allowed to finish (75 more seconds),
and `--rm` removed it. No leak, no gate contention. Recorded because the check
mattered more than the outcome: had it been left, later rounds would have been
misdiagnosed as production contention, which is what happened in Rounds 124-125.

## What is proven, and what is not

Proven:

- `mtf_candle_momentum_10bps_sma10_trend_filtered` clears PF>1, >=30 trades and
  positive PnL on all three splits on exness, binance and bybit BTC 4h+1d over
  1,800 days, with PF in a 1.07-1.17 band across nine cells.
- `candle_momentum_rv_regime_filter_10_50_1.3` inverts on both cross-brokers
  (train PF 0.86 and 0.79, train PnL −3.79 and −6.23) and is rejected.
- `three_candle_continuation` passes on binance only.

Not proven, and deliberately not claimed:

- That the candidate survives repartitioning or a different window. Untested, and
  these are the two axes this program measured as the main false-positive
  sources.
- That it is worth deploying. The edge is thin and the maturity gate would keep
  its weight at zero for months.
- Anything about XAU. This is a BTC result; Round 208 showed XAU/binance cannot
  supply a comparable long window at all.
