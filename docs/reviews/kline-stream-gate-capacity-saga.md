# `KlineService/Stream`'s 1-slot gate — full saga (Round 122-134)

Consolidated from scattered entries across `docs/archive/legacy-handoff-agent.md` (Round 122,
123, 125, 128, 129, 132, 133) so future rounds don't have to re-read the
whole sprawl to understand current state. This doc is a reference, not a
live task list — its references to `docs/archive/legacy-handoff-agent.md`'s
`## Todo`/`## Done` describe the historical workflow; current work is tracked in
OpenSpec and OPS.

## What the gate is

`kline_service_server.go:28-51` — `defaultMaxConcurrentHistoryStreams = 1`,
enforced via `klineStreamGate` (`stream_admission.go`), a `chan struct{}`
semaphore of capacity 1. Every `KlineService.Stream` RPC call — used both for
`finance-live-action`'s historical replay bootstrap AND for
`finance-research`'s ad-hoc backtest CLI AND for `GetOldestOpenTime` — must
acquire this single slot before decoding begins. Intentional, per the code's
own comment: "Production evidence showed two concurrent streams repeatedly
crossing that limit" — a memory-safety guard for Finance MW's 512 MiB
cgroup, not a bug.

## Timeline

- **Round 120-121:** Bybit kline WS crash-loop (separate root cause, in
  `finance-kline-ingest-1`, already closed — see
  `bybit-5m-kline-ws-crash-loop.md`) triggered a historical-replay bootstrap
  for both Bybit routes.
- **Round 122:** Discovered the gate itself while trying to backtest a new
  Vortex Indicator candidate — CLI hung `DeadlineExceeded`. Root-caused to
  the 1-slot gate being saturated by the ongoing Bybit backfill (16
  concurrent streams: 2 instances × 8 intervals contending for 1 slot).
- **Round 123:** Found a second contributing mechanism in
  `finance-live-action`: `bootstrap_pending_intervals`
  (`historical_replay.rs:160`) opens all pending intervals as separate
  streams; the merge loop propagates ANY single stream's error via `?`,
  aborting the WHOLE 8-interval batch and retrying from a fixed `from_time`
  — under gate contention, retries out-paced real progress (near-livelock).
  Self-implemented the fix (retry only the failed interval, not the whole
  batch) — FLA commit `bc4e74f`.
- **Round 124:** Bybit backfill confirmed fully caught up. But then
  misdiagnosed the gate as still blocked by "4 other routes' pending
  history backfill" — **this diagnosis was WRONG** (see Round 125).
- **Round 125:** Corrected Round 124: `pending_history_backfill` is an
  unrelated, purely local Kafka out-of-order-kline buffer
  (`trading_api.rs::record_closed_kline`), nothing to do with the gRPC
  gate. The REAL cause of the gate being stuck in both Round 124 and 125:
  **this session's own local research-CLI containers**, leaked because
  `timeout ... docker run ...` (used to bound the CLI's runtime) only kills
  the CLI/attach process, not the underlying container — confirmed via
  `docker ps -a --filter ancestor=finance-research-local:latest` finding a
  still-`Up` container after `timeout` reported the shell command killed.
  Fixed the local tooling habit: always `docker run -d --name X` +
  `docker kill X && docker rm -f X`.
- **Round 127:** Implemented and deployed a real production fix:
  `grpc.KeepaliveParams(Time: 30s, Timeout: 10s)` on Finance MW's gRPC
  server (`internal/interfaces/grpc/server.go`, commit `1adff58`) — so a
  client that dies without a clean stream-close no longer wedges its
  handler goroutine forever.
- **Round 128-129:** Verified the keepalive fix's deploy, but found
  `in_flight` still pinned at 2 even on a **genuinely fresh** `finance-mw-1`
  process (confirmed via `ps -o etimes` on PID 1, not just Docker's
  `StartedAt`) — ruling out dead-client leaks entirely for this instance.
  Root-caused a **4th, distinct mechanism**: `GetOldestOpenTime`
  (`kline_client.go:94-114`) opens the same gated `Stream` RPC with NO
  `From`/`To` bound just to read one record then cancel; combined with
  `trading_worker.go`'s **4-hour** `StartupTimeout` on the worker's first
  job run after restart (not the 10-minute recurring `Timeout` — a
  mid-round correction), a stuck/abandoned call from
  `kline_sync_full`'s startup burst (16 instrument×interval combinations,
  hit by connection-refused/DNS/GOAWAY during the redeploy transition)
  could hold the gate for up to 4h. Deliberately did NOT rush a fix in the
  same round (touches `GetOldestOpenTime`'s public contract and job
  scheduler startup-timeout semantics).
