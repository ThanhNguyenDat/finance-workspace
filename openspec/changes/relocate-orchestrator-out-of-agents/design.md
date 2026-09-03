## Context

See `proposal.md - Why`. Verified current-state facts (2026-09-02, at this
change's base commit):

- The package is 20 tracked files in the former hidden project, plus
  two untracked local artifacts: `accounts.yaml` (git-ignored via `.gitignore`
  line 14) and `.venv` (561 MB, self-ignored by uv's `.venv/.gitignore`).
- An empty leftover directory `tools/orchestrator/src/orchestrator/`
  exists
  from the original `uv init --package` scaffold; it is untracked and holds no
  files.
- Exactly seven non-OpenSpec files reference the former hidden-project path:
  `.agents/scripts/ops-runtime.sh`, `.agents/scripts/phase-agent-state.sh`,
  `.agents/scripts/quant-research-state.sh`,
  `.agents/scripts/tests/hermetic-env.sh`,
  `.agents/rules/coding-and-verification.md`,
  `.agents/skills/quant-research-loop/SKILL.md`, `.gitignore`, plus
  `pytest.ini`. Neither `.claude/`, `.codex/`, `openspec/specs/`, nor
  `.github/workflows/` contains the string.
- Each of the three shims resolves its project as
  `PROJECT_DIR="${PHASE_AGENT_ORCHESTRATOR_PROJECT:-$SCRIPT_DIR/../orchestrator}"`,
  where `SCRIPT_DIR` is derived from `BASH_SOURCE` (the `/proc`-based
  ancestry fallback was already removed by `phase-agent-python-orchestrator`
  task 8.2). The env-var override is the seam the hermetic test harness
  already uses, so the shims are relocatable by construction.
- Three modules derive a default root by counting levels:
  `state/ops_transaction.py:30`, `state/quant_research.py:21`, and
  `locks/change_lock.py:31` each use
  `Path(os.environ.get("<VAR>", Path(__file__).resolve().parents[5]))`, where
  the five ancestors are `<subpkg>/`, `orchestrator/`, `src/`,
  `orchestrator/`, `.agents/`. `state/candidates.py:23` does the same with
  `PHASE_AGENT_ROOT`. No test asserts the resulting value.
- `accounts/registry.py:29` uses `parents[3]` to find `accounts.yaml`, which
  is relative to the *project directory*, not the repository root, and is
  therefore unaffected by any relocation that keeps `src/<pkg>/<subpkg>/`
  intact.

## Goals / Non-Goals

**Goals:**
- The `uv` project no longer lives under `.agents/`, restoring `.agents/` to
  "shared agent instructions and their launcher scripts" as the documents
  describe it.
- Every externally observable contract is byte-identical after the move:
  the same `.agents/scripts/*.sh` paths accept the same subcommands and
  produce the same stdout and exit codes; state, lock, and log files are
  written to the same filesystem locations as before.
- The move's one real hazard — the `parents[5]` root derivation — is covered
  by a test after this change, not left as an implicit invariant.

**Non-Goals:**
- Moving or renaming any `.agents/scripts/*.sh` entry point. Operators invoke
  those paths directly from a terminal today.
- Refactoring the `parents[5]` call sites into one shared helper. That is a
  worthwhile cleanup but it is a behavior-adjacent edit to four modules, and
  keeping this change a pure move plus path edits is what makes it reviewable
  and revertible in one commit.
- Rewriting archived OpenSpec changes. `openspec/changes/archive/**` records
  what was true when each change shipped.

## Decisions

### Decision 1: target path is `tools/orchestrator/`

The directory name matches the distribution name already in
`pyproject.toml` (`phase-agent-orchestrator`) and the importable package
(`orchestrator`), so all three agree for the first time. A
`tools/` parent leaves room for future workspace tooling without another
top-level directory per tool, and it reads correctly against `CLAUDE.md`'s
rule that `finance-workspace` hosts orchestration, not runtime, code.

Critically, this target sits at **the same depth as the former location**:
`tools/orchestrator/src/<pkg>/<subpkg>/x.py` is six levels below
the repository root, so every `parents[5]` derivation continues to resolve to the
repository root with no source edit.

**Alternatives rejected:**
- `orchestrator/` at the repository root — one level shallower, which would
  silently make `parents[5]` resolve to the repository root's *parent*
  (`/home/.../finance/`), scattering `.ops` locks and state outside the repo.
  It is fixable by editing four magic numbers, but choosing a depth-preserving
  target removes the failure mode instead of managing it.
- `.ops/orchestrator/` — `.ops/**/runtime/` is declared transient and
  git-ignored; putting tracked source there contradicts the same
  instructions-vs-artifacts separation this change exists to restore.
- Publishing the package and depending on it as an external dependency — far
  beyond the requested scope, and it would put orchestration source outside
  the repository whose locks it manages.

### Decision 2: `git mv`, one commit, no source-code edits

The move is executed with `git mv` so rename detection keeps `git log
--follow` and `git blame` intact across the boundary — history continuity
matters here because this package's lock logic was corrected across several
recent commits and those fixes must stay attributable. No `.py` file's
contents change during the move step; the only Python addition in this change
is the new regression test from Decision 3.

The move and every path-reference edit land in **one commit**. A split (move
first, fix references second) leaves an intermediate commit in which every
shim, the whole bash suite, and CI are broken, which violates the
"small, focused, reviewable, and **reversible**" requirement in
`.agents/rules/coding-and-verification.md` more than a single 30-file commit
does.

### Decision 3: pin the root derivation with a test rather than refactor it

Add one pytest case asserting that, with the relevant environment variable
unset, the module-level default root equals the repository root — computed
independently in the test (walk up from the test file to the directory
containing `.git`, or the two-levels-up project parent), not by repeating
`parents[5]`. The test must fail if the package is moved to a different depth
without updating the constant.

This is the smallest change that converts an invisible coupling into a loud
one. Consolidating the four call sites is deliberately deferred (Non-Goals);
the test protects the same invariant either way and does not have to be
rewritten if the consolidation happens later.

### Decision 4: keep the `PHASE_AGENT_ORCHESTRATOR_PROJECT` override contract

The env-var override stays the single supported way to point the shims at a
non-default project directory, and `hermetic-env.sh` keeps setting it. Only
the literal default and the hermetic export change. This preserves the
existing seam that makes the shims testable from a copied fixture workspace.

### Decision 5: local artifacts are an explicit operator step, not automation

`accounts.yaml` is git-ignored and holds the operator's real per-account
directory paths; `.venv` is a 561 MB build artifact. Neither is moved by
`git mv`, and this change does **not** add a migration script for them.
Instead the cutover task requires the operator to move `accounts.yaml` and run
`uv sync --project tools/orchestrator`, and requires positive
verification that account-scoped routing still resolves real account
directories afterward. Silent fallback here is the most likely
post-relocation failure, so it gets a named verification step rather than a
best-effort helper.

## Risks / Trade-offs

- **A missed reference breaks every phase attempt.** The shims are on the hot
  path of `/ops:e2e` and `quant-research`; a stale `PROJECT_DIR` fails closed
  with `orchestrator project not found` (exit 1), which is loud rather than
  silent. Mitigation: a repository-wide search for the former hidden-project
  path is an
  explicit verification step, and the full bash suite plus a live smoke check
  must pass before the push.
- **`accounts.yaml` left behind.** Failure mode is an account registry that
  resolves to defaults or errors, not a corrupted lock. Mitigation:
  Decision 5's named step plus a post-cutover assertion that
  `configure-phase-agents.sh show` still reports the expected `ACCOUNT`
  column values.
- **In-flight changes referencing the old path.** `phase-agent-python-spawn-layer`
  (tasks 3.0, 6.2 and its design/proposal) and
  `phase-agent-account-registry-config` cite the former hidden project in
  commands a future implementer would paste verbatim. Mitigation: reconciling
  those two changes' text is in scope here (Task 4); their behavior and task
  ordering are untouched.
- **Reviewer cost of a rename-heavy diff.** One commit touching ~30 paths is
  harder to skim than several. Mitigation: `git mv` keeps the diff rendered as
  renames, and the only content edits are single-line path strings plus one
  new test.
- **`.venv` rebuild cost.** `uv sync` re-downloads the pinned dependency set,
  including two SDKs. Bounded, offline-cache-friendly, one-time.

## Migration Plan

1. Create `tools/` and move the former hidden project with `git mv` to
   `tools/orchestrator`.
2. Remove the empty leftover `src/orchestrator/` scaffold directory.
3. Update the three shims, `hermetic-env.sh`, `pytest.ini`, and `.gitignore`.
4. Update `.agents/rules/coding-and-verification.md` and
   `.agents/skills/quant-research-loop/SKILL.md`; re-run
   `./.agents/scripts/sync-agent-links.sh` and its `--check`.
5. Add the Decision 3 regression test.
6. Operator moves local `accounts.yaml`; run
   `uv sync --project tools/orchestrator`.
7. Run the full bash suite, `uv run --project tools/orchestrator pytest`,
   and one live `run-phase-agent-command.sh quant-research` smoke check.
8. Reconcile the two in-flight OpenSpec changes.
9. One commit, push to `main`, verify the `Agent contracts` run for that exact
   SHA is green on a clean hosted runner (which has no pre-existing `.venv` at
   either path — the strongest available evidence that no stale path survives).

**Rollback**: revert the single commit, move `accounts.yaml` back, re-run
`uv sync --project tools/orchestrator`. No deployed artifact and no
production surface is involved, so rollback is local plus one push.
