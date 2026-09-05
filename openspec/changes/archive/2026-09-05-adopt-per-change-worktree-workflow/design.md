## Context

See `proposal.md` - Why. Relevant existing facts this design builds on:

- Claude Code has native `EnterWorktree`/`ExitWorktree` tools. `EnterWorktree`
  either creates a new worktree (always under the fixed path
  `.claude/worktrees/<name>`, on a new branch from `origin/<default-branch>`
  by default) or switches into an *existing* worktree via `path`.
  `ExitWorktree` can `keep` or `remove` a worktree it created itself, but
  explicitly **cannot** `remove` a worktree it only entered via `path`
  ("ExitWorktree will not remove a worktree entered this way; use
  `action: "keep"`").
- `codex-exec`/`claude-exec`/`quant-research-exec` (`tools/orchestrator`)
  all take `--cwd <dir>`, which becomes the Codex/Claude SDK sandbox's
  working directory for that turn — already the integration point for
  pointing a background provider turn at an isolated directory.
- Verified empirically: a git worktree created at a path *inside* another
  git repository's working tree (e.g. `<repo>/.agents/worktrees/<name>`)
  shows up as an untracked directory (`?? .agents/`) in the outer repo's
  `git status` unless gitignored. Git does not hide nested worktrees
  automatically.
- `finance-workspace`'s own commit history is 100% linear today (every
  commit lands directly on `main`, zero merge commits).
- An older, already-abandoned worktree convention exists at
  `/home/lap17204/Desktop/finance/.worktrees/<repo>-<slug>` (sibling to all
  repos, `codex/<slug>` branch prefix), apparently from the deleted
  phase-agent coordinator's per-attempt worktree allocation. Three branches
  there are unmerged since 2026-08-21/22 (see proposal.md - Impact). This
  design does not reuse that location or naming.
- OpenSpec planning artifacts for every change always live in
  `finance-workspace`'s `openspec/changes/<name>/`, regardless of which
  repository(ies) the change implements against (`CLAUDE.md`'s Workspace
  Topology rules) — a cross-repo change's *planning* is always
  workspace-owned even though its *implementation* may span other repos.

## Goals / Non-Goals

**Goals:**
- Give every OpenSpec change, from the moment it is scaffolded to the
  moment it merges, its own isolated git worktree per affected repository —
  so a background Codex turn and the operator's own interactive session
  never write to the same tree at the same time.
- Keep `finance-workspace`'s (and every affected repo's) history linear —
  no merge commits — matching current practice.
- Leave nothing behind per change: worktree directory and branch both
  removed after a successful merge.
- Make the convention consistent and simple enough to state as a short rule
  addition, not a new tool or script.

**Non-Goals:**
- Building new tooling. This uses `EnterWorktree`/`ExitWorktree` plus plain
  `git worktree`/`git branch` commands — no new CLI, no new
  `tools/orchestrator` command.
- Cleaning up the three already-abandoned worktrees/branches from the old
  coordinator (proposal.md - Impact). Separate, explicit operator decision.
- Changing anything about *when* to use Codex vs. Claude, the failover
  design, or any of `tools/orchestrator`'s existing behavior. This change is
  purely about *where* the file edits for a change physically happen.
- A worktree-per-change requirement for ad-hoc, non-OpenSpec work (a quick
  one-off question, a read-only investigation). This applies to work that
  goes through an OpenSpec change; it does not retroactively require every
  trivial interaction to open a worktree.

## Decisions

**1. Worktree location and creation: manual `git worktree add`, then
`EnterWorktree` with `path`.**

`EnterWorktree`'s own creation path is fixed at `.claude/worktrees/<name>`,
not configurable — and the user explicitly wants `.agents/worktrees/`
instead, so every repo's shared (Codex-visible) directory convention holds
for worktrees too. So creation is always two steps:

```bash
git -C <repo> fetch origin
git -C <repo> merge --ff-only "origin/<default-branch>"
git -C <repo> worktree add ".agents/worktrees/<change-name>" \
  -b "<change-name>" "<default-branch>"
```

Branch from local `<default-branch>` (after fast-forwarding it to
`origin/<default-branch>`), not `origin/<default-branch>` directly — caught
during this change's own task 3.1 smoke test: local `<default-branch>` can
legitimately be ahead of `origin/<default-branch>` with not-yet-pushed
commits (this repo's own practice all session), and branching straight from
`origin/` silently drops those commits from the new worktree.

Then `EnterWorktree({ path: "<repo>/.agents/worktrees/<change-name>" })` to
switch the session into it. Branch name is the OpenSpec change's own kebab-
case name (already unique per change) — no `codex/` prefix; that prefix
belonged to the old, unrelated convention this design does not adopt.

Because the worktree was entered via `path` (not created via `name`),
`ExitWorktree` cannot remove it later — only `action: "keep"` is valid to
return to the original directory. Cleanup after a merge (Decision 3) is
therefore always a manual `git worktree remove` + `git branch -d`, never
`ExitWorktree({action: "remove"})`.

Alternative considered: let `EnterWorktree` create the worktree itself
(`name` parameter) and accept the `.claude/worktrees/` location. Rejected —
the user was explicit that the location must be `.agents/`, not
`.claude/`, since Codex (invoked via `--cwd`, not through Claude Code's own
tool surface) needs to operate in the same directory and the project
already draws this exact boundary (".agents/ = canonical shared, .claude/ =
Claude-native only") for skills and rules.

**2. Every affected repository gets its own worktree; planning artifacts
follow `finance-workspace`'s.**

For a single-repo change, one worktree in that repo holds everything: the
OpenSpec planning artifacts when the repo is `finance-workspace`, or just
the implementation when it's one of the other four. For a cross-repo
change, `finance-workspace`'s own worktree (created at `openspec new change`
time, holding `openspec/changes/<name>/`) is separate from each other
affected repository's own worktree (created lazily, the first time that
repo needs an edit for this change) — a git worktree cannot span multiple
repositories, so this is the only structure that fits multiple repos under
one change name. All worktrees for one change share the same branch name
(the change name) for traceability, even though they are unrelated branches
in unrelated repositories.

