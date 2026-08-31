# Round 207 — Durable Portfolio trade log verified live (Dev-done entry was two steps stale), and the first Target 3 measurement that is not a backtest

Read-only production evidence. No backtest container run. Codex available
(`codex_available=true`), so nothing was implemented.

## Part 1 — What the Dev-done entry was actually still waiting for

`raw/handoff_agent.md` carried `[trading][high][2026-08-27] Nối durable trade log
vào đúng Portfolio closed-ledger` in `## Dev-done`. Its **title** still reads
"chờ owner mở push gate", but its addenda are current and already record the push,
the deploy, the immutable digest and a green production verification run. Only the
title line is stale — the entry itself is accurate.

What it was genuinely blocked on is stated precisely in its last addendum, a
read-only Redis probe at 21:42 UTC+7 on 2026-08-27:

> cả hai trả `ZCARD=0`. Chưa có closed Portfolio trade sau rollout để chứng minh
> append/replay idempotency trên production; giữ Processing…

That is the gap this round closes: enough time has now passed for real closed
trades to land, so the append path can be verified against production data rather
than only against `cargo test`.

Deployment identity re-confirmed independently:

```
e452083 feat(trading): persist portfolio closed trades   2026-08-27 10:04:30 +0700
  git merge-base --is-ancestor e452083 origin/main   => pushed
  git merge-base --is-ancestor e452083 7a15b76       => in the deployed image
```

All six workers run `finance-live-action_sha-7a15b76ab5b8…`.

## Part 2 — The durable log works, and its consistency invariant holds

Keys are `trades:<broker>.<market_type>.<base>.<quote>` plus a `:payloads` hash
(`crates/finance-redis/src/trade_log.rs:74-84`). Production scan:

| key | index (ZCARD) | payloads (HLEN) |
|---|---|---|
| `trades:binance.perpetual_future.btc.usdt` | 9 | 9 |
| `trades:exness.cfd.btc.usd` | 6 | 6 |
| `trades:exness.cfd.xau.usd` | 3 | 3 |
| `trades:bybit.perpetual_future.btc.usdt` | 6 | 6 |
| `trades:bybit.spot.xaut.usdt` | 3 | 3 |
| `trades:binance.perpetual_future.xau.usdt` | **absent** | **absent** |

Index and payload cardinality match exactly on every populated route — no orphan
index entries, which is the invariant that would break first if the two writes
were not atomic.

The missing binance XAU key is **expected, not a defect**: that route has been
frozen since 2025-12-26 and Round 206 confirmed its Portfolio ledger is still at
7 trades, unchanged. Zero closes since deployment means zero durable records.
Two independent data paths agreeing on "this route is not trading" is a better
result than either alone.

One payload, read in full (no secrets present, structure complete):

```json
{"schema_version":1,
 "event_id":"06b2418522f8…",
 "pair":{"broker":"binance","market_type":"perpetual_future","base_asset":"BTC","quote_asset":"USDT"},
 "scope_id":"paper-risk-2pct-scope-…","run_id":"paper-risk-2pct-run-…",
 "trade":{"strategy":"weighted-strategies","interval":"5m","side":"long",
   "contributing_strategies":[["candle_momentum",0.38101190801323703],
     ["mtf_candle_momentum_5m_4h_sma10",0.0],["mtf_macd_5m_4h_sma10",0.0],
     ["mtf_stochastic_4h_1d_sma50",0.0],["mtf_stochastic_5m_4h_sma10",0.0],
     ["rsi_mean_reversion",-0.04488334961571409]],
   "entry_at":"2026-08-27T13:59:59.999Z","exit_at":"2026-08-27T19:59:59.999Z",
   "realized_pnl":15.51177223242972,"close_reason":"target_flat"}}
```

`event_id` is a deterministic SHA-256 over pair/scope/run/trade
(`trade_log.rs:91-105`), so replay is idempotent by construction and `append`
reports whether the record was newly added.

### Cross-path confirmation of Round 206

That payload independently confirms yesterday's finding through a completely
different mechanism. Round 206 read `strategy_weights` out of the checkpoint
policy; here the **decision record of a real closed Portfolio trade** lists
`mtf_stochastic_4h_1d_sma50` at exactly `0.0`, together with every other `mtf_*`
strategy, while `candle_momentum` (+0.381) and `rsi_mean_reversion` (−0.045)
carry the whole decision. The only mechanism this program ever validated
contributed nothing to this trade, and the durable log now records that fact
per-trade rather than only in a policy snapshot.

