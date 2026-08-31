# Round 222 — Applying the full accumulated rule stack to 4h leaves zero candidates, and the last survivor dies on three independent grounds

Classification: **REJECTED**. No containers used — the question was answerable
from saved runs, and the candidate under test was already disqualified before any
cross-broker run could matter.

## Identifying the survivor Round 221 counted but did not name

Round 221 recorded that one candidate of 77 still passes at volatility-adjusted
friction. It is **`ichimoku_cloud_9_26_52_26`**.

| candidate | split | trades | PF @1x | PnL @1x | PF @2.07x | PnL @2.07x |
|---|---|---|---|---|---|---|
| `ema_crossover_12_26` | train | 148 | 1.01 | −0.10 | **0.82** | −1.37 |
| | validation | 45 | 1.05 | −0.05 | 0.87 | −0.54 |
| | holdout | 40 | 1.42 | +0.79 | 1.25 | +0.40 |
| `ichimoku_cloud_9_26_52_26` | train | 32 | 1.18 | +0.60 | 1.05 | +0.63 |
| | validation | **10** | 1.97 | +0.31 | 1.78 | **−0.07** |
| | holdout | **10** | 4.15 | +1.67 | 3.83 | +1.47 |

## The funnel

Each filter below comes from a measured finding of Rounds 210-221, not from a
wish to reject:

| surviving | filter |
|---|---|
| **77** | all candidates swept (exness XAU 4h, 1,800 days) |
| **2** | PF > 1 on all three splits — the program's standing bar, friction 1x |
| **1** | + survives volatility-adjusted friction 2.07x (Round 220/221) |
| **0** | + >= 30 trades on all three splits (Round 210's information floor) |
| **0** | + positive PnL on all three splits (Round 212: PF excludes funding) |

**The stack admits nothing.**

Where each survivor dies, precisely:

- **`ema_crossover_12_26`** — fails the PF bar once friction is volatility-
  adjusted (train 1.01 → 0.82), and carries negative PnL on two of three splits
  there. Round 212 already rejected it; this is an independent second cause.
- **`ichimoku_cloud_9_26_52_26`** — **10 trades on validation and 10 on holdout**,
  below Round 210's 30-trade floor on two of three splits, so its headline 1.97
  and 4.15 carry no usable information. It also shows **PF 1.78 with PnL −0.07**
  on validation at adjusted friction — the Round 212 defect surfacing in the one
  candidate that appeared to survive. And it was already closed at Round 108.

Three independent grounds, any one of which is sufficient.

## Why no container was spent

The obvious next step would be a bybit XAUT cross-broker check, which Round 210
calibrated for exactly this purpose. It was not run: a candidate with 10 trades
on two splits is disqualified before cross-broker agreement could mean anything,
and confirming a dead candidate on a second source would be compute spent to
reach a conclusion already reached. Recorded so the omission reads as a decision
rather than an oversight.

## The calibration question this raises, honestly

A filter stack that admits nothing is only informative if it would admit
something real. This one has never been tested against a known positive.

The natural test is the program's single historically validated mechanism — the
swing 4h/1d MTF stochastic of Rounds 17/172/189. **It is not in this sweep**:
`grep -c '^mtf_'` over the output returns 0, because MTF candidates require
`--higher-timeframe-interval` and that flag was not passed in any run of this
series. So the stack has been applied only to single-timeframe candidates and has
never had the chance to admit the one thing this program believes is real.

That is the same shape of gap Round 210 recorded for the bybit calibration —
tested only against negatives — and it is now the more important one, because the
stack is being used to close a direction.

**Until the stack is shown to admit the swing 4h/1d candidate, "zero survivors"
should be read as "zero among single-timeframe candidates", not as "nothing works
at 4h".** That is a materially weaker claim than the funnel alone suggests, and
it is the honest one.

## What is proven, and what is not

Proven:

- The 2.07x-friction survivor is `ichimoku_cloud_9_26_52_26`, with 32/10/10
  trades and validation PnL −0.07 against PF 1.78.
- `ema_crossover_12_26` fails the PF bar at adjusted friction (train 0.82).
- The full stack admits 0 of 77 single-timeframe candidates at 4h/1,800 days.
- No MTF candidate appears in any run of this series.

Not proven, and deliberately not claimed:

- That nothing works at 4h. The stack has not been run over MTF candidates, which
  is where the program's only validated mechanism lives.
- That the stack is correctly calibrated. It has admitted nothing so far and has
  never been shown to admit a known positive — running it over the swing 4h/1d
  family with `--higher-timeframe-interval` is the test, and is the natural next
  round.
- Anything about instruments other than exness XAU.