**3. Worktree creation timing: at `openspec new change`, not at `apply`.**

Per the user's explicit "every change, no exception," even a docs-only
change's planning-artifact authoring happens inside `finance-workspace`'s
worktree, not on `main` directly — so the worktree for the *owning* repo
(always `finance-workspace`, since that's where `openspec new change`
scaffolds files) is created and entered *before* running `openspec new
change`, not after. A repository that only receives *implementation* work
for a cross-repo change gets its own worktree lazily, right before the
first edit lands there (typically inside the `codex-exec`/`quant-research-
exec --cwd` call for that repo) — there is no planning-artifact reason to
worktree a repo before it has any work scheduled in it.

**4. Provider turns point `--cwd` at the worktree, not the main tree.**

Any `codex-exec`/`claude-exec`/`quant-research-exec` call made while
implementing a change passes `--cwd <path to that repo's worktree for this
change>`. This is the mechanism that actually prevents the concurrency
proposal.md describes — a background Codex turn writes inside the isolated
worktree, never the tree the operator or another turn is using.

**5. Merge: fast-forward preferred, rebase-then-ff-merge as fallback, no
merge commits.**

After FINAL_VERIFY passes (unchanged from
`.agents/rules/coding-and-verification.md`'s existing required order) for a
given repository's branch:

```bash
git -C <repo> fetch origin
git -C <repo> checkout <default-branch>
git -C <repo> merge --ff-only "origin/<default-branch>"
git -C <repo> merge --ff-only "<change-name>" \
  || (git -C <repo> checkout "<change-name>" \
      && git -C <repo> rebase <default-branch> \
      && git -C <repo> checkout <default-branch> \
      && git -C <repo> merge --ff-only "<change-name>")
```

The extra `merge --ff-only "origin/<default-branch>"` right after checkout
syncs local `<default-branch>` to whatever else has landed on `origin`
since the worktree was created (same reasoning as Decision 1's creation
step), *before* attempting the branch merge — otherwise the first ff-only
attempt could succeed against a stale local `<default-branch>` while
`origin/<default-branch>` has moved further, silently reintroducing the
same staleness Decision 1 fixes. The rebase fallback targets local
`<default-branch>` (already synced to origin by the line above), not
`origin/<default-branch>` directly, for the same reason.

This keeps history exactly as linear as the current 100%-direct-to-main
practice, whether or not `main` moved during the change. A genuine,
unresolvable rebase conflict is a normal merge-conflict-resolution
situation, not something this design needs to special-case — resolve it the
same way any rebase conflict is resolved, then continue.

Alternative considered: plain `git merge` (allowing merge commits).
Rejected per explicit user preference and to match existing history shape;
would also complicate any future `git bisect`/history reading with commits
that were never independently the tip of `main`.

**6. Cleanup after merge: manual, always.**

```bash
git -C <repo> worktree remove ".agents/worktrees/<change-name>"
git -C <repo> branch -d "<change-name>"
```

Run from the main tree, after `ExitWorktree({action: "keep"})` has returned
the session there (Decision 1 — `remove` is not valid for a `path`-entered
worktree). Do this per repository, once that repository's branch has merged
— a cross-repo change's repos may finish and merge at different times.

**7. `.gitignore`: add `.agents/worktrees/` in every affected repository.**

Verified empirically (see Context) that an un-ignored nested worktree shows
up as an untracked directory in the outer repo's `git status`. Every
repository that will host these worktrees needs one `.gitignore` line added
once, up front, as part of this change's own tasks — not per future change.

## Risks / Trade-offs

- [An affected repo has no `.agents/` directory yet (e.g. a repo that never
  adopted the shared skills/rules convention)] → `.agents/worktrees/` is
  still a valid path to create; it does not require `.agents/skills/` or
  `.agents/rules/` to already exist in that repo.
- [Operator forgets to pass `--cwd <worktree>` to a provider turn, so Codex
  edits the main tree instead] → Not automatically preventable by this
  design (it is a documentation/discipline convention, like the existing
  `--change` convention); mitigate by stating the requirement explicitly in
  the rule text and by habit — a wrong `--cwd` is immediately visible in
  `git status` of the wrong tree.
- [Rebase-then-ff-merge hits a real conflict] → Ordinary conflict
  resolution; not a failure of this workflow, just normal git history
  divergence. No special tooling needed.
- [A crashed/abandoned session leaves an orphaned worktree, like the three
  already found from the old coordinator] → Same shape of risk as before,
  not worse; `git worktree list` surfaces it for manual cleanup same as
  today. This design does not add automatic reaping (a "no automatic
  resolver/coordinator" project-wide decision, per `CLAUDE.md`).

## Migration Plan

Purely a rule-text and `.gitignore` change; see `tasks.md`. Nothing to
migrate for changes already merged (e.g. this session's `add-quant-
research-exec-command`, already committed directly to `main` before this
workflow existed) — the new workflow applies to changes started after this
one merges. No rollback concern beyond reverting the rule text and
`.gitignore` lines if abandoned.
