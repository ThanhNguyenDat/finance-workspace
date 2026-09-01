# Round 270 — The gate's entry/trend asymmetry is real in design but does not bind in practice; and `gate_passed` is not a trade, which moves suspicion downstream

Classification: **NEEDS-MORE-RESEARCH**. Read-only production sampling.
**Zero containers.**

## The asymmetry, stated properly for the first time

Round 267 computed the entry threshold's severity per route but never named what
causes it: **`minimum_role_score` is a single absolute number compared against both
roles, while the two roles have very unequal weight budgets.** `entry_score` can
never exceed the entry interval-weight budget, `trend_score` never the trend budget.

| route | entry budget | 0.1 as % of it | trend budget | 0.1 as % of it | asymmetry |
|---|---|---|---|---|---|
| binance XAU | 0.1437 | **69.6%** | 0.8564 | 11.7% | **6.0x** |
| bybit XAUT | 0.2933 | 34.1% | 0.7068 | 14.1% | 2.4x |
| exness XAU | 0.2523 | 39.6% | 0.7475 | 13.4% | 3.0x |

**The same threshold is 2.4x to 6x stricter on entry than on trend, by construction.**

## But it does not bind that way

Across all 20 samples now in `research/quant/samples/signal-state-samples.csv` (rounds 265,
266, 267, 269, 270):

| route | n | \|entry\| < 0.1 | \|trend\| < 0.1 | gate passes |
|---|---|---|---|---|
| binance BTC | 5 | 1 | 1 | 0 |
| **binance XAU** | 5 | 3 | 0 | **2** |
| bybit XAUT | 5 | 0 | 0 | 0 |
| exness BTC | 5 | 2 | 4 | 1 |
| **POOLED** | **20** | **6 (30%)** | **5 (25%)** | **3** |

**Entry falls below the threshold in 30% of samples and trend in 25% — nearly
equal**, despite the 2.4-6x design asymmetry. `entry_score` evidently uses a large
fraction of its small budget routinely, while `trend_score` uses a small fraction of
its large one, and the two land at similar absolute magnitudes.

**The design asymmetry is real; the binding asymmetry it predicts is not observed.**
That is the second time in three rounds (Round 269 was the first) that a structural
argument about the entry budget has failed to survive contact with the samples.

## The correction that matters: `gate_passed` is not a trade

`binance XAU` now shows **2 passes in 5 samples** — the highest observed rate in the
log — while producing **1 close in 571 decisions (0.18%)** over the live window
(Round 264/265). Those two numbers cannot both describe the same quantity, and they
do not:

- `gate_passed` marks a decision with a directional stance;
- a **close** requires `portfolio_construction.construct()` to act, subject to
  `minimum_hold_decisions` (36 ≈ 3h) and the existing position, and then an exit via
  stop, take or flat.

So a pass with a position already open in the same direction produces **no new
trade**, and no close. **Gate pass rate and close rate are different quantities and
I have been treating them as comparable across Rounds 265-269.**

The consequence is a genuine narrowing: `binance XAU`'s gate **does** pass, at least
sometimes. Its low close count is therefore **downstream of the gate** — in position
construction, the hold guard, or the exit conditions — not at the gate itself. That
is the first time this thread has located the loss downstream rather than at or
before `decide()`.

## What is proven, and what is not

Proven:

- The budget/threshold table above, from Round 267's `interval_weights`.
- Across 20 samples: entry below threshold 6 times, trend 5 times, 3 gate passes,
  2 of them on `binance XAU`.
- `construct()` applies the hold guard and position state after `decide()`, so a
  gate pass does not imply a trade or a close.

Not proven, and deliberately not claimed:

- **That `binance XAU` passes more often than other routes.** 2 of 5 against 0 of 5
  is four samples' difference. Rounds 261 and 264 established the live differences
  are inside noise, and nothing here overturns that.
- That the design asymmetry is harmless. It is shown not to produce an observed
  binding asymmetry **in 20 samples**; that is a small sample and a single day.
- That the loss is definitely downstream. What is established is that the gate is
  not a total block; how much is lost at the gate versus after it is unmeasured.
- Which of seed or weights is the cause. Unchanged since Round 263.
- Anything about PnL or Target 3.
