## MODIFIED Requirements

### Requirement: Backend remains immutable during a transaction

Once initialized, a transaction SHALL route implementation from its persisted backend and SHALL NOT re-read quant availability to switch backend during IMPLEMENT or FIX. A later quant toggle, including an automatic `codex-off` caused by explicit global quota exhaustion, SHALL affect only newly initialized transactions. Worker failure SHALL return control to the orchestrator for bounded terminal cleanup and SHALL NOT rewrite the active backend.

#### Scenario: Fallback transaction survives Codex re-enable

- **WHEN** a fallback transaction is initialized and the quant state later changes to `codex_available=true`
- **THEN** the active transaction remains `claude-fallback` for both IMPLEMENT and FIX routing

#### Scenario: Active Codex transaction survives automatic disable

- **WHEN** a Codex worker reports explicit global quota exhaustion and availability is automatically disabled
- **THEN** the active transaction remains `codex`, no Claude worker replaces it, and orchestration performs bounded terminal cleanup

#### Scenario: New transaction observes current state

- **WHEN** a new normal transaction is initialized after Codex is re-enabled
- **THEN** the new transaction uses the default `codex` backend

#### Scenario: New quant fallback transaction observes automatic disable

- **WHEN** a new explicitly gated quant transaction is initialized after automatic Codex disable
- **THEN** it may select `claude-fallback` without mutating any earlier transaction
