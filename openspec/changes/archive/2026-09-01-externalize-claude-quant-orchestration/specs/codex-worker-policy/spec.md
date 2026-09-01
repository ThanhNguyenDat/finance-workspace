## MODIFIED Requirements

### Requirement: Worker phases select explicit role-specific profiles

Every Codex attempt SHALL receive the model and reasoning effort from the
candidate selected for `quant_research`, PLAN, IMPLEMENT, VERIFY, FIX, or
FINAL_VERIFY. Invocation-scoped provider/model/effort overrides SHALL take
precedence after the same safety validation as persisted candidates. Codex
SHALL use its supported approval-and-sandbox bypass; Claude adapters in the
same orchestration scope SHALL use `--dangerously-skip-permissions`. VERIFY and
FINAL_VERIFY SHALL remain read-only regardless of selected provider.

#### Scenario: IMPLEMENT uses Luna high

- **WHEN** the default IMPLEMENT policy selects Codex
- **THEN** argv explicitly selects `gpt-5.6-luna`, `high`, and the supported Codex permission bypass

#### Scenario: FIX uses Terra high

- **WHEN** the default FIX policy selects its first Codex candidate
- **THEN** argv explicitly selects `gpt-5.6-terra`, `high`, and the supported Codex permission bypass

#### Scenario: Configured FIX fallback is isolated

- **WHEN** an operator changes a later FIX candidate
- **THEN** no primary FIX, IMPLEMENT, or other phase candidate is changed

#### Scenario: Verification remains independent

- **WHEN** VERIFY or FINAL_VERIFY starts
- **THEN** it runs as a fresh read-only process and its actual provider relationship to the latest mutator is derived from evidence

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

On `global-quota-exhausted`, Codex health SHALL become unavailable atomically
without rewriting the completed attempt or changing automatic/manual phase
selection. After the old process exits, the current phase MAY continue through
the next eligible provider candidate. In automatic provider mode a successful
bounded probe after cooldown SHALL restore future eligibility; authentication
failure SHALL require manual attention. Inconclusive probes SHALL preserve the
previous availability.

#### Scenario: Primary FIX exhausts global quota

- **WHEN** the first Codex FIX candidate reports global quota exhaustion
- **THEN** future selection skips Codex and the current FIX round may continue through the next eligible non-Codex candidate

#### Scenario: Fallback FIX exhausts global quota

- **WHEN** a later Codex FIX candidate reports global quota exhaustion
- **THEN** no additional Codex model is selected while its circuit is open

#### Scenario: Successful auto probe re-enables future selection

- **WHEN** automatic Codex health is unavailable, cooldown has elapsed, and the bounded probe succeeds
- **THEN** later attempts may select Codex without rewriting any active or completed attempt

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
