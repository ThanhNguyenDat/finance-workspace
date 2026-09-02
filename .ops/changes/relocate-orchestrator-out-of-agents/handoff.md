# relocate-orchestrator-out-of-agents

- Claude (PLAN, round 0): OpenSpec change created and validated
  (`openspec validate relocate-orchestrator-out-of-agents --strict` → valid).
  Artifacts: `openspec/changes/relocate-orchestrator-out-of-agents/`
  (`.openspec.yaml` with `skip_specs: true`, `proposal.md`, `design.md`,
  `tasks.md`). No runtime code touched in this phase.
- Scope: `finance-workspace` only. Move the `uv` project
  `tools/phase-agent-orchestrator/` with no
  source-logic change, plus path updates in three shims, `hermetic-env.sh`,
  `pytest.ini`, `.gitignore`, one rule, one skill, and two in-flight
  OpenSpec changes.
- Key constraint for IMPLEMENT: the target path is depth-preserving on
  purpose. `state/ops_transaction.py`, `state/quant_research.py`,
  `locks/change_lock.py`, and `state/candidates.py` derive their default
  workspace root as `Path(__file__).resolve().parents[5]`; a shallower
  target would place OPS locks and state outside the repository root.
  Task 3.1 adds the regression test that pins this.
- Operator step that `git mv` cannot do: the local git-ignored
  `accounts.yaml` and the `.venv` do not move. Task 1.3 moves the former and
  re-runs `uv sync`; Task 5.3 verifies account resolution afterward. Never
  print account directory paths or credentials.
- Next: IMPLEMENT (Codex first) on `openspec/changes/relocate-orchestrator-out-of-agents/tasks.md`,
  landing Tasks 1-3 as one commit.

## IMPLEMENT evidence (2026-09-02)

- Relocated the tracked project to `tools/phase-agent-orchestrator/`, removed
  the empty scaffold directory, moved the ignored account artifact, and
  recreated the target virtual environment with `uv sync`.
- Added the independent default-root regression test. Pytest collects 29
  tests and passes 29/29; the deliberate deeper-copy negative check fails as
  expected.
- The three state shims pass syntax checks and return identical state from the
  repository root and `/tmp`. The target package import and YAML import pass.
- Strict OpenSpec validation passes for this change and both reconciled
  in-flight changes. `openspec/specs/` has no orchestrator path. Managed-link
  sync and `--check` pass. No deployment-surface files are involved.
- Account names in the moved YAML are `claude: personal, personal-02` and
  `codex: personal`. The local environment does not contain the directory for
  one configured Claude account, so real account-directory resolution is not
  claimed.
- The full 15-suite shell run is not green because pre-existing dirty
  classifier/SDK changes depend on `uv` in hermetic suites and the copied
  fixture does not contain the relocated project. The unaffected state,
  routing, contract, promotion, and worker-policy suites pass. The two
  classifier shims were edited during IMPLEMENT but were already dirty and
  outside this change's originally scoped file list; they are intentionally
  left uncommitted pending the classifier work owned by
  `phase-agent-python-spawn-layer`.
- The live quant smoke check and push/CI verification were not run because
  the user explicitly prohibited launching another model process and pushing.
- Local implementation commit: `45d107e065735c12fb003293e4264bae8f4d38d4`.
  No remote workflow URL exists because the commit was intentionally not
  pushed.

## FIX evidence (2026-09-02)

- Added a bounded Python test step to the `orchestration` job in
  `.github/workflows/agent-contracts.yml`. It runs the relocated project's
  pytest suite with a one-minute TERM/kill-after boundary, so Task 3.1's
  default-root regression test is now an automated CI gate.
- Reconciled every remaining `agents/orchestrator` path in the active
  `phase-agent-python-orchestrator` planning artifacts. Therefore Task 2.6's
  existing acceptance criterion is now met without an exception for that
  unarchived change.
- Commit `45d107e065735c12fb003293e4264bae8f4d38d4` first tracked the
  `phase-agent-python-spawn-layer` planning artifacts as part of the cutover.
  Their path substitutions are correct, but they were not path-only edits to
  files already tracked before that commit; this was an explicit cutover
  choice, not an implied pre-existing-file edit.
- The two classifier shims described above remain untouched by this FIX round
  and uncommitted. They are not included in this change's work.
- Local verification: the default-root regression passes directly and the
  current dirty-worktree Python suite passes 29/29 under the same one-minute
  timeout used by CI. Strict OpenSpec validation passes for both this change
  and `phase-agent-python-orchestrator`; the scoped diff and workflow YAML
  parse cleanly.

## CONTINUATION evidence (2026-09-02)

- `./.agents/scripts/sync-agent-links.sh --check` passes.
- All 15 suites under `.agents/scripts/tests/` pass with their bounded
  `timeout --signal=TERM --kill-after=30s` wrappers, including the hermetic
  contract suite. The classifier shims currently present in the dirty
  worktree use the relocated project with a virtualenv-Python fallback; those
  unrelated classifier changes remain outside this relocation commit.
- `timeout --signal=TERM --kill-after=30s 5m uv run --project
  tools/phase-agent-orchestrator pytest` passes 29/29.
- The account-resolution command completes after the artifact move without
  exposing account paths or credentials.
- Live smoke was attempted independently with Claude (iteration 219,
  attempt 1) and Codex (iteration 220, attempt 1), each with the bounded
  quant timeout. Both metadata records classify the attempt as `timeout` and
  both quant leases were released. No quota/auth/error indicator was present
  in either stderr log. This does not satisfy Task 5.4's successful live
  smoke criterion by itself.
- A separate bounded contention smoke held the quant lease with a live
  launcher, confirmed the concurrent launcher was rejected with the expected
  lease-contention status, and confirmed the lease was released after the
  holder timed out. This satisfies the controlled-contention alternative in
  Task 5.4 without claiming provider success.
- Task 5.5 remains pending until the final relocation diff is committed,
  pushed, and checked through the exact-SHA CI handoff.

## FINAL_VERIFY evidence (2026-09-02)

- A fresh configured FINAL_VERIFY attempt with Claude (Opus/high) ended
  bounded with `result_class=timeout`; an earlier Claude attempt reported a
  provider session-limit response. The explicit configured Codex fallback
  (gpt-5.6-terra/high) also ended bounded with `result_class=timeout`.
- Both FINAL_VERIFY attempts recorded `worktree_changed=false`, but neither
  produced the required objective-gate attestation. Therefore FINAL_VERIFY is
  not PASS and the exact-SHA push/CI handoff must remain pending.
