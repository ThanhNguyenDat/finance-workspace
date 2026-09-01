# quant-research-control Specification

## Purpose
Provides a safe, repeatable Claude Code entry point for one bounded quant research iteration while allowing the next scheduled iteration to observe whether Codex is available without restarting `/loop` or changing the research prompt.

## Requirements

### Requirement: Quant commands expose an explicit availability toggle

The workspace SHALL provide `/quant-research`, `/quant:codex-off`,
`/quant:codex-on`, `/quant:codex-auto`, `/quant:codex-manual`, and
`/quant:codex-config` as Claude Code custom commands. These commands SHALL
update only transient Codex routing state, SHALL NOT start or stop a loop, and
SHALL report in Vietnamese without exposing raw runtime JSON or probe logs.
Auto SHALL probe immediately and before each later auto-mode research
iteration. Success SHALL resolve available, explicit global quota SHALL resolve
unavailable, and every ambiguous outcome SHALL preserve the prior resolved
value. On/off SHALL be manual overrides; manual SHALL preserve availability.
Config SHALL inspect, update, or reset `probe`, `implement`, `fix`, and
`fix-fallback` profiles independently and SHALL NOT expose a Codex review role.

#### Scenario: Disable Codex for future iterations

- **WHEN** a user invokes `/quant:codex-off`
- **THEN** the runtime state records `codex_available=false` and a fresh update timestamp, with no research iteration or loop restart started

#### Scenario: Automatically disable on explicit global quota

- **WHEN** a Codex worker deterministically classifies explicit global quota exhaustion
- **THEN** the runtime state records `codex_available=false` for future transactions without changing the active transaction backend

#### Scenario: Generic rate limit does not disable Codex

- **WHEN** a Codex worker reports HTTP 429 or a transient rate limit without explicit global quota evidence
- **THEN** the runtime state's `codex_available` value is not automatically changed

#### Scenario: Re-enable Codex for future iterations

- **WHEN** a user invokes `/quant:codex-on` while a `/loop 20m /quant-research` schedule exists
- **THEN** the runtime state records `codex_available=true`, the existing loop remains active, and the next iteration can observe the new value

#### Scenario: Auto mode detects recovery

- **WHEN** `/quant:codex-auto` runs and its bounded probe succeeds
- **THEN** state records `codex_mode=auto` and `codex_available=true` without starting research or restarting the loop

#### Scenario: Inconclusive auto probe preserves state

- **WHEN** auto detection encounters a generic 429, model-local limit, authentication, network, timeout, missing executable, implementation, or unknown failure
- **THEN** state remains in auto mode with the previous resolved availability and the research iteration may continue

#### Scenario: Configure one worker role

- **WHEN** `/quant:codex-config implement <model> <effort>` receives valid values
- **THEN** only the implementation profile changes and verification remains independently Claude-owned

### Requirement: Runtime state updates are validated and atomic

The state helper SHALL maintain `schema_version=2`, `codex_mode` constrained to
auto/manual, boolean `codex_available`, validated role-specific Codex profiles,
boolean `research_enabled`, non-negative integer `iteration`, nullable
timestamps, and atomic file replacement under
`.ops/runtime/quant-research/state.json`. It SHALL atomically migrate valid v1
state to manual mode with role defaults while preserving existing values. It
SHALL reject malformed or unsupported state without overwriting it and SHALL
fail safely when another mutation holds the short-lived state lock.

#### Scenario: Initialize missing state

- **WHEN** the state helper runs `init` with no state file
- **THEN** it creates valid state in manual mode with Codex and research enabled, role-specific defaults, iteration zero, and null run/update timestamps

#### Scenario: Migrate version-one state

- **WHEN** the state helper reads a valid schema-version-1 state
- **THEN** it writes schema version 2 in manual mode with default profiles while preserving availability, research, iteration, and timestamps

#### Scenario: Refuse malformed state

- **WHEN** a mutation operation finds an existing state file that fails schema validation
- **THEN** it exits nonzero and leaves the malformed file unchanged

#### Scenario: Record one iteration

- **WHEN** the state helper runs `begin-iteration` on valid state
- **THEN** it increments `iteration` exactly once and writes UTC `last_run_at` and `updated_at` values atomically

### Requirement: A research command is exactly one state-aware iteration

