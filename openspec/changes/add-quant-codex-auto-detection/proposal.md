## Why

Quant research currently stores only the last manual Codex availability value,
so a long-running loop cannot distinguish an explicit override from a request
to keep detecting availability. This makes the loop easy to leave in stale
fallback mode after quota recovers.

## What Changes

- Add persistent `codex_mode=auto|manual` state alongside the resolved
  `codex_available` value, with atomic migration from the existing schema.
- Add `/quant:codex-auto` to enter persistent auto mode and probe immediately;
  every later `/quant-research` iteration probes again before selecting its
  backend.
- Add `/quant:codex-manual` to leave auto mode while retaining the last resolved
  availability. Existing `/quant:codex-on` and `/quant:codex-off` become
  explicit manual overrides.
- Add `/quant:codex-config` to inspect, update, or reset validated model and
  reasoning-effort profiles independently for availability probing,
  implementation, primary fixing, and eligible fix fallback. Claude remains
  the independent owner of verification and final verification.
- Reuse the existing deterministic Codex result classifier: successful probe
  enables Codex; explicit global quota exhaustion disables it; ambiguous,
  transient, model-local, authentication, network, and timeout outcomes leave
  the prior state unchanged and return a clear inconclusive result.
- Add offline Agent Contract coverage using a fake Codex executable; tests do
  not contact a real model service.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `quant-research-control`: expose persistent auto/manual detection mode,
  schema migration, per-iteration detection, and no-side-effect behavior.
- `codex-worker-policy`: allow a user-invoked, deterministically classified
  availability probe to re-enable future Codex selection without weakening
  global-quota or generic-rate-limit classification.

## Impact

- Affected repository: `finance-workspace` only.
- Affected surfaces: `.claude/commands/quant/`, quant state/probe and Codex
  phase-runner scripts, Agent Contract fixtures, and the two current
  specifications above.
- No trading strategy, execution, risk, market-data, deployment, or production
  behavior changes. The command only updates ignored local orchestration state.
- Rollback is a normal Git revert plus removal of the additive state field;
  explicit `codex-on`/`codex-off` commands remain available throughout rollout.
