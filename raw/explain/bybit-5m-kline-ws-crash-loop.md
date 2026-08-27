# Bybit 5m kline WS stream stuck in crash-loop — root cause and evidence (Round 120, 2026-08-23)

## Symptom

Both live Bybit routes (`bybit.perpetual_future.btc.usdt.5m`,
`bybit.spot.xaut.usdt.5m`) report `evaluation_count` climbing normally in
Redis checkpoints (worker loop alive), but `recent_klines`' last bar is
frozen at `open_time=2026-08-23T06:00:00Z` / `close_time=06:04:59.999Z` for
both routes, while wall-clock time is already past `06:53Z` — a 45+ minute
and growing staleness gap, confirmed static across three checkpoint reads
20s/2min/4min apart (see Round 120 handoff entry for the raw numbers). All
buffered Bybit klines also show `trades=0` and `taker_buy_volume=0` for
every bar, vs. Binance BTC's same-window kline showing real non-zero values
(`trades: 7221`, `taker_buy_volume: 80.48`).

Comparing `finance-live-action` worker container logs for the same 20-minute
window: `live-action-binance-perpetual-future-btc-usdt-*` processed 8 `5m`
interval Kafka events; `live-action-bybit-perpetual-future-btc-usdt-*`
processed **zero** `5m` events (only `1h`/`2h`, 46+14 events) in the same
window — the Portfolio's actual base interval for Bybit is silently
starved while higher timeframes look fine, which is why container health
checks and `evaluation_count` alone did not catch this.

## Root cause — confirmed via production log

Checked the actual kline producer, `finance-kline-ingest-1` (not
`finance-mw-1` — kline ingestion is a separate binary/container,
`cmd/kline-ingest/main.go` → `internal/initialize/kline_ingest.go:116` →
`worker.NewWSWorker().Run` → `internal/interfaces/worker/ws.go:44` →
`services.NewBybitWSService(...).Run`). Its logs for the last 15 minutes
show a tight crash-and-reconnect loop specific to the BTC linear instrument:

```
[BybitWS] instrument=bybit.perpetual_future.BTC.USDT websocket connected   (x5 in 15min)
[BybitWS] instrument=bybit.perpetual_future.BTC.USDT receiver exited retry=1 retry_in=2.1s
  error=Bybit returned 2 kline records in one stream update               (x4 in 15min)
```

The error string traces to `internal/services/bybit_ws_service.go:285-288`:

```go
func normalizeBybitKlineEvent(payload bybitKlineWSPayload, instrument marketdata.InstrumentIdentity, receivedAt time.Time) (marketdata.EventV2, error) {
	if len(payload.Data) != 1 {
		return marketdata.EventV2{}, fmt.Errorf("Bybit returned %d kline records in one stream update", len(payload.Data))
	}
	...
```

`receiver()` (same file, lines 156-232) treats any error from
`normalizeBybitKlineEvent` as fatal for the whole WS connection — it
`return`s out of the `receiver` loop (line 221), which propagates back to
`Run()`'s reconnect loop with a short backoff (~2s, from the log). A single
WS push containing 2 kline records (which Bybit's public V5 `kline` topic
can legitimately send — the topic's `data` array is not documented as
always length 1) is enough to tear down and reconnect the **entire**
per-instrument connection, including every other interval subscribed on the
same socket (`bybitKlineSubscription` subscribes all `ActiveKlineIntervals`
topics on one connection per instrument, lines 234-257). Whatever is
recurring right after each reconnect for this instrument keeps re-triggering
the same 2-record push, so the loop never gets past it — evidenced by 5
reconnects and 4 identical crashes in the 15-minute window, with the last
successfully-ingested `5m` bar dating to before this log window even
started.

`1h`/`2h` topics keep advancing because they change far less often and are
simply less likely to be the specific topic carrying the offending 2-record
push in any given cycle; they are not on a separate connection — they ride
the same socket and get reset too, but recover in between crashes since a
1h/2h bar is unlikely to need a new value inside any single 2-second retry
window.

## Why this wasn't caught by the standing "worker healthy" checks

`live-action-bybit-*` containers report `(healthy)` and `evaluation_count`
keeps climbing throughout — the worker's own health check and cycle counter
don't depend on receiving new market data, only on the process loop
running. The staleness is entirely upstream, in `finance-kline-ingest-1`'s
WS receiver, and only visible by cross-checking `recent_klines`' actual
timestamp against wall clock and by reading `finance-kline-ingest-1`'s own
logs (not `finance-mw-1`, which is the API/gRPC container and logs nothing
about Bybit — confirmed empty grep over its lifetime since its `06:48:05Z`
restart).

## Scope

- Confirmed affecting **both** Bybit routes' `5m` interval specifically
  (BTC linear proven directly via logs; XAUT spot checkpoint shows the
  identical frozen `06:00-06:05Z` bar, consistent with the same connection
  crash-loop pattern since spot uses the same `BybitWSService` code path,
  just a different WS URL).
- `bybit_enabled: true` confirmed both in-repo (`config/grpc.yaml`) and in
  the actually-running container config (`docker exec finance-kline-ingest-1`
  — checked the mounted `grpc.yaml`, not an env dump). `TRADING_INSTRUMENT_IDENTITIES`
  (`internal/interfaces/worker/consts.go`) correctly lists both Bybit
  instruments and `INTERVALS` includes `5m`. This is not a config or
  wiring gap — the connection is attempted, subscribes correctly, and the
  crash is purely in per-message payload handling.

## Suggested fix direction (Codex's call, not decided here)

`normalizeBybitKlineEvent`'s `len(payload.Data) != 1` check is the failure
point. A push with more than one record should very likely process every
record in the array (in order) rather than reject the whole message —
Bybit's own kline WS topic is not guaranteed single-record per push. This
is a payload-handling fix scoped to one function; it does not touch
Binance's WS code path or shared decision logic.

## Resolution (Round 121-124, 2026-08-23/24)

Fixed at the source: `normalizeBybitKlineEvent` → `normalizeBybitKlineEvents`,
processes every record in `payload.Data` instead of rejecting `!= 1`; `EventID`
keyed per-record instead of message-level. Commit `60e16bab`, deployed, CI
green. Ingest-layer crash-loop confirmed stopped (>10min clean logs, was
crashing every ~2s before). `trades=0`/`taker_buy_volume=0` on Bybit klines
confirmed as correct-by-design (Bybit V5 payload has no such field), not a
mapping gap as originally suspected.

Downstream catch-up took longer than the ingest fix itself: the MW redeploy
that shipped this fix caused live-action's gRPC connection to get cancelled
mid-call, triggering the known fail-closed panic/restart, which then had to
replay months of history through finance-mw's single-concurrent-stream gate
(`defaultMaxConcurrentHistoryStreams=1`) shared with 15 other pending
interval streams at the time — this contention (not a new bug) is what made
catch-up slow, and is the same gate mechanism documented in full in
`raw/explain/kline-stream-gate-capacity-saga.md`. Both Bybit routes'
`recent_klines` were confirmed caught up to within ~4.5 minutes of wall
clock by Round 124 (2026-08-24). Closed.
