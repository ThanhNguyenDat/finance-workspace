# Round 306 — NEEDS-MORE-RESEARCH: the live trade log is the one Target 3 measure Rounds 300-305 cannot touch. It says the fleet has **not closed a trade in 27-38 hours**, and the workers are **healthy**.

Classification: **NEEDS-MORE-RESEARCH** — a real measurement, no verdict; the sample is
13 closes. **Zero containers**; narrow read-only production evidence only. XAU-first in
reading, fleet-wide in scope.

## Why go here now

Rounds 300-305 established that every backtest Target 3 number depends on an arbitrary
`--days`: `exness XAU` passes on four windows and fails on two, and `binance BTC`'s
cushion collapsed from 33x to 1.0x once the perturbation was widened. Round 301 named
the one measurement immune to all of it: **the durable Redis trade log** — real closed
positions, no replay, no adaptive weights, no window choice (Rounds 207, 259-260).

Enough time has now passed to read it again.

## Part 1 — The live measurement

Log window **2026-08-27T14:39:59Z → 2026-08-30T04:10:39Z = 61.5 h (2.56 days)**. Index
and payload cardinality match exactly on all six routes (12/12, 9/9, 9/9, 3/3, 3/3,
3/3), so the append invariant Round 207 checked still holds. Closes = entries ÷ 3
(three capital rules), confirmed by the distinct `exit_at` values.

| route | closes | **live /week** | hours since last close | checkpoint age |
|---|---|---|---|---|
| `binance BTC/USDT` | 4 | **10.93** | 36.1 | 0.01 h |
| `exness BTC/USD` | 3 | **8.19** | 36.1 | 0.01 h |
| `bybit BTC/USDT` | 3 | **8.19** | 27.2 | 0.01 h |
| `binance XAU/USDT` | 1 | 2.73 | 35.8 | 0.01 h |
| `exness XAU/USD` | 1 | 2.73 | 38.0 | **28.18 h** |
| `bybit XAUT/USDT` | 1 | 2.73 | 38.0 | 0.01 h |

**`binance XAU` has produced its first durable close.** Round 207 found that key absent
and the route frozen since 2025-12-26; it now holds 3 entries, exit_at
2026-08-28T16:19:59Z. Its checkpoint `recent_klines` still ends in December 2025, so
the freeze is real in the market data while the Portfolio nonetheless closed a position.
I am recording that pairing, not explaining it.

## Part 2 — The fleet has stopped closing, and it is **not** an outage

Every route's last close falls in a **two-hour band on 2026-08-28, 14:09-16:19Z**,
except `bybit BTC` which continued to 2026-08-29T00:59Z. Since then: **27 to 38 hours
with no close anywhere.**

Simultaneity across three brokers, two instruments and both market types is the shape
of a system-level event, so the first thing to check is whether the workers are alive.
They are:

**Five of six checkpoints were written within 40 seconds of the read** (`updated_at`
2026-08-30T04:10:00-04:10:03Z). The workers are consuming Kafka and checkpointing on
schedule.

The sixth, `exness XAU`, is **28.18 hours stale** — and that is the expected weekend
CFD closure, not a fault: its last Kafka offset sits on the
`market.kline.v2.exness.cfd.xau.usd.**1d**` topic at 2026-08-29T00:00:04Z, which is
exactly what a gold CFD worker does when the market shuts. Round 102 recorded this same
signature as a false alarm.

**So the stall is not a worker outage.** Whatever is holding the fleet flat sits in the
Portfolio's decision-to-target path, on a live system whose data plane is healthy.

## Part 3 — Live against backtest

I expected, before reading, that the two would agree within a factor of 2. Stated
loosely rather than as one of this series' pre-registered thresholds, so I record it as
an expectation, not a test:

| route | **live** | backtest range | ratio |
|---|---|---|---|
| `binance BTC/USDT` | 10.93/wk | 8.12-9.52 | **1.15x-1.35x** |
| `bybit XAUT/USDT` | 2.73/wk | 2.40-2.60 | **1.05x-1.14x** |
| `exness XAU/USD` | 2.73/wk | 6.83-7.52 | **0.36x-0.40x** |

Two of three land close. `exness XAU` is the outlier — but its live window contains a
weekend, and the route trades only 67.4% of calendar time (194.1 of 288 bars/day).
Adjusting for market-open hours gives **4.05/week**, a ratio of **0.54x-0.59x**. Still
low, now within a factor of two.

That is worth stating carefully: **the backtest's most window-sensitive route is also
the one whose live rate it matches worst.** One weekend and one close is not evidence
of a systematic gap, but it is the direction the window-sensitivity work would predict.

## What this does and does not settle

It does not settle Target 3. **Thirteen closes across six routes** is the same
objection Round 207 raised at nine, and the 27-38 hour drought means the rates above
are still falling with every hour that passes rather than converging.

What it does establish is that the **instrument is sound**: index/payload cardinality
matches, closes are countable, the workers are demonstrably live, and the one stale
checkpoint has a benign explanation. Every future Target 3 statement should come from
here rather than from a `--days` window.

## What is proven, and what is not

Proven:

- Durable log at 2026-08-30T04:10:39Z: ZCARD/HLEN 12/12, 9/9, 9/9, 3/3, 3/3, 3/3 on
  the six routes; 13 closes total over a 61.5-hour window.
- Live rates 10.93 / 8.19 / 8.19 / 2.73 / 2.73 / 2.73 per week.
- Last close per route: 2026-08-28T16:04:59Z (both BTC majors), 2026-08-29T00:59:59Z
  (`bybit BTC`), 2026-08-28T16:19:59Z (`binance XAU`), 2026-08-28T14:09:59Z (both other
  gold routes) — a 27-38 hour drought.
- Five of six worker checkpoints have `updated_at` within 40 seconds of the read;
  `exness XAU` is 28.18 h stale with its last offset on the `.1d` topic.
- `binance XAU` now holds 3 durable entries where Round 207 found the key absent.

Not proven, and deliberately not claimed:

- **Any Target 3 verdict.** 1-4 closes per route. This is a baseline, exactly as
  Round 207 said of nine closes.
- That the 27-38 hour drought is abnormal. At `binance BTC`'s own rate a 36-hour gap is
  not individually rare; what is unusual is five routes stopping within two hours of
  each other, and I have **not** tested that against a null model.
- **Any cause** for the drought. The workers are alive; that excludes an outage and
  nothing else. Whether positions are open, whether targets simply have not changed, or
  whether a gate is firing was not inspected this round.
- That the backtest systematically overstates `exness XAU`. One close, one weekend,
  and a coverage adjustment I applied myself.
- That `binance XAU` is unfrozen. One close against a checkpoint whose market data
  still ends in December 2025 — the pairing is recorded, not resolved.
- Anything about the `recent_klines` tails I extracted by grep. That method takes the
  last occurrence in serialization order, not the newest bar across intervals, so the
  apparently stale tails on some routes are **not interpretable** from this evidence and
  no conclusion is drawn from them.
