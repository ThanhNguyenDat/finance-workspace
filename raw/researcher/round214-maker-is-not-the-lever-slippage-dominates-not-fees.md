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

# ⚠️ CORRECTION (Round 215)

The claim that **slippage accounts for almost all of the cost effect (~+10 for
4 bps)** is **wrong**. It was derived by subtracting non-orthogonal runs. Round 215
ran the missing 2x2 cells: slippage alone is worth **+1**, fee alone **+2**, both
together **+12** against an additive prediction of +3. The remainder this file
assigned to slippage was the **interaction term** it declined to measure.
This file's other conclusion — maker execution is not the lever — still stands.
See `round215-cost-effect-is-super-additive-no-single-lever-exists.md`.

---

# Round 214 — Maker execution is not the lever: dropping taker→maker fees gains one candidate, while slippage accounts for almost all of the cost effect

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps varying only
`--fee-bps`, differenced against saved runs.

## What Round 213 proposed, and why it needed testing

Round 213 measured 2/77 candidates clearing the bar at production cost against
14/77 at zero cost, and proposed maker execution as the first lever: *"more than
half the round-trip cost is the taker premium"* (`fee_bps` 5.0 vs
`maker_fee_bps` 2.0).

That arithmetic is right and the conclusion drawn from it is wrong. The research
CLI exposes no `--maker-fee-bps` or `--liquidity-role` flag, but it does expose
`--fee-bps`, and for a taker-role ledger setting it to 2.0 is exactly the maker
fee. Holding **slippage and funding constant**, the fee axis alone:

| `--fee-bps` | candidates clearing all three splits (of 77) |
|---|---|
| 5 (taker, production) | **2** |
| 2 (maker fee) | **3** |
| 0 (no fee at all) | **4** |

Removing the **entire** fee — 10 bps of round-trip cost, since it is charged on
both entry and exit — moves the count from 2 to 4. The taker→maker step gains
exactly **one** candidate:

```
sma200_trend_filtered_rsi_2_10_90   5bps 0.99/1.56/3.20 -> 2bps 1.05/1.66/3.31   (48 train trades)
```

and it gains it by moving a train split from 0.99 to 1.05. That is a candidate
sitting on the threshold, not a candidate unlocked.

**Maker execution is not the lever.** Round 213's suggestion is withdrawn on its
own evidence.

## Where the cost effect actually lives

Combining this round's fee curve with the two saved runs isolates the terms:

| configuration | fee | slippage | funding | pass |
|---|---|---|---|---|
| production | 5 | 2 | 1 | **2** |
| fee removed | 0 | 2 | 1 | **4** |
| funding removed (Round 213) | 5 | 2 | 0 | **2** |
| all costs removed (Round 213) | 0 | 0 | 0 | **14** |

- **Funding: worth 0 candidates.** Round 213 established this directly — no
  verdict changes when funding is zeroed, because the bar reads PF and PF never
  saw funding.
- **Fee: worth +2 candidates** for 10 bps of round-trip cost.
- **Slippage: worth roughly +10 candidates** for 4 bps of round-trip cost, by
  subtraction (0/0/0 gives 14; 0/2/1 gives 4; funding contributes nothing).

So the smallest of the three cost terms carries almost the entire effect, and the
largest carries very little.

### The likely mechanism, explicitly unverified

Fee is a pure subtraction from a trade's result. Slippage is applied to the
execution **price** (`close_position` shifts the exit price by
`slippage_bps/10_000` against the position side), so it moves the levels at which
protective stops and targets trigger. That makes it path-dependent: it does not
merely shave the result, it can change which trades happen and how they end.

That would explain a disproportionate impact per basis point. **This round did
not test it** — confirming it needs a run that varies slippage while holding
protective behaviour fixed, which the current flags cannot express cleanly.

## The consequence that matters most

Every conclusion this program has drawn rests on `--slippage-bps 2`, a default
nobody has ever justified against measured fills. This round shows the pass count
is roughly **five times more sensitive per basis point** to that unexamined
default than to the fee, which is a real, contractual, known number.

That reframes the research agenda. The productive questions are no longer about
fee tiers:

1. **What is the real slippage** on these instruments at these sizes? Until that
   is measured, the 2 bps default silently determines the outcome of every sweep.
2. **Reduce slippage exposure** rather than fee exposure: fewer and larger trades,
   less aggressive entries, resting orders. Trade count drives both cost terms,
   but it drives the path-dependent one harder.
3. **Report a break-even cost per candidate** instead of a single pass/fail, so a
   candidate that dies at 2 bps and one that dies at 8 bps stop looking identical.

## What is proven, and what is not

Proven:

- Fee axis alone, slippage and funding held constant: 2 → 3 → 4 candidates clear
  the bar at 5 → 2 → 0 bps.
- The taker→maker step gains exactly one candidate, by moving a train split from
  0.99 to 1.05 on 48 trades.
- Funding contributes 0 verdict changes (Round 213), fee contributes +2, and the
  remaining +10 of Round 213's zero-cost result is attributable to slippage.

Not proven, and deliberately not claimed:

- The path-dependence mechanism. It is the plausible explanation for slippage
  outweighing a larger fee, and it was not tested.
- That the +10 attribution is exact. It is a subtraction across runs that are not
  fully orthogonal; no interaction term was measured.
- That real maker fills are achievable. The question is now moot for this
  instrument — even granted perfectly, the maker fee buys one threshold-grazing
  candidate.
- Anything outside exness XAU 4h on the 1,800-day window.
