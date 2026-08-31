# Round 208 — XAU/binance's short history is a venue data horizon, not a backfill gap: the ceiling Round 205 hit cannot be lifted

Read-only production database evidence (bounded queries with
`statement_timeout`, no mutation). Codex available, nothing implemented.

## Why this question

Round 205 falsified four XAU/binance 4h candidates because binance held only
1,543 4h candles (~257 days) against exness's 7,986 (~3.6 years), and closed with
"still no validated strategy to add to XAU/binance". That left an obvious and
expensive-if-wrong assumption unexamined: **is that short window ours or the
venue's?** If ours, a backfill reopens the whole XAU/binance research space and
possibly unfreezes the route. If the venue's, every future round must stop
treating binance XAU as a primary evidence source.

Nobody had measured it. This round does.

## Coverage, measured directly

Gold, every interval, `min/max(open_at)` from `public.klines`:

| broker | instrument | first candle | span |
|---|---|---|---|
| exness | XAU/USD (cfd) | 2021-08-26 | **1,829 days** |
| bybit | XAUT/USDT (spot) | 2025-04-11 | 504 days |
| binance | XAU/USDT (perp) | **2025-12-11** | **260 days** |

The binance XAU start date is `2025-12-11` on **all eight intervals**
(5m, 15m, 30m, 1h, 2h, 4h, 12h, 1d) — identical, not staggered.

## The measurement that settles it

Instrument registration timestamps:

```
binance perpetual_future BTC USDT   created_at 2026-08-11 04:14:30.840671+00
binance perpetual_future XAU USDT   created_at 2026-08-11 04:14:30.840671+00   <- identical
exness  cfd              XAU USD    created_at 2026-08-12 16:30:27.017320+00
exness  cfd              BTC USD    created_at 2026-08-13 12:34:05.617418+00
bybit   perpetual_future BTC USDT   created_at 2026-08-23 06:09:43.274260+00
bybit   spot             XAUT USDT  created_at 2026-08-23 06:09:43.282444+00
```

**binance BTC and binance XAU were registered in the same transaction, to the
microsecond, and backfilled by the same pipeline.** Their outcomes:

| broker | instrument | first 4h candle | span |
|---|---|---|---|
| binance | BTC/USDT | 2021-08-26 | 1,829 days |
| binance | XAU/USDT | 2025-12-11 | 260 days |

Same venue, same job, same moment — one reached five years, the other stopped at
260 days. That difference cannot be our ingestion start date, our retention, or a
truncated backfill run, because the identical run got five years for BTC.

The same signature appears independently on a second venue: bybit BTC reaches
2021-08-26 while bybit XAUT stops at 2025-04-11, both registered in the same
transaction. Two unrelated crypto venues, both long on BTC and short on gold.

Meanwhile `2021-08-26` is the *same* first candle for binance BTC, bybit BTC,
exness BTC and exness XAU — that is our five-year retention boundary
(`migrations/trading/20260813160000_extend_kline_retention_to_five_years.sql`),
not an availability limit. Those routes are retention-capped; binance XAU and
bybit XAUT are availability-capped.

**Conclusion: 2025-12-11 is Binance's own horizon for XAU/USDT perpetual — the
listing date, in all likelihood. It is not a gap we can backfill.**

## Cross-validation against Round 205

An independent confirmation that Round 205 measured the real thing, from a
different tool (SQL against Timescale vs. the `finance-research` CLI):

| 4h candles | Round 205 (2026-08-25) | Round 208 (2026-08-28) | delta | expected accrual |
|---|---|---|---|---|
| binance XAU | 1,543 | **1,562** | +19 | ~18 (3 days x 6) |
| exness XAU | 7,986 | **8,009** | +23 | ~23 |

Both match the passage of time. Round 205's sample-size diagnosis was correct and
is now explained rather than merely observed.

(Third gold source, never used in research: bybit XAUT 4h = **3,026 candles**.)

## What this changes for the program

1. **The XAU/binance ceiling is structural and permanent on any research
   horizon that matters.** The route accrues one day per day. Three years of 4h
   history arrives around 2028-12. No amount of tooling or backfill work moves it.
2. **Round 203/205's "no validated strategy for XAU/binance" is therefore not a
   temporary state.** It is the expected consequence of a 260-day sample, and the
   frozen route stays frozen for a reason that will not resolve itself soon.
3. **Binance XAU must never again be primary evidence for a gold candidate.**
   Round 205 came close to promoting `engulfing_pattern` on 75/27/32 binance
   trades before exness's 322/107/106 inverted it. That was not luck; it is what
   a 260-day window will keep producing.
4. **Proposed methodology change: replace binance XAU with bybit XAUT as the
   second gold cross-check.** bybit XAUT has 3,026 4h candles against binance
   XAU's 1,562 — nearly double — and is currently unused by any round. Gold
   validation would then read: exness (5 years, authoritative) x bybit XAUT
   (504 days, real cross-check) x binance XAU (260 days, confirmation only).
   This is a proposal, not a validated result: bybit XAUT is spot Tether Gold,
   not a CFD on spot gold, and no round has yet checked whether its price series
   tracks XAU closely enough to serve as a cross-broker falsifier. That check is
   the natural next experiment and it is a backtest, not a query.

## Honest limits

- The venue horizon is inferred from a controlled comparison inside our own
  database (same-transaction registration, same pipeline, BTC reaching five
  years), **not** from Binance's own listing record. The remaining confirmation
  is one bounded broker query: ask the Binance adapter for an XAU/USDT kline
  before 2025-12-11. If it returns nothing, the direction closes permanently
  from the venue side too.
- No backtest container ran this round. This is the third consecutive round
  without one; unlike the previous two, this round is the prerequisite that
  decides whether further XAU/binance backtests are meaningful at all — and it
  says they are not. The next round should run the bybit XAUT correlation
  experiment proposed above.
- Minor, consistent with a known backlog item: binance XAU `1m` holds only
  2026-08-11 → 2026-08-15 (4 days), matching the recorded "1m collection is
  disabled" finding.
- Gap markers on 4h gold are negligible: exactly 2 candles carry
  `broker_session_or_no_tick` across binance + exness; the rest carry an empty
  reason. (Noted because an earlier query in this round appeared to show every
  candle marked — that was a misreading of empty-string versus NULL in `psql -A`
  output, resolved before any number here was used.)
