# Market Data → Live Action Runbook

This is the starting point for future sessions working on the Finance MW and
Finance Live Action market-data path. It intentionally contains no passwords,
tokens, or provider secrets.

Architecture review and editable diagrams:

- [End-to-end review with Mermaid](../diagram/finance-live-action-workflow.md)
- [Multi-page Draw.io source](../diagram/finance-live-action-workflow.drawio)

## Repositories

- Middleware and web:
  `/home/lap13330/Desktop/finance-eco-system/software/finance-mw`
- Strategy workers:
  `/home/lap13330/Desktop/finance-eco-system/software/finance-live-action`

Read each repository's `AGENTS.md` before editing.

## Production data flow

```text
Binance perpetual-futures WebSocket (realtime 1m/5m/15m/1h/4h)
  ┐
  ├→ normalized MarketEventV2 → Kafka topic market.kline.v2.{broker}.{market_type}.{base}.{quote}.{interval}
  │                            ├→ kline-ingest persistence consumer
  │                            │  → Redis priority queue → DB flusher
  │                            │  → PostgreSQL/Timescale historical klines
  │                            └→ one finance-live-action symbol worker
  │                               → filter active 5m/15m/1h/4h MTF bundle
  │                               → route/history gate
  │                               → candle_momentum strategy
  │                               → per-strategy/per-interval Alpha ledgers
  │                               → persistent Alpha-position evidence
  │                               → 5m-primary multi-timeframe Portfolio gate
  │                               → four Portfolio rule ledgers
  │                               → Redis checkpoint → Kafka offset commit
  │                               → gRPC → finance-mw WebSocket/API → browser
  │
Scheduled Binance REST sync (5m/15m/30m/1h/2h/4h/12h/1d)
  ┘
```

Important invariants:

- Finance Live Action must not connect directly to a broker WebSocket or REST
  endpoint for market data.
- Kafka is the durable source of truth.
- Redis is the warm restart checkpoint and CPU-recovery optimization.
- For a closed event that mutates TradingRuntime state, the Kafka offset is
  committed only after that state is checkpointed. Open events do not evaluate
  or mutate the durable trading state; they are broadcast and acknowledged
  without a runtime checkpoint.
- Every event carries explicit `broker`, `market_type`, `base_asset`,
  `quote_asset`, `interval`, and `is_final`. Neither the envelope nor its kline
  payload carries `symbol`, `canonical_symbol`, or `native_symbol`; broker
  adapters normalize their native identifier before publishing.
- Kafka topics are split one per
  `broker.base_asset.quote_asset.market_type.interval` route. `kline-ingest`'s
  persistent ingest pipeline discovers the active symbol registry at startup
  and opens one reader per pair and interval; finance-live-action derives the
  same eight evaluated topics from `BROKER`/`MARKET_TYPE`/`BASE_ASSET`/`QUOTE_ASSET`.
  Legacy `MARKET_DATA_TOPIC` overrides are ignored. Adding a symbol or interval
  therefore requires restarting both `kline-ingest` and the corresponding
  finance-live-action worker.
- There is one Kafka consumer group per symbol worker. `KAFKA_GROUP_ID` owns the
  identity; its default is derived from
  `broker.market_type.base_asset.quote_asset.primary_interval`. That same consumer filters the
  worker's `5m`, `15m`, `1h`, and `4h` subscriptions from its own pair topic.
  Different symbol workers must not share a group.
- Each symbol worker subscribes eight active decision intervals:
  `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`, `1d`.
- With the current single default strategy, each worker exposes 17 execution
  contexts: 1 runtime parent, 8 Alpha contexts, and 8 Portfolio contexts.
- Portfolio evidence comes from persistent Alpha ledger positions, not directly from
  the current raw strategy signal.
- Snapshot streams carry live state only. Closed history is fetched separately
  with scoped unary `ListHistoryTrades`.
- Finance MW owns exactly one snapshot, metrics, and all-interval kline upstream
  gRPC stream per worker and fans those streams out to browsers.
- Finance MW also owns public perpetual funding-history retrieval through
  `funding.FundingService`. Binance settlements include the exchange's signed
  rate and exact mark price. Bybit funding history carries the signed settlement
  rate/time but omits its mark; MW enriches it from the public hourly mark-price
  kline whose open timestamp exactly equals the settlement boundary. Missing or
  mismatched venue mark observations fail closed; trade-candle closes are never
  substituted.
- Selecting a symbol in the web changes application state only. It must not
  navigate to a `live-action-*` host or call a worker directly.

## Interval ownership

The interval sets are intentionally different by layer:

