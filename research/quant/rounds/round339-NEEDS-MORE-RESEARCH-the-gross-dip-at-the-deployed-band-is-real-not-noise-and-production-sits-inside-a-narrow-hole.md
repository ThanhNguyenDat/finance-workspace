# REFINED TO A SMOOTH TROUGH, AND THE INVARIANCE IS CLOSED (Round 340)

**1. "Narrow hole" is refined to a smooth trough.** Filling in the shoulders at 0.009
(**+0.1561**) and 0.015 (**+0.1414**) makes the seven-band gross sequence perfectly unimodal —
0.2662 > 0.2518 > 0.1561 > −0.0135 > −0.0682 < +0.1414 < +0.2590 — with monotone descent into
the minimum and monotone ascent out of it. That strengthens this file's conclusion rather than
weakening it: noise does not produce a monotone descent across three points followed by a
monotone ascent across three more.

**2. The 37/101 invariance is closed as coincidence.** The day *sets* differ — 0.008 and
0.0125 share only 29 of their 37 positive days (Jaccard 0.644). Same count, different days.

**3. New, and not visible from the metrics alone:** `2026-06-10` is the worst day at **every**
band measured, and at 0.02/0.04 it is **358.6 percent** of the entire net loss. See `round340-NEEDS-MORE-RESEARCH-the-hole-is-a-smooth-unimodal-trough-across-seven-bands-and-one-day-dominates-every-configuration.md`.

---

# Round 339 — NEEDS-MORE-RESEARCH: the gross dip at the deployed band is **real, not noise** — it extends to the neighbour above. On `bybit XAUT` the production band sits inside a narrow **0.01-0.0125 hole** where gross collapses from +0.25 to zero. Restoring gross does **not** restore net.

Classification: **NEEDS-MORE-RESEARCH** — a reproducible structural feature, unexplained, and
not actionable as measured. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**, on the gate-eligible route.

## The uncertainty Round 338 named about its own result

Round 338 measured gross +0.2662 at 0.005, **−0.0135 at the deployed 0.01**, and +0.2590 at
0.02, and wrote: *"Not claimed the deployed band's −0.0135 is noise. It is **consistent** with
noise of order ±0.28 given its neighbours; **I ran no repeat measurement** and cannot separate
noise from a genuine local dip."*

Two containers on the bands immediately either side of deployed settle it.

**Pre-registered, two-sided:**
- **(A) noise** — both neighbours return gross in **[+0.1, +0.4]**, near the +0.26 plateau,
  leaving the deployed band an isolated outlier.
- **(B) genuine dip** — at least one neighbour also returns gross in **[−0.15, +0.1]**,
  establishing a real low-gross region around the deployed band.

## Branch B fires — the dip has width

`bybit XAUT/USDT` spot, `--days 500`, identical holdout (2026-05-22 → 2026-08-30, 28,799
candles, 101 observed days), no continuity failures on any run:

| band | trades | tr/wk | **gross** | cost drag | net | Sharpe | pos-day | streak | cost÷gross |
|---|---|---|---|---|---|---|---|---|---|
| 0.005 / 0.01 | 148 | 10.36 | **+0.2662** | 1.0998 | −0.8336 | −3.074 | 0.386 | 5 | 4.131 |
| **0.008 / 0.016** | 84 | 5.88 | **+0.2518** | 0.7047 | −0.4529 | −1.655 | 0.366 | 13 | 2.799 |
| 0.01 / 0.02 **(deployed)** | 64 | 4.48 | **−0.0135** | 0.4069 | −0.4204 | −1.397 | 0.366 | 13 | 30.24 |
| **0.0125 / 0.025** | 48 | 3.36 | **−0.0682** | 0.3162 | −0.3843 | −1.279 | 0.366 | 13 | 4.639 |
| 0.02 / 0.04 | 28 | 1.96 | **+0.2590** | 0.3185 | −0.0595 | −0.171 | 0.406 | 21 | 1.230 |

