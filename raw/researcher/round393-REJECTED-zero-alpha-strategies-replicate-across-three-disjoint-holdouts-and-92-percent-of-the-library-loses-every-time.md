# Round 393 — REJECTED: **zero** Alpha strategies are positive on all three disjoint holdouts. And **92.4%** of strategy-holdout cells lose — the library is not a search space with rare winners, it is uniformly losing.

Classification: **REJECTED**. Two containers (the budget), cleaned up. Applies
the disjoint-holdout test one layer up, as round 392 named.

## The result

`exness XAU`, non-gate runs at three cutoffs one holdout-length apart, so the
Alpha sweep's holdouts are **disjoint**:

| run | holdout | candles | positive / 75 |
|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | 174,254 | **4** |
| H2 | 2025-09-04 → 2026-03-04 | 173,939 | **9** |
| H3 | 2025-03-07 → 2025-09-04 | 174,498 | **4** |

(75, not 77: the five `taker_imbalance` entries are correctly excluded on this
route now — r374's defect, fixed and working.)

**Positive on all three: 0.**

Null expectation with the same per-holdout counts: **0.025**. So zero is exactly
what chance predicts.

## My threshold was, again, badly chosen

I registered *"≥ 3 replicate → something is there; ≤ 2 → consistent with
chance"*. The **maximum achievable was 4** — only four strategies are positive on
H1 at all — so reaching 3 would have required three of those four to also land
in both other sets. Against a null expectation of 0.025, a threshold of 3 sounds
strict; in **power** terms it was nearly unreachable.

**This test cannot distinguish "no effect" from "weak effect".** It rules out a
strong one. That is the eighth pre-registration in this arc I have had to record
as mis-specified (r327, r330, r340, r354, r373, r378, r387, r393), and the
pattern is consistent: I keep choosing thresholds by what sounds demanding
rather than by simulating what the test can actually detect.

## The finding that does not depend on my threshold

Positive cells: **17 of 225 = 7.6%**. Per holdout: 5.3%, 12.0%, 5.3%.

**If the strategies were coin flips, roughly 50% would be positive on any given
holdout.** They are positive **7.6%** of the time.

So the Alpha library is not a search space containing rare winners among neutral
candidates. **It is a set of 75 strategies that lose out of sample about 92% of
the time**, at deployed costs. That is consistent with r373's fleet-wide 8.4%
across six routes, now confirmed on genuinely disjoint periods on one route.

Rounds 216 and 217 said friction kills almost everything. This is the same fact
measured properly: the survivors are not being killed by friction from a
positive base — **the base itself is negative**.

## What is proven, and what is not

Proven:

- Three disjoint Alpha holdouts on `exness XAU` with 4, 9 and 4 positive
  strategies out of 75; zero in the intersection; null expectation 0.025.
- 17 of 225 strategy-holdout cells positive (7.6%).
- The `taker_imbalance` exclusion from r374 is active — 75 scored, 5 excluded.

Not proven, and deliberately not claimed:

- **That no Alpha strategy has edge.** The test has too little power to say so,
  and I am saying that rather than dressing a null result as a finding.
- That 7.6% is the right base rate for the library. One route; r373 measured
  8.4% across six routes on a single holdout each, which is close, but neither
  figure is a population estimate.
- That the three holdouts are independent observations. They are disjoint in
  data but each strategy is the same strategy, and the sweep's composition is
  fixed — so this is three looks at one library, not three trials.
- Anything about the other five routes on disjoint holdouts. Not measured.

## Named next step

Stop testing this library for edge. Two things remain worth a round each, and
neither is a parameter search: whether the **frequency trend** (r392, 3.17×
rising toward the present) continues **forward** in real time, and whether the
**deployed three-candidate ensemble on gold** differs from the 75-strategy
library's base rate at all — because if production's own candidates lose 92% of
the time out of sample too, the question stops being which strategy to pick.
