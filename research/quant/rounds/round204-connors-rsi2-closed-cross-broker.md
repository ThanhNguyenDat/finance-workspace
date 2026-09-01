# Round 204 — Larry Connors RSI(2): CLOSED, falsified cross-broker on XAU

## Context

A genuinely new mechanism from published quant literature (Larry Connors,
"How Markets Really Work" / ConnorsRSI family): a very fast RSI(2) with
extreme 10/90 thresholds, traded only in the direction of a long-term trend
filter. Structurally distinct from every RSI variant this program had tried
(period 9/14, thresholds 20-35/65-80). Registered as two research-only
candidates — the bare oscillator and the published trend-filtered form —
`rsi_2_10_90` and `sma200_trend_filtered_rsi_2_10_90`.

Note on the filter: the classic rule uses a 200-**day** SMA on daily bars.
This program's registry sweeps at the CLI's `--interval`, so `200` here is
200 bars of the swept interval (5m), not 200 days. That is a deliberate
scaling of the published rule, not a reproduction of it.

## Result — falsified, both brokers, every split

| broker | candidate | train | validation | holdout | trades (train) |
|---|---|---|---|---|---|
| binance | `rsi_2_10_90` | 0.111 | 0.064 | 0.043 | 9,747 |
| exness  | `rsi_2_10_90` | 0.024 | 0.028 | 0.106 | 41,981 |
| binance | `sma200_trend_filtered_rsi_2_10_90` | 0.707 | 0.905 | 0.750 | 529 |
| exness  | `sma200_trend_filtered_rsi_2_10_90` | 0.425 | 0.552 | 0.865 | 2,296 |

Windows: binance 74,099 candles (~257 days — this instrument's full local
history), exness 353,733 candles (~3.4 years).

No cell clears 1.0 anywhere. The trend filter helps substantially on both
brokers (it is the difference between PF ~0.05 and PF ~0.7), consistent with
this program's standing finding that the filter, not the oscillator, is where
edge lives — but it does not come close to rescuing the entry. The two
brokers also disagree on which splits are least bad, so there is no stable
shape to chase.

**No 18-month cross-window check needed:** nothing is near breakeven on the
5-year/full-history window, which is this program's stated bar for skipping
it.

## The bare variant's failure mode is now an 8-mechanism pattern

`rsi_2_10_90` fired **41,981 times in the exness train split alone**. RSI(2)
with 10/90 thresholds reaches those extremes constantly on 5m bars, so the
strategy trades almost continuously and cost dominates completely (PF 0.024).

This is the same signature as OBV (Round 113, 53,878 trades, PF 0.09-0.37)
and Elder Ray (Round 119, 47,494 trades, PF 0.10-0.35), and the eighth
distinct oscillator mechanism to fail this way after Stochastic, CCI, MFI,
Vortex, and Awesome Oscillator. The convergence across mechanisms that share
nothing but "unfiltered oscillator at 5m" is strong evidence this is a
structural cost ceiling, not a property of any one indicator.

## Process note

This is the candidate that failed to run 7 consecutive times earlier today
across every window size (Rounds 190-196), which is what drove the
investigation into the kline-gate deadlock. After that fix
(finance-live-action `81dfcc1`) both runs completed on the first attempt,
with the gate reading `finance_mw_grpc_requests_in_flight{method="Stream"}=0`
— free for the first time all day. The backtest result here is therefore also
an independent end-to-end confirmation that the deadlock fix works.
