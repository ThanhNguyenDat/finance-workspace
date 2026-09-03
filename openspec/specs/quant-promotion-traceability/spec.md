# quant-promotion-traceability Specification

## Purpose
Defines when defensible quant research becomes engineering work and preserves one traceable identity from research evidence through OpenSpec, OPS, delivery, and archive.

## Requirements

### Requirement: Promotion requires an actionable evidence gate

A quant iteration SHALL classify its result as exactly one of `REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, `NEEDS-MORE-RESEARCH`, or `PROMOTE`. Only `PROMOTE` SHALL enter engineering orchestration, and it SHALL require applicable OOS, holdout, or walk-forward evidence; an implementation-worthy improvement or concrete defect; clear affected repositories, expected behavior, and acceptance criteria; understood risk and trading-safety implications; and an understood rollback approach when applicable. The gate SHALL NOT weaken evidence thresholds merely to create work.

#### Scenario: Rejected candidate remains research-only
- **WHEN** a candidate is rejected, fails unseen-data evidence, or needs more research
- **THEN** the iteration records research evidence without creating an OpenSpec change or OPS transaction

#### Scenario: Actionable candidate is promoted
- **WHEN** every applicable promotion criterion passes and the result is `PROMOTE`
- **THEN** the iteration creates or reuses a scoped OpenSpec change before entering OPS

### Requirement: Promoted work has one stable change identity

A promoted candidate SHALL derive one meaningful kebab-case change name and SHALL use it unchanged in `openspec/changes/<change>/` and `.ops/changes/<change>/`. OpenSpec SHALL own why, behavior, design, acceptance criteria, affected repositories, safety impact, and implementation tasks. OPS SHALL own phase, backend, verification mode, locks, findings, worker evidence, and execution status. The quant command SHALL reuse the canonical OPS lifecycle and SHALL NOT duplicate its PLAN, IMPLEMENT, VERIFY, FIX, RELEASE, DEPLOY_VERIFY, ARCHIVE, or DONE state machine.

#### Scenario: Same identity crosses planning and execution
- **WHEN** a candidate named `improve-xau-portfolio-sizing-v4` is promoted
- **THEN** planning uses `openspec/changes/improve-xau-portfolio-sizing-v4/` and execution uses `.ops/changes/improve-xau-portfolio-sizing-v4/`

#### Scenario: Existing OPS lifecycle is reused
- **WHEN** a promoted candidate enters implementation
- **THEN** execution follows `.claude/commands/ops/run.md` rather than a quant-specific lifecycle copy

### Requirement: Quant-origin OPS metadata is concise and immutable

During PLAN, a promoted transaction SHALL attach an immutable origin record
containing the stable change name, `origin=quant-research`, a positive research
iteration, a safe instrument identifier, and one or more repository-relative
research artifact paths. Artifacts SHALL be existing references under approved
`research/quant/rounds/`, `research/quant/studies/`,
`research/quant/audits/`, `research/quant/samples/`, or
`research/quant/reports/` locations and SHALL NOT be copied into OPS, contain
absolute/traversal paths, or serialize their contents. Origin metadata SHALL
contain no credentials, environment values, or secrets. After creation, only
an explicitly specified repository-wide artifact-root migration MAY rewrite
location fields; such a migration SHALL preserve every non-location field and
the identity and content of every referenced artifact.

#### Scenario: Valid origin metadata is attached

- **WHEN** the owning PLAN session records a promoted XAU candidate from
  iteration 87
- **THEN** OPS stores one immutable metadata record referencing its research
  note and metric history without duplicating either file

#### Scenario: Invalid or repeated metadata is rejected

- **WHEN** metadata has a non-positive iteration, unsafe instrument,
  missing/out-of-scope artifact, wrong session, non-PLAN phase, or an existing
  origin record
- **THEN** OPS exits nonzero and preserves existing state and metadata

#### Scenario: Artifact root is migrated

- **WHEN** a reviewed repository migration relocates every referenced artifact
  away from a retired root
- **THEN** location fields may be rewritten once while change identity, origin,
  iteration, instrument, artifact count, and artifact contents remain unchanged

### Requirement: Delivery and archive retain the trace chain

A completed promoted change SHALL be traceable from implementation commit and
CI/deployment evidence through the OPS archive, OpenSpec archive, and referenced
research evidence. OPS and OpenSpec archives SHALL retain references only;
research artifacts SHALL remain under `research/quant/` and SHALL NOT be
duplicated into archive directories.

#### Scenario: Completed promotion is auditable

- **WHEN** a promoted change completes its applicable lifecycle
- **THEN** its stable change name connects code, delivery evidence, OPS
  execution evidence, OpenSpec decisions/tasks, research artifacts, and quant
  metrics

### Requirement: Legacy handoff is non-authoritative

The former global agent handoff MAY remain only as preserved documentation
archive context and SHALL NOT exist as an active queue or own authoritative
`Todo`, `Processing`, `Dev-done`, `Verify`, or `Done` state. Historical entries
SHALL NOT be blindly converted into engineering transactions; independently
qualified active work SHALL use the normal promotion gate.

#### Scenario: Existing handoff history is preserved

- **WHEN** legacy entries include historical, research-only, obsolete, and
  active-looking records
- **THEN** they remain archived, non-authoritative context while OpenSpec tasks
  and OPS runtime/archive state provide current lifecycle truth

### Requirement: Promotion contracts are bounded and offline

Agent Contracts CI SHALL test research-only outcomes, promotion prerequisites, canonical OPS reuse, handoff demotion, stable change identity, origin metadata validation, backend preservation, and existing orchestration behavior with local fixtures and explicit timeouts. Tests SHALL NOT invoke a real research loop, backtest, Claude, Codex API, or production deployment.

#### Scenario: Promotion contract suite passes
- **WHEN** Agent Contracts runs for a promotion change
- **THEN** all promotion, trace, fallback, and regression assertions finish within the job timeout using only local fixtures
