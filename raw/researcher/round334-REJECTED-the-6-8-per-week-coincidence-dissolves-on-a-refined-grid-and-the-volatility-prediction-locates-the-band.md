# FINE ORDERING: A REASON, NOT JUST A CAVEAT (Round 345)

This file flagged that the ranking among its three middle bands was **not established** because
the net gaps (order **0.018**) might be configuration noise. Round 345 supplies a reason: on the
cost axis a **1.4%** parameter perturbation moved gross by **14.8%** and net by 11% on this same
route. Differences of 0.018 in net are well inside what a nudge of that size can produce.

The bracket conclusion — the optimum lies **between 0.01 and 0.02, not at 0.02** — is a
larger-magnitude statement and is unaffected. Note round 345 measured the cost axis, not the
band axis, so this is a reason for suspicion rather than a proven bound here. See `round345-REJECTED-the-cost-feedback-is-not-a-threshold-a-0-1-bps-fee-change-moves-gross-15-percent-and-the-replay-is-chaotic.md`.

---

# OPTIMUM IS A PLATEAU (Round 335)

The single best point reported here — 0.0125/0.025 at net −0.0121 — is the edge of a **flat
region**, not a peak. 0.0115/0.023 measures net **−0.01225**, the same number to within
1.2%, with matching Sharpe, positive-day ratio, streak and cost÷gross. The
volatility-scaled prediction of **0.0119 falls inside that plateau**, which is stronger
than this file's "located the region, not a point".

This file's worry that the fine ordering might be noise is **resolved on the rising side**:
net climbs −0.2283 → −0.0541 → −0.0122 across 0.01 → 0.011 → 0.0115, steps one to two
orders of magnitude larger than the gaps in question. The falling side (0.015 worse than
both neighbours) remains untested and unexplained. See
`round335-DATA-ISSUE-no-500-day-exness-xau-run-can-pass-the-gate-and-the-band-optimum-is-a-plateau-not-a-point.md`.

---

# GATE VERDICT QUALIFIED (Round 335)

