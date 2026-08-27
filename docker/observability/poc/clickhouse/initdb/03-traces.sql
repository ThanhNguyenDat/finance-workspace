-- clickhouse-trace-writer (spec: "Tracing co duong luu vao ClickHouse").
--
-- Consumes the OTel Collector's dual-published OTLP/JSON span batches. Identity
-- is trace_id + span_id, which is what makes replay of observability.traces.v1
-- idempotent; the span table shares neither primary identity nor retention with
-- the log or trading-fact tables.

CREATE TABLE IF NOT EXISTS observability.traces_queue
(
    raw String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'observability.traces.v1',
    kafka_group_name = 'observability-clickhouse-trace-writer-v1',
    kafka_format = 'JSONAsString',
    kafka_num_consumers = 1,
    kafka_max_block_size = 100000,
    kafka_flush_interval_ms = 5000,
    kafka_handle_error_mode = 'stream';

CREATE TABLE IF NOT EXISTS observability.spans
(
    start_time      DateTime64(9, 'UTC'),
    end_time        DateTime64(9, 'UTC'),
    duration_ns     UInt64,
    trace_id        String,
    span_id         String,
    parent_span_id  String,
    span_name       LowCardinality(String),
    span_kind       LowCardinality(String),
    status_code     LowCardinality(String),
    status_message  String,
    service_name    LowCardinality(String),
    service_version LowCardinality(String),
    service_env     LowCardinality(String)
)
ENGINE = ReplacingMergeTree
PARTITION BY toDate(start_time)
ORDER BY (service_name, start_time, trace_id, span_id)
TTL toDateTime(start_time) + INTERVAL 14 DAY;

-- One Kafka record is an OTLP ExportTraceServiceRequest holding many spans, so
-- the view fans it out: resourceSpans -> scopeSpans -> spans. Resource
-- attributes are a key/value array in OTLP, hence the indexOf lookup rather
-- than a direct field read.
CREATE MATERIALIZED VIEW IF NOT EXISTS observability.spans_mv
TO observability.spans AS
WITH
    JSONExtractArrayRaw(raw, 'resourceSpans') AS resource_spans
SELECT
    toDateTime64(toUInt64(JSONExtractString(span, 'startTimeUnixNano')) / 1000000000, 9, 'UTC') AS start_time,
    toDateTime64(toUInt64(JSONExtractString(span, 'endTimeUnixNano')) / 1000000000, 9, 'UTC')   AS end_time,
    toUInt64(JSONExtractString(span, 'endTimeUnixNano'))
        - toUInt64(JSONExtractString(span, 'startTimeUnixNano'))            AS duration_ns,
    lower(JSONExtractString(span, 'traceId'))                               AS trace_id,
    lower(JSONExtractString(span, 'spanId'))                                AS span_id,
    lower(JSONExtractString(span, 'parentSpanId'))                          AS parent_span_id,
    JSONExtractString(span, 'name')                                         AS span_name,
    JSONExtractString(span, 'kind')                                         AS span_kind,
    JSONExtractString(span, 'status', 'code')                               AS status_code,
    JSONExtractString(span, 'status', 'message')                            AS status_message,
    attr_value(resource_span, 'service.name')                               AS service_name,
    attr_value(resource_span, 'service.version')                            AS service_version,
    attr_value(resource_span, 'deployment.environment.name')                AS service_env
FROM observability.traces_queue
ARRAY JOIN resource_spans AS resource_span
ARRAY JOIN JSONExtractArrayRaw(resource_span, 'scopeSpans') AS scope_span
ARRAY JOIN JSONExtractArrayRaw(scope_span, 'spans') AS span
WHERE length(_error) = 0;
