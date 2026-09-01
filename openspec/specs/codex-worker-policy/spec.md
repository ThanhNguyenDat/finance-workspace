# codex-worker-policy Specification

## Purpose
Defines deterministic, auditable Codex worker selection and failure handling for Finance orchestration without weakening phase ownership or backend immutability.

## Requirements

### Requirement: Worker phases select explicit role-specific profiles

Every Codex worker attempt SHALL pass an explicit model and reasoning effort.
The phase runner SHALL resolve the persisted `implement` profile for IMPLEMENT,
the `fix` profile for primary FIX, and the `fix_fallback` profile only for an
eligible FIX fallback. Defaults SHALL remain Luna/high, Terra/high, and Sol/high
respectively. Explicit phase-runner environment overrides SHALL take precedence
over persisted profiles. The availability detector SHALL use only the `probe`
profile. VERIFY and FINAL_VERIFY SHALL remain independent Claude phases and
SHALL NOT be routed through a Codex review profile. Every Codex worker attempt
SHALL use the installed CLI's supported bypass-approval-and-sandbox flag; every
Claude CLI worker invocation in the same orchestration scope SHALL use
`--dangerously-skip-permissions`.

#### Scenario: IMPLEMENT uses Luna high
- **WHEN** a Codex-backed transaction invokes IMPLEMENT without overrides
- **THEN** the worker argv explicitly selects `gpt-5.6-luna`, `high`, and the supported Codex permission-bypass flag

#### Scenario: FIX uses Terra high
- **WHEN** a Codex-backed transaction invokes FIX without overrides
- **THEN** the first attempt explicitly selects `gpt-5.6-terra`, `high`, and the supported Codex permission-bypass flag

#### Scenario: Configured FIX fallback is isolated
- **WHEN** primary FIX is eligible for fallback and no environment override is present
- **THEN** attempt two uses both the persisted fix-fallback model and effort without changing the primary FIX or IMPLEMENT profiles

#### Scenario: Verification remains independent
- **WHEN** IMPLEMENT or FIX succeeds
- **THEN** the next required VERIFY or FINAL_VERIFY phase is executed by Claude rather than a configured Codex profile

#### Scenario: Claude worker bypass is explicit
- **WHEN** orchestration launches a Claude CLI worker
- **THEN** its argv contains `--dangerously-skip-permissions`

### Requirement: FIX fallback is narrow and stays in the same round

The worker SHALL retry a failed primary FIX attempt with Sol only when deterministic classification reports `model-unavailable` or `model-specific-limit`. It SHALL NOT use Sol for global quota exhaustion, transient rate limits, authentication, network, timeout, implementation, or unknown failures. A Sol fallback SHALL remain an additional attempt in the current FIX round and SHALL NOT increment the orchestration round.

#### Scenario: Terra unavailable falls back to Sol
- **WHEN** Terra reports a model-specific unavailable or limit condition during FIX
- **THEN** Sol runs as attempt two with `fallback_from` identifying Terra and the persisted FIX round is unchanged

#### Scenario: Ordinary implementation failure does not fall back
- **WHEN** Terra reports an implementation failure
- **THEN** no Sol attempt is launched

#### Scenario: Both FIX models are unavailable
- **WHEN** Terra and then Sol report model-local unavailable conditions
- **THEN** FIX exits nonzero without disabling global Codex availability

### Requirement: Result classification is deterministic and quota-safe

Every attempt SHALL produce exactly one of `success`, `global-quota-exhausted`, `model-unavailable`, `model-specific-limit`, `transient-rate-limit`, `auth-error`, `network-error`, `timeout`, `implementation-error`, or `unknown-error`. Classification SHALL prefer structured error codes and categories over stable message patterns. Generic HTTP 429 or transient rate-limit evidence SHALL NOT be classified as global quota exhaustion.

#### Scenario: Explicit global quota is recognized
- **WHEN** structured or stable explicit evidence states that account-wide Codex quota is exhausted
- **THEN** the attempt is classified `global-quota-exhausted`

#### Scenario: Generic 429 remains transient
- **WHEN** evidence reports HTTP 429 or rate limiting without explicit global quota exhaustion
- **THEN** the attempt is classified `transient-rate-limit`

### Requirement: Global quota disables only future Codex selection

On `global-quota-exhausted`, the worker SHALL atomically update resolved Codex
availability to false without changing the selected auto/manual mode, SHALL NOT
attempt another model, and SHALL exit nonzero so orchestration can perform
terminal cleanup. It SHALL NOT mutate the active transaction's persisted
backend. Re-enabling Codex SHALL require either an explicit manual on override
or a successful probe while auto mode is selected. Inconclusive probes SHALL
preserve the last resolved availability.

#### Scenario: Primary FIX exhausts global quota
- **WHEN** Terra reports global quota exhaustion
- **THEN** no Sol attempt runs, future quant transactions observe Codex disabled, and the active backend remains `codex`

#### Scenario: Fallback FIX exhausts global quota
- **WHEN** Sol reports global quota exhaustion after an eligible Terra fallback
- **THEN** future quant transactions observe Codex disabled and no additional model is attempted

#### Scenario: Successful auto probe re-enables future selection
- **WHEN** auto mode is selected, resolved availability is false, and the bounded probe succeeds
- **THEN** future transactions observe Codex enabled without changing any active transaction backend

### Requirement: FIX consumes round-specific Claude findings

Before every FIX worker invocation, orchestration SHALL require `.ops/changes/<change>/runtime/verification-findings-round-<round>.md`. The FIX prompt SHALL include only the exact current-round findings file. IMPLEMENT SHALL not require or inject a findings file, and a same-round model fallback SHALL reuse the same file.

#### Scenario: Round one findings reach FIX
- **WHEN** FIX round one starts with its required findings artifact
- **THEN** both the primary and any fallback attempt prompt contain the round-one findings

#### Scenario: Findings remain isolated by round
- **WHEN** FIX advances from round one to round two
- **THEN** the round-two prompt contains round-two findings and does not inject round-one findings

### Requirement: Every attempt preserves safe evidence and metadata

Each worker attempt SHALL preserve bounded stdout JSONL, stderr, last-message, and exit-code evidence and SHALL atomically write `codex-<phase>-round-<round>-attempt-<n>.meta.json`. Metadata SHALL contain only `worker`, `phase`, `round`, `attempt`, `model`, `reasoning_effort`, `fallback_from`, and `result_class`, and SHALL NOT contain prompts, credentials, environment dumps, or secret values.

#### Scenario: Attempt metadata is complete
- **WHEN** any Codex worker attempt terminates
- **THEN** its metadata file contains every required safe field and its result class matches the classifier output

### Requirement: Worker policy tests are bounded and use fake CLIs

Agent Contracts CI SHALL exercise model selection, permission flags, fallback eligibility, quota behavior, backend immutability, findings isolation, atomic FIX behavior, fallback guards, and metadata using fake Codex and Claude executables under explicit timeouts. CI SHALL NOT invoke real model workers.

#### Scenario: Worker policy contract suite passes
- **WHEN** Agent Contracts runs
- **THEN** all worker routing and failure classification scenarios complete within the job timeout without contacting Codex or Claude services
