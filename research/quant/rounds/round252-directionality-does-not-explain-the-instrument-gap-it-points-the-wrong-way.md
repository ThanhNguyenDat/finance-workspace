# RESOLVED (Round 253)

The hypothesis this file raised and explicitly left untested — that a candidate
population handling uptrends better than downtrends would explain the instrument
gap — was tested in Round 253 and **refuted on the independent instrument**.
BTC's up-trending band (0-150, drift +12.21%) has median edge **−0.00294**, the
only negative cell of the four and **worse than its own down-trending band**
(+0.00268). Regrouping the same 14 retained measurements by trend direction gives
XAU 7/7 but BTC 2/7 — instruments disagree — where the calendar-band grouping
gives 7/7 and 5/7 with both agreeing.

Nothing in this file's own measurements is corrected; its hypothesis simply did
not survive. See
`round253-trend-direction-does-not-explain-what-calendar-band-already-explains.md`.

---

# Round 252 — Why XAU responded 3.3x more than BTC: the obvious explanation is refuted, and it points the wrong way

Classification: **REJECTED** — the natural explanation for the instrument gap
fails. No containers; one read-only query and local computation.

## The gap Round 251 named

Round 251 measured, like-for-like, that the directional mechanisms reached
**124.9% of friction on XAU 4h** and only **38.2% on BTC 4h** in the same
150-300 day window, and closed with: *"not claimed: any explanation for the
instrument difference. Not investigated here."*

The obvious hypothesis, given Rounds 228 and 247-248: **XAU's market became more
directional than BTC's in that window**, so directional mechanisms had more to
work with there.

That is directly measurable. Same 4h series, same bands:

| instrument | band (days ago) | bars | volatility | **efficiency** | **drift** |
|---|---|---|---|---|---|
| exness XAU | 0-150 | 659 | 0.3022% | 0.0242 | −6.43% |
| exness XAU | **150-300** | 654 | 0.3480% | **0.0447** | **+16.89%** |
| binance BTC | 0-150 | 900 | 0.3628% | 0.0259 | +12.21% |
| binance BTC | **150-300** | 900 | 0.4823% | **0.0805** | **−48.18%** |

## The hypothesis is refuted, backwards

| instrument | efficiency ratio 150-300 / 0-150 | \|drift\| ratio | measured response |
|---|---|---|---|
| exness XAU | **1.85x** | 2.63x | **124.9% of friction** |
| binance BTC | **3.11x** | 3.95x | **38.2% of friction** |

**BTC's market became substantially more directional than XAU's** — efficiency up
3.11x against 1.85x, absolute drift up 3.95x against 2.63x — **and its strategies
responded 3.3x less.**

If directionality drove the response, BTC should have responded *more*. It
responded less. The explanation is not merely unsupported; **it points the wrong
way.**

## What survives, and what this costs the story

**The within-instrument time pattern survives.** Both markets became more
directional in the 150-300 band (efficiency 0.0242 → 0.0447 on XAU, 0.0259 →
0.0805 on BTC), which is what Rounds 228, 247 and 248 describe and what both
instruments' strategy responses show in direction.

**The cross-instrument magnitude is now unexplained.** The directional-regime
story explains *when* the response happened; it does not explain *how large* it
was on each instrument, and the one obvious mechanism for that is refuted.

## One observation, explicitly untested

The two strong bands are directional in **opposite directions**: XAU's drift is
**+16.89%** (uptrend) while BTC's is **−48.18%** (a large downtrend). Both are
"directional" by the efficiency measure, but a strategy population that handles
uptrends better than downtrends would produce exactly the observed pattern —
strong response on the uptrending instrument, weak on the downtrending one.

**This is a hypothesis, not a finding.** It was not tested, and after Rounds 228,
230 and 249 I am not going to present a story fitted to two data points as
anything else. The test is concrete: measure the candidate population's
performance in up-trending versus down-trending segments and see whether the
asymmetry exists.

## What is proven, and what is not

Proven:

- 4h band statistics: XAU efficiency 0.0242 → 0.0447 with drift −6.43% → +16.89%;
  BTC efficiency 0.0259 → 0.0805 with drift +12.21% → −48.18%.
- Efficiency ratios 1.85x (XAU) against 3.11x (BTC); |drift| ratios 2.63x against
  3.95x — both larger on BTC, whose strategy response was 3.3x smaller.

Not proven, and deliberately not claimed:

- That long/short asymmetry explains the gap. Two instruments, one window,
  untested.
- That the directional-regime description is wrong. It survives for the
  within-instrument time pattern; what fails is using it to explain the
  cross-instrument magnitude.
- Any statistical weight for these ratios. Four band-statistics on two
  instruments, no confidence intervals.
