# Bug investigation: kline-ingest keeps running (or crashes blindly) on bad data

Status: investigation only — root cause documented, **nothing fixed**. For
Codex to implement, then review a second time independently before this is
considered done (explicit user request: two separate passes).

## User's question, verbatim intent

1. "1 bug incident, dữ liệu kline bị miss (hư), tại sao worker vẫn chạy tiếp
   được?" — a kline-data-missing/corrupted incident happened; why does the
   worker keep running as if nothing happened?
2. "dữ liệu trước chưa có tại sao dữ liệu mới lại được insert success vào?"
   — if prior/earlier candle data doesn't exist, why does a newer candle
   still get inserted successfully?

Both questions turned out to have real, different, previously-undocumented
answers. Researched via a grounded code-reading pass (Explore agent, all
citations below independently traceable to file:line — not generalized).

## Headline finding: two distinct services, two distinct answers — and neither matches "keeps running as if nothing happened"

- **finance-mw's `kline-ingest` (Go)** — the service actually named in the
  bug report — does **not** silently continue on corrupt data. A single
  corrupted candle event **crashes the entire ingest process** (every
  route it serves, not just the offending one), and because the Kafka
  offset is never committed for that message, Docker's
  `restart: unless-stopped` brings the process back up, it re-fetches the
  exact same poison message, and crashes again — an **indefinite,
  alert-less crash-loop with no dead-letter/skip mechanism**. This is
  arguably worse than "ignores it": it's "silently self-destructs
  repeatedly," and the one metric that would explain *why* is never wired
  to any alert.
- **finance-live-action (Rust)** — the service that actually owns the
  "quality error 0" metric cited repeatedly in this session's incident
  postmortems (`raw/handoff_codex.md` lines ~410, ~417) — genuinely does
  enforce: quality errors flip `history_ready=false` and, in most call
  sites, `panic!()` the process immediately. **This is not the same
  metric** as finance-mw's `kline_invalid_total`, despite the similar name
  — anyone citing "quality error 0" as evidence about the Go
  `kline-ingest` worker's health is citing the wrong service.

## Root cause 1 — corrupt candle: crashes the whole process, not "keeps running"

`finance-mw/internal/interfaces/worker/kline_ingest.go`:
- `KlineEventSink.Process` (47–79) is the entry point for every kline event
  off Kafka. Line 57 calls `invalidKlineReason(record)` (81–112), which
  checks: NaN/Inf price, non-positive price, `close_before_open`,
  `negative_volume`, `high_below_low`, `high_below_body`, `low_above_body`.
- On invalid: line 58 increments `finance_mw_kline_ingest_invalid_total`
  (defined `pkg/metrics/metrics.go:152–157`, incremented via
  `RecordInvalidKline` at 233–241), line 66 returns an error — no cache
  write, no enqueue, correctly refuses to persist garbage.
- That error propagates up through `KlineKafkaConsumer.Run`
  (`kline_consumer.go:60–150`, error return at 122–131) — on error, `Run()`
  returns before committing the Kafka offset (commit only happens after
  `Process` succeeds), and its `defer` (67–71) closes **every** topic
  reader, not just the one that saw the bad message.
- `RunKlineIngest` (`internal/initialize/kline_ingest.go:112–130`) receives
  this error via a `done` channel, logs
  `"Kline ingest component stopped unexpectedly"`, and calls `cancel()` —
  which tears down the sibling `binance_websocket` worker too. The whole
  `kline-ingest` binary then exits (`main()` in `cmd/kline-ingest/main.go`
  returns).
- `docker/compose.worker.yaml:4` sets `restart: unless-stopped` on the
  shared config the `kline-ingest` service uses (14–29). Docker restarts
  the process, the consumer resumes from the **last committed offset**
  (i.e. before the poison message), re-fetches the same corrupt event,
  crashes again.
- `pkg/kafka/reader.go` / `writer.go`: no dead-letter queue, no
  max-retry-then-skip, no per-offset backoff anywhere. Checked all
  exported functions.

