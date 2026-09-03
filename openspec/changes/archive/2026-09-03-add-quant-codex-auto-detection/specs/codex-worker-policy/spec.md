## MODIFIED Requirements

### Requirement: Codex model profiles are phase-specific

The Codex phase runner SHALL resolve the `implement` profile for IMPLEMENT, the
`fix` profile for the primary FIX attempt, and the `fix_fallback` profile only
for an eligible fallback. Persisted profiles SHALL override built-in defaults,
while explicit phase-runner environment overrides SHALL retain precedence.
The availability detector SHALL use only the `probe` profile. Every worker
attempt SHALL record its effective model and reasoning effort. VERIFY and
FINAL_VERIFY SHALL remain independent Claude phases and SHALL NOT be routed to
a Codex profile.

#### Scenario: Implementation uses only its profile

- **WHEN** an IMPLEMENT phase starts without an explicit environment override
- **THEN** the worker receives the persisted implementation model and effort and no fix profile value affects the invocation

#### Scenario: Eligible fix fallback uses its own effort

- **WHEN** primary FIX returns model-unavailable or model-specific-limit
- **THEN** the fallback invocation uses both the persisted fix-fallback model and its persisted fix-fallback effort

#### Scenario: Verification remains independent

- **WHEN** Codex completes IMPLEMENT or FIX successfully
- **THEN** the next required VERIFY or FINAL_VERIFY phase is executed by Claude rather than by any configured Codex profile

#### Scenario: IMPLEMENT uses Luna high

- **WHEN** the default IMPLEMENT policy selects Codex
- **THEN** argv explicitly selects `gpt-5.6-luna`, `high`, and the supported Codex permission bypass

#### Scenario: FIX uses Terra high

- **WHEN** the default FIX policy selects its first Codex candidate
- **THEN** argv explicitly selects `gpt-5.6-terra`, `high`, and the supported Codex permission bypass

#### Scenario: Configured FIX fallback is isolated

- **WHEN** an operator changes a later FIX candidate
- **THEN** no primary FIX, IMPLEMENT, or other phase candidate is changed

#### Scenario: Claude worker bypass is explicit

- **WHEN** orchestration selects a Claude candidate
- **THEN** its argv contains `--dangerously-skip-permissions`

### Requirement: Global quota disables only future Codex selection

On `global-quota-exhausted`, the worker SHALL atomically invoke the quant state
helper's `codex-off` operation, SHALL NOT attempt another model, and SHALL exit
nonzero so orchestration can perform terminal cleanup. It SHALL NOT mutate the
active transaction's persisted backend. When persistent auto mode is selected,
the global-quota result SHALL preserve that mode while updating the resolved
availability to false so a later iteration can detect recovery. Re-enabling
Codex SHALL require either an explicit `/quant:codex-on` override or a
successful probe while auto mode is selected. An inconclusive auto probe SHALL
NOT change the last resolved availability.

#### Scenario: Primary FIX exhausts global quota

- **WHEN** Terra reports global quota exhaustion
- **THEN** no Sol attempt runs, future quant transactions observe Codex disabled, and the active backend remains `codex`

#### Scenario: Fallback FIX exhausts global quota

- **WHEN** Sol reports global quota exhaustion after an eligible Terra fallback
- **THEN** future quant transactions observe Codex disabled and no additional model is attempted

#### Scenario: Successful auto probe re-enables future selection

- **WHEN** Codex is unavailable, auto mode is selected, and a bounded probe succeeds
- **THEN** future quant transactions observe Codex enabled without changing any active transaction backend

#### Scenario: Ambiguous probe cannot re-enable Codex

- **WHEN** auto mode is selected and a probe produces any result other than success or explicit global quota exhaustion
- **THEN** future quant transactions retain the last resolved Codex availability
