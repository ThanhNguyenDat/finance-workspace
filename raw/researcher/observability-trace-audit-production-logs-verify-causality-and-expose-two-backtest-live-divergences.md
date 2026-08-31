# DIVERGENCE 2 IS WITHDRAWN (Round 348)

This file claimed *"the research replay has no such gate"*. **It has one.**
`finance-research/src/portfolio_measurement.rs:170-181` builds a `PortfolioRiskLayer` with
`PortfolioRiskPolicy::widened_for_simulation(...)`, which widens **only** notional and leverage
limits (`portfolio_risk.rs:272-307`) and leaves `max_total_cost_bps = 10.0` intact; the gate runs
on every risk-opening target and rejection suppresses execution. **The replay applies the same
10 bps ceiling as production, and Divergence 2 is withdrawn.**

What the gate is in practice: projected cost = `(fee + slippage) × 2` for a reversal, so at
deployed costs a reversal is 14 bps and is rejected while a single leg at 7 bps passes.
**All 369 production rejections across all six routes are at 14 bps** — it has never rejected
anything but a reversal. See `round348-DATA-ISSUE-the-cost-flags-move-reversals-across-a-10bps-gate-which-explains-rounds-344-345-and-346.md`.

---

# DIVERGENCE 1 QUANTIFIED AND DE-ESCALATED TO P3 (Round 347)

This file left the Binance kline-revision magnitude unmeasured. It is now measured by joining
the live `Signal evaluated` `price` to Timescale's stored `close_price` for the same bar — the
Kafka route was blocked without credentials, and this source was already in hand.

125 `binance BTC` 5m bars (2026-08-30, 00:00-17:30 UTC): **51.2% identical**, median |Δ|
**0.0000 bps**, mean 0.1806, p95 1.4211, **max 2.8955 bps**; 6.4% of bars ≥1 bps, 3.2% ≥2 bps,
and **none** reach the 7 bps round trip. **Divergence 1 de-escalates to P3.**

Two things to carry forward: the tail (2.9 bps) is the same order as the deployed **2 bps
slippage**, so it is bounded rather than harmless; and **`exness XAU`, the only route with a
positive gross edge, has zero revisions** — the divergence is confined to the two Binance routes,
which already fail on negative gross. Divergence 2 (the live 10 bps `execution_cost` gate the
replay does not model) is **unchanged and still open**. See `round347-NO-CHANGE-binance-kline-revisions-are-real-but-median-zero-bps-with-a-2-9-bps-tail.md`.

---

# Observability trace audit — production ECS logs verify causality, and expose **two backtest-vs-live divergences** the code audit could not see

**Investigation only — nothing applied, no fix proposed.** This complements the code-level
audit (`backtest-correctness-audit-look-ahead-and-fill-invariants.md`) with **observed runtime
evidence**: ECS JSONL logs and OpenTelemetry spans from the six live route workers, plus the
ECS events the backtest CLI itself emits. Read-only throughout; no credentials read or printed.
Production host clock at time of collection: **2026-08-30 17:48 UTC**.

## What the observability surface actually is

- Each route runs its own worker (`live-action-<broker>-<market>-<base>-<quote>-…`) writing ECS
  JSONL to `/data/log/finance-live-action-<route>/` — `application`, `info`, `warn`, `error`,
  `access`, rotated daily, exactly as `observability-logging.md` requires.
- Application events carry a `span` with **W3C trace context** plus Kafka coordinates:
  `market.event.id`, `market.interval`, `messaging.destination.name`,
  `messaging.kafka.offset/partition`, `trace.id`, `span.id`, `otel.kind: consumer`.
- The backtest CLI emits exactly **one** ECS event per run,
  `event.dataset: research.backtest_candle_count`, carrying the split sizes and the gap
  metadata. There is **no per-decision or per-trade event** — the runtime confirmation of audit
  item **L4**.
- VictoriaMetrics, vmagent, Grafana, Kibana, Elasticsearch, Filebeat and an OTel collector are
  all running. VictoriaMetrics' HTTP API is authenticated; I did not attempt to obtain
  credentials, so metric-series evidence below is not included.

---

## PASS 1 — no look-ahead, measured from production traces

