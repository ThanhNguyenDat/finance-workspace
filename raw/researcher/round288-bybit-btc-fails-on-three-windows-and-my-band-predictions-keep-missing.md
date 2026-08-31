# Round 288 — `bybit BTC` fails Target 3 on all three windows; and my window-effect predictions have now missed three rounds running

Classification: **NO-CHANGE** — Round 285's fleet split stands, with its weakest
verdict now the best-supported one. Two bounded Docker sweeps (exactly the
2-container budget).

## The target Round 287 named

Round 287 called `bybit BTC` *"the verdict I would trust least"* — the narrowest
Target 3 failure (−21%) and the only route still on a single window. Both containers
went to it, giving **three windows on the one verdict that mattered most**.

| window | trades | **/week** | shift vs 260d | pnl/trade | Target 3 |
|---|---|---|---|---|---|
| 180d | 80 | **3.11** | **−43.9%** | −0.01914 | **FAIL** |
| 260d | 206 | **5.55** | — | −0.01149 | **FAIL** |
| 360d | 244 | **4.74** | **−14.5%** | −0.00702 | **FAIL** |

**All three fail.** Range 3.11-5.55/week, a 1.78x spread, with the highest reading
still 21% below the bar. By the criterion I registered before running — *"all three
windows below 7 → the FAIL verdict is as solid as three windows can make it"* — that
is the outcome.

**Round 285's "2 of 6 pass" therefore stands**, and its least-secure row is now its
best-evidenced one.

## My band missed again — the third round in a row

I predicted 4.0-7.5/week. The 180-day window came in at **3.11**, below the floor.

| round | my band | actual | outcome |
|---|---|---|---|
| 286 | 9.0-10.5 | 8.92 | missed low |
| 287 | 3.2-4.1 and 2.2-2.7 | 2.06 and 4.86 | missed both, badly |
| 288 | 4.0-7.5 | 3.11 | missed low |

Every substantive criterion I set has held; **every numeric band I set has failed.**
The observed window effects now number seven: −4.6%, −5.3%, +3.2%, −43.2%, +100.9%,
−43.9%, −14.5%. I keep assuming a stability this quantity does not have.

**The honest position: single-window Target 3 rates vary by up to 2x on a route, and I
cannot forecast the direction or magnitude of that variation.** I should stop issuing
narrow bands for it — they add no information and have been wrong three times.

## The per-trade cost is not constant within a route either

| window | pnl/trade |
|---|---|
| 180d | −0.01914 |
| 260d | −0.01149 |
| 360d | −0.00702 |

**A 2.7x range on one route from window choice alone.** Round 275 widened the
"near-constant −0.0068" to a 1.6x cross-route spread; Round 285 widened it to 4.6x;
this round shows it also moves 2.7x *within* a single route. It is not a constant in
any useful sense and should not be quoted as one.

The qualitative result is untouched and has never wavered: **every route, every
window, every configuration loses money on every trade.**

## What is proven, and what is not

Proven:

- `bybit BTC` at 3.11 / 5.55 / 4.74 per week on 180 / 260 / 360-day windows, all
  failing Target 3, with per-trade cost −0.01914 / −0.01149 / −0.00702.
- Seven measured window effects spanning −43.9% to +100.9%.
- Three consecutive rounds in which my numeric band was wrong while the substantive
  criterion held.

Not proven, and deliberately not claimed:

- **That three windows settle it.** Three points bracket 3.11-5.55; a fourth could
  land outside. What they establish is that no measured window came within 21% of the
  bar, not that none could.
- That this holds in production. Backtests throughout; Round 259's live interval is
  still uninformative.
- Any cause for the window sensitivity. Round 287 showed trade count does not predict
  it, and nothing here advances that.
- That two windows per route is enough for the others. As of this round **every one
  of the six routes has at least two windows** — exness BTC (260/360), binance BTC
  (260/360), exness XAU (260/360), binance XAU (180/260), bybit XAUT (260/360) and
  bybit BTC (180/260/360) — but Round 287 showed two windows can bracket a 2x range,
  so "double-measured" is a floor, not a guarantee.
