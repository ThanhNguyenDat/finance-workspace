**Sequencing**: this change should land before `phase-agent-account-registry-config`
and `phase-agent-python-spawn-layer` start implementation (design.md
Goals). All tasks are in the `finance-workspace` repository only.

## 1. Leaf modules

- [x] 1.1 Create `phase_agent_orchestrator/io.py` with `CLIError`, `die`,
  `utc_now`, `utc_after`, `json_text`, `read_json`, `atomic_write_text`,
  `atomic_write_json`, `run_cli`, moved verbatim from `common.py`. Verify:
  `uv run --project .agents/orchestrator python -c "from
  phase_agent_orchestrator import io"` succeeds.
- [x] 1.2 Create `phase_agent_orchestrator/locks/pid_liveness.py`
  (`pid_is_alive`, `lock_pid_is_live`) and
  `phase_agent_orchestrator/locks/directory_lock.py` (`PidDirectoryLock`),
  moved verbatim, importing from `io` only.
- [x] 1.3 Create `phase_agent_orchestrator/accounts/registry.py`
  (`normalize_account`, `account_environment_name`, `resolve_account_dir`),
  moved verbatim, importing from `io` only.
- [x] 1.4 Delete `common.py` once nothing imports it. Verify: `grep -rn
  "from .common\|from phase_agent_orchestrator.common\|import common" .agents/orchestrator/src`
  returns no matches.

## 2. Lock modules

- [x] 2.1 Create `phase_agent_orchestrator/locks/change_lock.py`
  (`lock_change`, `unlock_change`, `lock_repositories`,
  `assert_repo_lock`, `release_repo_locks`, `owner_is_live`,
  `phase_attempt_lease_is_dead`, `lock_anchor_pid`, `canonical_repo`,
  `repo_lock_dir`, `repo_locks_dir`), moved verbatim from `ops_runtime.py`,
  importing from `io`, `locks.pid_liveness`, `accounts.registry` as
  needed.
- [x] 2.2 Create `phase_agent_orchestrator/locks/account_lock.py`
  (`lock_account`, `unlock_account`, `account_lock_dir`,
  `account_locks_dir`), moved verbatim, importing `locks.change_lock.
  owner_is_live` (design.md Decision 2 — reused, not duplicated).
  Verify: `uv run --project .agents/orchestrator pytest
  .agents/orchestrator/tests/test_state_helpers.py -q` passes after Task 5
  updates its imports.

## 3. State modules

- [x] 3.1 Create `phase_agent_orchestrator/state/ops_transaction.py` with
  everything in `ops_runtime.py` not moved to Tasks 1-2: directory/path
  helpers, `read_state`, `write_state`, `init_change`, `set_phase`,
  `set_terminal`, `cleanup`, `enter_fix`, `route`, `record_attempt`,
  `trace_origin`, `active_changes`, `complete`, `assert_active_owner`,
  `_ReturnStatus`.
- [x] 3.2 Create `phase_agent_orchestrator/state/candidates.py` with
  everything in `phase_agent_state.py` except `main`/`mutate_command`/
  `usage`.
- [x] 3.3 Create `phase_agent_orchestrator/state/quant_research.py` with
  everything in `quant_research_state.py` except `main`/`usage`.

## 4. CLI modules and shims

- [x] 4.1 Create `phase_agent_orchestrator/cli/ops_runtime.py`
  (`main`, `usage`, argv dispatch only, delegating to
  `state.ops_transaction`/`locks.change_lock`/`locks.account_lock`).
  Update `.agents/scripts/ops-runtime.sh`'s `python -m` target to
  `phase_agent_orchestrator.cli.ops_runtime` in the same commit. Verify:
  `.agents/scripts/tests/test_ops_orchestration.sh` passes.
- [x] 4.2 Create `phase_agent_orchestrator/cli/phase_agent_state.py` the
  same way, update `.agents/scripts/phase-agent-state.sh`'s target. Verify:
  `test_phase_agent_state.sh` and `test_phase_agent_routing.sh` pass.
- [x] 4.3 Create `phase_agent_orchestrator/cli/quant_research_state.py`
  the same way, update `.agents/scripts/quant-research-state.sh`'s target.
  Verify: `test_quant_research_state.sh` and `test_quant_backend_routing.sh`
  pass.
- [x] 4.4 Delete `ops_runtime.py`, `phase_agent_state.py`,
  `quant_research_state.py` once nothing imports them by their old path.

## 5. Test updates

- [x] 5.1 Update every test in `.agents/orchestrator/tests/` to import and
  `monkeypatch.setattr` the new submodule owning each patched name (design.md
  Decision 4), with no change to test bodies/assertions otherwise. Verify:
  `uv run --project .agents/orchestrator pytest -q` passes with the same
  test count as before this change (21 tests as of
  `phase-agent-multi-account-routing`).

## 6. Full-system verification

- [x] 6.1 Verify: every bash test under `.agents/scripts/tests/` passes
  unmodified.
- [ ] 6.2 Run one live end-to-end smoke check:
  `./.agents/scripts/run-phase-agent-command.sh quant-research`, and verify
  it completes with the same `Quant iteration <n> completed with <provider>`
  success line.
  Blocked for this session because the explicit task instruction prohibits
  launching another model process; this command invokes the selected model
  adapter.
- [x] 6.3 Verify `./.agents/scripts/sync-agent-links.sh --check` still
  passes (no shared rule/skill content references the old flat file paths).
