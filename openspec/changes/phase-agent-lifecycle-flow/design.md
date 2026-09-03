## Context

The current Python orchestrator has useful provider adapters, account locks,
change/repository locks and atomic JSON state, but the quant launcher places a
single workspace-global lease before iteration allocation. Removing that lease
alone would create duplicate iteration directories, shared provider-health
races and unsafe writes to common research artifacts.

The replacement must support several terminal prompts at once while keeping
the safety boundary: one mutable worktree/change at a time, one in-flight
attempt per provider account, bounded local resource usage, and session-local
quota continuation.

## Goals and non-goals

**Goals:**

- Make each prompt a durable, resumable session with a unique identity.
- Allow independent sessions to run concurrently up to a configured capacity.
- Protect shared mutable scopes with leases instead of a workspace-global
  mutex.
- Make iteration allocation, lifecycle transitions, quota rotation and event
  ordering atomic and recoverable.
- Keep provider SDK calls outside storage transactions and preserve the current
  phase-specific model/account policy.
- Support attach/detach monitoring and coordinator-owned operator input.

**Non-goals:**

- No trading, broker, market-data or application-runtime changes.
- No Redis, Celery, Temporal or new deployed service.
- No concurrent mutation of one Git worktree or one OpenSpec change.
- No automatic rollback of partial work after quota exhaustion.
- No use of provider output as lifecycle state.

## Decisions

### 1. SQLite is the local coordinator

Store coordinator state in `.ops/runtime/coordinator/coordinator.db`, which is
gitignored and created on demand. Open the database with WAL mode, foreign-key
checks and a busy timeout. Every mutation uses a short transaction; no model
call, test, approval wait or shell command is held inside a transaction.

The initial schema is:

```text
sessions(id, change, phase, round, quant_iteration, status, worktree, context_json,
         checkpoint, selected_provider, selected_account, lease_owner,
         lease_expires_at, fencing_token, version, created_at, updated_at)
attempts(id, session_id, phase, round, attempt_no, provider, account,
         model, effort, continuation, status, result_class, evidence_path,
         started_at, completed_at)
resource_leases(resource_type, resource_key, session_id, owner_pid,
                owner_start_time, lease_expires_at, fencing_token)
admission_slots(slot_id, session_id, lease_expires_at, fencing_token)
events(session_id, sequence, phase, attempt_id, event_type, safe_payload,
       created_at)
operator_questions(session_id, question_id, status, safe_payload,
                   response, expires_at)
```

The schema also has `coordinator_counters` for atomic quant iteration
allocation and `schema_migrations` for applied schema versions.

Unique keys on `(resource_type, resource_key)`, `(session_id, sequence)` and
`(session_id, phase, attempt_no)` prevent duplicate ownership, event ordering
and attempt records. A monotonic `version` plus `fencing_token` prevents an
old worker from writing after its lease has been replaced.

### 2. Admission is bounded but not globally serialized

The coordinator reserves one of `ORCHESTRATOR_MAX_SESSIONS` slots in a short
SQLite transaction. If all slots are occupied, the session is persisted as
`QUEUED` with a bounded reason; no provider process starts. Slot allocation is
the only coordinator-wide coordination and it lasts only for the database
transaction.

Independent sessions can therefore run concurrently. Admission is evaluated
before a worker starts, and restart reconstructs live slots from the persisted
lease expiry and owner identity.

### 3. Resource scope determines serialization

Resource keys are acquired in a stable order:

```text
admission slot -> change scope -> worktree scope -> provider/account scope
```

The coordinator never waits while holding a previously acquired resource. A
conflicting session is queued or rejected with the owner/session summary.

- `change:<name>` protects one mutable OpenSpec lifecycle.
- `worktree:<canonical-path>` protects one Git worktree.
- `account:<provider>/<account>` protects one provider login/configuration.
- Different changes, worktrees and accounts can run together.

Mutating sessions receive dedicated Git worktrees. Read-only verification may
use an explicitly disjoint repository scope, but it still has its own session
and phase lease. Quant research writes session-scoped run artifacts first;
promotion/index updates are a separate serialized publish operation.

### 4. Session-scoped state replaces the global quant lease

