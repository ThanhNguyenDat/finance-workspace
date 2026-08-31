# Round 223 — The stack does admit candidates (2 of 107 on BTC 4h+1d), it cannot evaluate the program's own deployed swing strategy, and both facts matter

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps. This is a
BTC round by necessity — the calibration question is about the one mechanism the
program validated, and that mechanism lives on BTC.

## Why BTC, and what was tested

Round 222 closed XAU 4h with "zero survivors" but flagged that the finding might
be an artifact of an unfalsifiable filter stack: `grep '^mtf_'` returned 0 across
every run of the series, because MTF candidates need `--higher-timeframe-interval`
and that flag had never been passed. The program's only validated mechanism —
the swing 4h/1d MTF stochastic of Rounds 17/172/189, deployed in production — is
an MTF candidate.

This round runs exness BTC/USD 4h with `--higher-timeframe-interval 1d` over
1,800 days: **107 candidates, 30 of them MTF, 17 stochastic variants**, including
the deployed one.

## Result 1 — the stack is not unfalsifiable

| surviving | filter |
|---|---|
| **107** | all candidates |
| **7** | PF > 1 on all three splits |
| **2** | + >= 30 trades on all three splits (Round 210 floor) |
| **2** | + positive PnL on all three splits (Round 212) |

Round 222's worry is answered: the stack admits things when they are there.

| candidate | trades t/v/h | PF t/v/h | PnL t/v/h | **edge/friction ratio t/v/h** |
|---|---|---|---|---|
| `candle_momentum_rv_regime_filter_10_50_1.3` | 376/152/115 | 1.02/1.39/1.05 | +0.60/+2.78/+0.18 | **1.23 / 3.55 / 1.19** |
| `mtf_candle_momentum_10bps_sma10_trend_filtered` | 193/58/62 | 1.07/1.14/1.08 | +1.42/+0.59/+0.40 | **2.04 / 2.23 / 2.00** |

For scale, the population holdout median ratio on this same run is **0.087**
(n=61). These two are one to two orders of magnitude above their peers, and the
second is stable across all three splits to within 12% — the cross-split
consistency Rounds 210-211 identified as the rare, meaningful signature.

**These are the first candidates in this session to clear every filter the
program has accumulated.**

## Result 2 — the stack cannot evaluate the deployed swing strategy

`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, validated in Rounds 17/172 and
deployed in Round 189:

```
train      n=41  PF=1.37  PnL=+3.10
validation n=18  PF=2.40  PnL=+2.54
holdout    n=19  PF=0.90  PnL=-0.17     -> PF bar: FAIL
```

It fails. But **18 and 19 trades are below Round 210's own 30-trade information
floor**, so by this program's rule those two splits carry no information in
either direction. The correct reading is not "the deployed strategy is refuted"
— it is **"this test has no power to judge it."**

That is not a detail. It exposes a structural tension the program has never
stated:

- the bar requires >= 30 trades on each of three splits, i.e. **90+ trades**;
- Round 207 measured this strategy's live frequency at **~0.28 trades/week**;
- 90 trades at that rate needs roughly **six years** of history;
- exness retention is **five years**.

**The program's evaluation bar cannot, even in principle, evaluate the class of
low-frequency mechanism it most wants to find.** Rounds 218-221 concluded that
slower intervals are where edge survives friction; this round shows the bar
cannot see anything that slow. Those two conclusions are in direct conflict and
the conflict is arithmetic, not opinion.

Note also that both surviving candidates are relatively **high**-frequency
(376/152/115 and 193/58/62 trades). The stack can currently only admit the
mechanisms that trade often enough to be measured — which Rounds 216-217 showed
are the most cost-exposed. The filter and the physics point in opposite
directions.

## Why this is not a PROMOTE

Both survivors are one broker, one instrument, one interval, one window, one
partition. The gate needs more, and the program's own history says exactly which
checks:

1. **Cross-broker.** Round 205 falsified four binance XAU candidates on exness;
   Round 210 calibrated bybit as a falsifier for precisely this. These results
   are exness-only. binance BTC and bybit BTC at 4h+1d are the next runs.
2. **Window sensitivity.** Round 219 measured a 38% swing in the same metric
   between 365d and 1800d windows.
3. **Partition sensitivity.** Round 211: 48% of cells flip their verdict when the
   partition moves.

Until at least the cross-broker check runs, promoting would repeat the Round 67
"zombie strategy" mistake — deploying on evidence that a second source has not
seen.

## What is proven, and what is not

Proven:

- exness BTC 4h+1d, 1,800 days: 107 candidates, 7 pass the PF bar, 2 clear the
  full accumulated stack.
- Those two carry edge/friction ratios of 1.19-3.55 and 2.00-2.23 against a
  population holdout median of 0.087.
- The deployed swing candidate fails the PF bar on this run (holdout PF 0.90) on
  18/19 trades — below the information floor on two splits.
- 90+ trades at 0.28/week needs ~6 years; retention is 5.

Not proven, and deliberately not claimed:

- That either survivor is real. No cross-broker, no second window, no second
  partition. One instrument, one source.
- That the deployed swing strategy is bad. This test cannot judge it; Rounds
  17/172 used binance BTC, this run is exness BTC, and the samples are too thin
  either way.
- That the stack is correctly calibrated in the strict sense. It admits
  candidates, which was the open question; whether it admits the *right* ones
  remains untested against any independently confirmed positive.