| Layer | Current intervals | Meaning |
| --- | --- | --- |
| MW protobuf/schema | `1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`, `1d` | Canonical contract and storage universe |
| Binance realtime ingest | `1m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`, `1d` | Published to one `market.kline.v2.{broker}.{market_type}.{base}.{quote}.{interval}` topic per interval |
| MW scheduled REST sync | `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`, `1d` | Backfill producer to the same per-interval Kafka topics; `1m` is realtime-only |
| Live Action Alpha/Portfolio | `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `12h`, `1d` | Synchronized MTF decision bundle; Portfolio executes on the primary `5m` clock |
| Web interval catalog | `5m`, `15m`, `30m`, `1h`, `4h`, `1d` | Strategy catalog; operational Grafana views cover all eight evaluated intervals |

Consequences:

- `1m` is already present in the realtime Kafka data plane, but the live-action
  consumer intentionally rejects it because no `1m` Alpha/Portfolio context,
  role/weight, or replay stream is configured.
- `30m`, `2h`, `12h`, and `1d` arrive over realtime WebSocket and are also
  repaired by scheduled REST sync; all eight evaluated intervals feed Live Action.
- Adding an interval to Live Action is a policy and state-schema change, not
  just an ingest subscription change. Update subscriptions, context inventory,
  MTF roles/weights, primary clock, metrics validation, replay selection and
  replay/checkpoint contract version together.

## Current trading-mode boundary

The runtime path currently ends at Alpha and Portfolio:

- Active default strategy: `candle_momentum`.
- Alpha: one ledger per `strategy × interval`, fixed `$5` notional, no protective
  levels, hold until reversal.
- Portfolio: one aggregate 5m-primary decision is applied to four independent rule
  ledgers: `fixed-pct`, `compounding-pct`, `fixed-atr`, and
  `compounding-atr`.
- Live safety/risk/cost/halt/reconciliation contracts exist in
  `finance-core`, but they are not wired into the worker runtime.
- No Broker execution context is currently created and worker API state reports
  `has_broker_keys=false`.

Do not present the standalone Binance order adapter as production Live Futures.
It is not orchestrated by `finance-api` and currently targets the Spot order
endpoint while the production market-data route is perpetual futures.

## Current build-phase scope

Only these groups are active:

- Large Cap: 6 workers
- Memecoin: 8 workers
- Commodity: 1 worker

Expected production total: **15 workers**.

Altcoin workers are intentionally excluded from CI/CD and monitoring during the
build phase.

The current Binance route is `market_type=perpetual_future`. Keep native
Futures symbols such as `1000PEPEUSDT`, `1000BONKUSDT`, `1000SHIBUSDT`,
`MEWUSDT`, and `XAUUSDT`; do not silently substitute Spot symbols.

## Contract and implementation entry points

Finance MW:

- Broker ingest and normalization:
  `internal/services/binance_ws_service.go`
- Persistent WebSocket -> Kafka -> Redis/PostgreSQL ingest pipeline:
  `internal/initialize/kline_ingest.go` (`RunKlineIngest`), entry point
  `cmd/worker/trading-worker/kline-ingest/main.go` — a separate binary and
  container from `trading-worker`, nested in its source tree since both are
  the trading business domain, so a stuck reconnect in one can't starve the
  other
- Dedicated scheduled-job entry points, one per business domain:
  `cmd/worker/trading-worker/main.go`, `cmd/worker/english-worker/main.go`,
  `cmd/worker/social-worker/main.go`, `cmd/worker/tvl-worker/main.go`
- Kafka writer:
  `pkg/kafka/writer.go`
- Kafka topic configuration:
  `docker/config/grpc.yaml`
- Active symbol registry:
  `internal/interfaces/worker/consts.go`
- Web composition registry:
  `web/src/constants/compositions.ts`
- Production runtime env:
  `docker/env/production.env`

The `cmd/server` process does not start background workers. Four domain
workers each own one business domain's schedule, in independent processes so
one domain's failure or resource use cannot starve another's:
`finance-trading-worker` (Kline sync), `finance-tvl-worker` (TVL analysis),
`finance-english-worker` (English lessons), and `finance-social-worker`
(Facebook, Threads, and the automation smoke check). Calendar jobs use
`Asia/Ho_Chi_Minh`, preserve the established cadence, and have per-run
timeouts plus Prometheus lifecycle metrics. Each domain worker is the sole
schedule owner for its own jobs and starts its native scheduler
unconditionally. `kline-ingest`, `trading-worker`, `english-worker`,
`social-worker`, and `tvl-worker` all run in the worker Coolify application,
independently from the request-serving runtime.
The persistent broker WebSocket -> Kafka -> Redis/PostgreSQL ingest pipeline
runs in its own `kline-ingest` container, separate from `trading-worker`'s
`kline_sync`/`kline_sync_full` scheduled jobs — same trading business
domain, independent process so a stuck WebSocket reconnect can't starve the
periodic sync jobs or vice versa.

Finance Live Action:

- Canonical event contract:
  `crates/finance-core/src/market_event.rs`
- Kafka consumer and manual acknowledgement:
  `crates/finance-kafka/src/consumer.rs`
- Worker processing order:
  `crates/finance-api/src/main.rs`
- Worker route configuration:
  `crates/finance-api/src/config.rs`
- Redis checkpoint contract:
  `crates/finance-redis/src/checkpoint.rs`
- Metrics:
  `crates/finance-api/src/metrics.rs`
- Kafka-only architecture guard:
  `scripts/verify-worker-data-plane.sh`
- Production env:
  `docker/env/production.env`

## Restart and recovery

On startup, a worker loads the Redis checkpoint for its exact broker, market
type, symbol, and interval route. The checkpoint contains recent klines,
serialized runtime state, and the last applied Kafka topic/partition/offset.
Runtime state includes Alpha/Portfolio ledgers, Portfolio evidence, pending 5m primaries,
the last processed primary, and historical replay continuation markers.

Before consuming forward data, historical Alpha/Portfolio replay streams the active
four klines from
Finance MW's KlineService. Completed UTC days are served from the MW Redis
day-cache when available and otherwise from PostgreSQL/Timescale. The four
interval streams are merged by close time with deterministic same-close ordering
`5m → 15m → 1h → 4h`.

For perpetual workers, historical replay also loads signed settlements from
Finance MW's FundingService before evaluating trades. The forward runtime uses
the same contract, starts with fixed-rate fallback disabled, and refreshes the
authoritative schedule every 60 seconds. A missing exact mark, upstream error,
or authentication failure is surfaced and does not silently switch back to the
configured estimate. Non-perpetual workers do not apply perpetual funding.
Funding calls send the credential from
`FINANCE_MW_GRPC_BEARER_TOKEN`; Finance MW accepts that service token only for
the read-only FundingService method. Configure the same non-empty value on both
applications and never commit it to either repository.

For each new closed event the worker:

1. validates the normalized route;
2. validates closed-kline continuity and history readiness;
3. updates Alpha ledgers and Portfolio evidence/rules;
4. saves the Redis checkpoint;
5. publishes the in-process update;
6. acknowledges the Kafka delivery.

If Redis checkpointing fails, the Kafka offset remains uncommitted. After a
restart, Kafka can replay the event without losing state. Redis avoids rebuilding
the entire strategy history and reduces restart CPU pressure.

Warm checkpoints expire after 24 hours without a refresh. A worker also keeps
only the newest contiguous Kline suffix: when the next event is more than three
intervals newer than the cached tail, it drops the stale prefix instead of
drawing a misleading gap across months or years. Checkpoint schema changes
invalidate incompatible cached runtime state on deployment.

Historical trading semantics are also versioned independently by
`HISTORICAL_REPLAY_CONTRACT_VERSION`. Changing Alpha/Portfolio replay behavior
requires a version bump so stale replay ledgers are rebuilt rather than silently
continued under new rules.

## Kline processing latency monitor

Metric:

`finance_live_action_kline_processing_duration_seconds`

The histogram label `finality` has two bounded values:

- `open`: the exchange may still update the kline;
- `closed`: the exchange marked the kline final.

The measured interval starts when the worker receives a Kafka delivery and
includes strategy evaluation and Redis checkpointing.

Grafana panels:

- `Kline Processing Latency — Open vs Closed`
- `Live Action Kline Processing Latency — Open vs Closed`

Both show p50 and p95 for `open` and `closed`.

Dashboard sources:

- `docker/observability/grafana/finance-live-action.json`
- `docker/observability/grafana/finance-mw-runtime.json`

Worker metrics copy the market identity from the consumed Kafka event. Grafana
therefore renders series as `BTC/USDT · binance perpetual_future` instead of
the ambiguous raw symbol `BTCUSDT`.

The Finance Live Action selector displays `BTC/Binance-Futures` while retaining
the exact `broker|market_type|symbol` route as its query value. Spot and Futures
workers with the same native symbol therefore remain distinct.

Production dashboards:

- `https://admin-grafana.thanhne.io.vn/d/finance-mw-prod`
- `https://admin-grafana.thanhne.io.vn/d/finance-live-action-prod`

