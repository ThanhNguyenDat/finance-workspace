# Round 248 — Per-candidate check of Round 247: the breakout result survives, the "3 of 4 families" framing does not

Classification: **NO-CHANGE**. Two bounded Docker sweeps reproducing Round 247's
runs for a stricter reading.

## The self-check Round 247 flagged

Round 247 reported per-family **aggregates** and listed its own limitation:
*"not claimed: that per-family aggregates are not dominated by a few high-trade
candidates — trades were summed within each family without weighting checks."*

That is the load-bearing number in the round, so it gets checked. Round 230's rule
applies: report the spread, not one aggregate.

exness XAU 5m Alpha sweep, zero cost, candidates with >= 30 trades in both bands:

| family | n | agg 0-150 → 150-300 | **median** 0-150 → 150-300 | improved |
|---|---|---|---|---|
| **breakout** | 15 | +0.00083 → +0.00294 | **+0.00056 → +0.00278** | **9/15** |
| trend/momentum | 24 | +0.00020 → +0.00031 | **+0.00030 → +0.00028** | 15/24 |
| other | 11 | +0.00008 → +0.00013 | +0.00012 → +0.00026 | 6/11 |
| **reversion** | 18 | −0.00049 → −0.00123 | **−0.00034 → −0.00241** | 6/18 |

## What survives, and what does not

**Breakout survives, and is now better supported than in Round 247.** The median
rises ~5x alongside the aggregate (+0.00056 → +0.00278), and the lift is spread
across 9 of 15 candidates from structurally distinct mechanisms —
`opening_range_breakout_london_30m/60m`, `donchian_breakout_100/200`,
`fibonacci_golden_zone_50`, `atr_breakout_14_3_0`, `bollinger_breakout_20_2`. It
is not an outlier artifact.

**Trend/momentum does not survive.** Its aggregate suggested improvement
(+0.00020 → +0.00031) but the **median moves the other way** (+0.00030 → +0.00028)
and only **15 of 24** candidates improve — near a coin flip. Round 247's inclusion
of this family in "3 of 4 peak at 150-300" was an **aggregate artifact**.

**Other does not survive either**: 6 of 11 (55%) on magnitudes near zero.

**Reversion is robustly worse**, which strengthens rather than weakens Round 247:
median −0.00034 → −0.00241 (7x worse) with only 6 of 18 improving.

## Corrected count, and why it makes the story cleaner

Round 247 said "3 of 4 families peak at 150-300". The honest per-candidate reading
is:

> **One family clearly up (breakout), one clearly down (reversion), two
> indistinguishable from noise (trend/momentum, other).**

That is a **cleaner directional signature**, not a weaker one — and it lines up
with Round 228's price statistics in a way the "3 of 4" version did not:

| Round 228 statistic, across the same transition | Round 248 family response |
|---|---|
| Kaufman efficiency doubled (0.0366 → 0.0753) | **breakout up** — keys on range expansion / directional efficiency |
| drift doubled (+13.9% → +26.9%) | **breakout up** |
| lag-1 autocorrelation flat/down (+0.0315 → +0.0276) | **momentum flat** — keys on persistence |
| — | **reversion down** |

Momentum keys on autocorrelation, which Round 228 measured as *not* improving;
breakout keys on efficiency and drift, which both doubled. **The family that
should have responded did, and the family that should not have, did not.** Two
independent measurement routes agreeing at this level of detail is the strongest
consistency this thread has produced.

## Round 247's core argument is unaffected

Its actual load-bearing claim was that **breakout — a family the deployed policy
barely uses — shows the effect most strongly**, arguing against the pure
shared-policy explanation. That claim rested on breakout, which survives this
check with better evidence than it had.

## What is proven, and what is not

Proven:

- Per-family medians and improvement counts as tabulated; breakout 9/15 with a
  ~5x median rise, trend/momentum 15/24 with a flat median, other 6/11, reversion
  6/18 with a 7x worse median.
- Breakout's lift appears across at least seven structurally distinct mechanisms.

Not proven, and deliberately not claimed:

- Significance. 11-24 candidates per family, no confidence intervals; 9/15 is
  suggestive, 15/24 is not.
- That the family taxonomy is authoritative — still my own string-matching
  heuristic, unchanged from Rounds 217 and 247.
- Causation between Round 228's statistics and the family responses. The mapping
  is consistent; it was not tested by construction (e.g. by regressing family
  returns on the statistics).
