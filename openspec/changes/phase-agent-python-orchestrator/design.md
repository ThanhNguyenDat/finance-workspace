## Context

See `proposal.md - Why` for motivation. Relevant current-state facts this
design must account for:

- `ops-runtime.sh`, `phase-agent-state.sh`, and `quant-research-state.sh` are
  referenced by **literal file path**, not by an installed command name, from
  `run-phase-agent.sh` (`RUNTIME="$SCRIPT_DIR/ops-runtime.sh"`,
  `STATE="${PHASE_AGENT_STATE_HELPER:-$SCRIPT_DIR/phase-agent-state.sh}"`) and
  from `run-phase-agent-command.sh` (`QUANT_STATE="${QUANT_RESEARCH_STATE_HELPER:-$SCRIPT_DIR/quant-research-state.sh}"`).
  Those callers are a non-goal (proposal.md) and stay unmodified, so the three
  paths must keep existing, keep being directly executable, and keep the same
  stdout/exit-code contract.
- This session added lock-staleness detection to `ops-runtime.sh`
  (`lock_owner_is_live`, `phase_attempt_lease_is_dead`, `lock_anchor_pid`)
  anchored on `$CLAUDE_PID`/`$CODEX_PID`, verified today against `origin/main`
  in `finance-live-action`. This is now part of the behavioral contract the
  Python port must reproduce exactly, including the bash-specific edge case
  it relies on: `kill -0` fails (and is therefore treated as "not confirmed
  alive") both when the pid is dead **and** when it exists but is owned by a
  different user (EPERM). Python's `os.kill(pid, 0)` must be handled the same
  way — catching only `ProcessLookupError` is not enough; `PermissionError`
  must also fall through to "not confirmed alive" to match today's behavior.
- Every state mutation currently goes through `atomic_write_state()`
  (`mktemp` in the same directory, write, `mv --`) so a reader never observes
  a partially written `state.json`/`owner.json`. This is a correctness
  property, not an implementation detail, and must survive the port.
- The three scripts are invoked fresh, once per call, from bash — there is no
  persistent daemon today. Every "child process" in the current system is a
  real `claude`/`codex` OS subprocess spawned by the *bash* layer
  (`run-claude-phase.sh`/`run-codex-phase.sh`), which this change does not
  touch.

## Goals / Non-Goals

**Goals:**
- Byte-identical CLI contract at the three existing paths (same subcommands,
  arguments, stdout JSON shape, exit codes, stderr `<prefix>: <message>`
  format) so no caller changes.
- Byte-identical behavior for every rule already covered by
  `openspec/specs/ops-backend-routing/spec.md` and by this session's
  lock-staleness logic.
- `uv`-managed, reproducible Python dependency environment.
- A test suite that can exercise the staleness/liveness logic without
  spawning real subprocesses for every case (today's bash tests use `( : ) &`
  and `sleep` backgrounding to fabricate live/dead pids — workable, but slow
  and awkward to extend).

**Non-Goals:**
- No persistent daemon / long-running orchestrator process. Each CLI
  invocation stays a fresh, short-lived Python process, exactly mirroring how
  bash invokes these scripts today. A daemon would need its own
  process-lifecycle management (start/stop/crash-recovery/its own lock) —
  exactly the class of problem this change is trying to make easier to
  reason about, not add a second instance of. See Open Questions.
- No change to `run-claude-phase.sh`, `run-codex-phase.sh`,
  `run-phase-agent.sh`, `run-phase-agent-command.sh`, or any script that
  spawns the `claude`/`codex` CLI (proposal.md Non-Goals).
- No change to any `openspec/specs/*` requirement.

## Decisions

**1. New code lives at `.agents/orchestrator/`, with the package under
`.agents/orchestrator/src/`.**
Grouped under `.agents/` alongside `.agents/scripts/`, `.agents/rules/`,
`.agents/skills/`, matching this repo's existing convention for shared
tooling rather than introducing a top-level `src/` that implies this is the
whole repository's source. `uv init --package` at
`.agents/orchestrator/` gives the standard `pyproject.toml` + `src/<pkg>/`
layout; `<pkg>` is `phase_agent_orchestrator`.
*Alternative considered*: a repository-root `src/` — rejected because
`finance-workspace` is an orchestration/specs repo (per its own
`CLAUDE.md`), not an application with one canonical source root, and a
root-level `src/` would misleadingly suggest this is the primary deliverable.

**2. The three existing file paths become thin bash shims that exec into
`uv run`; the real implementation is three Python modules.**
`.agents/scripts/ops-runtime.sh`, `phase-agent-state.sh`, and
`quant-research-state.sh` keep their names, paths, and executable bit, but
each becomes a two-line shim:
```bash
#!/usr/bin/env bash
exec uv run --project "$(dirname -- "${BASH_SOURCE[0]}")/../orchestrator" \
  python -m phase_agent_orchestrator.ops_runtime "$@"
```
(module name varies per script). `uv run --project` resolves/creates the
`.venv` under `.agents/orchestrator/` lazily and transparently; no separate
"activate" step is needed by any caller.
*Alternative considered*: rename the callers to invoke a `uv run`-based
command directly — rejected, since it would require editing every caller
listed as a non-goal in proposal.md, multiplying the review surface for no
behavioral benefit.
*Alternative considered*: a single merged Python CLI with subcommands
(`orchestrator ops-runtime lock ...`) instead of three modules — rejected for
this change to keep the three call sites' arguments completely unchanged
(`ops-runtime.sh lock <change> <session-id>` stays exactly that); revisit
only if a future change also touches the callers.

**3. Dependencies: `uv` + `pyproject.toml` + `uv.lock`, standard library
`json`, no ORM/heavy framework.**
`jq`'s role is replaced by Python's built-in `json` module plus small
dataclasses for `state.json`/`owner.json` shapes — no schema library needed
given the existing validation is a handful of field/type/enum checks.
*Alternative considered*: `pydantic` for schema validation — rejected as an
unnecessary dependency for this size of schema; revisit only if the schema
grows materially.

**4. Atomicity: `tempfile.NamedTemporaryFile(dir=..., delete=False)` +
`os.replace()`.**
Directly mirrors `mktemp "${file}.tmp.XXXXXX")" ... | mv --`: the temp file
is created in the same directory as the target (so the final `os.replace` is
on the same filesystem, staying atomic on POSIX) and is never observed
half-written by a concurrent reader.

**5. Liveness check: `os.kill(pid, 0)`, treating both `ProcessLookupError`
and `PermissionError` as "not confirmed alive," and only a clean call (no
exception) as alive.** See Context above for why this must match bash
`kill -0`'s behavior exactly, including the EPERM case.

**6. Threads are used only where the existing bash is already sequential
I/O that is safe to parallelize, not as a general concurrency pattern.**
The one concrete case in the current three scripts is `lock_repositories`
checking multiple repository-lock candidates' staleness one at a time; the
Python port MAY use a small `ThreadPoolExecutor` to check candidates
concurrently (each check is a `kill -0` plus a couple of small file reads —
I/O-bound, GIL-releasing, safe to parallelize; the *acquisition* itself
still happens one repository at a time and still calls `release_repo_locks`
on any failure, exactly as today). No other part of this change needs
threads: the CLI is invoked once per call and exits, so there is no
persistent pool of concurrent tasks to manage as in a daemon.

## Risks / Trade-offs

- **[Risk]** A subtle behavior mismatch between the bash original and the
  Python port (e.g., the EPERM-liveness nuance in Decision 5, or JSON
  key-ordering assumptions some caller might rely on) ships silently, since
  the two implementations are never run side by side in production.
  → **Mitigation**: FINAL_VERIFY for this change must run the existing bash
  integration test suites (`test_ops_orchestration.sh`,
  `test_phase_agent_state.sh`, `test_quant_research_state.sh`,
  `test_phase_agent_routing.sh`, `test_quant_backend_routing.sh`,
  `test_quant_promotion_trace.sh`, `test_hermetic_agent_contracts.sh`)
  unmodified against the new Python-backed shims, not just new pytest tests.
- **[Risk]** `uv run --project` adds per-invocation startup latency (dependency
  resolution check, interpreter start) to a layer called on every phase
  transition and every lock operation.
  → **Mitigation**: acceptable in absolute terms — these calls already sit
  next to CLI phase attempts that run for minutes to an hour; a startup cost
  well under a second is noise by comparison. If it ever matters,
  `uv run`'s resolution is a cached no-op once `uv.lock` is unchanged.
- **[Risk]** Introducing a Python/`uv` toolchain requirement to a workspace
  that has so far only assumed bash/`jq`/`git`/`gh` raises the bootstrap bar
  for any environment that runs `run-phase-agent-command.sh`
  (interactive sessions, and any unattended host running the quant-research
  cron loop).
  → **Mitigation**: `tasks.md` includes a bootstrap/preflight check
  (`command -v uv`) with a clear error message, matching the existing
  `for command in jq timeout git; do command -v ... done` pattern already in
  `run-phase-agent-command.sh`.
- **[Trade-off]** Keeping three separate modules (Decision 2) instead of a
  unified CLI means some duplication (argument parsing boilerplate) across
  `ops_runtime.py`, `phase_agent_state.py`, `quant_research_state.py`.
  Accepted deliberately to keep this change's blast radius to exactly the
  three files proposal.md scopes in.

## Migration Plan

1. Scaffold `.agents/orchestrator/` (`uv init --package`), add `pyproject.toml`
   dependencies, commit `uv.lock`.
2. Port `phase-agent-state.sh` first (smallest, no lock semantics) as the
   Python module + shim; get its existing bash test suite green.
3. Port `quant-research-state.sh` the same way.
4. Port `ops-runtime.sh` last (largest, carries this session's lock-staleness
   logic — hold it until the pattern is proven on the two smaller scripts).
5. Run the full existing bash integration test suite plus the new pytest
   suite; only then replace the three original bash files with the shims in
   the same commit sequence that adds each corresponding Python module.
6. **Rollback**: `git revert` the shim-cutover commit(s) for any one script
   independently — restores the original bash file at that exact path with
   no caller changes needed, because the calling contract never changed.

## Open Questions

- Whether to later evolve this into a persistent daemon (unlocking real
  internal concurrency and removing the per-call `uv run` startup cost) is
  deliberately deferred — nothing in this change forecloses it, since the
  three CLI contracts stay stable either way, but it is a materially bigger
  change (daemon lifecycle, its own supervision lock, IPC) that deserves its
  own proposal once the one-shot Python port has run in production for a
  while.
