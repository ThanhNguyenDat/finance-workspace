# Round 392 — REJECTED: gross **alternates sign** across four holdouts. Separately, trade frequency rises **3.2× toward the present** — reproducing an old finding by a method that is actually valid.

Classification: **REJECTED** — the pre-registered criterion fired. Two containers
(the budget), cleaned up.

## The registered question, answered

Round 391 found `exness XAU`'s gross edge reversed on one disjoint holdout, and
named the test: *of four holdouts, 3 or more positive → the positive reading is
the norm; 2 or fewer → it does not replicate.*

| holdout | window | days | **gross** | net | trades/wk |
|---|---|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | 179.7 | **+0.66471** | −0.37734 | 6.232 |
| H2 | 2025-09-04 → 2026-03-04 | 180.8 | **−0.72458** | −1.20812 | 3.020 |
| H3 | 2025-03-07 → 2025-09-04 | 180.2 | **+0.29154** | **+0.00095** | 2.176 |
| H4 | 2024-11-05 → 2025-05-06 | 181.9 | **−0.11094** | −0.37140 | 1.963 |

**Two of four positive. The registered answer is: it does not replicate.**

Gross runs **+ − + −**. Mean **+0.03018** across four, **+0.07722** across the
three that tile perfectly, against a range of **1.39**. That is a quantity
centred on zero with large dispersion — the shape of noise, not of edge.

H1, H2 and H3 tile **exactly**: each begins where the next ends. H4 overlaps H3
by about two months, because `exness XAU`'s history starts 2024-03-14 and a
900-day request at that cutoff loads less than 900 days. Three clean disjoint
holdouts and one partial.

## Two things in the table I did not expect

**H3's net is +0.00095** — the **only non-negative net on any holdout anywhere in
this arc**. It is essentially breakeven, not profit, and it occurs at **2.176
trades/week**, a third of the Target 3 bar. Consistent with everything the arc
has found: the configuration approaches breakeven only where it barely trades.

**Trade frequency rises monotonically toward the present**: 1.963 → 2.176 →
3.020 → **6.232**, a **3.2× increase** from the oldest holdout to the newest.

That matters beyond this round. Rounds 289 and 293 found trade rates "roughly
doubling over eighteen months" — by **nested differencing**, which round 300
invalidated for Portfolio counters because weights refit on every kline. The
finding has now reproduced on **genuinely disjoint holdouts**, a method with none
of that defect. **An invalidated result turns out to have been right, confirmed
by a valid method** — and the magnitude is larger than the original estimate.

## What this settles

The Portfolio-layer search as an edge-finding exercise is finished on the
evidence available. Six routes measured on holdout: three gross-negative, two
indistinguishable from zero, and the one with a real positive reading alternates
sign across four holdouts.

## What is proven, and what is not

Proven:

- The four-holdout table above, all Portfolio-faithful, holdout-restricted,
  pinned cutoffs, deployed configuration with hold 36.
- H1/H2/H3 are mutually disjoint and contiguous; H4 overlaps H3.
- Mean gross +0.03018 (four) and +0.07722 (three disjoint) against a 1.39 range.
- Frequency 1.963 / 2.176 / 3.020 / 6.232 oldest to newest.

Not proven, and deliberately not claimed:

- **That there is no edge.** Four holdouts on one route is four observations,
  and three of them are only disjoint by construction, not independent — they
  share the same fitted history up to each cutoff.
- That the frequency trend has a cause. It reproduces; nothing here explains it,
  and rounds 289–300 exhausted several candidates without finding one.
- That H3's +0.00095 net means anything. It is 0.03% of H1's gross magnitude
  and sits at a frequency the joint objective rejects.
- That the other five routes would alternate the same way. Not tested on
  disjoint holdouts; three are negative on their single holdout already.

## Named next step

Nothing further should be spent searching the Portfolio layer for edge. The two
questions worth a round are: whether the **frequency trend** continues forward
(a re-run in some weeks, not a backtest), and whether the **Alpha ensemble**
produces anything on disjoint holdouts — the same test applied one layer up,
where rounds 373–374 left a scan that survived no conservative test but was
never run against genuinely unseen data.