## Part 3 — First Target 3 measurement from live data instead of a backtest

Every prior Target 3 number (Round 80's ~15/week, Round 83's ~9.3/week, Round
92's corrected ~9.3/week over 5 years and ~7.2-7.3/week over 18 months) came
from `one_target` backtests. The durable log makes the live rate directly
countable: each Portfolio close writes exactly one record per capital rule
(three rules), so closes = entries / 3, confirmed by the timestamp grouping
(binance BTC's 9 entries fall on exactly 3 distinct `exit_at` values).

Observation window: **2026-08-27T14:39Z → 2026-08-28T15:50Z, ~25.2 hours.**

| route | entries | Portfolio closes | implied / week | first close | last close |
|---|---|---|---|---|---|
| binance BTC/USDT | 9 | 3 | ~20.0 | 2026-08-27T19:59Z | 2026-08-28T03:59Z |
| exness BTC/USD | 6 | 2 | ~13.3 | 2026-08-27T14:39Z | 2026-08-28T01:34Z |
| bybit BTC/USDT | 6 | 2 | ~13.3 | 2026-08-28T01:24Z | 2026-08-28T14:04Z |
| exness XAU/USD | 3 | 1 | ~6.7 | 2026-08-28T14:09Z | 2026-08-28T14:09Z |
| bybit XAUT/USDT | 3 | 1 | ~6.7 | 2026-08-28T14:09Z | 2026-08-28T14:09Z |
| binance XAU/USDT | 0 | 0 | 0 | — | — |

**This is a baseline, not a verdict.** One to three events per route cannot
support a frequency claim; the implied weekly rates are shown to make the
arithmetic explicit, not because a 1-close sample means 6.7/week. What the round
establishes is the measurement path and the starting point. Re-read the same
keys after roughly seven days and the numbers become comparable to Round 92's
backtest figures for the first time.

The directional hint worth carrying forward, and nothing more: BTC routes are
currently closing *above* the ≥7/week bar and above Round 92's backtest
estimate, while both XAU routes sit near it and binance XAU is at zero.

## Part 4 — The durable log has no retention policy (low)

`trade_log.rs` exposes `append`, `append_with_checkpoint`, `read` and `count`.
There is no `ZREMRANGEBY*`, no trim, and no TTL on either `trades:*` key — the
only TTL argument in the file belongs to the checkpoint payload. Both structures
grow without bound in Redis.

At the measured rate this is not urgent: ~700 bytes per record, ~9 records/day on
the busiest route, so on the order of **10-15 MB/year across all six routes**.
Flagging it as a decision that should be made deliberately rather than left
implicit, because `docs/specs/observability.md` designates business trade facts
as durable events with their own retention — Redis memory is the wrong final
home for an unbounded append-only financial fact table, even a small one.

## What is proven, and what is not

Proven:

- `e452083` is on `origin/main` and inside the deployed image `7a15b76`.
- The earliest durable record (2026-08-27T14:39Z) postdates Codex's `ZCARD=0`
  probe at 21:42 UTC+7 (14:42Z), so the two observations are consistent rather
  than contradictory.
- Five routes carry durable Portfolio closed-trade records with matching index
  and payload cardinality; the sixth is empty for a route independently
  confirmed to be frozen.
- The payload schema is complete, carries a deterministic idempotency key, and
  contains no credentials.
- A real closed Portfolio trade records `mtf_stochastic_4h_1d_sma50` at 0.0.
- Nine Portfolio closes occurred across five routes in a 25.2-hour window.
- No retention or TTL exists on the durable trade keys.

Not proven, and deliberately not claimed:

- Any live trade-frequency verdict. The sample is 1-3 closes per route.
- That the durable log's counts reconcile with the checkpoint `paper-*` ledger
  totals. The ledgers carry replay-seeded history the log never saw, so the two
  are not directly comparable and no reconciliation was attempted.
- Any statement about whether the log survives a Redis eviction/restart. Not
  tested this round.

## Method note for the next round

Two consecutive rounds (206, 207) produced findings from production evidence
without running a backtest container. Both were legitimate — a measurement
defect and a deployment verification — but the next round should return to a
bounded backtest experiment so the research thread does not drift into
verification-only work.
