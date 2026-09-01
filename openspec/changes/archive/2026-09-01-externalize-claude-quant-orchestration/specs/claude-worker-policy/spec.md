## Purpose

Defines provider-neutral phase candidates and bounded Codex/Claude adapters so Finance orchestration can select, observe, and safely replace unavailable model workers.

## ADDED Requirements

### Requirement: Phase-agent profiles are provider-neutral and atomic

The workspace SHALL persist independent ordered candidates for
`quant_research`, `plan`, `implement`, `verify`, `fix`, and `final_verify`.
Each candidate SHALL identify a supported provider, safe model identifier, and
provider-valid effort. Updates, resets, pins, provider mode changes and health
changes SHALL be atomic and SHALL preserve unrelated profiles. Safe terminal
configuration SHALL not print raw state JSON. Explicit invocation environment
overrides SHALL take precedence over persisted profiles.

#### Scenario: Configure one phase independently

- **WHEN** an operator changes the first `verify` candidate
- **THEN** every other phase candidate list and provider-health record remains unchanged

#### Scenario: Reject unsafe candidate configuration

- **WHEN** an operator supplies an unknown phase/provider, unsafe model, unsupported effort, or Opus effort outside `medium|high`
- **THEN** configuration exits nonzero and leaves prior state unchanged

#### Scenario: Manual pin overrides automatic selection

- **WHEN** an operator pins a phase to an eligible provider candidate
- **THEN** automatic resolution uses that candidate until the phase returns to automatic mode

### Requirement: Provider adapters are bounded and auditable

Every provider adapter SHALL receive a resolved phase attempt, use an explicit
model and provider-native effort, enforce TERM/KILL timeout, preserve safe
attempt-scoped output/status/metadata, and never push. Claude invocations SHALL
pass `--dangerously-skip-permissions`; Codex invocations SHALL pass the
supported approval/sandbox bypass. VERIFY and FINAL_VERIFY SHALL be read-only
and SHALL fail if their process mutates a Git worktree.

#### Scenario: Claude candidate runs with required flags

- **WHEN** the resolver dispatches a Claude phase candidate
- **THEN** exactly one bounded Claude process receives the phase prompt, explicit model/effort, permission bypass, and no-persistence settings

#### Scenario: Codex candidate runs with required flags

- **WHEN** the resolver dispatches a Codex phase candidate
- **THEN** exactly one bounded Codex process receives the phase prompt, explicit model/reasoning effort, and supported full-auto bypass

#### Scenario: Verifier mutation is rejected

- **WHEN** a VERIFY or FINAL_VERIFY adapter changes either owned Git worktree
- **THEN** its attempt fails and release evidence cannot treat it as a passing review

### Requirement: Provider health uses deterministic evidence

Provider health SHALL support automatic and manual modes. Explicit
account/global quota exhaustion SHALL mark that provider unavailable. A
model-specific limit SHALL make the affected candidate ineligible before the
resolver considers another model. Authentication failure SHALL require manual
attention. Generic 429, timeout, network, implementation and unknown failures
SHALL NOT be recorded as global quota exhaustion. Automatic recovery SHALL use
at most one bounded probe after the configured cooldown and SHALL preserve the
prior state when the probe is inconclusive.

#### Scenario: Global quota opens provider circuit

- **WHEN** a provider adapter deterministically reports account/global quota exhaustion
- **THEN** future candidate resolution skips that provider until manual recovery or a successful eligible auto probe

#### Scenario: Generic rate limit preserves quota state

- **WHEN** an adapter reports a generic 429 without account/global quota evidence
- **THEN** the provider is not marked globally unavailable

#### Scenario: Automatic probe detects recovery

- **WHEN** an unavailable automatic provider reaches its probe time and the bounded probe succeeds
- **THEN** provider health becomes available and later phase resolution may select it

#### Scenario: Inconclusive probe starts a new cooldown window

- **WHEN** a probe-eligible automatic provider returns an inconclusive result
- **THEN** availability and reason remain unchanged while the next probe time advances by one bounded cooldown

### Requirement: Provider tests never contact model services

Agent Contracts SHALL exercise profile isolation, provider modes, cooldown,
classification, CLI flags, timeouts, read-only guards and safe metadata using
fake provider executables under explicit timeouts. Tests SHALL NOT contact a
real Claude or Codex service.

#### Scenario: Offline provider contracts pass

- **WHEN** Agent Contracts runs
- **THEN** every provider state and adapter scenario completes within the job timeout using only fake executables

#### Scenario: Nested contract execution is hermetic

- **WHEN** Agent Contracts runs inside a phase-agent process with inherited orchestration variables
- **THEN** each suite clears the outer attempt context before constructing its isolated fake-provider fixture