- **Round 132:** Implemented the targeted fix:
  `context.WithTimeout(ctx, 10*time.Second)` in `GetOldestOpenTime`
  (commit `e5e4351`), independent of the caller's own context lifetime —
  guarantees the call itself can never hold the gate past 10s regardless of
  caller behavior.
- **Round 133 — honest experimental verification (not just "should work"):**
  - ✅ `finance_mw_grpc_requests_total{code="Unknown"}` for Stream climbed to
    **48** right after redeploy (previously never exceeded 2) — direct
    proof calls that used to hang forever now complete/time-out correctly.
  - ✅ A real `--days 1` request succeeded in 14s with clean data.
  - ⚠️ But `--days 7`, `--days 90`, and `--days 1825` requests all hung
    (zero bytes of output, `stream_messages_total{sent}` flat) for minutes
    — not a leak (cleanly killed via `docker kill`+`rm -f`, `in_flight`
    dropped back to baseline correctly each time) but genuine **capacity
    contention**: multiple legitimate consumers (worker `kline_sync`/
    `GetOldestOpenTime` calls, this CLI, etc.) all compete for the same 1
    slot, so anything that takes more than an instant is exposed to being
    starved by whatever else is active at that moment.
  - **Conclusion:** both fixes (Round 127 keepalive, Round 132 timeout) are
    correct and necessary — they close the "leak" failure mode — but they
    do NOT increase capacity. The gate remaining a scarce, contended
    resource under real load is an **architectural limit**, not a bug.
