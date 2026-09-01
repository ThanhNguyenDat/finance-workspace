# THE PROFITABLE WINDOW IS STILL A DEPLOYED-COST RESULT (Round 348)

Unlike rounds 344-345, this file's profitable configuration (`protective: none` @300, net
**+0.4069**) was run at **deployed costs**, so it is *not* explained by the 10 bps
execution-cost gate crossing that explains those rounds. Its refutation stands on its own
ground: the same change at 900 days is **87% worse** than the deployed band, and it misses
Target 3 by 4.9x.

Context worth carrying: every *other* profitable number in this arc (round 344's +0.1315, round
345's +0.1442) came from specifying costs below production's, which unlocks reversals. See
`round348-DATA-ISSUE-the-cost-flags-move-reversals-across-a-10bps-gate-which-explains-rounds-344-345-and-346.md`.

---

# Round 346 — REJECTED: removing the protective band is **profitable at 300 days** (Sharpe +3.05) and **worse than deployed at 900 days** — refuted inside the same round. And the audit's gap-fill optimism is now **quantified: 5.08% of session boundaries, bounded at ~2x the stop.**

Classification: **REJECTED** — the candidate this round raised is refuted by its own second
window. Two bounded Docker sweeps (exactly the 2-container budget) plus one narrow read-only
Timescale query. **XAU-first.**

## Part 1 — quantifying the audit's L1

The correctness audit recorded **L1 (P2)**: `try_close_at_protective_level`
(`trading_modes.rs:2143-2161`) fills at *exactly* the stop or take price whenever the bar's
low/high crosses it, with **no gap modelling** — and `exness XAU`, the one route with a positive
gross edge, closes every weekend. Its checklist asked for the frequency.

**Pre-registered as a partition:** let **G** = share of session-boundary gaps on `exness XAU`
whose magnitude exceeds the deployed **1% stop**.
- **G ≥ 10%** → gap-through fills are material; L1 stays **P2**;
- **G < 10%** → they are largely theoretical on this route; L1 **de-escalates to P3**.

Read-only Timescale, `exness XAU` 5m, since 2024-09-01, gap = `|open_t − close_{t−1}| /
close_{t−1}`, split by whether the bar spacing exceeds 2 hours:

| kind | n | mean | max | ≥0.5% | **≥1.0% (stop)** | ≥2.0% (take) |
|---|---|---|---|---|---|---|
| **session boundary** | 118 | 0.2565% | **2.0030%** | 17 (14.4%) | **6 (5.08%)** | 1 (0.85%) |
| intraday sequential | 140,901 | 0.0016% | 1.2958% | 5 (0.004%) | **1 (0.0007%)** | 0 |

**G = 6/118 = 5.08% — under the line. L1 de-escalates to P3.**

Two supporting facts make the de-escalation defensible rather than convenient:

- **Within a session the exact-stop fill is essentially exact**: one bar in 140,901 gaps past
  1%. The optimism is confined to session boundaries, which is where the audit predicted it.
- **The magnitude is bounded.** The worst session-boundary gap in two years is **2.0030%**
  against a 1% stop — at most about **2x** the modelled loss, on roughly **6 events in two
  years** (~118 boundaries, ~one per week).

**But the join is not available.** I measured the *market's* gap distribution, not whether the
Portfolio was actually holding a position across any of those six boundaries. Audit item **L4**
— no per-trade audit trail is serialized — makes that join impossible without a code change. So
the honest statement is: **the market-side exposure is small and bounded; whether any measured
trade was affected is not determinable with current tooling.**

## Part 2 — the candidate this raised, and its refutation

`protective: none` removes the stop/take path entirely, so the gap-fill optimism is **absent by
construction**. Two windows, `exness XAU`, deployed costs:

| window | protective | trades | tr/wk | gross | cost | **net** | Sharpe | Sortino | pos-day | streak |
|---|---|---|---|---|---|---|---|---|---|---|
| **300** | fractional 0.01/0.02 | 42 | 5.05 | +0.3391 | 0.3845 | −0.0454 | −0.249 | −0.374 | 0.373 | **3** |
| **300** | **none** | 12 | **1.44** | **+0.5001** | **0.0932** | **+0.4069** | **+3.046** | **+10.18** | 0.451 | 5 |
| **900** | fractional 0.01/0.02 | 174 | 6.85 | +0.7820 | 1.1929 | −0.4110 | −0.860 | −1.177 | 0.404 | 5 |
| **900** | **none** | 104 | 4.10 | **−0.0287** | 0.7389 | **−0.7675** | **−1.361** | −1.661 | 0.391 | 5 |

At **300 days** removing the band is dramatically profitable — net **+0.4069**, Sharpe
**+3.05**, Sortino **+10.18**, cost÷gross **0.186** — and unlike Round 344's zero-slippage
counterfactual this is an **achievable configuration**.

At **900 days** the same change turns gross **negative** (−0.0287, from +0.7820) and leaves net
**−0.7675 against the deployed −0.4110** — it is **87% worse than the band it replaced**.

**The candidate is refuted inside the round that raised it.** This is the same window fragility
as Rounds 331, 334 and 341, on a much larger lever, and Round 345's finding that this replay
amplifies a 1.4% input perturbation into a 15% output change applies with far more force to a
perturbation this large.

## And it fails the joint objective even where it wins

At its good window the no-band configuration trades **1.44 per week** — a **4.9x** miss on the
7/week Target 3 bar, worse than any band ever tested — with a **worse** negative-day streak than
deployed (5 against 3) and a positive-day ratio of 0.451 against the 0.55 requirement. Reading
Target 1 alone would call this a large win; reading all three, it is not a candidate.

The route also remains **gate-ineligible at both windows** (seven interval-continuity checks,
Rounds 335-336), so none of these numbers is a gate verdict.

## What is proven, and what is not

Proven:

- `exness XAU` 5m session-boundary gaps since 2024-09-01: n=118, mean 0.2565%, max 2.0030%,
  6 at or above 1%, 1 at or above 2%; intraday n=140,901, mean 0.0016%, max 1.2958%, 1 at or
  above 1%.
- `exness XAU` @300 `protective: none` → 12 trades / 1.444 per week / gross +0.50012 / cost
  0.09322 / net **+0.40691** / Sharpe +3.0460 / Sortino +10.1833 / streak 5.
- `exness XAU` @900 `protective: none` → 104 trades / 4.097 per week / gross **−0.02867** / cost
  0.73888 / net **−0.76754** / Sharpe −1.3613 / streak 5.
- Both no-band runs carry `protective: {"kind": "none"}` in `simulation_config`.

Not proven, and deliberately not claimed:

- **That the no-band runs isolate the gap-fill optimism.** They remove the stop path entirely,
  which changes the *strategy*, not just the fill model. They give **no** estimate of how much
  the optimism inflated the banded results, and I am not offering one.
- **That any measured trade was affected by a gap-through fill.** The market exposure is
  measured; the join to actual positions is blocked by audit item L4.
- That `protective: none` is bad, or good. It is **profitable at one window and clearly worse at
  another**, which is exactly what the arc's window-fragility findings predict — and neither
  window is a gate verdict on this route.
- That the 2-year gap distribution transfers to another route or period. `exness XAU` only;
  crypto routes have no session boundaries at all.
- Any promotion. The profitable configuration misses Target 3 by 4.9x, fails positive-day ratio,
  worsens the streak, and does not replicate on the second window measured.
