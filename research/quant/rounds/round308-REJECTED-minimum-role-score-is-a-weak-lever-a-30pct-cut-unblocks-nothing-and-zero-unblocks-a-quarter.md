# Round 308 — REJECTED: `minimum_role_score` is a weak frequency lever. A **30% cut unblocks nothing**; driving it to **zero** unblocks under a quarter. Three-quarters of blocks are **sign conflicts**.

Classification: **REJECTED** — lowering the role-score threshold to raise trade
frequency is rejected on **reach**, from accumulated live evidence, before spending a
container on it. **Zero containers, zero SSH**: the 26 samples already in
`research/quant/samples/signal-state-samples.csv` plus one local code read.

## The question Round 307 deferred

Round 307 verified that every live gate reason reproduces from the code and closed
with: *"whether `minimum_role_score = 0.1` is the right threshold is a different
question and was **not examined**."*

It is the obvious frequency lever — five of six routes were gate-blocked at the last
read, so a lower threshold means more passes, more targets, more closes. But the gate
has **three** conditions (`trading_modes.rs:850-857`), and the threshold only touches
two of them:

| condition | line | threshold-sensitive? |
|---|---|---|
| `entry_score.abs() < minimum_role_score` | 850 | **yes** |
| `trend_score.abs() < minimum_role_score` | 853 | **yes** |
| `entry_score` and `trend_score` disagree in sign | 857 | **no** |

A block caused by sign disagreement cannot be fixed at any threshold. So the lever's
ceiling is measurable without running anything.

**Registered before computing:** the threshold is a weak lever — **fewer than half** of
the recorded blocks would pass even at `minimum_role_score = 0`.

## The measurement

26 recorded samples (rounds 265-270 and 307): **4 passed, 22 blocked**.

| block reason | count |
|---|---|
| `entry_trend_conflict` | **10** |
| `entry_score_below_threshold` | 7 |
| `trend_score_below_threshold` | 4 |
| `stale_timeframe_evidence:15m` | 1 |

Excluding the one staleness block, **21 blocks**. At threshold 0 the two magnitude
checks vanish and only the sign test remains, so a block clears at zero **iff the two
scores share a sign**:

| threshold | blocks cleared | share |
|---|---|---|
| **0.100** (deployed) | 0 | — |
| 0.090 | **0** | 0.0% |
| **0.070** (a 30% cut) | **0** | **0.0%** |
| 0.050 (halved) | 2 | 9.5% |
| 0.040 | 3 | 14.3% |
| 0.010 (a 10x cut) | 4 | 19.0% |
| **0.000** (gate removed) | **5** | **23.8%** |

**A 30% reduction changes nothing at all. A 10x reduction unblocks four of twenty-one.
Deleting the check entirely unblocks five.** The prediction holds, and by a wide
margin: **16 of 22 blocks (72.7%) are sign conflicts and are immune to the threshold.**

## The trap in the labels

`entry_score_below_threshold` and `trend_score_below_threshold` account for 11 of the
22 blocks, which reads as "half the blocks are threshold-fixable". **They are not.**
The three conditions are evaluated in order, so a magnitude failure fires **first** and
masks a sign conflict underneath. Checking the scores directly:

**6 of those 11 magnitude-labelled blocks (55%) also have conflicting signs.** Counting
gate-reason labels overstates the lever by more than **2x** — 50% claimed against 22.7%
real.

The clearest live instance is `binance BTC` at Round 307: `|trend_score|` = 0.01048,
reported as `trend_score_below_threshold`. Lower the threshold below 0.01 and it does
not pass — `entry_score` is −0.1278 against `trend_score` +0.0105, so it lands
immediately on `entry_trend_conflict`.

The five clearable blocks are also concentrated: **four are `exness BTC`, one is
`bybit XAUT`**, and they need thresholds of 0.0693, 0.0693, 0.0405, 0.0119 and 0.0090
respectively.

## The tooling gap, recorded and not acted on

Even if the reach were better, the joint objective could not be evaluated:
**`minimum_role_score` is not exposed by the research CLI.** It is a `TradingPolicy`
field (`crates/finance-core/src/trading_modes.rs:427`, set and clamped at `:459`,
`:465`, read at `:850` and `:853`), and `crates/finance-research/src/main.rs` has **no
matching argument** — unlike `--portfolio-stop-value`, `--portfolio-take-value`,
`--portfolio-atr-periods` and `--portfolio-minimum-hold-decisions`, which all mirror
their runtime settings.

So PnL, PF, Sharpe/Sortino, drawdown and streak at a different threshold **cannot be
measured today**. This is the same class of gap Round 84 recorded for the protective
band, and it is recorded here as **investigation only — not applied**; implementation
is not Claude's to do.

Note that an A/B at a **fixed `--days`** would have been methodologically clean even
after Rounds 300-305, since those only invalidate comparisons *across* window lengths.
That makes the missing flag the binding constraint rather than the confound.

## What is proven, and what is not

Proven:

- 26 samples: 4 gate passes, 22 blocks; reasons 10 / 7 / 4 / 1 as tabulated.
- Of 21 non-stale blocks, the number clearing at thresholds 0.09 / 0.07 / 0.05 / 0.04 /
  0.01 / 0.00 is 0 / 0 / 2 / 3 / 4 / 5.
- 16 of 22 blocks (72.7%) have conflicting score signs and cannot clear at any
  threshold.
- 6 of the 11 magnitude-labelled blocks (55%) also have conflicting signs.
- `minimum_role_score` exists at `trading_modes.rs:427/459/465/850/853` and has no
  corresponding flag in `finance-research/src/main.rs`.

Not proven, and deliberately not claimed:

- **Anything about profitability at a different threshold.** Not measurable with the
  current tool; no PnL, PF, Sharpe or drawdown claim is made in either direction.
- That the sample is large or independent. **21 blocks but only 16 distinct
  (route, entry_score, trend_score) states, across 5 routes and 6 observation
  moments** — several routes were sampled minutes apart and carry an identical
  `trend_score`, so the effective sample is far smaller than 21. The curve above should
  be read as the shape of a small, autocorrelated snapshot, not as a fleet statistic.
  On distinct states only, the zero-threshold share is 5/16 = 31.2% rather than 23.8% —
  the conclusion survives either way, the number moves.
- That lowering the threshold would be *harmful*. It is rejected as a **frequency
  lever** because it barely reaches; whether the trades it would admit are good or bad
  is untested.
- That `entry_trend_conflict` is itself well-calibrated. It dominates the blocks, which
  makes it the more interesting parameter — and it has no threshold at all, so it is a
  different kind of question entirely. Not examined.
