---
name: trading-data-path
description: Diagnose and change the live data path carrying trading state from finance-live-action workers through finance-mw to the browser. Use when snapshots, metrics, candles, or trade history are missing, stale, or slow in the web app, and before changing any gRPC payload, stream, or gateway between the two repositories.
---

# Trading Data Path

State reaches the browser as `worker → gRPC → finance-mw → WebSocket → SPA`. The
ledgers are almost never the problem. Every outage traced in this path so far was
transport: a payload that outgrew a limit, a stream nobody was reading, or a
failure that no one logged.

## Diagnose by measuring, not by reading logs

A dashboard showing nothing had **complete data in every ledger**. The snapshot
carrying it was 5.71 MB against a 4 MB gRPC receive limit, so the stream died on
its third message of eleven and the browser never saw the scopes that mattered.

Nothing in the logs said so. `TradingController.TradingStream` closes the socket
through `writeWebSocketGatewayClose` **without logging**, so a fatal gateway error
leaves no trace at all.

Reason about the path in this order, and measure at each step:

1. **Is the data in the worker?** `docker logs <worker> | grep "replay applied"`,
   and the unary `ListHistoryTrades` for a specific `scope_id`.
2. **Does it survive the wire?** Write a throwaway gRPC client, run it inside the
   `finance` network from the worker's own image, and print `proto.Size` per
   message. This is the step that finds size limits, and it is the step that gets
   skipped.
3. **Does finance-mw forward it?** Access logs record `event.duration`; a browser
   WebSocket that lives ~1.5s and repeats is an upstream failure, not a client.
4. **Does the SPA render it?** Only now is the frontend worth reading.

Build the probe against `finance-mw`'s generated `internal/pb/webdata`, statically
(`CGO_ENABLED=0`), and run it with the worker's image rather than `alpine`, which
is musl and cannot exec a glibc binary. Delete it from the host afterwards.

## Counting upstreams on production

To answer "is finance-mw actually connected to every worker", count sockets rather
than trusting logs or config:

```bash
c=$(docker ps --format '{{.Names}}' | grep '^mw-' | head -1)
pid=$(docker inspect --format '{{.State.Pid}}' "$c")
nsenter -t "$pid" -n ss -tn state established \
  | awk '$4 ~ /:50051$/ {print $4}' | sed -E 's/:50051//' | sort -u
```

Then map those peer IPs back to worker containers. Five things get this wrong, each
of which produced a false conclusion at least once:

- **`state established` drops the State column.** Peer address is `$4`, not `$5`.
  Match the port explicitly; a worker also accepts connections on `:8002`, so
  grepping the bare IP counts a socket that is not the WebData stream.
- **Workers sit on more than one network.** Read the IP for the `finance` network
  specifically, not the first one the template emits, or the values concatenate.
- **Containers vanish between `docker ps` and `docker inspect`** during a rolling
  deploy. Skip a container whose inspect fails instead of reading the empty result
  as a bad state — otherwise every deploy looks like an outage.
- **Coolify injects environment at runtime.** `docker inspect .Config.Env` omits it
  and will report a configured variable as unset. Read
  `tr '\0' '\n' < /proc/$pid/environ` and grep the one key you need; these
  environments hold credentials, so never dump them whole.
- **A count below the worker count is normal mid-deploy.** Streams break and
  reconnect while containers are replaced; `stream_hub.go` logs the failure and
  retries with backoff. Only a shortfall that persists across several minutes means
  anything.

The count that matters is unique worker IPs on `:50051` versus running workers. When
they differ and the gap holds, compare the running instrument identities against
the canonical `BROKER.MARKET_TYPE.BASE.QUOTE` keys of
`TRADING_GRPC_UPSTREAM_BY_INSTRUMENT`. An identity absent from that map can fall
back to the default client and serve another market's numbers under its own name.

An instrument is not live-action-enabled merely because it appears in the SPA.
Adding one requires one atomic inventory change across the owning worker Compose,
`TRADING_GRPC_UPSTREAM_BY_INSTRUMENT`, vmagent/prom-agent scrape targets, the
expected upstream count and distinct-instrument production probe. Once that worker
exists, sidebar health must come from typed trading metrics; the DB/Redis Kline
probe is only the fallback for a deliberately market-data-only instrument. Keep
the venue's volume semantic explicit in the chart — MT5 supplies tick volume, not
Binance-style base or quote amount.

