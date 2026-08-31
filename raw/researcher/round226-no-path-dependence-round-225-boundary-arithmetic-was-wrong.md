# Round 226 — There is no path dependence: with the holdout period held fixed, three history lengths give byte-identical results. Round 225's mechanism and its boundary arithmetic were both wrong

Classification: **NO-CHANGE**. Two bounded Docker sweeps. This round refutes my
own explanation from the previous round.

## The claim under test

Round 225 explained its window-test failure like this:

> The ledger is path-dependent — equity state, open positions and the 1d trend
> filter's warmup all differ depending on where the run starts — so the
> candidate's apparent 1,800-day strength is partly a property of the history it
> was fed, not of the signal alone.

That is a strong claim about the engine, and it was asserted from an inference,
not a measurement. It is directly testable: hold the **evaluation period fixed**
and vary only how much history precedes it.

Three runs on binance BTC/USDT 4h+1d, ratios chosen so the holdout is always the
last ~360 days:

| history | ratios | holdout candles |
|---|---|---|
| 1,800d | 60/20/20 | 2,160 |
| 1,200d | 50/20/**30** | 2,159 |
| 900d | 40/20/**40** | 2,159 |

## Result — no path dependence whatsoever

`mtf_candle_momentum_10bps_sma10_trend_filtered`, holdout:

| history | trades | PF | PnL |
|---|---|---|---|
| 1,800d | 62 | 1.12 | +0.53 |
| 1,200d | 62 | 1.12 | +0.53 |
| 900d | 62 | 1.12 | +0.53 |

Identical. And at population level over the same fixed holdout:

| history | cells >= 30 trades | median PF | median PnL |
|---|---|---|---|
| 1,800d | 63 | 0.890 | −0.81 |
| 1,200d | 63 | 0.890 | −0.81 |
| 900d | 63 | 0.890 | −0.81 |

**0 of 63 candidates change their holdout PF by more than 10%**, and 59 of 63
have identical holdout trade counts (the four that differ are warmup-sensitive
indicators, a small and expected effect).

**Each split is evaluated on its own ledger, independent of how much history
preceded it.** Round 225's mechanism is refuted.

## And the "decisive contradiction" was my arithmetic error

Round 225 claimed the 1,800d and 900d runs assigned opposite verdicts to the
*same* calendar period. Recomputing the boundaries:

| run | train | validation | holdout |
|---|---|---|---|
| 1,800d, 60/20/20 | 1800 → 720 ago | 720 → 360 | 360 → 0 |
| 900d, 60/20/20 | **900 → 360 ago** | **360 → 180** | 180 → 0 |

Round 225 wrote the 900-day split as "train 900→540, validation 540→360". That is
wrong — 60% of 900 days is 540 days, so train ends 360 days ago, not 540. The two
runs' validation segments cover **different** periods (720→360 versus 360→180).
There was no same-period contradiction to explain, which is why the mechanism
invented to explain it does not exist.

## What survives from Round 225

The verdict does, on simpler and correctly-stated grounds.

With boundaries computed properly, the candidate reads:

- **1800 → 720 days ago**: PF 1.10 — good
- **720 → 360 ago**: PF 1.17 — good
- **900 → 360 ago** (the 900d run's train, overlapping the two above): PF **0.91**,
  PnL **−0.76** — bad
- **360 → 180 ago**: PF **0.79**, PnL **−0.59** — bad
- **360 → 0 ago**: PF 1.12 — good

A weak sub-period can legitimately hide inside a longer strong aggregate; that is
not a contradiction, it is what aggregation does. But it does mean the candidate
has a real soft patch, and "not promotable" stands — on **regime dependence**,
which is measured, rather than **path dependence**, which is disproven.

## The useful methodological fact this establishes

The program can now rely on something it never verified: **window comparisons are
about which calendar periods are included, not about run mechanics.** When two
windows disagree, the explanation is always in the data, never in the engine.
That removes an entire class of speculation from future rounds — including the
speculation I published last round.

Note also that full-stack survivor counts still vary (2 / 3 / 3) across these
three runs despite the identical holdout, because their train and validation
periods differ. That is Round 211's effect and is unaffected by this finding.

## What is proven, and what is not

Proven:

- With the holdout period fixed, varying preceding history from 1,800 to 900 days
  changes nothing: identical trades, PF and PnL for the candidate, identical
  population medians, 0 of 63 candidates moving more than 10%.
- Round 225's split-boundary arithmetic for the 900-day run was wrong; the two
  runs' validation segments do not overlap.
- The candidate is weak over 900→360 and 360→180 days ago, strong over
  1800→720, 720→360 and 360→0.

Not proven, and deliberately not claimed:

- That warmup never matters. Four of 63 candidates changed trade counts; the
  effect is small here but was not characterised.
- That the candidate should be reconsidered. The soft patch is real and the
  rejection stands; only the explanation changed.
