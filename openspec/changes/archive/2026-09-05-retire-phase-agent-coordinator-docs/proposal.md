## Why

`tools/orchestrator/`'s SQLite coordinator, lease/fencing, account rotation,
operator-approval-question flow, and the `/ops:e2e`/`run-phase-agent`
lifecycle were deleted intentionally (commits `9b8d218`, `73a3a71`). The
shared docs that described how to operate that system were not deleted or
updated at the same time, violating this project's own "Task Completion and
Skill Upsert" rule ("If a used skill was misleading, incomplete, or
conflicted with actual repository behavior, correct it before closing the
task"). A read-through of every non-`openspec*` file under `.agents/rules/`
and `.agents/skills/`, plus `CLAUDE.md` itself, found:
- `.agents/rules/phase-agent-coordinator.md` describes only the deleted
  coordinator (SQLite WAL schema, fencing tokens, admission slots,
  session-local account rotation) — nothing in the repository implements any
  of it anymore.
- `.agents/rules/coding-and-verification.md`'s "Required order for a
  non-trivial change" mandates a `phase-agent PLAN → IMPLEMENT → VERIFY →
  FIX → FINAL_VERIFY` pipeline with no remaining mechanism to route
  `IMPLEMENT`/`FIX` to Codex automatically.
- `CLAUDE.md`'s "Working Model" section describes the same dead automatic
  routing and names `ORCHESTRATE = deterministic OPS shell state`, which no
  longer exists.
- `.agents/skills/quant-research-loop/SKILL.md` and its
  `references/playbook.md` (1830 lines) contain ~6 lines, in two spots,
  that describe the same deleted launcher/coordinator/`/ops:e2e` mechanism
  and directly contradict the current, already-rewritten
  `.claude/commands/quant/research.md` ("Không có launcher hay orchestrator
  riêng nào chạy nền cho vòng này nữa").
- The other 3 rules and 12 non-`openspec*` skills were read and found to
  contain no reference to the deleted machinery.

## What Changes

- Delete `.agents/rules/phase-agent-coordinator.md` — nothing in the current
  codebase implements what it describes, so keeping it only misleads a
  future reader into expecting a coordinator that does not exist.
- Rewrite `.agents/rules/coding-and-verification.md`'s "Required order for a
  non-trivial change" (and any other passage assuming automatic phase
  routing) to describe the current, actual practice: Claude plans and
  implements/verifies directly when asked, using `/opsx:*` for OpenSpec
  planning; there is no automatic Codex-routing coordinator to hand
  `IMPLEMENT`/`FIX` to. Keep everything else in the file unchanged (branch
  discipline, solo-maintainer exception, language-specific checks,
  completion evidence — none of it referenced the deleted system).
- Rewrite `CLAUDE.md`'s "Working Model" section (and the `Role boundary`
  block naming `ORCHESTRATE = deterministic OPS shell state`) to match: no
  automatic phase routing exists; Claude owns PLAN/VERIFY and is also the
  practical IMPLEMENT path today, absent a working Codex-routing mechanism.
  Leave the rest of `CLAUDE.md` (secrets rules, scope control, workspace
  topology) unchanged — none of it referenced the deleted system.
- Patch `.agents/skills/quant-research-loop/SKILL.md`'s "Core workflow" step
  1 and `references/playbook.md`'s "Round structure" step 1 and "Promotion
  and provider failover" heading/step 1, replacing the
  launcher/phase-agent-state/`/ops:e2e`/`run-phase-agent` language with what
  `.claude/commands/quant/research.md` already documents: round-file
  sequence is the sole iteration source of truth, and `PROMOTE` only creates
  an OpenSpec change via `/opsx:propose` and stops. Leave playbook.md steps
  2-5 of that same section unchanged — they describe local Docker testing,
  commit-to-main, push, and CI tracking, all still accurate.
- **Out of scope**: no change to any of the 3 other rules or 12 other
  skills already confirmed clean; no change to any runtime code (this is
  documentation/process content only, hence `skip_specs: true`); no
  reintroduction of any deleted coordinator/lease/launcher mechanism.

## Capabilities

### New Capabilities

(none — this changes shared process documentation, not a system capability)

### Modified Capabilities

(none — no `openspec/specs/` capability's requirements change; this is
docs-only, `skip_specs: true`)

## Impact

- Affected paths: `.agents/rules/phase-agent-coordinator.md` (deleted),
  `.agents/rules/coding-and-verification.md`, `CLAUDE.md`,
  `.agents/skills/quant-research-loop/SKILL.md`,
  `.agents/skills/quant-research-loop/references/playbook.md`.
- After editing, run `uv run --project tools/orchestrator sync-agent-links`
  so `.claude/rules/` drops its now-stale symlink to the deleted rule file
  (or errors clearly if it does not, prompting a manual `rm` — the tool
  never deletes a real file, but a dangling symlink to a since-deleted
  target is exactly the "stale link" case it does clean up).
- **Added mid-apply, approved by the user** (see `tasks.md` "5a. Added
  scope"): `AGENTS.md` and `README.md` had the same class of staleness
  (`agent-role-state`, `run-phase-agent-command`, `configure-agent-roles`,
  `/ops:e2e`, a per-role state file, `.kimi-code`/`.opencode` directories
  that no longer exist) and were corrected the same way.
  `.claude/commands/orchestrator/e2e.md` was found resurrected with its
  full pre-deletion coordinator content (see design.md's environment-anomaly
  risk) and was rewritten — not deleted, per the user's request — into a
  fast, stateless implementation command built on this session's own
  `codex-exec`/`claude-exec`, for quick or recurring tasks.
- No changes to `finance-mw`, `finance-web`, `finance-live-action`,
  `finance-broker`, `mt5`, or any runtime code — documentation only.
