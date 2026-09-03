## Purpose

Provides one resumable, provider-neutral lifecycle for planning, exploration,
implementation, verification, bounded remediation and archival of an
orchestrated change.

## ADDED Requirements

### Requirement: Lifecycle state is explicit and resumable

The orchestration system SHALL persist the current lifecycle state for each
change and session using the phases PLAN, BRAINSTORM, IMPLEMENT, VERIFY, FIX
and ARCHIVE. A new invocation SHALL resume from the last safe checkpoint when
the change and session identity match, and SHALL reject an ambiguous or
conflicting active session instead of silently starting a second lifecycle.

#### Scenario: New prompt starts a lifecycle
- **WHEN** an operator submits a new prompt or change reference without an active session
- **THEN** the system creates one lifecycle session at PLAN with a durable change identity and checkpoint

#### Scenario: Plan advances to brainstorm
- **WHEN** PLAN completes with its required planning evidence
- **THEN** the same session advances to BRAINSTORM without losing the original prompt, change or repository scope

#### Scenario: Brainstorm advances to implementation
- **WHEN** BRAINSTORM records an actionable implementation direction
- **THEN** the same session advances to IMPLEMENT with the brainstorm evidence available as continuation context

#### Scenario: Interrupted lifecycle resumes
- **WHEN** the process exits, a terminal closes, or a provider quota is exhausted after a safe checkpoint
- **THEN** the next invocation resumes the current phase and round from persisted context rather than recreating completed work

#### Scenario: Conflicting session is rejected
- **WHEN** another active process owns the change/session lease
- **THEN** the new invocation exits bounded and does not launch a concurrent provider attempt

### Requirement: All operator entry points share one lifecycle

The shell end-to-end entry point, Claude terminal command, Codex terminal
command and long-running quant-research loop SHALL attach to the same
change/session state machine. An entry point SHALL select or resume the
appropriate logical phase through the generic resolver and SHALL NOT create a
provider-specific parallel lifecycle for the same change.

#### Scenario: Shell entry point attaches to a change
- **WHEN** `.e2e.sh` receives a prompt or change reference
- **THEN** it starts or resumes the shared lifecycle and reports the persisted phase and session identity

#### Scenario: Manual provider command attaches to the lifecycle
- **WHEN** a Claude or Codex terminal command is used for a requested fix
- **THEN** the command contributes to the current lifecycle phase under the resolver's selected candidate and preserves the same locks and context

#### Scenario: Quant loop reuses context
- **WHEN** `/loop 20m /quant-research` starts another bounded iteration
- **THEN** it resumes the existing quant session and records a new iteration checkpoint without reopening unrelated lifecycle phases

#### Scenario: Re-entry does not duplicate work
- **WHEN** an operator invokes any supported entry point while the lifecycle is already processing
- **THEN** the invocation observes the active lease and either reports the owner or performs the defined bounded resume path without launching a second worker

### Requirement: Independent prompts may run concurrently

The orchestration system SHALL admit multiple independent prompt sessions in
parallel up to a configured concurrency limit. Each admitted session SHALL
have a unique session identity, isolated lifecycle state, attempt/log
namespace, provider lease and repository worktree or an explicitly disjoint
scope. Prompts whose effective change/worktree scope overlaps SHALL be
serialized, queued or rejected with an actionable bounded status; they SHALL
never concurrently mutate one worktree or share one active phase lease.

#### Scenario: Two independent prompts run in parallel
- **WHEN** two prompts target disjoint changes or isolated repository worktrees and capacity is available
- **THEN** both sessions are admitted and progress independently without sharing lifecycle state or provider leases

#### Scenario: Parallel capacity is bounded
- **WHEN** more prompts are submitted than the configured concurrency limit
- **THEN** excess sessions receive a persisted queued/backpressure result and no untracked provider process is launched

#### Scenario: Overlapping worktree scope is protected
- **WHEN** two prompts target the same mutable change/worktree without an isolation plan
- **THEN** one session owns the scope while the other is queued or rejected, and no concurrent mutation attempt starts

#### Scenario: One parallel session exhausts quota
- **WHEN** one concurrent session reaches confirmed account/provider quota exhaustion
- **THEN** only that session rotates its candidate or account and the other sessions continue with their own state and leases

### Requirement: Admission and resource ownership are session-scoped

The coordinator SHALL persist each prompt session, bounded admission result and
resource lease independently. It SHALL reserve capacity only for the lifetime
of an admitted session and SHALL NOT use one workspace-global prompt mutex as
the condition for all sessions to run. Resource ownership SHALL be keyed by
the effective mutable change/worktree and provider account, so disjoint scopes
may run concurrently while overlapping scopes remain exclusive.

#### Scenario: Independent accounts run together
- **WHEN** two admitted sessions use different configured Claude accounts and disjoint worktrees
- **THEN** both provider attempts may remain active concurrently and each session records its own account lease

#### Scenario: Same account remains exclusive
- **WHEN** two sessions select the same provider account
- **THEN** only one attempt owns that account lease and the other is queued or rejected without starting a provider process

#### Scenario: Capacity exhaustion is persisted
- **WHEN** all configured admission slots are occupied
- **THEN** a new session is persisted as queued with a bounded reason and no provider process is launched

