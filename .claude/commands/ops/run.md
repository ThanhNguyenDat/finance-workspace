---
description: "Run the autonomous Claude-Codex Finance workflow"
---

Run a bounded, stateful implementation workflow for this request:

$ARGUMENTS

Invoke as `/ops:run "<request>"`.

Operate as the current top-level Claude session. Never invoke `claude`,
never recursively start another Claude session, and never treat a Codex
summary as independent verification.

## Contract

- Claude owns PLAN, VERIFY, ORCHESTRATE, and the final release decision.
- Codex owns IMPLEMENT, TEST, FIX, and change-related CI fixes.
- `/ops:*` is project orchestration. `/opsx:*` and native OpenSpec commands
  remain the CLI's native OpenSpec integration.
- Runtime state is transient under `.ops/changes/<change>/runtime/`; the
  concise handoff is `.ops/changes/<change>/handoff.md`.
- Never copy full tasks, CLI output, secrets, or credentials into handoff.
- Never push or deploy before independent final verification.

## PLAN

1. Reject an empty request. Derive one stable lowercase kebab-case change
   name. If that change already has an active runtime or lock, stop with
   BLOCKED rather than mixing sessions.
2. Run `./.agents/scripts/sync-agent-links.sh` first. Read `AGENTS.md`,
   `CLAUDE.md`, applicable `.agents/rules/`, relevant shared skills, the
   current specs, and the affected repository's local rules and skills.
   Treat `.agents/skills/openspec*` as Codex-native and do not sync or
   substitute them for Claude's native OpenSpec integration.
3. Inspect the affected repositories and identify ownership before planning.
   Do not put runtime application code in `finance-workspace`.
4. Use the native OpenSpec flow (normally `/opsx:propose`) to create or
   revise `openspec/changes/<change>/proposal.md`, `design.md`, `tasks.md`,
   and `specs/`. Keep the approved acceptance criteria in OpenSpec. Validate
   with the installed CLI, for example:

   `openspec validate <change> --strict --no-interactive`

5. Acquire the per-change lock before initialization so a second session
   cannot race the first session while it creates state:

   `./.agents/scripts/ops-runtime.sh lock <change> <session-id>`
   `./.agents/scripts/ops-runtime.sh init <change> <session-id>`
   `./.agents/scripts/ops-runtime.sh phase <change> PLAN 0`

   Use `CLAUDE_SESSION_ID` when available; otherwise create a unique local
   session id. Update the handoff with only current phase, affected repos,
   blocker/findings, next action, and verification evidence.

## IMPLEMENT, VERIFY, FIX

1. Set phase `IMPLEMENT` and invoke the bounded worker once per affected
   runtime repository, sequentially:

   `./.agents/scripts/run-codex-phase.sh <change> <repository> IMPLEMENT`

   The worker uses the installed `codex exec` interface, writes evidence to
   runtime logs, creates local commits when required, and never pushes.
   A nonzero exit, missing CLI, invalid repository, or timeout is a failed
   workflow; preserve evidence and move to `FAILED` or `BLOCKED`.
   Release the lock after recording the terminal state on every failure path.
2. Inspect the actual diff and local test/build/lint/typecheck evidence.
   Verify ownership, scope, API/contracts, migrations, security,
   observability, and trading invariants when applicable. Record concise
   findings in the handoff. Do not mark VERIFY complete from a worker claim.
3. For any P0/P1 finding, set `FIX`, increment the runtime round, and invoke
   the worker with `FIX`. Return to `VERIFY`. Allow at most three fix rounds;
   unresolved findings then become `BLOCKED`. P2/P3 items must not silently
   become release blockers unless the approved change requires it.
4. When no P0/P1 findings remain, set `FINAL_VERIFY` and repeat the critical
   evidence checks. A clean final verification is required before release.

## RELEASE, DEPLOY_VERIFY, ARCHIVE

1. For a change explicitly scoped for delivery, set `RELEASE` and follow the
   repository delivery rules: local checks, commit, push, GitHub Actions,
   deployment mechanism, and immutable revision tracking. CI or deployment
   failures return to the appropriate fix/verify loop; never paper over them.
   For a dev-only change, record that release was intentionally skipped.
2. Set `DEPLOY_VERIFY` only when deployment applies. Verify the exact deployed
   revision, health, and requested behavior through the authoritative path.
   Never claim production success from local checks alone.
3. Set `ARCHIVE`, validate/sync/archive the native OpenSpec change with the
   CLI's native integration, release the lock, and archive
   `.ops/changes/<change>` to the date-prefixed archive using the runtime
   helper. The helper finalizes the archived state as `DONE`. Preserve the
   handoff.
4. On design conflicts, missing contracts, duplicate-lock ownership, or any
   condition that cannot be verified safely, stop at `BLOCKED` and explain
   the evidence and required planning decision, then release the lock. Do not
   silently redesign.

Do not claim completion unless the runtime state, OpenSpec validation, local
checks, independent verification, and (when requested) CI/deployment evidence
all support the claim.
