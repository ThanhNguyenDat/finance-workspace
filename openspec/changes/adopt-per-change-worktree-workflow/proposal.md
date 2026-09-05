## Why

`.agents/rules/coding-and-verification.md`'s "Solo-maintainer exception"
(confirmed 2026-08-19) says branch/PR ceremony is unnecessary for
`finance-mw`, `finance-broker`, `finance-live-action`, and `mt5` because
"this ecosystem has exactly one maintainer... a problem this project
doesn't have" (no concurrent writers). That assumption no longer holds: this
session ran a Codex `codex-exec` turn in the background with `--cwd`
pointed at the main working tree while Claude kept working in the same
directory, and Codex committed six files directly to `main` while Claude
was mid-turn on unrelated work. Two agents (or an agent and the operator)
now routinely write to the same tree concurrently — exactly the concurrency
the original exception assumed away.

## What Changes

- Adopt a per-OpenSpec-change git worktree workflow, replacing direct-to-main
  commits, across `finance-workspace`, `finance-mw`, `finance-broker`,
  `finance-live-action`, and `mt5`: every change (no exception for
  docs-only or single-file changes) gets its own worktree and branch from
  the moment its OpenSpec change is scaffolded until it is merged.
- Worktrees live at `.agents/worktrees/<change-name>` inside the repo being
  changed (not `.claude/worktrees/`, so the location is visible to and usable
  by Codex as well as Claude, matching this project's ".agents/ = canonical
  shared, .claude/ = Claude-native only" convention).
- Merging back to `main` prefers fast-forward; when `main` has advanced
  during the change, rebase the branch onto the latest `main` first, then
  fast-forward merge — preserving the fully linear history this ecosystem
  already has (zero merge commits in `finance-workspace`'s history today).
- After a successful merge, remove the worktree and delete its branch —
  nothing left over per change, unlike the several already-abandoned
  worktrees/branches found from the old (deleted) coordinator's per-attempt
  worktree allocation (see Impact).
- Update `.agents/rules/coding-and-verification.md`'s "Solo-maintainer
  exception" section to replace the direct-to-main guidance with this
  worktree-per-change workflow; the "push remains the release gate" and
  full verification-order requirements are unchanged.
- No source code changes. This is a process/workflow rule change with no
  system-level behavior to spec — `.openspec.yaml` sets `skip_specs: true`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None (process rule change; `skip_specs: true`).

## Impact

- `.agents/rules/coding-and-verification.md`: rewrite the "Solo-maintainer
  exception" section.
- Every affected repository's day-to-day workflow: creating a change now
  starts with a worktree, not a direct edit on `main`.
- Related but out of scope for this change: three already-abandoned
  worktrees/branches from the old deleted coordinator were found during
  exploration (`finance-live-action`: `codex/pending-backfill-orphans`,
  `codex/reweight-eligibility`; `mt5`: `codex/mt5-password-rotation`, all
  unmerged since ~2026-08-21/22, at the pre-existing sibling location
  `/home/lap17204/Desktop/finance/.worktrees/<repo>-<slug>`). This change
  does not clean those up or adopt their location convention; it establishes
  the new `.agents/worktrees/` convention going forward. Cleanup of the old
  ones is a separate, explicit decision for the operator.
