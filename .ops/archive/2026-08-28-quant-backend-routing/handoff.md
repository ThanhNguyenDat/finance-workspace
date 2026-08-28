# quant-backend-routing

- Scope: finance-workspace orchestration only; no runtime repository or
  production change.
- Backend contract: new transactions persist `implementation_backend` and
  `verification_mode`; normal defaults to `codex`/`independent`, while the
  explicit quant fallback requires `claude-fallback quant-fallback` and
  `codex_available=false`.
- Routing: `ops-runtime.sh route` reads the persisted backend for IMPLEMENT
  and FIX. The Codex worker rejects non-Codex state; fallback remains in the
  current top-level Claude session and records self-review mode.
- Verification: bounded backend-routing, orchestration, quant-state, quant
  command-contract, strict OpenSpec, shell syntax, managed-link, and diff
  checks passed.
- Smoke residue: superseded failed OpenSpec change archived as
  `openspec/changes/archive/2026-08-28-finance-mw-dev-docs-smoke`; its `.ops`
  record remains terminal `FAILED` evidence. No production deployment.
- Next: final verification, native OpenSpec archive, commit, push, and CI
  tracking.
