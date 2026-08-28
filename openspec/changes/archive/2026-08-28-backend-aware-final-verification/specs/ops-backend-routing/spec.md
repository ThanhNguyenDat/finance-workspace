## ADDED Requirements

### Requirement: Final verification follows the persisted verification mode

The orchestration contract SHALL choose the FINAL_VERIFY evidence gate from
the transaction's persisted `verification_mode`. `independent` SHALL require
independent Claude final verification after Codex implementation or fixes.
`claude-fallback-self-review` SHALL permit the current top-level Claude session
to perform enhanced final self-review using all applicable objective evidence,
and SHALL prohibit any claim of independent maker/checker separation. Either
valid mode SHALL be eligible for release, deployment verification, archive,
and completion only after its own evidence gate passes. Final verification
SHALL NOT re-read quant availability or mutate the persisted backend pair.

#### Scenario: Codex transaction requires independent final verification

- **WHEN** an active transaction persists `implementation_backend=codex` and `verification_mode=independent`
- **THEN** release remains blocked until independent Claude FINAL_VERIFY passes

#### Scenario: Fallback transaction uses enhanced self-review

- **WHEN** an active transaction persists `implementation_backend=claude-fallback` and `verification_mode=claude-fallback-self-review`
- **THEN** the current top-level Claude session may pass FINAL_VERIFY using a fresh diff review, acceptance-criteria review, and all applicable objective repository, CI, deployment, and production evidence
- **AND** the workflow records that independent maker/checker verification is not available

#### Scenario: Fallback transaction may complete

- **WHEN** enhanced fallback final verification and every applicable objective evidence gate pass
- **THEN** the transaction may proceed through RELEASE, DEPLOY_VERIFY when applicable, ARCHIVE, and DONE without claiming independent review

#### Scenario: Insufficient verification blocks release

- **WHEN** the evidence required by the persisted verification mode is missing or a P0/P1 finding remains
- **THEN** release is blocked and any implementation defect returns through the existing bounded FIX, VERIFY, and FINAL_VERIFY path using the same persisted backend

### Requirement: Terminal operation handoffs leave the active namespace

Terminal historical operation handoffs with status DONE, FAILED, or BLOCKED
SHALL live under `.ops/archive/` rather than `.ops/changes/`. Archiving a
FAILED handoff SHALL preserve its failure reason, lock-cleanup status, and
deployment outcome and SHALL NOT relabel it as DONE.

#### Scenario: Failed smoke evidence is archived accurately

- **WHEN** the terminal `finance-mw-dev-docs-smoke` record is removed from the active namespace
- **THEN** its handoff exists under `.ops/archive/2026-08-28-finance-mw-dev-docs-smoke/` and still reports FAILED due to the bounded Codex timeout, cleaned locks, and no production deployment
