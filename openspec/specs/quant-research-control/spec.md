# quant-research-control Specification

## Purpose
Provides a safe, repeatable Claude Code entry point for one bounded quant research iteration while allowing the next scheduled iteration to observe whether Codex is available without restarting `/loop` or changing the research prompt.

## Requirements

### Requirement: Quant commands expose an explicit availability toggle

The workspace SHALL provide `/quant-research`, `/quant:codex-off`, and `/quant:codex-on` as Claude Code custom commands. The toggle commands SHALL update only the transient Codex availability state, SHALL NOT start or stop a loop, and SHALL report the resulting mode in Vietnamese without exposing raw runtime JSON by default.

#### Scenario: Disable Codex for future iterations

- **WHEN** a user invokes `/quant:codex-off`
- **THEN** the runtime state records `codex_available=false` and a fresh update timestamp, with no research iteration or loop restart started

#### Scenario: Re-enable Codex for future iterations

- **WHEN** a user invokes `/quant:codex-on` while a `/loop 20m /quant-research` schedule exists
- **THEN** the runtime state records `codex_available=true`, the existing loop remains active, and the next iteration can observe the new value

### Requirement: Runtime state updates are validated and atomic

The state helper SHALL maintain `schema_version`, boolean `codex_available`, boolean `research_enabled`, non-negative integer `iteration`, nullable timestamps, and atomic file replacement under `.ops/runtime/quant-research/state.json`. It SHALL reject malformed existing state without overwriting it and SHALL fail safely when another mutation holds the short-lived state lock.

#### Scenario: Initialize missing state

- **WHEN** the state helper runs `init` with no state file
- **THEN** it creates valid state with both availability and research enabled, iteration zero, and null run/update timestamps

#### Scenario: Refuse malformed state

- **WHEN** a mutation operation finds an existing state file that fails schema validation
- **THEN** it exits nonzero and leaves the malformed file unchanged

#### Scenario: Record one iteration

- **WHEN** the state helper runs `begin-iteration` on valid state
- **THEN** it increments `iteration` exactly once and writes UTC `last_run_at` and `updated_at` values atomically

### Requirement: A research command is exactly one state-aware iteration

`/quant-research` SHALL read the runtime state at the start of every invocation, record one iteration mechanically, and check `research_enabled` before expensive research. It SHALL not schedule another loop, sleep for the loop interval, recursively invoke Claude, or embed Codex quota state in the loop prompt.

#### Scenario: Intended recurring invocation

- **WHEN** a user configures recurring research
- **THEN** the documented invocation is `/quant:codex-off` followed by `/loop 20m /quant-research`, with quota state held in runtime state rather than loop arguments

#### Scenario: Research is disabled

- **WHEN** `/quant-research` observes `research_enabled=false`
- **THEN** it records the bounded iteration and skips new research/backtests without launching expensive work

#### Scenario: State changes between iterations

- **WHEN** a user runs `/quant:codex-on` after one loop iteration and before the next
- **THEN** the next `/quant-research` invocation reads the current state and uses normal Codex-available behavior without restarting the loop

### Requirement: Research policy preserves quant and safety constraints

Each enabled iteration SHALL respond in Vietnamese, prioritize XAU then BTC, treat other instruments as UI/backlog-only, require defensible OOS/holdout or walk-forward evidence before claiming improvement, allow a valid rejection/no-improvement result, limit exploratory work to at most two local strategy/service containers with bounded production-equivalent resources, and update the research report/handoff conventions without fabricating metrics or secrets.

#### Scenario: Normal Codex-available mode

- **WHEN** valid research produces an actionable candidate and `codex_available=true`
- **THEN** the command researches, backtests, validates unseen data, updates the CSV/research record, and hands off implementation without editing, committing, pushing, or deploying runtime code

#### Scenario: Codex fallback mode

- **WHEN** valid research produces a clearly scoped actionable candidate and `codex_available=false`
- **THEN** the command may request the existing `/ops:run` lifecycle with an explicit Claude-fallback backend, preserving locks, OpenSpec, tests, verification, release, deployment, archive, and DONE gates

#### Scenario: No false improvement

- **WHEN** no candidate beats the baseline on defensible unseen data
- **THEN** the iteration records the negative result and its evidence rather than manufacturing an improvement or cherry-picking metrics

### Requirement: Normal orchestration remains Codex-backed by default

The existing `/ops:run` command SHALL keep `implementation_backend=codex` as its default. Claude fallback SHALL require explicit quant context and a current state value of `codex_available=false`; the top-level Claude session SHALL implement directly in fallback mode and SHALL NOT launch a nested `claude`, `claude -p`, or other Claude CLI/session.

#### Scenario: Unrelated normal request

- **WHEN** a normal `/ops:run` request has no explicit fallback context
- **THEN** the implementation and FIX phases continue to use the Codex worker contract

#### Scenario: Fallback verification limitation

- **WHEN** the same top-level Claude session implements a fallback change
- **THEN** the handoff/report identifies verification as `claude-fallback-self-review` unless an actually independent supported reviewer performed the check

### Requirement: Repository contracts test the integration without a long loop

The repository SHALL provide bounded shell tests for state initialization/toggles/iteration/malformed-state safety and static command composition, and the Agent Contracts workflow SHALL run them alongside existing orchestration tests. Tests SHALL not start a real 20-minute loop or expose credentials.

#### Scenario: Contract suite passes

- **WHEN** the bounded state, quant command, and existing orchestration tests run in CI
- **THEN** all scripts, JSON settings, state transitions, command layout, default backend, and secret-safety assertions pass within the job timeout
