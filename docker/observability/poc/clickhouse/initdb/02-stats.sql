-- clickhouse-stats-writer (spec: "Contract event thong ke va toi uu chien thuat").
--
-- Separate topic, separate consumer group, separate tables, separate retention
-- from the log branch. A log storm must not be able to slow or drop a closed
-- trade fact, and log retention must never delete the source of a research
-- dataset.

CREATE DATABASE IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.trading_events_queue
(
    raw String
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'analytics.trading.events.v1',
    kafka_group_name = 'analytics-clickhouse-stats-writer-v1',
    kafka_format = 'JSONAsString',
    kafka_num_consumers = 1,
    kafka_max_block_size = 100000,
    kafka_flush_interval_ms = 5000,
    kafka_handle_error_mode = 'stream';

-- Raw fact: append-only, event-time ordered, deduplicated on the producer's
-- stable event.id. This is the audit/rebuild layer; nothing writes back to it.
CREATE TABLE IF NOT EXISTS analytics.trading_events
(
    occurred_at        DateTime64(9, 'UTC'),
    ingested_at        DateTime64(9, 'UTC'),
    event_id           String,
    event_type         LowCardinality(String),
    portfolio_id       String,
    source_sequence    UInt64,
    trading_mode       LowCardinality(String),
    is_replay          UInt8,
    broker             LowCardinality(String),
    market             LowCardinality(String),
    base_asset         LowCardinality(String),
    quote_asset        LowCardinality(String),
    raw_symbol         String,
    interval           LowCardinality(String),
    strategy_name      LowCardinality(String),
    strategy_version   LowCardinality(String),
    model_version      LowCardinality(String),
    feature_version    LowCardinality(String),
    decision           LowCardinality(String),
    reason_code        LowCardinality(String),
    confidence         Float64,
    quantity           Float64,
    gross_pnl          Float64,
    realized_pnl       Float64,
    fee                Float64,
    funding            Float64,
    slippage           Float64,
    holding_seconds    UInt64,
    service_version    LowCardinality(String),
    trace_id           String,
    raw                String
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(occurred_at)
ORDER BY (portfolio_id, event_type, occurred_at, event_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.trading_events_mv
TO analytics.trading_events AS
SELECT
    parseDateTime64BestEffortOrZero(JSONExtractString(raw, 'event', 'occurred_at'), 9, 'UTC') AS occurred_at,
    parseDateTime64BestEffortOrZero(JSONExtractString(raw, 'event', 'ingested_at'), 9, 'UTC') AS ingested_at,
    JSONExtractString(raw, 'event', 'id')                     AS event_id,
    JSONExtractString(raw, 'event', 'type')                   AS event_type,
    JSONExtractString(raw, 'portfolio', 'id')                 AS portfolio_id,
    JSONExtractUInt(raw, 'source', 'sequence')                AS source_sequence,
    JSONExtractString(raw, 'trading', 'mode')                 AS trading_mode,
    toUInt8(JSONExtractBool(raw, 'trading', 'replay'))        AS is_replay,
    JSONExtractString(raw, 'instrument', 'broker')            AS broker,
    JSONExtractString(raw, 'instrument', 'market')            AS market,
    JSONExtractString(raw, 'instrument', 'base_asset')        AS base_asset,
    JSONExtractString(raw, 'instrument', 'quote_asset')       AS quote_asset,
    JSONExtractString(raw, 'instrument', 'raw_symbol')        AS raw_symbol,
    JSONExtractString(raw, 'instrument', 'interval')          AS interval,
    JSONExtractString(raw, 'strategy', 'name')                AS strategy_name,
    JSONExtractString(raw, 'strategy', 'version')             AS strategy_version,
    JSONExtractString(raw, 'strategy', 'model_version')       AS model_version,
    JSONExtractString(raw, 'strategy', 'feature_version')     AS feature_version,
    JSONExtractString(raw, 'decision', 'outcome')             AS decision,
    JSONExtractString(raw, 'decision', 'reason_code')         AS reason_code,
    JSONExtractFloat(raw, 'decision', 'confidence')           AS confidence,
    JSONExtractFloat(raw, 'trade', 'quantity')                AS quantity,
    JSONExtractFloat(raw, 'trade', 'gross_pnl')               AS gross_pnl,
    JSONExtractFloat(raw, 'trade', 'realized_pnl')            AS realized_pnl,
    JSONExtractFloat(raw, 'trade', 'fee')                     AS fee,
    JSONExtractFloat(raw, 'trade', 'funding')                 AS funding,
    JSONExtractFloat(raw, 'trade', 'slippage')                AS slippage,
    JSONExtractUInt(raw, 'trade', 'holding_seconds')          AS holding_seconds,
    JSONExtractString(raw, 'service', 'version')              AS service_version,
    JSONExtractString(raw, 'trace', 'id')                     AS trace_id,
    raw                                                       AS raw
FROM analytics.trading_events_queue
WHERE length(_error) = 0;

-- Derived aggregate. Deliberately NOT a SummingMergeTree over the MV stream:
-- a summing aggregate would add a replayed closed trade to PnL a second time,
-- which is exactly the failure the spec forbids. Instead the daily view is a
-- plain view over the deduplicated raw fact, so replay is idempotent by
-- construction and the aggregate can always be rebuilt from raw/S3.
CREATE VIEW IF NOT EXISTS analytics.daily_strategy_pnl AS
SELECT
    toDate(occurred_at)              AS trade_date,
    portfolio_id,
    strategy_name,
    strategy_version,
    broker,
    raw_symbol,
    count()                          AS closed_trades,
    -- Aliases must NOT reuse the source column name: ClickHouse resolves the
    -- alias first and then reads sum(realized_pnl) as an aggregate over an
    -- aggregate (ILLEGAL_AGGREGATION).
    sum(realized_pnl)                AS realized_pnl_total,
    sum(gross_pnl)                   AS gross_pnl_total,
    sum(fee)                         AS fee_total,
    sum(funding)                     AS funding_total,
    sum(slippage)                    AS slippage_total,
    countIf(realized_pnl > 0) / nullIf(count(), 0) AS win_rate,
    max(ingested_at)                 AS watermark
FROM analytics.trading_events FINAL
WHERE event_type = 'closed_trade' AND is_replay = 0
GROUP BY trade_date, portfolio_id, strategy_name, strategy_version, broker, raw_symbol;