`/quant-research` SHALL read runtime state at the start of every invocation. In
auto mode it SHALL run exactly one bounded probe and re-read state; in manual
mode it SHALL skip probing. It SHALL then record one iteration mechanically,
check `research_enabled` before expensive research, and classify the result as
`REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, `NEEDS-MORE-RESEARCH`, or `PROMOTE`. It
SHALL not schedule another loop, sleep for the loop interval, recursively
invoke Claude, embed Codex quota state in the loop prompt, or create an OPS
transaction unless the result is `PROMOTE` and the promotion gate passes.

#### Scenario: Intended recurring invocation

- **WHEN** a user configures recurring research
- **THEN** the documented invocation may use `/quant:codex-auto` or an explicit manual override followed by `/loop 20m /quant-research`, with routing state held outside loop arguments

#### Scenario: Research is disabled

- **WHEN** `/quant-research` observes `research_enabled=false`
- **THEN** it records the bounded iteration and skips new research/backtests without launching expensive work

#### Scenario: State changes between iterations

- **WHEN** a user runs `/quant:codex-on` after one loop iteration and before the next
- **THEN** the next `/quant-research` invocation reads the current state and uses normal Codex-available behavior without restarting the loop

#### Scenario: Non-promoted iteration has no engineering side effect

- **WHEN** an iteration is classified as anything other than `PROMOTE`
- **THEN** it records research evidence without requiring a new OpenSpec change or OPS transaction

### Requirement: Research policy preserves quant and safety constraints

Each enabled iteration SHALL respond in Vietnamese, prioritize XAU then BTC, treat other instruments as UI/backlog-only, require defensible OOS/holdout or walk-forward evidence before claiming improvement, allow a valid rejection/no-improvement result, limit exploratory work to at most two local strategy/service containers with bounded production-equivalent resources, and update research notes, metric history, and the research navigation backlog without fabricating metrics or secrets. When a candidate passes the promotion gate, the command SHALL create or reuse a scoped OpenSpec change, attach concise research-origin references to the corresponding OPS transaction, and enter the existing OPS lifecycle. It SHALL NOT use `docs/archive/legacy-handoff-agent.md` as an engineering queue or source of lifecycle truth.

#### Scenario: Normal Codex-available mode

- **WHEN** valid research produces a promoted actionable candidate and `codex_available=true`
- **THEN** the command records research evidence, creates or reuses OpenSpec, and enters a new OPS transaction with the normal Codex backend without implementing runtime code outside OPS

#### Scenario: Codex fallback mode

- **WHEN** valid research produces a promoted actionable candidate and `codex_available=false`
- **THEN** the command creates or reuses OpenSpec and enters the existing `/ops:run` lifecycle with the explicitly gated Claude-fallback backend, preserving locks, tests, verification, release, deployment, archive, and DONE gates

#### Scenario: No false improvement

- **WHEN** no candidate beats the baseline on defensible unseen data
- **THEN** the iteration records the negative result and its evidence rather than manufacturing an improvement, cherry-picking metrics, or opening engineering work

### Requirement: Normal orchestration remains Codex-backed by default

The existing `/ops:run` command SHALL keep `implementation_backend=codex` as its default. Claude fallback SHALL require explicit quant context and a current state value of `codex_available=false`; the top-level Claude session SHALL implement directly in fallback mode and SHALL NOT launch a nested `claude`, `claude -p`, or other Claude CLI/session.

#### Scenario: Unrelated normal request

- **WHEN** a normal `/ops:run` request has no explicit fallback context
- **THEN** the implementation and FIX phases continue to use the Codex worker contract

#### Scenario: Fallback verification limitation

- **WHEN** the same top-level Claude session implements a fallback change
- **THEN** the handoff/report identifies verification as `claude-fallback-self-review` unless an actually independent supported reviewer performed the check

### Requirement: Repository contracts test the integration without a long loop

The repository SHALL provide bounded shell tests for state initialization/toggles/iteration/malformed-state safety, promotion and trace metadata, static command composition, handoff non-authority, stable OpenSpec/OPS identity, and preserved backend routing. Agent Contracts SHALL run them alongside existing orchestration and Codex worker tests without launching a real loop, model worker, backtest, or production deployment.

#### Scenario: Contract suite passes

- **WHEN** the bounded state, promotion, command, backend, worker, and existing orchestration tests run in CI
- **THEN** all state, classification, trace, source-of-truth, routing, timeout, and secret-safety assertions pass within the existing job timeout
