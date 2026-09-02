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
  routing, contract, promotion, and worker-policy suites pass. Those changes
  were preserved and not repaired here.
- The live quant smoke check and push/CI verification were not run because
  the user explicitly prohibited launching another model process and pushing.
- Local implementation commit: `45d107e065735c12fb003293e4264bae8f4d38d4`.
  No remote workflow URL exists because the commit was intentionally not
  pushed.