## Payload rules

0. **Market identity is structured.** Kafka `MarketEventV2`, gRPC, HTTP, and SPA
   requests carry `broker`, `market_type`, `base_asset`, and `quote_asset`. Do not add
   `symbol`, `canonical_symbol`, or `native_symbol` back to the envelope or
   kline body, and do not make finance-live-action parse broker symbol formats.
   The canonical map key is `BROKER.MARKET_TYPE.BASE.QUOTE`, normalized as
   `binance.perpetual_future.BTC.USDT`; the Kafka topic adds the interval as
   `market.kline.v2.BROKER.MARKET_TYPE.BASE.QUOTE.INTERVAL`. Broker adapters may
   compose a venue-native code only at the outbound API/SDK boundary. There is no
   legacy concatenated-pair compatibility path in development.
1. **Streams carry live state; history is fetched.** Closed-trade history grows
   with every replayed day and has no ceiling. It belongs to the unary
   `ListHistoryTrades`, never to a stream message.
2. **Audit every field, not the obvious one.** The ledger appeared twice: in
   `history_trades_json` and again as the `trades` array inside
   `trade_state_json`. Removing the first left 2.6 MB behind and the stream still
   broke. Grep for every place a ledger is serialized before declaring a payload
   small.
3. **Raise the receive limit as defence, not as the fix.** Go's gRPC default is
   4 MB (`MaxCallRecvMsgSize` in `web_data_client.go`); tonic's is set on the
   service. Both are raised, but a payload that needs them is already wrong.
4. **Project venue precision conservatively at an integer contract boundary.**
   Bybit's risk-limit ladder can contain a fractional `maxLeverage` even when
   the instrument's general leverage range has whole-number endpoints. The
   funding protobuf and live-action validation use `uint32`, so floor a positive
   fractional tier maximum and reject values below `1`, non-finite values, and
   overflow. Never round to nearest or up: advertising leverage above the venue
   maximum weakens the downstream risk gate.

## Container health is not trading readiness

A green Docker health check proves only the dependency/liveness contract chosen
by that container. It does not prove historical replay completed, market events
are flowing, or strategies evaluated. When a dashboard has no numbers, compare
`finance_live_action_worker_ready` with
`finance_live_action_kline_history_ready`, the collected/required history
gauges, and the evaluation counter. `grpc_serving`, Kafka, and Redis can all be
healthy while the worker correctly reports `not_ready`.

Treat a restart loop in `kline-ingest`'s ingest pipeline (briefly folded
into `trading-worker` on 2026-08-23, split back into its own container on
2026-08-24, source nested under `cmd/worker/trading-worker/kline-ingest/`)
as part of the same data path. One observed
failure had current repositories querying `instruments`/`instrument_id` while the
complete Atlas migration stream still created `symbols`/`symbol_id`. Both live
workers stayed healthy at the container level but collected only 4/200 candles,
and ingest exited on every topic-discovery attempt. Before resetting a database,
replay the committed migration stream against a disposable PostgreSQL instance
and compare its final columns and indexes with generated Ent schema. A clean
database recreated from stale migrations reproduces the outage instead of
repairing it.

Redis is outside that reset boundary and can retain broker/instrument entities
forever. A cache-first repository can therefore recreate instruments with broker
UUIDs that no longer exist in PostgreSQL, leaving `instruments > 0` while
`brokers = 0`; topic discovery then fails or ingest stops on `broker not found`.
Keep PostgreSQL authoritative for broker and instrument identity reads, use
Redis only as write-through acceleration, and remove orphan dependents before
orphan instruments in the reset recovery migration. Verify table counts and
container stability after the rollout instead of assuming a successful Atlas
apply also reset external caches.

### Broker-current, storage-stale recovery

For terminal-backed brokers such as MT5, an old database cursor may be outside
the broker's retained history window. An empty or short page at that cursor does
not prove that current candles are unavailable. Compare these timestamps and
depths before changing data:

1. newest candle returned by a direct canonical broker gRPC request;
2. PostgreSQL `max(open_at)` for the exact instrument and interval;
3. Kafka producer offset, consumer offset, and lag for the exact canonical
   topics; and
