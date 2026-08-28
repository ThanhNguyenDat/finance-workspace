## Why

The quant command documents a Claude fallback but `/ops:run` still always dispatches the Codex worker, and the implementation backend is not persisted in transaction state. The generic worker also contains restrictions from the earlier documentation smoke test, so normal future changes could receive the wrong prompt contract.

## What Changes

- Persist `implementation_backend` and `verification_mode` in every new `.ops` transaction, defaulting to Codex/independent verification.
- Gate the Claude fallback to explicit quant context plus current `codex_available=false`, and route both IMPLEMENT and FIX from the persisted backend.
- Restore `run-codex-phase.sh` to a generic OpenSpec worker prompt.
- Add behavioral routing/state immutability tests and extend bounded Agent Contracts CI.
- Resolve the superseded smoke OpenSpec residue without changing quant strategy policy.

## Capabilities

### New Capabilities

- `ops-backend-routing`: Immutable transaction backend selection and IMPLEMENT/FIX routing for normal and quant-fallback workflows.

### Modified Capabilities

- None.

## Impact

Only `finance-workspace` runtime orchestration scripts, Claude command contract, shell tests, CI, OpenSpec/handoff evidence, and the README-level workflow documentation are affected. No trading runtime repository, strategy, API, database, deployment, or production state changes are required.
