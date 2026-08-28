## MODIFIED Requirements

### Requirement: Quant commands expose an explicit availability toggle

The workspace SHALL provide `/quant-research`, `/quant:codex-off`, and `/quant:codex-on` as Claude Code custom commands. The toggle commands SHALL update only the transient Codex availability state, SHALL NOT start or stop a loop, and SHALL report the resulting mode in Vietnamese without exposing raw runtime JSON by default. A Codex worker MAY invoke the same `codex-off` state operation automatically only after deterministic classification of explicit global quota exhaustion. Generic HTTP 429, model-local limits, and other worker failures SHALL NOT automatically disable Codex. Re-enable SHALL remain manual through `/quant:codex-on`.

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
