# Round 369 — REJECTED: the band asymmetry **inverts between routes**. Tightening is **52x cheaper** than widening on `exness XAU` and **1.9x more expensive** on `binance BTC`.

Classification: **REJECTED** — my pre-registered criterion fired against the
hypothesis. Two bounded Docker runs (exactly the 2-container budget),
`binance.perpetual_future.BTC.USDT` @500, both `candle_count` **143,998**,
matching the entire Round 367 grid. Executes the next step named in Round 368.

## The pre-registration

Round 368 found that on `exness XAU`, tightening the band from the deployed
0.01/0.02 to 0.0075/0.015 bought **+29.6% frequency for a 1.36% PnL change**,
while widening cost 31.1% frequency for a 74.2% PnL gain. Expressed as a **cost
ratio** `|ΔPnL%| / |Δfreq%|`, that is **0.046 tightening against 2.385
widening** — tightening 52x cheaper per unit of frequency.

`binance BTC`'s widening cost ratio was already computable from Round 367 data
without any new run: 689 → 481 trades (−30.19%) for −4.74869 → −3.94375
(+16.95%), giving **0.561**. That fixed the threshold *before* the runs:

- tightening cost ratio **< 0.561** → the asymmetry reproduces on a second route;
- **≥ 0.561** → it does not, and Round 368's asymmetry is route-specific.

**Observed: 1.052. The criterion fired. The asymmetry does not reproduce.**

## The completed `binance BTC` band axis at hold 36

| band | trades | trades/week | `one_target` PnL | PnL/trade |
|---|---|---|---|---|
| **0.005/0.01** *(new)* | 1039 | **14.55** | **−6.88814** | −0.006630 |
| **0.0075/0.015** *(new)* | 821 | **11.49** | −5.70555 | −0.006950 |
| 0.01/0.02 *(deployed)* | 689 | 9.65 | −4.74869 | −0.006892 |
| 0.02/0.04 | 481 | 6.73 | −3.94375 | −0.008199 |

| direction from deployed | Δ freq | Δ PnL | cost ratio |
|---|---|---|---|
| tighten → 0.0075/0.015 | **+19.16%** | **−20.15%** | **1.052** |
| widen → 0.02/0.04 | −30.19% | +16.95% | 0.561 |

On this route **tightening is nearly twice as expensive per unit of frequency as
widening** — the exact opposite ordering to `exness XAU`. Frequency here is
bought at close to one-for-one in PnL: +19% trades, −20% PnL.

| route | tighten ratio | widen ratio | which direction is cheap |
|---|---|---|---|
| `exness XAU` (r368) | 0.046 | 2.385 | **tightening, by 52x** |
| `binance BTC` (this round) | **1.052** | **0.561** | **widening, by 1.9x** |

## The per-trade gradient reverses sign too

Per-trade PnL across the band axis at hold 36:

- `binance BTC`: −0.006630 / −0.006950 / −0.006892 / −0.008199 for
  0.005 / 0.0075 / 0.01 / 0.02 — **best at the tightest band**;
- `exness XAU` (r368): −0.006080 / −0.004554 / −0.005824 / −0.002181 —
  **best at the widest band**.

Both curves are non-monotone, and their endpoints disagree about which end is
good. This is the third generalisation about the band to fail in three rounds:
r364 refuted "per-trade PnL is constant", r367 refuted "wider is better per
trade", and this round refutes "tightening is the cheap direction".

## Where this leaves the arc

Round 368's asymmetry was the first cell in 60+ rounds with the shape a
candidate would need — more frequency at no PnL cost. **It exists on one route
and inverts on the other.** Nothing in the arc has produced a Portfolio-layer
effect that holds its sign across routes: not the per-trade constant, not the
band gradient, not the direction of cheapness, not the weekday pattern (r354),
not the trough (r341).

The joint objective is also no closer on this route. The tightest band reaches
**14.55 trades/week — more than double the Target 3 bar — at −6.88814, the worst
PnL anywhere in the grid.** Frequency is available on `binance BTC`; it is
simply expensive.

## What is proven, and what is not

Proven:

- `binance BTC` @500, hold 36, band 0.005/0.01: 1039 trades, 14.55/week,
  `one_target` PnL −6.88814. At 0.0075/0.015: 821 trades, 11.49/week, −5.70555.
- Both runs report `candle_count` 143,998, identical to each other and to the
  Round 367 grid, so all eight cells are the same window.
- Cost ratios 1.052 tightening against 0.561 widening; the threshold was
  computed from Round 367 data before the runs.
- Per-trade PnL is non-monotone in band on both routes and its best end differs.

Not proven, and deliberately not claimed:

- **That either route's asymmetry is stable.** One window each, full-window
  `one_target`, **in-sample**. r331/r334/r341 all showed band-axis structure
  moving with the window, and nothing here tests that.
- **That "route" is the explanatory variable.** The two runs differ in venue,
  instrument, market type and trading calendar simultaneously. What is shown is
  that the effect **does not generalise**, not what it depends on.
- Any mechanism. The replay is deterministic (r351), so these are genuine input
  sensitivities rather than sampling noise, but no mechanism is offered for the
  inversion and a two-point ratio is a weak summary of a non-monotone curve.
- That Round 368 was wrong. Its measurement stands; what fails is the
  generalisation it named as its own next test — which is why it named it.
- Holdout behaviour is unchanged: these are band-only cells at the default hold,
  so a gate score is in principle obtainable and was **not attempted** in this
  round.

## Process note

The first evaluation of these runs compared them against a mislabelled baseline
(a stored `0.02/0.04` log read as the deployed cell), which would have reported
the cost ratio as 0.632 against the same 0.561 threshold — the same verdict by
luck, from the wrong arithmetic. Caught before anything was written. The lesson
is Round 360's, one level out: **stored logs must be identified by their
reported parameters, not by the filename a previous round gave them.**
