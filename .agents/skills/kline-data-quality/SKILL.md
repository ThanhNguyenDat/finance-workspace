---
name: kline-data-quality
description: Audit, diagnose, repair, and optimize canonical Kline continuity across broker history, Kafka, Redis, Timescale, Finance MW, and the chart. Use when candles look missing, stale, truncated, duplicated, off-grid, or visually discontinuous; when adding an instrument or interval; and before claiming a chart gap is data loss.
---

# Kline Data Quality

Treat a visible chart discontinuity as a hypothesis. A grid slot absent from
Timescale is actionable only when the owning broker has a candle at that exact
open time. Session-based markets and no-tick periods legitimately omit candles;
never synthesize OHLCV, delete history, or reset offsets merely to make a chart
look continuous.

## Start with the complete route inventory

Use the canonical identity
`BROKER.MARKET_TYPE.BASE_ASSET.QUOTE_ASSET.INTERVAL`. Derive the instrument
inventory from the active application composition and worker inventory, and the
interval inventory from the shared market-data interval contract. Keep the
continuity workflow's expected-route assertion equal to their Cartesian product.
A green subset is not production evidence.

For the current production composition, the required surface is:

- `binance.perpetual_future.BTC.USDT`
- `binance.perpetual_future.XAU.USDT`
- `bybit.perpetual_future.BTC.USDT`
- `bybit.spot.XAUT.USDT` (Tether Gold spot, not XAU CFD/perpetual)
- `exness.cfd.XAU.USD`
- `exness.cfd.BTC.USD`
- intervals `5m,15m,30m,1h,2h,4h,12h,1d`

This is 48 routes. Update the inventory and its regression atomically whenever a
composition or chart interval changes.

Do not confuse the wire vocabulary with the active retention surface. A parser
may accept a broker's `1m` payload for compatibility, but production must not
subscribe, publish, consume, or expose that interval unless the historical
worker, chart, continuity workflow, and retention budget all own it. Compare
the producer stream list, Kafka topic discovery, historical backfill intervals,
chart selector, database route inventory, and metric labels. A route present in
only some of those places is shadow ingestion, not harmless extra data. Either
promote it everywhere and audit it, or disable it at the producer and consumer;
never let a partial route make the metric series count look more complete than
the audited inventory.

## Measure in ownership order

1. Query Timescale in a read-only transaction for every route: first and last
   open time, count, internal and trailing grid gaps, off-grid timestamps,
   invalid OHLCV, historical open flags, and duplicate open times.
   Check the requested retention boundary separately: an internal-gap query
   cannot detect history truncated before the first stored candle.
2. Verify every missing database timestamp against the owning broker:
   Binance Futures REST for Binance, public Bybit V5 REST for Bybit, and
   canonical `finance.MarketDataService` gRPC for Exness/MT5. Native venue
   codes may exist only inside the adapter.
3. If the broker also lacks the timestamp, classify it as
   `broker_session_or_no_tick_gap`. Preserve it and keep it out of actionable
   missing-candle counts.
4. If the broker returns a timestamp absent from Timescale, classify it as
   `collector_or_persistence_omission`. Then trace the exact canonical topic,
   Kafka producer/consumer offsets, Redis closed-candle queue and payload hash,
   flusher checkpoint, and database upsert before changing data.
5. Apply the five-minute closed-candle ingestion grace only to the live tail.
   It never exempts an older internal omission.
6. Verify the API and chart only after broker, Kafka, Redis, and Timescale are
   reconciled. A healthy container is not data progress.

