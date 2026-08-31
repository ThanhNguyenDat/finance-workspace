# Round 379 — NO-CHANGE: tasks 2–5 verified in code, **two P2 findings**, and the cross-path equality check is still outstanding.

Classification: **NO-CHANGE** — no research finding, no configuration verdict.
**Zero containers.** OPS transaction `portfolio-measurement-integrity` remains in
`VERIFY`.

## Verified this round, by reading the committed code

- **Task 3, walk-forward.** `split.rs:50` builds
  `training = klines[..start]`, `evaluation = klines[start..end]` with
  `start = index*total/n`, so segments **partition the input exactly once**,
  are disjoint, and training is strictly earlier. The test at `split.rs:191`
  asserts contiguity, the disjoint sum, anchoring, and the no-look-ahead
  boundary `training.last().close_time <= evaluation[0].open_time`.
- **Task 2, metrics.** `ExecutionFootprint` now carries `profit_factor`,
  `win_rate`, `sharpe_ratio`, `sortino_ratio`, `max_drawdown`,
  `longest_negative_day_streak`, `sqn`, `decision_rate` and
  `cost_to_gross_pnl_ratio` — all as `Option`, i.e. **absent rather than zero**,
  which is what the requirement asked for. Implementations are imported from the
  gate module rather than duplicated.
- **Task 4, trade export.** `--emit-trades <PathBuf>` at `main.rs:276`, used at
  `main.rs:668`.
- **Task 5, refusal.** `sweep.rs:32` adds `excluded: Option<String>`;
  `sweep.rs:74` `exclusion_reason` returns a reason when no candle has both
  `volume > 0` and `taker_buy_volume > 0`; `sweep.rs:46` makes an excluded row
  fail `survives_selection`; `sweep.rs:60` reports `realized_pnl = 0` when
  `trade_count == 0`. That is exactly the round 374 defect, closed.
- **Task 1.3 equality test** exists at `daily_profit_gate.rs:1433-1441`: the
  gate report's `portfolio_faithful` must equal a directly invoked
  `replay_guarded_portfolio_targets` on the same decisions. Valid, and it proves
  the gate report is produced by the shared function.

## Two P2 findings

Neither is P0/P1, so neither blocks release on its own; recorded so they are not
lost.

**P2-1 — walk-forward segment 1 is evaluated with no warm-up at all.**
`split.rs` gives segment 1 `training = klines[..0]`, and the test asserts
`segments[0].training.is_empty()`. The requirement is satisfied literally —
there are no earlier bars — but round 267 established that the Portfolio does
not decide until all eight required intervals are synchronised, so segment 1's
numbers are dominated by warm-up and are **not comparable to later segments**.
Expected behaviour: report segment 1 as non-comparable, or require a minimum
training prefix before the first scored segment.

**P2-2 — the exclusion rule is hardcoded to one strategy name.**
`exclusion_reason` returns `None` unless
`strategy.name().contains("taker_imbalance")`. The spec requirement is general:
*"a strategy whose required input is unavailable for the route SHALL be reported
as excluded"*. Round 375's audit found the taker family is the only **currently**
affected one, so today's output is correct — but a new strategy, or an existing
one on a route with a different missing column, would be **silently degraded
again**, which is the exact failure this requirement exists to prevent.

## The equality criterion is still outstanding

The existing test compares the gate against the shared function on the **same
decisions**. It does not establish that the gate and `portfolio_measurement`
feed that function the **same inputs** — which is where the two paths could
still diverge. Round 378's own attempt was mis-specified (full-window baseline
against a holdout-restricted gate) and remains unexecuted against a valid basis.

The strongest evidence so far is indirect and, I think, real: the gate's
faithful-versus-control sign matches the independently known full-window sign on
**both** routes — positive on `bybit BTC`, negative on `binance XAU` (r375,
r372). If the gate were feeding the shared function the wrong inputs, agreeing
on two routes whose signs are opposite would be a coincidence. That is an
argument, not the pinned test.

## Test suite

I launched `cargo test --workspace` myself under a 25-minute hard timeout, per
`.agents/rules/coding-and-verification.md`. At the close of this round it is
**still running with no failures observed**. It is **not** complete, so I make no
claim about it — Codex's report that it passed remains the worker's claim, and
`verification_mode=independent` means it does not count until my own run
finishes.

## What is proven, and what is not

Proven:

- The code locations and behaviours listed under "Verified this round".
- Segment 1 of a walk-forward has empty training, asserted by the
  implementation's own test.
- `exclusion_reason` is gated on the strategy name containing
  `taker_imbalance`.

Not proven, and deliberately not claimed:

- **That the test suite passes.** Incomplete at round close; no failures seen is
  not the same as passing.
- **That the gate and `one_target` produce identical numbers.** The criterion
  the change was said to stand or fall on has still not been executed against a
  valid basis.
- That tasks 2 and 4 behave correctly at runtime. Verified by reading
  declarations and call sites, not by running them and checking output.
- That the two P2 findings are the only ones. Tasks 2 and 4 had a lighter
  inspection than 3 and 5.

## Named next step

Finish the test run and read its result; execute the equality criterion against
a holdout-restricted basis; exercise `--emit-trades` once and reconcile the
emitted records against the reported aggregate, which is task 4.2's own
acceptance check and the only way to confirm the audit trail is real. Only then
FINAL_VERIFY.
