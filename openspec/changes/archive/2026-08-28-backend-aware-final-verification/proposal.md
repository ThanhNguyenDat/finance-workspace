## Why

The accepted backend routing contract persists a fallback self-review mode,
but `/ops:run` still globally requires independent final verification. This
contradiction prevents a valid Claude fallback transaction from reaching its
release/archive path, while a terminal failed smoke handoff also remains in
the active `.ops/changes` namespace.

## What Changes

- Make FINAL_VERIFY and completion gates depend on the persisted
  `verification_mode` without weakening the Codex independent-review path.
- Define enhanced objective self-review evidence for
  `claude-fallback-self-review` and prohibit independent maker/checker claims.
- Extend bounded contract/state tests for both verification modes and backend
  immutability through FINAL_VERIFY.
- Move the terminal failed smoke handoff from `.ops/changes` to `.ops/archive`
  while preserving its FAILED evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ops-backend-routing`: Make final verification and release eligibility
  verification-mode aware while retaining immutable backend pairs.

## Impact

Only `finance-workspace` Claude command documentation, shell contract tests,
OpenSpec artifacts, and `.ops` handoff placement are affected. No runtime
repository, trading policy, API, migration, deployment, or production state
changes are required. Rollback is a normal Git revert.
