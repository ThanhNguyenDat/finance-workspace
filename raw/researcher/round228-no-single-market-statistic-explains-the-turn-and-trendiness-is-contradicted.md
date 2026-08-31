# Round 228 — Six market statistics against the segment ratios: trendiness is contradicted, and the two transitions have different signatures

Classification: **NO-CHANGE**. No containers — one read-only query and local
computation on the same five segments as Round 227.

## The question

Round 227 measured the walk-forward ratio sequence across five ~360-day segments
of exness XAU 4h (−0.114, −0.264, +0.151, +0.158, +0.659) and showed volatility
cannot explain the **S2 → S3** turn, because volatility *falls* there. It left
"what changed around 1,080 days ago" open.

Six statistics computed per segment from the same OHLC, all cheap and all
derivable without a backtest:

| seg | ratio | volatility | lag-1 autocorr | Kaufman efficiency | drift | median range | body/range |
|---|---|---|---|---|---|---|---|
| S1 | −0.114 | 0.1549% | +0.0183 | 0.0132 | −5.24% | 0.392% | 0.452 |
| S2 | −0.264 | 0.1520% | +0.0315 | 0.0366 | +13.93% | 0.375% | 0.452 |
| S3 | +0.151 | 0.1471% | +0.0276 | 0.0753 | +26.89% | 0.385% | 0.436 |
| S4 | +0.158 | 0.1820% | +0.0172 | 0.0805 | +34.73% | 0.456% | 0.446 |
| S5 | +0.659 | 0.3143% | +0.0178 | 0.0278 | +22.85% | 0.769% | 0.443 |

## Result 1 — the trendiness hypothesis is contradicted, not merely unsupported

The intuitive explanation for "signals started working" is that the market became
trendier. It did not.

**Lag-1 autocorrelation is essentially zero in every segment** (+0.017 to +0.032)
and its ordering runs *against* the ratio sequence — 2 of 10 concordant pairs.
The two segments with the highest autocorrelation are S2 (worst ratio) and S3.
Body-to-range, another persistence proxy, is 3 of 10.

Whatever changed, it is not that 4h gold bars started following each other.

## Result 2 — the two transitions do not share a signature

Reading the transitions separately, which is what Round 227's finding demanded:

**S2 → S3** (ratio −0.264 → +0.151, the turn that volatility cannot explain):

| statistic | S2 → S3 |
|---|---|
| Kaufman efficiency | 0.0366 → **0.0753** (roughly doubles) |
| drift | +13.9% → **+26.9%** (roughly doubles) |
| volatility | 0.1520% → 0.1471% (falls) |
| median range | 0.375% → 0.385% (+2.7%, flat) |
| lag-1 autocorrelation | +0.0315 → +0.0276 (falls) |

**S4 → S5** (ratio +0.158 → +0.659):

| statistic | S4 → S5 |
|---|---|
| volatility | 0.1820% → **0.3143%** (1.73x) |
| median range | 0.456% → **0.769%** (1.69x) |
| Kaufman efficiency | 0.0805 → **0.0278** (collapses to a third) |
| drift | +34.7% → +22.9% (falls) |

The two jumps move opposite statistics. S2→S3 is **directionality** at flat
volatility; S4→S5 is **volatility** at collapsing directionality. No single
statistic tracks both, which is why the overall concordance counts are
unimpressive for everything: range 9/10, volatility 8/10, drift 7/10, efficiency
6/10, body 3/10, autocorrelation 2/10.

This is consistent with Round 227's conclusion rather than a refinement of it:
the two halves of the gradient genuinely have different causes.

## The honest caveat, stated before anyone leans on the table

**Five segments.** Concordance counts out of ten pairs at n=5 cannot distinguish
9/10 from 6/10 in any meaningful sense, and no significance test was performed
because none would be credible. The ranking of the six statistics should not be
read as a ranking.

What survives the small sample is the *sign* evidence, which does not depend on
ordering: autocorrelation is near zero everywhere and moves the wrong way; and
across S2→S3 specifically, volatility and range are flat while efficiency and
drift double. Those are statements about individual transitions, not about a
fitted relationship.

**A story fitted to five points is a story, not a finding.** Recorded as the
former.

## What is proven, and what is not

Proven:

- Per-segment values for all six statistics as tabulated above.
- Lag-1 autocorrelation is between +0.017 and +0.032 in every segment and is
  anti-concordant with the ratio sequence (2/10).
- Across S2→S3 efficiency and drift roughly double while volatility falls and
  range is flat; across S4→S5 volatility and range rise ~1.7x while efficiency
  falls to a third.

Not proven, and deliberately not claimed:

- That directionality caused the S2→S3 turn. Two statistics co-moved with one
  transition at n=5; that is a coincidence-compatible observation.
- Any causal claim at all. These are price statistics measured on the same bars
  the strategies traded, so co-movement is expected wherever a strategy family
  keys on the same property.
- That the list is exhaustive. Six statistics derivable from OHLC were tested;
  order flow, positioning, macro regime and session structure were not.
