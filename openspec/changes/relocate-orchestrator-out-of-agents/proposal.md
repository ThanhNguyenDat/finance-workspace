## Why

`.agents/` is declared by `CLAUDE.md`, `AGENTS.md`, and `openspec/config.yaml`
as the **shared instruction source of truth** for both agents: rules, skills,
and the launcher scripts that read them. `phase-agent-python-orchestrator`
placed a full `uv`-managed Python distribution in the hidden orchestrator
project directory under `.agents/`
because that was the shortest path from the three bash scripts it replaced
(`.agents/scripts/*.sh` shims resolve their project as `$SCRIPT_DIR/../orchestrator`).
The result is that an instruction directory now also contains a build system,
a locked third-party dependency set (`claude-agent-sdk`, `openai-codex`,
`pyyaml`), a test suite, and a 561 MB `.venv` — four kinds of artifact that
`.agents/` was never described as owning.

Two concrete costs today:

- **Ambiguous ownership.** `sync-agent-links.sh` mirrors `.agents/skills` and
  `.agents/rules` into each CLI's native directory and explicitly skips
  `openspec*`; `orchestrator/` is skipped only because the script iterates
  two named subdirectories rather than because any rule says it should be.
  Every reader of `CLAUDE.md`'s "Canonical Instructions" section has to learn
  by inspection that one child of `.agents/` is not instructions at all.
- **Hidden-path friction.** The application code of the orchestration system
  lives under a dotted directory, so it is invisible to a plain `ls`, is
  skipped by default by tools that ignore dot-directories, and its
  `pyproject.toml`/`uv.lock`/`pytest.ini` triple is split across a visible
  root file (`pytest.ini`, whose only content is
  `testpaths` entry and a hidden project directory.

`phase-agent-python-spawn-layer` will move the *remaining* ~700 lines of bash
into this same package, making it the primary home of the orchestration
system rather than a side car. Relocating now, while the package is 20 tracked
files, is materially cheaper than relocating after that change lands.

## What Changes

- Move the `uv` project from the former hidden orchestrator project directory
  to
  `tools/orchestrator/` with **no source-code behavior change**:
  `git mv` of every tracked file, preserving the internal
  `src/orchestrator/...` layout, the distribution name
  (`phase-agent-orchestrator`), and every module path used by
  `python -m orchestrator.cli.<module>`.
- Update every path reference to the former hidden project location:
  - the three bash shims' `PROJECT_DIR` default (`.agents/scripts/ops-runtime.sh`,
    `phase-agent-state.sh`, `quant-research-state.sh`);
  - `.agents/scripts/tests/hermetic-env.sh`'s
    `PHASE_AGENT_ORCHESTRATOR_PROJECT` export;
  - `pytest.ini`'s `testpaths`;
  - `.gitignore`'s `accounts.yaml` entry;
  - `.agents/rules/coding-and-verification.md` and
    `.agents/skills/quant-research-loop/SKILL.md` bootstrap instructions.
- Pin the workspace-root derivation that the move puts at risk. Three modules
  (`state/ops_transaction.py`, `state/quant_research.py`,
  `locks/change_lock.py`) default their root to
  `Path(__file__).resolve().parents[5]`, a magic depth that silently encodes
  "package is exactly five levels below the repository root". The chosen
  target preserves that depth, but the coupling is currently untested; this
  change adds a regression test asserting the default root resolves to the
  repository root, so a future move cannot break lock and state placement
  silently.
- Reconcile the in-flight OpenSpec changes that reference the old path
  (`phase-agent-python-spawn-layer`, `phase-agent-account-registry-config`)
  to the new one, so their unstarted tasks stay executable.
- **Non-goals**: no change to `.agents/scripts/` script names, locations, or
  CLI contracts; no change to the package's internal module layout (that was
  `phase-agent-orchestrator-submodules`); no consolidation of the three
  `parents[5]` call sites into one shared helper; no dependency, version, or
  Python-version change; archived OpenSpec changes are historical records and
  are not rewritten.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
(none — `openspec/specs/ops-backend-routing/spec.md` contains no reference to
the package's filesystem location, and every external CLI contract
(`.agents/scripts/*.sh` paths, subcommands, stdout, exit codes) is unchanged.
`skip_specs: true` is set.)

## Impact

- **Affected repository**: `finance-workspace` only. This is orchestration
  tooling, not production runtime code, so `finance-mw`, `finance-web`,
  `finance-live-action`, `finance-broker`, and `mt5` are unaffected.
- **Affected files**: 20 tracked files under the former hidden project move;
  three shims, `hermetic-env.sh`, `pytest.ini`, `.gitignore`, one rule file,
  one skill file, and two in-flight OpenSpec changes are edited in place.
  `.github/workflows/agent-contracts.yml` needs no path edit (it references
  only `.agents/scripts/**` and sets up `uv` generically) — this must be
  confirmed, not assumed, by a green run on the cutover commit.
- **Operator action required**: the existing hidden-project `.venv` and the
  local, git-ignored `accounts.yaml` are untracked
  and do **not** move with `git mv`. `accounts.yaml` must be moved by hand
  before the first post-cutover run or every account-scoped phase attempt
  loses its account directories; the `.venv` is re-created by `uv sync` at the
  new path.
- **Trading safety**: none directly. Safety-relevant to the OPS workflow: the
  `parents[5]` derivation decides where change locks and OPS state are written,
  so an unnoticed break would place locks outside the repository root and
  allow two concurrent OPS transactions to believe they each hold the lock.
  This is why the regression test above is in scope rather than deferred.
- **Rollback**: a single revert of the cutover commit restores the old path;
  the operator must move `accounts.yaml` back and re-run `uv sync` at the old
  location. No data migration, no deployed artifact, no CI/CD or production
  surface is involved.
