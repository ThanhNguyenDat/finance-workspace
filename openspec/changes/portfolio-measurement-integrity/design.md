## Context

`finance-research` has two Portfolio replay paths that were allowed to diverge.

| | gate path | Portfolio-faithful path |
|---|---|---|
| location | `daily_profit_gate.rs:376-412` | `portfolio_measurement.rs:184-208` |
| construction guard | **absent** | `construction.construct(decision)` |
| risk layer | **absent** | `evaluate_historical` → `execution_target` |
| execution | `ledger.on_kline(...)` | `ledger.execute_target(...)` |
| scorecard metrics | full | `ledgers`/`trades`/`realized_pnl`/`funding_paid` |
| holdout restriction | yes | **no** |

Each path holds exactly what the other lacks. The gate can score a holdout but
models the wrong system; the measurement path models the right system but has no
holdout and few metrics. Every promotion attempt in 170 iterations has died in
that gap.

The replay is bit-for-bit deterministic (`raw/researcher/round351-*.md`), which
makes an exact-equivalence regression test possible and is the basis of the
correctness gate below.

## Goals / Non-Goals

Goals:

- One replay path, used by every report, that applies the construction guard and
  risk layer.
- Out-of-sample segments that are genuinely disjoint.
- The metrics the standing joint objective names, on that one path.
- Refusal to publish an unsupportable score.

Non-Goals:

- Changing any live trading semantics, risk policy, or execution rule.
- Changing strategy logic, other than declining to run a strategy whose required
  input is absent.
- Making any configuration profitable. This change makes measurement correct; it
  does not predict, and must not be judged on, the sign of the result.

## Decisions

### 1. The gate replays through the measurement path

Replace the `ledger.on_kline` loop in `daily_profit_gate.rs` with the
`construct` → `evaluate_historical` → `execution_target` → `execute_target`
sequence, and delete `conflicts_with = "daily_profit_gate"` from
`main.rs:264`.

**Correctness gate — the acceptance criterion this change stands or falls on:**
with the deployed default hold, a gate run and a `one_target` run over the same
window MUST produce **identical** trade counts and realized PnL. The replay is
deterministic, so any difference is a defect, not noise. This test is what
proves the two paths were unified rather than merely made similar.

The existing `legacy_selected_rule` stream is retained and reported alongside,
so the gap the gate used to report remains visible rather than disappearing
silently.

**Verification limitation:** the end-to-end equality form of this criterion
cannot be executed from the current report surface. The gate emits holdout-only
Portfolio-faithful figures, but `one_target` is not emitted for that same
holdout; a short-window substitute starts Portfolio cold whereas the gate reaches
the holdout warm. The shared replay function, its unit-level equality test, and
the containment invariants are therefore the accepted evidence. No additional
report is introduced solely to make this comparison executable.

### 2. Walk-forward is anchored and disjoint

Add `--walk-forward-segments N`. The window splits into N contiguous segments;
segment *i* is evaluated after fitting on all bars strictly before it. Segments
are **disjoint by construction** and reported individually, never pooled into a
single figure.

The existing trailing-holdout mode is kept and remains the default, so no past
result silently changes meaning.

No-look-ahead is preserved by reusing the existing closed-bar filter
(`klines.rs:246`) and the `close_time`-sorted replay order, with a test
asserting that no segment's evaluation observes a bar at or after its own end.

### 3. Metrics move to the measurement path

Extend `ExecutionFootprint` with profit factor, win rate, Sharpe, Sortino, max
drawdown, longest negative-day streak, SQN, decision rate, and cost-to-gross
ratio. Reuse the gate's existing implementations rather than writing second
versions — two implementations of a metric is how the two paths diverged in the
first place.

Daily bucketing keeps the operational timezone (`Asia/Ho_Chi_Minh`), matching
`daily_profit_gate.rs:340,402`.

### 4. Per-trade records are serializable

`SimulatedTrade` (`trading_modes.rs:1548-1562`) gains `Serialize` and is emitted
under `--emit-trades <path>`. Off by default: the record is large, and the
default output contract does not change.

This is what makes an independent fill-level audit possible; without it the
`ExecutionFootprint` aggregates cannot be checked against market data at all.

### 5. Unsupportable rows are refused, not degraded

- A strategy whose required input column is absent for the route is reported
  with an explicit `excluded` reason and **no score**. It is not run with a
  defaulted input.
- A row with `trades == 0` reports `realized_pnl = 0.0` and carries any funding
  accrual in a separate, explicitly named field. The current behaviour — a
  positive-looking `realized_pnl` on a strategy that never traded — is what
  produced a false result in round 373.
- A wrapper whose threshold cannot bind, because the inner strategy's entry
  condition saturates the filtered metric, is reported once rather than as
  several identical entries.

## Risks / Trade-offs

- **Live-path regression is the principal risk.** Mitigation: the change adds a
  call site and additive serialization; it does not modify
  `PortfolioConstructionState`, `PortfolioRiskLayer`, or `trading_modes`
  execution semantics. Acceptance requires the existing `finance-core` suite to
  pass unchanged.
- **Past gate verdicts become non-comparable.** They were already describing a
  different configuration; this makes that explicit. Affected rounds are named
  in the tasks so the research record can be annotated rather than quietly
  reinterpreted.
- **Walk-forward segments are individually smaller**, so per-segment samples are
  thinner. This is a real cost and is the reason the trailing holdout is kept
  rather than replaced.
- **Runtime increases** where the gate now performs risk evaluation per
  decision. Bounded by the existing 2-container / 2 CPU / 4 GB research budget;
  if a run exceeds it, reduce the window rather than the correctness.

## Migration Plan

Additive and flag-gated. Existing invocations keep their current behaviour
except that gate figures now describe the Portfolio-faithful stream — which is
the correction being made. No data migration, no deployment.

## Open Questions

- Whether `bybit` and `exness` ingestion *can* supply `taker_base_vol`. Round
  374 measured what is stored (0.00% on four routes), not what the venues
  expose. Until that is known, the correct action is exclusion, not backfill —
  which is what this change specifies.