- **Round 134:** Retried a `--days 7` backtest — hung again (56s, zero
  output) despite no visible trading-worker activity in the same window.
  Confirms the capacity constraint is still live and somewhat
  unpredictable in timing; did not chase further this round (see "Not yet
  done" below — deliberately not rushed).
- **Round 135-138:** Repeated retries (small windows, different times),
  mixed results — `sent` counter proven to move over hours (real periodic
  legitimate traffic exists), but ad-hoc requests still frequently starved.
  Round 138 corrected an over-strong "permanently dead" claim from Round
  136 back to "frequently starved, not deadlocked."
- **Round 139:** Wired up `net/http/pprof` on the internal-only `:8002` port
  (`pkg/profiler/profiler.go`, commit `b3780fa`) — `StartPrometheusClient`'s
  own comment had claimed pprof auto-registered there for what turned out to
  be this entire saga's duration; it never did (no blank import). This is
  what actually cracked the case in Round 141.
- **Round 141 — ROOT CAUSE FOUND, via a real goroutine dump (not
  speculation) for the first time:** `curl finance-mw-1:8002/debug/pprof/goroutine?debug=2`
  showed **two goroutines both blocked for exactly 459 minutes** — matching
  `finance-mw-1`'s own process uptime almost to the second (`ps -o etimes`
  on PID 1: 27,579s ≈ 459.65 min), i.e. **both have been stuck since
  essentially the moment the process booted** and neither fix (keepalive,
  `GetOldestOpenTime` timeout) ever touched them because they're neither a
  dead client nor a `GetOldestOpenTime` call:
  - **Goroutine 665 (holds the gate slot):** blocked in
    `internal/transport.(*writeQuota).get` — an HTTP/2 **flow-control**
    wait, inside `KlineServiceServer.Stream`'s `stream.Send()` call
    (`kline_service_server.go:277` → `repository_impl.go:219/122`
    `streamRange`/`StreamEach`). This is NOT "client disconnected" (which
    keepalive would catch) — it's "the client's HTTP/2 receive window
    never grants more credit because the client stopped calling `Recv()`
    on its side, even though the underlying TCP/HTTP2 transport is still
    alive and would ACK a PING fine." Keepalive is structurally unable to
    detect this failure mode. This goroutine also spawned goroutine 676,
    a `lib/pq` `watchCancel` watcher, also 459 minutes old — **the
    underlying Postgres query/cursor backing this stream has been held
    open the whole time too**, a secondary DB-connection-pinning concern
    on top of the gRPC gate issue.
  - **Goroutine 675 (waiting for the gate slot):** blocked in
    `klineStreamGate.Acquire` (`stream_admission.go:23`) — queued behind
    goroutine 665, **also since process boot**, never once getting a
    turn. This is the exact, literal explanation for `in_flight` reading
    a frozen baseline value across dozens of checks spanning many rounds.
  - **Correlated to a likely originating client via log timing** (not a
    100%-certain trace-ID match, but strong circumstantial evidence):
    `live-action-bybit-perpetual-future-btc-usdt`'s historical-replay
    bootstrap logged 7/8 intervals failing to open with `transport error`
    at `08:09:12Z` (the *old* MW instance dying mid-redeploy), the `5m`
    interval got 18,893 candles before also failing at `08:09:13Z`
    (`h2 protocol error: error reading a body from connection` — same
    redeploy-transition cause), then at `08:15:13Z` — 17 seconds after the
    *new* `finance-mw-1` process actually came up (`08:14:56Z`) — the
    worker's `StrategyEngine initialized` log fired inside a fresh
    `HistoricalReplay` gRPC client span, and from that point on the
    worker's own logs show only live-tailing activity ("Skipping
    duplicate or stale replay") with **no further explicit replay-interval
    error or success log** for the remaining 7 intervals. The most likely
    explanation: `bootstrap_pending_intervals`
    (`finance-live-action/crates/finance-api/src/historical_replay.rs`)
    re-opened streams for the still-pending intervals against the fresh
    MW, one of them started receiving data server-side, and something in
    the client's per-stream reader (likely in the `select!`-based merge
    loop) stopped calling `.recv()`/`.next()` on that particular stream —
    possibly related to the "missing required timeframe data" deferral
    path seen in the 08:09 log batch — without erroring or logging
    anything further, leaving the SERVER side blocked on flow control
    forever with no client-visible symptom at all (this worker looks
    completely healthy from its own logs and from production trading
    dashboards).
  - **Not fixed this round** — the fix belongs in
    `finance-live-action`'s replay/merge-loop code (a client-side bug: a
    stream whose reader stops advancing) and/or a defensive MW-side
    mitigation (e.g. `grpc.KeepaliveEnforcementPolicy`/`MaxConnectionAge`
    to force periodic reconnection so a flow-control-stuck stream can't
    survive indefinitely, since transport-level keepalive alone cannot
    detect this failure mode). Both need careful, dedicated review — not
    a same-round rush — given the first touches core replay logic shared
    by every broker and the second is a global connection-lifecycle
    change. See the Todo entry for suggested next steps.

- **Round 142:** Implemented `MaxConnectionAge: 30m` / `MaxConnectionAgeGrace: 30s`
  on `serverKeepalive` (commit `edc2201`) — a defensive mitigation, not a
  root-cause fix, since the exact client-side bug (which task/code path
  stops draining its receive window) was not pinned down precisely enough
  to safely patch. Deployed and verified: `matched:true`, correct SHA.
