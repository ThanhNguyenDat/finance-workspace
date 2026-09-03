## Why

The current phase-agent entry points expose provider-specific commands and
individual phases, but they do not present one resumable lifecycle for a
change. This makes it easy to reopen terminals or restart work after quota
rotation, losing the relationship between planning, brainstorming,
implementation, verification, fixes and archival. The workspace needs one
durable orchestration flow that accepts the existing shell, Claude, Codex and
quant-research entry points while preserving the current change context.

The current implementation also places a workspace-global quant lease in
front of every research invocation. That prevents independent prompts from
running concurrently and makes a simple lock removal unsafe because iteration
allocation, provider health and shared research paths are not session-scoped.

## What Changes

- Add a general lifecycle coordinator for
  `PLAN → BRAINSTORM → IMPLEMENT → VERIFY → ARCHIVE`.
- Replace workspace-global directory locking with a local SQLite WAL
  coordinator that stores session state, short transactions, admission slots,
  resource leases, fencing tokens and ordered events. Provider calls never run
  inside a database transaction and there is no global mutex around a prompt.
- Add the bounded remediation loop `VERIFY → FIX → VERIFY`, with a configured
  maximum per verification round and explicit escalation when the limit is
  reached.
- Allow multiple independent prompts to run concurrently in bounded,
  session-isolated workers. Allocate an isolated Git worktree for mutable
  scopes, while serializing or queueing prompts that target the same change or
  worktree.
- Run every model-owned phase through its provider SDK in streaming mode and
  expose a session event/log channel that the operator can follow from
  `.e2e.sh` or an attached console.
- Keep background sessions interactive: when Claude/Codex asks for approval,
  input or a tool decision, surface the question to the operator and route the
  answer back to the live SDK session.
- Provide monitor views for phase, provider/model/account, elapsed time,
  current action, quota/failover, tests and terminal outcome; allow detach and
  reattach without losing the running session or its log position.
- Persist lifecycle phase, session/change identity, round, context pointers,
  selected agent candidate, quota/failover history and resumable checkpoints
  in the coordinator so a later invocation continues from the last safe
  boundary without reusing another session's state.
- Route every model-owned phase through the existing phase-agent resolver;
  Claude/Codex selection, model, effort and account remain phase-specific.
- Rotate to the next eligible account/provider after confirmed quota
  exhaustion without restarting completed work or creating a concurrent
  attempt. Preserve the same OpenSpec change, repository lock, round and
  context when continuing.
- Provide one operator-facing entry point that accepts a prompt or change
  reference and can be resumed by `.e2e.sh`, Claude CLI, Codex CLI, or the
  quant-research loop without opening a new orchestration context.
- Make `ARCHIVE` a guarded terminal operation that runs only after successful
  verification and required release/final-verification evidence.
- Record machine-readable lifecycle events and concise handoff evidence under
  the session/change scope; move terminal history to the archive namespace.
- Apply bounded admission/backpressure so concurrency cannot exhaust local
  resources or create untracked provider processes.
- Persist per-session structured events and displayable logs with redaction;
  concurrent sessions must never mix output or operator input.

## Capabilities

### New Capabilities

- `phase-agent-lifecycle-orchestration`: A resumable, provider-neutral
  lifecycle with explicit planning, brainstorming, implementation,
  verification, bounded fix loops and archival transitions.

### Modified Capabilities

- `openspec/specs/ops-backend-routing/spec.md`: Extend phase routing and
  continuation requirements to cover the explicit BRAINSTORM phase, lifecycle
  checkpoints, shared entry points and guarded ARCHIVE transition.

## Impact

- **Affected repository:** `finance-workspace` only; runtime application code
  remains in its owning Finance repositories.
- **Affected components:** the Python orchestrator under
  `tools/orchestrator/`, SQLite coordinator state under the
  gitignored `.ops/runtime/` namespace, phase-agent routing, quant-research
  launcher, worktree/admission management, handoff/archive records and bounded
  contract tests.
- **External behavior:** Existing provider commands remain usable, but they
  attach to or resume a shared lifecycle session instead of silently creating
  unrelated work. New lifecycle state and transition evidence become part of
  the operator-facing contract.
- **Safety:** No trading execution behavior changes directly. The orchestration
  must retain exclusive leases, prevent duplicate provider processes, preserve
  read-only VERIFY semantics, and never start a replacement while an old
  process or ambiguous side effect remains unresolved. Parallel prompts must
  use isolated session state and worktrees, or be rejected/queued when their
  scopes overlap.
- Interactive provider questions and shell/tool output must use a bounded,
  authenticated session channel and must never expose credentials, tokens or
  unredacted secret-bearing output.
- **Dependencies:** Reuse the existing Python/`uv` orchestrator, provider SDK
  adapters, account registry and OPS transaction state. SQLite is the only new
  coordinator dependency and is accessed by bounded invocations; no persistent
  daemon or external queue service is required.
- **Rollback:** Disable the new lifecycle entry point and resume the existing
  phase-agent commands from the previous OPS state format; preserve all
  already-recorded attempt and archive evidence.
