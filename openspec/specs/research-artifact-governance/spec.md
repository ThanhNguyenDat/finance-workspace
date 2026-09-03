# research-artifact-governance Specification

## Purpose
Defines durable, purpose-owned locations and lifecycle rules for Finance
research evidence after removal of the ambiguous repository-level `raw/` root.

## Requirements

### Requirement: Durable research uses a purpose-owned namespace

The workspace SHALL store quant research rounds, studies, audits, samples,
reports, and navigation state under `research/quant/`. Operational reviews and
legacy-only documents SHALL live under explicit `docs/` subdirectories. The
repository SHALL NOT use a top-level `raw/` directory as an active artifact
store, task queue, handoff, or scratch contract.

#### Scenario: New quant iteration records evidence

- **WHEN** a bounded quant iteration records a result and supporting metrics
- **THEN** its durable artifacts are written under the applicable
  `research/quant/` location and no `raw/` path is created

#### Scenario: Operational explanation is retained

- **WHEN** an explanation is reusable as an incident review, runbook, or
  supporting document
- **THEN** it is stored under the matching `docs/` location rather than mixed
  with quant evidence

### Requirement: Engineering work uses native OpenSpec and OPS ownership

Requirements, design, acceptance criteria, and implementation tasks SHALL be
owned by an OpenSpec change. Execution phase, findings, worker evidence, and
concise coordination SHALL be owned by the corresponding OPS transaction.
Ad-hoc request files and a global handoff SHALL NOT act as an engineering queue
or lifecycle source of truth.

#### Scenario: New non-trivial request is planned

- **WHEN** a request requires tracked planning or cross-cutting implementation
- **THEN** the agent uses the native `/opsx:*` workflow and the canonical OPS
  lifecycle instead of creating a request file under a scratch directory

#### Scenario: Research result is not promoted

- **WHEN** a research result is not classified `PROMOTE`
- **THEN** it remains research evidence without creating an OpenSpec change or
  OPS transaction

### Requirement: Migration preserves evidence and discoverability

The retirement migration SHALL preserve tracked artifact contents and Git
history through repository moves, update current references to their new
locations, and preserve user-owned untracked files without silently deleting
or overwriting them. Legacy documents that remain useful only as history SHALL
be marked non-authoritative in an explicit documentation archive.

#### Scenario: Tracked corpus is migrated

- **WHEN** the repository transitions away from `raw/`
- **THEN** every tracked source artifact has a deterministic destination and
  no tracked content is lost

#### Scenario: Untracked file occupies the legacy root

- **WHEN** migration finds an untracked user-owned file under `raw/`
- **THEN** it is preserved at a reviewed destination or the migration stops
  without deleting it

### Requirement: Platform-native integrations remain CLI-owned

The migration SHALL NOT hand-edit agent-native `/opsx:*` command
implementations or `openspec*` skills. Shared Finance rules, non-platform
skills, and project orchestration MAY reference native workflows but SHALL not
replace or duplicate their implementation.

#### Scenario: Shared guidance is updated

- **WHEN** a shared rule or Finance skill changes its artifact paths
- **THEN** native OpenSpec commands and platform-specific OpenSpec skills remain
  byte-for-byte unchanged