**Net effect:** one bad candle from any single route can crash-loop the
entire multi-route ingest process indefinitely, and the metric that names
the reason (`kline_invalid_total{reason=...}`) has **zero** Grafana
coverage — confirmed via `grep -n "invalid_total"
scripts/deploy_grafana_alerts.py docker/monitor/grafana/*.json
scripts/validate-grafana-dashboards.py`, no matches anywhere. On-call would
only see a generic "container restarting," never the actual cause, unless
someone manually queries Prometheus.

## Root cause 2 — missing candle: no crash, but no DB-level continuity guarantee either

Separate path, `finance-mw/internal/interfaces/worker/kline_flusher.go`:
- `KlineDBFlusher.Flush` (64–148) fetches `newest` = latest DB candle for
  the route (`NewestOpenTime`, `db_repository.go:151–170` — a plain
  `ORDER BY open_at DESC LIMIT 1`, no locking).
- `selectContiguousClosedKlines(newest, candidates)`
  (`kline_ingest.go:137–187`) is the **only** continuity check anywhere in
  the pipeline: it requires each candidate's `OpenAt` to equal
  `cursor.Add(step)`, cursor starting at `newest.OpenAt`. The first
  candidate that breaks this, and everything after it, is excluded from
  `ready` and withheld from the write batch.
- If a gap exists (`len(ready)==0`), `appendGapRepair` (208–258) calls the
  broker REST API to backfill (`kline_gap_repairer.go:25–61`); on repair
  failure it just logs a `Warn` and continues — no alert beyond the
  gap-gauge (below), retried every flush cycle (default 5 min,
  `internal/initialize/kline_ingest.go:77–80`) indefinitely, no retry cap.
