## MODIFIED Requirements

### Requirement: Research policy preserves quant and safety constraints

Each enabled iteration SHALL respond in Vietnamese, prioritize XAU then BTC,
treat other instruments as UI/backlog-only, require defensible OOS, holdout, or
walk-forward evidence before claiming improvement, allow a valid rejection or
no-improvement result, limit exploratory work to at most two local
strategy/service containers with bounded production-equivalent resources, and
update research notes, metric history, samples, and the research navigation
index under `research/quant/` without fabricating metrics or secrets. When a
candidate passes the promotion gate, the command SHALL create or reuse a scoped
OpenSpec change, attach concise research-origin references to the corresponding
OPS transaction, and enter the existing OPS lifecycle. It SHALL NOT create or
use a global handoff or ad-hoc request file as an engineering queue or source
of lifecycle truth.

#### Scenario: Normal Codex-available mode

- **WHEN** valid research produces a promoted actionable candidate and
  `codex_available=true`
- **THEN** the command records research evidence, creates or reuses OpenSpec,
  and enters a new OPS transaction with the normal Codex backend without
  implementing runtime code outside OPS

#### Scenario: Codex fallback mode

- **WHEN** valid research produces a promoted actionable candidate and
  `codex_available=false`
- **THEN** the command creates or reuses OpenSpec and enters the existing
  `/ops:run` lifecycle with the explicitly gated Claude-fallback backend,
  preserving locks, tests, verification, release, deployment, archive, and
  DONE gates

#### Scenario: No false improvement

- **WHEN** no candidate beats the baseline on defensible unseen data
- **THEN** the iteration records the negative result and its evidence rather
  than manufacturing an improvement, cherry-picking metrics, or opening
  engineering work
