All tasks are in the `finance-workspace` repository only.

## 1. YAML registry

- [x] 1.1 Add `pyyaml` via `uv add --project .agents/orchestrator pyyaml`,
  and verify `uv run --project .agents/orchestrator python -c "import yaml"`
  succeeds.
- [x] 1.2 Replace `account_environment_name`/`resolve_account_dir` in
  `common.py` to read `.agents/orchestrator/accounts.yaml` (or
  `$PHASE_AGENT_ACCOUNTS_FILE` when set, design.md Decision 1), keeping the
  exact same function signatures so `ops_runtime.py` and
  `phase_agent_state.py` need no changes. Verify: unit tests assert distinct
  messages for (a) missing file, (b) provider key absent, (c) account key
  absent, (d) account directory does not exist on disk.
- [x] 1.3 Update the existing account pytest tests
  (`test_account_registry_rejects_unset_and_missing_directories` and every
  other test currently using `monkeypatch.setenv("PHASE_AGENT_..._DIR", ...)`)
  to write a temp YAML file and set `PHASE_AGENT_ACCOUNTS_FILE` instead.
  Verify: the full existing account-related pytest suite passes unmodified
  in intent (same scenarios, new fixture mechanism).
- [x] 1.4 Update `.agents/scripts/tests/test_multi_account_routing.sh` to
  write the accounts as a YAML fixture instead of exporting
  `PHASE_AGENT_CLAUDE_ACCOUNT_*_DIR`. Verify: the test still passes
  end-to-end (lock exclusivity + real failover cycle, unchanged from
  `phase-agent-multi-account-routing`).
- [x] 1.5 Add a real `.agents/orchestrator/accounts.yaml.example` (not the
  operator's real one, which stays untracked/gitignored) documenting the
  shape from design.md Decision 2, and reference it from
  `.agents/orchestrator/README.md`.

## 2. Full-system verification

- [x] 2.1 Verify: the full bash and pytest suites from
  `phase-agent-multi-account-routing` Task 3.1 still pass.
- [ ] 2.2 Run one live end-to-end smoke check with the operator's real
  `accounts.yaml` (not the example), confirming resolution still exports
  the correct `CLAUDE_CONFIG_DIR`/`CODEX_HOME` for a real candidate.
