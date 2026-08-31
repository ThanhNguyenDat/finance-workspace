# GATE VERDICT QUALIFIED (Round 336)

Gate results in this file come from `exness XAU`, where **all seven non-5m intervals fail
`input_continuity` at both 500 and 900 days**. `minimum_holdout_days` passes at 900 days
(151 observed days) but the continuity checks do not, so **no configuration on this route
can pass the gate at any window measured**.

The band comparisons and relative rankings here are unaffected — a structural check failing
identically across every configuration cannot reorder them. What does not hold is reading
any run in this file as a **gate verdict**. See `round336-DATA-ISSUE-exness-xau-can-never-pass-the-gate-at-any-window-and-binance-btc-is-the-first-gate-eligible-route-measured.md`.

---

# COINCIDENCE WITHDRAWN (Round 334)

The "~6.8 trades/week at both windows" coincidence reported here **does not survive a
refined grid**. The 500-day optimum is not 6.82/week but **7.67/week** (band 0.0125/0.025,
net −0.0121); the 900-day optimum remains 6.85. The apparent match was an artifact of where
the coarse grid happened to land, and I am withdrawing it.

The volatility reading that Round 333 built on the coincidence survives on different
grounds: it **predicted the 500-day optimal band** (0.0119 predicted, 0.0125 best tested —
within 5%). See
`round334-REJECTED-the-6-8-per-week-coincidence-dissolves-on-a-refined-grid-and-the-volatility-prediction-locates-the-band.md`.

---

# Round 332 — NO-CHANGE: at 900 days the **deployed band is the optimum** of five settings. And the optimal *frequency* is **~6.8 trades/week at both windows** — it is the band-to-frequency mapping that moved, not the optimum.

Classification: **NO-CHANGE** — the deployed protective band is the best of five settings
at this window; nothing on this lever needs changing. My two-sided pre-registration
resolved on the interior-optimum branch. Two bounded Docker sweeps (exactly the
2-container budget), **XAU-first**.

## The gap Round 331 named

Round 331 found the deployed band best at 900 days and flagged the obvious hole: *"It is
the best of the **three tested** there; nothing tighter than 0.01/0.02 was run at that
window, so the optimum could sit **below** it."* At 900 days net had improved monotonically
with frequency across 4.29 → 5.04 → 6.85, so tightening further was the open direction.

**Pre-registered, two-sided:** (A) if the monotone trend continues, tighter bands beat the
deployed net of −0.4118; (B) if there is an interior optimum at or near the deployed band,
tighter bands are worse. Either way, record whether any net turns positive.

## The completed 900-day ladder

`exness XAU/USD`, `--days 900`, deployed costs, holdout 2026-03-04 → 2026-08-28:

| band | trades | tr/wk | pos-day | streak | Sortino | Sharpe | cost÷gross | gross | **net** |
|---|---|---|---|---|---|---|---|---|---|
| 0.04 / 0.08 | 109 | 4.29 | 0.391 | 5 | −1.793 | −1.384 | 37.27 | −0.0207 | −0.7931 |
| 0.02 / 0.04 | 128 | 5.04 | 0.397 | 5 | −1.134 | **−0.788** | 1.95 | +0.4933 | −0.4695 |
| **0.01 / 0.02 (deployed)** | 174 | **6.85** | 0.404 | 5 | −1.179 | −0.861 | **1.53** | **+0.7812** | **−0.4118** |
| 0.0075 / 0.015 | 240 | 9.45 | 0.351 | 5 | −3.205 | −2.504 | 2.69 | +0.6660 | −1.1279 |
| 0.005 / 0.01 | 350 | 13.78 | 0.351 | 6 | −4.758 | −3.969 | 2.85 | +0.8681 | −1.6051 |

**Branch B fires.** Tightening past the deployed band makes things clearly worse:
−0.4118 → −1.1279 → −1.6051. The curve is **unimodal with its peak at the deployed
setting**, and **the deployed protective band is the optimum of the five tested at this
window.**

That is worth stating plainly after several rounds of finding things wrong: on this lever,
at this window, **the production configuration is not misconfigured.**

## The observation that reframes Round 331

Round 331 concluded "the optimum moves with the window". With the ladder completed at both
windows, a better reading appears:

| window | optimal band | optimal frequency |
|---|---|---|
| 500 days | 0.02 / 0.04 | **6.82 trades/week** |
| 900 days | 0.01 / 0.02 (deployed) | **6.85 trades/week** |

**The band setting differs; the resulting frequency is 6.82 against 6.85 — within 0.4%.**
So what moved between the windows is the **band-to-frequency mapping**, not the optimal
frequency. A plausible reason is that the market's volatility over the two spans differs,
so the same fractional band produces a different trade rate — but I have not tested that
and am not asserting it.

Two points is two points, and I am flagging this as a **striking coincidence worth
checking**, not a law.

**And ~6.8/week sits just below the 7/week Target 3 bar at both windows** — −2.6% at 500
days, −2.1% at 900. Round 328's Target 1 / Target 3 conflict now holds at both windows
rather than one.

## Two honest details

**Net and Sharpe do not pick the same configuration at 900 days.** Net peaks at 6.85/week
(−0.4118) while Sharpe peaks at 5.04/week (−0.788 against −0.861). On a joint objective
that matters: the two metrics disagree about which band is best, by one step of the
ladder. At 500 days they agreed.

**Nothing is profitable.** Across all nine distinct configurations measured on this route
over the two windows, the best net is **−0.0301** and **none is positive**.

## What is proven, and what is not

Proven:

- `exness XAU` at `--days 900`: 0.0075/0.015 → 240 trades / 9.45 per week / gross +0.6660
  / net −1.1279; 0.005/0.01 → 350 / 13.78 / +0.8681 / −1.6051.
- The 900-day net curve is unimodal with its maximum at the deployed 0.01/0.02
  (−0.4118), falling on both sides.
- Optimal frequency 6.82/week at 500 days and 6.85/week at 900 days, from different band
  settings.
- Nine configurations across two windows, none with positive net.
- At 900 days net peaks at 6.85/week and Sharpe at 5.04/week.

Not proven, and deliberately not claimed:

- **That ~6.8/week is an optimal frequency in any general sense.** Two windows, one
  route, and the grid is coarse — the true peak could sit anywhere between 5.04 and 9.45
  at 900 days. It is a coincidence worth checking, not a finding.
- **Why the band-to-frequency mapping shifts.** A volatility-regime explanation fits;
  it was not tested and no per-window volatility was measured here.
- That the deployed band is optimal in general. It is the best of five at 900 days and
  the *second* best of four at 500 days. "Not misconfigured" is scoped to this lever,
  this route and this window.
- That the round licenses any change. It licenses **no** change — that is the finding.
- Anything about other routes. `binance BTC`'s ladder was never extended below its
  deployed band at any window.
