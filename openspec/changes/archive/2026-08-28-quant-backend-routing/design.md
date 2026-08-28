## Context

See `proposal.md` and the `ops-backend-routing` delta spec. `ops-runtime.sh` currently creates phase/round state after a change lock, while `/ops:run` and `run-codex-phase.sh` define the orchestration/worker boundary. Quant availability already lives in a separate transient state file.

## Goals / Non-Goals

**Goals:**

- Persist backend ownership at transaction initialization and expose a read-only routing decision for IMPLEMENT/FIX.
- Keep default requests and existing callers Codex-backed.
- Make fallback selection mechanically gated and testable without a second Claude process.
- Remove smoke-test residue from the generic Codex prompt and preserve atomic FIX limits.

**Non-Goals:**

- Changing quant research strategy rules or running a real research loop.
- Allowing backend changes mid-transaction.
- Adding another scheduler, orchestration state machine, runtime service, API, migration, or deployment path.

## Decisions

1. **Extend `init` compatibly.** Keep `init <change> <session>` as the default Codex path and accept `init <change> <session> claude-fallback quant-fallback` only for explicit quant fallback. The runtime reads the quant state from the same workspace root and requires `codex_available=false`.
   - Alternative rejected: a free-form setter after init, because backend ownership could race with IMPLEMENT and be changed mid-transaction.

2. **Persist verification mode alongside backend.** The runtime derives `independent` for Codex and `claude-fallback-self-review` for fallback. Existing legacy state without these fields is treated as Codex for compatibility, but all new states persist them.
   - Alternative rejected: deriving fallback repeatedly from quant state, because later toggles must not change an active transaction.

3. **Expose a read-only `route` operation.** `ops-runtime.sh route <change> <session> <IMPLEMENT|FIX>` validates active ownership/current phase and prints the persisted route. `/ops:run` uses this result to dispatch without duplicating lifecycle rules; tests can assert behavior without invoking either real agent.
   - Alternative rejected: a second dispatch script, which would create another source of truth for phase ownership.

4. **Guard the Codex worker.** `run-codex-phase.sh` refuses a non-Codex persisted backend, then uses a generic prompt. Fallback instructions stay in `/ops:run` and the quant command, where the current Claude session can act without recursive CLI invocation.

## Risks / Trade-offs

- [Old active state lacks backend fields] → compatibility defaults to Codex while every new initialization persists explicit fields; tests cover new state.
- [A caller tries to force fallback] → require both exact `quant-fallback` context and current quant state false; reject unknown values before state creation.
- [Prompt routing is natural-language] → centralize the state decision in `route`, assert it in behavioral shell tests, and keep `/ops:run` instructions explicit.

## Migration Plan

1. Deploy the workspace-only script/command/test changes through the normal commit and CI path.
2. Existing active transactions continue as Codex-compatible legacy state; new transactions receive backend fields.
3. Rollback is a follow-up revert of the workspace commit; no runtime data migration or production rollback is required.

## Open Questions

None.