#### Scenario: Lease recovery fails closed
- **WHEN** a lease expires but owner liveness, process identity or fencing state is ambiguous
- **THEN** the coordinator reports an indeterminate recovery state and does not delete or replace the lease automatically

### Requirement: Every model-owned phase runs through a streaming SDK session

PLAN, BRAINSTORM, IMPLEMENT, VERIFY and FIX SHALL execute through the
selected provider's SDK session, not an untracked direct provider command. The
session SHALL emit structured lifecycle, provider, tool/shell, approval,
quota, log and terminal events to a per-session channel while retaining the
existing phase result and attempt contracts.

#### Scenario: SDK phase exposes live events
- **WHEN** a model-owned phase is processing
- **THEN** its session channel emits ordered structured events for phase status, provider/model/account, progress, logs and terminal result while the SDK session remains authoritative

#### Scenario: Provider output remains session-scoped
- **WHEN** multiple prompt sessions run in parallel
- **THEN** each session writes to its own event/log stream and the monitor never displays another session's output or input

#### Scenario: SDK failure is terminally classified
- **WHEN** the provider SDK returns a structured success, interruption, quota, authentication, tool or failure result
- **THEN** the coordinator records the mapped result class and terminal event without treating a partial log line as success

### Requirement: Running sessions remain operator-interactive

The operator console attached to `.e2e.sh` SHALL follow a running session's
structured events and display a readable monitor for current phase,
provider/model/account, elapsed time, current action, quota/failover, tests
and terminal state. If Claude or Codex requests approval, input or a tool
decision, the console SHALL display the request and route the operator's
response back to the same SDK session. A detached session SHALL continue under
its bounded lease and SHALL be attachable again from its session identity.

#### Scenario: Operator answers a provider question
- **WHEN** a live SDK session asks for approval or input
- **THEN** the monitor enters a waiting state, accepts the operator response and resumes that same session without starting a replacement attempt

#### Scenario: Background session is detached and reattached
- **WHEN** the operator leaves the console while a phase is still processing
- **THEN** the bounded session continues, persists events/logs, and a later attach replays from the requested event/log position before following new output

#### Scenario: Operator response times out safely
- **WHEN** a provider question remains unanswered past its configured bounded wait
- **THEN** the session records an operator-timeout outcome and releases its lease safely without launching a duplicate session

#### Scenario: Shell/tool activity is visible
- **WHEN** the SDK session performs an allowed shell/tool action or runs a bounded test
- **THEN** the monitor shows its redacted command/status/output metadata and keeps the action correlated to the owning phase and session

### Requirement: Interactive channels protect secrets and control boundaries

Session event streams, monitor output and operator input SHALL be scoped to the
owning session and SHALL redact credentials, tokens, cookies, authorization
values and secret-bearing command output. Only the coordinator may forward
operator responses to the SDK; a log viewer SHALL be read-only and SHALL NOT
be able to inject provider input or bypass phase permissions.

#### Scenario: Secret-bearing event is redacted
- **WHEN** a provider or shell event contains a configured secret pattern
- **THEN** the persisted and displayed event contains a redacted placeholder and never the secret value

#### Scenario: Wrong session cannot answer a question
- **WHEN** an operator sends input using a different or stale session identity
- **THEN** the coordinator rejects it without changing the live SDK session

### Requirement: Verification remediation is bounded and cyclic

After IMPLEMENT, the lifecycle SHALL enter VERIFY. A verification result with
no blocking findings SHALL advance to ARCHIVE. A result with P0/P1 findings or
other configured blocking evidence SHALL enter FIX and then return to VERIFY
within the same remediation round. The system SHALL stop and report a bounded
failure when the configured fix limit is reached.

#### Scenario: Clean verification archives
- **WHEN** VERIFY records the required passing evidence and no blocking findings
- **THEN** the lifecycle advances to guarded ARCHIVE

#### Scenario: Verification finding enters fix
- **WHEN** VERIFY records a blocking finding
- **THEN** the lifecycle enters FIX with only the current-round findings and the implementation context

#### Scenario: Fix returns to verification
- **WHEN** FIX completes its bounded changes and regression checks
- **THEN** the lifecycle returns to VERIFY in the same round with a fresh verifier attempt

#### Scenario: Fix limit blocks completion
- **WHEN** the configured maximum number of FIX attempts is exhausted without a passing VERIFY
- **THEN** the lifecycle remains non-terminal, records the failure evidence and does not archive the change

### Requirement: Archive is a guarded terminal transition

ARCHIVE SHALL be reachable only after the required VERIFY/FINAL_VERIFY
attestation, zero blocking findings and all applicable release gates pass. It
SHALL preserve the lifecycle, attempt, quota and verification evidence in the
historical archive namespace and SHALL not relabel a failed or blocked session
as successful.

#### Scenario: Archive succeeds after all gates
- **WHEN** the final verifier has persisted the required passing attestation and every applicable gate passes
- **THEN** the change is archived with its terminal status and evidence

#### Scenario: Archive is blocked by missing evidence
- **WHEN** a required attestation, lock cleanup result or release gate is missing
- **THEN** ARCHIVE is rejected and the active lifecycle remains available for remediation

#### Scenario: Failed lifecycle retains history
- **WHEN** the lifecycle terminates as FAILED or BLOCKED
- **THEN** its reason, attempts, account rotations and cleanup outcome remain under the archive namespace without being reported as DONE
