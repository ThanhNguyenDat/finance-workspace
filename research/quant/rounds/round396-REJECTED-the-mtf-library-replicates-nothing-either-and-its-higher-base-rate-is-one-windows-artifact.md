# Round 396 — REJECTED: the MTF library replicates **nothing** across disjoint holdouts either, and its apparently higher base rate is **one window's artifact**.

Classification: **REJECTED** — the pre-registered criterion is not met. Two
containers (the budget), cleaned up. Applies round 393's test to the library
production actually draws from.

## The test, pre-registered with null and power

Following the r393/r394 lesson, both were simulated **before** running:

| threshold | P(null) | power (5 strategies at p=0.70) | power (10 at p=0.60) |
|---|---|---|---|
| ≥ 1 | 0.0520 | — | — |
| **≥ 2** | **0.0014** | **0.573** | **0.682** |
| ≥ 3 | 0.0001 | — | — |

Chosen: **≥ 2 strategies positive on all three disjoint holdouts**.

## The result

`exness XAU`, MTF sweep (`--higher-timeframe-interval 4h`), three disjoint
holdouts:

| run | holdout | scored | positive |
|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | 98 | 8 |
| H2 | 2025-09-04 → 2026-03-04 | 98 | **31** |
| H3 | 2025-03-07 → 2025-09-04 | 98 | 9 |

**Positive on all three: 0.** Null expectation 0.232; P(≥1) = 0.212, so zero is
unremarkable.

**Registered answer: 0 → consistent with chance.** The same verdict r393
returned for the plain library. Neither library replicates.

## The base-rate impression, and why it dissolves

Across all cells the MTF library looks better than the plain one: **48 of 294 =
16.3%**, against 7.6% (r393).

**Excluding H2 it is 17 of 196 = 8.7%** — indistinguishable from the plain
library's 7.6%.

**The entire apparent improvement is one window.** H2 alone is 31 of 98 =
31.6%, nearly four times the other two holdouts. A single period where many
multi-timeframe strategies happened to work is not a property of the library,
and reporting 16.3% without that decomposition would have been the same
interpretation error as round 390's cost ratio.

## An observation I am not calling a finding

H2 is the window where the **Alpha library did best** (31.6% positive) and where
the **Portfolio's own gross was worst** (−0.72458, r391 — the most negative of
its four holdouts). In the period when the most strategies were working, the
Portfolio's selection produced its worst result.

That is one window and two quantities measured on the same data. It is written
down because it is the kind of thing worth re-checking, **not** because a
selection-versus-availability anti-correlation has been established.

## What is proven, and what is not

Proven:

- MTF sweep positive counts 8 / 31 / 9 of 98 on three disjoint holdouts of
  `exness XAU`; zero in the intersection; null expectation 0.232.
- Cell rates: 16.3% overall, **8.7% excluding H2**, 31.6% for H2 alone.
- The plain library's comparable figure is 7.6% (r393).

Not proven, and deliberately not claimed:

- **That the MTF library has no edge.** Power at the chosen threshold was 0.57
  to 0.68 against plausible effects — better than round 393's test but still
  not high. A weak effect would likely have been missed.
- That 8.7% and 7.6% are the same rate. Different populations, different runs,
  and no test performed on the difference.
- Any cause for H2's outlier rate. Not investigated.
- That the Portfolio/Alpha anti-correlation in H2 is real. One window, and both
  quantities come from the same underlying period.

## Named next step

Both libraries have now been tested the same way and neither replicates. The
remaining measurable question on this route is the **single unscored production
configuration** (`mtf_stochastic` trend-5, r395), which is a one-line change
deferred until the current OPS transaction is released. Beyond that, this arc
has run out of backtest questions that a further round can answer — what is left
is forward time.
