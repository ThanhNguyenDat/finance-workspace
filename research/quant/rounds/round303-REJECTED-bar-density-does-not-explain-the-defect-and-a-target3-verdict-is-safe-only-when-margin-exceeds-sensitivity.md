# CORRECTED (Round 305)

The `binance BTC` sensitivity used here — **1.04%** from a one-day perturbation, giving
a **33x** cushion over its Target 3 margin — is **15x too small**. Extending the ladder
to 270 and 280 days (Round 305) produced a **−42 trade** nesting violation and a rate
spread of **15.9%**, which equals that route's smallest margin (+15.9%). The pass still
holds on 4 of 4 windows; the *cushion* does not. Read every one-day sensitivity in this
file as a floor. See
`round305-REJECTED-binance-btc-sensitivity-is-15x-the-one-day-figure-and-its-safe-margin-is-gone.md`.

---

# CORRECTED (Round 304)

This file describes the defect as *"an approximately **fixed absolute** disturbance of
a few trades"* (5-8 across three routes). **That is too small.** Extending the
`exness XAU` ladder to 370 and 380 days produced a **−20 trade** nesting violation over
a single +10-day step — 5.4% of the count. The 5-8 figure is a **floor observed at
one-day perturbations**, not the confound's scale, and every per-route sensitivity in
this file is therefore a **lower bound**.

The margin-versus-sensitivity rule and the rejection of bar density both stand;
`exness XAU`'s sensitivity is revised from 5.5% to **9.5%**, and its Target 3 verdict
is now shown to flip outright — 4 passes and 2 fails across six same-day windows. See
`round304-REJECTED-the-confound-is-not-a-fixed-few-trades-it-reaches-20-and-the-xau-target3-verdict-flips-with-window-choice.md`.

---

# Round 303 — REJECTED: bar density does not explain the defect. `bybit XAUT` is 24/7 like BTC and moves **+8.57%** on one day. The confound is a roughly **fixed absolute** perturbation.

Classification: **REJECTED** — my pre-registered prediction failed at the threshold I
set. Two bounded Docker sweeps (exactly the 2-container budget), XAU-first. Third route
in the perturbation series; extends Rounds 301-302.

## The question Round 302 left open

Round 302 found the measurement defect small on `binance BTC` (+1.04% on one day) and
large on `exness XAU` (a *negative* response, 5.5% spread), and said plainly: *"I did
not test any of these and I am not proposing a mechanism."* The two routes differ in
instrument, bar density (288 against 194/day), trade count and candidate set — four
confounded differences.

`bybit XAUT` separates two of them: it is **XAU** like Exness, but trades **24/7 at
288.0 bars/day** like BTC, with no session gaps.

**Registered before running:** if bar density and session continuity drive the defect
magnitude, `bybit XAUT` behaves like `binance BTC` — the one-day perturbation moves the
Target 3 rate by **< 2%** and `one_target` moves **non-negatively**. Refuted at
**≥ 5%**.

I predicted the small-defect outcome, reasoning that `exness XAU`'s 385 verified
session gaps repeatedly desynchronise the required intervals and make the cumulative
Alpha performance driving the weights noisier.

## The result: refuted

| `--days` | candles | **`one_target`** | legacy | grid | cost | decisions | Alpha 5m |
|---|---|---|---|---|---|---|---|
| 260 | 74,878 | **89** | 104 | 1,688 | 28 | 74,342 | 216,999 |
| **261** | 75,166 | **97** | 113 | **2,262** | 35 | 74,630 | 217,823 |

One extra day: **+288 candles, `one_target` +8** against an expected content of
**0.34 trades** — a **23x** overshoot. **The Target 3 rate moves +8.57%**, above my
refutation threshold. `legacy_grid` moves 1,688 → 2,262, **+34% from a single day**.

**Bar density and session continuity are rejected as the explanation.** A 24/7 XAU
route with 288.0 bars/day and zero session gaps has a *larger* relative defect than the
gap-ridden 194 bars/day route.

