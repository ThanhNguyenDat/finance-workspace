## Context

See `proposal.md` for the exact function-to-module mapping (derived
directly from the current file contents, not re-invented) and the full
current line counts (`ops_runtime.py` 671, `phase_agent_state.py` 503,
`quant_research_state.py` 245, `common.py` 173).

## Goals / Non-Goals

**Goals:**
- Each submodule has one clear responsibility (I/O primitives, PID-based
  locking, account resolution, one script's state/domain logic, one
  script's CLI dispatch) and can be read/tested in isolation.
- Zero behavior change: every bash integration test and every existing
  pytest test still passes, asserting the same scenarios, after only their
  import/mock targets are updated.
- `phase-agent-account-registry-config` and `phase-agent-python-spawn-layer`
  can build their new code directly into this layout (an `accounts/`
  package already exists for the YAML change; an `adapters/`, `classify/`,
  `detect/`, `subprocess_supervision/` set of packages is anticipated by,
  but not created by, this change).

**Non-Goals:**
- No behavior change of any kind — this is Non-Goal #1. Any bug noticed
  during the move is logged as a follow-up finding, not fixed inline,
  exactly like `phase-agent-python-orchestrator`'s own migration discipline.
- No dependency changes (no new packages).
- No change to any `.agents/scripts/*.sh` shim's arguments or external
  behavior, only the Python module path it invokes internally.

## Decisions

**1. Layer boundaries: `io` (leaf, no internal imports) → `locks`/
`accounts` (import only `io`) → `state` (imports `io`, `locks`, `accounts`)
→ `cli` (imports `state`, dispatch only, no business logic of its own).**
This ordering matches actual current dependencies (e.g. `lock_change`
already calls `atomic_write_json` and `lock_anchor_pid`; `record_attempt`
already calls `atomic_write_json`) and prevents a future circular import
between, say, `state/ops_transaction.py` and `locks/change_lock.py` by
fixing which one is allowed to import the other (state can import locks;
locks must never import state).
*Alternative considered*: one `core/` package with everything except CLI
— rejected, too close to the current one-big-file problem, just renamed.

**2. `locks/change_lock.py` keeps `owner_is_live` and
`phase_attempt_lease_is_dead` even though `locks/account_lock.py` also
calls `owner_is_live`.**
`owner_is_live` is change/repo-lock-shaped logic (its second parameter is
literally a change path) that the account lock reuses as-is
(`phase-agent-multi-account-routing` design.md Decision 3 already
established this reuse, not a new one). Moving it to a third
"shared lock logic" file for two call sites would add a module for
theoretical symmetry with no current second implementation to justify it
(Simplicity First).

**3. Every submodule directory gets an `__init__.py` that re-exports
nothing beyond making the directory a package** (no `from .x import *`
convenience re-exports). Callers import the specific submodule they need
(`from phase_agent_orchestrator.locks import change_lock`), keeping
`grep`/"find references" meaningful and avoiding the classic
`__init__.py`-as-junk-drawer problem.

**4. Test updates are mechanical, not a rewrite: the same test function
body, same fixture construction, same assertions — only the
`monkeypatch.setattr(ops, "x", ...)`-style targets change to name the new
submodule that now owns `x`.** A test whose intent doesn't map cleanly onto
exactly one new submodule (none currently do, per proposal.md's mapping)
would be a signal the split boundary is wrong, not that the test should
change shape.

## Risks / Trade-offs

- **[Risk]** A mechanical split can still introduce an import-order bug
  (a genuine circular import, or a module-level side effect that ran once
  in the old single file now running in a different order).
  → **Mitigation**: Decision 1's layering rule makes a cycle structurally
  impossible if followed; `uv run --project .agents/orchestrator python -c
  "import phase_agent_orchestrator.cli.ops_runtime"` (and the other two CLI
  modules) must succeed cleanly as a smoke check before any test run.
- **[Trade-off]** More files/directories to navigate for a codebase this
  size (~1600 lines) is a real cost, not free — accepted because two more
  changes are about to add meaningfully more code into this package
  (`phase-agent-python-spawn-layer` alone is a larger surface than what
  exists today), where the flat-file cost would only grow.

## Migration Plan

1. Create the new package directories and move `io.py`'s content first
   (leaf, no dependents to break yet in a half-done state).
2. Move `locks/` and `accounts/` content, updating their internal imports
   to `io`.
3. Move `state/` content, updating imports to `locks`/`accounts`/`io`.
4. Move `cli/` content last, updating the three `.agents/scripts/*.sh`
   shims' `python -m` targets in the same commit as each CLI module's move
   so the shim and its target never disagree in a committed state.
5. Update every test file's imports/mock targets to match, then run the
   full bash + pytest suite.
6. **Rollback**: `git revert` the whole restructuring commit sequence;
   external shim paths/arguments never changed, so no caller is affected
   either direction.
