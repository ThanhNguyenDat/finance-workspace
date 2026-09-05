# Coding and Verification Rules

## Source of truth

- Treat the local Git repository and the pushed GitHub commit as the source of
  truth.
- Treat production as a deployment target, never as an editing workspace.
- Keep changes small, focused, reviewable, and reversible.
- Reuse existing patterns before adding abstractions or dependencies.

## Branch and merge discipline

- Every new branch starts from current `main` — pull `main` before creating
  it, never branch off another in-progress or unmerged branch.
- Finish one branch by merging it into `main` before starting the next piece
  of work; do not stack a new branch on top of an unmerged one.
- Keep local `main` and `origin/main` equal — fetch and fast-forward local
  `main` before branching and again immediately after every merge, so the
  two never drift apart.
- History stays fully linear: merge with `--ff-only`; if `main` moved during
  the change, rebase the branch onto the latest `main` first, then
  fast-forward. Never a plain `git merge` that creates a merge commit.

### Per-change worktree workflow

Every OpenSpec change gets its own git worktree and branch, in every
affected repository (`finance-workspace`, `finance-mw`, `finance-broker`,
`finance-live-action`, `mt5`), from the moment the change is scaffolded
until it merges — no exception for a docs-only or single-file change. This
supersedes a prior "commit directly to `main`" solo-maintainer exception:
that exception assumed no concurrent writers ever touch the same tree,
which stopped being true once a background Codex turn could commit to the
same working tree an interactive session was also using at the same time
(`adopt-per-change-worktree-workflow`, 2026-09-05).

- **Location**: `.agents/worktrees/<change-name>` inside the repo being
  changed — not `.claude/worktrees/`, so the location is shared/Codex-
  visible like the rest of `.agents/`. Branch name is the change's own
  kebab-case name, no prefix.
- **Create**: sync local `<default-branch>` first (`git fetch origin && git
  merge --ff-only origin/<default-branch>`, per the "Branch and merge
  discipline" bullets above — local `<default-branch>` may legitimately be
  ahead of `origin/<default-branch>` with not-yet-pushed commits, so branch
  from local, never straight from `origin/`), then `git worktree add
  .agents/worktrees/<change-name> -b <change-name> <default-branch>` (this
  already checks the new branch out inside the new worktree — no separate
  `checkout` needed). Switch into it with Claude Code's `EnterWorktree({
  path: ... })`.
- **Timing**: `finance-workspace`'s own worktree (it always holds
  `openspec/changes/<name>/`) is created before running `openspec new
  change`. Any other repository a cross-repo change touches gets its own
  worktree lazily, right before the first edit lands there — a git worktree
  cannot span repositories, so a cross-repo change has one worktree per
  affected repo, sharing the change's branch name for traceability.
- **Provider turns**: every `codex-exec`/`claude-exec`/`quant-research-exec`
  call for the change passes `--cwd <that repo's worktree path>`, never the
  main tree. This is the mechanism that actually removes the concurrency
  risk.
- **Merge**: sync local `<default-branch>` to `origin/<default-branch>`
  first (it may have moved since the worktree was created), then fast-
  forward the change's branch in; if that fails, rebase the branch onto the
  now-synced local `<default-branch>` and fast-forward. Never a merge
  commit. Do this per repository, once that repository's branch has passed
  FINAL_VERIFY (see required order below).
- **Cleanup**: `EnterWorktree` was entered via `path`, so `ExitWorktree`
  cannot `remove` it — only `action: "keep"` returns to the original
  directory. After merging, clean up manually: `git worktree remove
  .agents/worktrees/<change-name>` then `git branch -d <change-name>`.
