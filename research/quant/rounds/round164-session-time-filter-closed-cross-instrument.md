# Round 164 — Session time-of-day filter: genuinely new mechanism, closed cross-instrument

## Context

After Round 163's correction (Rule 1's classic Portfolio-construction space
confirmed exhausted — hold, stop/take, their interaction, and sizing-mode
all already closed by Round 87-92/151-152), this round returns to Rule 2/3
with a mechanism verified as genuinely untested: an intraday hour-of-day
session filter, distinct from the CLOSED day-of-week seasonality test
(Round 47, a data-mining artifact on a weekly cycle) — this filters by UTC
hour instead, the standard "avoid thin Asian-session liquidity, trade the
London/NY overlap" heuristic from FX/gold systematic trading.

## Implementation

`SessionTimeFilterStrategy` (`crates/finance-research/src/strategies.rs`) —
wraps an inner strategy, forwards its signal only when `kline.open_time`'s
UTC hour falls inside `[start_hour, end_hour)` (wrapping past midnight when
`start > end`). Stateless (no rolling window). Two windows tested, layered
on both production base signals:

- `12-16 UTC`: the classic London/NY liquidity overlap.
- `6-22 UTC`: broader window excluding only the thin Asian session
  (22:00-06:00 UTC).

Unit tests cover same-day and midnight-wrapping window logic. `cargo fmt
--check` clean; full workspace suite green (130/130 in the touched crates).
Committed to `finance-live-action` alongside this round's backtest evidence.

## Results

5-year window, both BTC/binance and XAU/binance (XAU tested first per this
program's stated priority):

| instrument | candidate | train PF | validation PF | holdout PF | holdout trades |
|---|---|---|---|---|---|
| XAU | `candle_momentum` + London/NY overlap | 0.483 | 0.579 | 0.454 | 267 |
| XAU | `candle_momentum` + exclude-Asian | 0.356 | 0.420 | 0.342 | 484 |
| XAU | `rsi_mean_reversion` + London/NY overlap | 0.614 | 0.492 | **0.971** | 55 |
| BTC | `candle_momentum` + London/NY overlap | 0.515 | 0.481 | 0.563 | 3,481 |
| BTC | `candle_momentum` + exclude-Asian | 0.400 | 0.380 | 0.374 | 10,891 |
| BTC | `rsi_mean_reversion` + London/NY overlap | 0.894 | 0.945 | 0.612 | 412 |

## Verdict: CLOSED

- **`candle_momentum` variants (both windows, both instruments):** clean
  PF<1 across all 3 splits, no false-positive shape — consistent
  falsification cross-instrument. The London/NY overlap window is
  consistently the *less bad* of the two (fewer, marginally better trades),
  showing the filter does something, but never crosses PF=1.
- **`rsi_mean_reversion` + London/NY overlap on XAU:** holdout PF 0.971 is
  the closest-to-breakeven result in this file, but on only 55 trades with
  train(0.614)/validation(0.492) well below — this is exactly the "only
  holdout wins" shape the skill's own methodology flags as a known
  false-positive pattern requiring independent-window re-test before any
  trust. Not chased further this round given the thin sample and the
  pattern match to prior false positives in this program (e.g. Round 94's
  Donchian+trend-filter reversal). Not promoted.
- **`rsi_mean_reversion` + London/NY overlap on BTC:** the opposite,
  *honest* shape — strong train/validation (0.894/0.945) collapsing on
  holdout (0.612) — a real generalization failure, not a candidate.

No promotion. Code stays in the working tree per this program's convention.
This adds one more closed direction to the "structural ceiling" evidence
base (Round 93's plateau finding, Round 150's 7-oscillator convergence):
a filter that changes *which hours* trade, much like the volatility/ADX/
volume filters already closed, narrows a negative-edge base signal to fewer
negative-edge trades without changing its sign.
