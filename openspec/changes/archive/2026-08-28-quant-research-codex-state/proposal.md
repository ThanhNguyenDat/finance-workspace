## Why

Recurring quant research needs to continue when Codex is temporarily unavailable without embedding stale quota text in a persistent `/loop` prompt. The workspace currently has `/ops:run`, but no Claude-native quant command, durable runtime toggle, or contract tests for this handoff boundary.

## What Changes

- Add `/quant-research`, `/quant:codex-off`, and `/quant:codex-on` Claude command files.
- Add a transient, schema-validated runtime state helper with atomic updates and a short-lived mutation lock.
- Keep normal `/ops:run` behavior Codex-backed while allowing an explicit Claude fallback backend only when the runtime state is off.
- Add shell contract/state tests, bounded CI execution, and concise README usage documentation.
- Preserve Vietnamese output, XAU-before-BTC research priority, honest OOS/holdout claims, research artifact conventions, and secret-safety constraints.

## Capabilities

### New Capabilities

- `quant-research-control`: Runtime-controlled quant research commands and the Codex availability/fallback contract.

### Modified Capabilities

- None.

## Impact

Only `finance-workspace` orchestration commands, scripts, tests, CI contract checks, README, and OpenSpec artifacts change. No Finance runtime repository, API, schema, migration, deployment, or production state changes are required.
