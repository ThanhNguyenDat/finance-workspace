# Round 389 — NEEDS-MORE-RESEARCH: the **first correctly-measured holdout scorecard** in 184 iterations. The edge is **real** — and costs are **157% of it**.

Classification: **NEEDS-MORE-RESEARCH**. **Zero containers**, read from a run
already held. This is the measurement the entire arc has been unable to make.

## What is now possible that was not

`exness.cfd.XAU.USD` @900, **deployed configuration with `minimum_hold_decisions`
36**, holdout only, pinned window, scored through the **Portfolio-faithful**
replay. Every one of those clauses was impossible before this transaction: the
gate rejected a hold value outright (`conflicts_with`, r356), it scored the
unguarded stream, and no window could be pinned (r382).

Holdout: **2026-03-04 → 2026-08-31, 34,851 candles, 179.7 calendar days, 152
observed days.**

## The scorecard

| metric | value | threshold | |
|---|---|---|---|
| **`gross_pnl_before_costs`** | **+0.664709** | > 0 | **PASS** |
| **`total_cost_drag`** | **1.042052** | — | |
| **`net_realized_pnl`** | **−0.377343** | — | |
| **`cost_to_gross_pnl_ratio`** | **1.567682** | ≤ 0.5 | **FAIL, 3.1× over** |
| `sharpe_ratio` | −0.810499 | ≥ 1.0 | FAIL |
| `sortino_ratio` | −1.150073 | ≥ 1.0 | FAIL |
| `positive_day_ratio` | 0.401316 | ≥ 0.55 | FAIL |
| `median_daily_pnl` | 0.0 | > 0 | FAIL |
| `trades_per_week` | 6.232 | ≥ 7.0 | FAIL, by 11% |
| `maximum_negative_day_streak` | 5 | ≤ 5 | PASS, at the limit |
| `maximum_total_drawdown_fraction` | 7.3e−05 | ≤ 0.1 | PASS |
| `minimum_holdout_days` | 179.7 | ≥ 90 | **PASS** |
| `holdout_interval_continuity` | 0 violations | — | PASS |

Also reported: skewness +0.284, excess kurtosis +0.647, max drawdown duration
134 days, ulcer index 3.7e−05, closed trades 160.

## The one number that matters

**The Portfolio has positive gross edge on holdout — and costs are 157% of it.**

`cost_to_gross_pnl_ratio` **1.5677** against a 0.5 threshold. That is the binding
constraint, over by **3.1×**, and every other failure follows from it: a strategy
whose costs exceed its gross edge cannot have positive Sharpe, a positive median
day, or a positive-day ratio above half.

Rounds 216 and 217 suspected this ("friction kills 96% of gross-positive
candidates", "the gap is 8×, not marginal") from full-window, in-sample,
wrong-path measurements. **It is now measured on holdout, on the deployed
configuration, through the replay that actually models the Portfolio.** The
suspicion was right and the magnitude is 1.57×, not 8×.

## Two structural blockers, re-checked

- **`minimum_holdout_days` now PASSES.** Rounds 335/336 concluded `exness XAU`
  "can never pass the gate at any window" partly because a 500-day run gave 84
  observed days against a 90-day minimum. At **900 days it gives 152**. That
  half of the blocker is lifted by window depth, not by any code change.
- **Seven `input_continuity_failed` intervals remain** — 15m, 30m, 1h, 2h, 4h,
  12h, 1d; every interval except 5m. This is the CFD trading calendar (r337) and
  it is **structural**: the gate's overall verdict cannot pass on this route
  while those checks are counted, regardless of performance.

So r335/r336 were right that the route cannot pass, and **wrong about which part
was permanent**.

## Honest reporting of what could not be computed

The gate declares three metrics **unavailable with reasons** rather than
emitting zeros: `information_ratio` (needs a benchmark daily return series),
`system_quality_number` (needs a per-trade R-multiple distribution),
`maximum_consecutive_losing_trades` (needs retained ordered per-trade outcomes).
That is the refusal semantics the change specified, working.

## What is proven, and what is not

Proven:

- The scorecard above, from a pinned-window gate run on commit `ae6a1fd`.
- Gross edge is positive (+0.664709) and net is negative (−0.377343) on holdout.
- `cost_to_gross_pnl_ratio` 1.567682 against a 0.5 threshold.
- `minimum_holdout_days` passes at 900 days; seven input-continuity checks fail.

Not proven, and deliberately not claimed:

- **That this generalises.** One route, one window, one configuration. The
  cost-to-gross ratio has not been measured this way on any other route.
- **That reducing costs by 1.57× would make the configuration profitable.** The
  ratio is measured, not the counterfactual; r344/r345 showed cost changes move
  the decision stream, so a cheaper fee is not a scalar rescaling.
- That 6.232 trades/week is close enough to matter. It fails, and r367 showed
  frequency and profitability trade off against each other on this family.
- That the drawdown figures are meaningful at this scale. Max total drawdown
  7.3e−05 on an account that lost 0.377 is a number I do not yet understand and
  am not interpreting.

## Named next step

Measure `cost_to_gross_pnl_ratio` on the other five routes through the same
gate, pinned. If the ratio is above 1.0 everywhere, the fleet has real edge that
is uniformly too small to pay its friction, and the target becomes cost per
trade rather than any Portfolio-layer knob — a conclusion 184 iterations have
circled without being able to measure.
