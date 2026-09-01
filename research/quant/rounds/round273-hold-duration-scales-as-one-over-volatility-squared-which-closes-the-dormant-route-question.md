# QUALIFICATION (Round 276)

This file's law — **hold × σ² ≈ constant** — stands. What does **not** stand is the
step Rounds 273 and 275 took from it to *Portfolio frequency*.

Round 272's identity is `frequency = occupancy × 168 / hold`, so σ² governs frequency
only if occupancy is constant across routes. **It is not** — Round 272 measured it
from 59.6% to 86.7%, a 1.45x spread. Round 276's pre-registered test found three BTC
routes whose volatility spreads 1.3% trading at **5.55 to 9.80/week, a 1.77x spread**.

`bybit BTC` was already this file's worst fit (hold × σ² = 0.2520 against binance
BTC's 0.2263) and its Portfolio frequency deviates far more than its hold does — so
the extra factor acts at the Portfolio layer, not in exit timing. See
`round276-QUALIFICATION-sigma-squared-governs-hold-not-frequency-and-bybit-btc-also-fails-target3.md`.

---

# Round 273 — Hold duration scales as 1/σ², exactly as a fixed fractional barrier predicts. That closes the "dormant route" question.

Classification: **NO-CHANGE** — the behaviour is explained and expected; no system
change is warranted. Read-only production evidence. **Zero containers.**

## The claim Round 272 left untested, tested properly

Round 272 recorded: *"NOT claimed volatility explains the hold ratio — 2.74x observed
against a ~2.4x volatility contrast is suggestive and was NOT tested."* And Round
255's own rule says to measure a variable on **every unit available**, not on the two
the current comparison happens to produce. So: all six routes, and a prediction with
a reason behind it.

**The prediction is not "hold ∝ 1/σ".** Exits are a **fixed fractional** band (stop
1%, take 2%). First-passage time of a random walk to a fixed barrier scales as
`(d/σ)²`, so the prediction is **hold ∝ 1/σ²**, i.e. a slope of **−2** in
log-log. A drift-dominated regime would give −1.

Per-route 5m log-return volatility since 2026-02-01, against mean hold from each
route's retained trade history:

| route | n | mean hold | vol (5m) | hold × σ | **hold × σ²** |
|---|---|---|---|---|---|
| exness BTC | 481 | 10.89h | 0.14218% | 1.548 | **0.2201** |
| binance BTC | 473 | 10.96h | 0.14371% | 1.575 | **0.2263** |
| exness XAU | 392 | 19.17h | 0.11212% | 2.149 | **0.2410** |
| bybit BTC | 311 | 12.14h | 0.14406% | 1.749 | **0.2520** |
| binance XAU | **7** | 29.98h | 0.09058% | 2.715 | **0.2459** |
| bybit XAUT | **1** | 32.92h | 0.08812% | 2.901 | **0.2556** |

## Result

**On the four well-sampled routes (n = 311-481): `log(hold)` against `log(σ)` gives
Pearson r = −0.9756 and a slope of −2.130**, against the theoretical −2.

And **`hold × σ²` is nearly constant across all six routes**: 0.2201 to 0.2556 — a
spread of **16%** across two asset classes, three brokers, and trade counts ranging
from 1 to 481. `hold × σ` spreads by 87% over the same set, so the square is clearly
the right exponent.

The two barely-sampled routes land **inside** the same narrow band as the
well-sampled ones. That is corroboration, not proof — but it is the shape you would
want.

## What this closes

The "dormant route" question that has run since Round 261 is **answered**:
`binance XAU` and `bybit XAUT` trade less often because they are the **least volatile
instruments in the fleet** (0.091% and 0.088% against BTC's ~0.143%), and a fixed
fractional exit band takes ~2.5x longer to be reached at ~0.63x the volatility.

No defect is required to explain it. Combined with Round 271 (4 of 5 routes holding
open positions) and Round 272 (occupancy 63.5%, *above* the healthiest route), the
picture is complete: **those routes are fully participating; their exits simply take
longer, by a mechanical consequence of the band being fixed in price fraction.**

This also retires the seed↔weights confound as an *explanation of trade frequency*.
It does not retire Round 262's seeding observation, which remains a separate P3.

## One consequence worth flagging, not proposing

If Target 3 (≥7/week) is applied **per route**, then under a fixed fractional band a
route's trade frequency is largely determined by its volatility — so low-volatility
instruments will structurally undershoot. Rounds 81-82 tested ATR-scaled protective
bands and **rejected them on cross-broker PnL grounds**; that rejection stands and is
not reopened here. What was never examined is the same lever as a **frequency**
question. Flagged only.

## What is proven, and what is not

Proven:

- Per-route 5m volatilities and mean holds as tabulated.
- Four well-sampled routes: r = −0.9756, log-log slope −2.130.
- `hold × σ²` ranges 0.2201-0.2556 across six routes (16% spread); `hold × σ` spreads
  87%.

Not proven, and deliberately not claimed:

- **A law from four points.** The regression rests on four well-sampled routes, three
  of which are BTC and cluster tightly in volatility — so `exness XAU` carries much of
  the leverage. Four points with one influential observation is not a validated
  scaling law.
- That `binance XAU` and `bybit XAUT` confirm it. Their n is 7 and 1; they are
  *consistent with* the band, which is the weakest form of support.
- That the volatility window matches. Volatility is measured since 2026-02-01 while
  each ledger's trades span its own window — those do not align, and no sensitivity
  check was run.
- That the random-walk model is right. Slope −2.13 is close to −2, but real returns
  are neither driftless nor independent, and the fit was not tested against
  alternatives.
- Anything about PnL, or about whether an ATR band would help frequency. Not tested.
