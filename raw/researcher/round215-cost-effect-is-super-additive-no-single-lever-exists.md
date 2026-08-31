# MECHANISM FOR THE NON-ADDITIVITY (Round 344)

This file's "super-additive, no single lever exists" now has a **mechanism**, and the
conclusion holds for a stronger reason than it was argued on. The cost flags are **not
exogenous**: on `exness XAU` @300, `--fee-bps 0` left the trade count at exactly 42 and dropped
`gross_pnl_before_costs` — a quantity measured *before* costs — by **79%**, and
`--slippage-bps 0` moved the count 42 → 38. Cheaper execution makes more strategies profitable,
which changes the per-kline Alpha weights (round 300), which changes what the Portfolio trades.

So a `--fee-bps` / `--slippage-bps` delta is a **joint** cost-and-decision effect. No run in
this arc supports a per-component cost attribution. See `round344-DATA-ISSUE-the-cost-flags-change-the-decision-stream-so-cost-component-attribution-is-not-identified.md`.

---

# Round 215 — The 2x2 factorial: neither fee nor slippage is the lever. The cost effect is super-additive (+12 observed vs +3 additive), so no realistic execution improvement unlocks anything

Classification: **REJECTED**. The cost-reduction direction opened by Round 213
and re-aimed by Round 214 is falsified by a proper factorial. Two bounded Docker
sweeps completing the design.

## Why this run existed

Round 214 attributed Round 213's 2-vs-14 cost result to slippage — "worth roughly
+10 candidates for 4 bps" — by subtracting non-orthogonal runs, and flagged the
attribution as unmeasured. Round 87 had already recorded the standing lesson that
levers in this system must be tested as a **full factorial**, never assumed
additive. That lesson was not applied in Round 214. It is applied here.

Two missing cells were run, funding held constant at 1.0 bps:

## Result

| candidates clearing all three splits (of 77) | slippage 2 bps | slippage 0 bps |
|---|---|---|
| **fee 5 bps** | **2** (production) | **3** |
| **fee 0 bps** | **4** | **14** |

Main effects measured from the production corner:

| change | effect |
|---|---|
| remove fee only (10 bps round-trip) | **+2** |
| remove slippage only (4 bps round-trip) | **+1** |
| remove both | **+12** |
| *additive prediction from the two separate effects* | *+3* |
| additionally remove funding | **+0** |

**The interaction is the entire result: +12 observed against +3 predicted, a 4x
amplification.**

### ⚠️ Correcting Round 214

Round 214's headline — *"slippage accounts for almost all of the cost effect,
roughly +10 candidates for 4 bps"* — is **wrong**. Slippage alone is worth **+1**.
Fee alone is worth +2, so the ordering was reversed as well. Round 214 derived its
number by subtracting `(0,0,0)` from `(0,2,1)` and assigning the remainder to
slippage; the remainder was not slippage, it was the interaction term it
explicitly declined to measure.

Round 214's correction of Round 213 (maker execution is not the lever) still
stands — the taker→maker step gains one candidate, and this factorial confirms
fee alone is worth only +2 even taken to zero.

## Why the effect is super-additive

The bar is a conjunction: PF > 1 on train **and** validation **and** holdout.
A candidate sitting near the threshold typically clears one or two splits when a
single cost term is removed, and needs the remaining friction gone to clear the
third. Removing one term moves many candidates partway and almost none the whole
way; removing both moves a dozen across simultaneously.

This is not a property of slippage or of fees. It is a property of measuring
against a three-way conjunction near its threshold — the same structure that
Rounds 210 and 211 found to be robust precisely because it is a conjunction.
The robustness and the super-additivity are the same phenomenon seen from two
sides.

Note also the contrast with Round 87, which measured the hold x stop/take
interaction as **sub**-additive (56-62% of the linear prediction). Same system,
opposite sign, on a different axis. There is no default direction to assume —
which is exactly why the factorial has to be run.

## The consequence, and why this is REJECTED

Read the table as an operator rather than a researcher:

- Negotiating fees to **zero** — not achievable — buys **+2** candidates.
- Eliminating slippage entirely — not achievable — buys **+1**.
- Only removing essentially *all* friction reaches 14, and that world does not
  exist.

There is no partial execution improvement that unlocks anything at exness XAU 4h.
A realistic best case — say maker fees and halved slippage — sits between the
+1 and +2 corners, i.e. approximately zero new candidates.

**The cost-reduction direction is therefore closed.** Round 213 opened it on a
real measurement, Round 214 re-aimed it at the wrong term, and this round shows
the target does not exist in a form anyone can act on. The finding that survives
from Round 213 is the diagnostic one, not the prescriptive one: these mechanisms
carry positive gross edge that is smaller than total friction. That remains true
and remains unactionable through execution improvements.

## What is proven, and what is not

Proven:

- The 2x2 factorial at constant funding: 2 / 3 / 4 / 14 for
  (fee 5, slip 2) / (fee 5, slip 0) / (fee 0, slip 2) / (fee 0, slip 0).
- Fee alone +2, slippage alone +1, both +12, additive prediction +3.
- Removing funding from the (0,0) corner adds 0, consistent with Round 213 at the
  production corner.

Not proven, and deliberately not claimed:

- Any mechanism for the super-additivity beyond the threshold-conjunction
  explanation above. That explanation fits the structure of the bar but was not
  tested against an alternative.
- That the same interaction sign holds on BTC, on other intervals, or on other
  sources. Round 87 found the opposite sign on a different axis in the same
  system, so this must not be generalised.
- Anything about real fills. The whole factorial is a model of cost, not a
  measurement of it; Round 214's open question — what real slippage actually is
  on these instruments — is untouched and remains the one honest way to know
  whether the production corner is even the right starting point.
