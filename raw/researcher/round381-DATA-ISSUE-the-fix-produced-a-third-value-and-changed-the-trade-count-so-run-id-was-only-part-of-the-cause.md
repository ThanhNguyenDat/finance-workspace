# Round 381 — DATA-ISSUE: the fix produced a **third** value and changed the trade count, so `run_id` was only part of the cause.

Classification: **DATA-ISSUE**. Two containers (the budget), both cleaned up.
OPS transaction: FIX round 1 completed, verified, **not resolved** → FIX round 2
launched with new findings.

## FIX round 1 and its root-cause claim

Codex `gpt-5.6-terra` / high, attempt 1, exit 0, `result_class: success`, commit
`c07951a`. It reported a plausible root cause: the unified replay had changed
the `DecisionScope.run_id` from `"portfolio-construction-comparison"` to
`"portfolio-measurement-integrity"`, and the risk layer's scope evidently feeds
something deterministic, so the string change moved the risk decisions and hence
the fills. It restored the original and added a
`pre_unification_measurement_replay` regression test.

Codex also reported it **could not** run the 900-day check because its
environment had no reachable endpoint. That check is mine, and it is the whole
point.

## The check: still failing, and differently

Exact command from round 1's findings, re-run against `c07951a`:

| build | `candle_count` | `one_target.trades` | `one_target.realized_pnl` |
|---|---|---|---|
| pre-unification (required) | 259,198 | **847** | **−3.769332905847924** |
| `59e2489` | 259,198 | 847 | −3.618298890847919 |
| **`c07951a`** | 259,198 | **846** | **−3.713368400847926** |

The `run_id` restoration moved PnL **toward** the required value but did not
reach it — and it **introduced a trade-count difference that did not exist
before**. `59e2489` matched 847 trades exactly; `c07951a` produces 846.

So `run_id` was at most part of the cause, and the fix has now perturbed the
**decision stream** as well as the fills. Three builds, three results.

The important methodological point for the findings file: Codex's new regression
test **passes** while the real 900-day run **fails**. A synthetic fixture that
does not exercise whatever differs is necessary but not sufficient, and round
2's findings ask explicitly why the fixture missed it rather than asking for
another fixture.

## Resolved and verified

- **P2-1** — walk-forward segment 1 now carries `"comparable": false`.
- **P2-2** — required inputs are strategy-declared in `crates/finance-strategy`
  (`StrategyInput` enum, `required_inputs()` with an **empty default**, wrappers
  forwarding to the inner strategy) and the sweep exclusion no longer matches on
  names. **Verified additive**: no `evaluate()` body changed, so no production
  strategy behaviour is affected — checked, because `finance-strategy` is a
  crate the live workers use.

## A provisional research observation, flagged as provisional

The `exness XAU` @900 gate run on `c07951a` gives, on its 179.7-day holdout:

| | trades | PnL |
|---|---|---|
| Portfolio-faithful | 161 | −0.39768 |
| `legacy` control | 169 | −0.28338 |
| **advantage** | | **−0.11430 (−40.3%)** |

Full-window on the previous build, that route's advantage was **+68.7%** (r372).
On holdout it is **negative**. If that survives, it is a sign flip between
full-window and holdout on the same route, and it would make `exness XAU` the
second route where the guard hurts out of sample.

**I am not recording it as a finding.** It comes from a build whose measurement
path is demonstrably unstable across three commits, which is exactly the defect
under repair. It is written down so it is re-checked once P1 closes, not so it
can be cited.

## What is proven, and what is not

Proven:

- The three-build comparison table, all at `candle_count` 259,198.
- FIX round 1's terminal evidence: exit 0, Terra/high, `result_class: success`.
- The `finance-strategy` diff is additive: an enum, a defaulted trait method,
  and wrapper forwarding; no strategy evaluation logic changed.
- P2-1 and P2-2 are addressed.

Not proven, and deliberately not claimed:

- **Any cause for the residual difference.** Round 2's findings list places to
  compare — ledger observation order, which ledger's `performance()`/`equity()`
  reaches `evaluate_historical`, and `max_retained_trades` — and says plainly
  that this is not a diagnosis.
- That `run_id` was irrelevant. It moved the number; it did not close the gap.
- **Anything about the `exness XAU` holdout advantage.** Provisional, from an
  unverified build.
- That the cross-path equality criterion can be attempted yet. It should not be:
  the measurement path is unstable across builds, so a comparison against it
  would measure the instability.

## Named next step

Verify FIX round 2 the same way: re-run the exact command and require 847 and
−3.769332905847924. `OPS_MAX_FIX_ROUNDS` is 3, so one further round remains
after this one before the workflow is mechanically blocked. Nothing is pushed;
`main` is 2 commits ahead of `origin/main` locally.
