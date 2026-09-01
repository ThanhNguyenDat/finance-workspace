# THE HOLD LEVER IS NOT DEAD — IT WAS BEING TESTED AT THE WRONG BAND (Round 365)

This file closed the hold direction because its endpoint looked like *no activity, not profit* —
measured at the **deployed** band. At the **wide** band (0.02/0.04) the same hold step goes
**+748.5%** on PnL per trade and turns positive: **+1.17395** at hold 288 (83 trades,
**+0.014144** per trade), against −0.32723 at the deployed band.

The closure's *reasoning* stands for the deployed band, and the joint-objective problem is worse
in the profitable corner (**1.94 trades/week**, a 3.6x Target 3 miss). What was wrong was testing
one lever with the other pinned at its deployed value. See `round365-NEEDS-MORE-RESEARCH-band-and-hold-compose-super-additively-into-the-first-positive-pnl-at-deployed-costs.md`.

---

# THE SAME INSTRUMENT, APPLIED TO THE BAND (Round 364)

This file's technique — net PnL per trade plus `funding_paid` per trade to separate "fewer trades"
from "better trades" — was applied to the protective band and produced the **opposite** profile to
the hold ladder. At nearly identical trade reduction:

| lever | Δ trades | Δ PnL/trade | dominated by |
|---|---|---|---|
| hold 72 → 144 (this file) | −28.4% | **+2.7%** | count |
| band 0.01 → 0.02 (round 364) | −31.1% | **+62.6%** | **quality** |

One caveat carried forward: `legacy_selected_rule` is a free drift control only for
Portfolio-construction parameters. **The band changes the ungated ledger too** (345 → 214 trades),
so a band comparison has no such control and must rely on `candle_count` alone.
See `round364-REJECTED-per-trade-economics-are-not-constant-across-band-settings-the-wide-band-trades-62-percent-better.md`.

---

# Round 363 — REJECTED as a candidate: the hold lever improves **both** trade quality (**+48%** per trade) and trade count (**−60%**), shrinking the loss **79%** from hold 36 to 288 — and its trajectory is toward **no activity, not profit**. Target 3 is destroyed at every step: **6.30 → 2.52 per week**.

Classification: **REJECTED** — the lever is real and well characterised, and it is not a
promotable direction. My own mid-round expectation was refuted along the way. Two bounded Docker
sweeps (exactly the 2-container budget), **XAU-first**.

## Two questions, one registered

Round 362 left the ladder untested past 144 and could not say whether the gain was added edge or
removed cost.

**Pre-registered as a partition** on the decomposition: let Q = net PnL **per trade**. If the gain
were pure trade removal at constant quality, Q would be flat.
- **|ΔQ| / |Q₃₆| ≥ 5%** between hold 36 and 144 → the surviving trades differ in quality;
- **< 5%** → consistent with pure removal.

The ladder extension (144 vs 288, same window, both arms launched together) rode along under the
usual validity gate.

## Validity gate — passed

`candle_count` **57,934** in both arms; `legacy_selected_rule` **345 trades / −1.633800** in both,
as required of a guard-free ledger.

## Result — quality changes, and the ladder does not stop

`exness XAU` @300:

| hold | trades | trades/week | `one_target` PnL | **PnL/trade** | Δ trades | Δ PnL/trade |
|---|---|---|---|---|---|---|
| 36 (deployed) | 270 | 6.30 | −1.57256 | **−0.005824** | — | — |
| 72 | 229 | 5.34 | −1.00705 | −0.004398 | −15.2% | **+24.5%** |
| 144 | 164 | 3.83 | −0.70183 | −0.004279 | −28.4% | +2.7% |
| **288** | **108** | **2.52** | **−0.32723** | **−0.003030** | −34.1% | **+29.2%** |

**Q(36) → Q(144) is +26.5%, well past the 5% line — the registered branch fires: the surviving
trades are genuinely better, not merely fewer.**

**The funding evidence sharpens it.** Funding cost **per trade** rises with hold — −0.000354 at
36 against **−0.000409** at 144, 15.5% worse — exactly as longer holds should. So per-trade
**cost went up while per-trade net improved 26.5%**, which means per-trade **gross** improved by
more than the net figure shows. This is the first mechanism in this arc that visibly touches the
**edge** rather than the cost.

**And my mid-round reading was wrong.** After seeing 72 → 144 move quality only **+2.7%**, I
expected everything past 72 to be pure trade removal. The 288 point refutes that: quality jumps
another **+29.2%**. The per-trade series is **lumpy, not monotone in step size**, and I am
recording that against my own inference.

## Why it is still not a candidate

Cumulatively from hold 36 to 288: PnL improves **79.2%**, trades fall **60.0%**, frequency goes
**6.30 → 2.52 per week**.

- **It never turns positive.** Per-trade loss is **−0.003030 at the deepest point tested** —
  clearly negative, with no sign of crossing zero. The loss shrinks *mostly because there are
  fewer trades*: magnitude falls 48% per trade while count falls 60%.
- **Target 3 is destroyed.** `exness XAU` already failed at hold 36 (6.30/week against 7.0); at
  288 it is **2.52/week, a 2.8x miss**. Every step buys PnL with frequency the route cannot
  spare.
- **The endpoint is no activity.** Extending the hold indefinitely drives trades toward zero and
  PnL toward zero from below. That is arithmetic, not a strategy.
- **`binance BTC` — the one route that kept Target 3 at hold 72 — saturates** (Round 360: 3.5% at
  the same step). So neither route offers a path: XAU keeps improving but cannot trade, BTC can
  trade but stops improving, and its gross is negative (Round 342).
- **It remains unpromotable regardless**: `--portfolio-minimum-hold-decisions` conflicts with
  `--daily-profit-gate`, so no holdout score exists and promotion condition 1 cannot be met.

**The direction is closed as a candidate.** What survives is the mechanism: the guard improves
trade quality, which is worth remembering the next time something looks like a pure frequency
knob.

## What is proven, and what is not

Proven:

- Validity gate: 57,934 candles and identical `legacy` (345 / −1.633800) in both arms.
- The four-point ladder above, `exness XAU` @300 at the deployed band.
- Q(36) = −0.005824 against Q(144) = −0.004279, a 26.5% relative improvement; Q(288) = −0.003030,
  48.0% better than Q(36).
- Funding per trade −0.000354 (hold 36) against −0.000409 (hold 144).
- Cumulative 36 → 288: PnL +79.2%, trades −60.0%, frequency 6.30 → 2.52 per week.

Not proven, and deliberately not claimed:

- **That per-trade loss never crosses zero.** Four points, all clearly negative, with no fitted
  trend. What is established is that **nothing in the tested range suggests it does**.
- That the quality improvement is edge rather than some other cost component. Funding is the only
  cost that provably varies with hold and it moves **against** the improvement; fee and slippage
  per trade are not separately observable, so the argument is directional, not a decomposition.
- That the lumpiness is structural. Three steps, one route, one window — it may be noise, and
  Round 351 established the replay is deterministic, so "noise" here means input sensitivity, not
  randomness.
- That `binance BTC`'s saturation and XAU's continuation share a cause. Two routes, no mechanism.
- Any promotion. The blocker is unchanged and structural.
