# Round 268 — `binance XAU`'s data supports *more* trading than the healthy route's, not less: the shortfall is policy-side, not data-side

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps (exactly the
2-container budget), matched 260-day window.

## The leg of the confound a backtest can settle

Rounds 263-267 could not resolve the seed ↔ weights direction from snapshots. But a
prior question is settleable and had never been asked: **is `binance XAU`'s low
activity a property of its market data, or of its deployed policy and seed?**

The Alpha sweep is the right instrument for this because it is **policy-independent**
— it scores each candidate on its own ledger, without `interval_weights`,
`strategy_weights`, `minimum_role_score` or the sign gate. So it measures what the
instrument's price series can support, with the Portfolio layer removed entirely.

Matched window: 260 days, the span bounded by `binance XAU`'s history (data begins
2025-12-11). Same interval, same candidate set, production costs.

## Result — the "dormant" route's data is the more active one

| | **binance XAU/USDT** (8 live trades) | **exness XAU/USD** (395 live trades) |
|---|---|---|
| candles / 260 d | 1559 (6.00/day, 24/7) | 1130 (4.35/day, weekend-closed) |
| mechanisms scored | 36 | 36 |
| **median trades per mechanism** | **71.5** | **39.0** |
| p25 / p75 | 32 / 146 | 11 / 92 |
| busiest mechanism | `candle_momentum` 474 | `candle_momentum` 444 |
| median trades / week | **1.92** | 1.05 |
| **trades per candle** | **0.0459** | 0.0345 |

**Per candle, `binance XAU` is 1.33x more active than `exness XAU`, and per week
1.83x.** The candidate ranking is nearly identical on both
(`candle_momentum` → `heikin_ashi_momentum` → `rsi` → `macd_trend` → `elder_ray`),
so the same mechanisms find the same kind of material on both instruments.

## What that settles

**The instrument is not quiet, and the data is not the cause.** With the Portfolio
layer removed, `binance XAU`'s own price series supports *more* candidate trading
than the route that has produced 395 live trades against its 8.

Rounds 262-267 eliminated the replay window, replay completion, data depth, data
continuity, synchronization and decision cadence. This round is the first to rule
something **in**: the shortfall lives on the **policy/seed side** — the weights, the
gate, or the near-empty seed that feeds them — not in the market data.

That does not pick between seed and weights. It removes the last non-policy
alternative.

## Severity unchanged

Round 264 de-escalated this to **P3** because no live impact was demonstrated:
all six routes construct decisions at identical cadence, and the live close-rate
difference (1 against 3-4) is within Poisson noise. **That still holds** — this round
does not show harm, it shows the *headroom* is real. If a shortfall exists, it is
policy-side; whether one exists at all is still unestablished.

## What is proven, and what is not

Proven:

- On a matched 260-day window at the same interval and candidate set: `binance XAU`
  median 71.5 trades per mechanism against `exness XAU`'s 39.0; 0.0459 vs 0.0345
  trades per candle; 1.92 vs 1.05 per week.
- The busiest-mechanism ordering is the same on both routes.
- The sweep applies none of the Portfolio policy, so this isolates instrument from
  policy.

Not proven, and deliberately not claimed:

- **That the Portfolio layer *should* trade more on `binance XAU`.** The sweep
  measures individual Alpha candidates, not gated Portfolio decisions; a healthy
  gate legitimately rejects most candidate activity (99.3-99.8% hold on every
  route, Round 265).
- That the 4h result carries to the production 5m interval. The ratio ought to, but
  that was not measured.
- Which of seed or weights is the cause. Unchanged from Round 263.
- That `binance XAU` has a Target 3 shortfall. One live close in 46 hours gives a
  95% interval of [0.09, 20.30]/week (Round 259) — it settles nothing.
- Anything about PnL. Not examined.