- **This continuity check has an explicit bypass**: for `market_type ==
  "cfd"` (`marketAllowsClosedSessionGaps`, `kline_flusher.go:260–262`),
  `brokerConfirmedSessionKlines` (264–316) writes broker-confirmed candles
  starting at the blocked candle's `OpenAt` **without** re-running
  `selectContiguousClosedKlines` against `newest` — i.e., for CFD/forex
  routes only, a permanent hole between `newest` and the new candles is
  written on purpose (broker-confirmed session closure), with **no DB-level
  marker** distinguishing this intentional gap from any other kind of hole.
  Crypto/perpetual-future routes get no equivalent distinction (see
  `raw/handoff_codex.md`'s already-documented `market_closed`/
  `data_missing` chart-badge work — that's a *frontend display* decision
  consuming whatever's already in the DB, it does not gate writes).
- **The actual write function has zero enforcement of its own**:
  `KlineDBRepository.UpsertBatch` (`db_repository.go:23–89`) is a bare
  `ent` bulk `CreateBulk(...).OnConflictColumns(OpenAt, InstrumentID,
  Interval).Update(...)` — no `WHERE EXISTS(prior candle)` guard, no
  sequencing constraint, no unique/exclusion constraint enforcing
  contiguity (the `OnConflictColumns` key only prevents *duplicate* rows,
  not gaps). It will write any candle slice handed to it, contiguous or
  not. Continuity is **application-layer convention in one call site**,
  not a schema or repository guarantee — nothing stops a future refactor,
  an admin backfill script, or a different worker from calling
  `UpsertBatch` directly with a gapped slice and having it succeed silently.
- No transaction/lock spans the `NewestOpenTime` read and the later
  `UpsertBatch` write, and the CFD gap-repair path can run concurrently
  with the main batch path for the same route within one `Flush()` — a
  theoretical race where both paths compute "contiguous relative to
  `newest`" against an already-stale `newest`.

**This directly answers the user's second question**: a new candle gets
inserted successfully even when prior data is missing because (a) the CFD
bypass writes through a known gap by design, and (b) even outside that
bypass, the only thing preventing it is one call site's discipline — the
database and the write function itself have no opinion on continuity at
all.

## What IS alerted vs. what is purely observational

- `finance_mw_kline_ingest_gap_missing` (Gauge,
  `pkg/metrics/metrics.go:146–151`, set via `kline_flusher.go:115–122`) —
  **has** a real alert: `scripts/deploy_grafana_alerts.py:295–318`, rule
  `finance-mw-kline-gap-blocked`, fires after 5 minutes of nonzero gap,
  rendered on dashboard `finance-mw-prod` panel 54.
- `finance_mw_kline_ingest_invalid_total` (Counter, corrupt-OHLC) — **no**
  alert, **no** dashboard panel anywhere. Purely observational.

## Adjacent mechanisms checked — none of them cover this

- **No-lookahead** (finance-live-action) validates temporal ordering of
  trading-decision evidence, not OHLC correctness or candle presence.
- **History readiness** (finance-live-action) is tied to
  `record_history_quality_error()` — real enforcement, but it's a
  finance-live-action concept with no finance-mw equivalent; the Go
  ingest worker has no "readiness" gate for downstream consumers at all.
- **Kafka consumer lag** alerts measure offset drift, not message content —
  a corrupt candle processed immediately produces no lag signal before the
  crash; lag only appears as a side effect once the crash-loop starts
  piling up unread messages behind it.

## Fix direction — not applied, for Codex to design and implement

Two independent problems, likely two independent fixes:

1. **Corrupt-candle crash-loop.** Do not let one poison Kafka message take
   down the whole multi-route process. Options to weigh (Codex's call):
   skip-and-commit-offset for a message that fails `invalidKlineReason`
   (with the existing counter as the audit trail) instead of propagating a
   process-fatal error; and/or route-scope the failure so one bad route
   doesn't tear down every reader in `KlineKafkaConsumer.Run`'s shared
   `defer`. Either way, wire `kline_ingest_invalid_total` into Grafana
   (dashboard panel + alert) so this stops being silent regardless of
   which containment strategy is chosen.
2. **Missing continuity guarantee at the write layer.** Decide whether
   `UpsertBatch`/`KlineDBRepository` should itself refuse or flag
   non-contiguous writes (defense in depth, not just single-call-site
   discipline), and whether the CFD broker-confirmed-gap path should write
   an explicit marker (a boolean column, a separate small table, anything
   queryable) distinguishing "intentional broker-confirmed session gap"
   from "unexplained hole" — right now the two are indistinguishable at
   read time by row shape alone.

Both fixes should add regression coverage that currently doesn't exist:
a corrupt-event test asserting the process does *not* crash the whole
consumer, and a continuity test asserting `UpsertBatch` (or a new guard in
front of it) rejects/flags a gapped batch outside the CFD bypass.

## Verification checklist (for whoever implements + re-verifies)

- [ ] Confirm `invalidKlineReason`'s error no longer propagates to a
      process-fatal path (or, if the design keeps a fatal path, confirm
      it's scoped to the single offending route/topic, not all readers).
- [ ] Confirm the Kafka offset advances past a genuinely corrupt message
      instead of crash-looping on it forever (test with a poison-message
      fixture, verify offset commits and ingestion continues for other
      messages on the same topic).
- [ ] Confirm `kline_ingest_invalid_total` has a Grafana panel and an
      alert rule with a sane threshold/duration, deployed the same way as
      `finance-mw-kline-gap-blocked`.
- [ ] Confirm whatever continuity guard is added actually rejects a
      synthetic gapped batch passed directly to the repository layer (not
      just via the existing `Flush()` call site).
- [ ] Confirm the CFD broker-confirmed-gap path still works after any
      write-layer guard is added (it must remain the one legitimate way to
      write through a real gap) — add/keep a fixture test for this.
- [ ] Production: after deploy, confirm live `kline_ingest_invalid_total`
      and `kline_ingest_gap_missing` for all 32 routes (per Codex's
      concurrent 32-route audit, `raw/handoff_codex.md`'s
      "P0 — Audit và fix toàn bộ gap dữ liệu klines production" item —
      cross-reference that item's findings, don't re-derive them) show the
      expected steady state, and that a deliberately-injected bad message
      (staging, not production) no longer crash-loops the container.
- [ ] Codex: do a second, independent review pass of both the fix and this
      investigation doc before marking done — this was an explicit user
      request (two review passes, not one).