4. Redis closed-candle route, sorted-set queue, and payload-hash depth for the
   same canonical routes.

Fix producer replay/idempotence first. The worker must recover from a stale
cursor within its page budget and advance a monotonic published watermark only
after Kafka accepts the batch. Otherwise cleanup merely starts another duplicate
flood.

Do not interpret every interval-sized hole as data loss for session-based
markets. CFDs can close overnight or over a weekend. Keep continuity strict for
always-open markets, but let a CFD flusher cross a closure only after an
authoritative broker repair contains the same first candle currently blocked in
the queue. Broker responses may include an overlap before that candle; discard
the overlap and validate the accepted suffix's canonical identity, closed state,
interval grid, and monotonic timestamps before advancing the database watermark.

The same session rule applies to pagination. A broker request for 500 wall-clock
slots can legitimately return fewer than 500 CFD candles, including zero for a
fully closed window. Never treat that short page as end-of-history. Full recovery
must walk fixed time windows backwards from the oldest durable candle to the
configured lookback boundary; incremental sync remains forward from the newest
watermark. This separation prevents the production failure where every interval
stopped at its first page and 5m appeared as exactly 500 candles.

Kafka offset reset is not a Redis reset. Records already materialized into
`kline:ingest:closed:{BROKER.MARKET_TYPE.BASE.QUOTE.INTERVAL}:queue` and its
`payloads` hash survive a consumer-group reset and can repopulate PostgreSQL with
old candles. For an authorized reseed, stop only the affected consumer, back up
the exact PostgreSQL rows and Redis route keys, reset only the affected Kafka
topics, remove only the matching Redis queue/payload keys and route-set members,
then delete the matching database rows and restart the consumer. Never flush the
shared Redis instance or reset unrelated broker routes.

Finish by verifying two lag samples (to prove the backlog is not growing), a
current database `max(open_at)` for every configured interval, direct broker
freshness, container health, and the dashboard/API result. Do not embed runtime
UUIDs, hostnames, passwords, or other production credentials in this skill.

## Stream fanout

`finance-mw` holds **one upstream stream per worker per surface**, started before
any browser connects and never stopped. Client count changes only the
mw-to-browser connections.

- `streamHub` in `internal/interfaces/http/stream_hub.go` owns this. Snapshots and
  metrics coalesce per scope; candles queue with a bounded backlog because they
  are events, not state that supersedes itself.
- A worker publishes every context on one stream: `StreamSnapshots` and
  `StreamAllTradingMetrics`. `StreamKlines` with an empty interval covers every
  timeframe, which is why `Kline` carries its own `interval`.
- **Keepalive is required.** When a worker container is replaced its address
  disappears without resetting the old socket, so `Recv` blocks forever, no error
  is raised, and the reconnect loop never runs. Two workers sat with no upstream
  while the logs stayed clean.
- **Serving from a shared stream must not turn a rejection into silence.** A
  request naming an unknown scope would match nothing, so the metrics path still
  validates it against the worker with a unary call before subscribing.

## Known issue: Kafka topic race on coordinated restart

`kline-ingest`'s pipeline (briefly folded into `trading-worker` on
2026-08-23, split back into its own container on 2026-08-24 — the race
itself is a property of the producer/consumer restart timing, not of which
container the producer runs in, so it remains an open concern regardless of
which side of that fold the code was on) and a
`live-action-<instrument>` worker restarting within the same window (a deploy,
a host-level Coolify redeploy) can race the Kafka broker's topic metadata.
Observed on production 2026-08-08: both restarted ~10:16 UTC, and for several
minutes both sides logged `UnknownTopicOrPartition` — `kline-ingest`'s producer
failed to write (`[BinanceWS] base_asset=XRP quote_asset=USDT kafka
write error=[3] Unknown Topic Or Partition`) and the worker's consumer failed
to subscribe (`Subscribed topic not available:
market.kline.v2.binance.perpetual_future.xrp.usdt.<interval>`) across all
eight intervals simultaneously. The topic exists; the race is the consumer
subscribing before the broker has finished registering it after a restart.

**User-visible effect:** for the ~20-minute window until the race cleared,
`/v1/klines/sources` served real-looking but wrong-magnitude candles for the
affected instrument (BTC/USDT showed ~$75 against a real ~$65,000 — a consistent,
slowly-drifting series, not an obvious zero/sentinel, which is why it read as
live data on the chart rather than an error state). Confirm any recurrence
against the timestamp of the nearest coordinated restart before assuming a
new bug.

