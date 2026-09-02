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

## 3. FIX round — Claude VERIFY finding

- [ ] 3.1 **P1 (scope/data-loss risk, out of scope for this change).**
  Commit `9a7d7bd` added a bare `raw` line to the repo-root `.gitignore`
  (currently line 20), directly underneath the existing comment "# Do not
  ignore raw/: handoff and research history are workspace artifacts."
  Nothing in this change's proposal/design/tasks calls for touching `raw/`
  handling — this change is scoped to the account YAML registry only. A
  bare `raw` pattern (no leading `/`, no trailing `/`) matches any path
  component named `raw` anywhere in the tree, so it silently un-tracks any
  future `raw/` directory's contents (e.g. research/backtest artifacts) the
  moment one is created, with no error or warning — the exact outcome the
  adjacent comment says must not happen. No `raw/` directory exists in the
  tree today (verified via `git ls-files | grep raw`), so there is no
  immediate data loss, but the regression is live and silent for the next
  one created.
  Fix: remove the `raw` line from `.gitignore`. Only keep
  `.agents/orchestrator/accounts.yaml` and `__pycache__/` if `__pycache__/`
  is still wanted — it is unrelated to `raw/` and does not contradict the
  adjacent comment, so it may stay if useful, but the `raw` line must go.
  Verify: `git ls-files --others --ignored --exclude-standard | grep -x raw`
  no longer would hide a `raw/` directory (create one temporarily under a
  scratch path, confirm `git status` reports it, then remove the scratch
  directory) — or simply confirm the line is gone and the adjacent comment
  is no longer contradicted.
- [ ] 3.2 Verify: re-run the full bash + pytest suite (Task 2.1's list)
  after 3.1, confirming no regression from removing the `raw` line.
