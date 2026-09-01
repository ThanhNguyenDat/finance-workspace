# QUALIFICATION (Round 289)

This file's table presents Target 3 status **as a property of each route**. For three
of the six that reading does not hold.

Round 289 differenced the nested windows and found the trade rate is **non-stationary**
on exactly the three routes whose verdicts moved: sub-period spreads of **3.48x
(binance XAU), 4.14x (bybit BTC), 4.62x (bybit XAUT)** against 1.12-1.24x on the three
stable routes. **In their busy slices those three reach 7.17, 11.03 and 11.20 per
week — at or above the bar.**

So for `binance XAU`, `bybit BTC` and `bybit XAUT`, "fails Target 3" describes **the
averaging window**, not the route: they alternate between near-dormant stretches
(2.1-3.1/week) and busy ones (7.2-11.2/week).

This file's numbers stand, and the two passes plus `exness XAU`'s on-the-threshold
reading are unaffected. See
`round289-the-window-effect-is-non-stationarity-and-the-quiet-routes-clear-the-bar-in-their-busy-slices.md`.

---

# Round 285 — The complete fleet Target 3 table on one matched window: **2 of 6 routes pass**, and `exness XAU`'s verdict flips with the window

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps (exactly the
2-container budget). Corrects Round 274.

## Closing the measurement gap

Rounds 274-276 built the Target 3 picture piecemeal: `exness XAU` at 360 days,
four routes at 260 days, and `bybit XAUT` never measured at all. This round measures
the missing route and re-measures `exness XAU` on the matched window, so the whole
fleet sits on **one comparable basis** — `one_target`, deployed parameters
(fractional 0.01/0.02, hold 36), 260 days.

| route | vol (5m) | trades | **/week** | pnl | pnl/trade | **Target 3** |
|---|---|---|---|---|---|---|
| exness BTC/USD | 0.14218% | 364 | **9.80** | −3.6254 | −0.00996 | **PASS** |
| binance BTC/USDT | 0.14371% | 350 | **9.42** | −3.3986 | −0.00971 | **PASS** |
| exness XAU/USD | 0.11212% | 254 | **6.84** | −1.0919 | −0.00430 | **FAIL** |
| bybit BTC/USDT | 0.14406% | 206 | **5.55** | −2.3669 | −0.01149 | **FAIL** |
| binance XAU/USDT | 0.09058% | 135 | **3.63** | −1.4331 | −0.01062 | **FAIL** |
| bybit XAUT/USDT | 0.08812% | 90 | **2.42** | −0.2234 | −0.00248 | **FAIL** |

**Two of six routes meet Target 3. Four do not. All six lose money.**

## Correction to Round 274

Round 274 recorded `exness XAU` at **7.06/week — "passes by 0.9%"**. On the matched
260-day window it is **6.84/week — fails by 2.3%**.

**The verdict flips with the observation window.** Round 274 flagged the margin as
razor-thin; it is thinner than that — thin enough that "pass" and "fail" are not
stable properties of the route. Neither number is wrong; the correct statement is
that `exness XAU` sits **on the threshold**, and a single measurement should not be
quoted as a verdict either way.

## Correction to Round 275's per-trade spread

Round 275 recorded per-trade cost spanning 1.6x across four measurements and warned
the "near-constant −0.0068" was looser than earlier rounds claimed. The full fleet is
**−0.00248 to −0.01149, a 4.6x spread**. The qualitative result is untouched — every
route loses on every trade — but the constant should not be quoted as a single number
at all when comparing routes.

## Volatility and frequency across the full fleet

| set | Spearman | exact perm p |
|---|---|---|
| all six routes | **+0.600** | 0.242 |
| excluding `bybit BTC` (Round 276's outlier) | **+0.900** | 0.083 |

Round 276's qualification holds and is now visible in one table: volatility orders
frequency well **except for `bybit BTC`**, whose 43.3% occupancy (Round 277) drags it
from an expected ~9.5/week to 5.55. Neither figure is significant at n=6, and the
second is not an independent test — it is the same data with the known outlier removed,
which is a description, not evidence.

## What is proven, and what is not

Proven:

- The six-route table above, all on one matched 260-day window with deployed
  parameters, read from `one_target`.
- `exness XAU` measures 7.06/week at 360 days and 6.84/week at 260 days.
- Per-trade cost spans 4.6x across the fleet.
- Volatility-vs-frequency Spearman +0.600 across six, +0.900 excluding `bybit BTC`.

Not proven, and deliberately not claimed:

- **That four routes fail Target 3 in production.** These are 260-day backtests under
  deployed parameters. The live window (Round 259) still gives intervals like
  [0.09, 20.30]/week and settles nothing, and `exness XAU` shows how sensitive the
  verdict is to the window.
- That excluding `bybit BTC` is legitimate inference. It is **not** — the +0.900 line
  is shown to make Round 276's outlier visible, and removing a point because it
  disagrees is exactly what I should not treat as evidence.
- Any cause for the differences beyond what Rounds 273-278 established.
- That Target 3 should be reconsidered. Round 275 already established Targets 1 and 3
  are mechanically opposed; what to do about a target four of six routes miss is the
  user's decision, and I make no recommendation.
