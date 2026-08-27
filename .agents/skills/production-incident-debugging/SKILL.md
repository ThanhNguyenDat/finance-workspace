---
name: production-incident-debugging
description: Diagnose production outages, zero or stale data, reconnects, errors, and latency through the unified metrics, traces, ECS logs, data dependencies, and runtime identity. Use when a production root cause must be proved from correlated evidence rather than inferred from health status.
---

# Production Incident Debugging

Build an evidence chain before naming a root cause. Never turn absence of
evidence into evidence of absence, treat `No data` as zero, or infer functional
health from a green container, HTTP 200, or successful deployment.

## Open an incident envelope

Record the exact UTC interval, affected user path, expected and observed
behavior, and the smallest canonical scope that identifies the failure. For
trading data include broker, market type, base asset, quote asset, interval,
layer, setup, and rule when applicable. Resolve the immutable deployed commit
for every service on the path and the exact Coolify resource that owns each
runtime.

Set a bounded observation budget before monitoring an intermittent failure:
use a fixed UTC duration or a fixed number of connection attempts appropriate
to the reported frequency. When the budget ends without an exemplar, classify
the cause `unknown/unverified`, preserve the measured non-occurrence, and name
the next discriminating probe instead of watching indefinitely.

Every claim must cite all of:

- the query, probe, or artifact that produced the result;
- result count or measured value, not only a screenshot or prose summary;
- UTC observation time and query window;
- service, environment, and business scope;
- status: `proven`, `disproven`, or `unknown/unverified`.

Redact credentials and sensitive payloads. Preserve trace IDs, immutable
commits, safe route labels, timestamps, counts, rates, durations, and offsets.

Never print a broad process command line with `ps ... args`, `docker top ...
args`, or `/proc/*/cmdline`. Container entrypoints can translate secret
environment settings into argv, so a read-only process dump can itself expose
credentials. Resolve the exact PID/container from non-command metadata and
inspect only allowlisted fields. When proving that a known secret is absent
from one exact process, keep both the expected values and captured argv in
mode-`0600` temporary files, compare without printing either file, emit only a
boolean result, and remove the files with a trap.

## Follow the evidence path

1. Reproduce the exact behavior through the same public API, browser path, or
   consumer contract. Capture status, response schema, row/series count,
   freshness timestamp, latency, and authentication scope. If it cannot be
   reproduced, keep the report inconclusive and compare a known-good scope.
2. Prove runtime identity and topology. Resolve the public response or runtime
   metadata to immutable commit SHAs, then map each container to one Coolify
   resource and its configured upstreams. A deployment is not verified merely
   because the expected image exists.
3. Query current `/metrics` endpoints and VictoriaMetrics/Grafana for the
   incident window. Check scrape target status, sample timestamps, label
   cardinality, rates, errors, latency, queue depth, and progress counters.
   Distinguish a missing metric family, stale samples, and a real numeric zero.
   Use a current instant query to validate a range-query conclusion.
4. Select one concrete failing request, message, or operation. Obtain its W3C
   `traceparent` or `trace.id`, query Tempo by that identifier, and record the
   involved services, span names, status, timing, parent/child path, and failing
   boundary. If no trace exists, prove whether instrumentation, propagation,
   sampling, or export is missing; do not invent the path. A transport
   reconnect may not have a request trace. In that case correlate a real
   connection or session identifier with gRPC status or WebSocket close code,
   proxy/load-balancer event, peer identity, and aligned client/server UTC
   timestamps. If those identifiers are unavailable, record that telemetry gap
   and keep the reconnect cause unverified.
5. Correlate Elasticsearch/Kibana ECS logs by the exact `trace.id`, UTC window,
   service identity, and business scope before searching message text. Record
   counts and representative structured fields such as `@timestamp`,
   `service.name`, `service.version`, `log.level`, `event.dataset`, `trace.id`,
   `span.id`, `error.type`, and `log.caller`. Missing correlation fields are an
   observability defect, not proof that the service produced no error.
6. Measure the affected dependency path. For streaming trading data, follow
   producer timestamp and Kafka partition/offset/consumer lag, Redis queue and
   checkpoint, Timescale count/min/max/duplicates/gaps, Finance MW payload, and
   browser freshness. Verify a suspected Kline omission against the owning
   broker before calling it data loss. Use `kline-data-quality` or
   `trading-data-path` for their specialized contracts.
7. Measure host and runner safety for the same window: load, CPU and memory
   pressure, available memory, disk/inodes, OOM/kernel events, container
   restart counts, throttling, and self-hosted runner jobs. Temporal overlap is
   correlation only; require resource-pressure or failure evidence before
   assigning causality.
8. State the causal chain only when the failing behavior, telemetry boundary,
   and dependency/runtime evidence agree in time and scope. Separate the
   report into proven facts, disproven hypotheses, and unknowns. Label a likely
   explanation as `unknown/unverified` until a discriminating probe confirms
   it.

## Fix and verify

Add a failing regression for a reproducible software defect before changing
code. Choose the delivery lane with `repository-delivery`: repository-owned
runtime changes are commit-first through CI/Coolify; infrastructure and Grafana
administration are backed up, applied live-first to the exact Coolify-owned
resource, verified, then reconciled in source.

After deployment, require evidence for all of these before moving the task to
`Verify`:

- exact deployed immutable SHA and Coolify owner;
- the original reproduction now behaves correctly with current data;
- two progressing samples when the fix concerns a worker, queue, or replay;
- affected metrics exist, are fresh, and have the expected measured value;
- a new real trace crosses the changed path with recorded span outcomes;
- Filebeat/Elasticsearch ingestion freshness is proven for the verification
  window, then correlated ECS log counts show no new scoped error, or document
  the exact remaining errors; a zero count without fresh ingestion is unknown;
- dependent data and host safety remain within measured bounds;
- the rollback artifact or previous immutable image is still identifiable.

Do not close an incident because one layer is healthy. If a required signal is
unavailable, report the observability gap as a separate actionable defect and
leave the corresponding conclusion `unknown/unverified`.

## Report evidence

Return a compact ledger with columns `claim`, `status`, `scope/window`,
`evidence source`, and `measured result`. Include exact trace IDs and immutable
commits outside secrets. End with the proven root cause, the fix, production
verification evidence, remaining unknowns, and rollback identity. If the root
cause was not proved, say so directly and list the next discriminating probe.