`0.008` returns **+0.2518** — branch A's range. `0.0125` returns **−0.0682** — branch B's
range. **The dip is not a single point.** Two adjacent bands, 0.01 and 0.0125, both sit at
roughly zero gross, bracketed on both sides by +0.25 to +0.27.

**So `bybit XAUT` has a narrow hole spanning 0.01-0.0125 in which the route's gross edge
collapses to nothing — and the deployed production band is inside it.** Round 338's
±0.28-noise reading is withdrawn: noise does not produce two adjacent low readings between
three high ones.

## Why this is not an actionable improvement

Moving out of the hole restores gross and **does not restore net**:

| move | gross | cost | net vs deployed |
|---|---|---|---|
| deployed 0.01 | −0.0135 | 0.4069 | −0.4204 |
| tighten to 0.008 | +0.2518 (**+0.265**) | 0.7047 (**+0.298**) | −0.4529 (**worse by 0.032**) |

The +0.265 of recovered gross is **more than consumed** by +0.298 of additional cost, because
tightening the band raises frequency from 4.48 to 5.88 per week and cost scales with trade
count. That is the standing result from Round 274 onward reproduced exactly: **frequency
bought by moving the band is paid for proportionally.**

Widening to 0.02 does improve net (−0.0595), but Round 338 already established what that
costs on the joint objective — 1.96 trades/week against a 7.0 bar and a **21-day** negative
streak against a threshold of 5.

**So the hole is a real property of the route's decision stream, and no band tested converts
it into a joint-objective improvement.**

## An invariance I cannot explain

Three of the five bands — 0.008, 0.01 and 0.0125, at **84, 64 and 48 trades** — return
**identical** positive-day ratios (0.36634 = exactly 37 of 101 days) and **identical**
maximum negative-day streaks (13). The other two bands differ (39/101 and 41/101; streaks 5
and 21).

Three configurations with a 1.75x spread in trade count landing on exactly the same daily
classification is worth recording. **I did not inspect the daily results array**, so I cannot
say whether the same days are profitable in each or whether it is arithmetic coincidence.

## What is proven, and what is not

Proven:

- `bybit XAUT` @500, identical holdout, no continuity failures: 0.008/0.016 → 84 trades /
  5.880 per week / gross +0.25180 / cost 0.70466 / net −0.45287 / Sharpe −1.6546 / Sortino
  −2.2826 / streak 13; 0.0125/0.025 → 48 / 3.360 / **−0.06816** / 0.31615 / −0.38431 /
  −1.2786 / −1.7864 / streak 13.
- Two adjacent bands (0.01, 0.0125) have gross at roughly zero; the three surrounding bands
  (0.005, 0.008, 0.02) are all between +0.2518 and +0.2662.
- Tightening from deployed to 0.008 recovers +0.265 gross and adds +0.298 cost, leaving net
  0.032 **worse**.
- Positive-day ratio 37/101 and streak 13 are identical at 0.008, 0.01 and 0.0125.

Not proven, and deliberately not claimed:

- **Any cause for the hole.** Five points on a grid establish that it exists and roughly where;
  nothing here explains why a barrier between 0.01 and 0.0125 should destroy this route's
  gross edge. I have no mechanism and am not proposing one.
- That the hole's edges are at 0.008 and 0.02. Nothing was run between 0.008 and 0.01, or
  between 0.0125 and 0.02 — the boundaries are **where the grid stops**.
- That the hole exists on any other route. **One route, one window.** `exness XAU`'s refined
  grid (Rounds 334-335) showed no such collapse in the same band range, but it is a different
  instrument, venue and gross regime, so that is not a control.
- That the hole is stable in time. **One window**, and Rounds 331-334 already showed band
  behaviour moving with the window on the other route.
- That the deployed band being inside it means production is misconfigured. Net at 0.008 is
  **worse** than at deployed, and the only band with better net fails frequency and streak
  badly. **Nothing here is a recommendation to change the deployed configuration.**
- Any promotion. No tested band improves the joint objective over deployed.
