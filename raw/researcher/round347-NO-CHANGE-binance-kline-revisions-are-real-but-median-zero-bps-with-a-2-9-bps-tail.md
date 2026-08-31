# Round 347 — NO-CHANGE: Binance revises **74% of closed 5m bars**, but the price change is **median 0.0000 bps** with a **2.90 bps** worst case. Divergence 1 de-escalates — and the route the whole arc depends on has **zero** revisions.

Classification: **NO-CHANGE** — the pre-registered partition fired the de-escalation branch, no
research conclusion moves, and nothing about the deployed configuration changes. **Zero
containers**; all evidence is read-only production observation. **XAU-first** in consequence:
the finding's main import is that `exness XAU` is unaffected.

## The follow-up the observability audit named

The observability audit recorded **Divergence 1**: Binance logs *"Exchange revised a closed
kline; matching history entry replaced and strategy evaluation remains blocked for this
revision"*, so live traded the **pre-revision** candle while the replay reads the
**post-revision** Timescale row. It closed with *"magnitude is not established — the log carries
no before/after prices"* and named the follow-up.

**Pre-registered as a partition:** let **D** = median relative `|Δclose|` in basis points
between what the live strategy used and what Timescale stores, over a sample of `binance BTC`
5m bars.
- **D ≥ 1 bps** → material against the 7 bps round trip; Divergence 1 escalates;
- **D < 1 bps** → cosmetic; Divergence 1 de-escalates to a documentation note.

## How the magnitude was obtained without Kafka

The broker's internal listener refused the console consumer on the port available to a
read-only session, and chasing it further would have meant hunting credentials — out of scope.
A cleaner source was already in hand: the live worker logs a `Signal evaluated` event carrying
the `price` the strategy actually used, and the same message's span carries
`market.event.id`, which identifies the bar. Joining that against Timescale's stored
`close_price` for the same bar **is** the pre-versus-post revision delta.

Sample: `binance BTC/USDT` perp 5m, 2026-08-30 00:00 → 17:30 UTC, **125 distinct bars** where a
signal fired.

A useful self-check falls out: if my bar alignment were off by one bar the deltas would be tens
of basis points (a 5m BTC move); they are hundredths. The alignment is right.

## Result — the de-escalation branch fires

| statistic | value |
|---|---|
| bars compared | 125 |
| **identical (0 bps)** | **64 (51.2%)** |
| differing | 61 (48.8%) |
| **median \|Δ\|** | **0.0000 bps** |
| mean | 0.1806 bps |
| p95 | 1.4211 bps |
| **max** | **2.8955 bps** |
| median among differing bars | 0.0128 bps |

| threshold | bars at or above |
|---|---|
| ≥ 0.1 bps | 24 (19.2%) |
| ≥ 0.5 bps | 12 (9.6%) |
| ≥ 1.0 bps | 8 (6.4%) |
| ≥ 2.0 bps | 4 (3.2%) |
| **≥ 7.0 bps (round-trip cost)** | **0 (0.0%)** |

Largest observed: 2026-08-30 04:20, live 78075.30 against stored 78052.70 — 22.60 absolute,
**2.8955 bps**.

**D = 0.0000 bps. Divergence 1 de-escalates to P3.**

## The tail is not nil, and I am not pretending otherwise

A median of zero is the registered criterion, but 6.4% of bars differ by **≥ 1 bps** and 3.2% by
**≥ 2 bps** — the same order as the deployed **2 bps slippage line**. Round 345 showed this
replay turns a **1.4%** cost perturbation into a **15%** change in gross, so a systematic input
perturbation of this size on roughly half the Binance bars is **not self-evidently negligible**
for Binance routes. What the measurement establishes is that it is **bounded well below the
round-trip cost**, not that it is zero.

## Why this barely touches the arc

The revision counts, full day 2026-08-29: `binance BTC` **347**, `binance XAU` **154**, and
**zero** on `bybit BTC`, `bybit XAUT`, `exness BTC` and `exness XAU`. Per interval on
`binance BTC` that is a **74.0%** revision rate at 5m (213 of 288), 68.8% at 15m and 30m, 83.3%
at 1h and 4h.

**`exness XAU` — the only route with a positive gross edge, and the subject of Rounds 313-346 —
has no revisions at all.** The divergence is confined to the two Binance routes, both of which
already fail on negative gross. No conclusion in the arc rests on them.

## What is proven, and what is not

Proven:

- 125 `binance BTC` 5m bars, 2026-08-30 00:00-17:30 UTC: 64 identical, 61 differing; median
  |Δ| **0.0000 bps**, mean 0.1806, p95 1.4211, max **2.8955**; 8 bars ≥1 bps, 4 ≥2 bps, **0
  ≥7 bps**.
- Revision counts and per-interval rates for 2026-08-29 as tabulated; zero revisions on all
  Bybit and Exness routes.
- The comparison method: live `Signal evaluated` `price` joined to Timescale `close_price` on
  the bar identified by the event's `market.event.id`.

Not proven, and deliberately not claimed:

- **That 48.8% is the revision rate.** My sample is bars **where a signal fired**, not all bars;
  the log-derived revision rate on the same route is **74.0%** at 5m. These are different
  populations and I am not equating them.
- **That the deltas are harmless.** The registered criterion is met at the median; the tail
  reaches the slippage line, and Round 345's amplification result means small systematic input
  changes are not safely ignored here. What is established is a **bound**, not harmlessness.
- **That live always used the pre-revision value.** The log message says evaluation is blocked
  for the revision; I read the code path only far enough to quote it, and did not verify the
  ordering of revision arrival against signal emission per bar.
- Anything about intervals other than 5m, routes other than `binance BTC`, or days other than
  2026-08-30 for the magnitude.
- Any promotion. Nothing here changes a configuration or a result.
