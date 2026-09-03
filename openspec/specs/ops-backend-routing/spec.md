# ops-backend-routing Specification

## Purpose
Provides provider-neutral, phase-scoped routing for Finance orchestration while preserving exclusive ownership, bounded recovery, auditable verification, and legacy transaction safety.

## Requirements

### Requirement: New transactions persist a safe implementation backend

New orchestration transactions SHALL persist a phase-agent routing-policy
version and append-only attempt history instead of selecting one immutable
implementation backend and verification mode for the whole transaction. Each
attempt SHALL identify phase, round, provider, model, process identity,
continuation mode and terminal class. Legacy active transactions with an
existing backend pair SHALL retain legacy routing until terminal. Unknown
policy versions, providers, phases and incompatible attempt values SHALL be
rejected.

#### Scenario: Normal transaction defaults to Codex
- **WHEN** a new transaction initializes without manual phase overrides
- **THEN** it records the current routing-policy version and resolves each phase from its ordered default candidates rather than persisting a transaction-wide backend

#### Scenario: Explicit quant fallback is accepted
- **WHEN** an operator has pinned an eligible quant or implementation phase candidate before a new attempt
- **THEN** the attempt records that explicit provider selection without changing unrelated phase profiles

#### Scenario: Ungated or invalid backend is rejected
- **WHEN** initialization or resolution encounters an unsupported policy/provider/phase combination
- **THEN** it exits nonzero and does not create an invalid transaction or attempt record

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

### Requirement: IMPLEMENT and FIX use the selected backend

The OPS contract SHALL route PLAN, IMPLEMENT, VERIFY, FIX and FINAL_VERIFY
through the generic phase-agent resolver, which SHALL invoke only the selected
Codex or Claude adapter. Every route SHALL preserve locks, OpenSpec scope,
tests, current-round findings, release/deploy gates, archive and DONE semantics.
Direct model CLI invocation and concurrent provider workers SHALL be prohibited.

#### Scenario: Codex implementation route
- **WHEN** candidate resolution selects Codex for IMPLEMENT or FIX
- **THEN** only the bounded Codex adapter runs for that attempt

#### Scenario: Claude fallback route
- **WHEN** candidate resolution selects Claude for IMPLEMENT or FIX
- **THEN** only the bounded Claude adapter runs for that attempt

#### Scenario: Verification route is phase-specific
- **WHEN** a transaction enters VERIFY or FINAL_VERIFY
- **THEN** a fresh read-only attempt uses only that phase's selected candidate and cannot alter routing history

#### Scenario: Fallback verification is explicit
- **WHEN** the latest mutator and verifier are separate processes of the same provider
- **THEN** evidence records same-provider process separation and does not claim provider independence

#### Scenario: Arbitrary nested Claude remains prohibited
- **WHEN** orchestration needs any model-owned phase
- **THEN** it invokes the generic resolver and selected adapter rather than calling Claude or Codex directly

#### Scenario: Workspace-only change uses the workspace repository
- **WHEN** a phase-agent change affects `finance-workspace` without a separate runtime repository
- **THEN** the selected adapter runs against the workspace worktree without requiring or duplicating an additional repository root

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

### Requirement: The global Codex worker remains generic

The Codex adapter SHALL accept every configured model-owned phase, read the
active OpenSpec change and applicable instructions, preserve phase-specific
read/write boundaries, create required local commits only for mutating phases,
and never push. It SHALL NOT contain change-specific or smoke-specific wording.

#### Scenario: Generic worker prompt
- **WHEN** Codex is selected for any supported phase or runtime repository
- **THEN** its prompt is reusable across changes and enforces that phase's scope

### Requirement: Routing and regression tests are bounded

The repository SHALL test candidate selection, manual pins, provider health,
legacy routing compatibility, attempt immutability, continuation after quota,
current-round findings, verifier read-only behavior and existing atomic FIX
limits without contacting real model services or production.

#### Scenario: Agent Contracts remains green
- **WHEN** bounded orchestration and fake-provider tests run in CI
- **THEN** all routing, state, continuation, timeout, lock and evidence assertions pass within the job timeout

### Requirement: Final verification follows the persisted verification mode

FINAL_VERIFY SHALL derive its evidence label from the latest successful
mutating attempt and the fresh final verifier attempt. Different providers
SHALL produce `provider-independent`; different processes of one provider SHALL
produce `same-provider-process-separated`. Release SHALL require the selected
FINAL_VERIFY attempt to persist an explicit passing objective-gate attestation,
zero P0/P1 findings, and every applicable objective gate to pass. A zero process
exit without that attestation SHALL fail FINAL_VERIFY. Release SHALL NOT allow a
configured label to overstate actual separation.

#### Scenario: Codex transaction requires independent final verification
- **WHEN** Codex is the latest mutator and Claude performs fresh FINAL_VERIFY
- **THEN** evidence records provider-independent verification before release

#### Scenario: Fallback transaction uses enhanced self-review
- **WHEN** the latest mutator and FINAL_VERIFY use the same provider in distinct processes
- **THEN** evidence records same-provider process-separated review and that provider independence is unavailable

#### Scenario: Fallback transaction may complete
- **WHEN** the derived verification gate and every applicable objective gate pass
- **THEN** the transaction may proceed through RELEASE, DEPLOY_VERIFY when applicable, ARCHIVE and DONE using the honest separation label

#### Scenario: Insufficient verification blocks release
- **WHEN** required evidence is missing, process separation is not proven, or a P0/P1 remains
- **THEN** release is blocked and the defect returns through bounded FIX, VERIFY and FINAL_VERIFY attempts

#### Scenario: Successful exit without gate attestation blocks release
- **WHEN** a FINAL_VERIFY process exits zero without the required passing objective-gate attestation
- **THEN** its attempt is recorded as failed and RELEASE or ARCHIVE remains blocked

### Requirement: Terminal operation handoffs leave the active namespace

Terminal historical operation handoffs with status DONE, FAILED, or BLOCKED
SHALL live under `.ops/archive/` rather than `.ops/changes/`. Archiving a
FAILED handoff SHALL preserve its failure reason, lock-cleanup status, and
deployment outcome and SHALL NOT relabel it as DONE.

#### Scenario: Failed smoke evidence is archived accurately
- **WHEN** the terminal `finance-mw-dev-docs-smoke` record is removed from the active namespace
- **THEN** its handoff exists under `.ops/archive/2026-08-28-finance-mw-dev-docs-smoke/` and still reports FAILED due to the bounded Codex timeout, cleaned locks, and no production deployment
