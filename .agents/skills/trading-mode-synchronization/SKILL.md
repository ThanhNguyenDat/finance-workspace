---
name: trading-mode-synchronization
description: Preserve Alpha strategy-by-interval ledgers and synchronized Portfolio/Live execution when changing contexts, multi-timeframe evidence, replay order, realtime Klines, scoped metrics, or Alpha/Portfolio/Live selectors.
---

# Trading Mode Synchronization

Keep strategy evidence isolated by interval while Portfolio and Live consume one
synchronized aggregate decision without lookahead or execution duplication.

## Inputs and output

Input is the affected context, interval set, replay/realtime path, ledger scope,
and selector/API contract. Output is a synchronized implementation with explicit
invariants and regression evidence across Alpha, Portfolio, and Live modes.

## Workflow

1. Map the changed behavior to its owning context and repository.
2. Preserve per-strategy/per-interval evidence and deterministic replay order.
3. Aggregate only at the Portfolio boundary after synchronization is complete.
4. Keep Live execution idempotent and aligned with the aggregate Portfolio state.
5. Update selectors, metrics, and contracts together.
6. Test no-lookahead, restart, duplicate, stale evidence, and concurrent updates.

## Non-negotiable invariants

- Alpha ledgers remain scoped; Portfolio/Live state is aggregate and synchronized.
- Risk validation precedes execution and retries cannot duplicate orders.
- Closed-bar and multi-timeframe evidence semantics remain causal.
- Historical replay and realtime processing must converge on equivalent state.

## Detailed guidance

Read [references/playbook.md](references/playbook.md) for full invariants,
strategy selection, layer boundaries, concurrent execution rules, sizing modes,
repository ownership, validation, and stop conditions. Read the sections touched
by the proposed change before editing runtime code.
