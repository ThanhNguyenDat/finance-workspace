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
- `implementation_backend=codex` is the default for every normal request.
  Only an explicit quant-research fallback context, after the current runtime
  state reports `codex_available=false`, may use
  `implementation_backend=claude-fallback`; never infer this from prompt text.
- Claude fallback is performed by this top-level Claude session and must never
  launch a nested Claude CLI/session. Record
  `verification_mode=claude-fallback-self-review` when the same session
  implements and verifies.
- `/ops:*` is project orchestration. `/opsx:*` and native OpenSpec commands
  remain the CLI's native OpenSpec integration.
- Runtime state is transient under `.ops/changes/<change>/runtime/`; the
  concise handoff is `.ops/changes/<change>/handoff.md`.
- Never copy full tasks, CLI output, secrets, or credentials into handoff.
- Never push or deploy before independent final verification.

## PLAN

1. Reject an empty request and derive one stable lowercase kebab-case change
   name. Do not inspect, sync, or write any change-specific file before the
   change lock is acquired. If that change already has an active runtime or
   lock, stop with `BLOCKED` rather than mixing sessions.
2. Acquire the per-change lock and select the implementation backend once at
   transaction start. Normal requests use Codex. Only an explicit quant
   research fallback request may use Claude fallback, and only when the
   current quant state reports `codex_available=false`. Initialize runtime
   state as `PLAN` before any change-specific planning write:

   `./.agents/scripts/ops-runtime.sh lock <change> <session-id>`
   `./.agents/scripts/ops-runtime.sh init <change> <session-id>`

   For the explicitly gated quant fallback only, use:

   `./.agents/scripts/ops-runtime.sh init <change> <session-id> claude-fallback quant-fallback`

   The initializer persists `implementation_backend` and
   `verification_mode`; never use a later setter or re-read quant state to
   switch an active transaction.

   Use `CLAUDE_SESSION_ID` when available; otherwise create a unique local
   session id. The initial handoff is created by `init`; keep later updates
   concise.
3. Run `./.agents/scripts/sync-agent-links.sh`, then read `AGENTS.md`,
   `CLAUDE.md`, applicable `.agents/rules/`, relevant shared skills, current
   specs, and affected repository instructions. This discovery must remain
   read-only. Treat `.agents/skills/openspec*` as Codex-native and use only
   Claude's native OpenSpec integration for OpenSpec operations.
4. Identify every affected runtime repository without modifying it. Do not
   put runtime application code in `finance-workspace`. Acquire all affected
   repository locks before any OpenSpec or implementation-repository write;
   the helper canonicalizes and sorts paths and releases partial ownership if
   any lock conflicts:

   `./.agents/scripts/ops-runtime.sh lock-repos <change> <session-id> <repo>...`
5. Use the native OpenSpec flow (normally `/opsx:propose`) to create or revise
   `openspec/changes/<change>/proposal.md`, `design.md`, `tasks.md`, and
   `specs/`. Keep acceptance criteria in OpenSpec. Validate with the installed
   CLI, for example:

   `openspec validate <change> --strict --no-interactive`

## IMPLEMENT, VERIFY, FIX

1. Set phase `IMPLEMENT` with the ownership-aware interface, then route from
   the persisted backend once per affected runtime repository, sequentially:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> IMPLEMENT`
   `backend="$(./.agents/scripts/ops-runtime.sh route <change> <session-id> IMPLEMENT)"`

   If `backend=codex`, invoke:

   `./.agents/scripts/run-codex-phase.sh <change> <repository> IMPLEMENT`

   If `backend=claude-fallback`, the current top-level Claude session performs
   the implementation directly under the same repository lock and OpenSpec,
   scope, test, and commit gates. Do not invoke `claude`, `claude -p`,
   `claude --print`, or any nested Claude session, and do not invoke the
   Codex worker. Record the persisted
   `verification_mode=claude-fallback-self-review`; do not claim independent
   maker/checker verification for this route.

   The worker mechanically verifies the current change/session owns the
   repository lock, then uses the installed `codex exec` interface with
   `finance-workspace` as primary cwd and the runtime repository as an
   additional writable directory. It writes evidence to runtime logs, creates
   local commits when required, and never pushes.
   A nonzero exit, missing CLI, invalid repository, or timeout is a failed
   workflow; preserve evidence and move to `FAILED` or `BLOCKED`.
   Release owned repository and change locks after recording the terminal state
   on every failure path, using the centralized cleanup helper when possible:

   `./.agents/scripts/ops-runtime.sh cleanup <change> <session-id> FAILED`
2. Set phase `VERIFY`, then inspect the actual diff and local
   test/build/lint/typecheck evidence:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> VERIFY`

   Verify ownership, scope, API/contracts, migrations, security,
   observability, and trading invariants when applicable. Record concise
   findings in the handoff. Do not mark VERIFY complete from a worker claim.
