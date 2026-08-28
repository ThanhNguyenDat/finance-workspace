# ops-backend-routing Specification

## Purpose
Provides an explicit, immutable implementation-backend contract for Finance orchestration so normal requests remain Codex-owned while a validated quant fallback can be implemented by the current Claude session without bypassing lifecycle safety gates.

## Requirements

### Requirement: New transactions persist a safe implementation backend

The orchestration runtime SHALL persist `implementation_backend` and `verification_mode` when a transaction is initialized. An omitted backend SHALL select `codex` with `independent` verification. `claude-fallback` SHALL be accepted only with explicit `quant-fallback` context and a valid quant state reporting `codex_available=false`; arbitrary backend values and ungated fallback SHALL be rejected.

#### Scenario: Normal transaction defaults to Codex

- **WHEN** a transaction is initialized without a backend
- **THEN** its runtime state contains `implementation_backend=codex` and `verification_mode=independent`

#### Scenario: Explicit quant fallback is accepted

- **WHEN** a transaction is initialized with `claude-fallback`, `quant-fallback` context, and current quant state `codex_available=false`
- **THEN** its runtime state contains `implementation_backend=claude-fallback` and `verification_mode=claude-fallback-self-review`

#### Scenario: Ungated or invalid backend is rejected

- **WHEN** a transaction requests an unknown backend or requests Claude fallback without both required gates
- **THEN** initialization exits nonzero and does not create an invalid transaction state

### Requirement: Backend remains immutable during a transaction

Once initialized, a transaction SHALL route implementation from its persisted backend and SHALL NOT re-read quant availability to switch backend during IMPLEMENT or FIX. A later quant toggle SHALL affect only newly initialized transactions.

#### Scenario: Fallback transaction survives Codex re-enable

- **WHEN** a fallback transaction is initialized and the quant state later changes to `codex_available=true`
- **THEN** the active transaction remains `claude-fallback` for both IMPLEMENT and FIX routing

#### Scenario: New transaction observes current state

- **WHEN** a new normal transaction is initialized after Codex is re-enabled
- **THEN** the new transaction uses the default `codex` backend

### Requirement: IMPLEMENT and FIX use the selected backend

The `/ops:run` contract SHALL route `codex` IMPLEMENT/FIX phases to `run-codex-phase.sh` and route `claude-fallback` phases to the current top-level Claude session. Fallback SHALL preserve locks, OpenSpec, scope, tests, verification, release/deploy gates, archive, and DONE semantics and SHALL never launch another Claude process.

#### Scenario: Codex implementation route

- **WHEN** an active transaction has `implementation_backend=codex` and enters IMPLEMENT or FIX
- **THEN** the Codex worker route is selected

#### Scenario: Claude fallback route

- **WHEN** an active transaction has `implementation_backend=claude-fallback` and enters IMPLEMENT or FIX
- **THEN** the current Claude session is the implementer and the Codex worker route is not selected

#### Scenario: Fallback verification is explicit

- **WHEN** the current Claude session both implements and verifies a fallback change
- **THEN** evidence records `verification_mode=claude-fallback-self-review` and does not claim independent maker/checker separation

### Requirement: The global Codex worker remains generic

`run-codex-phase.sh` SHALL instruct the worker to apply the active OpenSpec change in the declared implementation repository, read applicable repository instructions/rules/skills, respect scope and safety constraints, run verification, create required local commits, and not push before Claude final verification. It SHALL NOT contain smoke-specific documentation restrictions.

#### Scenario: Generic worker prompt

- **WHEN** the Codex worker is invoked for any supported runtime repository
- **THEN** its prompt is reusable across changes and contains no finance-mw documentation smoke-test wording

### Requirement: Routing and regression tests are bounded

The repository SHALL test default backend selection, gated fallback selection, backend immutability after quant toggles, invalid requests, IMPLEMENT/FIX route selection, generic worker wording, and existing atomic FIX behavior without launching real Claude, Codex implementation, loops, or production deployment.

#### Scenario: Agent Contracts remains green

- **WHEN** the bounded backend and existing orchestration tests run in CI
- **THEN** all routing, state, generic-worker, timeout, and lock assertions pass within the existing job timeout

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