- **Round 144-145 (2026-08-24/25) — MaxConnectionAge CONFIRMED WORKING, plus
  a major refinement: the recurrence trigger includes THIS LOOP'S OWN
  killed research containers, not only live-action workers:**
  - **Confirmed the fix works exactly as designed:** polled `in_flight`
    across the fresh process's lifetime — pinned at 2 through ~29.6
    minutes, then **dropped to 0 at 31.27 minutes** (`ps -o etimes` on
    PID 1: 1876s). A real `--days 90` backtest immediately after
    succeeded cleanly: 78,004 bytes of valid JSON (25,918 candles, clean
    continuity, correct train/validation/holdout split) in 20 seconds —
    the first genuinely successful non-trivial backtest since this saga
    began at Round 122.
  - **Then, within ~15 minutes of that success, `in_flight` was back to a
    stuck baseline again** — confirming the underlying stall condition
    recurs relatively often (not a rare, one-off event), so
    `MaxConnectionAge` bounds each occurrence's damage to ≤30 min but does
    not prevent recurrence. A follow-up `--days 1825` (5-year) request
    that this round itself started got stuck after ~6 minutes (`sent`
    plateaued, container CPU 0%) and was killed via the documented-correct
    pattern (`docker run -d --name X` ... `docker kill X && docker rm -f X`).
  - **Critical new finding:** a fresh `pprof` goroutine dump immediately
    after showed the new stuck pair's age as **9 minutes — matching almost
    exactly when this round's own killed 5-year request was started**, not
    a live-action worker's timing. This strongly suggests **this loop's own
    killed research containers can themselves leave the server-side stream
    stuck in the identical flow-control state**, even when killed via the
    "correct" detached + `docker kill`+`rm -f` pattern (Round 125's fix).
    Plausible explanation: `docker kill` sends SIGKILL, which should close
    the socket immediately at the OS level and should NOT need this
    long to be noticed server-side — but empirically, across repeated
    tests this round, killing an in-progress large request was followed
    by a stuck goroutine matching that kill's rough timing. This does not
    rule out live-action workers als also contributing (both sources are
    plausible and not mutually exclusive), but it means **the loop's own
    ad-hoc backtest usage is a genuine, demonstrated contributing cause of
    this saga, not just an innocent bystander repeatedly getting starved
    by someone else's bug.**
  - **Revised practical guidance:** avoid killing an in-progress large
    (`--days` > ~7) request once started — let it run to completion or
    accept that killing it may itself recreate the stall for up to another
    30 minutes. Prefer smaller windows that are unlikely to need killing
    at all. This is now guidance rule 6 below.

## Current state (as of Round 145, 2026-08-25)

- **Fixed and closed:** dead-client leak (keepalive, Round 127),
  `GetOldestOpenTime`'s own worst-case hold time (10s cap, Round 132),
  pprof wired up (Round 139, enabler not a fix), `MaxConnectionAge` safety
  net bounding worst-case gate starvation to ~30 min (Round 142) — **this
  one is now experimentally CONFIRMED working in production**, not just
  deployed. All verified.
- **Root cause of individual stall occurrences: still not pinned down to
  a single confirmed source.** Round 141 pointed at a live-action worker's
  replay-merge-loop reader; Round 144-145 found strong evidence that this
  loop's own killed research-CLI containers can independently trigger the
  identical symptom. Both are plausible and likely co-occurring. The
  practical impact is now bounded (≤30 min per occurrence, not
  indefinite) but occurrences remain frequent enough (~observed twice
  within roughly an hour this round) that sustained large-backtest usage
  is still unreliable — small/opportunistic windows remain the practical
  mode of operation until/unless the exact client-side trigger(s) are
  found and fixed at the source.

## Round 194 — likely mechanism finally identified: research CLI requests
## genuinely compete with production's own revision-recovery replay for the
## single capacity=1 slot, worse than previously understood

Round 193 called the stall "spontaneous, not caused by research CLI usage"
after killing a new request didn't immediately unfreeze things. Round 194
re-tested more carefully and found a cleaner, reproducible signal: right
after the gate had fully recovered (`sent` freshly advancing
`598897→700365`), starting one new detached `finance-research` request
against a 5-year BTC window froze `sent` again within ~15s, with
`requests_in_flight` going `4→5`. Killing only the new request dropped
`in_flight` back to 4.

Reading `internal/interfaces/grpc/servers/kline/kline_service_server.go` and
`stream_admission.go` clarifies the actual mechanism:
`klineStreamGate` really is `capacity=1` (`defaultMaxConcurrentHistoryStreams`,
deliberately fail-closed given a real prior 512 MiB cgroup OOM — do not
raise this without a reviewed memory-budget change, matching guidance
below). `requests_in_flight` is a middleware-level counter around the whole
`Stream()` RPC handler, so it counts every client **currently blocked
inside `streamGate.Acquire()` waiting for the single slot**, not just the
one actively streaming. A steady `in_flight=4` baseline (even before any
research CLI connects) means **4 separate Stream() calls are typically
already queued behind whichever one client currently holds the sole slot**
— consistent with the 3 Binance/Exness-BTC routes' own revision-recovery
replay calls (`"Exchange revised a closed kline ... remains blocked for
this revision"`, only these 3 routes hit this path; Exness/XAU's MT5 data
source never does) each parking in the same queue whenever an exchange
kline revision needs replaying, competing with whoever else is already
holding or waiting for the slot.

**This means an ad-hoc `finance-research` historical backtest is not just
"unreliable for the researcher" as previously framed — it adds one more
competitor to an already-often-saturated single-slot queue that 3 of the 4
production routes also depend on for revision recovery, and can measurably
extend how long those routes sit unable to evaluate.** Not a new bug to
fix casually (capacity=1 is deliberate, documented, memory-constrained) —
but a real safety consideration for how this loop uses the tool going
forward.

**Updated practical guidance, supersedes the framing in rules 1-7 below
where they conflict:**
- Prefer the smallest `--days` window that still answers the research
  question, and treat every backtest run as consuming a scarce production
  resource, not just a "might fail, retry" convenience.
- Before starting any backtest, check BOTH `sent` is currently advancing
  (rule 1) AND consider checking `evaluation_count` on the 3
  Binance/Exness-BTC routes isn't already frozen — starting a new request
  while production is already contending for the slot only compounds it.
- If a request must be killed, immediately re-verify (as done here) that
  `in_flight` drops and `sent` resumes — do not assume recovery, confirm it,
  since the point of killing is to hand the slot back to production's own
  competing needs, not just to stop the local CLI.

## Round 195 — even a 1-year window hit the same contention; deferring the
## RSI(2) backtest indefinitely rather than retrying again this session

Tried the smallest reasonable window yet (`--days 365`, not the full 5-year
`1825`) specifically to minimize competing with production per Round 194's
guidance. Same result: `in_flight` went `4→5`, `sent` frozen immediately,
confirmed stuck via a background 40s wait (still frozen after), killed
within ~1 minute of detecting it, verified all 3 previously-affected
production routes' `evaluation_count` resumed normally afterward (no
lasting damage). This is now 6 consecutive failed attempts across Rounds
190-195 (days: 1825, 1825, 730, 90, 1825 twice, 365) — window size does not
appear to be the deciding factor; whatever is holding the single slot most
of the time this session is not releasing it quickly regardless of what a
new request asks for. **Deferring the RSI(2) Connors-strategy backtest
entirely for this session** rather than continuing to retry — the
`sma200_trend_filtered_rsi_2_10_90`/`rsi_2_10_90` candidates remain
registered in `finance-research/src/strategies.rs` (uncommitted, local
working tree) for a future session when the gate is confirmed genuinely
idle for a sustained period, not just momentarily at baseline `in_flight=4`.