Use `cmd/ops/kline-continuity-audit`, run by hand over guarded SSH per
`docs/runbooks/kline-maintenance-tools.md` (it is a production data-audit tool
for this service's own data, not repository-owned application code or its
deploy, so it never runs as a `.github/workflows/*.yml` file — see
`.agents/skills/repository-delivery/SKILL.md`'s "Ownership and Delivery
Lane"), as the canonical evidence path. Schema v2 distinguishes raw grid holes
from actionable broker-confirmed omissions:

- `grid_missing_candles`: every absent interval slot;
- `broker_native_missing_candles`: slots also absent at the broker;
- `total_missing_candles`: broker candles missing from persistence, or an
  unverified segment that must fail closed;
- `broker_unverified_missing_candles`: verification errors, never success.

## Keep broker verification bounded

MT5 returns at most 5,000 candles per request. For sparse gaps, request each gap
segment. For frequent session gaps, walk fixed 5,000-slot wall-clock windows and
match returned open times to missing segments. Choose the smaller request count.
Do not treat a short or empty MT5 page as end-of-history; it can be a fully closed
market window.

For five-year 5m retention, MT5 must allow at least 527,040 bars (five leap
years); production defaults to 600,000 for headroom. A route holding about
500,000 5m rows while slower intervals reach farther back is a terminal
`Charts/MaxBars` ceiling, not a PostgreSQL retention policy. Verify both the
container's `MT5_MAX_BARS` and the persisted UTF-16 `Charts/MaxBars` value after
deployment, then let the canonical worker backfill the newly exposed history.

Give the CLI an overall timeout and every broker call its own timeout. A CI probe
must use one exact temporary container on the `finance` network, enforce CPU,
memory, and PID limits, and remove that exact container with a trap. Never print
database URLs, broker credentials, raw log messages, or container environments.

## Repair only broker-confirmed omissions

Before a targeted repair, preserve the exact affected rows and Redis route keys.
Stop only the affected consumer. Reset only the canonical affected topics and
consumer group, remove only matching Redis queue/payload members, backfill from
the owning broker, and restart the exact consumer. Never flush shared Redis,
drop the database, reset unrelated offsets, or fill a session closure with fake
candles.

After repair, require two advancing lag/checkpoint samples, current database
tails across every interval, broker parity, API freshness, and chart behavior.
Run the 48-route `cmd/ops/kline-continuity-audit` again; success requires all
routes complete, zero actionable or unverified missing candles, zero invalid
candles, zero historical open flags, and zero duplicate open times.

Historical session markers are a separate, guarded metadata repair. First run
the canonical read-only continuity audit with broker verification. Then run
`cmd/ops/kline-gap-marker-backfill` in its default dry-run mode for one exact
`BROKER.MARKET_TYPE.BASE.QUOTE` plus interval, by hand over guarded SSH per
`docs/runbooks/kline-maintenance-tools.md`. Apply only with the exact dry-run
plan SHA-256, update count, and the prior reviewed dry-run's retained
evidence/backup files as `--reviewed-evidence`/`--reviewed-backup`. That first
dry-run must have written the exact source-bound plan and empty-state backup
before any later apply is permitted. The command rejects leading, off-grid, partial
broker-response, unverified, and conflicting-marker segments. A broker-verified,
on-grid trailing closed-session segment is bound into the full evidence digest
and reported as deferred because there is no following persisted candle that
can carry its marker; it never enters the mutation plan or blocks eligible
internal segments. An apply reloads both the reviewed plan backup and its
reviewed continuity evidence. A fresh audit may extend that one deferred
trailing segment only when its first timestamp is unchanged and its last
timestamp/count grow monotonically on-grid with zero broker candles and clean
broker verification. The complete internal segment inventory and the
database-eligible mutation entries must remain exactly equal to the reviewed
evidence and plan; a shortened or moved tail, any new segment, or any internal
evidence/marker drift fails before mutation. The command applies the exact
reviewed plan and digest rather than rebinding it to the moving tail, then
rechecks the route identity, predecessor,
target, and missing count in one serializable route-locked transaction and
conditionally updates only empty markers. Before an `--apply`, the operator
running the SSH procedure must independently confirm exact MW/Live Action
revisions, four distinct replay-ready workers, no concurrent BuildKit load,
stable restarts/replay growth, and host/DB headroom (see
`docs/runbooks/kline-maintenance-tools.md`'s preflight checklist) — this gate
used to run automatically inside the deleted CI workflow and is now the
operator's responsibility, not the command's. For Exness XAU only, aggregate
`worker_ready=0` is expected during the bounded weekend closure: all UTC
Saturday and Sunday before the observed 22:00 UTC reopen; Sunday at or after
22:00 and every missing dependency remain fail-closed. Run the tool inside the
source-built `finance-mw-kline-maintenance` scratch image without host bind
mounts (same Dockerfile the deleted workflow used, at
`docker/infrastructure/kline-maintenance/Dockerfile`), write an exact
pre-mutation backup, preserve before/plan/after artifacts, and rerun the full
read-only audit afterward. Any command receipt or post-audit failure restores
the empty marker backup under the same route lock; the operator must retain
that rollback/audit evidence, since there is no workflow artifact upload to
retain it automatically. Historical upserts and live appends must take that
same canonical `instrument_id:interval` advisory lock. Never update these
columns with ad-hoc SQL.

The canonical `kline.Kline` gRPC response carries
`gap_before_reason` field 16 and `gap_before_candles` field 17. These fields are
outbound authoritative metadata from Timescale. `Upsert` and `Upload` inputs
must not populate them, because a caller-provided marker has not passed Finance
MW's broker verification. Keep `proto/kline.proto` byte-identical with the
pinned Finance Live Action contract and preserve empty/zero as the fail-closed
default.

## Keep monitoring evidence honest

Materialize rare-event metric families at zero for every observed healthy route.
Prometheus cannot scrape a `CounterVec` label set that has never been touched;
without zero initialization, an invalid-candle dashboard and alert deployment say
`No data` until the first production failure. Use an explicit non-firing sentinel
reason such as `none`; real rejection reasons remain separate series.

Treat a client-cancelled server stream as normal lifecycle, not an application
error. Suppress only `context.Canceled` and gRPC `Canceled`; deadlines, storage
errors, decode failures, and broker failures remain actionable. In ECS, audit
error counts by `service.name`, `log.caller`, route labels, and time bucket before
reading message text. A burst at deploy time can be cancellation noise, but must
be proved rather than assumed.

Do not verify trading upstream identity by requiring the total number of port
50051 sockets to equal the number of Kline workers. Finance MW can legitimately
hold another gRPC connection to Finance Broker on the same port. Use the expected
worker count only as a socket lower bound, then probe every configured canonical
instrument and require each distinct worker to serve a current Kline.

Timescale chunk locks are part of the live-write budget. Never guard multiple
instrument/interval routes in one PostgreSQL transaction: a latest-watermark
query can lock hundreds of historical chunks, and accumulating those locks
across routes produces `pq: out of shared memory` even while the process remains
Docker-healthy. Group a flush deterministically by route, use one serializable
transaction and advisory lock per route, commit it, then advance to the next.
Partial route commits are safe only when queue removal waits for the whole flush
and retries are idempotent. Add an integration regression that proves an earlier
route remains committed when a later route fails continuity validation.

Do not launch the five-year continuity audit while a fresh deployment is still
replaying history. First require stable runtime/worker restart counters and
completed upstream replay; then run the audit. If PostgreSQL reports shared lock
exhaustion, cancel the read-only audit immediately, preserve the Kline queue, and
fix transaction/chunk-lock scope rather than raising limits blindly.

## Regression and delivery

Add a failing regression before fixing a reproducible gap. At minimum cover:

- the full instrument-by-interval inventory;
- dynamic broker, market type, base asset, and quote asset resolution;
- a broker-native closed-session gap that remains complete;
- a partial broker response where only broker-present timestamps are actionable;
- bounded MT5 pagination/window selection;
- `cmd/ops/kline-continuity-audit`'s and `cmd/ops/kline-gap-marker-backfill`'s
  exact route count, resource limits, timeout, and cleanup contract, and the
  SSH runbook's preflight/backup/rollback procedure that replaces what the
  deleted CI workflow used to automate.

Run bounded focused tests, the Go test suite covering both tools, `go test
-timeout=10m ./...`, `go vet ./...`, and `git diff --check`. Deliver source
changes through GitHub CI/CD and Coolify as usual; the tools themselves still
run by hand over guarded SSH per `docs/runbooks/kline-maintenance-tools.md`.
Finish with the production continuity audit plus current Kafka/Redis/DB/API,
Grafana `/metrics`, and ECS error-log checks. Record immutable evidence in
`raw/handoff_agent.md`; leave Codex-completed production work in `Verify`.
