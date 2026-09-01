# Round 216 — At the production 5m interval, 31% of candidates have positive gross edge and friction kills 96% of them

Classification: **NO-CHANGE**. A directional prediction from the cost model,
tested on an interval this sweep had never been run at, and confirmed. Nothing
promoted, no defect found. Two bounded Docker sweeps.

## The prediction being tested

Rounds 213-215 built a cost picture entirely at **4h**. The model says friction
scales with trade count while gross edge does not. That yields a falsifiable
prediction for the **5m** interval production actually trades: with roughly five
times the trades per candidate, the production-cost pass count should fall and
the zero-cost pass count should not — so the gap between them should widen.

If the gap had stayed the same or narrowed, the cost story would be incomplete.

## Result — confirmed, and more sharply than expected

| interval | window | candles | median train trades | pass at production cost | pass at zero cost | gap |
|---|---|---|---|---|---|---|
| 4h | 1,800d | 7,880 | 99 | **2** | **14** | 12 |
| **5m** | **365d** | **70,852** | **536** | **1** | **24** | **23** |

At 5m the production-cost count *falls* to one while the zero-cost count nearly
doubles to 24. The gap widens from 12 to 23, as predicted.

Stated the way that matters: **24 of 77 candidates (31%) show positive gross edge
on all three splits at 5m. Exactly one survives friction. Friction kills 96% of
the gross-positive set.**

That is the sharpest measurement of the cost constraint this program has produced.
The 5m interval is not short of signal — it is short of signal that survives the
cost of harvesting it, and it is worse than 4h on exactly the axis the model
predicted.

## The survivor confirms the mechanism, and is disqualified by our own rule

`sma10_trend_filtered_fibonacci_golden_zone_100`:

| split | trades | PF (production cost) | PnL | PF (zero cost) |
|---|---|---|---|---|
| train | 47 | 1.26 | +0.79 | 1.41 |
| validation | **18** | 1.16 | +0.12 | 1.39 |
| holdout | **16** | 4.15 | +0.88 | 4.99 |

Against a **median of 1,531 train trades** across the gross-positive set, this
candidate trades 47. The only candidate that survives friction is the one that
barely pays it — the mechanism, seen directly.

**It is not a lead, by this program's own rule.** Round 210 established that a
per-split PF from fewer than ~30 trades carries no usable information; this
candidate's validation (18) and holdout (16) are both below that floor. It is
also a variant of the Fibonacci Golden Zone direction already closed in Rounds
105-106, reappearing at a different interval on a thin sample — the exact
false-positive shape Round 205 warned about.

Recording it as a survivor of the *cost* test while explicitly refusing it as a
*candidate* is the honest reading. Both things are true.

## What is proven, and what is not

Proven:

- exness XAU 5m, 365 days, 70,852 candles: 1 of 77 candidates clears all three
  splits at production cost, 24 of 77 at zero cost.
- The cost gap is 23 at 5m against 12 at 4h, in the predicted direction.
- The lone survivor trades 47/18/16 against a gross-positive-set median of 1,531
  train trades.

Not proven, and deliberately not claimed:

- That interval alone explains the difference. The two runs use different
  calendar windows (1,800 days at 4h, 365 days at 5m), so this is **not** a
  controlled comparison of interval. What *is* internally controlled is the
  production-versus-zero-cost gap within each interval, which is the quantity
  actually compared — each gap is measured on identical data.
- That any of the 24 gross-positive candidates is tradeable. They are not; they
  pass only with all friction removed.
- That the friction numbers are real. Round 215's limitation carries in full:
  `fee_bps 5.0 / slippage_bps 2.0` is a model, not a measurement, and
  `finance-api/src/deployment_rules.rs` shows production uses the same modelled
  pair — so production PnL rests on the same unmeasured assumption. Nothing here
  escapes that.

## Note on what this does not open

The obvious inference — trade a slower interval to pay less friction — is already
closed. Round 92 measured the Target 3 frequency margin as thin (~9.3/week over
five years, ~7.2-7.3/week over 18 months) and closed the "extend hold" direction
because further reductions breach the >= 7/week floor. This round strengthens the
diagnosis without reopening that lever.
