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

# QUALIFIED (Round 298)

The gap this file named against itself — `[360,540]` resting on a 360-day figure from
an earlier round, with no same-day re-measurement — was closed in Round 298. Same-day
`360d = 374` (recorded 363, **+3.03%**) and `260d = 254` (recorded 254, **exact**), so
cross-round differencing is sound at this magnitude and this file's argument stands.

Two numbers here should be read as corrected, because differencing **amplifies** that
drift: `[360,540]` is **0.74/week (19 trades)**, not 1.17/week (30) — the anomaly is
**larger**, not smaller — and `[260,360]` is **8.40/week**, not 7.63. The five-slice
spread is **18.2x**, not 11.5x. Round 298 also rejected σ², trend magnitude and trend
efficiency as explanations for the near-stoppage. See
`round298-REJECTED-the-xau-near-stoppage-is-real-and-bigger-and-volatility-does-not-explain-it.md`.

---

# Round 297 — REJECTED: the deep-slice collapse is **not** a method artifact, and `bybit XAUT` was misclassified as "erratic" when its sequence is monotone

Classification: **REJECTED** — the rival explanation I tested (deep-window collapse
is an artifact of the differencing method) fails a pre-registered two-sided test.
Two bounded Docker sweeps (exactly the 2-container budget), XAU-first. Corrects
Round 293; Round 296 inherited that error.

## Part 1 — A correction to Round 293, from numbers already on record

Round 293 introduced the "smooth trend versus erratic swing" dichotomy and named its
members explicitly: *"The four other routes do not do this. `bybit XAUT` runs 1.79 →
3.85 → 11.20; `bybit BTC` runs 3.11 → 11.03 → 2.66 — **non-monotone, swinging**."*

**`bybit XAUT`'s sequence is monotone.** 1.79 → 3.85 → 11.20, read going back in
time, is strictly increasing at every step. It is not a swing; read forwards, that
route's trade rate has **fallen** 11.20 → 3.85 → 1.79, smoothly, across the three
slices measured. The example was placed on the wrong side of the dichotomy it was
introduced to illustrate.

Re-classifying all six routes on the recorded slices, by **shape** rather than by
spread:

| route | slices going back in time | shape |
|---|---|---|
| exness BTC | 10.31 / 8.66 / 8.19 / 4.90 | **monotone — rising forward** |
| binance BTC | 9.61 / 9.01 / 7.63 / 6.26 | **monotone — rising forward** |
| **bybit XAUT** | **1.79 / 3.85 / 11.20** | **monotone — falling forward** |
| binance XAU | 2.06 / 7.17 | monotone, but only two points |
| exness XAU | 3.89 / 13.47 / 7.63 | non-monotone |
| bybit BTC | 3.11 / 11.03 / 2.66 | non-monotone |

So **three of six routes are monotone across every slice measured**, not two — and
one of the three trends in the **opposite direction**. Round 293's dichotomy
conflated *shape* with *direction*: it read "monotone" as a signature of the two
Target-3-passing routes, when a failing route shares the shape and reverses the sign.
Round 296's phrase "the four erratic routes" inherits the same error and should be
read as three.

**What this does not do:** it does not restore Round 292's "stable" reading for
anyone, it does not make `bybit XAUT` resemble the majors (a 6.26x fall is not a
1.5x rise), and with three points a monotone sequence is a weak observation — there
is a 1-in-3 chance of monotonicity from an arbitrary ordering of three values. I
record it because Round 293 stated the opposite of what its own numbers show, not
because three points settle a shape.

## Part 2 — Two routes cannot be measured at the depth this question needs

Read-only Timescale query over 5m coverage for every gold route:

| route | bars | first bar | last bar | span | bars/day |
|---|---|---|---|---|---|
| `binance.perpetual_future.XAU.USDT` | 75,372 | 2025-12-11 | 2026-08-30 | 262d | 287.7 |
| `bybit.spot.XAUT.USDT` | 145,621 | 2025-04-11 | 2026-08-30 | 506d | 287.8 |
| `exness.cfd.XAU.USD` | 354,814 | 2021-08-26 | 2026-08-28 | 1,828d | 194.1 |

**`bybit XAUT` has 506 days of 5m history.** A `[360,540]` slice does not exist for
it, and `[540,720]` is entirely outside its data. The two-year depth the BTC majors
carry is **structurally unavailable** on that route — so the monotone-falling reading
in Part 1 can never be extended to the depth at which the majors' own trend was
established. `binance XAU` is worse at 262 days, and is a frozen route besides
(Round 207).

This is a standing bound on the fleet comparison, not a defect: **equal-depth
classification of all six routes is impossible with the data that exists.** Any
future statement of the form "the fleet splits into trending and swinging routes"
is comparing two years on two routes against 14 months and 9 months on others.

`exness XAU` runs at 194.1 bars/day against the crypto routes' ~288 because gold CFD
closes at weekends and daily session breaks — the effect Round 260 already quantified
against the live gap. The tool reports it as `verified_session_gap_candles`
(50,004 over the 540-day window, `authoritative_gap_metadata: true`,
`unverified_gap_count: 0`), so it is **recorded market closure, not missing data**.

## Part 3 — The pre-registered test, and what it kills

Rounds 289-296 rest on nested differencing, and the majors' deepest slice is the one
that carries the story: `[540,720]` comes back at **0.39/week** (binance BTC) and
**1.83/week** (exness BTC) — near-zero, on both routes, at the same depth. Round 294
raised warm-up and Round 295 refuted it on the shape of the average-rate curve. But a
sharper worry was never tested: **whatever suppresses the deepest slice might be a
property of window depth itself**, in which case every deep reading in this series
is an artifact and the trend narrative goes with it.