## Production alert evaluation

Production does not run Prometheus, vmalert, or Alertmanager. Runtime metrics
flow through vmagent into VictoriaMetrics, and Grafana evaluates the production
alert rules through its Prometheus-compatible datasource.

The alert source of truth is `scripts/deploy_grafana_alerts.py`. It renders the
rules, links each alert to a diagnostic dashboard panel, configures the
`finance-telegram` contact point, and verifies the live Grafana copy. The
Telegram audience is the trade admin bot and the named admin selected from
`pkg/telegram/telegram.go`; do not copy chat IDs or bot tokens into docs,
workflows, or issue comments.

System Monitoring rules use the same `finance-telegram` policy. They cover host
scrape loss, filesystem space at 80% or more, RAM at 90% or more, sustained CPU
at 90% or more, and inode use at 85% or more. Each condition must persist for
fifteen minutes (except the five-minute scrape-loss rule) to avoid transient
pages. The source dashboard is `docker/observability/grafana/finance-host-runtime.json`;
it is deployed into `System Monitoring` with the other versioned dashboards.

There is intentionally no generic container-health rule: production does not
scrape cAdvisor, so `container_*` metrics are absent. Before each deploy and
verify, the script queries the Grafana VictoriaMetrics datasource's live
`__name__` values and fails if a required alert metric is absent. Add a
container-specific alert only after its metric is confirmed there; a plausible
expression that selects no series is not monitoring.

