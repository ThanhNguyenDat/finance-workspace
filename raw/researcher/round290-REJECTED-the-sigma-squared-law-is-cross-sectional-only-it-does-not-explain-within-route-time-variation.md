# Round 290 — REJECTED: the σ² law is cross-sectional only. It does not explain a route's own rate changing over time.

Classification: **REJECTED** — the pre-registered criterion fired against the
hypothesis. Read-only Timescale query. **Zero containers.**

## The obvious candidate for Round 289's open question

Round 289 explained the window effect as non-stationarity of the trade rate and
declined to say why. The obvious candidate was already sitting in this session's
results:

- **Round 273/275**: frequency ∝ σ² (hold ∝ 1/σ² under a fixed fractional band),
  confirmed by a pre-registered cross-route prediction to 2.8%.
- **Round 258**: volatility is strongly non-stationary and clusters — lag-1
  autocorrelation +0.50 to +0.61 at p < 0.0001. That was Round 258's *positive
  control*.

If both hold, a route's rate should track **its own** volatility, slice by slice.
Registered before querying any volatility (`precommit_r290.md`): **slope of
log(rate) on log(σ) near +2; confirmed if in 1.0-3.0 with a clearly positive
correlation.** The band was set deliberately wide because Rounds 286-288 saw three
narrow bands miss.

## Result — refuted, and not narrowly

**n = 13 slices: slope +0.415, Pearson r +0.191.**

Against a theoretical +2 and a registered floor of +1.0. The correlation is close to
nothing.

Two counter-examples make it concrete:

| | volatility | rate |
|---|---|---|
| bybit BTC [0,180] | 0.12807 | 3.11/week |
| bybit BTC [260,360] | **0.14853 (higher)** | **2.66/week (lower)** |
| bybit XAUT [260,360] | **0.06769 — lowest in the table** | **11.20/week — highest measured** |

`bybit XAUT`'s busiest slice is its **quietest** market.

## The scope limit this establishes

**σ² explains differences *between* routes and not changes *within* one over time.**
The law was fitted cross-sectionally (Round 273's six routes, Round 275's
pre-registered pair, Round 285's +0.600/+0.900) and it holds there. I was one step
from extending it to the time dimension; the data say no.

That is a boundary worth having written down, and it means **Round 289's
non-stationarity is still unexplained** — with its most obvious candidate now
eliminated rather than assumed.

## An incidental observation that sharpens the puzzle

The `[180,260]` slice is the **highest-volatility slice on all six routes** — the
volatility regime is shared market-wide, exactly the clustering Round 258 measured.
But the trade-rate peaks are **not** shared: `bybit BTC` and `binance XAU` peak in
`[180,260]` with the volatility, while `bybit XAUT` peaks in `[260,360]` against it.

**Volatility moves together across routes; trade rates do not.** Whatever drives the
rate non-stationarity is therefore at least partly route-specific, not a market-wide
regime.

## What is proven, and what is not

Proven:

- Per-slice 5m volatilities for all six routes, and the 13 (rate, σ) pairs tabulated.
- Slope +0.415 and Pearson +0.191 for log(rate) on log(σ) across those slices.
- `bybit BTC`'s higher-volatility slice has the lower rate; `bybit XAUT`'s
  lowest-volatility slice has the highest rate.
- `[180,260]` is the highest-volatility slice on all six routes.

Not proven, and deliberately not claimed:

- **That σ² is wrong cross-sectionally.** Nothing here touches Rounds 273/275/285;
  what is rejected is extending the law to within-route time variation.
- Any alternative cause for the non-stationarity. None is offered — Rounds 279-284
  are a standing reminder of what happens when I propose mechanisms faster than I can
  test them.
- That 13 slices is a strong test. Four routes contribute only pooled `[0,260]`
  points, and pooling variances across a regime change is itself lossy. A slope of
  +0.415 with r = +0.191 is weak enough that a cleaner design would not rescue it,
  but the design is not clean.
- That route-specificity is established. The shared volatility peak against unshared
  rate peaks is one observation across six routes, not a decomposition.
