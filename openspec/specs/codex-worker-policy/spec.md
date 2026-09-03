# codex-worker-policy Specification

## Purpose

Defines Codex as a bounded provider adapter within provider-neutral Finance phase routing, with deterministic classification, safe evidence, and no hidden fallback policy.

## Requirements

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

### Requirement: FIX fallback is narrow and stays in the same round

The generic resolver SHALL advance through ordered FIX candidates only after a
terminal `model-unavailable`, `model-specific-limit`, `global-quota-exhausted`,
or `auth-error` classification. Provider adapters SHALL NOT perform hidden
fallback. Candidate advancement SHALL preserve the current FIX round and exact
current-round findings. Implementation, transient-rate-limit, network,
timeout, and unknown failures SHALL not be treated as quota/model fallback.

#### Scenario: Terra unavailable falls back to Sol

- **WHEN** Terra reports model-specific unavailability and Sol is the next eligible candidate
- **THEN** Sol starts a new attempt in the same FIX round through the generic resolver

#### Scenario: Ordinary implementation failure does not fall back

- **WHEN** a FIX candidate reports an implementation failure
- **THEN** no replacement candidate is launched

#### Scenario: Both FIX models are unavailable

- **WHEN** consecutive Codex FIX models report model-local unavailability
- **THEN** the resolver may select the next eligible provider candidate without disabling Codex globally or changing the FIX round

### Requirement: Result classification is deterministic and quota-safe

Every Codex attempt SHALL produce exactly one of `success`,
`global-quota-exhausted`, `model-unavailable`, `model-specific-limit`,
`transient-rate-limit`, `auth-error`, `network-error`, `timeout`,
`implementation-error`, or `unknown-error`. Classification SHALL prefer
structured error codes and categories over stable message patterns. Generic
HTTP 429 or transient-rate-limit evidence SHALL NOT be classified as global
quota exhaustion.

#### Scenario: Explicit global quota is recognized

- **WHEN** structured or stable explicit evidence states that account-wide Codex quota is exhausted
- **THEN** the attempt is classified `global-quota-exhausted`

#### Scenario: Generic 429 remains transient

- **WHEN** evidence reports HTTP 429 or rate limiting without explicit global quota exhaustion
- **THEN** the attempt is classified `transient-rate-limit`

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

### Requirement: FIX consumes round-specific Claude findings

Before every FIX adapter invocation, orchestration SHALL require
`.ops/changes/<change>/runtime/verification-findings-round-<round>.md`. The FIX
prompt SHALL include only that exact current-round verifier findings file.
IMPLEMENT SHALL not require or inject findings, and every same-round candidate
continuation SHALL reuse the same file regardless of provider.

#### Scenario: Round one findings reach FIX

- **WHEN** FIX round one starts with its required findings artifact
- **THEN** every selected candidate prompt contains the round-one findings

#### Scenario: Findings remain isolated by round

- **WHEN** FIX advances from round one to round two
- **THEN** the round-two prompt contains round-two findings and does not inject round-one findings

### Requirement: Every attempt preserves safe evidence and metadata

Each Codex attempt SHALL preserve bounded stdout JSONL, stderr, last-message,
exit status, and result classification under an attempt-scoped evidence base.
The generic resolver SHALL append safe attempt metadata containing phase,
round, provider, model, effort, continuation, process identity, timestamps,
Git fingerprints, mutation status, result class, and relative evidence paths.
It SHALL NOT serialize prompts, credentials, environment dumps, or secret
values, and completed attempt records SHALL not be overwritten.

#### Scenario: Attempt metadata is complete

- **WHEN** any Codex attempt terminates
- **THEN** its evidence and append-only attempt record contain the required safe fields and matching classification

### Requirement: Worker policy tests are bounded and use fake CLIs

Agent Contracts CI SHALL exercise phase selection, permission flags, candidate
advancement, provider health, continuation, findings isolation, read-only
verification, safe metadata, and legacy transaction compatibility using fake
Codex and Claude executables under explicit timeouts. CI SHALL NOT contact real
model services.

#### Scenario: Worker policy contract suite passes

- **WHEN** Agent Contracts runs
- **THEN** all worker routing and failure-classification scenarios complete within the job timeout without contacting Codex or Claude services