**It self-heals — do not delete data on sight.** The existing replay/reconcile
path (`"Skipping duplicate or stale replay of closed kline"`, once a minute)
re-validates recent candles against the authoritative source once the Kafka
race clears, and silently overwrites the wrong values. Verified by re-querying
`/v1/klines/sources?before_ts=<window>` for the same open_times minutes apart:
first response showed ~$75, second showed the correct ~$65,000 for the
identical `ts` values. No manual deletion or backfill was needed or performed.

**Diagnose:** `docker logs --since <window> <container> | grep -iE
'error|warn'` on both `kline-ingest` and the affected `live-action-<instrument>`
worker; a topic-not-available error appearing on both sides for the same
instrument/interval in the same few minutes is this issue, not a genuine outage.
Cross-check with `docker ps --format '{{.Names}}\t{{.Status}}'` — both
containers showing a similarly short `Up` duration confirms the coordinated
restart.

**Open, unfixed:** nothing currently orders `kline-ingest`'s startup
ahead of the workers it feeds, or retries a consumer's topic subscription past
this specific race. It will recur on the next restart that happens to land both
sides in the same window; treat a repeat with the same signature as this
known issue rather than re-investigating from scratch, but a real fix
(subscription retry-with-backoff on `UnknownTopicOrPartition`, or a startup
dependency between the two) is still open.

## Sizing the load before adding to it

Every measurement here was taken on production and is worth repeating rather than
trusting:

- `klines:*` Redis keys are a rebuildable daily cache over PostgreSQL, not the
  candle ledger. It is safe to expire/delete whole-day cache keys by date
  retention when PostgreSQL remains authoritative; it is not safe to apply broad
  Redis eviction while the same instance also holds worker checkpoints and ingest
  queues.
- One worker with one strategy: ~110 MiB of a 512 MiB ceiling once replay
  completes. Roughly 16 MiB per additional strategy.
- Contexts are `8 x strategies + 3`. Every snapshot embeds the full context list,
  so the stream cost is quadratic in context count. At eleven contexts it is
  4.9 KB; at eight hundred it is hundreds of megabytes per tick.
- Saving a checkpoint used to build a `serde_json::Value` tree of the whole
  runtime state before producing the string, holding three copies of a year of
  trades on every closed candle. It is raw JSON now, and that alone cut peak
  memory ~2.8x.

Comparing many strategies is a research workload. Run it in `finance-research`,
which streams candles once and keeps only aggregates, not in the workers whose
memory, checkpoints and streams all scale with context count.

## Required validation

```bash
cd finance-live-action
cargo fmt --all -- --check
timeout --signal=TERM --kill-after=30s 15m cargo test --workspace

cd ../finance-mw
go vet ./...
go test -race ./internal/interfaces/http/...
cd web && npm test -- --run && npm run build
```

Run the Go HTTP package with `-race`: the hub is concurrent, and a slow-reader
bug there stalls every viewer of an instrument rather than one.

## Stop conditions

Stop when the change is covered by a test that fails without it, the suites above
pass, and any production claim was measured rather than inferred. A claim about
what production will do after a deploy is not a result; the measurement after the
deploy is.

## Closed-candle revision telemetry

The scheduled Binance REST sync deliberately republishes an overlapping tail so
the canonical candle can absorb late trades. An exact replay is idempotent; a
same-`open_time` payload with changed OHLCV is an accepted revision, not by itself
a history-quality failure. Keep a separate revision counter for diagnosis. Only
gap, invalid checkpoint/candle, fatal validation, or sustained unreadiness should
drive the Telegram history-quality alert.

## Continuity audit live tail

Production persistence is asynchronous at the candle boundary. The strict
continuity audit therefore applies a fixed five-minute grace measured from the
candle's close time; it does not exempt a whole interval. Record that grace in
the evidence artifact. Once the grace expires, a missing trailing candle fails
exactly like an internal gap, and any older one-candle gap always fails. Without
this boundary the 5m and 15m routes can all report the same false gap during the
few minutes after a shared close, hiding the difference between ingestion delay
and missing history.
