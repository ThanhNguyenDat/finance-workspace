# Round 243 — BTC's most recent band is positive too: the "two different diseases" claim from Round 241 is rejected

Classification: **REJECTED** — the hypothesis under test is my own from two rounds
ago. Two bounded Docker sweeps.

## The claim being tested

Round 241 measured BTC's Portfolio gross edge over the full 1,800 days as
**−0.00080 per trade** with all costs zeroed and concluded:

> "For XAU it is friction dominating a small real edge. **For BTC over the full
> window it is not friction at all** — the signal is negative to begin with.
> Two routes, two different diseases, previously described as one."

Round 242 then band-decomposed XAU and found the full-window figure was small
*because the oldest band was negative*, not because the edge was uniformly tiny.
It explicitly noted BTC had not been decomposed. If the same decomposition applies
to BTC, the "two diseases" claim does not survive.

binance BTC/USDT 5m, `one_target`, hold 36, all costs zero:

| window | trades | gross PnL | gross per trade |
|---|---|---|---|
| 450 days | 716 | +0.558 | **+0.00078** |
| 900 days | 1,708 | −0.387 | −0.00023 |
| 1,800 days | 3,312 | −2.658 | −0.00080 |

## The bands, and the claim collapses

| band (days ago) | trades | gross PnL | gross per trade | % of friction (~0.0070) |
|---|---|---|---|---|
| 900-1800 | 1,604 | −2.271 | −0.00142 | −20.2% |
| 450-900 | 992 | −0.945 | −0.00095 | −13.6% |
| **0-450** | 716 | **+0.558** | **+0.00078** | **+11.1%** |

**BTC's most recent 450 days are positive.** Its full-window negative comes
entirely from the two older bands.

Side by side with Round 242's XAU decomposition:

| band | **XAU** gross/trade | **BTC** gross/trade |
|---|---|---|
| 900-1800 | −0.00242 (−35%) | −0.00142 (−20%) |
| 450-900 | **+0.00517 (+74%)** | **−0.00095 (−14%)** |
| **0-450** | **+0.00107 (+15%)** | **+0.00078 (+11%)** |

The two routes have **the same shape**: oldest band negative, most recent band
positive, and the recent figures converge — **+0.00107 vs +0.00078**, i.e. 15% and
11% of friction. They differ only in the middle band.

**Round 241's "two different diseases" is withdrawn.** It was an artifact of
comparing XAU's band-decomposed picture against BTC's full-window aggregate — the
same aggregation error that made XAU look uniformly weak before Round 242
decomposed it. I made the comparison on unequal footing.

## What replaces it

One coherent statement covering both instruments:

> **On both routes the Portfolio layer has a small positive gross edge confined to
> the most recent ~450 days, worth 11-15% of friction. Everything older is
> negative. Neither route is anywhere near covering its costs, and both would need
> roughly 7-9x more gross edge per trade to break even.**

That is more consistent, and less flattering, than either the "friction kills a
real edge" narrative (true only recently) or the "BTC has no signal" one (true
only in aggregate).

It also aligns with Round 227's Alpha-layer walk-forward, Round 234's holdout-only
gate, and Round 242's XAU bands. Five measurement routes, one shape.

## What is proven, and what is not

Proven:

- binance BTC 5m zero-cost `one_target`: 450d gives 716 trades and +0.558; 900d
  gives 1,708 and −0.387; 1,800d gives 3,312 and −2.658.
- Bands: 900-1800 −0.00142, 450-900 −0.00095, 0-450 **+0.00078**.
- BTC's recent band (+0.00078) and XAU's (+0.00107) are within 37% of each other.

Not proven, and deliberately not claimed:

- That the recent positive bands are statistically significant. 716 trades on BTC,
  693 on XAU, no confidence intervals; Rounds 230-232 showed figures at this scale
  need a spread before they carry weight, and the spread here is across nested
  windows, not independent samples.
- That the middle-band divergence (XAU +74% vs BTC −14%) means anything. It is one
  band on one window per instrument.
- That the subtraction is exact. Same Round 226 inference flagged in Round 242.
