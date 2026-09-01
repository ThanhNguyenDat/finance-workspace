# Round 149 — Vortex Indicator + Realized Volatility Regime Filter: closed, falsified on 5-year honest backtest

## Context

`VortexIndicatorStrategy` and `RealizedVolatilityRegimeFilterStrategy` were
implemented locally in `finance-live-action` back in Round 121/130-131 but
never got a real backtest run — every `finance-research` attempt through
Round 145 hit the `KlineService/Stream` 1-slot gate saga (see
`docs/reviews/kline-stream-gate-capacity-saga.md`). Round 145 confirmed the
`MaxConnectionAge` fix works; Round 148 confirmed it again on a second cycle
(`in_flight` 0 at the 30-31 min mark, `sent` climbing) and got a full 5-year
BTC/binance backtest through cleanly — the first real numbers for these two
candidates.

## Method

`finance-research`, Docker, `--cpus=2`, `--broker binance --market-type
perpetual_future --base-asset BTC --quote-asset USDT --interval 5m --days
1825 --json` (5-year window, 525,600 candles: train 315,360 / validation
105,120 / holdout 105,120). Plain sweep table (no `--daily-profit-gate`),
scores every registered candidate including the two local unpromoted ones.

## Results

All four sweep entries touching the new mechanisms:

| strategy | train PF | validation PF | holdout PF | holdout trades | holdout win rate |
|---|---|---|---|---|---|
| `vortex_indicator_14` | 0.388 | 0.357 | 0.344 | 11,276 | 15.8% |
| `candle_momentum_rv_regime_filter_10_50_1.1` | 0.495 | 0.466 | 0.479 | 6,460 | 26.5% |
| `candle_momentum_rv_regime_filter_10_50_1.3` | 0.612 | 0.542 | 0.553 | 3,781 | 28.6% |
| `rsi_mean_reversion_rv_regime_filter_10_50_1.1` | 0.834 | 0.845 | 0.574 | 855 | 56.4% |

## Verdict: CLOSED, both falsified

- **Vortex Indicator (VI+/VI- crossover, period 14):** PF stays in a tight
  0.34-0.39 band across all three splits — no "weak train, strong later"
  false-positive shape, just a consistently losing mechanism on BTC 5m. Raw
  crossover signal is too noisy at 5m without a trend-strength or volatility
  filter; not worth revisiting without a materially different filter
  attached.
- **Realized Volatility Regime Filter** (applied to `candle_momentum` and
  `rsi_mean_reversion` as the base signals): every variant stays PF<1 on all
  three splits. The `1.3` threshold variant is the least-bad (holdout PF
  0.553) by cutting trade count roughly 3x vs the `1.1` threshold, showing
  the filter *is* doing something (fewer, marginally better trades) — but
  even the filtered signal never crosses PF=1. The high win-rate RSI variant
  (56.4% holdout) still loses because its RR is too poor to compensate,
  consistent with the mean-reversion-at-5m failure mode seen repeatedly in
  this program (see closed-directions table in
  `research/quant/index.md`).

Neither candidate is promoted. No further investigation planned for either
mechanism at 5m without a genuinely different base signal or timeframe —
matches the same closed-directions pattern as prior filter-family attempts
(ADX/min-strength/volume filters, all closed for the same reason: a filter
narrows a bad base signal to fewer bad trades, it doesn't fix the sign).

## Housekeeping

- Both candidates' code stays in the working tree
  (`crates/finance-strategy/src/indicators/vortex.rs`,
  `RealizedVolatilityRegimeFilterStrategy` in
  `crates/finance-research/src/strategies.rs`) per this program's convention
  — unvalidated/closed candidates are not deleted, just not promoted, so a
  future round can see exactly what was tried without re-deriving it.
- This also serves as a second independent confirmation that the
  `MaxConnectionAge` gate fix (Round 142) works across repeated cycles, not
  just the single Round 145 observation — see
  `docs/reviews/kline-stream-gate-capacity-saga.md` for the updated state.
