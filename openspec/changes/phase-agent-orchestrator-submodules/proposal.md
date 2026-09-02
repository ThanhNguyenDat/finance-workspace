## Why

`.agents/orchestrator/src/phase_agent_orchestrator/` is four flat files
totaling ~1600 lines (`ops_runtime.py` alone is 671), each mixing CLI
argument parsing, domain logic (locks, state transitions, candidate
validation), and I/O in one file. The operator has asked for this split
into proper submodules before the two changes currently building on top of
it (`phase-agent-account-registry-config`,
`phase-agent-python-spawn-layer`) add more code to the same flat files —
restructuring now, once, is cheaper than restructuring after those land
too.

## What Changes

- Split the package into layered submodules with no behavior change
  (pure refactor; every existing bash/pytest test must pass unmodified in
  intent, only internal import paths change):
  - `io.py`: `CLIError`, `die`, `utc_now`, `utc_after`, `json_text`,
    `read_json`, `atomic_write_text`, `atomic_write_json`, `run_cli`.
  - `locks/pid_liveness.py`: `pid_is_alive`, `lock_pid_is_live`.
  - `locks/directory_lock.py`: `PidDirectoryLock`.
  - `locks/change_lock.py`: `lock_change`, `unlock_change`,
    `lock_repositories`, `assert_repo_lock`, `release_repo_locks`,
    `owner_is_live`, `phase_attempt_lease_is_dead`, `lock_anchor_pid`,
    `canonical_repo`, `repo_lock_dir`, `repo_locks_dir`.
  - `locks/account_lock.py`: `lock_account`, `unlock_account`,
    `account_lock_dir`, `account_locks_dir`.
  - `accounts/registry.py`: `normalize_account`, `account_environment_name`,
    `resolve_account_dir`.
  - `state/ops_transaction.py`: change-directory/path helpers, `read_state`,
    `write_state`, `init_change`, `set_phase`, `set_terminal`, `cleanup`,
    `enter_fix`, `route`, `record_attempt`, `trace_origin`,
    `active_changes`, `complete`, `assert_active_owner`, `_ReturnStatus`.
  - `state/candidates.py`: everything `phase_agent_state.py` currently
    does except its `main()`/`mutate_command` dispatcher — candidate
    validation, default state, schema validation, legacy import,
    load/save/`with_state`.
  - `state/quant_research.py`: everything `quant_research_state.py`
    currently does except its `main()`.
  - `cli/ops_runtime.py`, `cli/phase_agent_state.py`,
    `cli/quant_research_state.py`: only argv parsing and dispatch to the
    modules above, each keeping its exact current subcommand set and
    stdout/exit-code contract.
- Update every `.agents/scripts/*.sh` shim's `python -m
  phase_agent_orchestrator.<module>` target to the new `cli.<module>` path.
- Update every existing pytest test's imports and `monkeypatch.setattr`
  targets to point at the new submodule that now owns each function (for
  example, a test currently doing `monkeypatch.setattr(ops,
  "change_dir", ...)` moves to patching `phase_agent_orchestrator.
  state.ops_transaction.change_dir`).

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
(none — this changes internal module organization only; every requirement
in `openspec/specs/ops-backend-routing/spec.md` and every external CLI
contract is unchanged, so `skip_specs: true` is set)

## Impact

- **Affected repository**: `finance-workspace` only.
- **Affected files**: all four existing files under
  `.agents/orchestrator/src/phase_agent_orchestrator/`, all three
  `.agents/scripts/*.sh` shims that reference a module path, and every
  existing test file under `.agents/orchestrator/tests/` (import/mock
  target updates only, not new test scenarios).
- **Sequencing**: this change should land, and its bash+pytest suites pass
  green, before `phase-agent-account-registry-config` or
  `phase-agent-python-spawn-layer` starts implementation, so both build
  directly on the new module layout instead of the flat files.
- **Trading safety**: none (pure internal reorganization of orchestration
  tooling, no behavior change).
- **Rollback**: `git revert` the restructuring commit(s); every caller's
  external contract (`.agents/scripts/*.sh` paths and arguments) is
  unchanged either way.
