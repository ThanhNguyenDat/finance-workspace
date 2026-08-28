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
- Delivery: commits `824c68a` and `ebb60ec` are on `main`; exact remote SHA
  verified as `ebb60ec1534310c55ca5e9bd5de1a3e427e2e1fd`.
- CI: Agent Contracts run `33183686571` passed all steps, including bounded
  backend routing and managed-link checks.
- Final: OpenSpec archived and runtime state finalized as `DONE`; no runtime
  repository or production deployment was involved.
