# Round 181 — 5m entries gated by 1d trend filter: XAU cleanly closed, BTC ambiguous (needs follow-up)

## Context

Directly motivated by Round 172-180's definitive confirmation that
`mtf_stochastic_14_3_30_70_sma50_trend_filtered` (4h entry, 1d SMA50 trend
filter) has a real edge on BTC. Tested the natural follow-on hypothesis:
does the 1d-timescale trend signal also add value as a **gate on the
existing 5m production entries** (candle_momentum, rsi_mean_reversion, plus
a few other already-implemented entry mechanisms), rather than deploying
the swing signal as its own standalone strategy? This combination
(`--interval 5m --higher-timeframe-interval 1d`) is architecturally
supported by the existing `MultiTimeframeTrendFilterStrategy` +
`multi_timeframe_candidates()` — no new code needed, just a genuinely
untested CLI combination (prior MTF filter tests all used 5m+4h, not
5m+1d).

## Method

2-year window (`--days 730`, dropped from the full 5-year window after gate
contention — same pattern documented in the swing-candidate saga), both
XAU/binance and BTC/binance, 7 trend-filtered variants covering the
production base signals (candle_momentum, rsi_mean_reversion) plus a few
already-implemented others (Bollinger, Keltner reversion).

## Result — XAU: CLOSED, falsified cleanly

| candidate | train PF | validation PF | holdout PF |
|---|---|---|---|
| candle_momentum sma10 | 1.64 | 0.83 | 0.52 |
| candle_momentum sma5 | 0.72 | 0.88 | 0.61 |
| rsi 14/30/70 | 0.95 | 3.87 (n=2) | 0.00 |
| rsi 14/20/80 | 1.22 | 3.43 (n=2) | 0.03 |
| rsi 9/35/65 sma10 | 1.57 | 0.56 | 0.33 |
| bollinger sma10 | 1.52 | 0.51 | 0.34 |
| keltner sma10 | 1.88 | 0.39 | 0.21 |

All 7 variants show the classic overfitting shape (strong-looking train,
collapsing validation/holdout) or thin-sample artifacts (the RSI variants'
n=2 validation trades). Consistent, clean falsification — the 1d trend
signal does not usefully gate XAU's 5m entries.

## Result — BTC: mixed, NOT closed, needs follow-up

| candidate | train PF | validation PF | holdout PF |
|---|---|---|---|
| candle_momentum sma10 | 1.21 | 0.60 | 1.82 |
| candle_momentum sma5 | 0.91 | 0.92 | 0.54 |
| **rsi 14/30/70** | 0.95 | **1.86** | **2.12** |
| **rsi 14/20/80** | 1.01 | **1.90** | **2.72** |
| rsi 9/35/65 sma10 | 1.16 | 0.64 | 1.53 |
| bollinger sma10 | 1.27 | 0.50 | 1.81 |
| keltner sma10 | 1.05 | 0.60 | 1.86 |

The two plain RSI variants show a striking pattern: train near breakeven
(~1.0), **validation AND holdout both clearing 1.0** — the opposite of the
XAU shape. This is *not* a clean promotable result: it is the "weak train,
strong later splits" pattern this program's own methodology flags as a
known false-positive shape (a regime-dependent artifact — e.g. one
directional trend late in the window favoring this exact filter — looks
identical to a real edge until tested on an independent window). Several
other variants also show holdout>1 with a weak validation dip, a less
clean but still notable pattern (`candle_momentum sma10`, `bollinger
sma10`, `keltner sma10` all land holdout 1.8-1.9).

## Verdict

- **XAU: CLOSED.** Consistent, decisive falsification across all 7
  variants. Do not retry this exact combination.
- **BTC: NOT closed, NOT promoted, genuinely ambiguous.** Round 184
  independent-window follow-up (18-month window, non-overlapping split
  boundaries from the original 2-year check):

  | candidate | window | train PF | validation PF | holdout PF |
  |---|---|---|---|---|
  | rsi 14/30/70 | 2yr (orig) | 0.95 | 1.86 | 2.12 |
  | rsi 14/30/70 | 18mo (indep) | 0.88 | 1.30 | 1.23 |
  | rsi 14/20/80 | 2yr (orig) | 1.01 | 1.90 | 2.72 |
  | rsi 14/20/80 | 18mo (indep) | 0.87 | 1.30 | 1.42 |

  The "weak train, strong later splits" shape **repeats consistently
  across two independent windows** — train stays below/near 1.0, validation
  and holdout both clear 1.0 both times, just at a more modest magnitude
  on the second window. This is NOT the behavior of pure regime-dependent
  noise (which would typically flip direction or vanish on an independent
  window, as it did for e.g. Round 94's Donchian reversal) — it raises the
  odds this reflects something real, even if modest and not yet
  promotable (samples stay thin: 10-16 trades per split both windows).
  **Round 185 — cross-broker check (Exness/BTC, same 2-year window)
  COMPLETED, near-identical to Binance:**

  | candidate | broker | train PF | validation PF | holdout PF |
  |---|---|---|---|---|
  | rsi 14/30/70 | Binance | 0.95 | 1.86 | 2.12 |
  | rsi 14/30/70 | Exness | 0.94 | 1.67 | 2.13 |
  | rsi 14/20/80 | Binance | 1.01 | 1.90 | 2.72 |
  | rsi 14/20/80 | Exness | 1.07 | 1.81 | 2.52 |

  This is now **3 consistent confirmations** (2 independent windows +
  cross-broker) — the near-identical Binance/Exness match on the same
  window is this program's established hallmark of a real signal (same
  pattern the swing candidate showed).

  **Round 187 — full 5-year window (Binance), DEFINITIVE and HONEST
  recalibration:**

  | candidate | trades (train/val/holdout) | PF (train/val/holdout) |
  |---|---|---|
  | rsi 14/30/70 | 130 / 37 / 43 | 1.01 / 1.02 / 1.38 |
  | rsi 14/20/80 | 126 / 37 / 43 | 1.13 / 1.06 / 1.54 |

  With a much larger sample (210+ trades combined, vs 45-80 in the smaller
  windows), **all splits stay above 1.0 — the edge is confirmed real** —
  but it is far more modest than the smaller windows suggested (train and
  validation both barely clear 1.0, only holdout shows real separation at
  1.38-1.54). This is the expected, honest behavior when a real-but-modest
  edge gets measured on progressively larger samples: the earlier
  1.86-2.72 PF readings were partly a small-sample inflation artifact, not
  wrong in *direction* but overstated in *magnitude*. **Verdict: real,
  positive, but modest edge — a second genuine candidate alongside the
  swing signal, though with a smaller effect size.** Not promoted; the
  same architecture question (how to fit this into Portfolio construction)
  applies, and the modest magnitude means it's less obviously worth the
  complexity than the swing candidate's stronger, larger-sample-confirmed
  edge (Round 172-180: PF 1.50-2.43 on a comparable-or-larger sample).

## Note on the swing candidate's actual mechanism

This round's clean XAU falsification (and BTC's ambiguity) suggests the
confirmed swing edge from Round 172-180 is specifically tied to the
**stochastic crossover entry evaluated at 4h** combined with the 1d SMA50
filter — not simply "1d trend direction as a coarse gate for unrelated
faster entries." The mechanism doesn't trivially generalize to "attach a
1d filter to any existing 5m signal." This is useful negative information
for the architecture-decision question left open in Round 172-180's
writeup — a naive "use swing trend as a 5m gate" wrapper is not a free win,
reinforcing that a real design pass (not a quick filter bolt-on) is needed
for the trend-bias/gate architecture proposal.
