# quant-research-control Specification

## Purpose
Provides a safe one-shot quant research entry point whose logical phase agent can select and recover Codex or Claude providers without duplicating iterations or weakening promotion gates.

## Requirements

### Requirement: Quant commands expose an explicit availability toggle

The workspace SHALL provide `/quant-research`, `/quant:codex-off`,
`/quant:codex-on`, `/quant:codex-auto`, and `/quant:codex-manual` as Claude Code
custom commands. The workspace SHALL also provide `/quant:codex-config` to
inspect, update, and reset role-specific Codex profiles. The availability and
configuration commands SHALL update only transient Codex
routing state, SHALL NOT start research or start, stop, or restart a loop, and
SHALL report the result in Vietnamese without exposing raw runtime JSON or probe
logs by default. `/quant:codex-auto` SHALL enter persistent auto mode and run one
bounded, non-mutating availability probe immediately. While auto mode remains
selected, every `/quant-research` iteration SHALL run the same probe before
selecting a backend. A successful probe SHALL set `codex_available=true`;
explicit global quota exhaustion SHALL set it to false; all other outcomes
SHALL retain the last resolved value and report an inconclusive result.
`/quant:codex-manual` SHALL leave auto mode without changing that resolved
value. `/quant:codex-on` and `/quant:codex-off` SHALL select manual mode and set
the resolved value explicitly. A Codex worker MAY record automatic
unavailability only after deterministic classification of explicit global
quota exhaustion. Generic HTTP 429, model-local limits, and other worker
failures SHALL NOT automatically disable Codex.

`/quant:codex-config` SHALL address `probe`, `implement`, `fix`, and
`fix-fallback` independently and SHALL NOT provide a Codex review profile;
VERIFY and FINAL_VERIFY SHALL remain independent Claude phases. It SHALL accept
only a non-empty safe model value and a reasoning effort in
`none|minimal|low|medium|high|xhigh`, update state atomically, and avoid printing
raw runtime JSON.

#### Scenario: Disable Codex for future iterations

- **WHEN** a user invokes `/quant:codex-off`
- **THEN** runtime state records `codex_mode=manual`, `codex_available=false`, and a fresh update timestamp, with no research iteration or loop restart started

#### Scenario: Automatically disable on explicit global quota

- **WHEN** a Codex worker or auto-mode probe deterministically classifies explicit global quota exhaustion
- **THEN** runtime state records `codex_available=false` for future transactions, preserves auto mode when it is selected, and does not change any active transaction backend

#### Scenario: Auto mode detects recovery

- **WHEN** a user invokes `/quant:codex-auto` and its bounded probe succeeds
- **THEN** runtime state records `codex_mode=auto` and `codex_available=true` without starting research or changing an existing loop

#### Scenario: Generic rate limit does not disable Codex

- **WHEN** a Codex worker reports HTTP 429 or a transient rate limit without explicit global quota evidence
- **THEN** the runtime state's `codex_available` value is not automatically changed

#### Scenario: Inconclusive auto probe preserves state

- **WHEN** an auto-mode probe encounters a generic rate limit, model-local limit, authentication failure, network failure, timeout, unavailable executable, implementation error, or unknown failure
- **THEN** it reports detection as inconclusive, preserves `codex_mode=auto` and the last resolved `codex_available` value, and a scheduled research iteration may continue with that last resolved value

#### Scenario: Re-enable Codex for future iterations

- **WHEN** a user invokes `/quant:codex-on` while a `/loop 20m /quant-research` schedule exists
- **THEN** runtime state records `codex_mode=manual` and `codex_available=true`, the existing loop remains active, and the next iteration can observe the new value

#### Scenario: Return to manual mode without changing availability

- **WHEN** a user invokes `/quant:codex-manual`
- **THEN** runtime state records `codex_mode=manual`, retains the last `codex_available` value, and later research iterations stop probing automatically

