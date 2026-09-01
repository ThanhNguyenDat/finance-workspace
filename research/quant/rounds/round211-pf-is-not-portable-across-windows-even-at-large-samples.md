# Round 211 — Changing only the window moves large-sample PF by 30%: the conjunction bar is stable, its components are not

Classification: **NO-CHANGE**. Nothing promoted, no defect found. One bounded
Docker sweep (the 500-day control was reused from Round 210's saved output).

## The question

Round 210 measured cross-source PF disagreement and attributed it to small
samples: the gap fell from 53.8% (under 30 trades) to 18.3% (30+ trades on both
sources). That framing implies more trades would fix it.

This round tests the other axis. Same source, same engine, same interval, same
candidates — **only the window changes**:

```
finance-research --broker exness --market-type cfd --base-asset XAU
                 --quote-asset USD --interval 4h  --days {500 | 1800}
```

| window | candles | train / validation / holdout |
|---|---|---|
| 500 days (Round 210) | 2,191 | 1,315 / 438 / 438 |
| 1,800 days (this round) | 7,880 | 4,728 / 1,576 / 1,576 |

**These are not independent samples.** The 500-day window is contained in the
1,800-day one, and the 60/20/20 boundaries fall in completely different places.
This is a window-and-partition sensitivity test, not a replication — which makes
the result below stronger, not weaker: the data overlaps and the answers still
move.

## Result — sample size does not cure it

| cells | n | mean relative PF change, 500d → 1,800d |
|---|---|---|
| all | 23 | **47.6%** |
| **>= 100 trades in both windows** | 4 | **29.9%** |
| 30-99 trades in both | 2 | 6.4% *(n=2, no weight — reported only for completeness)* |
| < 30 trades in either | 17 | 56.6% |

**11 of 23 cells (48%) flip the binary "PF > 1?" answer.**

The four large-sample cells in full:

| candidate | split | PF 500d → 1,800d | rel. change | trades |
|---|---|---|---|---|
| `heikin_ashi_momentum_1` | train | 0.88 → 0.58 | 34.1% | 316 → 1,137 |
| `heikin_ashi_momentum_1` | validation | 1.03 → 0.95 | 7.8% | 108 → 350 |
| `heikin_ashi_momentum_1` | holdout | 0.58 → 0.86 | 32.6% | 109 → 388 |
| `heikin_ashi_momentum_3` | train | 1.17 → 0.64 | 45.3% | 132 → 466 |

Three of those four are **worse** on the five-year window.

This is a different mechanism from Round 210's finding. There, disagreement
shrank as trade count grew, which is what sampling noise does. Here, cells with
300-1,100 trades still move 30-45% when the window changes. Sampling noise does
not behave that way. This is regime dependence: the recent 500 days were a
friendlier environment for these strategies than the full five years, and no
amount of additional trades *within* a window fixes a wrong choice *of* window.

**Put together with Round 210: at comparable sample sizes, changing the window
(29.9%) moves PF more than changing the price source (18.3%).**

## What stayed stable

On the 1,800-day window, **no candidate clears PF > 1 on all three splits** —
identical to the 500-day exness run and to the bybit XAUT run in Round 210.
`donchian_breakout_20` reads 0.94 / 0.66 / 1.62, `donchian_breakout_55` reads
1.05 / 0.32 / 1.28, `keltner_reversion_20_2_0` reads 0.73 / 1.48 / 0.51 — every
one has at least one split below 1.

So across two price sources and two windows spanning 3.6x of data, the
all-three-splits conjunction returned the same verdict every time, while its
individual components flipped in roughly half of all cells. The bar works
because it is a conjunction of unreliable tests, not because any single test is
reliable.

## Practice consequences (research-only, nothing to implement)

1. **Never quote a single-split PF as a property of a strategy.** It is a
   property of a strategy *and* a window *and* a partition. Round 210 established
   this for samples under 30 trades; this round extends it to 100+ trades.
2. **Prefer the longest available window — for regime coverage, not accuracy.**
   The five-year exness numbers are not "more precise" per split; they include
   more regimes, and 3 of 4 large-sample cells got worse when those regimes were
   added. A 500-day result that looks good may simply be a friendly regime.
3. **Keep the all-three-splits-both-sources bar exactly as it is.** It is the
   only measure in this program that has now survived a source change and a 3.6x
   window change without changing a single verdict.

## What is proven, and what is not

Proven:

- Same source, same engine, window 500d → 1,800d: mean relative PF change 47.6%
  across 23 cells; 29.9% restricted to cells with 100+ trades in both.
- 11 of 23 cells flip the binary PF > 1 answer.
- No candidate clears all three splits on the 1,800-day window, matching both
  Round 210 runs.

Not proven, and deliberately not claimed:

- That the older data is "worse" in a causal sense. Three of four large-sample
  cells declined; that is a direction, not an explanation, and no regime analysis
  was run to attribute it.
- Any independent replication. The windows overlap by construction; this measures
  sensitivity, not reproducibility.
- Anything about the 30-99 trade bucket. It has two cells.
- Anything outside exness XAU 4h.
