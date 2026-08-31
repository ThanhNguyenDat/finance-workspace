# Round 323 — NEEDS-MORE-RESEARCH: the "unidentified path" is the **cost gate** after all. What varies is not *which* path but **trades lost per rejection — 0.055 to 3.24, a 59x swing with depth**.

Classification: **NEEDS-MORE-RESEARCH** — resolves Round 322's named gap by elimination
and corrects my own framing of it; the reason the conversion rate varies stays open.
**Zero containers, zero SSH**: every number from the six JSON reports Rounds 321-322
already produced.

## The gap Round 322 named

Round 322 found the deployed cost arm trading **4.3% / 21.1% / 43.5%** less than the
zero-cost arm at 360 / 700 / 900 days, while `execution_cost` rejections ran
**181 / 236 / 120** — not monotone — and concluded: *"trades are being lost through more
than the cost gate's explicit rejections, and I have not identified the rest of the
path."*

Six reports were already on disk with every counter in them. This round differences all
of them.

## What the counters show

| | 360d | 700d | 900d |
|---|---|---|---|
| `decision_count`, zero-cost vs deployed | 66,079 / **66,079** | 128,896 / **128,896** | 165,687 / **165,687** |
| `one_target` trades, Δ | −17 | −136 | **−311** |
| guard-free trades, Δ | −10 | −150 | **−389** |
| `execution_cost` rejections (deployed) | 181 | 236 | **120** |
| any other non-zero risk bucket | none | none | none |

Three things follow.

**1. The decision stream is cost-independent.** `decision_count` is **identical** between
the two arms at all three windows. Cost changes nothing about how many decisions are
made — only what happens to them afterwards.

**2. The loss is upstream of the hold guard.** The guard-free
`legacy_selected_rule` loses **more** trades than `one_target` at 700 and 900 days
(−150 against −136, and −389 against −311), so the guard is not what is removing them.

**3. `execution_cost` is the only counter that differs at all.** Every other risk bucket
is zero in both arms, at every window.

## So the path was never missing — my framing was wrong

Cost enters the simulation in exactly two places: the PnL arithmetic (fees and slippage
deducted from each fill, which cannot change a trade *count*) and the **cost gate**.
Under `fixed_notional` sizing the position size does not depend on realised PnL, and the
fractional protective band is set off entry price, so neither is cost-sensitive.

**By elimination, for `one_target` and `legacy_selected_rule` the cost gate is the only
mechanism by which cost can change the trade count.** Round 322's "rest of the path" does
not exist. What I actually found, and mis-described, is this:

| `--days` | guard-free trades lost | rejections | **trades lost per rejection** |
|---|---|---|---|
| 360 | 10 | 181 | **0.055** |
| 700 | 150 | 236 | **0.636** |
| 900 | 389 | 120 | **3.242** |

**The conversion rate rises monotonically with depth — a 59x swing** — while the raw
rejection count does not. One rejection at 360 days costs almost nothing; one at 900 days
costs about three trades.

That is arithmetically consistent with a rejection *deferring* a target change rather
than cancelling one: whether the deferral costs trades depends on whether the change
ever happens later. **But I cannot verify that from these counters** — it would need a
per-decision trace, and I am not proposing it as established.

## A side observation on the hold guard

`trade_reduction_fraction` (the guard's bite) moves between arms: 0.1716 → 0.1905 at
360d and 0.1502 → 0.1642 at 700d — the guard bites **more** under cost — but at 900d it
runs **0.1386 → 0.0839**, biting **less**. A sensible reading is that at depth the cost
gate has already removed the reversals the guard would otherwise have blocked, leaving
it less to do. Recorded as an observation; the interaction was not tested directly.

`legacy_grid` behaves inconsistently as expected: **+388** trades *with* cost at 360d
against −1,520 and −1,572 at 700 and 900. That is exactly the equity-path dependence
Round 299 documented for its compounding rules, and is not a new finding.

## What is proven, and what is not

Proven:

- `decision_count` is identical between the zero-cost and deployed arms at 360, 700 and
  900 days (66,079 / 128,896 / 165,687).
- `execution_cost` is the only non-zero entry in `risk_rejected_counts` in either arm at
  any of the three windows: 181 / 236 / 120 in the deployed arms, none in the zero-cost
  arms.
- Guard-free trade losses of 10 / 150 / 389 against those rejection counts give
  **0.055 / 0.636 / 3.242** trades lost per rejection.
- The guard-free measure loses more trades than `one_target` at 700 and 900 days.
- `trade_reduction_fraction` 0.1716→0.1905, 0.1502→0.1642, 0.1386→0.0839 across the
  three windows.

Not proven, and deliberately not claimed:

- **The cascade mechanism.** "A rejection defers rather than cancels" fits the
  arithmetic; it is not verified, and Round 312 already showed one of my mechanisms
  making a wrong prediction. No per-decision trace was inspected.
- **Why the conversion rate rises with depth.** Three points, one route, and no
  candidate offered — Rounds 279-284 remain the standing reason.
- That the guard/cost-gate interaction at 900 days is causal. One window, one
  observation.
- That this changes any profitability or ratio conclusion. Round 322's measured
  edge-to-cost points (30.1% / 43.7% / 24.3%) stand exactly as recorded; this round
  explains *where* the denominator's trade-selection change comes from, not what it is
  worth.
- Anything about other routes. All six reports are `exness XAU`.
