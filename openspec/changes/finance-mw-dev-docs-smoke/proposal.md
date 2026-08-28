## Why

The first real `/ops:run` smoke test needs a small, low-risk implementation
target. `finance-mw` lacks a concise developer guide that connects its actual
local startup, dependencies, verification commands, and health endpoint.

## What Changes

- Add a concise developer-only section to the existing `finance-mw` developer
  documentation.
- Document only commands, configuration sources, dependencies, and health
  checks verified from the repository.
- Keep the change documentation-only with no runtime, API, schema, dependency,
  deployment, or production-setting changes.

## Capabilities

### New Capabilities

<!-- No spec-level capability: this is documentation-only. -->

### Modified Capabilities

<!-- No requirements change. -->

## Impact

- Affected repositories: `finance-workspace` for orchestration/OpenSpec state
  and `finance-mw` for one existing developer documentation file.
- No production runtime behavior, API, database, dependency, CI/CD, or
  deployment impact.
- No rollout or rollback is required beyond reverting the documentation
  commit if desired.