Creating a quant session and allocating its iteration happen in one SQLite
transaction. The transaction returns a unique `(session_id, iteration)` and
the run directory is `.ops/runtime/phase-agents/quant-runs/<session-id>/`.
The old `.quant-research-lock` is removed. The quant state file remains a
short-lived compatibility/migration surface, not the owner of an active
provider session.

Provider health is a future-selection hint. The session persists its selected
candidate and continuation state; a quota result rotates only that session.
Other sessions keep their candidate, context and leases unchanged.

### 5. Leases use fencing and fail closed

Lease acquisition uses `BEGIN IMMEDIATE`, a unique resource key and an
owner-start identity in the same transaction. Workers heartbeat while active.
Every write includes the session's fencing token; a stale token is rejected.

Recovery may reclaim a lease only after its expiry and a failed owner liveness
check. A missing owner record, permission error, PID reuse or ambiguous process
state is `INDETERMINATE`, not stale. The coordinator reports it and does not
delete it automatically. This removes the current mkdir-then-write-pid race
and the unsafe `rmtree` stale recovery path.

### 6. Events and operator input are session-scoped

Adapters append ordered events to `events` and a redacted JSONL view. The
monitor follows a session and sequence offset. Provider approval/input is
represented as one pending `operator_questions` row tied to the session,
attempt and question ID. Only the owning coordinator worker may answer it;
wrong-session or stale-sequence responses are rejected.

Provider SDK calls remain authoritative. Logs are evidence and display data,
never a control channel. Detached sessions keep their bounded worker lease and
can be reattached until the phase timeout or operator-input deadline.

### 7. Crash, quota and restart behavior

On normal completion, the worker records the terminal attempt, releases the
account/worktree/change leases and advances the lifecycle in a transaction.
On confirmed quota exhaustion, it records the attempt, releases only the
account/attempt lease, and resumes the same session and phase with the next
candidate. On timeout, crash or ambiguous side effect, it records
`INTERRUPTED`/`BLOCKED` and requires bounded recovery inspection before a
replacement starts.

On coordinator restart, sessions with live leases remain `RUNNING`; expired
leases become recoverable only after process identity checks. Queued sessions
are admitted in creation order subject to scope conflicts and capacity.

### 8. Compatibility and cutover

The canonical implementation remains under
`tools/orchestrator/`. Existing shell entry points, where retained,
are thin `uv` wrappers only. The coordinator adds `submit`, `resume`, `status`,
`attach`, `answer`, `cancel` and `recover` operations; existing commands map to
these operations without creating provider-specific lifecycle state.

## Risks and mitigations

- **SQLite contention:** keep transactions short, enable WAL/busy timeout and
  bound retries; never hold a transaction across an SDK call.
- **Stale worker writes:** require fencing tokens on every session/resource
  update and reject old tokens.
- **Worktree leaks:** persist allocation metadata and reclaim only after lease
  expiry plus liveness evidence; surface indeterminate cases.
- **Shared research publication conflicts:** write session-local artifacts and
  serialize only the final publish/index operation.
- **Capacity overload:** persist queued state and expose the reason; never fork
  an untracked provider process.
- **Interactive session leaks:** enforce phase, worker and operator-input
  deadlines with SDK interrupt/hard-kill cleanup.

## Migration plan

1. Add the SQLite schema, connection policy, migrations and coordinator CLI
   without changing existing provider adapters.
2. Add session state, transition validation, fencing leases and bounded
   admission; keep the old JSON state readable for rollback.
3. Move quant iteration allocation and run namespaces to session scope; remove
   the global quant lease after fake-provider concurrency tests pass.
4. Add worktree scope isolation, account lease integration and session-local
   quota continuation.
5. Add event persistence, monitor attach/detach and operator input routing.
6. Cut over `.e2e`, quant and manual provider commands through the coordinator.
7. Run bounded unit, shell, fake-provider, concurrency and interactive tests,
   then perform a read-only end-to-end smoke test.
8. Roll back by restoring the old entrypoint mapping; preserve SQLite evidence
   as historical runtime state and do not delete it automatically.

## Open questions

- The default `ORCHESTRATOR_MAX_SESSIONS` value can be selected from measured
  local CPU/memory limits during implementation; the bound must remain
  explicit and persisted in coordinator status.
- The initial worktree naming convention can be finalized as long as its path,
  source revision and owner session are persisted before a provider starts.