Grafana and the metrics agents are durable Coolify resources. Apply dashboard,
alert, contact-point, datasource, or collector changes live-first over the
guarded production SSH lane against the exact Coolify-owned resource. After the
live queries pass, commit the matching sources. The default-branch
`.github/workflows/verify-observability.yml` is deliberately verify-only;
it reads Grafana and fails if a rule is missing, paused, linked to the wrong
folder or panel, querying a drifted expression, or routed to the wrong contact
point. It must never create a native container or mutate Grafana.

There is no inactive reference rule file. Production paging requires adding or
updating Grafana live, committing the matching rule source, and running the
observability verification workflow.

## Configuration and CI/CD

### Production environment hard rule

All production environment values for both repositories live in
`docker/env/production.env`, except `BROKER_CREDENTIAL_ENCRYPTION_KEY`. That
key is a repository-scoped GitHub Secret delivered to the `finance-mw` runtime
through the audited CI/Coolify deployment path. Never commit or print its
value.

The runtime image copies `docker/env/production.env` into the container.
The container entrypoint sources that file with automatic export before starting
the application. Compose must not inject, resolve, or duplicate the file-backed
production values. Coolify remains a deployment transport; its runtime
environment stores only the broker-credential encryption key and immutable
image tag managed by CI.

### Coolify destination/network hard rule

**Every service started through Coolify must use the external Docker network
`finance` as its destination network. Do not use a Coolify-generated default
network or another destination.**

Every production Compose file must declare the external network and attach every
application, worker, and supporting container that participates in this data
path:

```yaml
networks:
  finance:
    name: finance
    external: true
```

The same startup contract applies to Finance MW and Finance Live Action:

1. Dockerfile copies `docker/env/production.env`.
2. Entrypoint fails closed if the file is missing.
3. Entrypoint sources and exports the file.
4. Application starts only after the production file is loaded.

Finance MW:

- Workflow: `.github/workflows/pipeline-ci-cd.yml`
- Trigger: push to `main`

Finance Live Action:

- Workflow: `.github/workflows/build-deploy.yaml`
- Deploy from `main`: manual `workflow_dispatch`
- Active deploy matrix: Large Cap, Memecoin, Commodity

Useful verification commands:

```bash
# finance-mw
go test ./...
go vet ./...
go build ./cmd/server
python3 scripts/validate-grafana-dashboards.py
npm test --prefix web -- --run
npm run build --prefix web

# finance-live-action
cargo fmt --all -- --check
cargo test --workspace --no-fail-fast
bash scripts/verify-worker-data-plane.sh
docker compose --env-file docker/env/production.env \
  --file docker/compose.large-cap.yaml config --quiet
```

Dashboard deployment and verification use the
`Finance Production Observability` GitHub Actions workflow. Dispatch it from
the default branch, select `deploy` or `verify`, and use the `production`
environment audit gate. Workstations must not SSH into production
or call the Grafana write API directly.

## Authentication

Username/password, Telegram-delivered one-time tokens, OAuth authorization-code
redirects, database-scoped groups, CSRF, CORS allowlisting, and application
rate limits are documented in
[`authentication-authorization.md`](authentication-authorization.md).

Never document actual credentials in either runbook. Production values belong
in `docker/env/production.env`, except for the broker-credential encryption key
described above.
