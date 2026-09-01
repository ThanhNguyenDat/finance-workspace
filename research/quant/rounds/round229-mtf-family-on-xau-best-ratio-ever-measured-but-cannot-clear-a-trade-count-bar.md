# CORRECTION (Round 230)

**Result 2 of this file is withdrawn.** The MTF ratio of **+4.571** is the
holdout cell only. Round 230 read the other two splits and the other instrument:
XAU MTF is **+0.371 / -1.954 / +4.571** (validation deeply negative) and BTC MTF
is **+1.458 / -1.086 / -1.563** (negative on both out-of-sample splits). MTF
split-spreads are **9.5x** (XAU) and **4.3x** (BTC) wider than single-timeframe
on 2.3-2.8x fewer trades per cell — the +4.571 was the best of three cells from
the noisiest population in the run. There is no measured MTF edge advantage.
Result 1 (the empty funnel) stands.
See `round230-the-mtf-advantage-does-not-generalise-it-is-variance.md`.

---

# Round 229 — The MTF sweep finally run on XAU: zero survivors, and the highest edge-to-friction ratio this program has ever measured

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## The gap being closed

Round 223 was the first run in this entire series to pass
`--higher-timeframe-interval`, and it was on BTC — where it produced the
program's best-ever candidate. The same experiment had **never been run on XAU**,
the priority instrument. Round 205 tested a handful of swing candidates there;
the 30-candidate MTF registry against the full accumulated stack had not.

exness XAU/USD 4h with a 1d trend filter, 1,800 days: **107 candidates, 30 of
them MTF**.

## Result 1 — the funnel, and it is empty

| surviving | filter |
|---|---|
| **107** | all candidates (30 MTF) |
| **2** | PF > 1 on all three splits — `ema_crossover_12_26`, `ichimoku_cloud_9_26_52_26` |
| **1** | + >= 30 trades on all three splits |
| **0** | + positive PnL on all three splits |

**Not one MTF candidate clears even the PF bar.** The two that do are the same
single-timeframe pair Round 222 already rejected, and they fail again for the
same reasons: `ema_crossover_12_26` reads PF 1.01/1.05/1.42 with PnL
**−0.10/−0.05**/+0.79 — the Round 212 defect, caught by the PnL filter added for
exactly this; `ichimoku_cloud_9_26_52_26` has 32/**10**/**10** trades.

Adding 30 MTF candidates to the XAU sweep changed the survivor count by zero.

## Result 2 — and yet the MTF family carries the best ratio ever measured here

Splitting the same run's holdout population (cells with >= 30 trades):

| population | cells | median trades | edge/trade | **ratio** | % edge > 0 |
|---|---|---|---|---|---|
| **MTF (30 candidates)** | 11 | 40 | **+0.02895** | **+4.571** | **82%** |
| single-timeframe (77) | 40 | 110 | +0.00470 | +0.659 | 70% |
| all 107 | 51 | 71 | +0.00594 | +0.841 | 73% |

**6.9x the edge per trade at roughly a third of the trade count, giving an
edge-to-friction ratio of 4.57 — the highest this program has measured anywhere.**
Even after Round 221's volatility adjustment, which roughly halves such figures,
that is ~2.3, still clearly above break-even. Every prior population measured in
this series sat below 1.

So the trend filter does exactly what the cost model predicts it should: fewer,
better trades against a fixed per-trade toll.

## Why nothing passes anyway — the tension is sample size, again

Per-split behaviour of the 30 MTF candidates:

| split | clearing PF > 1 | cells with >= 30 trades |
|---|---|---|
| train | 7 / 30 | 22 / 30 |
| validation | 8 / 30 | **12 / 30** |
| holdout | **18 / 30** | **11 / 30** |

Two separate problems, and they are not the same problem:

1. **Sample size.** Only 12 of 30 reach the trade floor on validation and 11 on
   holdout. A conjunction over three splits cannot certify a family that trades
   ~40 times per 360-day segment. This is exactly the structural tension Round
   223 measured for the deployed swing strategy on BTC — the bar needs 90+ trades
   and these mechanisms do not produce them.
2. **The older segments are genuinely bad.** 18 of 30 clear PF on holdout against
   7 on train. That is not only a sample effect; it matches Round 227's
   walk-forward, where S1 and S2 are negative for the whole instrument. The MTF
   family looks good recently and poor historically, like everything else on XAU.

Problem 1 is a measurement limitation. Problem 2 is a real weakness. Conflating
them would be the mistake here, so they are stated separately.

## What this changes

The honest position on XAU shifts from "nothing works" to something more precise:

> **On XAU 4h, trend-filtered MTF mechanisms earn roughly 4.6x their friction on
> the most recent 360 days and cannot be certified by a bar that requires 30
> trades on each of three splits. Their historical performance is poor, and the
> favourable segment is the same high-volatility one that flatters everything.**

That is not a validated edge and must not be treated as one. It is the most
promising unvalidated population the program has found on the priority
instrument, and it is unvalidatable with the current bar.

## What is proven, and what is not

Proven:

- exness XAU 4h+1d, 1,800 days, 107 candidates: 2 clear the PF bar, 1 clears the
  trade floor, 0 clear positive PnL. No MTF candidate clears the PF bar.
- MTF holdout population: 11 cells, median 40 trades, edge/trade +0.02895, ratio
  +4.571, 82% positive — against 0.659 for the 77 single-timeframe candidates in
  the same run.
- MTF per-split PF>1 counts: 7/30 train, 8/30 validation, 18/30 holdout; cells
  above the trade floor: 22/12/11.

Not proven, and deliberately not claimed:

- That the MTF family has a real edge. Its holdout advantage sits in Round 227's
  S5 segment, which flatters every population, and only 7 of 30 clear PF on
  train.
- That 4.571 survives correction. Round 221's method would put it near 2.3, but
  that adjustment was derived for a different population and was not recomputed
  here.
- That the trade floor is wrong. Round 210 measured it and it has repeatedly
  caught false positives; the finding is that it and low-frequency mechanisms are
  incompatible, not that either is mistaken.
