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

# QUALIFICATION (Round 293)

This file called the two BTC majors **"genuinely stable"** at 1.26x — measured over
**one year**, and it flagged that limit itself.

Extended to 18 months (Round 293): `exness BTC` reaches **2.10x** once `[360,540]`
(4.90/week) is added, and `binance BTC` **1.53x**. So "genuinely stable" was a
one-year artifact on at least one of the two.

**But the shape differs from the other four routes**: both majors decline
*monotonically* going back (10.31/8.66/8.19/4.90 and 9.61/9.01/7.63/6.26) — a smooth
trend, roughly doubling over 18 months — where `bybit XAUT` (1.79/3.85/11.20) and
`bybit BTC` (3.11/11.03/2.66) swing non-monotonically. This file's clean bimodal
split is better read as **trend versus swing**, not stable versus unstable.

This file's measurements stand, as does its point that the split is not explained by
instrument or volatility. See
`round293-REJECTED-stability-was-a-one-year-artifact-but-the-majors-trend-rather-than-swing.md`.

---

# Round 292 — REJECTED (my prediction): the two BTC majors are genuinely stable. The fully-unpooled fleet splits cleanly in two, and not by instrument or volatility.

Classification: **REJECTED** — my pre-registered prediction failed, and the failure is
the result. Two bounded Docker sweeps (exactly the 2-container budget).

## The last two routes, unpooled

Round 291 named the job: `exness BTC` and `binance BTC` were the only routes whose
`[0,260]` was still pooled, and the only two left in Round 289's "stable" group. I
predicted, directionally, that **both would turn out non-stationary (spread > 2x)**,
because all four routes unpooled so far had (3.46x, 3.48x, 4.14x, 6.26x).

| route | [0,180] | [180,260] | [260,360] | **spread** | Round 289 said |
|---|---|---|---|---|---|
| exness BTC | 10.31 | 8.66 | 8.19 | **1.26x** | 1.20x |
| binance BTC | 9.61 | 9.01 | 7.63 | **1.26x** | 1.24x |

**Both are genuinely stable.** My prediction is refuted, and Round 289's
classification was right for these two — it was wrong only for `exness XAU`. Round
291's suspicion that the whole stable group was a pooling artifact was **too broad**,
and I am recording that against my own reasoning as well as my prediction.

## The completed fleet picture — a clean bimodal split

All six routes are now unpooled:

| route | spread | Target 3 |
|---|---|---|
| bybit XAUT | 6.26x | fail |
| bybit BTC | 4.14x | fail |
| binance XAU | 3.48x | fail |
| exness XAU | 3.46x | fail / threshold |
| **binance BTC** | **1.26x** | **pass** |
| **exness BTC** | **1.26x** | **pass** |

**Two routes at 1.26x, four at 3.46-6.26x, and nothing in between.** The split is
sharp, and the stable pair is **exactly the pair that passes Target 3**.

## What the split is not

**Not the instrument.** BTC appears on both sides — `binance BTC` and `exness BTC` at
1.26x, `bybit BTC` at 4.14x.

**Not the volatility.** Round 276 measured the three BTC routes at 0.14371%, 0.14218%
and 0.14406% — identical to three decimal places — yet two are stable and one is not.

So stability is a **venue-level** property here, not an instrument or market
property. Consistent with Round 277's other venue-level oddity on the same route:
`bybit BTC`'s occupancy is 43.3% against ~60% on the other two BTC routes.

## What is proven, and what is not

Proven:

- `exness BTC` 180d = 265 trades (10.31/week); `binance BTC` 180d = 247 (9.61/week).
- Unpooled sub-period rates and spreads of 1.26x on both.
- The full six-route spread table, all routes unpooled.
- The three BTC routes share volatility to three decimals (Round 276) yet split
  1.26x / 1.26x / 4.14x on stability.

Not proven, and deliberately not claimed:

- **That stability causes Target 3 passing, or vice versa.** The 2/2 and 4/4
  alignment is across **six routes** and both quantities are computed from the same
  trade counts, so they are not independent measurements. It is a pattern worth
  noting and not a result.
- That the split is venue-driven. What is shown is that instrument and volatility do
  **not** explain it; "venue" is what is left after eliminating two candidates on six
  routes, which is a much weaker thing than a demonstrated cause.
- Any cause for the non-stationarity itself. Unchanged since Round 289; Round 290
  eliminated the σ² candidate and nothing has replaced it.
- That three slices per route settles stability. `[0,180]`, `[180,260]` and
  `[260,360]` are one year; a route stable across three quarters could still move
  across years.