## What the three routes do show

| route | instrument | bars/day | trades | **1-day Δ trades** | expected | **Δ rate** | **relative impact** |
|---|---|---|---|---|---|---|---|
| `binance BTC` | BTC | 288.0 | 350 | **+5** | 1.37 | +1.04% | **1.4%** |
| `exness XAU` | XAU | 193.8 | 374 | **−7** | 0.11 | −2.14% | **1.9%** |
| **`bybit XAUT`** | **XAU** | **288.0** | **89** | **+8** | 0.34 | **+8.57%** | **9.0%** |

**The absolute perturbation is nearly the same on all three routes — 5, 7 and 8
trades — across a 4x range of trade counts, a 1.5x range of bar densities, two
instruments and both market types.** What differs is what that fixed handful of trades
is a fraction *of*.

So the defect reads as an approximately **fixed absolute** disturbance of a few trades,
whose damage is **inversely proportional to how many trades a route makes**. That is a
description of three routes, not a law — three points, no error bars, and one
perturbation each — but it explains Round 302's contrast without needing bar density,
and it makes the routes with the fewest trades the least measurable.

## The practical rule this yields for Target 3

A Target 3 verdict is trustworthy exactly when the **margin over the bar exceeds the
route's perturbation sensitivity**:

| route | rate | margin over 7/week | sensitivity | verdict |
|---|---|---|---|---|
| `binance BTC` | 9.42/week | **+34.6%** | 1.04% | **pass — safe** |
| **`bybit XAUT`** | **2.40/week** | **−65.8%** | 8.57% | **fail — safe** |
| `exness XAU` | 7.12-7.52/week | **+1.7% to +7.4%** | 5.5% | **undetermined** |

A large *relative* defect does not by itself invalidate a verdict: `bybit XAUT`'s 8.57%
sensitivity cannot bridge a 65.8% gap, so its **fail is as safe as `binance BTC`'s
pass**. Only routes near the bar are endangered — which at present is `exness XAU`
alone.

And `exness XAU` is worse placed than Round 302 recorded. Its 260-day count (254,
Round 289) gives **6.84/week — below the bar** — while its 360-day count gives
**7.27/week, above it**. **The same route passes or fails depending only on how long a
window is requested.** "Undetermined" is if anything generous.

## What is proven, and what is not

Proven:

- `bybit XAUT` at the deployed config, same day, same endpoint: `one_target` = 89 at
  260 days and 97 at 261; rates 2.396 and 2.602/week; change **+8.57%**.
- 74,878 candles over 260 days = **288.0 bars/day**, matching the crypto routes.
- `legacy_grid` 1,688 → 2,262 and `execution_cost` 28 → 35 on one extra day.
- Alpha 5m 216,999 → 217,823 (+824 over 288 candles = 2.861/candle).
- Absolute one-day `one_target` movements across the three routes measured so far:
  +5, −7, +8.
- `exness XAU` reports 6.84/week at 260 days and 7.27/week at 360 days.
- `bybit XAUT` realized_pnl −0.2506 and −0.3081; it loses money, as every route does.

Not proven, and deliberately not claimed:

- That the confound is a **fixed** absolute quantity. Three routes, one perturbation
  each, values 5-8. That is a pattern worth naming and nothing stronger; a fourth route
  could break it, and I have not tested how it scales with the size of the perturbation
  either.
- **Any mechanism** for the defect's magnitude. Bar density and session continuity are
  now excluded; trade count is *consistent* with the data but untested as a cause, and
  candidate-set differences remain entirely unexamined.
- That `bybit XAUT`'s Target 3 fail is new. Rounds 289-292 already had it failing; what
  is added is that the fail is **robust to the defect**, which was not previously known.
- Anything about `exness BTC`, `bybit BTC` or `binance XAU`. Three of six routes still
  have no perturbation run.
- That any differenced deep slice is rescued. Unchanged from Rounds 300-302.
