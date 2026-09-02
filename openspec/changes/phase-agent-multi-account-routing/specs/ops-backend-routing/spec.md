## MODIFIED Requirements

### Requirement: Backend remains immutable during a transaction

A selected provider/model/account SHALL remain immutable while its phase
attempt is running, and exactly one process SHALL own the phase lease and
repository lock. After that process exits, later phases SHALL re-resolve
current candidates. A confirmed quota-interrupted phase MAY create a
continuation attempt through another eligible provider, or through a
different account of the same provider and model, without changing the
phase or FIX round. Availability changes SHALL never rewrite completed
attempt history.

#### Scenario: Fallback transaction survives Codex re-enable
- **WHEN** a Claude attempt is already running and Codex becomes available
- **THEN** the running attempt remains Claude-owned and no concurrent replacement starts

#### Scenario: Active Codex transaction survives automatic disable
- **WHEN** a running Codex attempt reports explicit global quota exhaustion
- **THEN** it is allowed to exit and checkpoint evidence before one eligible continuation attempt may be resolved

#### Scenario: New transaction observes current state
- **WHEN** a new phase starts after provider health or a manual override changes
- **THEN** candidate resolution observes current state without altering earlier attempts

#### Scenario: New quant fallback transaction observes automatic disable
- **WHEN** a quant phase starts while its preferred provider is deterministically unavailable
- **THEN** it selects the next eligible candidate without creating a second research iteration

#### Scenario: Same-provider account failover preserves the preferred model
- **WHEN** a running attempt's account reports confirmed quota exhaustion and a different account of the same provider and model is eligible
- **THEN** the continuation attempt uses that other account under the same provider and model rather than degrading to a different provider or model

### Requirement: Interrupted processing continues from preserved work

After confirmed account/global quota exhaustion, orchestration SHALL ensure
the old process has exited, checkpoint safe evidence and Git state, and
release only the attempt lease before selecting another candidate under the
same phase and repository lock. If files or commits changed, the
replacement SHALL run in continuation mode and inspect current work rather
than restart or roll it back. Ambiguous external side effects or an
unverifiable old process SHALL block automatic failover. A candidate naming
an account distinct from the interrupted attempt's account SHALL be treated
as eligible on the same basis as a candidate naming a different provider.

#### Scenario: Quota ends an unchanged attempt
- **WHEN** a quota-exhausted PLAN, IMPLEMENT or FIX attempt made no Git change
- **THEN** the next eligible candidate may start another attempt in the same phase and round

#### Scenario: Quota interrupts partial implementation
- **WHEN** a quota-exhausted IMPLEMENT or FIX attempt left a diff or commit
- **THEN** the next eligible candidate receives continuation context and completes from the actual worktree without automatic rollback

#### Scenario: Old process is still alive
- **WHEN** the interrupted provider process cannot be confirmed exited after bounded TERM/KILL
- **THEN** orchestration blocks instead of starting a concurrent replacement

#### Scenario: Implementation failure is not quota failover
- **WHEN** an attempt fails because code or tests are incorrect
- **THEN** orchestration records the failure and does not substitute providers as if quota were exhausted

#### Scenario: Account-scoped quota exhaustion does not block a sibling account
- **WHEN** one account of a provider reports confirmed quota exhaustion
- **THEN** a different account of the same provider remains eligible for the next candidate rather than being treated as unavailable

## ADDED Requirements

### Requirement: Account eligibility and identity are explicit and registry-bound

A candidate MAY name an account alongside its provider, model and effort.
Every named account SHALL resolve through a fixed, named registry entry for
its provider rather than an arbitrary caller-supplied path, and an unknown
account name SHALL be rejected the same way an unsupported provider is
rejected today. A candidate omitting an account SHALL resolve through that
provider's ambient environment exactly as it does without this capability.
Availability SHALL be tracked per provider-and-account pair once an account
is named, so one account's confirmed quota exhaustion, manual disable, or
auth error SHALL NOT change a different account's recorded availability.

#### Scenario: Unknown account is rejected
- **WHEN** a candidate or manual override names an account with no registry entry for its provider
- **THEN** resolution is rejected the same way an unsupported provider or invalid model is rejected, and no attempt starts

#### Scenario: Unnamed account preserves existing single-account behavior
- **WHEN** a candidate has no account field
- **THEN** its attempt resolves the provider's configuration from the ambient environment exactly as before this capability existed

#### Scenario: One account's exhaustion does not disable a sibling account
- **WHEN** the `work` account of a provider is marked unavailable after confirmed quota exhaustion
- **THEN** the `personal` account of the same provider remains independently available for resolution
