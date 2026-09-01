# Round 209 — bybit XAUT tracks spot gold well enough to be a cross-check, but the usable sample is +41%, not the ~2x I claimed last round

Read-only production data (4h closes, 2025-04-11 → 2026-08-28), analysed
locally. Codex available, nothing implemented. This is the experiment Round 208
proposed for itself.

## The question Round 208 left open

Round 208 proved binance XAU's 260-day history is a venue horizon and proposed
replacing it with **bybit XAUT** as the second gold cross-check, explicitly
flagging the proposal as unvalidated: XAUT is spot Tether Gold on a crypto
venue, not a CFD on spot gold, and no round had checked whether it tracks XAU
closely enough to falsify a candidate.

The bar to clear is not "correlates with gold". It is **"tracks at least about
as well as the binance XAU it would replace"** — because the program already
accepts binance XAU as a legitimate cross-broker falsifier.

## Method

4h log returns on **aligned consecutive bars**: a bar counts only when both
sources have that timestamp *and* the preceding 4h timestamp. This matters —
exness is a weekday CFD, so its raw consecutive returns span weekends while
bybit's span 4 hours. Comparing unaligned returns would manufacture a
correlation artifact.

## Result — XAUT tracks spot gold, nearly as tightly as binance XAU does

| pair | n bars | Pearson | Spearman | tracking error (sd of 4h return diff) | direction agreement |
|---|---|---|---|---|---|
| bybit XAUT vs exness XAU | 2,132 | **0.9915** | 0.9867 | 0.0850% | **95.06%** |
| binance XAU vs exness XAU | 1,096 | 0.9954 | 0.9916 | 0.0724% | 97.63% |
| binance XAU vs bybit XAUT | 1,561 | 0.9837 | 0.9530 | 0.1144% | 90.39% |

Mean return difference is ~0 on all three pairs (−0.0008% / +0.0002% / −0.00002%
per 4h bar), so there is no systematic return bias, only noise.

bybit XAUT tracks exness slightly worse than binance XAU does (0.9915 vs 0.9954;
95.1% vs 97.6% direction agreement) but is unambiguously in the same league.
**The proposal survives its first test.**

## Two conditions the proposal did not anticipate

### 1. 27.1% of bybit's bars have no exness counterpart, and they are a different animal

| bybit 4h bars | n | median volume | median high-low range |
|---|---|---|---|
| with exness counterpart | 2,207 | 419.22 | 0.653% |
| **without** counterpart | **819 (27.1%)** | **140.75** | **0.178%** |

The no-counterpart bars are 432 Saturday + 360 Sunday + 27 session-edge bars.
They carry **one third the volume and one quarter the range** of weekday bars.

That is precisely the microstructure that manufactures false signals: a
mean-reversion oscillator sees a quiet range and trades it; a breakout strategy
sees compressed ranges and fires on the Monday reopen. A candidate backtested on
the full bybit series and a candidate backtested on exness are not being asked
the same question.

**Condition: weekend/no-counterpart bars must be excluded for cross-broker
falsification.** (For a standalone bybit backtest they are real tradeable bars
and excluding them would be wrong — the exclusion is about like-for-like
comparison, not about the venue.)

### 2. There is a slow basis drift, so level-based comparisons are invalid

Median bybit/exness close ratio by quarter:

```
2025Q2  1.00107      2026Q1  0.99767
2025Q3  0.99990      2026Q2  0.99711
2025Q4  0.99945      2026Q3  0.99777
```

A ~0.4% downward drift over 15 months, with per-quarter extremes spanning
roughly ±0.6-1.2%. Per 4h bar that is ~0.001% — irrelevant for return- and
range-based indicators, which is what every candidate in this program uses. It
does mean an absolute price level, a long-lookback SMA *level*, or any threshold
expressed in price units is not comparable across the two sources.

## Correcting Round 208's own number

Round 208 wrote that bybit XAUT has "3,026 4h candles against binance XAU's
1,562 — nearly double". That is the raw count. Once weekend bars are excluded to
make the comparison like-for-like, the usable weekday sample is **2,207 vs
1,562 — a 41% advantage, not ~94%.**

The advantage that survives is still real and is mostly about *reach*, not
count: bybit XAUT starts 2025-04-11 against binance XAU's 2025-12-11, so it
covers **eight additional months** of independent gold history, including a
market regime binance XAU never saw.

## Verdict

**bybit XAUT is conditionally accepted as the second gold cross-check**, on the
two conditions above. Recommended gold validation stack from here:

```
exness XAU/USD   5 years, weekday CFD     -> authoritative long window
bybit XAUT/USDT  504 days, weekday-only   -> real independent cross-check
binance XAU/USDT 260 days                 -> confirmation only, never primary
```

## What is proven, and what is not

Proven:

- Aligned 4h log returns of bybit XAUT and exness XAU correlate 0.9915 (Pearson)
  / 0.9867 (Spearman) over 2,132 bars, direction agreement 95.06%, tracking
  error 0.085% per bar, no systematic return bias.
- The same statistics for the already-accepted binance XAU pair are 0.9954 /
  0.9916 / 97.63% / 0.072%.
- 819 of 3,026 bybit bars (27.1%) have no exness counterpart and carry ~1/3 the
  volume and ~1/4 the range.
- Basis drifts ~0.4% over 15 months.

Not proven, and deliberately not claimed:

- That a strategy sweep on bybit XAUT reproduces exness's verdicts. Return
  correlation is necessary, not sufficient — a candidate's PF depends on tails
  and on cost, not on average co-movement. **The calibration test is the next
  round's job**: sweep a handful of already-closed candidates (Donchian r88,
  Keltner r91, Connors RSI(2) r204) on weekday-only bybit XAUT and confirm it
  reproduces the known falsifications. A source that fails to reproduce a known
  falsification is not a falsifier.
- Anything about intervals other than 4h. Only 4h was measured.

## Method note, carried forward and now overdue

This is the **fourth** consecutive round without the Dockerised `finance-research`
CLI. Rounds 206-208 each had a defensible reason; this one is a data-fidelity
experiment that had to precede the sweep. The concrete blocker to name so it
stops slipping: **`finance-research-local:latest` does not exist on this machine**
and must be built (`docker build -f docker/Dockerfile-research`) before any
strategy sweep can run. That build is the first action of the next round.
