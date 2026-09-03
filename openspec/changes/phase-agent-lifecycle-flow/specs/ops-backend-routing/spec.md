## MODIFIED Requirements

### Requirement: IMPLEMENT and FIX use the selected backend

The OPS contract SHALL route PLAN, BRAINSTORM, IMPLEMENT, VERIFY, FIX and
FINAL_VERIFY through the generic phase-agent resolver, which SHALL invoke only
the selected Codex or Claude adapter. Every route SHALL preserve locks,
OpenSpec scope, tests, current-round findings, release/deploy gates, archive
and DONE semantics. Direct model CLI invocation and concurrent provider
workers SHALL be prohibited. ARCHIVE SHALL remain a guarded orchestration
transition and SHALL not launch an untracked provider worker.

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

#### Scenario: Brainstorm uses the same selected lifecycle context
- **WHEN** PLAN advances to BRAINSTORM
- **THEN** the brainstorm attempt uses the generic resolver, the same change/session lock and the persisted plan context

#### Scenario: Archive does not bypass verification
- **WHEN** an operator requests ARCHIVE
- **THEN** the operation checks the persisted final verification and release gates before changing the lifecycle to a terminal archived state

#### Scenario: Independent lifecycle sessions may run concurrently
- **WHEN** two prompts have disjoint repository/change scopes or isolated worktrees
- **THEN** each uses its own phase lease and selected adapter while preserving the existing one-process-per-phase rule

#### Scenario: Shared mutable scope remains exclusive
- **WHEN** two prompts would mutate the same change/worktree
- **THEN** routing serializes, queues or rejects one prompt and never starts concurrent provider workers against that scope

#### Scenario: Interactive SDK output remains phase-scoped
- **WHEN** a selected adapter streams provider events or waits for operator input
- **THEN** the event channel, logs and responses remain bound to that phase attempt and cannot bypass the resolver, lease or read-only verification boundary