## Round 196 — 7th consecutive deterministic failure; this is a confirmed bug,
## not spontaneous contention

Retried once more at healthy baseline (`in_flight=4`, `sent` static but
idle-consistent, no signs of prior contention) with an even smaller window
(`--days 180`). Same result within 15s: `in_flight` 4→5, `sent` frozen
immediately. Killed within ~20s this time (fastest response yet), confirmed
zero production impact (all 3 previously-sensitive routes' `evaluation_count`
unchanged across the whole attempt). This is **7 consecutive failures**
across Rounds 190-196, at every window size tried (90 to 1825 days) and at
every gate baseline state tried (freshly recovered, idle, contended) — 100%
reproducible. This is no longer plausibly "spontaneous production
contention, bad luck on window size/timing" — something in how
`finance-research`'s specific request pattern interacts with
`streamGate.Acquire()` or the subsequent `repo.StreamEach` query appears to
deterministically stall. **Conclusion: this needs real Go-level
investigation (add stall logging inside `Acquire`/`StreamEach`, or reproduce
outside a research CLI, e.g. via `grpcurl`), not more black-box CLI retries.**
Fully deferring the RSI(2) backtest and any other `finance-research`
historical-replay work until that investigation happens in a dedicated
round — do not retry this exact pattern again without a Go-level finding to
act on first.

## Round 200 (2026-08-25) — ROOT CAUSE PROVEN: a structural deadlock between
## the client's N-stream merge and the server's capacity-1 gate

Removing `MaxConnectionAge` (finance-mw `3f53612`) did NOT fix replay, and a
goroutine dump taken straight afterward finally explains the whole saga.

`GET /debug/pprof/goroutine?debug=2` on finance-mw at 14:18 UTC:

