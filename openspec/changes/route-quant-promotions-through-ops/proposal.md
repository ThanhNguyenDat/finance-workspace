## Why

Quant research currently promotes engineering work through `raw/handoff_agent.md`, duplicating task and lifecycle truth already owned by OpenSpec and OPS. Promotion needs one stable change identity that traces defensible research evidence through implementation, verification, delivery, and archive without creating an OPS transaction for every research iteration.

## What Changes

- Classify each bounded quant iteration as `REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, `NEEDS-MORE-RESEARCH`, or `PROMOTE`; only `PROMOTE` enters engineering orchestration.
- Require promoted candidates to satisfy an explicit evidence, scope, acceptance, risk, trading-safety, and rollback gate before creating or reusing OpenSpec and entering the existing OPS lifecycle.
- Use the same stable change name for `openspec/changes/<change>/` and `.ops/changes/<change>/` and attach concise immutable quant-origin metadata to the OPS transaction.
- Demote `raw/handoff_agent.md` to a legacy, non-authoritative human index while preserving its history; OpenSpec tasks and OPS runtime state become the engineering and execution truth.
- Update shared rules/skills, command contracts, bounded tests, CI, and documentation to remove the duplicate handoff queue semantics.
- Preserve Codex Luna/high IMPLEMENT, Terra/high FIX, Sol/high eligible fallback, immutable backend selection, atomic FIX, maximum FIX rounds, quant availability toggles, and existing release/archive behavior.

## Capabilities

### New Capabilities

- `quant-promotion-traceability`: Promotion gate, stable identity, concise research-origin metadata, and end-to-end trace requirements for actionable quant changes.

### Modified Capabilities

- `quant-research-control`: Replace handoff-queue promotion with explicit outcome classification and OpenSpec + OPS orchestration while retaining bounded research and fallback behavior.

## Impact

- Affected repository: `finance-workspace` only.
- Affected components: quant and OPS command contracts, OPS runtime helper/tests, quant contract tests, shared delivery/research guidance, README, legacy handoff banner, CI, and OpenSpec.
- No strategy, broker, order, risk, market-data, database, runtime service, or production deployment change.
- Existing handoff history remains intact. Rollback is a normal Git revert; transient OPS origin metadata is ignored with the rest of runtime state and requires no migration.
