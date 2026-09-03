# Phase-agent coordinator

The local phase-agent coordinator is the source of truth for concurrent
prompt admission and session identity.

- Store runtime state in `.ops/runtime/coordinator/coordinator.db`; it is
  transient and must remain ignored by Git.
- Use SQLite WAL, foreign keys, a bounded busy timeout and short transactions.
  Never hold a database transaction across an SDK call, shell command, test,
  approval wait or provider quota probe.
- Do not add a workspace-global prompt mutex. Reserve an admission slot, then
  acquire resource keys in this order: `change`, `worktree`, `account`.
  Different worktrees and provider accounts may run concurrently; overlapping
  scopes remain exclusive.
- Persist every session's context, checkpoint, attempt namespace and event
  offset. Quant runs belong under
  `.ops/runtime/phase-agents/quant-runs/<session-id>/`; iteration allocation
  must happen atomically with session creation.
- Use fencing tokens and host-qualified process start identity for writes and
  recovery. An expired lease with ambiguous liveness is `INDETERMINATE` and
  must not be deleted automatically.
- Account rotation is session-local. Confirm the old SDK process has exited,
  release its account lease, then acquire the next account; never rotate a
  different session's candidate.
- Use the Python project through `uv run --project
  tools/orchestrator ...`. Bound every non-interactive test with a
  hard timeout and leave transient evidence under `.ops/runtime/`.

Package boundaries:

- Keep process-facing parsers and `project.scripts` targets under
  `orchestrator.cli`.
- Keep reusable provider SDK, availability, and result-classification code
  under `orchestrator.providers`.
- Keep reusable lifecycle and quant orchestration runners under
  `orchestrator.runners`; they must not parse CLI arguments.
- Keep lifecycle/state services in their domain packages. The package root
  should contain only package metadata; do not add implementation modules
  there.
