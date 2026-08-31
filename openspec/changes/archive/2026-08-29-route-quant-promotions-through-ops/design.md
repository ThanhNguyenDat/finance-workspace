## Context

The quant command currently writes engineering work into a mutable legacy handoff while OpenSpec and OPS already own planning and execution state. Concurrent research rounds also edit that handoff frequently, making it a poor lock-free task database. Existing OPS initialization, backend routing, repository locks, FIX rounds, worker evidence, and archives remain authoritative and should be extended minimally rather than copied.

## Goals / Non-Goals

**Goals:**

- Make promotion a deliberate classification after defensible research rather than an automatic side effect of every iteration.
- Preserve a stable path from research references through planning, execution, delivery, and archives.
- Make origin metadata mechanically validated, immutable, concise, and testable.
- Remove every shared rule/skill/command dependency on legacy handoff lifecycle statuses while preserving history.

**Non-Goals:**

- Automating OpenSpec proposal writing without the native integration.
- Adding a second `/ops:run` state machine, a global trace UUID, or new backend/model behavior.
- Migrating every historical handoff entry, running research/backtests, modifying runtime repositories, or deploying production.

## Decisions

### Add one owner-checked OPS origin operation

`ops-runtime.sh trace-origin` writes `runtime/origin.json` only while the owning session is in PLAN. It accepts a positive iteration, safe instrument, and one or more existing repository-relative research paths under approved `raw/` evidence roots. It refuses overwrite. This keeps lifecycle transitions in the existing runtime while making trace creation deterministic. Embedding optional fields in `init` was rejected because it would overload backend-origin arguments and complicate all normal transactions.

### Keep classification and promotion policy in the quant command contract

The command explicitly names the five outcomes and promotion criteria. Non-PROMOTE outcomes only update research evidence. PROMOTE first creates or reuses native OpenSpec artifacts, then follows the referenced OPS command and attaches origin metadata during PLAN. A separate executable promotion state machine was rejected because it would duplicate orchestration and could bypass planning/lock gates.

### Treat raw handoff as immutable-compatible legacy index

The existing file receives a concise top banner declaring it legacy/non-authoritative; its current content remains untouched. Shared rules and skills stop asking agents to move entries among status headings. New engineering status is read from OpenSpec tasks and OPS state/archive. This avoids a risky wholesale rewrite while concurrent quant rounds preserve historical audit content.

### Update reusable guidance at the source

`quant-research-loop`, `repository-delivery`, deployment verification guidance, and any domain skill that names handoff statuses are revised to reference OpenSpec/OPS. Managed links are re-synchronized after skill changes. This is required because leaving old agent guidance would silently recreate the duplicate queue.

### Test mechanics and prose separately

Runtime tests exercise valid origin creation, immutability, ownership/phase checks, path validation, and backend preservation with temporary Git fixtures. Quant command tests assert classification, gate criteria, OpenSpec-before-OPS ordering, canonical OPS reuse, same-name paths, and forbidden handoff status semantics. CI remains bounded and offline.

## Risks / Trade-offs

- [Legacy headings can still look active to humans] → Add a prominent banner and make all active command/rule/skill contracts point to OpenSpec/OPS.
- [Concurrent research edits overlap the legacy file] → Change only the top banner and stage that hunk independently; never rewrite or discard concurrent history.
- [Broken research references weaken traceability] → Require existing repository-relative paths under an allowlisted set of raw evidence roots.
- [Promotion metadata could become another state machine] → Keep it immutable reference data only; phase/backend/transitions stay exclusively in OPS state.

## Migration Plan

1. Add the origin metadata operation and bounded fixture tests.
2. Rewrite quant command and shared guidance around classification and promotion.
3. Add a legacy banner without moving historical entries.
4. Update README, OpenSpec, and Agent Contracts; run all bounded suites and strict validation.
5. Commit/push the orchestration-only change, verify exact SHA and CI, and do not deploy production.

Rollback is a normal Git revert. Existing research evidence and legacy handoff history remain in place, and transient origin metadata requires no persistent migration.
