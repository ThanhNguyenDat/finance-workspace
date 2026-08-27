# OpenTelemetry tracing

## Purpose

Tracing exists to replace incident guesswork with a causal record. Metrics still
answer whether the system is unhealthy and ECS logs preserve detailed events;
traces connect one request or market event across process boundaries.

This rollout is trace-only:

```text
Finance service SDK --OTLP/gRPC--> OTel Collector --OTLP/gRPC--> Tempo --S3
        |                                 |                         |
        +-- ECS JSONL --> Filebeat/ES     +-- /metrics              +-- /metrics
        +-- /metrics --> vmagent/VictoriaMetrics
```

Do not send application metrics or logs through the Collector in this phase.
That would duplicate the existing VictoriaMetrics and Elasticsearch pipelines.

## Causal boundaries

- Finance MW HTTP/gRPC server spans propagate to its actual gRPC clients.
- Finance MW calls Live Action and Broker/MT5 as separate downstream paths.
  Live Action does not call Broker/MT5, so those paths must not be presented as
  one fabricated linear trace.
- A Kafka producer injects W3C TraceContext and Baggage into message headers.
  The consumer extracts those headers and owns the processing span through the
  durable commit. Replays without valid headers start a new trace.
- Health and `/metrics` probes are excluded from application tracing.

## Runtime configuration

Tracing is opt-in so an application rollout remains safe before the backend is
available:

| Variable | Default | Meaning |
| --- | --- | --- |
| `OTEL_TRACES_ENABLED` | `false` | Enable SDK/exporter startup. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://finance-otel-collector:4317` | Internal OTLP/gRPC endpoint. |
| `OTEL_EXPORTER_OTLP_INSECURE` | `true` | Plaintext is allowed only on the private Docker network. |
| `OTEL_SERVICE_NAME` | runtime name | Stable service identity. |
| `OTEL_SERVICE_VERSION` | build SHA/version | Immutable deployed identity. |
| `OTEL_SERVICE_INSTANCE_ID` | runtime instance | One container/process identity. |

Invalid tracing configuration fails startup instead of silently disabling the
diagnostic path. Shutdown gets a bounded flush window.

## Sampling and limits

The SDK head-samples every trace so the Collector can make a complete tail
decision. The Collector retains:

- every trace whose span status is `ERROR`;
- every trace with latency at least one second;
- 10% of normal traces.

The Collector is capped at 512 MiB/0.5 CPU with a 384 MiB memory limiter and a
bounded 1,000-batch exporter queue. Tempo is capped at 1 GiB/1 CPU. The initial
production trace retention is seven days. Revisit normal sampling and retention
only after measuring accepted spans, sampled traces, queue pressure and S3
growth per day.

## Data safety

Spans may include low-cardinality route, RPC method, messaging destination and
canonical instrument identity. They must never include credentials, bearer
tokens, cookies, raw request/response bodies, Kafka payloads, order payloads,
customer data or arbitrary exception dumps containing secrets.

ECS logs use independent request/event IDs. When an active span exists they also
carry real `trace.id` and `span.id`; never copy the request ID into either field.

## Local verification

The local override is the only supported filesystem-backed Tempo deployment. It
retains blocks for one hour and uses isolated Docker volumes:

```bash
docker compose \
  -f docker/observability/docker-compose.local-tracing.yaml \
  up -d tempo otel-collector
```

Resolve the internal container addresses and run the bounded controlled-error
test:

```bash
OTEL_INTEGRATION_ENDPOINT=http://COLLECTOR_IP:4317 \
TEMPO_INTEGRATION_URL=http://TEMPO_IP:3200 \
timeout --signal=TERM --kill-after=10s 45s \
go test -timeout=35s ./pkg/observability/tracing \
  -run TestCollectorTempoRetainsControlledErrorTrace -count=1 -v
```

The gate passes only when Tempo returns the exact trace ID with the expected
service name, service version and controlled error span.

## Production storage and rollout

Production Tempo must use the S3 backend in `tempo-production.yaml`; local disk
is not an acceptable substitute. Provision a dedicated bucket and least-
privilege credentials for that bucket. Configure a bucket lifecycle longer than
Tempo's seven-day retention to allow compaction/deletion to complete; never use
the bucket for unrelated data.

Before enabling the tracing profile:

1. create `/data/monitor/tempo/wal` with ownership matching the Tempo container;
2. provide `TEMPO_S3_ENDPOINT`, `TEMPO_S3_BUCKET`, `TEMPO_S3_ACCESS_KEY`,
   `TEMPO_S3_SECRET_KEY` and the correct `TEMPO_S3_INSECURE` value;
3. validate the exact Collector and Tempo configs with their pinned images;
4. start Tempo, then Collector, and verify both health and `/metrics`;
5. add the Grafana Tempo datasource and validate a direct TraceQL/query-by-ID;
6. enable `OTEL_TRACES_ENABLED=true` on one service, measure overhead/data loss,
   then expand one causal boundary at a time.

## Production acceptance gate

A deployment is not verified merely because containers are healthy. Record
evidence for all of the following:

- exact application, Collector and Tempo image revisions;
- Collector and Tempo healthy with restart count zero;
- both vmagent targets `up == 1`;
- accepted/exported spans increase while refused/failed spans remain zero;
- exporter queue remains below 80% and tail-sampling decisions increase;
- a controlled error can be queried by trace ID in Grafana/Tempo;
- the trace shows every real service boundary and immutable service version;
- the corresponding Elasticsearch ECS event contains the same real trace/span
  IDs without a credential or payload;
- existing `/metrics`, VictoriaMetrics, Filebeat and Elasticsearch flows have no
  duplicate or regression;
- host CPU, memory, disk and S3 growth remain within the recorded budget.

## Rollback

Set `OTEL_TRACES_ENABLED=false` to stop application export without disrupting
metrics or logs. If the backend is unhealthy, stop the `tracing` profile after
applications are disabled. Preserve the Tempo WAL and S3 bucket for diagnosis;
do not delete either as part of rollback. Restore the previous immutable images
if tracing instrumentation itself changes runtime behavior.
