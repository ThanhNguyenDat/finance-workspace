# Round 17 (2026-08-20) — Swing 4h/1d family: regime-filter/frequency sweep

Status: research-only, honest backtest via `finance-research` CLI against real
production Finance MW data (SSH tunnel `root@160.22.122.55:8086` →
`127.0.0.1:18086`, `--broker binance --base-asset BTC --quote-asset USDT
--interval 4h --higher-timeframe-interval 1d --days 1825`). No code changed,
no config touched. Continuing the same session's `raw/portfolio-btc-optimization-log.md`
Round 14/16 finding (`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, the
first candidate this whole program found with positive Sharpe+Sortino+
consistent PF>1, but blocked by a 48-day negative-day streak and only
0.35 trades/week vs the user's 7/week target).

## What this round tested

Same 4h base / 1d higher-timeframe pairing as the Round 14 winner (never
tested at this swing timescale before this round for anything but the plain
sma50 stochastic), applied to three regime-filtered/alternate-entry MTF
candidates that already exist in `strategies.rs` but had only ever been swept
at a different (shorter, likely 5m/4h) timescale per their code comments:

1. `mtf_candle_momentum_10bps_sma10_trend_filtered` — momentum entry instead
   of stochastic, sma10 (faster) trend filter.
2. `mtf_macd_5_13_5_sma10_trend_filtered` — MACD-crossover entry, sma10 trend
   filter.
3. `mtf_stochastic_14_3_35_65_adx14_20_sma10_trend_filtered` — same
   stochastic family but ADX(14)<20 ranging-regime gate stacked on top.

Also re-ran the Round 14 baseline (`..._sma50_trend_filtered`) fresh this
round to get its full daily-results series for a fair side-by-side (all 4
now measured with identical extended-metric methodology, see below).

## Extended metrics methodology (new this round)

`--daily-profit-gate --json` only emits Sharpe, Sortino, drawdown fraction,
negative-day streak, cost ratio, and `positive_day_ratio` in its `checks`/
`metrics` blocks — it does **not** emit Information Ratio, Ulcer Index, SQN,
skewness/kurtosis, or drawdown *duration* (only drawdown *fraction*), even
though the tool's own `daily_results` array (366 real per-day
`{date, realized_pnl, return_fraction, maximum_drawdown_fraction,
ending_equity}` rows) has everything needed to derive them. Computed the
following myself from that real array (not fabricated, not estimated —
formulas below, one Python pass over the actual `daily_results` each gate run
returned):

- **Ulcer Index**: `sqrt(mean(drawdown_pct^2))` over the daily
  peak-to-current-equity drawdown series.
- **Max drawdown duration (days)**: longest run of consecutive days with
  `drawdown_pct > 0` (i.e. equity below its running peak).
- **Max consecutive losing *days*** (not trades — the tool only exposes
  daily-aggregated PnL, not a per-trade ledger, so this is a day-level proxy
  for the trade-level "Max Consecutive Losses" metric the user asked for).
- **Skewness / excess kurtosis**: of the daily `return_fraction` series,
  standard moment formulas.
- **"SQN" (daily-return approximation)**: `mean(daily_return) /
  std(daily_return) * sqrt(n_days)` — labelled explicitly as a
  daily-return-based approximation, **not** the real Van Tharp System Quality
  Number (which is defined on a per-trade R-multiple distribution). Flagged
  as not equivalent, not a substitute.
- **Information Ratio**: **not computed**. IR needs a benchmark return series
  (e.g. buy-and-hold BTC) to take the excess-return ratio against; this tool
  has no benchmark series wired in anywhere. Left blank in the CSV, logged as
  a real tool gap below rather than silently substituting Sharpe for it.

## Results (BTC/binance, 4h base / 1d higher-tf, 5-year window, holdout = 366 days)

| Candidate | Holdout trades | Holdout win% | Holdout PF | Sharpe | Sortino | Net PnL (holdout $) | Max neg-day streak | Max DD duration (days) | Ulcer Index | Skew (daily ret) | Excess kurtosis | SQN (daily, approx) | Trades/week (holdout) | Gate `passed` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `mtf_stochastic_14_3_30_70_sma50_trend_filtered` (R14 baseline) | 18 | 50.0% | 1.65 | 1.13 | 3.10 | 1.69 | 48 | 120 | 0.0030 | 8.25 | 91.48 | 1.136 | 0.34 | **false** (only `negative_day_streak`) |
| `mtf_candle_momentum_10bps_sma10_trend_filtered` | 65 | 38.5% | 1.115 | 0.24 | 0.49 | 0.41 | 17 | 196 | 0.0081 | 4.99 | 43.31 | 0.239 | 1.24 | **false** (`positive_day_ratio`, `negative_day_streak`, `sortino_ratio`, `sharpe_ratio`) |
| `mtf_macd_5_13_5_sma10_trend_filtered` | 31 | 45.2% | 1.238 | 0.31 | 0.64 | 0.63 | 25 | 117 | 0.0063 | 5.81 | 56.10 | 0.307 | 0.59 | **false** (same 4 as above) |
| `mtf_stochastic_14_3_35_65_adx14_20_sma10_trend_filtered` | 11 | 63.6% | 4.07 | 1.37 | 4.61 | 2.51 | 66 | 87 | **0.0022 (best)** | 9.78 | 120.77 | **1.370 (best)** | 0.21 | **false** (`positive_day_ratio`, `median_daily_pnl`, `negative_day_streak`) |

All 4 also pass PF>1 consistently across train/validation/holdout (only these
4 do, out of the 51 candidates the same sweep call scored for this timescale
— every other MTF/plain candidate in this same sweep had at least one split
with PF<1, so this table is not cherry-picked, it's the complete set of
"consistent PF>1 across 3 splits" survivors at this timescale).

## Honest conclusion — a real, quantified tension, not a fixable gap

1. **Frequency vs. quality trade off is now measured, not assumed.**
   Candle-momentum's sma10 filter trades **3.6x more often** than the sma50
   stochastic baseline (1.24 vs 0.34/week) but its Sharpe collapses from 1.13
   to 0.24 and its Ulcer Index nearly triples (0.0081 vs 0.0030) — worse
   risk-adjusted quality *and* the max drawdown duration actually gets worse
   (196 vs 120 days) despite the shorter losing-day streak. More trades here
   means noisier trades, not "the same edge sampled more often."
2. **The ADX ranging-regime filter is the best quality candidate found in
   this whole research program by Sharpe/Sortino/Ulcer/SQN** (1.37 / 4.61 /
   0.0022 / 1.37) — but it achieves that by trading even *less* often (0.21/
   week, the lowest of the 4) and tolerating an even longer losing-day streak
   (66 days, worse than the baseline's already-failing 48). It fails 3 gate
   checks instead of the baseline's 1. Higher quality per trade, strictly
   worse on every axis the user's Rule 3 cares about (frequency, streak).
3. **None of the 4 candidates in this family — across a real trade-off
   spectrum from "most frequent, weakest edge" to "rarest, strongest edge" —
   can satisfy both quality gates and the user's 7-trades/week floor
   simultaneously.** This isn't one bad parameter choice; it's 4 genuinely
   different entry/filter mechanisms on the same timescale converging on the
   same ceiling. Structural, not tunable: a swing strategy whose *trend
   filter* (the thing responsible for all 4 candidates' positive-PF edge —
   confirmed separately by this program's Round 8/47 finding that R:R/sizing
   cannot create an edge which isn't already there) requires waiting for
   4h/1d-scale trend agreement cannot also fire multiple times a day by
   construction. Squeezing more trades out of this family (by loosening the
   filter, as `sma10` vs `sma50` already shows) trades away the very edge
   that made it interesting in the first place.

**Recommendation for whoever picks this up next (not implemented by this
session — explore/optimize scope only):** stop trying to make the 4h/1d
swing family itself hit 7 trades/week. The only two paths that don't fight
this structural ceiling: (a) treat swing as a genuinely separate frequency
bucket with its own lower target (as Round 14 already proposed and this round
reconfirms with 3 more data points), or (b) use the swing signal's *direction*
as a bias/gate on the existing high-frequency 5m Alpha signals
(`candle_momentum`, `rsi_mean_reversion`, already live) rather than as its own
entry signal — i.e. only take 5m entries that agree with the 1d trend, which
would let the 5m layer supply the trade count while the swing layer supplies
directional quality. This is a **new StrategyKind / decision-policy change**,
not a parameter sweep — genuinely new code, logged to `raw/handoff_codex.md`
below as a concrete P2 proposal, not implemented here.

## Tool gap found this round (new, logged to handoff)

`finance-research --daily-profit-gate` has no frequency/trades-per-week
threshold check at all (confirmed: `failed_checks` only ever contains items
from `{minimum_holdout_days, holdout_interval_continuity,
positive_day_ratio, median_daily_pnl, negative_day_streak, daily_drawdown,
total_drawdown, sortino_ratio, sharpe_ratio, gross_pnl_positive,
cost_to_gross_pnl_ratio}` — grepped the full JSON schema across all 4 gate
runs this round). The user's explicit Rule 3 target (≥1/day or ≥7/week) is
currently invisible to this gate — a candidate could pass every other check
and still be un-deployable on frequency, and the tool wouldn't say so. Logged
as a concrete, scoped feature request below.
