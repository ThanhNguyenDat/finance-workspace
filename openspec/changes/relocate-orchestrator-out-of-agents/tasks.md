All tasks are in the `finance-workspace` repository only (see proposal.md
Impact). This change is a pure relocation: apart from the one new test in
Task 3.1, no `.py` file's contents may change. If any task appears to require
a source-logic edit, stop and revise `design.md` first — that is evidence the
depth-preservation assumption in Decision 1 is wrong.

Tasks 1-3 must land as **one commit** (design.md Decision 2); do not commit
after Task 1.

## 1. Move the project

- [x] 1.1 Move the former hidden orchestrator project with `git mv` to
  `tools/orchestrator` (creating `tools/` as needed). Verify:
  `git status` shows the 20 tracked
  files as renames (`R`), not as deletes plus adds, and
  `git log --follow tools/orchestrator/src/orchestrator/state/ops_transaction.py`
  still reaches the commits that predate this change.
- [x] 1.2 Remove the empty leftover `uv init` scaffold directory
  `tools/orchestrator/src/orchestrator/` (design.md Context —
  untracked and empty). Verify: `find tools/orchestrator/src -maxdepth 1 -type d`
  lists only `src` and `src/orchestrator`.
- [x] 1.3 Move the local, git-ignored `accounts.yaml` to
  `tools/orchestrator/accounts.yaml` and run
  `uv sync --project tools/orchestrator` (design.md Decision 5).
  Verify: `uv run --project tools/orchestrator python -c "import orchestrator, yaml"`
  exits 0, and `test -f tools/orchestrator/accounts.yaml` succeeds;
  also assert that the former hidden project directory is absent. Do not print
  the file's contents.

## 2. Update every path reference

