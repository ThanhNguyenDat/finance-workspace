# Round 255 — CORRECTION: with 7 bands instead of 3, drift *does* explain the edge; the window is neither unique nor predictable

Classification: **REJECTED** — the operational premise of the Round 242-254 thread
fails on both counts, and this round corrects my own conclusions in Rounds 252,
253 and 254. Two bounded Docker sweeps (XAU only), one read-only Timescale query.

## What made this possible

The CLI has **no as-of/end-date flag** — every window ends at "now". But `train`
and `validation` can be *placed* anywhere by choosing `--days` and the ratios, so
two runs (`--days 1050` at 1/7, `--days 750` at 0.2) yield four extra 150-day
bands further back. With Round 254's three, that is **seven contiguous 150-day
bands covering 2023-10-15 → 2026-08-28**, boundaries lining up to within a day.

exness XAU 4h, zero cost, directional-mechanism median edge, dedup rule unchanged:

| band | period | drift | efficiency | edge |
|---|---|---|---|---|
| B1 1050-900d | 2023-10-15 → 2024-03-13 | +12.81% | 0.0964 | +0.00032 |
| B2 900-750d | 2024-03-13 → 2024-08-09 | +11.92% | 0.0702 | +0.00148 |
| B3 750-600d | 2024-08-09 → 2025-01-08 | +9.03% | 0.0599 | +0.00177 |
| **B4 600-450d** | 2025-01-08 → 2025-06-06 | **+26.72%** | 0.1277 | **+0.01134** |
| B5 450-300d | 2025-06-05 → 2025-10-31 | +19.62% | 0.1005 | +0.00304 |
| **B6 300-150d** | 2025-10-31 → 2026-04-01 | +19.63% | 0.0560 | **+0.00987** |
| B7 150-0d | 2026-04-01 → 2026-08-28 | −6.90% | 0.0248 | −0.00018 |

## Finding 1 — the "favourable window" is not unique. It is rank #2 of 7.

Rounds 242-254 treated the 300-150 day band as a special shared event. **B4
(600-450 days ago) is higher: +0.01134 against B6's +0.00987.** Thirteen rounds
were spent characterising the second-best band in the sample because the analysis
never looked back further than 450 days.

## Finding 2 — CORRECTION: drift magnitude *does* explain the ordering

I rejected drift as an explanation three times: Round 252 (2 bands × 2
instruments), Round 253 (relabeling, 2 bands), Round 254 ("natural control", 3
bands). **With seven bands the relationship is nearly monotone.**

| band | B1 | B2 | B3 | B4 | B5 | B6 | B7 |
|---|---|---|---|---|---|---|---|
| \|drift\| rank | 4 | 3 | 2 | 7 | 5 | 6 | 1 |
| edge rank | 2 | 3 | 4 | 7 | 5 | 6 | 1 |

Only B1 and B3 are transposed. **Spearman +0.857, exact permutation p = 0.0238**
(all 5040 orderings). Efficiency is much weaker: +0.500, p = 0.267.

**Round 254's "natural control" was over-read, and I called it "the strongest
single piece of evidence in this thread".** It compared B5 (+19.62%, +0.00304) and
B6 (+19.63%, +0.00987) and concluded drift cannot matter because the edge differs
3.25x at identical drift. Under the rank relationship that pair is ordered
*correctly* — 19.62 < 19.63 and +0.00304 < +0.00987. What is anomalous is the
**magnitude**, not the direction: 0.01 pp of drift alongside 3.25x of edge. So the
honest statement is narrower than either of my previous ones: **drift magnitude
ranks the bands well and does not pin down the edge level.**

This is the Round 230 failure mode again, one level up. That rule said "report all
three splits and the spread, or report nothing." I obeyed it for splits and broke
it for bands: I declared a variable irrelevant from the two or three bands that
happened to be in one run, without measuring it across every band obtainable.
**Extension: before calling a variable irrelevant, measure it on every band the
tooling can reach, not on the bands the current invocation happens to produce.**

## Finding 3 — the decisive one: none of it is available in advance

Everything above is **contemporaneous**. A band's drift is known only once the
band is over. The tradable question is whether anything observable at the *start*
of a band predicts it:

| predictor | → edge(t+1) | Spearman | Pearson | perm p |
|---|---|---|---|---|
| edge(t) | | +0.086 | −0.358 | 0.919 |
| \|drift\|(t) | | −0.371 | −0.255 | 0.497 |
| drift(t) | | −0.371 | −0.255 | 0.497 |
| efficiency(t) | | +0.314 | −0.014 | 0.564 |

**Nothing predicts the next band.** For reference the contemporaneous figure is
+0.857. The two best bands are each followed by a collapse: B4 +0.01134 → B5
+0.00304, and B6 +0.00987 → B7 −0.00018.

The crude walk-forward rule, stated with its arms:

- trade the next band only after a high-\|drift\| band → next-band edges
  +0.00304, +0.00987, −0.00018 (mean **+0.00424**)
- otherwise → +0.00148, +0.00177, +0.01134 (mean **+0.00486**)

**The rule is worse than not using it.** Three observations per arm — this has no
power to detect a small benefit, but it certainly shows no large one.

## Where this leaves the thread

Round 254 named the question that decides whether this line is worth continuing:
*"is it anything that could be known in advance rather than only in hindsight? A
window identifiable only after the fact is worth nothing operationally."*

**The answer is that it is only identifiable in hindsight.** The band effect is
real, it is largely a restatement of how much the instrument trended during the
band, and it is not forecastable one band ahead by any of the four quantities
tested. Combined with Finding 1 — the window was not even the best one — the
Round 242-254 direction is closed for operational purposes.

Nothing here changes the standing result that loss ≈ trade count × a near-constant
and that no Portfolio-construction lever improves per-trade economics. All figures
are gross of fees, slippage and funding.

## What is proven, and what is not

Proven:

- Seven contiguous 150-day XAU 4h bands with the drift, efficiency and
  directional-median-edge values tabulated above, boundaries contiguous to within
  a day.
- B4 (600-450d) edge +0.01134 exceeds B6 (300-150d) +0.00987; B6 ranks #2 of 7.
- \|drift\| vs edge Spearman +0.857, exact permutation p = 0.0238; efficiency
  +0.500, p = 0.267.
- All four lagged predictors of the next band's edge are non-significant, three of
  the four negative in Pearson terms.
- The high-\|drift\| walk-forward rule's arms: mean +0.00424 after high against
  +0.00486 otherwise.

Not proven, and deliberately not claimed:

- That this generalises beyond XAU. **This round is one instrument.** BTC was not
  re-run — the two-container budget went to extending XAU's history, per the
  standing XAU-first priority.
- That drift *causes* the edge. Rank agreement on seven non-overlapping periods
  from one price path is suggestive, not causal, and adjacent bands can share a
  regime.
- That signed drift is what matters. **Six of the seven bands have positive
  drift**, so drift and \|drift\| are nearly the same variable in this sample and
  cannot be separated. Under the \|drift\| reading BTC's three Round 254 bands give
  Spearman +0.5 — the same direction, on three points with no power. That is
  recorded as an observation, not a claim, and it is the obvious next test.
- Any tradable edge. Every figure is zero-cost and gross.
- That no ex-ante predictor exists. Four were tested on six transitions; that is a
  weak search, and it rules out a strong effect, not a subtle one.