3. For any P0/P1 finding, enter `FIX` through the atomic ownership-aware
   operation before routing the selected backend with `FIX`:

   `./.agents/scripts/ops-runtime.sh fix <change> <session-id>`

   `backend="$(./.agents/scripts/ops-runtime.sh route <change> <session-id> FIX)"`

   Route `codex` to `run-codex-phase.sh`. Route `claude-fallback` to the
   current top-level Claude session using the same no-nested-session rule.

   The helper increments the fix round and enters `FIX` atomically. It
   mechanically enforces `OPS_MAX_FIX_ROUNDS` (default `3`); an attempted
   fourth fix marks the workflow `BLOCKED` and releases owned
   locks. Return to `VERIFY`. P2/P3 items must not silently become release
   blockers unless the approved change requires it.
4. When no P0/P1 findings remain, set `FINAL_VERIFY` and repeat the critical
   evidence checks:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> FINAL_VERIFY`

   A clean final verification is required before release.

## RELEASE, DEPLOY_VERIFY, ARCHIVE

1. For a change explicitly scoped for delivery, set `RELEASE` and follow the
   ownership-aware interface:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> RELEASE`

   Then follow repository delivery rules: local checks, commit, push, GitHub Actions,
   deployment mechanism, and immutable revision tracking. CI or deployment
   failures caused by an implementation change return through the fix/verify
   loop: classify the failure, run `fix`, invoke the persisted implementation
   backend, then set `VERIFY`,
   `FINAL_VERIFY`, and `RELEASE` again. The transition from `RELEASE` to
   `FIX` is owned by `fix`; do not jump directly to `VERIFY` or `IMPLEMENT`.
   For a dev-only change, record that release was intentionally skipped.
2. Set `DEPLOY_VERIFY` only when deployment applies:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> DEPLOY_VERIFY`

   Verify the exact deployed revision, health, and requested behavior through
   the authoritative path. If deployment verification exposes an
   implementation defect, classify it, run `fix`, invoke the persisted
   implementation backend, then return
   through `VERIFY`, `FINAL_VERIFY`, `RELEASE`, and `DEPLOY_VERIFY`. Do not
   jump directly to `VERIFY` or `RELEASE`. External or infrastructure
   blockers such as outages, unavailable platforms, expired credentials, or
   required manual approval become `BLOCKED` with evidence via cleanup; do
   not force a code fix.
3. Set `ARCHIVE`, validate/sync/archive the native OpenSpec change with the
   ownership-aware interface:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> ARCHIVE`

   the CLI's native integration, then use the single successful completion path:
   `./.agents/scripts/ops-runtime.sh complete <change> <session-id>`

   `complete` requires `ARCHIVE`, releases only owned repository/change locks,
   archives `.ops/changes/<change>`, and finalizes the archived state as
   `DONE`. Preserve the handoff.
4. On design conflicts, missing contracts, duplicate-lock ownership, or any
   condition that cannot be verified safely, stop at `BLOCKED` and explain
   the evidence and required planning decision, then run cleanup to release
   only this workflow's locks. Do not silently redesign.

Do not claim completion unless the runtime state, OpenSpec validation, local
checks, independent verification, and (when requested) CI/deployment evidence
all support the claim.