- Every affected repository must gitignore `.agents/worktrees/` — a nested
  worktree shows up as an untracked directory in the outer repo's `git
  status` otherwise.

The **push remains the release gate**: non-trivial implementation must
receive a fresh configured FINAL_VERIFY process before it is pushed.
Provider-independent verification is preferred. When quota or an explicit
phase pin yields the same provider, process-separated review plus all
applicable objective evidence is required and must not be called
independent.

Required order for a non-trivial change:

```text
PLAN (OpenSpec proposal/design/tasks, in the change's worktree) → IMPLEMENT
→ local checks → local commit (on the change's branch) → independent VERIFY
→ FIX (if needed) → independent FINAL_VERIFY → merge (ff/rebase, per repo)
→ worktree/branch cleanup → push main → GitHub Actions → Coolify
→ production verification
```

Claude plans and verifies by default; Codex implements and fixes by default
(`CLAUDE.md`'s Role/Working Model role boundary). Either falls back to the
other when the default provider for that step is confirmed out of quota.
There is no coordinator or resolver that detects quota and switches
providers automatically — that mechanism was deleted along with the old
`tools/orchestrator/`; provider selection and fallback are a manual,
operator- or session-level decision. "Independent"/"fresh" above means a
verification pass that re-derives evidence rather than trusting the
implementer's own summary, not a separate provider identity.

This does **not** relax anything else in this file: still run the full local
verification pass before committing, still keep each commit small and
reviewable, still push and track CI to a real green, still verify the deployed
revision and behavior in production. The worktree-per-change requirement is
about isolating *where* edits happen, not about skipping verification.

## Required verification order

1. Inspect the relevant local code, tests, configuration, and Git history.
2. Implement and validate the change locally.
3. Review the diff and commit every in-scope change.
4. Push the commit and verify the exact SHA on GitHub.
5. Track all required GitHub Actions jobs to success.
6. Let CI/CD deploy the immutable revision through Coolify.
7. Verify the deployed revision and behavior in production.

Do not skip directly to production inspection when the answer can be obtained
from the local repository or GitHub. Do not edit production code or
configuration over SSH.

### Claude role note: bug investigations & system reviews

This file is shared across agents; the exception below applies only to
Claude, not to other agents reading this file (e.g. Codex still owns the
full order above).

When the user's request to Claude is a bug investigation or a system review
(not an explicit "fix this" instruction), Claude stops after step 1 —
inspect, do not implement. Document the root cause with exact file:line
citations, a fix-direction note explicitly marked "not applied —
investigation only", and a verification checklist in `docs/reviews/<topic>.md`
instead of proceeding to steps 2-7. A separate Codex agent implements,
commits, pushes, and carries the change through the rest of this
verification order; Claude verifies the result afterward once Codex reports
done. If the user explicitly asks Claude for a direct code fix in a given
request, that overrides this note for that request only.

## Test timeout contract

- Give every unit, integration, load, contract, shell, and end-to-end test
  command a hard timeout.
- Use the test framework's native timeout when it can terminate the full test
  process, such as `go test -timeout=10m`; otherwise wrap the command with GNU
  `timeout --signal=TERM --kill-after=30s`.
- Set `timeout-minutes` on every GitHub Actions job as a final safety boundary.
- Keep a short TERM grace period, then force-kill the process tree so a
  deadlocked test cannot occupy a self-hosted runner indefinitely.
- Interactive watch-mode commands are the only exception; CI must never use
  watch mode.

## Language-specific checks

### Go

- Run `gofmt` or the repository formatting check.
- Run targeted Go tests, then `go test ./...`, `go vet ./...`, and the required
  build.
- Keep business logic tests deterministic and independent from production
  services.

### Web

- Run the applicable lint, tests, typecheck, and production build when web code
  changes.
- Display only data supported by the current backend contract.

### Native automation

- Keep scheduled automation in Go under `internal/automation` with operational
  entry points under `cmd/worker/`; run each business domain's schedule
  through exactly one owning worker process (currently `finance-trading-worker`,
  `finance-english-worker`, `finance-social-worker`, `finance-tvl-worker`) —
  splitting a single worker into per-domain processes for independent
  scaling/resource limits/failure isolation is expected and does not itself
  count as adding "a second schedule owner" below; that phrase means two
  processes racing to own the *same* job, not one job living in its own
  dedicated process.
- Do not add Python automation modules or fork language runtimes from the Go
  worker.
- Keep every domain's scheduler always enabled. Do not add a second process
  that can run the *same* scheduled job as another, and do not add a cutover
  flag for a job's schedule ownership without a tested distributed lease.
- Run native automation Go tests with a hard timeout in GitHub Actions.

### Orchestrator tooling

- `uv` is required for the Python-backed CLIs under `tools/orchestrator/`
  (`codex-exec`, `claude-exec`, `sync-agent-links`).
- Bootstrap the project with `uv sync --project tools/orchestrator`
  before invoking the executable wrappers in
  `tools/orchestrator/bin/`; the wrappers use `uv run --project`
  and can use the bootstrapped venv when a restricted `PATH` omits `uv`.
- Keep `tools/orchestrator/pyproject.toml` and `uv.lock` committed together;
  do not introduce another Python package manager for this tooling.

## Completion evidence

A change is complete only when the local checks pass, the commit exists on
GitHub, CI succeeds, Coolify deploys the intended revision when deployment is
required, and production verification passes.