```
goroutine 32110 [select, 7 minutes]:
  transport.(*writeQuota).get(...)            flowcontrol.go:60
  ... KlineServiceServer.Stream.func1         <- HOLDS the gate slot
goroutine 32854 [select, 7 minutes]:
  klineStreamGate.Acquire(...)                stream_admission.go:23
goroutine 32787 [select, 7 minutes]:  (same)
goroutine 32148 [select, 8 minutes]:  (same)
```

One stream blocked writing into a full HTTP/2 window while holding the only
gate slot; three more queued behind it in `Acquire`.

The deadlock, confirmed by reading both sides:

1. `historical_replay.rs` opens one stream per interval **sequentially**, and
   `open_replay_stream` ends with `replay.advance().await?` — it does not
   return until that interval's **first message arrives**. Each interval also
   gets its own connection (a deliberate earlier fix, see the comment at
   `historical_replay.rs:190`).
2. The server admits stream #1 (gate free), and its handler keeps writing for
   the whole stream — the gate slot is held for the entire send, not just the
   DB read.
3. The client now tries to open stream #2. That handler blocks in `Acquire`,
   so no first message is ever produced, so `advance()` never returns.
4. The client is therefore not reading stream #1 either. Stream #1 fills the
   flow-control window and parks in `writeQuota.get`.
5. Nothing can progress: #1 waits for the client to read, the client waits for
   #2's first message, #2 waits for #1 to release the gate.

This is deterministic, not a race, which is exactly why every attempt failed
and why `finance-research` failed 7/7 across every window size — it opens
multiple interval streams the same way.

It also explains the interval pattern: small intervals whose entire response
fits inside the initial flow-control window let the server finish sending and
release the gate before the client reads, so they succeed. Large ones do not.
The observed `failed_intervals` were always `5m`/`15m`/`30m` — the three
highest-volume intervals — never `1d`/`12h`.

And it re-frames the whole saga: Round 141's "459-minute stuck Send" was this
same deadlock, not an unrelated client bug. Round 142's `MaxConnectionAge`
did not fix it either — it just broke the deadlock every 30 minutes by
killing a stream, which cleared the gate while guaranteeing the replay could
never assemble all 8 intervals in one attempt (`portfolio_inputs_complete`).
Removing the age limit therefore removed the periodic unwedging and made the
stall permanent, which is the state observed at 14:18-14:21 UTC (`sent`
frozen at 59371 across 90s with 4 in-flight).

**The fix is client-side and must preserve the cross-interval chronological
merge that no-lookahead depends on.** The merge itself is fine; holding N
concurrent server streams to feed it is what breaks. Fetch each interval
fully, one stream at a time (never more than one gate slot in use), then
merge the collected series in memory in exactly the current `replay_order`.
Alternatives rejected: raising gate capacity contradicts the documented
512 MiB cgroup OOM evidence, and any age/timeout-based server-side kill
recreates Round 142.

Not implemented in this round: it is surgery on the replay path that feeds
no-lookahead ordering, and warrants its own careful change with tests rather
than being rushed at the end of an incident.

## Practical guidance for future rounds

1. Before starting a backtest, check
   `finance_mw_grpc_requests_in_flight{method="Stream",service="kline.KlineService"}`
   on `finance-mw-1:8002/metrics` (via `docker exec finance-mw-1 curl -s
   http://localhost:8002/metrics`). A steady non-zero baseline is normal
   now (not necessarily stuck) — the decisive signal is whether
   `stream_messages_total{direction="sent"}` is climbing over ~30-60s.
2. Try small windows first (`--days 1-7`) — cheaper to retry, and the
   Round 133 evidence shows small requests succeed more reliably than
   large ones under contention.
3. Always run research containers detached and clean them up explicitly:
   `docker run -d --name finance-research-<label> ...` then
   `docker kill <name> && docker rm -f <name>`. Never wrap a foreground
   `docker run` in `timeout` alone.
4. If a request hangs for several minutes with zero `sent` progress, it is
   reasonable to kill and retry later (possibly a different time of day
   with less production replay/sync activity) rather than waiting
   indefinitely.
