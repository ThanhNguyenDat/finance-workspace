# ⚠️ QUALIFICATION (Round 218)

The **8x gap** below is a **5m** number, not a property of gold. Round 218
measured the same edge-to-friction ratio at other intervals: **0.057 at 5m**
(gap ~18x on holdout medians), **0.331 at 1h**, and **0.659 at 4h** on the long
window (gap ~1.5x) — friction per trade is flat at ~0.0070 across all three, so
the whole difference is edge per trade. This file's measurements stand; its
implied verdict on gold as a whole does not.
See `round218-the-gap-closes-with-interval-1.5x-at-4h-not-8x.md`.

---

# Round 217 — Sizing the gap: gold 5m signals do carry positive out-of-sample edge, and it is roughly one order of magnitude smaller than the friction

Classification: **NO-CHANGE**. No new sweeps — this is analysis of Round 216's
saved production-cost and zero-cost runs. Nothing promoted, no defect found.

## The question the program had never asked

Every round so far has answered "does this candidate pass?" None has asked **"by
how much does it miss?"** A direction that misses by 20% is worth attacking; one
that misses by 800% is not. The two Round 216 runs make the number computable
without any assumption about sizing or notional, because friction can be measured
by difference:

```
friction per trade = (zero-cost PnL - production PnL) / trades
edge per trade     = zero-cost PnL / trades
```

Restricted to cells with **>= 30 trades** (Round 210's information floor): 193
candidate-split cells on exness XAU 5m, 365 days.

## Friction is a near-constant per-trade tax

| | value |
|---|---|
| friction per trade, median | **0.00701** |
| p10 / p90 | 0.00685 / 0.00714 |

A 4% spread between the 10th and 90th percentile across 193 cells. Friction is
effectively a fixed toll per trade, exactly as the cost model assumes — this is
the first time it has been measured rather than assumed to behave that way.

## The gap

| | value |
|---|---|
| cells with edge/friction ratio > 1 | **14 of 193 (7.3%)** |
| **median ratio** | **0.035** |
| p90 ratio | 0.674 |
| candidates with ratio > 1 on **all three** splits | **0** |
| candidates with ratio > 1 on two splits | 1 (`donchian_breakout_200`) |

**The median candidate at 5m generates gross edge worth 3.5% of the friction it
pays.** Even the 90th percentile does not reach parity. Not one candidate
out-earns its friction on all three splits.

## Out of sample, the signal is real — and about 8x too small

Holdout only, cells with >= 30 trades, grouped by mechanism family:

| family | n | median edge per trade | share positive |
|---|---|---|---|
| breakout | 11 | **+0.00086** | **82%** |
| trend / momentum | 23 | +0.00043 | **83%** |
| reversion | 18 | +0.00037 | 61% |
| other | 10 | +0.00009 | 60% |
| *friction per trade* | | *0.00701* | |

Two things are true at once and both matter.

**There is real signal.** 82-83% of breakout and trend/momentum cells have
positive gross edge *out of sample*. After 200-odd rounds of "nothing works",
that is worth stating plainly: the mechanisms are not noise.

**The signal is roughly an order of magnitude too small.** The best family's
holdout median is 0.00086 against friction of 0.00701 — a ratio of **0.12**. The
gap is about **8x**, not 20%.

That number is the point of this round. An 8x gap is not closable by execution
tuning (Round 215 measured the whole realistic cost improvement as worth about
zero candidates), by parameter search (Rounds 88-93, 149-151, 204-205), or by a
better indicator (0 for 15+). The program has been trying to close an 8x gap with
1.1x tools.

## A family story I nearly recorded, and why I did not

Ranked by ratio, the top eight cells looked like a clean structural finding:
breakout mechanisms on top (`opening_range_breakout_london_30m` 4.41,
`atr_breakout_14_3_0` 2.79, `donchian_breakout_200` 1.87) and reversion at the
bottom (`session_vwap_reversion_london` −1.80, `rsi_mean_reversion_session` −1.93).

**Six of those top eight cells are `train`.** Recomputing on holdout only
dissolves the story: reversion's median edge per trade is *positive* (+0.00037,
61% of cells) and sits within 2x of trend/momentum. Breakout still leads, but the
ordering is a mild in-sample gradient, not the categorical split the ranked list
suggested. Recorded here as a near-miss so the next round does not re-derive it
from the same table.

## What is proven, and what is not

Proven:

- Friction per trade at 5m is 0.00701 median, p10-p90 spread of 4%.
- Median edge/friction ratio is 0.035; 14 of 193 cells exceed 1; no candidate
  exceeds 1 on all three splits.
- Holdout median edge per trade by family: breakout +0.00086, trend/momentum
  +0.00043, reversion +0.00037, other +0.00009; 82-83% of breakout and
  trend/momentum holdout cells are positive.

Not proven, and deliberately not claimed:

- That the 8x gap holds at other intervals or instruments. Only exness XAU 5m
  over 365 days was measured. Round 216 showed 4h is less cost-bound, so the gap
  there is smaller and was not computed.
- That the family medians are significant. They are medians over 10-23 cells with
  no significance test, and Rounds 210-211 showed per-cell figures are noisy.
- That friction is 0.00701 in reality. It is 0.00701 *in the model*
  (`fee_bps 5.0`, `slippage_bps 2.0`, `funding_rate_bps 1.0`), and Round 215's
  limitation stands: the model has never been checked against a real fill.
  If real friction were half the model's, the gap would be 4x, not 8x — still
  not closable, which is why this conclusion survives that uncertainty.