Every signal log carries the Kafka message's `market.event.id`, whose suffix is the bar
timestamp. For `exness XAU` that suffix is **exactly bar-aligned** (offset within its own
interval is 0 for all 620 events), so it is an unambiguous reference.

`exness.cfd.XAU.USD`, full trading day 2026-08-28, 620 signal events across all eight intervals
(5m 348, 15m 126, 30m 70, 1h 40, 2h 22, 4h 10, 12h 2, 1d 2):

| quantity | value |
|---|---|
| signals emitted **before** their bar closed | **0 / 620** |
| lag (`@timestamp` − bar close), min | **+1.015 s** |
| median / p95 / max | +2.133 s / +5.012 s / +8.083 s |

**Nothing is evaluated before its bar closes, in production, on every interval the Portfolio
consumes.** This is the same conclusion the code audit reached by reading `replay_order` and the
MTF filter — now confirmed against runtime behaviour.

## PASS 2 — no duplicate execution, no reprocessing

Same day, same route:

- **Kafka offsets are strictly increasing on all eight topics** — 0 non-increasing steps after
  collapsing the 2-3 log lines each message produces.
- **245 distinct `market.event.id`, 0 of them processed under more than one `trace.id`.** No
  market event is handled twice.

Duplicate execution is a named trading-safety invariant in this repository; this is the first
time it has been checked against production rather than argued from code.

## PASS 3 — W3C trace context is well formed

620/620 `trace.id` are exactly 32 characters and 620/620 `span.id` exactly 16 — the lengths
`observability-logging.md` mandates. 245 traces / 245 spans on this route-day.

## PASS 4 — the session calendar holds live

`exness XAU`'s `application.jsonl` is **0 bytes** from 2026-08-29 00:00 onward and its last
rotated file is 2026-08-28. On Saturday 2026-08-29 the gold worker emitted **0 application
events**, while all five 24/7 routes emitted 933-1893. Independent confirmation of the session
boundary that Round 346 measured from price data.

## PASS 5 — split integrity, from the backtest's own emitted events

The `research.backtest_candle_count` event carries `candle_count`, `train_candle_count`,
`validation_candle_count`, `holdout_candle_count`. Across **24 saved runs** (Rounds 335-346, all
six routes, windows 300-1200 days):

**`train + validation + holdout == candle_count` exactly, in every one of the 24 runs** — a
60/20/20 partition with no overlap and no dropped bar. Previously this was assumed; it is now
observed.

---

## DIVERGENCE 1 — Binance revises closed klines; live blocks the revision, the backtest reads it

Production `warn` events, verbatim message:

> *"Exchange revised a closed kline; matching history entry replaced and **strategy evaluation
> remains blocked for this revision**"*

Counts for the full day 2026-08-29, all six routes:

| route | application lines | **kline revisions** | risk rejections |
|---|---|---|---|
| `binance BTC/USDT` perp | 1893 | **347** | 0 |
| `binance XAU/USDT` perp | 1009 | **154** | 0 |
| `bybit BTC/USDT` perp | 1031 | 0 | 3 |
| `bybit XAUT/USDT` spot | 933 | 0 | 0 |
| `exness BTC/USD` cfd | 1064 | 0 | 0 |
| `exness XAU/USD` cfd | 0 (session closed) | 0 | 0 |

**Revisions occur only on Binance routes** — zero on Bybit and Exness. Today's partial-day
breakdown on `binance BTC` (242 events to 17:45 UTC): 5m 152, 15m 48, 30m 24, 1h 8, 2h 6, 4h 4.

The consequence is structural:

- **Live** replaces the stored history entry but **blocks strategy evaluation** for the
  revision — so the live strategy acted on the **pre-revision** candle.
- **The research replay** loads from Timescale, i.e. the **post-revision** stored values.

**The backtest therefore evaluates on candles the live system deliberately refused to
re-evaluate on.** A revised close embeds information that arrived after the bar closed, so this
is a mild look-ahead **in the backtest** — one that no amount of code reading would have
surfaced, because the code is correct and the *data* differs.

**Magnitude is not established.** The warning carries `open_time`, interval and Kafka
coordinates but **no before/after prices**, so how much the revised values differ is unknown.
The affected routes are `binance BTC` and `binance XAU`; `exness XAU`, the only route with a
positive gross edge, shows **zero** revisions.

