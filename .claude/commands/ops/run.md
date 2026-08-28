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
- Never push or deploy before the final verification required by the
  persisted runtime `verification_mode` has passed.
- This workflow does not currently launch a Claude CLI worker. If an explicit
  future worker route does invoke the `claude` CLI, it must pass
  `--dangerously-skip-permissions`; this does not permit nested Claude in the
  existing fallback route.

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
   additional writable directory. IMPLEMENT defaults to `gpt-5.6-luna` with
   `high` reasoning. Every attempt passes its model and effort explicitly and
   uses `--dangerously-bypass-approvals-and-sandbox`, the installed CLI's
   supported equivalent of `--yolo`. It writes attempt-scoped JSONL, stderr,
   last-message, exit-code, and allowlisted metadata evidence to runtime logs,
   creates local commits when required, and never pushes.
   A nonzero exit, missing CLI, invalid repository, or timeout is a failed
   workflow; preserve evidence and move to `FAILED` or `BLOCKED`. If metadata
   reports `global-quota-exhausted`, the launcher has already invoked the
   quant state helper's `codex-off` operation for future transactions. Do not
   try another model, switch this transaction to Claude, or mutate its
   persisted backend. A generic HTTP 429 is `transient-rate-limit` and must
   never trigger automatic disable. Use centralized cleanup after recording
   the terminal class.
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

   Read the incremented round from runtime state and write the current
   verifier's exact P0/P1 findings before invoking any FIX worker:

   `.ops/changes/<change>/runtime/verification-findings-round-<round>.md`

   The file must be non-empty and contain only the current round's findings.
   Never reuse or concatenate an earlier round's artifact.

   `backend="$(./.agents/scripts/ops-runtime.sh route <change> <session-id> FIX)"`

   Route `codex` to `run-codex-phase.sh`. Route `claude-fallback` to the
   current top-level Claude session using the same no-nested-session rule.

   The helper increments the fix round and enters `FIX` atomically. Codex FIX
   defaults to `gpt-5.6-terra` with `high` reasoning. Only
   `model-unavailable` or `model-specific-limit` may launch one
   `gpt-5.6-sol` fallback attempt; it reuses the same findings file and remains
   in the same FIX round. Global quota, generic 429, auth, network, timeout,
   implementation, and unknown failures never use Sol. It
   mechanically enforces `OPS_MAX_FIX_ROUNDS` (default `3`); an attempted
   fourth fix marks the workflow `BLOCKED` and releases owned
   locks. Return to `VERIFY`. P2/P3 items must not silently become release
   blockers unless the approved change requires it.
4. When no P0/P1 findings remain, set `FINAL_VERIFY`, read the persisted
   `verification_mode`, and apply exactly its evidence gate. Do not re-read
   quant availability or switch backend:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> FINAL_VERIFY`

   For `verification_mode=independent`, preserve maker/checker separation:
   Claude independently re-reads the actual diff and evidence after Codex
   IMPLEMENT/FIX. Release is allowed only after this independent final
   verification passes.

   For `verification_mode=claude-fallback-self-review`, the current top-level
   Claude session performs enhanced final self-review. Freshly re-read the
   actual and committed diff, check every OpenSpec acceptance criterion, and
   verify every applicable repo-local test, lint, typecheck, static-analysis,
   build, migration/schema, trading-invariant, scope, secret/security, CI,
   exact pushed/deployed revision, and production-behavior requirement. Do not
   require inapplicable checks and never invent evidence. Record explicitly:

   `verification mode: claude-fallback-self-review`
   `independent maker/checker verification: NOT AVAILABLE`

   Fallback may release when enhanced final self-review passes and all
   applicable objective evidence passes; never present it as independent
   review. If either mode lacks required evidence, move to `BLOCKED`. If
   FINAL_VERIFY exposes a
   P0/P1 implementation defect, use the existing atomic `fix` operation and
   the same persisted backend, then return through VERIFY and FINAL_VERIFY.

## RELEASE, DEPLOY_VERIFY, ARCHIVE

1. For a change explicitly scoped for delivery, set `RELEASE` and follow the
   ownership-aware interface:

   `./.agents/scripts/ops-runtime.sh phase <change> <session-id> RELEASE`

   Enter RELEASE only after the final verification gate selected by the
   persisted `verification_mode` has passed. Both valid modes may continue
   when their own required evidence is satisfied. Then follow repository
   delivery rules: local checks, commit, push, GitHub Actions,
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

Do not claim completion unless the persisted verification mode, runtime state,
OpenSpec validation, local checks, and all applicable CI/deployment evidence
support the claim. For fallback, always disclose that independent
maker/checker verification was not available.
