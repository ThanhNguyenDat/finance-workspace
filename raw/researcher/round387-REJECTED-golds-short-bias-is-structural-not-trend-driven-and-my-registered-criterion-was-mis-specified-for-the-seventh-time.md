# Round 387 — REJECTED: gold's short bias is **structural, not trend-driven**. My registered criterion was mis-specified for the **seventh** time.

Classification: **REJECTED** — the hypothesis that a mean-reversion tilt sells
into strength is refuted. **Zero containers**, from records already held.

## The registered test, and the defect in how I wrote it

Rounds 385–386 left one open question: why is the Portfolio short most of the
time on a route that rose 105%? The leading explanation was a mean-reversion
tilt — two of gold's three production candidates are reversion strategies —
which predicts **short exposure should rise where price rose**.

I registered: *positive correlation → consistent with selling into strength;
zero or negative → the hypothesis loses its support.*

**Observed: Spearman ρ = +0.006 over ten time deciles.**

That is zero. But my criterion said "positive", and +0.006 is positive, so as
written the test would have returned "yes". **A sign test with no magnitude
threshold makes any noise count as confirmation.** This is the seventh
mis-specified pre-registration in this arc (r327, r330, r340, r354, r373, r378,
r387) and I am reading the number, not the criterion: **there is no correlation,
and the trend-driven explanation is refuted.**

## What the deciles actually show

| decile | avg price | long h | short h | short share |
|---|---|---|---|---|
| 1 | 2316.28 | 643.5 | 965.6 | 60.0% |
| 2 | 2430.15 | 427.8 | 1389.3 | 76.5% |
| 3 | 2658.32 | 337.2 | 1631.4 | 82.9% |
| 4 | 2783.40 | 712.3 | 1363.2 | 65.7% |
| 5 | 3221.57 | 210.1 | 903.3 | 81.1% |
| 6 | 3381.17 | 943.2 | 635.7 | **40.3%** |
| 7 | 4060.34 | 259.4 | 1346.7 | 83.8% |
| 8 | 4877.98 | 120.2 | 1167.1 | **90.7%** |
| 9 | 4714.19 | 963.9 | 568.5 | **37.1%** |
| 10 | 4187.35 | 772.1 | 979.8 | 55.9% |

Deciles 8 and 9 sit at almost the same price (4878, 4714) and are **90.7% and
37.1% short** — the widest swing in the table, across the smallest price change.
Short share is above 50% in **eight of ten** deciles regardless of where price
is.

**The bias is persistent and price-independent.** It is not a response to the
trend.

## The finding that replaces it: the bias is gold-specific

Short share of exposure time, all three routes, matched pinned window:

| route | long h | short h | **short share** |
|---|---|---|---|
| **`exness XAU`** | 5,390 | 10,951 | **67.0%** |
| `binance BTC` | 4,696 | 5,920 | 55.8% |
| `bybit BTC` | 5,070 | 4,898 | 49.1% |

`bybit BTC` is balanced, `binance BTC` mildly short-tilted, and **gold spends two
of every three exposure-hours short — on the one route that rose 105%.** Gold is
the outlier by a wide margin, and it is the route where that costs the most.

## A candidate mechanism, named and not tested

Gold receives **three** production candidates against BTC's five (r375), and its
unique extra is `mtf_stochastic_5m_4h_sma5` — an oscillator. BTC's extras are a
stochastic, a MACD **and** a candle-momentum variant, so BTC's ensemble carries
momentum weight that gold's does not. A more oscillator-weighted ensemble on a
trending instrument is a plausible source of a persistent counter-trend tilt.

**Plausible is not measured.** I have not tested it, and this arc's record on
plausible mechanisms is poor: round 372's whipsaw-frequency story and round
375's input-count story were both refuted by the data that suggested them.

## What is proven, and what is not

Proven:

- ρ(price level, short share) = +0.006 across ten deciles on `exness XAU`.
- The decile table above; short share above 50% in eight of ten.
- Short share of exposure time: 67.0% / 55.8% / 49.1% on gold / `binance BTC` /
  `bybit BTC`, matched pinned window.

Not proven, and deliberately not claimed:

- **Any cause for the gold short bias.** One candidate named, untested.
- That the bias is harmful in itself. It is costly *on this window* because gold
  rose; on a falling window the same bias would have helped. Round 386 already
  established that side outcomes here are drift alignment.
- That three routes establish a pattern. Two BTC routes of the same instrument
  are close to one observation (r276), so this is nearer two points than three.
- That the decile price proxy is exact. It is the mean entry price of trades
  opening in each decile, which is weighted by when trades open rather than by
  time.

## Named next step

Test the ensemble-composition candidate directly: compare each production
candidate's own long/short signal distribution on gold, using the Alpha sweep
already present in every run's `strategy_scores`. If the oscillator candidates
are short-biased on a rising instrument and the momentum ones are not, the
mechanism is located; if all three are balanced, the bias is in the Portfolio's
aggregation rather than in its inputs, which is a different and more serious
place to look.
