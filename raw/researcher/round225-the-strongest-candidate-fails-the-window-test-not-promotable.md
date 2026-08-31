# CORRECTION (Round 226)

Two things in this file are **wrong**, both mine:

1. **The path-dependence mechanism does not exist.** Round 226 held the holdout
   period fixed and varied preceding history from 1,800 to 1,200 to 900 days:
   the candidate's holdout is byte-identical (62 trades, PF 1.12, PnL +0.53) in
   all three, population medians are identical, and 0 of 63 candidates move more
   than 10%. Splits are evaluated independently of preceding history.
2. **The "decisive contradiction" was a boundary arithmetic error.** 60% of 900
   days is 540 days, so the 900d run's train is 900->360 ago and its validation
   360->180 — not 900->540 and 540->360 as written below. The two runs'
   validation segments cover different periods; there was no same-period
   contradiction.

**The verdict stands** — the candidate is weak over 900->360 and 360->180 days
ago — but on *regime* dependence, which is measured, not *path* dependence,
which is disproven.
See `round226-no-path-dependence-round-225-boundary-arithmetic-was-wrong.md`.

---

# Round 225 — The candidate survives repartitioning but fails the window test: its edge lives in the older history and is negative in the recent 2.5 years

Classification: **REJECTED** for promotion. Two bounded Docker sweeps, no leaks.

## The two checks Round 224 named

`mtf_candle_momentum_10bps_sma10_trend_filtered` cleared the full stack on all
three brokers. Round 224 withheld promotion pending the two axes this program has
measured as its main false-positive sources: partition (Round 211: 48% of cells
flip) and window (Round 219: 38% metric swing). Both run here on binance BTC/USDT,
the production route.

## Result 1 — partition: PASSES, and gets stronger

| run | trades t/v/h | PF t/v/h | PnL t/v/h | full stack |
|---|---|---|---|---|
| 1,800d, 60/20/20 (Round 224 baseline) | 187/58/62 | 1.10 / 1.17 / 1.12 | +2.01 / +0.72 / +0.53 | **PASS** |
| 1,800d, **40/20/40** (partition test) | 132/55/121 | 1.09 / 1.13 / 1.16 | +1.31 / +0.63 / +1.40 | **PASS** |

The holdout doubles to 121 trades and the candidate still clears everything —
out-of-sample evidence is *better* under the harder partition, not worse. Against
Round 211's 48% flip rate, that is a real result.

## Result 2 — window: FAILS, and not on a technicality

| run | trades t/v/h | PF t/v/h | PnL t/v/h | full stack |
|---|---|---|---|---|
| **900d**, 60/20/20 | 88/36/25 | **0.91 / 0.79** / 2.12 | **−0.76 / −0.59** / +1.24 | **FAIL** |

Train and validation are both **below 1 with negative PnL**, on 88 and 36 trades —
above and near the 30-trade floor, so this is not a small-sample dodge. Only the
25-trade holdout is strong, and 25 is below the floor.

### The contradiction that makes this decisive

The two runs disagree about the *same calendar period*.

- 1,800d run: validation covers roughly **720→360 days ago**, PF **1.17**.
- 900d run: train covers **900→540 ago** (PF 0.91) and validation **540→360 ago**
  (PF 0.79).

Overlapping calendar time, opposite verdicts. The ledger is path-dependent —
equity state, open positions and the 1d trend filter's warmup all differ
depending on where the run starts — so the candidate's apparent 1,800-day
strength is partly a property of the history it was fed, not of the signal alone.

Reading the periods together: the last ~360 days are good, the ~540 days before
that are bad, the older ~900 days are good. **That is regime dependence, not a
stable edge.**

## Verdict

Not promotable. Cross-broker agreement across three sources (Round 224) was
genuine and remains the strongest result this program has recorded, and the
partition test strengthens it further — but a candidate whose edge disappears and
turns negative over the most recent 2.5 years fails the "would I trade this
tomorrow" question, which is the only one that matters for deployment.

It stays on record as the best candidate found, with its exact failure mode
documented, rather than being deployed and discovered in production.

## Two secondary observations

- **Survivor sets are themselves partition-dependent.** The 40/20/40 partition
  admits **5** full-stack survivors (`donchian_breakout_20`,
  `mtf_candle_momentum_10bps_sma10_trend_filtered`, `mtf_macd_5_13_5_sma10_trend_filtered`,
  `sma10_trend_filtered_engulfing_pattern`, `three_candle_continuation`) against
  2 at 60/20/20. A "how many survive" count is not a stable quantity — another
  instance of Round 211, now at the population level rather than the cell level.
- **The 900-day window admits zero of 107.** Consistent with every other short
  window measured in this series.

## What is proven, and what is not

Proven:

- Partition 40/20/40 on binance BTC 4h+1d/1,800d: the candidate clears PF>1,
  >=30 trades and positive PnL on all three splits, with a 121-trade holdout.
- Window 900d: PF 0.91/0.79/2.12, PnL −0.76/−0.59/+1.24, trades 88/36/25 — fails
  the PF bar, the trade floor and the PnL condition.
- The 1,800d and 900d runs assign opposite verdicts to overlapping calendar
  periods.
- 5 vs 2 full-stack survivors under two partitions of the same data; 0 of 107 on
  the 900-day window.

Not proven, and deliberately not claimed:

- That the candidate has no edge. It passed cross-broker on three sources and
  passed repartitioning; what is shown is that its edge is not stable across
  history, which is sufficient to withhold deployment but not to call it noise.
- The exact cause of the path dependence. Equity state, open positions and trend
  filter warmup are the plausible mechanisms; none was isolated.
- Anything about XAU, or about intervals other than 4h+1d.
