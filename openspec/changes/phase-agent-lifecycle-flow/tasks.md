## 1. Coordinator storage and lifecycle state

- [x] 1.1 Add the SQLite coordinator database under gitignored `.ops/runtime/` with WAL, foreign keys, bounded busy timeout and schema versioning; verify concurrent short transactions do not corrupt the database.
- [x] 1.2 Add session, attempt, event, question and migration records with unique constraints for session/phase/attempt and event sequence; verify malformed and interrupted writes are rejected without partial state.
- [x] 1.3 Add atomic session creation/resume and unique quant iteration allocation; verify two concurrent prompts receive different session/iteration identities and run namespaces.
- [x] 1.4 Implement lifecycle transition validation for `PLAN → BRAINSTORM → IMPLEMENT → VERIFY → ARCHIVE` and `VERIFY → FIX → VERIFY`; verify stale versions and illegal transitions leave state unchanged.
- [x] 1.5 Implement stable context manifests and read-only coordinator status; verify resumed sessions receive the same request, OpenSpec, repository, findings and attempt references.

## 2. Admission, scopes and leases

- [x] 2.1 Implement bounded admission slots with persisted `QUEUED`/`RUNNING` state and configurable capacity; verify capacity exhaustion launches no provider process.
- [x] 2.2 Replace directory PID ownership with transactional resource leases carrying owner process identity, expiry and fencing tokens; verify stale tokens cannot write and ambiguous leases fail closed.
- [x] 2.3 Add change/worktree scope admission and isolated Git worktree allocation for mutable sessions; verify disjoint worktrees run concurrently and overlapping scopes serialize or queue.
- [x] 2.4 Integrate provider/account leases without holding database transactions across SDK calls; verify `personal-02` and `personal` can run concurrently while the same account remains exclusive.
- [x] 2.5 Add coordinator restart/recovery with bounded heartbeat and liveness checks; verify live sessions are preserved, expired sessions are recoverable only with unambiguous owner evidence, and indeterminate sessions remain blocked.

## 3. Coordinator entry points

- [x] 3.1 Implement `submit`, `resume`, `status`, `recover`, `cancel`, `attach` and `answer` operations and a common session contract; verify a new prompt starts at PLAN and repeated invocation resumes idempotently.
- [ ] 3.2 Route `.e2e.sh`, Claude and Codex terminal commands through the coordinator while preserving compatibility arguments/output; verify they attach to the same session/change without provider-specific lifecycle state.
- [x] 3.3 Move quant launcher iteration allocation and run artifacts to session namespaces; remove the workspace-global `.quant-research-lock` only after concurrency tests pass.
- [ ] 3.4 Route `/loop 20m /quant-research` through session resume/checkpoints; verify repeated bounded iterations do not duplicate work or reopen unrelated lifecycle phases.

## 4. Model phases and continuation

- [x] 4.1 Add the BRAINSTORM adapter and explicit empty/approved checkpoint; verify it is bounded, read-only for runtime code and passes plan context to IMPLEMENT.
- [x] 4.2 Route PLAN, BRAINSTORM, IMPLEMENT, VERIFY and FIX through phase-specific SDK candidates; verify model, effort, account, prompt context and attempt history remain phase-specific.
- [ ] 4.3 Persist VERIFY findings and guarded FIX transitions with the current round only; verify P0/P1 findings require a fresh verifier and never bypass ARCHIVE gates.
- [x] 4.4 Add session-local quota/account/provider continuation with old-attempt exit confirmation and worktree fingerprints; verify one session rotates without changing another session's candidate or lease.
- [ ] 4.5 Add bounded process interruption and terminal reopen recovery; verify completed phases are not repeated and ambiguous side effects block automatic replacement.
- [ ] 4.6 Add guarded ARCHIVE transition and historical evidence move; verify missing attestation, failed gates, uncleared leases or blocked status prevent archive.

## 5. Events, monitor and operator control

- [ ] 5.1 Emit ordered per-session SDK/tool/shell/result events and redacted human-readable views; verify event sequence, phase/attempt correlation and cross-session isolation.
- [x] 5.2 Add attach/detach/follow from an event offset; verify a detached bounded session continues and reattach replays only its own events.
- [ ] 5.3 Add coordinator-owned approval/input forwarding with question IDs and expiry; verify wrong-session, stale-question and read-only viewer responses cannot reach the provider.
- [ ] 5.4 Add bounded monitor output for phase, model, account, elapsed time, quota/failover, tests and terminal state; verify credentials and secret-bearing output are redacted before persistence.

## 6. Contract and regression verification

- [x] 6.1 Add bounded unit tests for schema migration, iteration allocation, transitions, optimistic versions, fencing and lease recovery; verify the focused Python suite passes.
- [ ] 6.2 Add fake-provider tests for quota exhaustion, account rotation, partial worktree continuation, interruption, duplicate invocation and session-local state.
- [ ] 6.3 Add bounded concurrency tests for independent prompts, capacity backpressure, same-worktree protection, two Claude accounts, coordinator restart and no duplicate provider process.
- [ ] 6.4 Add bounded interactive tests for event ordering, attach offsets, operator responses, timeout, redaction and per-session channel isolation.
- [ ] 6.5 Run the existing Python and shell contract suites with hard timeouts and verify no legacy routing regression.

## 7. Documentation and delivery

- [x] 7.1 Update applicable orchestration rules/skills with session leases, worktree scopes, SQLite recovery, quota continuation and archive gates; verify `uv run --project tools/orchestrator sync-agent-links --check`.
- [ ] 7.2 Run OpenSpec validation, Python/shell suites, format/lint and workflow syntax checks with hard timeouts.
- [ ] 7.3 Run one bounded read-only lifecycle smoke test with fake providers and inspect session, attempts, events, leases and archive evidence.
- [ ] 7.4 Obtain fresh configured FINAL_VERIFY, commit the implementation and push/track exact-SHA CI evidence only after all local gates pass.
