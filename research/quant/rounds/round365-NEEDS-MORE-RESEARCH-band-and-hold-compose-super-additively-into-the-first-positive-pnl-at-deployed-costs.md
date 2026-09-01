# SIGN REFUTED ACROSS WINDOWS (Round 370)

The profitable corner recorded here (band 0.02/0.04, `minimum_hold_decisions` 288)
**flips sign at 900 days**. Measured on `exness XAU` at the same band and hold:

| window | `one_target` PnL | `legacy` control |
|---|---|---|
| 300 (this file) | **+1.17395** | - |
| 500 | **+0.79730** | -1.44608 |
| **900** | **-0.70835** | -2.25984 |

The corner beats the `legacy` control at **every** window, including the one where it
loses money - so the configuration does something real. What fails is the only thing
that made it interesting: **crossing zero**. Its positive PnL is a property of the
recent window, consistent with r241/r244 on this layer, not a property of the
configuration.

This file's measurement at 300 days stands, as does its caution that it was
full-window and in-sample. See
`round370-REJECTED-the-arcs-only-profitable-configuration-flips-sign-at-900-days-so-the-corner-is-a-recent-window-property-not-a-configuration-property.md`.

---

# THE CORNER TRANSFERS — AND THE JOINT OBJECTIVE IS NOW THE WHOLE STORY (Round 366)

The test this file asked for was run. Applied unchanged to two routes it was **never selected
from** (all runs at `candle_count` 143,998): `binance BTC` @500 turns **+0.37527** (200 trades)
and `bybit XAUT` @500 improves **+81.9%** to −0.28493. The corner improves **all three** routes
tested and turns **two** positive — real evidence against "an `exness XAU` window artefact".

**But it destroyed the one route that met the frequency bar**: `binance BTC` went 9.65 → **2.80
trades/week**. And the arc-wide tally is now unambiguous — **six profitable configurations across
four levers, six Target 3 failures**, the best at 4.57/week and the two most profitable under
2/week. See `round366-NEEDS-MORE-RESEARCH-the-profitable-corner-transfers-to-binance-btc-and-every-profitable-configuration-ever-found-fails-target-3.md`.

---

# Round 365 — NEEDS-MORE-RESEARCH: the band and hold levers are **distinct and compose super-additively**. Together — band 0.02/0.04 with hold 288 — `exness XAU` turns **positive: +1.17395** at deployed costs, the first in this arc. It also trades **1.94 per week**, a **3.6x Target 3 miss**, and **cannot be validated on a holdout**.

Classification: **NEEDS-MORE-RESEARCH** — the most consequential number the arc has produced, and
the one that most needs the discipline. Two bounded Docker sweeps (exactly the 2-container
budget), **XAU-first**.

## The question

Both levers work by keeping positions alive longer — a wider band moves the exit barriers out, a
longer hold forbids early reversal. **They might be the same mechanism measured two ways.**

**Pre-registered as a partition:** the band's effect on PnL **per trade**, measured at hold 288.
- **≥ 30%** (at least half of its 62.5% effect at hold 36) → the levers are **distinct** and
  compose;
- **< 30%** → the band's effect largely disappears once the hold is long, so they are
  substantially the **same mechanism**.

## Validity

All five configurations report `candle_count` **57,934** — one window. Round 363's hold-288 point
reproduced **exactly** (108 trades, −0.32723) when re-run this round, which is both a
determinism check and confirmation the window is shared.

## Result — distinct, and the interaction crosses zero

`exness XAU` @300, deployed costs:

| band | hold | trades | trades/week | `one_target` PnL | **PnL/trade** | funding/trade |
|---|---|---|---|---|---|---|
| 0.01/0.02 | 36 | 270 | 6.30 | −1.57256 | −0.005824 | −0.000354 |
| 0.02/0.04 | 36 | 186 | 4.34 | −0.40571 | −0.002181 | −0.000522 |
| 0.01/0.02 | 288 | 108 | 2.52 | −0.32723 | −0.003030 | −0.000542 |
| **0.02/0.04** | **288** | **83** | **1.94** | **+1.17395** | **+0.014144** | −0.000620 |

The band's per-trade effect is **+62.5%** at hold 36 and **+566.8%** at hold 288 — far past the
30% line. **The registered branch fires: the levers are distinct and compose super-additively.**
Read the other way, the hold's effect is +48.0% at the narrow band and **+748.5%** at the wide one.

**And the corner is profitable**: **+1.17395** over 300 days, **+0.014144 per trade**. Funding per
trade is **worse** there (−0.000620 against −0.000354), so this is not cost removal.

The configuration has a coherent description: **hold at least ~24 hours (288 × 5m) and exit at
−2% / +4%** — a swing configuration, against the deployed scalp one. The implied win rate for
+1.41% per trade on a 4%/2% payoff is about **57%**, which is not an implausible number.

## Why this is not a candidate, stated plainly

1. **Target 3 fails by 3.6x.** 1.94 trades/week against a 7.0 bar; Target 3 needs ~300 trades over
   this window and the configuration makes **83**. The single most profitable corner is also the
   least active — the exact trade-off this arc has hit at every lever.
2. **There is no holdout evidence, and there cannot be.**
   `--portfolio-minimum-hold-decisions` conflicts with `--daily-profit-gate`, so **promotion
   condition 1 cannot be met for any configuration involving the hold**. Everything above is
   full-window `one_target`.
3. **The parameters were chosen after seeing the window.** Across Rounds 359-365 I have walked
   roughly four hold values against four band values on this route; a positive corner in a ~16-cell
   search on one window is what overfitting looks like, and I am not going to pretend otherwise.
4. **One window, one route.** Rounds 331, 334 and 341 each found a configuration that looked
   settled and moved with the window; Round 352 showed all holdouts are nested, so even a
   "second window" check is weaker than it sounds.
5. **83 trades is a small sample** for a per-trade mean, and no confidence interval is available
   from this output.

**What would change the picture** is a holdout score for the combined configuration — which needs
a code change — and the same corner surviving on a route or window it was not selected on.

## What is proven, and what is not

Proven:

- All five configurations at `candle_count` 57,934; Round 363's hold-288 point reproduced exactly.
- The 2×2 table above, `exness XAU` @300 at deployed costs.
- Band effect on PnL/trade: +62.5% at hold 36, **+566.8%** at hold 288. Hold effect: +48.0% at the
  narrow band, **+748.5%** at the wide one.
- `band 0.02/0.04 + hold 288` gives **+1.17395** over 300 days on 83 trades, **+0.014144 per
  trade**, with funding per trade **worse** than every other cell.

Not proven, and deliberately not claimed:

- **That this configuration is profitable out of sample.** No holdout score exists for it and none
  can be produced with the current CLI. Full-window PnL from a searched parameter corner is not
  evidence of edge.
- **That it is not overfitting.** A ~16-cell search on one window found one positive corner; that
  is exactly the null hypothesis and nothing here rejects it.
- That the super-additive reading is a mechanism. The interaction is measured, not explained; both
  levers lengthen holds and why their combination crosses zero is unknown.
- That the ~57% implied win rate is real. It is arithmetic from the payoff ratio, not a measured
  win rate — the output carries no win-rate field for `one_target`.
- That it transfers to `binance BTC` or `bybit XAUT`, or to another window. **Untested.**
- Any promotion. Condition 1 is structurally unmeetable here, and the joint objective fails by
  3.6x regardless.
