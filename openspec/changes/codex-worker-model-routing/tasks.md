## 1. Deterministic Worker Policy

- [x] 1.1 Add a deterministic Codex result classifier in `finance-workspace` and verify all ten result classes, structured-code priority, explicit quota detection, and generic-429 safety with bounded shell tests.
- [x] 1.2 Update the generic Codex launcher with explicit phase models, `high` effort, operator overrides, the supported Codex permission-bypass flag, attempt-scoped evidence, and allowlisted atomic metadata; verify fake argv and metadata assertions pass.
- [x] 1.3 Implement FIX-only Terra-to-Sol same-round fallback and automatic `codex-off` only for global quota exhaustion; verify eligible, ineligible, both-unavailable, and quota scenarios with fake Codex.

## 2. Verification Handoff and Orchestration

- [x] 2.1 Require and inject exact current-round Claude findings for FIX while excluding them from IMPLEMENT and prior rounds; verify round-one, round-two, and fallback prompt tests pass.
- [x] 2.2 Update `/ops:run` worker/cleanup contracts and add `--dangerously-skip-permissions` to every in-scope Claude CLI launcher; verify static argv and backend-immutability tests pass.
- [x] 2.3 Preserve existing atomic FIX and gated `claude-fallback` behavior; verify the existing orchestration and backend-routing suites remain green.

## 3. Contracts and Documentation

- [x] 3.1 Add the bounded fake-CLI worker-policy suite to Agent Contracts CI and verify workflow syntax and timeout coverage.
- [x] 3.2 Document model routing, reasoning effort overrides, permission flags, fallback boundaries, quota disable semantics, findings artifacts, evidence metadata, backend immutability, and manual re-enable behavior; verify documentation contract assertions pass.

## 4. Validation and Delivery

- [x] 4.1 Run shell syntax checks, all bounded agent contract suites, strict OpenSpec validation, and the synchronization check; record only passing evidence.
- [x] 4.2 Perform the mandatory skill upsert review, updating only reusable guidance that changed, then re-run synchronization if needed.
- [x] 4.3 Commit and push the scoped `finance-workspace` changes to `main`, verify exact local/remote SHA equality and green required GitHub Actions, and do not deploy production.
