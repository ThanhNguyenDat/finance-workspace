---
name: kline-data-quality
description: Diagnose or repair missing, stale, duplicated, off-grid, or visually discontinuous Klines across broker history, Kafka, Redis, Timescale, Finance MW, and charts. Use before treating a chart gap as data loss or adding an instrument/interval.
---

# Kline Data Quality

Establish whether a candle problem is source availability, transport, storage,
API shaping, or chart presentation before changing data.

## Inputs and output

Input is a route (`broker`, market type, symbol, interval), observed time range,
and symptom. Output is an evidence-backed classification, the owning layer, the
smallest safe repair when needed, and continuity verification after the change.

## Workflow

1. Inventory every affected route and interval; do not generalize from one pair.
2. Measure broker availability, ingestion, canonical storage, API output, and UI
   rendering in ownership order.
3. Distinguish expected market closures and marker semantics from missing data.
4. Repair only omissions confirmed against the broker, preserving canonical
   timestamp, precision, idempotency, and closed-candle semantics.
5. Re-run bounded continuity checks and record exact before/after evidence.

## Non-negotiable invariants

- Never synthesize candles merely to make a chart continuous.
- Preserve raw symbols and canonical time-grid semantics.
- Treat production repair as an explicit, bounded, recoverable operation.
- Do not infer source data loss from chart appearance alone.

## Detailed guidance

Read [references/playbook.md](references/playbook.md) for route inventory,
ownership-order queries, broker verification limits, repair procedures,
monitoring semantics, regression checks, and delivery evidence. Read only the
sections relevant to the observed layer and operation.
