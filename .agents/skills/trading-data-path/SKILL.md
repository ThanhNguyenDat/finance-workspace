---
name: trading-data-path
description: Diagnose or change the live trading-data path from Finance Live Action workers through Finance MW to the browser. Use when snapshots, metrics, candles, or trade history are missing, stale, slow, duplicated, or when changing a gRPC/stream/gateway contract.
---

# Trading Data Path

Find the first layer where observed state diverges from its upstream source,
then change the owning repository and keep every downstream contract aligned.

## Inputs and output

Input is a route/scope, payload type, expected freshness, and observed symptom.
Output is a measured bottleneck or contract defect, a scoped fix when requested,
and end-to-end evidence from worker to browser.

## Workflow

1. Establish immutable runtime identity and current route readiness.
2. Measure production rates and freshness at worker, transport, Finance MW, and
   browser boundaries; do not diagnose from logs alone.
3. Compare payload scope, timestamps, ordering, fanout, buffering, and recovery.
4. Change the earliest owning layer and synchronize schemas/consumers.
5. Test backpressure, reconnect, duplicate, stale, and closed-candle behavior.
6. Verify end-to-end freshness and observability after delivery.

## Non-negotiable invariants

- Container health is not trading readiness.
- Preserve ordering, scope identity, closed-candle semantics, and bounded fanout.
- Do not mask upstream data loss or staleness in the browser.
- Stop on a cross-repository contract mismatch that lacks an approved design.

## Detailed guidance

Read [references/playbook.md](references/playbook.md) for production counting,
payload contracts, readiness, broker-current/storage-stale recovery, fanout,
Kafka restart races, load sizing, validation, telemetry, and stop conditions.
Read only the sections relevant to the failing boundary.
