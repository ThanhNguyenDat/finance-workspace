## MODIFIED Requirements

### Requirement: Quant commands expose an explicit availability toggle

The workspace SHALL provide safe terminal controls for automatic/manual
provider health and per-phase candidate configuration while preserving existing
Codex command aliases during migration. Controls SHALL not start research,
restart a process, expose raw runtime JSON/probe logs, or modify an active
attempt. Automatic mode SHALL use bounded provider-specific probes only when
probe-eligible; manual pin/on/off SHALL win until returned to automatic mode.

#### Scenario: Disable Codex for future iterations

- **WHEN** an operator manually disables Codex
- **THEN** future phase resolution skips Codex without interrupting an active attempt

#### Scenario: Automatically disable on explicit global quota

- **WHEN** a Codex or Claude worker deterministically classifies account/global quota exhaustion
- **THEN** shared provider health records that provider unavailable for future attempts

#### Scenario: Generic rate limit does not disable Codex

- **WHEN** any provider reports a generic 429 without explicit global quota evidence
- **THEN** its global availability is not automatically disabled

#### Scenario: Re-enable Codex for future iterations

- **WHEN** an operator manually re-enables Codex
- **THEN** later phase resolution may select Codex without scheduling or restarting research

#### Scenario: Auto mode detects recovery

- **WHEN** a probe-eligible automatic provider's bounded probe succeeds
- **THEN** state records it available without starting research

#### Scenario: Inconclusive auto probe preserves state

- **WHEN** an automatic probe has a generic 429, model-local limit, network, timeout, implementation or unknown result
- **THEN** the prior resolved availability is preserved

#### Scenario: Configure one worker role

- **WHEN** an operator changes one phase's candidate list
- **THEN** other phase profiles and verification candidates remain unchanged

### Requirement: Runtime state updates are validated and atomic

Quant state SHALL retain research enablement, non-negative iteration and
timestamps, while provider availability and phase profiles SHALL live in the
atomic phase-agent state. Migration SHALL import valid existing Codex/Claude
profiles and availability without changing research iteration values. Both
helpers SHALL reject malformed state without overwriting it and fail safely
under a live mutation lock.

#### Scenario: Initialize missing state

- **WHEN** both helpers initialize with no state files
- **THEN** they create valid research and phase-agent defaults with no iteration started

#### Scenario: Migrate version-one state

- **WHEN** migration reads supported legacy quant/provider state
- **THEN** it preserves research counters and imports provider profiles exactly once

#### Scenario: Refuse malformed state

- **WHEN** a mutation encounters state that fails schema validation
- **THEN** it exits nonzero and leaves that file unchanged

#### Scenario: Record one iteration

- **WHEN** quant state runs `begin-iteration`
- **THEN** it increments the iteration exactly once and atomically updates timestamps

### Requirement: A research command is exactly one state-aware iteration

The canonical quant prompt SHALL run through one manually launched bounded
`quant_research` phase agent and return control to the terminal. It SHALL record
one iteration, check `research_enabled`, and classify the outcome as REJECTED,
NO-CHANGE, DATA-ISSUE, NEEDS-MORE-RESEARCH or PROMOTE. If confirmed provider
quota interrupts processing, a replacement candidate MAY continue the same
iteration from preserved artifacts but SHALL NOT increment it again. No entry
point SHALL schedule a loop, daemon, sleep or unbounded retry.

#### Scenario: Intended recurring invocation

- **WHEN** an operator wants a research iteration
- **THEN** the documented terminal launcher runs one bounded phase-agent invocation and returns after it terminates

#### Scenario: Research is disabled

- **WHEN** the selected research worker observes `research_enabled=false`
- **THEN** it records the iteration and skips expensive research/backtests

#### Scenario: State changes between iterations

- **WHEN** provider profiles or health change after one terminal invocation
- **THEN** the next invocation resolves current state without retaining a model session

#### Scenario: Non-promoted iteration has no engineering side effect

- **WHEN** an iteration is classified as anything other than PROMOTE
- **THEN** it records research evidence without requiring a new OpenSpec change or OPS transaction

#### Scenario: Quota interrupts research

- **WHEN** a research provider exhausts global quota after the iteration has begun
- **THEN** any eligible continuation candidate uses the same iteration and existing artifacts rather than starting a new iteration

#### Scenario: Concurrent terminal launch is rejected

- **WHEN** one terminal quant iteration already owns the research lease
- **THEN** another launcher exits before incrementing iteration state or starting a provider process

### Requirement: Research policy preserves quant and safety constraints

Each enabled iteration SHALL preserve the existing instrument priority,
unseen-data, resource, evidence, promotion and secret-safety requirements. A
PROMOTE result SHALL create or reuse one scoped OpenSpec change, attach concise
origin references, and enter OPS using phase-agent routing. Provider
availability SHALL affect candidate selection only and SHALL NOT weaken any
promotion, lock, test, verification, release, deployment, archive or DONE gate.

#### Scenario: Normal Codex-available mode

- **WHEN** valid research promotes a candidate and preferred phase candidates are available
- **THEN** OPS resolves each phase normally without implementation outside the lifecycle

#### Scenario: Codex fallback mode

- **WHEN** a preferred provider is unavailable during a promoted transaction
- **THEN** the next eligible phase candidate may run while preserving every lifecycle and evidence gate

#### Scenario: No false improvement

- **WHEN** no candidate beats the baseline on defensible unseen data
- **THEN** the iteration records the negative result instead of manufacturing improvement or engineering work

### Requirement: Normal orchestration remains Codex-backed by default

OPS SHALL use ordered phase-agent defaults rather than permanently assigning
one provider to each role. Defaults MAY continue to prefer Codex for
IMPLEMENT/FIX and Claude for planning/verification, but manual overrides and
deterministic provider health SHALL allow eligible alternatives per attempt.
No fallback SHALL bypass process isolation or verification gates.

#### Scenario: Unrelated normal request

- **WHEN** normal OPS starts with healthy default providers and no override
- **THEN** each phase uses its first configured candidate

#### Scenario: Fallback verification limitation

- **WHEN** mutation and verification resolve to the same provider
- **THEN** handoff reports same-provider process separation rather than provider independence

### Requirement: Repository contracts test the integration without a long loop

The repository SHALL provide bounded tests for state migration, provider
selection/health, one-iteration semantics, interrupted continuation, promotion
traceability, stable OpenSpec/OPS identity and routing evidence. Agent Contracts
SHALL not launch a real model, loop, backtest or production deployment.

#### Scenario: Contract suite passes

- **WHEN** bounded quant, phase-agent, provider and orchestration tests run in CI
- **THEN** all state, classification, continuation, trace, timeout, lock and secret-safety assertions pass within the job timeout