5. **Do not rush a capacity increase** (`KLINE_MAX_CONCURRENT_HISTORY_STREAMS`
   above 1) without a reviewed memory-budget change — the code's own
   comment cites real production OOM evidence for why it's 1. If this
   becomes a recurring, serious blocker across many rounds, escalate as a
   proper reviewed Todo item (not an ad-hoc fix) proposing either a
   controlled capacity increase with fresh memory-headroom evidence, or
   splitting `GetOldestOpenTime` onto a dedicated lightweight unary RPC
   that doesn't consume the historical-replay gate at all.
6. **(Round 145) Never `docker kill` an in-progress large request.** Doing
   so has been directly observed (twice) to leave the server-side stream
   stuck in the same flow-control state this whole saga is about, even
   when following the otherwise-correct detached-container pattern (rule
   3 above) — `docker kill`'s SIGKILL does not reliably and promptly close
   the connection from MW's perspective. If a request is genuinely stuck
   (rule 4), killing it is still the right call, but expect that action
   itself to plausibly cost the gate another up-to-30-minute
   `MaxConnectionAge` cycle before it's usable again — budget for that
   when deciding whether to kill-and-retry versus just waiting.
8. **(Round 191-192) Self-inflicted repeat-kill compounding, confirmed via the
   documented metrics diagnostic.** Hit 5 consecutive hung `finance-research`
   attempts (90-day to 5-year windows, tunnel confirmed healthy each time)
   and `docker kill`'d 4 of them across ~1.5 hours, directly against rule 6
   above. Checked the decisive diagnostic afterward:
   `finance_mw_grpc_requests_in_flight{method="Stream",service="kline.KlineService"}=4`
   and `stream_messages_total{direction="sent"}` completely static across 3
   samples 8s apart (579413, unchanged) — confirms the gate was genuinely
   stuck, not just busy. Given rule 6's own warning, this was very plausibly
   self-inflicted: each kill plausibly cost another up-to-30-min
   `MaxConnectionAge` recovery cycle, compounding rather than fixing it.
   Corrected response: stopped killing, let it recover on its own rather
   than retrying a 5th/6th time. **Lesson for future rounds: after 1 kill
   confirms genuine stuck-ness via the metrics check, stop — do not retry
   immediately, walk away and check back after the ~30-min MaxConnectionAge
   window instead of compounding with more kills.**

9. **(Round 193) Correction to the Round 191-192 self-blame — the gate was
   independently stuck this time, not caused by repeat-killing.** Round
   192 concluded the stuck gate was likely self-inflicted from repeated
   `docker kill`s. Round 193 re-checked cleanly: at round start,
   `stream_messages_total{sent}` was advancing normally (579413→598897
   over the ~50min gap since Round 192, confirming the gate HAD recovered
   on its own by then, consistent with the MaxConnectionAge bound working
   as designed). Started one fresh detached research request (rule 3
   pattern, no prior kills this round) — `sent` froze again immediately,
   `requests_in_flight` went 4→5. Killed only the new request (not the
   other 4) and confirmed `in_flight` dropped back to 4 — but **`sent`
   stayed frozen at 598897 even after removing the new request**,
   proving the pre-existing 4 production streams were themselves already
   stuck, independent of and not caused by the new research request. This
   means occurrences can be genuinely spontaneous on the production side
   (likely the same live-action-worker replay-reader trigger Round 141
   originally flagged), not always a research-CLI-side artifact — both
   mechanisms are real and can occur independently. Left it alone
   afterward rather than probing further; per rule 6, expect natural
   recovery within the ~30-min `MaxConnectionAge` bound rather than
   chasing it with more diagnostic connections.

7. **(Round 155-161) Check the local SSH tunnel before blaming the gate.**
   A `transport error` from `finance-research` can come from the client
   side, not MW at all — the research tunnel (`ssh -f -N -L
   18086:localhost:8086 my`) can die silently mid-session (idle timeout,
   network blip) while direct `ssh my "..."` commands keep working fine
   (different connection). Several consecutive `transport error` failures
   that don't correlate with `in_flight`/`sent` looking stuck are a signal
   to check `ss -tlnp | grep 18086` before spending more rounds on gate
   theories — an empty result means the tunnel is down, not MW. Fix is one
   command (`ssh -f -N -L 18086:localhost:8086 my`) and takes under a
   second to verify either way, so check it first, not last.
