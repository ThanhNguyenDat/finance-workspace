# WITHDRAWN (Round 301)

This file's headline — *"the near-stoppage is real and bigger"* — is **wrong**. Round
301 perturbed the window start by one day: `one_target` goes **374 → 367**, a strictly
larger window returning **seven fewer** trades. Across 360/361/365 days the count runs
367 / 374 / 392, a **25-trade** spread, and the `[360,540]` slice this file reports as
19 trades evaluates to **26, 19 or 1** depending on which base is used.

**The anomaly is wholly inside the method's own noise.** The same-day re-measurement in
this file was sound and its arithmetic stands; what fails is the conclusion drawn from
it. See
`round301-REJECTED-the-near-stoppage-is-below-the-method-noise-floor-one-extra-day-moves-the-count-by-seven-trades.md`.

---

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

# Round 298 — REJECTED: `exness XAU`'s 180-day near-stoppage survives same-day re-measurement, is **larger** than Round 297 reported, and volatility does not explain it

Classification: **REJECTED** — the pre-registered σ² explanation for the anomaly
fails. Two bounded Docker sweeps (exactly the 2-container budget) plus one read-only
Timescale query. XAU-first. Closes the gap Round 297 named against itself.

## What Round 297 left open, in its own words

Round 297 reported `exness XAU`'s `[360,540]` slice at **1.17/week** — the lowest on
any route in this series — and flagged the weakness explicitly: *"It rests on one
differencing against a 360-day figure measured in an earlier round; the endpoint drift
between that run and today's is small relative to a 180-day slice, but it is not zero
and I did not spend a third container to re-measure 360d today."*

That is this round's job, and it is worth doing precisely because differencing
**amplifies** cross-round drift: a small error in a cumulative count becomes a large
error in the slice that subtracts it, and the smaller the slice the worse the
amplification. `[360,540]` held 30 trades, so it was the most exposed number in the
series.

## Part 1 — The recorded ladder reproduces, and the anomaly gets bigger

**Registered before running:** today's same-day `260d` and `360d` counts reproduce the
recorded 254 and 363 **within ±10%**. Refuted if either misses by more than 10%, which
would mean every slice in Rounds 289-297 derived from mixed-round figures needs
re-deriving.

| window | recorded | **today** | drift |
|---|---|---|---|
| 260d | 254 (Round 289) | **254** | **0.00%** |
| 360d | 363 (Rounds 274, 289) | **374** | **+3.03%** |
| 540d | — | 393 (Round 297) | — |
| 720d | — | 526 (Round 297) | — |

**The prediction holds.** Cross-round differencing is sound at this magnitude — 260d
reproduces exactly, 360d to 3%. Same config throughout (fractional 0.01/0.02, hold 36,
fee 5bps, slippage 2bps); today's runs are 18 minutes after Round 297's, so 360d/540d
is now a **same-day pairing**.

But amplification is real, and it cuts against Round 297's own number:

| slice | trades | span | **rate/week** | Round 297 said |
|---|---|---|---|---|
| [0,180] | 100 | 180d | 3.89 | 3.89 |
| [180,260] | 154 | 80d | 13.47 | 13.47 |
| [260,360] | 120 | 100d | **8.40** | 7.63 |
| **[360,540]** | **19** | 180d | **0.74** | **1.17** |
| [540,720] | 133 | 180d | 5.17 | 5.17 |

An **11-trade** shift in the 360d cumulative moved `[360,540]` from 30 trades to
**19** — a 37% change in the slice from a 3% change in the input. **The near-stoppage
is not an artifact of cross-round drift; correcting for that drift made it worse.**
Five-slice spread goes from 3.46x (three slices, Round 291) to **18.2x**.

`[260,360]` also moves, 7.63 → 8.40/week (+10.1%), which is the same amplification in
the other direction. That number appears in the fleet tables of Rounds 289-297 and
should be read as **8.40** going forward.

## Part 2 — The near-stoppage is not a data, coverage, or decision-cadence effect

From the same runs, and from Timescale independently:

| slice | candles (tool) | candles (Timescale) | decisions | trades | **1 trade per N decisions** |
|---|---|---|---|---|---|
| [260,360] | 19,751 | 19,751 | 18,389 | 120 | **153** |
| **[360,540]** | **34,898** | **34,898** | **33,672** | **19** | **1,772** |
| [540,720] | 35,007 | 35,002 | 32,818 | 133 | **247** |

Three things follow.

1. **The research tool and Timescale agree on candle counts exactly** (19,751 and
   34,898 identical; 35,007 against 35,002 at a boundary). The tool is reading the
   data the database holds.
2. **`[360,540]` and `[540,720]` are near-identical in every input**: 34,898 against
   35,007 candles, 33,672 against 32,818 decisions, both spanning 180 days at 193.9
   bars/day. The decision engine ran normally throughout — consistent with Round 264's
   finding that every route decides at an identical cadence.