## DIVERGENCE 2 — production rejects targets on an execution-cost gate the backtest does not model

Production `warn` event, verbatim fields:

```
message        Portfolio target rejected by risk management
gate           execution_cost
reason         projected execution cost is 14bps; maximum is 10bps
rejected_count 73
scope_id       paper-fixed-pct-scope-…
```

So the live risk layer enforces a **10 bps ceiling on projected execution cost** and had
rejected **73** targets cumulatively at the time of the sample (3 events on `binance BTC` today,
3 on `bybit BTC` on 2026-08-29).

**The research replay has no such gate.** It charges fee, slippage and funding on every trade
but never *refuses* a target for being too expensive. Production therefore trades a **strictly
smaller** set of targets than the backtest, and the ones it drops are precisely the expensive
ones.

This matters more than it would in another arc: Rounds 313-346 concluded that **cost is the
binding constraint** on the one route with an edge. A backtest that takes the expensive trades
production declines is biased in the permissive direction on exactly the axis the research has
been optimising.

---

## DATA-ISSUE — `market.event.id` does not mean the same thing on every broker

- **Exness**: the suffix is the bar **open** time and is exactly aligned (ms offset within the
  interval is `0` for all 620 events). Signals land 1.02-8.08 s after bar close.
- **Binance**: the suffix behaves as a **close-side event timestamp with jitter** — ms offset
  within the interval ranges **0 to 1444 ms**, and one sample is
  `…BTC.USDT.4h.1788076800219`, 219 ms past the 4h boundary.

Read under the Exness convention, the Binance data shows 518 of 528 events "before bar close" at
a median of −299.93 s — an artefact of the wrong convention, **not** look-ahead. Read under its
own convention, the worst case is **−0.43 s**, inside the observed jitter.

**I nearly reported a false look-ahead alarm from exactly this**, and I am recording it: any
trace-based causality analysis must establish the `market.event.id` convention **per broker**
before differencing timestamps. The precise look-ahead evidence in PASS 1 stands on `exness XAU`,
where alignment is exact; the Binance data is **consistent** with no look-ahead but cannot be a
sub-second test.

---

## What is proven, and what is not

Proven (all read-only, from production logs):

- `exness XAU` 2026-08-28: 620 trace-carrying signal events, **0** emitted before bar close, min
  lag +1.015 s, median +2.133 s, max +8.083 s; all eight intervals present.
- Kafka offsets strictly increasing on all eight of that route's topics; 245 distinct
  `market.event.id`, 0 under more than one trace.
- 620/620 `trace.id` 32 chars, `span.id` 16 chars.
- 2026-08-29 per-route table above, including `exness XAU` at 0 application events.
- 24 backtest runs: `train + validation + holdout == candle_count` exactly in all 24.
- The two warn messages quoted verbatim, with their fields.

Not proven, and deliberately not claimed:

- **How much the Binance revisions change the data.** The log carries no before/after values.
  Quantifying it requires comparing the original Kafka message against the stored Timescale row —
  neither is in the log.
- **That any specific backtest result is wrong because of either divergence.** Both are
  systematic and directional, but their magnitudes are unmeasured. I am not adjusting any past
  result.
- **Anything from metrics series.** VictoriaMetrics is authenticated; no metric evidence was
  collected, so decision-rate and counter verification against `/metrics` is still open.
- That the exness worker's clean result generalises to routes whose event ids are jittered. It
  is the route where the test is exact; the others are consistent but weaker.
- That `rejected_count: 73` is a daily figure. It reads as a cumulative counter and its window
  is not documented in the event.

## Follow-ups this opens

- [ ] Quantify Binance revision magnitude: capture the pre-revision value (Kafka) against the
      stored row (Timescale) for a sample, and report the price delta distribution.
- [ ] Decide whether the replay should model the live `execution_cost` 10 bps gate — without it,
      backtest and production trade different sets.
- [ ] Normalise `market.event.id` semantics across brokers, or document the per-broker
      convention where it is consumed.
- [ ] Obtain read-only metrics access to verify decision-rate and trade counters against
      `/metrics`, which this audit could not reach.
