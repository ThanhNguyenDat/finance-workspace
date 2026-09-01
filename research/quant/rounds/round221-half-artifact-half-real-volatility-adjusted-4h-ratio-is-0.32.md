# Round 221 — Charging the recent era its volatility-implied friction halves the advantage but does not erase it: the 4h ratio is ~0.32, not 0.66

Classification: **NO-CHANGE**. One bounded Docker sweep. Resolves the attribution
Round 220 raised and explicitly declined to make.

## The question Round 220 left

Round 220 measured that gold's 4h volatility is **2.07x** higher in the recent
holdout segment than in the train era, while modelled friction moved **+3%**, and
concluded the direction of the modelling error was one-sided — but refused to say
how much of the time gradient was artifact, because normalising by volatility
against a negative train base gives unreliable arithmetic.

There is a cleaner way that avoids ratio-of-ratios entirely: **charge the recent
segment the friction its volatility implies, and compare it against the old era
charged normally.**

## Design

One run at friction scaled by the measured 2.07x
(`--fee-bps 10.35 --slippage-bps 4.14 --funding-rate-bps 2.07`), against the saved
1x run and the saved zero-cost run.

The scaling applies to the whole window, so train and validation in that run are
*over*-charged and are not used. The pairing that answers the question is:

- **train from the 1x run** — the low-volatility era, charged its own friction;
- **holdout from the 2.07x run** — the high-volatility era, charged its own.

Sanity check that the flags did what was intended: measured friction per trade
went 0.00713 → 0.01476, exactly 2.07x, and edge per trade is identical in both
(the zero-cost reference is unchanged).

## Result

| | ratio |
|---|---|
| train @ 1x friction (low-vol era, correctly charged) | **−0.029** |
| **holdout @ 2.07x friction (high-vol era, vol-adjusted)** | **+0.318** |
| holdout @ 1x friction — the Round 218/219 headline | +0.659 |

Volatility-adjusting the recent segment **halves** its ratio, 0.659 → 0.318. It
does **not** erase the gradient: +0.318 still comfortably beats the old era's
−0.029.

**So the time gradient is roughly half artifact and half real.** Rounds 218-219
overstated it by about a factor of two; Round 220's suspicion that it might be
entirely an artifact is also wrong.

Also worth recording: at doubled friction the pass count falls only from 2/77 to
1/77 — one candidate survives even under the harsher charging.

## Where this leaves the number, after five rounds of correction

| round | claim about the 4h gap | status |
|---|---|---|
| 218 | ~1.5x (ratio 0.659) | holdout-only, overstated |
| 219 | range −0.03 to +0.66 across splits | correct but wide |
| 220 | possibly all volatility artifact | too pessimistic |
| **221** | **ratio ~0.32 under linear friction scaling; ~3x gap** | current best |

The honest statement is a bounded range rather than a point: the true ratio lies
between **0.32** (friction scales linearly with volatility) and **0.659**
(friction does not scale at all). Both bounds are assumptions about
microstructure, and the conservative end is the one to plan against. Either way
the recent era is genuinely better than the old one, and neither end reaches
break-even.

## What is proven, and what is not

Proven:

- Friction per trade scales exactly as commanded: 0.00713 → 0.01476 (2.07x).
- Holdout ratio at volatility-adjusted friction is +0.318, against +0.659 at flat
  friction and −0.029 for the train era at its own friction.
- Pass count at 4h falls from 2/77 to 1/77 when friction is doubled.

Not proven, and deliberately not claimed:

- That friction scales linearly with volatility. That is the assumption this
  round tests *under*, not a fact — real spread scaling may be sub- or
  super-linear, which is why the answer is reported as a range with linear
  scaling as one bound.
- That the train-era friction is correctly 1x. It is the model's default; the
  early period may itself be mischarged, which would move the baseline.
- Any escape from the standing limitation: this system has never produced a real
  fill (production runs simulated `paper-*` ledgers), so every friction number
  here remains a model. Measuring real spread by volatility regime would settle
  the range, and cannot be done from inside this system.
