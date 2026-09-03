## MODIFIED Requirements

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
