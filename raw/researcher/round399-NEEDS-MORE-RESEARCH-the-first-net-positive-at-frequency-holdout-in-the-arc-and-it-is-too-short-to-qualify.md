# Round 399 — NEEDS-MORE-RESEARCH: the **first holdout in the arc that is both net-positive and at Target 3 frequency** — and it is **too short to qualify**.

Classification: **NEEDS-MORE-RESEARCH**. Two containers (the budget), cleaned up.

## The registered question

Round 398 pooled seven disjoint holdout gross readings and found the 95%
interval includes zero. Registered: does that survive at n = 9?

| | mean | sd | se | 95% interval | |
|---|---|---|---|---|---|
| n = 7 (r398) | +0.08923 | 0.59160 | 0.22360 | [−0.34903, +0.52749] | includes zero |
| **n = 9 (now)** | **+0.19085** | 0.55193 | 0.18398 | **[−0.16974, +0.55144]** | **includes zero** |

**Registered answer: yes — the conclusion is stable as n grows.** The interval
narrowed by 18% and the mean roughly doubled, but zero remains inside.

Gross is now positive on **6 of 9** holdouts, which is a different impression
from the earlier "alternates around zero" — but the mean is still not separable
from zero because the spread is large, and 6 of 9 is not itself unusual.

## The two new points, and the one that matters

| route | holdout | days | gross | **net** | trades/wk |
|---|---|---|---|---|---|
| `bybit XAUT` | 2025-12-28 → 2026-03-04 | **65.3** | +0.46972 | **+0.06359** | **7.073** |
| `exness BTC` | 2025-09-05 → 2026-03-04 | 180.0 | +0.62328 | −0.04486 | 4.162 |

**`bybit XAUT`'s holdout is net-positive (+0.06359) at 7.073 trades/week.** That
clears the Target 3 bar of 7.0 **and** is profitable — the first holdout in 194
iterations to do both at once.

**And it does not qualify.** The holdout is **65.3 calendar days** against the
gate's `minimum_holdout_days` threshold of **90**. The gate rejects it as too
short, and it is short because `bybit XAUT`'s history runs out: a 900-day
request at that cutoff loads far less than 900 days.

So the arc's first joint-objective success is on a sample the gate itself
declares insufficient. That is not a technicality to argue around — 65 days is
where a positive result is most likely to appear by chance, which is precisely
why the threshold exists.

## A correction to round 398's estimate

Round 398 said the four untested routes would yield "six or seven more points in
two rounds". **Data horizons make that optimistic.** Every route's history stops
around 2024-03-14, so earlier cutoffs load progressively less: this round's
`bybit XAUT` holdout came out at 65 days rather than 180. Usable additional
points are closer to **two or three**, not six or seven.

## What is proven, and what is not

Proven:

- The two new holdout rows above, pinned cutoffs, Portfolio-faithful gate path.
- Pooled n = 9: mean +0.19085, 95% interval [−0.16974, +0.55144], includes zero.
- 6 of 9 holdout gross readings positive.
- `bybit XAUT`'s 65.3-day holdout is below the gate's 90-day minimum.

Not proven, and deliberately not claimed:

- **That `bybit XAUT` has a profitable configuration.** One holdout, 65 days,
  below the qualifying minimum, and r397 established that single-holdout
  readings do not characterise routes.
- **That gross edge is positive.** 6 of 9 and a mean of +0.19 with an interval
  spanning [−0.17, +0.55] is not a positive result; it is a wider-than-useful
  estimate that happens to sit above zero.
- That the interval is trustworthy at face value. The nine holdouts come from
  four routes with overlapping fitted histories, so the standard error assumes
  more independence than exists and is optimistic.
- That +0.06359 is meaningful in magnitude. It is 0.06 against holdout swings of
  ±1.8 elsewhere in the series.

## Named next step

Re-run `bybit XAUT` at a cutoff that gives it a **≥ 90-day** holdout — its H1
window was 180 days, so a cutoff between the two would produce a qualifying
length. If the net stays positive at a qualifying length and at frequency, it is
the first result in this arc worth a promotion discussion; if it does not, the
65-day reading was the short-sample effect the threshold exists to catch.
