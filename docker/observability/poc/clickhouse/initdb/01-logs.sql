-- clickhouse-log-writer (spec: "ClickHouse writers").
--
-- The Kafka table engine IS the consumer group. It commits offsets only after
-- the materialized view has written the block, which is the spec's "chi commit
-- Kafka offset sau khi ClickHouse xac nhan batch".
--
-- Ingest format is JSONAsString rather than JSONEachRow on purpose: the
-- canonical event is nested ECS (`service.name`, not `service_name`), and
-- pinning column names to a nested JSON shape would make every additive schema
-- change a breaking ClickHouse migration. Extracting from a single raw String
-- keeps the writer tolerant of new fields, which is what an additive
-- `schema.version` contract requires.

CREATE DATABASE IF NOT EXISTS observability;

CREATE TABLE IF NOT EXISTS observability.logs_canonical_queue
(
    raw String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'observability.logs.canonical.v1',
    kafka_group_name = 'observability-clickhouse-log-writer-v1',
    kafka_format = 'JSONAsString',
    kafka_num_consumers = 1,
    kafka_max_block_size = 100000,
    kafka_poll_max_batch_size = 10000,
    kafka_flush_interval_ms = 5000,
    kafka_handle_error_mode = 'stream';

-- ReplacingMergeTree keyed on event_id is what makes at-least-once delivery
-- safe: a replayed offset produces a row with an identical ORDER BY tuple, so
-- the duplicate collapses on merge. Queries that must not see a pre-merge
-- duplicate use FINAL or uniqExact(event_id) -- see poc/README.md.
CREATE TABLE IF NOT EXISTS observability.logs
(
    timestamp            DateTime64(9, 'UTC'),
    ingested_at          DateTime64(9, 'UTC'),
    event_id             String,
    event_dataset        LowCardinality(String),
    event_kind           LowCardinality(String),
    log_level            LowCardinality(String),
    message              String,
    service_name         LowCardinality(String),
    service_environment  LowCardinality(String),
    service_version      LowCardinality(String),
    service_instance_id  String,
    host_name            LowCardinality(String),
    container_id         String,
    container_image      LowCardinality(String),
    trace_id             String,
    span_id              String,
    http_request_id      String,
    rpc_request_id       String,
    schema_version       LowCardinality(String),
    raw                  String
)
ENGINE = ReplacingMergeTree
PARTITION BY toDate(timestamp)
ORDER BY (service_environment, service_name, timestamp, event_id)
TTL toDateTime(timestamp) + INTERVAL 30 DAY
SETTINGS index_granularity = 8192;

CREATE MATERIALIZED VIEW IF NOT EXISTS observability.logs_mv
TO observability.logs AS
SELECT
    parseDateTime64BestEffortOrZero(JSONExtractString(raw, '@timestamp'), 9, 'UTC')            AS timestamp,
    parseDateTime64BestEffortOrZero(JSONExtractString(raw, 'event', 'ingested_at'), 9, 'UTC')  AS ingested_at,
    JSONExtractString(raw, 'event', 'id')                                                      AS event_id,
    JSONExtractString(raw, 'event', 'dataset')                                                 AS event_dataset,
    JSONExtractString(raw, 'event', 'kind')                                                    AS event_kind,
    JSONExtractString(raw, 'log', 'level')                                                     AS log_level,
    JSONExtractString(raw, 'message')                                                          AS message,
    JSONExtractString(raw, 'service', 'name')                                                  AS service_name,
    JSONExtractString(raw, 'service', 'environment')                                           AS service_environment,
    JSONExtractString(raw, 'service', 'version')                                               AS service_version,
    JSONExtractString(raw, 'service', 'instance', 'id')                                        AS service_instance_id,
    JSONExtractString(raw, 'host', 'name')                                                     AS host_name,
    JSONExtractString(raw, 'container', 'id')                                                  AS container_id,
    JSONExtractString(raw, 'container', 'image', 'name')                                       AS container_image,
    JSONExtractString(raw, 'trace', 'id')                                                      AS trace_id,
    JSONExtractString(raw, 'span', 'id')                                                       AS span_id,
    JSONExtractString(raw, 'http', 'request', 'id')                                            AS http_request_id,
    JSONExtractString(raw, 'rpc', 'request', 'id')                                             AS rpc_request_id,
    JSONExtractString(raw, 'schema', 'version')                                                AS schema_version,
    raw                                                                                        AS raw
FROM observability.logs_canonical_queue
WHERE length(_error) = 0;

-- Parse failures are diverted rather than dropped, so a malformed canonical
-- record is visible instead of silently missing from analytics.
CREATE TABLE IF NOT EXISTS observability.logs_ingest_errors
(
    occurred_at DateTime DEFAULT now(),
    topic       LowCardinality(String),
    partition   UInt64,
    offset      UInt64,
    error       String,
    raw         String
)
ENGINE = MergeTree
ORDER BY (occurred_at, topic, partition, offset)
TTL occurred_at + INTERVAL 7 DAY;

CREATE MATERIALIZED VIEW IF NOT EXISTS observability.logs_ingest_errors_mv
TO observability.logs_ingest_errors AS
SELECT
    now()      AS occurred_at,
    _topic     AS topic,
    _partition AS partition,
    _offset    AS offset,
    _error     AS error,
    _raw_message AS raw
FROM observability.logs_canonical_queue
WHERE length(_error) > 0;
