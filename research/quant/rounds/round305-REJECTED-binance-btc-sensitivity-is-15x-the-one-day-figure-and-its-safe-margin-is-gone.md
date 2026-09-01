# QUALIFIED (Round 312)

`binance BTC`'s Target 3 pass recorded here is a property of **260-280-day windows**.
At **900 days** the same route returns **6.704/week (−4.2%, FAIL)** and at **901 days**
**7.085/week (+1.2%, pass)** — the bar falls between two windows one day apart. The
*level* at depth may be genuine history (Round 293 measured this route's deeper slices
lower); the *straddle* is measurement noise. Read the verdict as **pass on recent
windows, undetermined at depth**. See
`round312-REJECTED-the-confound-grows-with-depth-one-day-moves-50-trades-at-900d-and-binance-btc-straddles-the-bar.md`.

---

# Round 305 — REJECTED: `binance BTC`'s sensitivity is **15x** the one-day figure. Its Target 3 pass survives every window tested, but the "33x safety margin" is gone.

Classification: **REJECTED** — my pre-registered prediction fails on its spread
criterion while holding on its pass criterion, and I report both. Two bounded Docker
sweeps (exactly the 2-container budget). BTC-scoped: `exness XAU` has now been measured
at six window lengths and its verdict is settled as undetermined, while `binance BTC`
carries the fleet's only remaining safe pass — so that is where the budget goes.

## The limit Round 304 named

Round 304 closed with: *"`binance BTC` and `bybit XAUT` were not re-run with a +10-day
perturbation; their sensitivities are **one-day figures and therefore lower bounds**,
not measurements of their worst case."*

`binance BTC` is the route that matters. Round 302 measured it at **+1.04%** on one day
and Round 303 built the fleet rule on that: margin **+34.6%** against sensitivity
1.04%, a **33x** cushion, *"pass — safe"*. If that 1.04% is a floor, the cushion is
unknown.

**Registered before running:** the pass is robust — every window in the ladder
260/261/270/280 stays **above 7/week**, and the rate spread stays **under 10%** of its
mean. Refuted if any window falls below 7/week **or** the spread exceeds 15%.

## The result: the pass holds, the cushion does not

| `--days` | candles | **`one_target`** | legacy | grid | cost | Alpha 5m | **rate/week** | margin |
|---|---|---|---|---|---|---|---|---|
| 260 | 74,878 | 350 | 502 | 4,584 | 52 | 315,121 | 9.423 | +34.6% |
| 261 | 75,166 | 355 | 503 | 4,578 | 53 | 316,454 | 9.521 | +36.0% |
| **270** | 77,758 | **313** | 439 | 4,086 | 22 | 327,558 | **8.115** | **+15.9%** |
| **280** | 80,638 | **334** | 475 | 4,438 | 28 | 339,918 | 8.350 | +19.3% |

| counter | sequence | violations |
|---|---|---|
| **`one_target`** | 350 / 355 / **313** / 334 | 1 — **`−42`** at 261→270 |
| `legacy_selected_rule` | 502 / 503 / 439 / 475 | 1 — `−64` |
| `legacy_grid` | 4,584 / 4,578 / 4,086 / 4,438 | 2 — `−6`, `−492` |
| `execution_cost` | 52 / 53 / 22 / 28 | 1 — `−31` |
| **Alpha 5m** | 315,121 → 339,918 | **0** |
| candles | 74,878 → 80,638 | **0** |

**Both halves of the prediction must be reported.**

- **The pass holds: 4 of 4 windows clear the bar**, the weakest at 8.115/week.
- **The spread is 15.9% of the mean — above my 15% refutation threshold**, so the
  prediction is refuted, and the sensitivity is **15.3x** the 1.04% one-day figure.

A single +9-day step drops the count by **42 trades** where the genuine content of nine
days is about **+12**. Over 260→280 days the true content is **+26.9 trades**; the
measure returns **−16**. That is a 43-trade discrepancy on the route Round 302 called
the well-behaved one. The Alpha control and the candle count remain strictly monotone,
as in every round of this series.

## What this does to the fleet rule

Round 303's rule — a verdict is trustworthy when the margin exceeds the sensitivity —
survives. What changes is the numbers fed into it:

| route | margin over bar | **sensitivity (best known)** | margin ÷ sensitivity | verdict |
|---|---|---|---|---|
| `binance BTC` | +15.9% to +36.0% | **15.9%** (4 windows, ≤20-day span) | **1.0x** *(was 33x)* | **pass — no longer comfortable** |
| `bybit XAUT` | −65.8% | ≥8.57% (**one day only**) | ≤7.7x | fail — safe on a floor |
| `exness XAU` | −2.4% to +7.4% | 9.5% (6 windows, ≤20-day span) | 0.8x | undetermined — demonstrated |

**`binance BTC`'s smallest margin and its sensitivity are now the same number.** Its
pass was not refuted — every window measured clears the bar — but it is no longer
protected by a wide cushion, and a window length I have not tried could plausibly bring
it to the bar.

`bybit XAUT`'s "safe fail" now rests on the same kind of one-day floor that just proved
15x too small on BTC. I am **not** claiming its fail is in doubt — a 65.8% gap is wide —
only that its 7.7x cushion is computed against a figure of the type that has already
failed once. How the growth factor behaves is not predictable from what I have:
`binance BTC` grew **15.3x** from one day to a 20-day span while `exness XAU` grew only
**1.7x** over the same extension.

## What is proven, and what is not

Proven:

- `binance BTC` at the deployed config, same day, same endpoint: `one_target` = 350 /
  355 / **313** / 334 at 260 / 261 / 270 / 280 days.
- One nesting violation of **−42 trades** at the +9-day step; `legacy_selected_rule`
  −64, `legacy_grid` −492, `execution_cost` −31 at the same step.
- Alpha 5m 315,121 → 339,918 and candles 74,878 → 80,638, both strictly monotone —
  zero violations.
- Rates 9.423 / 9.521 / 8.115 / 8.350 per week; spread **15.9%** of the mean; all four
  above 7/week, minimum margin **+15.9%**.
- True content of 260→280 days at the 260-day rate is +26.9 trades; observed −16.
- realized_pnl −3.399 / −3.562 / −1.764 / −1.852 — negative on every window.

Not proven, and deliberately not claimed:

- That `binance BTC` fails Target 3, or is about to. **Four of four windows pass.** The
  claim is that the safety margin Round 302-303 reported was computed from a figure
  15x too small, not that the verdict has changed.
- That 15.9% is the route's true sensitivity. It is the spread over four windows
  spanning 20 days; a wider span was not tried, and Round 304 already showed these
  figures only grow.
- **Any scaling law** for the growth factor. 15.3x on one route against 1.7x on another
  over the same extension — two points, no model, and I am not proposing one.
- That `bybit XAUT`'s fail is in doubt. It is not tested; the caveat above is about the
  *provenance* of its cushion, not about the verdict.
- Anything about `exness BTC`, `bybit BTC` or `binance XAU`. Three of six routes still
  have no perturbation run at all.
- That the PnL improvement at longer windows (−3.40 → −1.76) means anything. It is the
  same unreliable comparison across window lengths that this whole series is about, and
  every value is a loss.
