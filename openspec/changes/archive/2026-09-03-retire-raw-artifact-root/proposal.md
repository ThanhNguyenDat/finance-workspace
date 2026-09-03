## Why

The catch-all `raw/` root mixes authoritative quant evidence, reports, incident
notes, obsolete prompts, ad-hoc implementation requests, and a legacy handoff.
Its ambiguous ownership keeps old queue semantics alive and makes durable
research references depend on a directory explicitly described as scratch or
legacy in several artifacts.

## What Changes

- **BREAKING**: remove the repository-level `raw/` namespace after preserving
  tracked content under purpose-owned research, documentation, or archive
  locations.
- Introduce `research/quant/` as the durable home for quant rounds, audits,
  samples, reports, and the research navigation index.
- Route reusable incident reviews and operational explanations into `docs/`,
  and preserve legacy-only material in a clearly named documentation archive.
- Replace ad-hoc request/proposal files with native `/opsx:*` planning,
  implementation, verification, synchronization, and archive workflows.
- Update quant promotion origin validation to accept only the new research
  evidence roots while preserving concise reference-only OPS metadata.
- Update shared rules, skills, commands, tests, active planning references, and
  repository documentation without modifying agent-native `openspec*` skills
  or `/opsx:*` command implementations.
- Remove the legacy handoff as an active artifact; OpenSpec remains engineering
  truth and `.ops/changes/<change>/handoff.md` remains concise coordination
  truth.

## Capabilities

### New Capabilities

- `research-artifact-governance`: Defines purpose-owned storage, lifecycle,
  preservation, and discoverability for durable research and supporting
  evidence after removal of `raw/`.

### Modified Capabilities

- `quant-promotion-traceability`: Changes approved promotion-origin paths and
  the durable research location retained by completed trace chains.
- `quant-research-control`: Changes where each bounded iteration records its
  notes, metrics, samples, and navigation state.

## Impact

- Affected repository: `finance-workspace` only; no runtime application
  repository changes.
- Affected surfaces: tracked research/documentation paths, README and AGENTS
  guidance, shared rules and non-platform skills, quant and `/ops:run` Claude
  commands, OPS origin validation, Agent Contract fixtures, current OpenSpec
  references, and transient active origin metadata when safe to migrate.
- Agent-native `.claude/commands/opsx/*`, `.claude/skills/openspec*`, and
  `.agents/skills/openspec*` remain platform-owned and unchanged.
- No trading, broker, risk, execution, API, database, deployment, or production
  behavior changes. Existing research bytes and Git history are preserved by
  moves; rollback is a Git revert of the migration.
