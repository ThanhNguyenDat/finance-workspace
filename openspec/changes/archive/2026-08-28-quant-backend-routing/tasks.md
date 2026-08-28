## 1. Runtime backend contract

- [x] 1.1 Extend `ops-runtime.sh init` with validated default/fallback backend and verification fields while preserving the old two-argument caller; verify malformed/ungated backend requests fail and new state is valid JSON.
- [x] 1.2 Add ownership-aware read-only IMPLEMENT/FIX route selection and Codex-worker backend guard; verify route output follows persisted state and does not change after quant toggles.

## 2. Worker and command integration

- [x] 2.1 Restore `run-codex-phase.sh` to a generic OpenSpec worker prompt with no smoke-specific wording; verify generic prompt markers and forbidden phrase checks.
- [x] 2.2 Update `.claude/commands/ops/run.md` to select backend once at init and route IMPLEMENT/FIX from persisted state without re-reading quant state mid-transaction; verify fallback has no nested Claude route and normal default remains Codex.

## 3. Tests, CI, and residue

- [x] 3.1 Add bounded behavioral backend-routing tests for default, gated fallback, immutability, invalid backend, Codex route, fallback route, and FIX preservation; verify no real agent/loop is launched.
- [x] 3.2 Extend Agent Contracts CI with backend test syntax/execution while keeping all existing orchestration, quant state, and quant command tests; verify job timeout remains bounded.
- [x] 3.3 Resolve or explicitly preserve only terminal failed smoke residue with concise evidence; verify no misleading active smoke OpenSpec change remains.

## 4. Verification and delivery

- [x] 4.1 Run all shell/OpenSpec/link/diff checks and review every acceptance criterion; verify no quant strategy policy changes were introduced.
- [ ] 4.2 Archive OpenSpec, commit scoped workspace files, push fast-forward to `main`, verify exact remote SHA, and track Agent Contracts success.
