# Round 380 — DATA-ISSUE: independent verification finds the measurement path **moved 4% on an identical window**. The audit trail **reconciles exactly**.

Classification: **DATA-ISSUE** — a measurement defect found by verification.
Two containers (the budget), both cleaned up. OPS transaction
`portfolio-measurement-integrity` moved `VERIFY` → **`FIX` round 1**, Codex
worker launched with the findings file.

## The finding: same window, same trades, different PnL

`bybit.perpetual_future.BTC.USDT` @900, deployed configuration, **no gate flag**
— the invocation task 3.4 requires to be unchanged:

| field | previous build | commit `59e2489` | delta |
|---|---|---|---|
| `candle_count` | 259,198 | 259,198 | identical |
| `one_target.trades` | **847** | **847** | identical |
| `one_target.realized_pnl` | **−3.769332905847924** | **−3.618298890847919** | **+0.151034 (+4.0%)** |
| `funding_paid` | 0.017000 | 0.016000 | −0.001 |

**The decision stream is unchanged — 847 closed trades in both — so the shift is
at the fill or cost level, not in what the Portfolio decided.** Funding accounts
for 0.001 of a 0.151 move; **roughly 99% is unexplained**.

I checked the obvious candidate and eliminated it: `execute_target` merely
delegates to `execute_target_with_closed_trade`
(`trading_modes.rs:1737-1743`), so swapping between them cannot be the cause.
`finance-core` is unmodified, so the cause is inside `crates/finance-research`.

Recorded as **P1**. It may turn out that the new value is the correct one and
the old was wrong — that would be a good outcome — but an unexplained 4% shift
in the path this change was required to leave alone is exactly the class of
defect the change exists to eliminate. It must be explained, not absorbed.

## What passed

- **Task 4.2, the audit trail, reconciles exactly.** `--emit-trades` produced
  **847 records** against 847 reported trades, and
  `sum(realized_pnl) = −3.618298890847919` against a reported
  `−3.618298890847919` — difference **1.8e-15**. Records carry `entry_at`,
  `exit_at`, `entry_price`, `exit_price`, `side`, `quantity`, `fees`,
  `slippage`, `funding_paid`, `realized_pnl`, `exit_reason`. This is the first
  time in the arc that a reported aggregate has been checkable against
  individual fills (audit L4, closed).
- **`cargo test --workspace`, run by me**, not by the worker: **699 passed, 0
  failed, 1 ignored, 37 suites**, no build errors. Codex's claim is now
  independently confirmed.
- `finance-core` untouched; shared guarded replay used by both paths; gate
  accepts a hold value and restricts to a 20.0% holdout; metrics `Option`-typed;
  zero-trade rows report zero PnL.

## Scope observation on walk-forward

`main.rs:689-712` applies walk-forward to the **Alpha sweep**
(`sweep::score_walk_forward_segment`), not to the Portfolio path, and rebuilds
`strategies::candidates()` per segment so stateful strategies cannot carry
observations forward — a deliberate no-leak choice, stated in a comment.

So r352's nested-holdout blocker is closed **for the Alpha layer**. The
Portfolio layer's out-of-sample story remains the gate's **single trailing
holdout**, which is still nested across `--days` values. That is not a spec
violation — the requirement names no layer — but the Portfolio's OOS is
improved by the gate becoming Portfolio-faithful, **not** by walk-forward, and
the record should not blur the two.

## Two P2 findings, carried into the same findings file

- Walk-forward **segment 1 has empty training** and is dominated by warm-up
  (r267), so it is not comparable with later segments.
- The exclusion rule is **hardcoded to `taker_imbalance` by name**, so a future
  strategy with a missing input would be silently degraded again.

Neither blocks release on its own.

## What is proven, and what is not

Proven:

- The five-row comparison table above, both runs at `candle_count` 259,198.
- 847 emitted trade records reconciling to 1.8e-15 against the reported figure.
- 699 tests passing across 37 suites, in a run I executed.
- Walk-forward is applied to the Alpha sweep and rebuilds candidates per segment.

Not proven, and deliberately not claimed:

- **Any cause for the 4% shift.** One candidate eliminated; no mechanism
  identified. I am not guessing at one in the findings file either — the request
  to Codex is "reproduce the old value, or name the code path and justify the
  new one".
- **That the new value is wrong.** It may be the correction. What is established
  is that it is *different* and *unexplained*, against a task that required it
  to be unchanged.
- That the cross-path equality criterion has been executed. Still outstanding —
  walk-forward turned out not to provide a holdout-restricted Portfolio figure,
  so that route to testing it is closed and another is needed.
- That the P2 list is complete.

## Named next step

Verify the FIX when the worker reports: re-run the exact `bybit BTC` command and
require `−3.769332905847924`, or read the written justification and its pinned
regression test. Then FINAL_VERIFY. Nothing is pushed.