#### Scenario: Configure one worker role

- **WHEN** a user invokes `/quant:codex-config implement <model> <effort>` with valid values
- **THEN** only the implementation profile changes and the fix, fix-fallback, probe, mode, and resolved availability values remain unchanged

#### Scenario: Reset all role profiles

- **WHEN** a user invokes `/quant:codex-config reset all`
- **THEN** probe and implementation use Luna/high, primary fixing uses Terra/high, eligible fix fallback uses Sol/high, and routing mode and availability remain unchanged

### Requirement: Runtime state updates are validated and atomic

The state helper SHALL maintain `schema_version=2`, `codex_mode` constrained to
`auto` or `manual`, role-specific `codex_profiles` for probe, implementation,
primary fixing, and eligible fix fallback, boolean `codex_available`, boolean `research_enabled`, a
non-negative integer `iteration`, nullable timestamps, and atomic file
replacement under `.ops/runtime/quant-research/state.json`. It SHALL atomically
migrate a valid schema-version-1 state by deriving `codex_mode=manual` and
preserving every existing field. It SHALL reject malformed or unsupported
existing state without overwriting it and SHALL fail safely when another
mutation holds the short-lived state lock.

Each profile SHALL contain a validated non-empty model and one supported
reasoning effort. Profile mutations SHALL change only the selected profile and
SHALL preserve mode, availability, iteration, research, and timestamps except
for the mutation timestamp.

#### Scenario: Initialize missing state

- **WHEN** the state helper runs `init` with no state file
- **THEN** it creates valid state in manual mode with Codex and research enabled, iteration zero, and null run/update timestamps

#### Scenario: Migrate version-one state

- **WHEN** the state helper reads a valid schema-version-1 state
- **THEN** it atomically writes schema version 2 with `codex_mode=manual` while preserving availability, research, iteration, and timestamp values

#### Scenario: Refuse malformed state

- **WHEN** a mutation operation finds an existing state file that fails supported schema validation
- **THEN** it exits nonzero and leaves the malformed file unchanged

#### Scenario: Record one iteration

- **WHEN** the state helper runs `begin-iteration` on valid state
- **THEN** it increments `iteration` exactly once and writes UTC `last_run_at` and `updated_at` values atomically without changing detection mode or resolved availability

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

Each enabled iteration SHALL respond in Vietnamese, prioritize XAU then BTC,
treat other instruments as UI/backlog-only, require defensible OOS, holdout, or
walk-forward evidence before claiming improvement, allow a valid rejection or
no-improvement result, limit exploratory work to at most two local
strategy/service containers with bounded production-equivalent resources, and
update research notes, metric history, samples, and the research navigation
index under `research/quant/` without fabricating metrics or secrets. When a
candidate passes the promotion gate, the command SHALL create or reuse a scoped
OpenSpec change, attach concise research-origin references to the corresponding
OPS transaction, and enter the existing OPS lifecycle. It SHALL NOT create or
use a global handoff or ad-hoc request file as an engineering queue or source
of lifecycle truth.

#### Scenario: Normal Codex-available mode

- **WHEN** valid research produces a promoted actionable candidate and
  `codex_available=true`
- **THEN** the command records research evidence, creates or reuses OpenSpec,
  and enters a new OPS transaction with the normal Codex backend without
  implementing runtime code outside OPS

#### Scenario: Codex fallback mode

- **WHEN** valid research produces a promoted actionable candidate and
  `codex_available=false`
- **THEN** the command creates or reuses OpenSpec and enters the existing
  `/ops:run` lifecycle with the explicitly gated Claude-fallback backend,
  preserving locks, tests, verification, release, deployment, archive, and
  DONE gates

#### Scenario: No false improvement

- **WHEN** no candidate beats the baseline on defensible unseen data
- **THEN** the iteration records the negative result and its evidence rather
  than manufacturing an improvement, cherry-picking metrics, or opening
  engineering work

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