`exness XAU` is the right control: a different instrument, a different broker, a
different market calendar, five years of data, and a sequence that has never resembled
the majors'.

**Registered before running:** the majors' deep collapse does **not** reproduce —
`exness XAU`'s `[540,720]` comes back at **≥ 4.0/week**. Refuted if **< 2.0/week**,
which would make depth-dependence the leading explanation and put Rounds 289-296 at
risk.

Two runs, `--days 540` and `--days 720`, launched together so they share an endpoint
exactly (`holdout_end 2026-08-28T20:59:59.999Z` on both):

| window | cumulative trades | source |
|---|---|---|
| 180d | 100 | Round 291 |
| 260d | 254 | Round 289 |
| 360d | 363 | Round 274, Round 289 (independent, agree) |
| **540d** | **393** | **this round** |
| **720d** | **526** | **this round** |

| slice | trades | span | **rate/week** |
|---|---|---|---|
| [0,180] | 100 | 180d | 3.89 |
| [180,260] | 154 | 80d | 13.47 |
| [260,360] | 109 | 100d | 7.63 |
| **[360,540]** | **30** | 180d | **1.17** |
| **[540,720]** | **133** | 180d | **5.17** |

**`[540,720]` = 5.17/week. The prediction holds and the artifact hypothesis is
rejected.** On the deepest slice available, `exness XAU` trades at **13x** binance
BTC's rate and **2.8x** exness BTC's at the identical depth. Depth alone does not
suppress the count.

The rejection is stronger than the single number, because `exness XAU`'s **deepest
slice is not its lowest**: `[540,720]` (5.17) is **4.4x** `[360,540]` (1.17). A
mechanism that suppresses whatever sits at the far end of the window would have
produced a minimum at the far end. It produced a minimum one slice short of it.

Two controls that close off the obvious alternatives, from the same runs:

- **Coverage is uniform at depth.** 104,639 candles at 540d and 139,646 at 720d —
  193.8 and 193.9 bars/day. The deep window is not thinner data.
- **The decision stream is dense throughout.** decisions/candles is 0.9533 at 540d
  and 0.9493 at 720d, and `[540,720]` alone contains **32,818 decisions** producing
  133 trades. `[360,540]` spans almost exactly the same number of candles and
  therefore a comparable decision count, and produced **30**. Equal decision volume,
  **4.4x** different trade output — consistent with Round 264's finding that every
  route decides at an identical cadence, and locating the variation downstream of the
  decision, not in it.

## Part 4 — The surprise, which I did not predict

`[360,540]` at **1.17/week** is the lowest slice measured on any route in this
series, lower than either major's near-zero deep slice, and it sits **between** two
ordinary ones (7.63 before it, 5.17 after it). Across five slices `exness XAU` now
spans **11.5x** (13.47 / 1.17), against the 3.46x recorded at three slices.

This confirms `exness XAU` in the non-monotone group and does so emphatically, but I
want to be plain that **I have no explanation for it**, that I did not predict it,
and that a 180-day stretch producing 30 trades on a route averaging ~7/week is the
kind of observation that has twice in this session turned out to be my own
measurement error rather than the market's behaviour. It rests on one differencing
against a 360-day figure measured in an earlier round; the endpoint drift between
that run and today's is small relative to a 180-day slice, but it is not zero and I
did not spend a third container to re-measure 360d today.

## Where the cause question stands

Eliminated for the majors' two-year trend: **warm-up** (Round 295, wrong sign),
**volatility** (Round 296, inverted), **data gaps** (Round 296, complete coverage),
and now **depth-dependence of the differencing method** (this round, refuted on a
third route with a maximum one slice short of the deepest). Still unexplained. I am
not proposing a fifth candidate; Rounds 279-284 are the standing reason.

## What is proven, and what is not

Proven:

- `bybit XAUT`'s recorded slices 1.79 / 3.85 / 11.20 are strictly monotone going
  back in time; Round 293 cited them as an example of non-monotone swinging.
- 5m coverage: `binance XAU` 262 days, `bybit XAUT` 506 days, `exness XAU` 1,828 days
  at 194.1 bars/day with session gaps carrying authoritative metadata.
- `exness XAU` at the deployed config: 540d = 393 cumulative trades, 720d = 526,
  both ending 2026-08-28T20:59:59.999Z.
- Derived slices `[360,540]` = 1.17/week and `[540,720]` = 5.17/week; five-slice
  spread 11.5x.
- 193.8 and 193.9 bars/day at the two depths; decisions/candles 0.9533 and 0.9493;
  32,818 decisions inside `[540,720]`.

Not proven, and deliberately not claimed:

- **Any cause** for the rate variation on any route. Unchanged since Round 289.
- That the differencing method is sound in general. One route's deepest slice failing
  to be its lowest refutes *depth-dependence*; it does not validate the method against
  every other confound, and the `[360,540]` figure still leans on a 360-day
  measurement taken on an earlier day.
- That three monotone routes constitute a real class. Three points is a weak shape
  test, and `binance XAU`'s two points are no test at all.
- That `exness XAU`'s 1.17/week slice is a market phenomenon rather than a
  measurement artifact I have not yet found. It is recorded, not explained.
- Any Target 3 verdict change. Today's verdict rests on recent data and is untouched;
  these are historical slices.
