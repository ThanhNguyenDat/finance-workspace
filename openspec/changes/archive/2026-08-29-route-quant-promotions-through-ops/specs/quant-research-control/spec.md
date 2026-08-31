## MODIFIED Requirements

### Requirement: A research command is exactly one state-aware iteration

`/quant-research` SHALL read the runtime state at the start of every invocation, record one iteration mechanically, check `research_enabled` before expensive research, and classify the result as `REJECTED`, `NO-CHANGE`, `DATA-ISSUE`, `NEEDS-MORE-RESEARCH`, or `PROMOTE`. It SHALL not schedule another loop, sleep for the loop interval, recursively invoke Claude, embed Codex quota state in the loop prompt, or create an OPS transaction unless the result is `PROMOTE` and the promotion gate passes.

#### Scenario: Intended recurring invocation

- **WHEN** a user configures recurring research
- **THEN** the documented invocation is `/quant:codex-off` followed by `/loop 20m /quant-research`, with quota state held in runtime state rather than loop arguments

#### Scenario: Research is disabled

- **WHEN** `/quant-research` observes `research_enabled=false`
- **THEN** it records the bounded iteration and skips new research/backtests without launching expensive work

#### Scenario: State changes between iterations

- **WHEN** a user runs `/quant:codex-on` after one loop iteration and before the next
- **THEN** the next `/quant-research` invocation reads the current state and uses normal Codex-available behavior without restarting the loop

#### Scenario: Non-promoted iteration has no engineering side effect

- **WHEN** an iteration is classified as anything other than `PROMOTE`
- **THEN** it records research evidence without requiring a new OpenSpec change or OPS transaction

### Requirement: Research policy preserves quant and safety constraints

Each enabled iteration SHALL respond in Vietnamese, prioritize XAU then BTC, treat other instruments as UI/backlog-only, require defensible OOS/holdout or walk-forward evidence before claiming improvement, allow a valid rejection/no-improvement result, limit exploratory work to at most two local strategy/service containers with bounded production-equivalent resources, and update research notes, metric history, and the research navigation backlog without fabricating metrics or secrets. When a candidate passes the promotion gate, the command SHALL create or reuse a scoped OpenSpec change, attach concise research-origin references to the corresponding OPS transaction, and enter the existing OPS lifecycle. It SHALL NOT use `raw/handoff_agent.md` as an engineering queue or source of lifecycle truth.

#### Scenario: Normal Codex-available mode

- **WHEN** valid research produces a promoted actionable candidate and `codex_available=true`
- **THEN** the command records research evidence, creates or reuses OpenSpec, and enters a new OPS transaction with the normal Codex backend without implementing runtime code outside OPS

#### Scenario: Codex fallback mode

- **WHEN** valid research produces a promoted actionable candidate and `codex_available=false`
- **THEN** the command creates or reuses OpenSpec and enters the existing `/ops:run` lifecycle with the explicitly gated Claude-fallback backend, preserving locks, tests, verification, release, deployment, archive, and DONE gates

#### Scenario: No false improvement

- **WHEN** no candidate beats the baseline on defensible unseen data
- **THEN** the iteration records the negative result and its evidence rather than manufacturing an improvement, cherry-picking metrics, or opening engineering work

### Requirement: Repository contracts test the integration without a long loop

The repository SHALL provide bounded shell tests for state initialization/toggles/iteration/malformed-state safety, promotion and trace metadata, static command composition, handoff non-authority, stable OpenSpec/OPS identity, and preserved backend routing. Agent Contracts SHALL run them alongside existing orchestration and Codex worker tests without launching a real loop, model worker, backtest, or production deployment.

#### Scenario: Contract suite passes

- **WHEN** the bounded state, promotion, command, backend, worker, and existing orchestration tests run in CI
- **THEN** all state, classification, trace, source-of-truth, routing, timeout, and secret-safety assertions pass within the existing job timeout
