# Round 284 — The call graph is confirmed, so the discrepancy is real: no code path I can find permits what the ledgers record

Classification: **NEEDS-MORE-RESEARCH**. Local code inspection plus read-only
production state. **Zero containers.**

## Round 283's named check, done

Round 283 said the most likely place it was wrong was assuming the
`paper-backtest-*` ledgers are written by the Portfolio path, and that verifying this
was the next step **before any further mechanism claims**.

**The assumption is correct** (`trading_api.rs:831-866`):

```rust
let mut realtime = context.simulated_child(&format!("paper-{rule_id}"), "weighted-strategies",
                                            DecisionPolicyKind::WeightedEnsemble);
let mut backtest = context.simulated_child_with_workflow(&format!("paper-backtest-{rule_id}"),
                    "weighted-strategies", WorkflowKind::Backtest, DataOriginKind::Market,
                    DecisionPolicyKind::WeightedEnsemble);
```

Both lanes carry the same `PortfolioReplaySemantics` — same
`minimum_holding_decisions`, same `decision_policy`, same `risk_policy`. So the
backtest ledgers are written by the Portfolio machinery with the deployed policy, and
Round 283's call graph was right.

## The persisted construction state, read directly

`runtime_state.portfolio_construction` on three routes:

| route | current_target | reason | `waiting_after_protective_exit` | `decisions_since_target_change` | `minimum_holding_decisions` |
|---|---|---|---|---|---|
| binance BTC | long | `multi_timeframe_gate_passed` | **false** | 250 | 36 |
| bybit BTC | short | `multi_timeframe_gate_passed` | **false** | 238 | 36 |
| exness XAU | short | `multi_timeframe_gate_passed` | **false** | 39 | 36 |

The flag is transient as expected — a gate pass that changes position resets it — and
the deployed `minimum_holding_decisions` is confirmed as **36** in persisted state,
not just in configuration.

## The discrepancy, now robust

Tracing `construct()` exhaustively: the gate-pass branch always yields Long or Short
(`side != Hold`), the non-passing branch clones the current target, and
`decision.exit` is never true on this path (Round 283). **So `current_target` can only
become Flat via `force_flat()` or `observe_execution(ProtectiveExit)` — and both set
`waiting_after_protective_exit = true`, which forces the next entry to wait 36
decisions.**

Round 282 measured re-entry after `target_flat` at **100% ≤0.2h on all three routes**
(n = 66/18/186, median 0.08h ≈ one 5m candle).

**Every candidate path has now been excluded, the call graph is verified, and the two
still disagree.** I am not proposing a fourth mechanism.

## What this is, stated plainly

Either I am misreading a state transition in `PortfolioConstructionState`, or the
ledger's `close_reason` labelling does not correspond to the code path I have traced.
**Both are worth someone checking with the ability to instrument the running system**
— a single log line carrying `current_target.reason` and
`waiting_after_protective_exit` at each `apply_target` flat close would settle it
immediately, and Round 265 already recorded that the equivalent observability does not
exist for hold reasons.

Filing this as **P3, investigation only, not applied** — it explains no PnL and blocks
no target; it is a discrepancy between documented mechanism and recorded behaviour.

## An honest note on this thread

Rounds 279-284 have spent six rounds on the `target_flat` mechanism. The chain of
*measurements* is solid and reusable — hold ∝ σ², occupancy from flat time, the
guard's exact floor, the pairwise close-reason table, the absence of `target_changed`.
The chain of *mechanism claims* has produced three refutations of my own work
(Rounds 279, 282, 283). The measurements are the durable part; I should have stopped
proposing mechanisms after the second refutation and filed the discrepancy then.

## What is proven, and what is not

Proven:

- `paper-*` and `paper-backtest-*` contexts are both Portfolio lanes with identical
  replay semantics (`trading_api.rs:831-866`).
- Persisted `portfolio_construction` state on three routes, including
  `minimum_holding_decisions = 36` and `waiting_after_protective_exit = false`.
- Every path to a Flat `current_target` sets `waiting_after_protective_exit = true`.
- That is inconsistent with 100% immediate re-entry after `target_flat`.

Not proven, and deliberately not claimed:

- **Which side of the discrepancy is wrong.** My reading or the labelling; I cannot
  distinguish them from static inspection plus snapshots.
- Any fourth mechanism for `target_flat`.
- That this affects trading outcomes. It affects my *description* of them; the PnL and
  frequency measurements of Rounds 272-278 do not depend on which mechanism produces
  the close.
- Anything about routes beyond the three read here.
