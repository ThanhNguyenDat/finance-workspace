# UNRELIABLE — METHOD DEFECT (Round 300)

Every **Portfolio-layer slice rate** in this file comes from **nested differencing**
of `--days` runs, and Round 300 found that method invalid for Portfolio counters: the
Portfolio refits its interval and strategy weights **on every kline** from cumulative
Alpha performance (`portfolio_decision_replay.rs:317`), so two runs of different
length carry **different weights over every bar they share**. A difference between a
540-day and a 360-day run is therefore not "what happened in `[360,540]`".

The weight-free Alpha layer, which *is* cleanly nested (76 of 77 strategies strictly
monotone), shows **no** corresponding variation — 3,773.9 / 3,560.4 / 3,499.5 trades
per week across the same slices, a 4.5% spread against the Portfolio's 7-17x.

Treat this file's Portfolio slice rates as **unreliable pending re-derivation** — not
as disproved; a method defect removes evidence, it does not establish the opposite.
Coverage facts, single-window measurements and live production readings in this file
are unaffected. See
`round300-DATA-ISSUE-portfolio-weights-refit-every-kline-so-nested-differencing-does-not-isolate-a-calendar-period.md`.

---

# CORRECTION (Round 291)

This file's **stable / unstable classification** is partly a pooling artifact.

`exness XAU` was placed in the stable group at **1.12x** on the strength of a pooled
`[0,260]` point. Unpooled (Round 291): **3.89 → 13.47 → 7.63 per week, a 3.46x
spread** — squarely with the routes this file called unstable. `bybit XAUT` also
worsens, 4.62x → **6.26x**.

**Every route since unpooled has turned out non-stationary; the only two still in the
stable group (`exness BTC` 1.20x, `binance BTC` 1.24x) are the only two never
unpooled.** Their stability is untested, not established.

This file's **central finding is unaffected and strengthened**: the window effect is
non-stationarity of the trade rate, and the quiet routes clear the bar in their busy
slices. See
`round291-CORRECTION-exness-xau-was-stable-only-because-it-was-pooled.md`.

---

# Round 289 — The window effect is non-stationarity, and in their busy slices the "failing" routes clear Target 3 outright

Classification: **NEEDS-MORE-RESEARCH**. Derived from data already collected.
**Zero containers.**

## Explaining a phenomenon I had hit seven times

Rounds 286-288 measured window effects of −4.6%, −5.3%, +3.2%, −43.2%, +100.9%,
−43.9% and −14.5%, and Round 287 showed trade count does not predict them. Round 288
concluded I should stop trying to forecast the quantity. **A better move is to explain
it**, and that needs no new runs: every `--days N` window is nested and ends at the
same "now", so **differencing consecutive cumulative trade counts gives the rate
inside each slice**.

| route | slice (days ago) | trades | days | **/week** |
|---|---|---|---|---|
| exness BTC | [0, 260] / [260, 360] | 364 / 117 | 260 / 100 | 9.80 / 8.19 |
| binance BTC | [0, 260] / [260, 360] | 350 / 109 | 260 / 100 | 9.42 / 7.63 |
| exness XAU | [0, 260] / [260, 360] | 254 / 109 | 260 / 100 | 6.84 / 7.63 |
| **bybit BTC** | [0,180] / [180,260] / [260,360] | 80 / 126 / 38 | 180 / 80 / 100 | **3.11 / 11.03 / 2.66** |
| **binance XAU** | [0, 180] / [180, 260] | 53 / 82 | 180 / 80 | **2.06 / 7.17** |
| **bybit XAUT** | [0, 260] / [260, 360] | 90 / 160 | 260 / 100 | **2.42 / 11.20** |

| route | sub-period spread |
|---|---|
| exness XAU | **1.12x** |
| exness BTC | **1.20x** |
| binance BTC | **1.24x** |
| **binance XAU** | **3.48x** |
| **bybit BTC** | **4.14x** |
| **bybit XAUT** | **4.62x** |

**The three routes whose verdicts moved with the window are exactly the three whose
rate is non-stationary.** The window effect is not measurement noise and not a tooling
artifact — it is the trade rate genuinely changing by 3.5-4.6x between consecutive
80-100 day stretches. The three stable routes move 1.1-1.2x and their verdicts held.

This is not Poisson noise: the smallest slice has 38 trades (±16% at 1σ), the largest
160 (±8%), against observed swings of 250-360%.

## The part that corrects my own framing

**In their busy slices the "failing" routes clear Target 3 outright:**
`binance XAU` **7.17/week**, `bybit BTC` **11.03/week**, `bybit XAUT` **11.20/week** —
all at or above the 7/week bar, and `bybit BTC`'s 11.03 is the busiest slice measured
on **any** route in this session.

So for those three routes, "fails Target 3" is a property of **the averaging window**,
not of the route. Rounds 285-288 presented the fleet table as route status; for half
the fleet that reading is wrong. The honest statement is that they **alternate**
between near-dormant stretches (2.1-3.1/week) and busy stretches (7.2-11.2/week), and
a single window reports whichever mix it happens to span.

The two passing routes and `exness XAU` are unaffected — their slices are stable, and
`exness XAU`'s straddle the bar (6.84 and 7.63), which is exactly the "on the
threshold" reading Round 285 gave it.

## What is proven, and what is not

Proven:

- The sub-period rates tabulated, derived by differencing nested windows measured
  under identical deployed parameters.
- Sub-period spreads of 1.12-1.24x on three routes and 3.48-4.62x on the other three.
- The three high-spread routes are exactly the three whose Target 3 verdicts moved
  with the window.
- Each quiet route has at least one 80-100 day slice at or above 7/week.

Not proven, and deliberately not claimed:

- **That the quiet routes would pass Target 3 over a long horizon.** Their *pooled*
  rates over every window measured remain below 7. What is shown is that the shortfall
  is intermittent, not constant — which is a different claim and a weaker one.
- Any cause for the non-stationarity. Rounds 273-279 explain the *level* of a route's
  rate (volatility, occupancy, the guard); nothing here explains why a route's rate
  changes 4x between quarters, and I am not guessing after Rounds 279-284.
- That the differencing is exact. The windows were run hours apart, which is
  negligible against 80-100 day slices, but the slice counts are differences of two
  measurements and inherit both their errors.
- That Round 285's table should be withdrawn. Its numbers stand; what needs the
  qualifier is reading a windowed rate as a route property on the three unstable
  routes.
