# Remaining backlog after the 2026-08-13 review pass

Consolidated for Codex. Everything else opened across `raw/system-review-strategy-optimization.md`,
`raw/multi-timeframe-interval-gap.md`, `raw/portfolio-rule-trade-count-imbalance.md`,
`raw/portfolio-strategy-attribution.md`, `raw/todo.md`, and `raw/refactor.md`
has already shipped and was re-verified against the current `main` branch of
both repos on 2026-08-13 (commit history + live code read, not just doc
status):

- `refactor.md` / `todo.md` (Historical Portfolio Replay shared-driver,
  multi-rule replay Phase 2) — done, `multi_rule_replay_conflict()` guard
  removed, shared-driver split matches the spec.
- `portfolio-strategy-attribution.md` — done end-to-end
  (`contributing_strategies` field: Rust → JSON passthrough → TS
  `dominantContributor`/`groupTradesByStrategy`).
- `multi-timeframe-interval-gap.md` Symptom A (interval filter regression) —
  done, finance-mw `ef8c243`.
- `multi-timeframe-interval-gap.md` Symptom B (evidence panel empty since
  restart) — done, finance-live-action `e0ba169` ("continue portfolio
  evidence from replay", #82) — evidence and the primary clock now carry
  from the replay driver into the realtime runtime instead of starting
  empty on every restart.
- `portfolio-rule-trade-count-imbalance.md` Cause 1 (`risk-2pct` blocked by
  an unscaled risk gate) — done, finance-live-action `8d31ac1` ("scale
  Portfolio risk gates per execution rule", #83).
- `system-review-strategy-optimization.md` P1 core (static decision
  weights) — done, finance-live-action `40fdfa3` ("derive portfolio weights
  from alpha performance") — `reweight_from_alpha_performance` is wired
  into both the realtime path (`trading_api.rs:1530`) and historical replay
  (`trading_api.rs:2085`).
- `system-review-strategy-optimization.md` P3 gap-recovery global reset
  (Suspect B) — appears already fixed as a side effect of the above: the
  gap-recovery path (`trading_api.rs:1349-1359`) now calls
  `inner.portfolio_evidence.clear_interval(&interval)` (scoped to the one
  affected interval) and no longer resets `inner.evaluation_count` at all —
  confirmed by reading the current function body, no matching commit
  message found so this was likely folded into `e0ba169` or a neighboring
  commit rather than filed separately.
- `system-review-strategy-optimization.md` P4 (cross-scope comparison view)
  — done, finance-mw `b0c49fa` ("compare strategy performance across
  scopes") — `useTradingMetricsComparison.ts` + `StrategyLayerPage.tsx`.

Two items are still genuinely open. Both are small, both are investigation
only (nothing applied).

---

## 1. `list_history_trades`/`GetTradeState` silently pick one Portfolio rule when no scope is given

**Confirmed still present, re-read live on 2026-08-13** (touches
`/home/lap17204/Desktop/finance/finance-live-action`, and the finance-mw
call site is informational context only):

```rust
// crates/finance-api/src/grpc.rs:384-406, list_history_trades
let context = if request.scope_id.is_none() && request.run_id.is_none() {
    self.state.runtime.portfolio_context()
        .unwrap_or(self.state.runtime.context())
} else {
    self.state.runtime.resolve_context(request.scope_id.as_deref(), request.run_id.as_deref())
        .expect("validated history context must resolve")
};
```

```rust
// crates/finance-api/src/trading_api.rs:1041-1047
pub(crate) fn portfolio_context(&self) -> Option<&ExecutionContextConfig> {
    self.contexts.iter().find(|context| {
        context.execution == ExecutionKind::Simulated
            && context.workflow == WorkflowKind::Realtime
            && context.decision_policy == DecisionPolicyKind::WeightedEnsemble
    })
}
```

With multiple Portfolio rules configured (`fixed-pct`, `risk-2pct`,
`compounding-10pct` today), `portfolio_context()` returns the **first**
match in `self.contexts`' insertion order — always `fixed-pct`, since
`configured_portfolio_rules()` pushes it first
(`crates/finance-api/src/deployment_rules.rs:31`). Any caller that hits
`list_history_trades` (or the equally scope-blind no-arg `get_trade_state`,
`grpc.rs:375-381`, called from finance-mw's `GetTradeState` gateway,
`internal/interfaces/http/trading_gateway.go:206-216`) without an explicit
`scope_id`/`run_id` silently gets `fixed-pct`'s data with no error — which
could mask `risk-2pct`/`compounding-10pct`'s real trade history rather than
those rules genuinely having fewer trades. Flagged as a real risk, not
confirmed as currently causing a visible bug — finance-mw's `LedgerScopeFilter`
now auto-selects a scope quickly on page load (this session's earlier fix),
which narrows but doesn't eliminate the window where a caller could omit
scope/run.

This is the same gap `raw/todo.md`'s "Also still open from Phase 1's
investigation" section already named and left unresolved.

**Fix direction** (not applied — investigation only): either (a) require an
explicit `scope_id`/`run_id` for these two RPCs and return a clear error
when both are omitted and more than one Portfolio rule is configured
(forces every caller to be scope-explicit), or (b) deprecate both endpoints
in favor of the already scope-generic `GetTradingMetrics`/
`ListHistoryTrades`-with-filters paths once every caller has migrated —
`raw/todo.md` already raised this exact fork and didn't resolve it either;
picking (a) vs (b) is a design call for whoever implements this.

### What "done" looks like

- Either scope-blind calls to `list_history_trades`/`get_trade_state` return
  an explicit error/require a scope when N>1 Portfolio rules are configured,
  or both endpoints are deprecated and every caller (finance-mw's
  `trading_gateway.go:206-216`) is migrated off them.
- Regression test: with 2+ configured Portfolio rules, a scope-omitted
  `list_history_trades` call either errors clearly or is removed as a code
  path — not silently defaulting to whichever rule happens to be first.

---

## 2. Offline strategy-research workflows are manual-only, not scheduled

**Confirmed still present, re-read live on 2026-08-13** (touches
`/home/lap17204/Desktop/finance/finance-live-action`):

```bash
$ grep -n "schedule:\|workflow_dispatch" .github/workflows/portfolio-research.yaml .github/workflows/universe-research.yaml
.github/workflows/universe-research.yaml:3:  workflow_dispatch:
.github/workflows/portfolio-research.yaml:4:  workflow_dispatch:
```

Neither workflow has a `schedule:` trigger — `crates/finance-research/src/sweep.rs`'s
train/validation/holdout scoring pipeline (`SplitScore`/`StrategyScore`,
`survives_selection()`) only runs when someone manually dispatches it.

This is a secondary note from `system-review-strategy-optimization.md`'s P1,
now smaller in scope than originally framed: the *headline* P1 problem (the
live decision engine ignoring real performance) is already fixed a
different way — `reweight_from_alpha_performance` recomputes interval/
strategy weights live from each Alpha ledger's own closed-trade
`SimulatedPerformance`, not from `sweep.rs`'s offline train/validation/
holdout pipeline. `sweep.rs` and its CI workflows remain a separate,
standalone research tool (train/validation/holdout-based strategy
screening before something goes live) rather than the mechanism feeding
production weights now — so scheduling it is a "should this research tool
run periodically for visibility" question, not a blocker for anything
currently live.

**Fix direction** (not applied — investigation only, and lower priority
than item 1 above): add a `schedule:` cron trigger to
`portfolio-research.yaml`/`universe-research.yaml` if periodic (rather than
purely on-demand) strategy screening is wanted. Confirm with the user
whether this is still wanted now that production weighting no longer
depends on it — it may be fine to leave manual-only.

### What "done" looks like

- Either a `schedule:` trigger is added to both workflows with an agreed
  cadence, or this item is explicitly closed as "not needed" once confirmed
  that `sweep.rs`'s output isn't meant to feed anything live-facing.

---

## Explicitly not included here

`system-review-strategy-optimization.md`'s P5 (TVL/news/macro sentiment
data) remains deferred, per that doc's own framing ("revisit only after
P1-P4" — P1-P4 are now done, but P5 still needs its own ingestion-pipeline
design pass before it's implementable, not a direct code fix). Not
scoped into this backlog.
