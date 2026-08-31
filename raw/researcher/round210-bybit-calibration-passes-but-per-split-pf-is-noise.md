# Round 210 — bybit XAUT passes calibration (0 false promotions), and the same run shows per-split PF at 4h is noise-dominated

Classification: **NO-CHANGE**. Nothing promoted, no defect found. Two bounded
Docker sweeps (the resource cap for the round), one control, one new source.

## Setup

Round 209 accepted bybit XAUT conditionally and named the calibration test: sweep
already-closed candidates and confirm the new source **reproduces known
falsifications**. A source that cannot reproduce a falsification is not a
falsifier.

Both runs used the same engine, interval and calendar window so the only variable
is the price source:

```
finance-research --interval 4h --days 500
  A: --broker bybit  --market-type spot --base-asset XAUT --quote-asset USDT
  B: --broker exness --market-type cfd  --base-asset XAU  --quote-asset USD
```

| source | candles | train / validation / holdout |
|---|---|---|
| bybit XAUT | 2,999 | 1,799 / 600 / 600 |
| exness XAU | 2,191 | 1,315 / 438 / 438 |

The 808-candle difference is the weekend session, matching Round 209's count of
819 no-counterpart bars. **The CLI has no weekday filter**, so Round 209's
"exclude weekend bars" condition could not be met — see the interpretation rule
below.

## Result 1 — calibration PASSES

Nine candidates from three closed directions (Donchian r88, Keltner r91,
Heikin-Ashi r93), profit factor by split:

| candidate | bybit XAUT (t / v / h) | exness XAU (t / v / h) |
|---|---|---|
| `donchian_breakout_20` | 1.61 / 0.86 / 0.96 | 1.24 / 1.10 / 0.39 |
| `donchian_breakout_55` | 1.18 / 0.73 / 0.88 | 0.97 / 0.22 / 0.00 |
| `donchian_breakout_100` | 0.79 / 0.19 / 0.00 | 0.00 / 0.00 / 0.00 |
| `donchian_breakout_200` | 0.00 / 0.00 / 0.00 | 0.00 / 0.00 / 0.00 |
| `keltner_reversion_20_1_5` | 0.77 / 1.39 / 0.61 | 0.51 / 0.62 / 2.20 |
| `keltner_reversion_20_2_0` | 0.65 / 1.83 / 1.08 | 0.98 / 0.22 / 0.78 |
| `keltner_reversion_20_2_5` | 0.55 / 7.75 / 1.15 | 1.44 / 7.38 / 0.00 |
| `heikin_ashi_momentum_1` | 0.72 / 0.77 / 0.53 | 0.88 / 1.03 / 0.58 |
| `heikin_ashi_momentum_3` | 0.82 / 0.62 / 0.86 | 1.17 / 0.70 / 1.03 |

**Candidates clearing PF > 1 on all three splits: none on bybit, none on exness.**
Nine out of nine known-closed candidates stay closed on the new source. Zero
false promotions. bybit XAUT reproduces the program's existing verdicts and is
therefore usable as a falsifier.

## Result 2 — but the per-split numbers disagree, and the disagreement is sample size

The verdicts agree; the numbers behind them do not.

| measure | value |
|---|---|
| cells where the binary "PF > 1?" answer **disagrees** between sources | **11 of 24 (45.8%)** |
| mean relative PF gap, all cells | **45.0%** |
| mean relative PF gap, cells with **>= 30 trades on both** sources | **18.3%** (n=6) |
| mean relative PF gap, cells with **< 30 trades on either** source | **53.8%** (n=18) |
| worst single cell | `keltner_reversion_20_2_0` validation: **1.83 vs 0.22** on 13 and 5 trades |

Two series whose 4h log returns correlate **0.9915** (Round 209) produce per-split
profit factors that differ by 45% on average and by 8x in the worst cell. The gap
is three times larger in small-sample cells than in large-sample ones. That is
the signature of noise, not of a source difference — if the price series were the
cause, the gap would not shrink with trade count.

### What this invalidates

The program has repeatedly recorded "near-miss" leads from a single split
clearing 1.0 at small trade counts. Round 205's
`mtf_stochastic_14_3_30_70_sma10_trend_filtered` was kept as a lead on
18/7/9 trades; Round 114 called MFI "closest bare oscillator". At 5-15 trades per
split, this round measures the cross-source PF disagreement at ~54% — those leads
were reading noise, not edge.

**Practice change (research-only, nothing to implement): a per-split PF from
fewer than ~30 trades carries no usable information. Do not record it as a lead,
do not rank candidates by it, and do not describe a candidate as a near-miss on
that basis.** The all-three-splits-both-brokers bar survives because it is a
conjunction of weak tests, which is exactly why it has held up.

## Result 3 — weekend drag is real but did not bias the verdicts

Round 209's unmet condition, quantified on the full bybit 4h series:

| | share |
|---|---|
| Sat/Sun bars | **28.6%** of bars (864 of 3,026) |
| their share of total intrabar range | **12.3%** |
| their share of total abs(log close/open) | 11.0% |
| opportunity-to-cost ratio | **0.43x** (1.0 = neutral) |
| median 4h range, weekday vs Sat/Sun | 0.642% vs 0.190% |

A per-bar strategy pays 28.6% of its cost budget on bars carrying 12.3% of the
movement. The correct interpretation rule while no weekday filter exists:

- a candidate **failing** on full-series bybit is **not** a clean falsification —
  weekend drag contributes;
- a candidate **passing** on full-series bybit is a **stronger** result than the
  exness equivalent, because it passed while carrying the drag.

In this round the rule did not bite: bybit's PFs are not systematically lower
than exness's — in several cells they are higher — which is further evidence that
noise, not weekend drag, dominates at this sample size.

## What is proven, and what is not

Proven:

- 9 of 9 closed candidates remain closed on bybit XAUT; no candidate clears PF>1
  on all three splits on either source.
- Per-split PF disagrees on the >1 question in 11 of 24 cells; mean relative gap
  45.0%, falling to 18.3% when both sources have >= 30 trades and rising to 53.8%
  below that.
- Weekend bars are 28.6% of bybit bars and 12.3% of its range (0.43x).

Not proven, and deliberately not claimed:

- That bybit XAUT would reproduce a *promotion*. Calibration tested only
  negatives, because the program has no positive at 4h XAU to test against. A
  source that correctly rejects nine losers has not yet been shown to correctly
  accept a winner.
- Anything about the weekday-only variant of this sweep. It could not be run:
  `finance-research` has no session filter, and adding one is a code change this
  round is not proposing.
- Anything at intervals other than 4h, or windows other than these 500 days.

## Method note closed

Round 209 named the blocker: `finance-research-local:latest` did not exist. It
was built this round from `docker/Dockerfile-research` and both sweeps ran capped
at `--cpus=2 --memory=4g`, two containers total, each `--rm`. The read-only SSH
tunnel was opened for the runs and closed at the end of the round.