- [x] 2.1 Update the `PROJECT_DIR` default in `.agents/scripts/ops-runtime.sh`,
  `.agents/scripts/phase-agent-state.sh`, and
  `.agents/scripts/quant-research-state.sh` from `$SCRIPT_DIR/../orchestrator`
  to the new location, and update each script's `uv is required (or bootstrap
  ...)` error message to name the new `.venv` path. Keep the
  `PHASE_AGENT_ORCHESTRATOR_PROJECT` override precedence unchanged (design.md
  Decision 4). Verify: `bash -n` passes on all three, and
  `./.agents/scripts/ops-runtime.sh state` (run from the repository root and
  again from a different working directory, e.g. `/tmp`) returns the same
  output it returns before this change rather than
  `orchestrator project not found`.
- [x] 2.2 Update `PHASE_AGENT_ORCHESTRATOR_PROJECT` in
  `.agents/scripts/tests/hermetic-env.sh` to
  `"$HERMETIC_ROOT_DIR/tools/orchestrator"`. Verify:
  `./.agents/scripts/tests/test_hermetic_agent_contracts.sh` passes unmodified.
- [x] 2.3 Update `pytest.ini`'s `testpaths` to
  `tools/orchestrator/tests`. Verify: `uv run --project
  tools/orchestrator pytest --collect-only` collects the same
  number of tests as it collected before the move.
- [x] 2.4 Update `.gitignore` line 14 to
  `tools/orchestrator/accounts.yaml`. Verify:
  `git check-ignore -v tools/orchestrator/accounts.yaml` reports
  that rule, and `git status --porcelain` does not list `accounts.yaml` as an
  untracked file. This check is mandatory — the file holds the operator's real
  account directory paths and must never become tracked.
- [x] 2.5 Update the `uv`/bootstrap paths in
  `.agents/rules/coding-and-verification.md` (the "Phase-agent orchestration
  tooling" section) and `.agents/skills/quant-research-loop/SKILL.md`. Verify:
  `./.agents/scripts/sync-agent-links.sh` then
  `./.agents/scripts/sync-agent-links.sh --check` both succeed.
- [x] 2.6 Verify no reference survives:
  `grep -rn "agents[/]orchestrator" --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ .`
  returns hits only under `openspec/changes/archive/` (historical records,
  deliberately untouched per design.md Non-Goals) and under
  `.ops/**/runtime/logs/` (transient, git-ignored).

## 3. Pin the workspace-root derivation

- [x] 3.1 Add a pytest case (design.md Decision 3) asserting that, with
  `OPS_ROOT`, `QUANT_RESEARCH_ROOT`, and `PHASE_AGENT_ROOT` unset, the default
  root used by `state/ops_transaction.py`, `state/quant_research.py`,
  `locks/change_lock.py`, and `state/candidates.py` equals the repository
  root, computed independently in the test (walk up from `__file__` to the
  directory containing `.git`) rather than by repeating `parents[5]`. Verify:
  the test passes at the new location, and — as a deliberate negative check
  run manually, not committed — temporarily copying the package one directory
  deeper makes it fail.

## 4. Reconcile in-flight OpenSpec changes

- [x] 4.1 Update every former hidden-project path in
  `openspec/changes/phase-agent-python-spawn-layer/{proposal,design,tasks}.md`
  and `openspec/changes/phase-agent-account-registry-config/{proposal,design,tasks}.md`
  to `tools/orchestrator`, changing paths only — no task, decision,
  or sequencing text. Verify: `openspec validate --strict` (or the repository's
  configured equivalent) passes for both changes, and a `git diff` of the two
  directories shows only path substitutions.
- [x] 4.2 Confirm `openspec/specs/ops-backend-routing/spec.md` and the other
  files under `openspec/specs/` still contain no reference to either path.
  Verify: `grep -rn "orchestrator/" openspec/specs/` returns nothing, keeping
  `skip_specs: true` correct for this change.

## 5. Full verification and delivery

- [x] 5.1 Verify: every bash suite under `.agents/scripts/tests/` passes
  unmodified with its existing bounded timeout — the same 15-suite list
  `.github/workflows/agent-contracts.yml` runs (`test_ops_orchestration.sh`,
  `test_quant_research_state.sh`, `test_codex_availability_detection.sh`,
  `test_quant_research_contract.sh`, `test_quant_backend_routing.sh`,
  `test_codex_worker_policy.sh`, `test_quant_promotion_trace.sh`,
  `test_phase_agent_state.sh`, `test_provider_availability.sh`,
  `test_phase_agent_routing.sh`, `test_phase_agent_quant_launcher.sh`,
  `test_multi_account_routing.sh`, `test_claude_quant_launcher.sh`,
  `test_claude_worker_policy.sh`, `test_hermetic_agent_contracts.sh`).
- [x] 5.2 Verify: `uv run --project tools/orchestrator pytest`
  passes with the same test count as before the move plus the one added in
  Task 3.1.
- [x] 5.3 Verify account resolution survived the local-artifact move
  (design.md Decision 5, the most likely silent failure):
  `./.agents/scripts/configure-phase-agents.sh show` reports the same
  `ACCOUNT` column values it reported before this change. Report the account
  *names* only; never print account directory paths or any credential.
- [x] 5.4 Run one live end-to-end smoke check:
  `./.agents/scripts/run-phase-agent-command.sh quant-research`, and verify it
  completes with a `Quant iteration <n> completed with <provider>` line (or
  the same lease-contention message when a prior run still holds the lease).
- [ ] 5.5 Commit Tasks 1-3's files as one reviewable commit (Task 4's OpenSpec
  reconciliation may ride along), push to `origin/main` per the solo-maintainer
  direct-to-main rule, and verify the `Agent contracts` workflow run **for that
  exact SHA** succeeds — including the "Run bounded orchestration tests" step,
  which executes on a clean hosted runner with no pre-existing `.venv` at
  either path and is therefore the strongest available evidence that no stale
  path reference survives. Record the SHA and run URL in
  `.ops/changes/relocate-orchestrator-out-of-agents/handoff.md`.
- [x] 5.6 Confirm no deployment surface is involved: this change touches no
  file under `docker/`, no service image, and no Coolify-deployed application,
  so `.agents/rules/production-deployment-verification.md`'s production gate
  does not apply. Verify by inspecting the commit's file list and stating that
  conclusion explicitly in the handoff note rather than leaving the production
  gate silently skipped.
