# Round 409 — REJECTED: the seventh production strategy loses on holdout too — and shows the **strong-train, collapsing-later** shape the codebase's own comments call disqualifying.

Classification: **REJECTED** — the pre-registered criterion answered negative.
Two containers (the budget), cleaned up. Closes the question round 408 opened.

## The measurement

`mtf_stochastic_14_3_30_70_sma50_trend_filtered` — production's
`mtf_stochastic_4h_1d_sma50`, deployed on both BTC routes and absent from the
research mirror (r408) — run for the **first time at its own intervals**:
`--interval 4h --higher-timeframe-interval 1d`, pinned window, 5,401 candles.

| route | holdout | trades | train | validation | **holdout** |
|---|---|---|---|---|---|
| `binance BTC` | 2026-03-04 → 2026-08-31 | 11 | +1.06746 | −0.11951 | **−1.12232** |
| `exness BTC` | 2026-03-04 → 2026-08-31 | 11 | +1.09441 | −0.11826 | **−1.15979** |

**Registered answer: neither positive.** **All seven distinct production
strategies now lose on holdout.**

## The shape

Train **positive**, validation **negative**, holdout **more negative** — on both
routes, nearly identically.

That is the pattern `strategies.rs`'s own documentation calls out and rejects:

> *"shows the classic overfitting shape instead … strong-train-weak-later is the
> inverse of, and just as disqualifying as, the 'weak-train-strong-later'
> pattern this program has repeatedly flagged and falsified elsewhere."*

The comment was written about a **candidate that was closed** for showing it.
The same shape appears here on a strategy that is **deployed**.

## And it barely trades

**11 holdout trades over 180 days = 0.43 per week.** Whatever this strategy
contributes to the six-strategy BTC ensembles, it is not frequency.

The two routes agreeing to within 3% (−1.122 against −1.160, 11 trades each) is
consistent with r276's finding that they are near-duplicate markets, not two
independent confirmations.

## The complete production picture

Seven distinct configurations across the fleet, all measured on holdout:

| # | config | worst / best holdout across routes |
|---|---|---|
| 1 | `candle_momentum` (10bps) | −21.08 |
| 2 | `rsi_mean_reversion` (14/30/70) | −6.56 |
| 3 | `mtf_stochastic` sma5 | −2.13 / **−0.05** |
| 4 | `mtf_stochastic` sma10 | −1.32 / −0.92 |
| 5 | `mtf_macd` sma10 | −1.56 / −1.50 |
| 6 | `mtf_candle_momentum` sma10 | −0.97 / −0.54 |
| **7** | **`mtf_stochastic` 4h/1d sma50** | **−1.16 / −1.12** |

**Every one loses.** The best single figure anywhere is −0.05.

## What is proven, and what is not

Proven:

- The two rows above, at 4h/1d intervals on a pinned window, 5,401 candles each.
- Train positive, validation and holdout negative, on both routes.
- 11 holdout trades per route = 0.43/week.

Not proven, and deliberately not claimed:

- **That the overfitting shape is established.** Three splits on **11 holdout
  trades** is a shape, not a test. The codebase's comment describes the same
  pattern with profit factors on larger samples; I have one sign sequence on a
  thin sample, twice, on near-duplicate markets.
- That this strategy should be removed. It loses on this holdout at low
  frequency; whether it contributes to the ensemble through diversification
  rather than standalone PnL is not something a per-strategy score answers, and
  the Portfolio replay does not consume it (it uses the research mirror, r408).
- That all seven figures are comparable. They come from runs at different
  intervals with different trade counts, from 11 to 3,262.
- Anything about the Portfolio's output. This is the Alpha layer; r394 showed
  the Portfolio removes 98.6% of the loss it is handed on the one route measured.

## Named next step

None that is unblocked. The last runnable backtest question is answered, and it
answered the same way as the other six. What remains is the release decision,
a definition for Target 2, and forward time.
