## Why

Finance orchestration currently hard-codes phase ownership to Codex or Claude,
so account quota exhaustion requires manual backend switching and can strand a
partially completed phase. A provider-neutral phase-agent layer can select an
available worker per phase, preserve interrupted work, and keep verification
claims consistent with the providers that actually ran.

## What Changes

- Represent quant research, PLAN, IMPLEMENT, VERIFY, FIX, and FINAL_VERIFY as
  logical phase agents with ordered Codex/Claude candidates and provider-native
  model/effort settings.
- Add atomic phase-agent and provider-health state with automatic/manual modes,
  bounded recovery probes, per-phase overrides, and safe terminal controls.
- Add a generic phase runner that resolves one candidate per attempt and
  dispatches to bounded Codex or Claude adapters.
- Detect quota/model availability failures during processing, stop the old
  process, preserve attempt evidence and worktree state, then continue through
  an eligible candidate without changing phase or FIX round.
- Persist append-only phase-attempt history instead of one immutable
  transaction-wide implementation backend; keep each running attempt and its
  repository lock immutable.
- Derive provider-independent or same-provider process-separated verification
  from the providers that actually mutated and reviewed the work.
- Keep one-shot terminal quant execution; do not add `/loop`, retries without
  bounds, a daemon, or concurrent phase workers.

## Capabilities

### New Capabilities

- `claude-worker-policy`: compatibility capability for provider adapters,
  phase-specific candidate profiles, bounded external workers, and provider
  health/failure evidence; it is no longer a Claude-only orchestrator.

### Modified Capabilities

- `codex-worker-policy`: make Codex a phase-neutral provider adapter and move
  fallback, continuation, health, and verification selection to the generic
  phase-agent resolver.
- `quant-research-control`: launch one research phase agent and use shared
  provider availability instead of Codex-only routing state.
- `ops-backend-routing`: resolve providers per phase attempt, continue safely
  after quota interruption, and derive verification separation from evidence.

## Impact

- Affected repository: `finance-workspace` only.
- Affected surfaces: `.agents/scripts/`, `.claude/commands/`, transient
  `.ops/runtime/` and per-change attempt evidence, README, shared quant skill,
  OpenSpec contracts, and bounded Agent Contracts.
- Existing provider-specific runners become adapters behind a generic resolver;
  active legacy OPS transactions retain their persisted backend until terminal.
- The former Codex-only FIX fallback contract is superseded by ordered generic
  candidates; provider-local model alternatives remain expressible in policy.
- No trading strategy, broker, risk, market-data, runtime application,
  deployment, or production behavior changes.
- Rollback restores provider-specific routing and ignores the new transient
  state; no production data migration is required.
