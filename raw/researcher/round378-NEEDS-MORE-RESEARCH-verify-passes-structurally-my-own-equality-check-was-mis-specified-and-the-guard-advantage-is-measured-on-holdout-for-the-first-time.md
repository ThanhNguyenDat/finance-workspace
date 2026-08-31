# Round 378 — NEEDS-MORE-RESEARCH: VERIFY passes structurally, **my own equality check was mis-specified**, and the guard advantage is measured **on holdout for the first time**.

Classification: **NEEDS-MORE-RESEARCH**. Two containers (the budget), both
cleaned up. OPS transaction `portfolio-measurement-integrity` moved
`IMPLEMENT` → `VERIFY`; it remains in `VERIFY`.

## IMPLEMENT completed

Codex worker, `gpt-5.6-luna` / high, attempt 1, exit 0, `result_class: success`,
local commit `59e2489` — 8 files, +916/−183. Not pushed.

## Independent verification — what passes

Per `verification_mode=independent` I verified against the code and a live run,
not against the worker's summary.

- **`finance-core` untouched.** `git show --name-only 59e2489` contains no
  `finance-core` path. The trading-safety requirement holds at the diff level
  (task 6.1). Codex's claim that `SimulatedTrade: Serialize` was already present
  is consistent with this.
- **One shared guarded replay, used by both paths.**
  `portfolio_decision_replay.rs:50` `replay_guarded_portfolio_targets` applies
  `construct` → `evaluate_historical` → `execution_target` →
  `execute_target_with_closed_trade` → `observe_execution`, and it is called by
  **both** `daily_profit_gate.rs:414` and `portfolio_measurement.rs:356` (1.1).
- **The CLI conflict is gone.** `main.rs:266-269` declares
  `portfolio_minimum_hold_decisions` with no `conflicts_with`, and both live
  runs accepted `--daily-profit-gate` together with
  `--portfolio-minimum-hold-decisions 36` (1.2). The remaining
  `conflicts_with = "daily_profit_gate"` at `main.rs:237` belongs to
  `weighted_ensemble_gate`, a different flag — checked, not assumed.
- **The control is retained and distinct.** Gate output carries both
  `portfolio_construct_evaluate_execute_target` and
  `legacy_selected_rule_on_kline_control`, with different numbers (1.4).
- **The gate is holdout-restricted**, 20.0% of the window on both routes.

## The defect in my own check

Round 377 pinned **full-window `one_target`** figures as the equality target.
The gate is **holdout-restricted by design** — that is its purpose. Comparing a
holdout figure against a full-window baseline cannot succeed and does not test
anything:

| route | gate faithful (holdout) | my pinned baseline (full window) |
|---|---|---|
| `bybit BTC` | 219 trades, −2.45576 | 847 trades, −3.76933 |

219/847 = 25.9%, on a holdout that is 20.0% of the window. The numbers are
consistent with a correct implementation; **the comparison was invalid.**

**This is the sixth mis-specified pre-registration in this arc (r327, r330,
r340, r354, r373, r378) and the first one in verification rather than
research.** The pinned values are correct measurements against the wrong basis.
The correct test is the gate's faithful figures against a **holdout-restricted**
`one_target` on the same build, which the container budget did not allow this
round.

`binance XAU` additionally returned 75,696 candles against 75,672 pinned — 24
new bars (two hours) arrived at that route's venue horizon since round 372, so
its window genuinely moved. A legitimate reason for a candle-count mismatch, and
a reminder that a pinned baseline on a growing route expires.

## The new research result: the guard advantage, on holdout

Because the gate now runs both paths, its output measures the
guard-plus-risk-layer advantage **on out-of-sample data for the first time**:

| route | holdout | faithful | `legacy` control | advantage |
|---|---|---|---|---|
| `bybit BTC` | 180.0 days | 219 trades, −2.45576 | 286 trades, −3.11011 | **+0.65435 (+21.0%)** |
| `binance XAU` | 52.6 days | 36 trades, −0.62329 | 38 trades, −0.41645 | **−0.20684 (−49.7%)** |

**Both signs reproduce out of sample**: positive on `bybit BTC` (+56.9%
full-window, r375) and negative on `binance XAU` (−31.9% full-window, r372).
The one route where the guard hurts still hurts on data never used to find it.

Magnitudes differ substantially from the full-window figures, which is expected
on a different and much shorter period and is not evidence either way.

## Verification status

No P0/P1 finding against the implementation. VERIFY is **incomplete**, not
failed: the behavioural equality criterion — the one the change was said to
stand or fall on — has **not** been executed against a valid basis. Tasks 2–5
(metrics, walk-forward, trade export, refusal semantics) are unverified.
Nothing is committed to `main` beyond the local commit, and nothing is pushed.

## What is proven, and what is not

Proven:

- The diff touches no `finance-core` file; 8 files, +916/−183, commit `59e2489`.
- One shared guarded replay function exists and both callers use it.
- The gate accepts a minimum-hold value and restricts to a 20.0% holdout.
- The gate emits both the guarded path and the legacy control, with distinct
  figures.
- The two holdout advantage measurements above.

Not proven, and deliberately not claimed:

- **That the paths produce identical numbers.** Not tested against a valid
  basis. Structural identity of the call sequence is not behavioural equality —
  the whole point of the pinned check was that the code can look right and still
  diverge.
- That tasks 2–5 are implemented correctly. Not inspected this round.
- That `cargo test --workspace` passed. That is the worker's claim; I have not
  run it, and `verification_mode=independent` means it does not count until I do.
- That the holdout advantage generalises. Two routes, one holdout each, and
  `binance XAU`'s holdout is 52.6 days against 180.

## Named next step

Complete VERIFY: run a holdout-restricted `one_target` against the gate's
faithful figures on one route to execute the equality criterion properly, run
the test suite myself, and inspect tasks 2–5. Only then FINAL_VERIFY, and only
then any push.
