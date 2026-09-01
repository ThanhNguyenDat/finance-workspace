# Round 205 — Swing 4h/1d sweep on XAU (never run before): CLOSED, binance results falsified cross-broker

## Why this was worth running

Round 17 established the swing 4h/1d family but scoped it to **BTC only**
(`--broker binance --base-asset BTC`). It had never been swept for XAU on
either broker. Three things made it the right next experiment for XAU:

- The only confirmed edge this program has ever found is at 4h/1d (BTC).
- Round 204 re-confirmed that the trend filter, not the oscillator, carries
  whatever edge exists (PF ~0.05 bare vs ~0.7 filtered).
- Round 203 showed XAU/binance's frozen Portfolio needs a genuinely
  validated strategy, and that nothing in the 5m registry qualifies
  (cross-broker join of 71 shared candidates: best `min(PF)` was
  `donchian_breakout_200` at 0.72, with opposite shapes per broker).

## Result — binance looked strong, exness falsified it

| candidate | binance t/v/h | exness t/v/h | exness trades |
|---|---|---|---|
| `engulfing_pattern` | **1.44/1.58/1.73** | 0.65/0.86/0.70 | 322/107/106 |
| `heikin_ashi_momentum_3` | **1.14/1.51/1.16** | 0.63/0.63/1.04 | 469/157/150 |
| `mtf_stochastic_21_5_35_65_sma10_trend_filtered` | **1.80/2.31/1.08** | 0.89/0.53/1.64 | 92/39/33 |
| `sma10_trend_filtered_engulfing_pattern` | 1.66/0.94/1.49 | 0.70/1.20/1.07 | 186/62/57 |
| `mtf_stochastic_14_3_30_70_sma10_trend_filtered` | 1.09/1.33/1.16 | 1.19/0.70/1.79 | 102/41/37 |

Windows: **binance 1,543 4h candles (~257 days)**, **exness 7,986 (~3.6
years)** — binance's local XAU history is 5x shorter, and its samples are
correspondingly thin (75/27/32 for engulfing vs exness's 322/107/106).

Every binance candidate that cleared 1.0 on all three splits inverts on the
broker with 4-5x the sample. That is the same signature that falsified
`atr_breakout_14_3_0` (Round 61), Donchian (Round 88), and Fibonacci Golden
Zone (Round 106): a short-window, thin-sample result that does not survive a
larger independent sample. **No promotion.**

## The tempting wrong conclusion, stated so it is not repeated

`engulfing_pattern` was closed in Round 103 with PF 0.16-0.42 — the lowest
ever recorded here — measured at 5m with ~34k trades, where cost dominates
completely. At 4h on binance it reads 1.44/1.58/1.73 on 75/27/32 trades. It
is very tempting to read that as "candlestick geometry is noise at 5m but
real at 4h, the program closed these mechanisms at the wrong timeframe."

Exness says otherwise: 0.65/0.86/0.70 on 322/107/106 trades at the same 4h
base. The timeframe did not rescue the mechanism; the short binance window
did. **Do not re-open 5m-closed mechanisms at 4h on the strength of
binance XAU alone** — its 257-day history cannot carry that conclusion.

## One weak lead, explicitly not a promotion

`mtf_stochastic_14_3_30_70_sma10_trend_filtered` is the only candidate with
train >1 AND holdout >1 on **both** brokers (1.09/1.16 and 1.19/1.79). Only
exness validation dips (0.70). That is 4 of 6 cells clear across brokers,
which is better than anything else here, but it is not the "all three splits,
both brokers" bar and the binance sample is 18/7/9 trades. Recorded as a lead
to re-test if XAU/binance ever accumulates a longer history; not promotable
now.

## Standing conclusion for XAU

After this round, there is still **no validated strategy to add to
XAU/binance**. Adding any current registry candidate would be the Round 67
"zombie strategy" anti-pattern. Its frozen Portfolio (Round 203) therefore
stays frozen by choice, not by oversight — and per Round 203's backtest, the
unfrozen behavior of that route returns -1.54 PnL anyway, so unfreezing it
without an edge would only lose faster.
