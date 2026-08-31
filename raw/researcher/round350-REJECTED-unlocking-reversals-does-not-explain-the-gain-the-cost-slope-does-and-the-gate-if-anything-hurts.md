# Round 350 — REJECTED: unlocking reversals does **not** explain Round 349's 31% gain. A blocked-arm cost ladder shows the gain is the **cost slope**, and the gate crossing, if anything, makes things **worse** by ~0.13-0.18. But the design cannot resolve an effect that small.

Classification: **REJECTED** — the natural reading of Round 349 ("unlocking reversals improves
the result") is refuted, and my own framing with it. Two bounded Docker sweeps (exactly the
2-container budget), **XAU-first**.

## Getting around the missing flag

Round 349 could not separate "cheaper execution" from "reversals permitted" because
`--slippage-bps 0` changes both, and the CLI has no `max_total_cost_bps` flag.

There is a way around it that needs no code change. The gate rejects a reversal when
`(fee + slippage) × 2 > 10`. Holding `--fee-bps 5`, the reversal cost crosses the ceiling
between slippage 0.5 and 0:

| slippage | total | reversal cost | gate |
|---|---|---|---|
| 2.0 | 7.0 | 14.0 | blocked |
| 1.0 | 6.0 | 12.0 | blocked |
| 0.5 | 5.5 | 11.0 | blocked |
| **0.0** | **5.0** | **10.0** | **unlocked** |

So three points measure the **pure cost slope with the action space held fixed**, and
extrapolating them to 5.0 bps predicts what the unlocked point *would* have been had it stayed
blocked. The difference is the gate.

**Pre-registered as a partition:** Δ = (actual unlocked PnL) − (blocked-arm linear extrapolation
to 5.0 bps).
- **|Δ| ≥ 0.15** → the gate crossing is a material discontinuity;
- **|Δ| < 0.15** → the cost slope alone explains Round 349's gain.

## Result

`exness XAU` @300, deployed band, hold 36, 55,045 decisions, identical window, `--fee-bps 5`
throughout:

| slippage | total bps | gate | `execution_cost` rejections | `one_target` trades | **`one_target` PnL** | ungated `legacy` PnL |
|---|---|---|---|---|---|---|
| 2.0 | 7.0 | blocked | 102 | 280 | −1.32216 | −1.32799 |
| 1.0 | 6.0 | blocked | 96 | 273 | −1.08032 | −0.75172 |
| 0.5 | 5.5 | blocked | 97 | 272 | −0.90624 | −0.72084 |
| **0.0** | **5.0** | **unlocked** | **3** | 277 | **−0.91662** | −0.83321 |

The rejection counts confirm the design: 102 / 96 / 97 while blocked, **3** once unlocked.

Blocked-arm fit (registered method, three points): slope **−0.27222 PnL per +1 bps**,
predicting **−0.78532** at 5.0 bps.

**Actual unlocked: −0.91662. Δ = −0.13130.** |Δ| = 0.1313 **< 0.15** — the registered branch is
*"the cost slope alone explains it"*.

**And the sign is the real result.** The unlocked point is **worse** than the blocked trend
predicts. Round 349's 31% improvement from slippage 2 → 0 is a **cost** effect; permitting
reversals **subtracts** roughly 0.13 from it rather than adding. The reading that suggested
itself in Round 349 — that production's gate is costing PnL — is refuted: on this evidence the
gate is mildly *protective*.

## The honest caveat: this does not resolve

The verdict is not robust to the extrapolation method, and I registered only one:

| extrapolation | predicted at 5.0 | Δ | verdict |
|---|---|---|---|
| 3-point linear fit **(registered)** | −0.78532 | **−0.13130** | below 0.15 |
| nearest-pair slope (6.0 → 5.5), extended | −0.73216 | **−0.18446** | at/above 0.15 |

The blocked arm's own pairwise slopes differ by **44%** (−0.24184 against −0.34816 per bps), so a
0.5 bps extrapolation carries more uncertainty than the 0.15 threshold I chose.

Worse, the **ungated** ledger — which the gate never touches — moves **−0.11237** across the same
0.5 → 0.0 step, and is itself non-monotone (−1.32799, −0.75172, −0.72084, **−0.83321**). An
effect of ~0.13 cannot be separated from a cost-feedback wobble of ~0.11 on a ledger where no
gate exists.

**So the bound is what stands: the gate crossing is worth roughly −0.13 to −0.18, small relative
to the 0.4056 total move from slippage 2 to 0, and of a sign that does not favour unlocking.**
The exact figure is beyond this design's resolution, and the clean run still needs the
`max_total_cost_bps` flag that does not exist.

## What is proven, and what is not

Proven:

- The four-point ladder above, all at `--fee-bps 5`, same window and configuration.
- Rejection counts 102 / 96 / 97 / 3 confirm the gate is active on the first three and
  effectively inactive on the fourth.
- Blocked-arm 3-point fit: slope −0.27222 per bps, prediction −0.78532 at 5.0 bps, Δ = −0.13130.
- Nearest-pair extrapolation gives −0.73216 and Δ = −0.18446.
- The ungated `legacy_selected_rule` PnL is non-monotone across the same ladder and moves
  −0.11237 over the final step.

Not proven, and deliberately not claimed:

- **That the gate crossing is worth exactly −0.13.** Two defensible extrapolations straddle my
  registered threshold; the honest statement is a **range of roughly −0.13 to −0.18**, not a
  point.
- **That permitting reversals is harmful.** The sign is negative under both extrapolations, but
  the magnitude sits inside the ungated ledger's own wobble over the same step. It is *not
  favourable*; that is weaker than *harmful*.
- **That production's gate protects PnL.** Same reason, and the comparison arm still specifies a
  cost production does not have.
- That the cost slope is linear. Pairwise slopes differ by 44% over 1.5 bps; three points cannot
  establish a functional form.
- Anything about other routes, windows, or the holdout. These are full-window `one_target`
  figures on one route at one window.
- Any promotion. Every point on the ladder loses money.