3. **Trade output differs 7.0x on matched inputs** (19 against 133), and yield per
   decision differs **7.2x**.

So whatever suppresses `[360,540]` sits **downstream of the decision**, not in data
availability and not in decision cadence.

## Part 3 — The pre-registered σ² test, and its failure

Round 273 established `hold ∝ 1/σ²` cross-sectionally: lower volatility means longer
holds, hence fewer closes. That is the obvious candidate for a 180-day near-stoppage,
and it makes a sharp prediction.

**Registered before querying:** if σ² explains this, `[360,540]` is the **lowest
realized-volatility slice of the five.**

Read-only Timescale, 5m log returns on `exness.cfd.XAU.USD`:

| slice | bars | **vol% per 5m** | path length % | drift % | efficiency | **rate/week** |
|---|---|---|---|---|---|---|
| [0,180] | 35,166 | 0.10297 | 2,309.4 | −17.07 | 0.00739 | 3.89 |
| [180,260] | 14,824 | **0.13764** | 1,173.2 | +24.92 | 0.02124 | 13.47 |
| [260,360] | 19,751 | 0.08080 | 1,069.5 | +21.36 | 0.01997 | 8.40 |
| **[360,540]** | 34,898 | **0.06538** | 1,512.1 | +21.82 | **0.01443** | **0.74** |
| **[540,720]** | 35,002 | **0.04940** | 1,192.2 | +16.54 | **0.01387** | **5.17** |

**`[360,540]` is not the lowest-volatility slice — `[540,720]` is, at 0.04940 against
0.06538, and it trades 7x more.** The prediction fails and **σ² is rejected as the
explanation for this anomaly.**

Two further candidates fall out of the same table for free, and neither separates the
two slices:

- **Trend magnitude**: +21.82% against +16.54% drift — comparable, and the *larger*
  drift belongs to the near-stopped slice.
- **Trend efficiency** (|drift| / path length, the Round 252 measure): **0.01443
  against 0.01387** — within 4% of each other. The two slices are almost the same
  shape of market.

Across all five slices Spearman(rate, vol) = **+0.500** (exact two-sided p = **0.45**,
n=5). That is the sign σ² predicts and it is **not significant**; it is also
contradicted at the extreme, which is where the anomaly lives. Round 296 measured
**−0.300** on the two BTC majors. Taken together: no reliable within-route
rate/volatility relationship has been established in either direction, and neither
round's coefficient should be read as one.

## Where this leaves the cause question

Eliminated for `exness XAU`'s `[360,540]` near-stoppage: **cross-round measurement
drift** (Part 1 — correcting it made the anomaly larger), **data coverage** (Part 2 —
matched candle counts, confirmed against Timescale), **decision cadence** (Part 2 —
matched decision volume), **volatility** (Part 3 — the lowest-σ² slice trades 7x
more), **trend magnitude** and **trend efficiency** (Part 3 — both matched).

Every observable I can compute from price or from the tool's own counters is
essentially matched between a slice with 19 trades and a slice with 133. I have no
explanation and I am not proposing one; Rounds 279-284 are the standing reason for
that restraint, and it applies with more force here, not less, because the
elimination list is now long enough to be tempting.

## What is proven, and what is not

Proven:

- Same-day `exness XAU` cumulative counts: 260d = 254, 360d = 374, at the deployed
  config, 18 minutes after Round 297's 540d = 393 and 720d = 526.
- Recorded 260d reproduces exactly; recorded 360d to +3.03%.
- Same-day slice rates: 3.89 / 13.47 / 8.40 / **0.74** / 5.17 per week; five-slice
  spread 18.2x.
- `[360,540]`: 34,898 candles, 33,672 decisions, **19 trades**. `[540,720]`: 35,007
  candles, 32,818 decisions, **133 trades**.
- Tool and Timescale candle counts agree (19,751 and 34,898 exactly).
- Per-slice 5m realized volatility, path length, drift and efficiency as tabulated;
  `[540,720]` is the lowest-volatility slice of the five.
- Spearman(rate, vol) = +0.500, exact two-sided p = 0.45, n = 5.

Not proven, and deliberately not claimed:

- **Any cause** for the near-stoppage, or for any of the rate variation in this
  series. Unchanged since Round 289.
- That σ² is irrelevant. Round 273's cross-sectional law is untouched; what is
  rejected is σ² as the explanation for **this** slice, on the criterion registered
  before the query.
- That the +0.500 rank correlation means anything. n=5, p=0.45.
- That the five slices are directly comparable. Widths run 80-180 days, uneven, and
  `[0,180]` is the only slice with negative drift.
- That `[180,260]`'s 13.47/week is same-day verified. Its 180d input (100 trades) is
  still an earlier round's figure; only 260d and above were re-measured today.
- Any Target 3 verdict change. These are historical slices; today's verdict rests on
  recent data and is untouched.
