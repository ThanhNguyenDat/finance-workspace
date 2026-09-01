# Round 304 — REJECTED: the confound is **not** "a fixed few trades". It reaches **−20**, and `exness XAU`'s Target 3 verdict **flips** across six equally-valid window lengths.

Classification: **REJECTED** — my own characterisation from Round 303 fails. Two
bounded Docker sweeps (exactly the 2-container budget), XAU-first. Answers the limit
Round 303 named against itself.

## The limit Round 303 named

Round 303 described the defect as *"an approximately **fixed absolute** disturbance of
a few trades"* (values 5-8 across three routes) and stated the gap: *"I have not tested
how it scales with the **size** of the perturbation."*

The clean way to test that needs no estimate of the true trade rate, which is the very
thing in dispute: a nested cumulative counter **must** be non-decreasing in `--days`,
whatever the market did. So extend the ladder and count violations.

**Registered before running:** if the confound is persistent rather than a one-off at
361 days, **at least one further decrease appears** in the extended ladder
360/361/365/370/380.

## The extended ladder

| `--days` | candles | **`one_target`** | legacy | grid | cost | Alpha 5m |
|---|---|---|---|---|---|---|
| 360 | 69,741 | **374** | 462 | 5,092 | 181 | 197,670 |
| 361 | 70,005 | **367** | 455 | 4,928 | 176 | 198,335 |
| 365 | 70,578 | **392** | 481 | 5,262 | 198 | 199,805 |
| **370** | 71,891 | **391** | 490 | 5,382 | 192 | 203,017 |
| **380** | 73,545 | **371** | 462 | 5,160 | 173 | 207,381 |

Nesting violations:

| counter | sequence | violations |
|---|---|---|
| **`one_target`** | 374 / 367 / 392 / 391 / 371 | **3** — `−7`, `−1`, **`−20`** |
| `legacy_selected_rule` | 462 / 455 / 481 / 490 / 462 | 2 — `−7`, `−28` |
| `legacy_grid` | 5,092 / 4,928 / 5,262 / 5,382 / 5,160 | 2 — `−164`, `−222` |
| `execution_cost` | 181 / 176 / 198 / 192 / 173 | 3 |
| **Alpha 5m** | 197,670 / 198,335 / 199,805 / 203,017 / 207,381 | **0** |
| candles | 69,741 → 73,545 | **0** |

**Three of four steps violate nesting on `one_target`, and the largest violation is
−20 trades**, at the largest step. The weight-free Alpha counter and the candle count
are strictly monotone across all five, as they must be.

**Round 303's "fixed few trades" is rejected.** The scale I have been working with
since Round 301 — about 7 trades — is a *floor observed at small perturbations*, not
the confound's size. On a 380-day window, −20 trades is **5.4%** of the count.

I will not claim a scaling law from this: the violations run −7 at +1 day, −1 at
+5 days and −20 at +10 days, which is not monotone in step size. What is established
is that **the disturbance is at least 20 trades and the biggest one found so far came
from the biggest step**, so treating it as bounded by a handful was wrong.

## The consequence that matters: the Target 3 verdict flips

Six same-day measurements of the **same route at the same config**, differing only in
an arbitrary `--days`:

| `--days` | trades | **rate/week** | margin over 7.0 | verdict |
|---|---|---|---|---|
| 260 | 254 | 6.838 | **−2.3%** | **FAIL** |
| 360 | 374 | 7.272 | +3.9% | pass |
| 361 | 367 | 7.116 | +1.7% | pass |
| 365 | 392 | 7.518 | +7.4% | pass |
| 370 | 391 | 7.397 | +5.7% | pass |
| **380** | **371** | **6.834** | **−2.4%** | **FAIL** |

**Four pass, two fail. The rate spans 6.834 to 7.518 — 9.5% of its mean — and the
7/week bar sits inside that range.** This is no longer a caution about a thin margin;
it is a demonstration that `exness XAU`'s Target 3 verdict is **decided by the window
length the analyst happens to pick**.

Rounds 302 and 303 recorded this route as **undetermined**. That classification is
correct and now rests on direct evidence rather than on an inference from sensitivity.

## What does not change

The margin-versus-sensitivity rule from Round 303 survives, with `exness XAU`'s
sensitivity revised from 5.5% to **9.5%**:

| route | margin over bar | sensitivity | verdict |
|---|---|---|---|
| `binance BTC` | +34.6% | 1.04% | pass — safe |
| `bybit XAUT` | −65.8% | 8.57% | fail — safe |
| `exness XAU` | −2.4% to +7.4% | **9.5%** | **undetermined — demonstrated** |

`binance BTC`'s margin is still 33x its measured sensitivity, so nothing here touches
its pass. Neither route's sensitivity was re-measured with a larger perturbation, and
both should be assumed larger than the one-day figure now that `exness XAU`'s was.

## What is proven, and what is not

Proven:

- `exness XAU` at the deployed config, same day, same endpoint: `one_target` = 391 at
  370 days and 371 at 380 days, against 374 / 367 / 392 at 360 / 361 / 365.
- Three of four steps in the 360-380 ladder decrease; the largest decrease is
  **−20 trades** over a +10-day step.
- `legacy_selected_rule` decreases by 28 over the same step; `legacy_grid` by 222.
- Alpha 5m (197,670 → 207,381) and candles (69,741 → 73,545) are strictly monotone
  across all five windows — zero violations.
- Across six same-day windows the Target 3 rate runs 6.834 to 7.518/week, straddling
  the bar, with **4 passes and 2 fails**.

Not proven, and deliberately not claimed:

- **A scaling law.** The violations are not monotone in step size (−7 / −1 / −20) and
  five points cannot establish a functional form. Only the **lower bound of 20 trades**
  is established.
- That 20 trades is the maximum. A larger perturbation was not tried, and a 180-day
  gap — the scale Rounds 289-299 actually used — remains unmeasured.
- That `exness XAU` fails Target 3. It passes on four of six windows and fails on two.
  **Undetermined** is the verdict, and it is now demonstrated rather than inferred.
- That `binance BTC` or `bybit XAUT` would behave the same under a +10-day
  perturbation. Neither was re-run; their sensitivities are one-day figures and are
  therefore **lower bounds**, not measurements of their worst case.
- That any historical differenced slice is rescued or further condemned beyond what
  Rounds 300-303 already recorded.