This file reports that the best configuration "still fails the gate" and attributes it to
performance checks. That attribution is **incomplete**. At `--days 500` on `exness XAU` the
gate **also** fails `minimum_holdout_days` (84 observed days against a threshold of 90 — a
CFD's closed weekends make 90 unreachable in this window) and `input_continuity_failed` on
**all seven** non-5m intervals. **No configuration of any kind can pass the gate on this
route at 500 days**, so this file's gate verdicts are not performance verdicts.

The **relative rankings** across bands on this common window are unaffected and stand. See
`round335-DATA-ISSUE-no-500-day-exness-xau-run-can-pass-the-gate-and-the-band-optimum-is-a-plateau-not-a-point.md`.

---

# Round 334 — REJECTED: the "~6.8 per week at both windows" coincidence **dissolves** on a refined grid. The 500-day optimum is **0.0125 at 7.67/week** — within **5%** of the band the volatility argument predicted.

Classification: **REJECTED** — two of my own recent claims (Round 330's optimum location,
Round 332's frequency coincidence) fail once the grid is refined; Round 333's mechanism
gains a quantitative success it had declined to claim. Two bounded Docker sweeps (exactly
the 2-container budget), **XAU-first**.

## The gap Round 333 named

Round 333 confirmed that the 500-900 day segment is 42% calmer and that the same band's
trade-rate ratio matched the volatility ratio to 10% — then stopped short: *"the
optimal-band ratio of 2.0x is a **grid artifact** — nothing was run between 0.01 and
0.02"*, and *"I am **not** claiming the band scales with volatility."*

If it does scale, the arithmetic is explicit: the 900-day optimum is 0.01 and the 500-day
window is **1.190x** more volatile, so the 500-day optimum should sit near
**0.01 × 1.190 = 0.0119** — not at the 0.02 Round 330 reported.

**Pre-registered:** (A) a band near 0.0119-0.015 beats 0.02/0.04's net of −0.0301;
(B) both intermediates are worse, so the 500-day optimum really is at 0.02 and volatility
scaling does not predict band location.

## The refined 500-day grid

`exness XAU/USD`, `--days 500`, deployed costs, identical holdout:

| band | trades | tr/wk | pos-day | streak | Sortino | Sharpe | cost÷gross | gross | **net** | Target 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.01 / 0.02 (deployed) | 126 | 8.95 | 0.429 | 4 | −1.152 | −0.814 | 1.38 | +0.6000 | −0.2283 | pass |
| **0.0125 / 0.025** | 108 | **7.67** | 0.405 | 4 | **−0.066** | **−0.041** | **1.02** | **+0.7121** | **−0.0121** | **pass** |
| 0.015 / 0.03 | 107 | 7.60 | 0.417 | 4 | −0.361 | −0.230 | 1.11 | +0.6499 | −0.0724 | pass |
| 0.02 / 0.04 | 96 | 6.82 | 0.417 | 5 | −0.155 | −0.096 | 1.05 | +0.6067 | −0.0301 | fail |
| 0.04 / 0.08 | 86 | 6.11 | 0.429 | 5 | −0.725 | −0.445 | 1.31 | +0.4460 | −0.1396 | fail |

**Branch A fires. The best net on the refined grid is 0.0125/0.025 at −0.0121** — 2.5x
better than the 0.02/0.04 that Round 330 reported as the optimum.

## Three consequences

**1. The volatility argument predicted the band, not just the direction.** Predicted
0.0119; the best tested point is **0.0125**, within **5%**. Round 333 explicitly declined
to claim this; the refined grid supports it. But **only two intermediate points were
tested and the lower one won**, so the true optimum could sit at or below 0.0119 — the
prediction located the **region**, not a point.

**2. Round 330's "interior optimum at 0.02/0.04" was a coarse-grid artifact.** The
optimum lies between 0.01 and 0.02, which is exactly the interval Round 330 never
sampled and Round 333 flagged.

**3. Round 332's "~6.8 trades/week at both windows" is refuted.** The 900-day optimum is
6.85/week; the 500-day optimum, refined, is **7.67/week** — not 6.82. The coincidence
that looked striking enough to reframe Round 331 was an artifact of where the coarse grid
happened to land. I am withdrawing it.

## And Target 3 is no longer in conflict at this window

Round 328 concluded that the configuration nearest break-even **misses** the 7/week bar.
On the refined grid the best-net configuration trades **7.67/week — it passes Target 3**,
with the best Sharpe (−0.041), the best gross (+0.7121) and the lowest cost÷gross (1.02)
of any configuration measured on this route.

So the Target 1 / Target 3 conflict holds at **900 days** (optimum 6.85/week, fails) and
**not** at 500 days once the grid is fine enough. That is a narrower and more accurate
statement than Round 328's.

**It still fails the gate**: Sharpe −0.041 against +1.0, positive-day ratio 0.405 against
0.55, cost÷gross 1.02 against 0.5, and net is still negative. **No promotion.**

## The caveat that limits all of this

**The fine ordering is not established.** 0.015/0.03 (7.60/week, −0.0724) is worse than
**both** its neighbours — 0.0125 (−0.0121) and 0.02 (−0.0301). The net curve is
non-monotone there, and with magnitudes of 0.01-0.07 those gaps may be
configuration-to-configuration noise rather than signal.

**The robust statement is:** the optimum lies **between 0.01 and 0.02**, not at 0.02, and
the best point found is 0.0125 with net −0.0121. The exact ranking of the three middle
points is **not** established.

## What is proven, and what is not

Proven:

- `exness XAU` at `--days 500`, identical holdout: 0.0125/0.025 → 108 trades / 7.67 per
  week / gross +0.7121 / net −0.0121 / Sharpe −0.041 / cost÷gross 1.02; 0.015/0.03 → 107
  / 7.60 / +0.6499 / −0.0724 / −0.230 / 1.11.
- The best net on the five-point refined grid is at 0.0125, not 0.02.
- The volatility-scaled prediction of 0.0119 is within 5% of that best tested band.
- The 500-day and 900-day optima differ in frequency: 7.67 against 6.85 per week.
- The best-net configuration at 500 days passes Target 3 and still fails the gate on
  Sharpe, positive-day ratio and cost÷gross.

Not proven, and deliberately not claimed:

- **That the band scales with volatility as a law.** One prediction, one route, two
  windows, and a two-point test whose lower point won. It located a region.
- That 0.0125 is the optimum. Nothing was run below it at this window, and the true peak
  could be lower — possibly at the predicted 0.0119 or below.
- **The ranking among 0.0125, 0.015 and 0.02.** The curve is non-monotone and the
  differences are small enough to be noise.
- That any of this transfers to another route or window. `exness XAU` only, and Rounds
  331-332 already showed the optimum moving between windows.
- Any promotion. The best configuration found still fails three gate checks and loses
  money.
