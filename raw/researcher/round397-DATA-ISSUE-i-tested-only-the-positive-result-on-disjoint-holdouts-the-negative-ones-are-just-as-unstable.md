# Round 397 — DATA-ISSUE: I applied the disjoint-holdout test **only to the positive result**. The negative ones are just as unstable — `binance BTC` is gross-positive on **two of three** holdouts.

Classification: **DATA-ISSUE** — a defect in my own procedure that invalidates a
characterisation I published two rounds ago. Two containers (the budget),
cleaned up.

## The asymmetry in my own method

Rounds 391 and 392 subjected `exness XAU`'s **positive** gross reading to four
holdouts and found it alternates. Round 390 recorded three routes as
**gross-negative** and one as positive — each on **a single holdout** — and I
built a fleet characterisation on that without testing the negatives the same
way.

**Testing only the result that stands out is a selection asymmetry regardless of
which direction it points.** This round tests a negative one.

## The result

`binance BTC`, three disjoint holdouts, gate path, pinned cutoffs:

| run | holdout | **gross** | net | cost/gross | trades/wk |
|---|---|---|---|---|---|
| H1 | 2026-03-04 → 2026-08-31 | **−0.58685** | −1.77712 | 2.0282 | 7.661 |
| H2 | 2025-09-05 → 2026-03-04 | **+0.82128** | **+0.00025** | 0.9997 | 4.200 |
| H3 | 2025-03-08 → 2025-09-04 | **+0.26947** | −0.15914 | 1.5906 | 4.900 |

**Two of three positive.** Round 390 measured H1 only and recorded the route as
gross-negative.

Side by side:

| route | gross across holdouts | positive |
|---|---|---|
| `exness XAU` | +0.66471, −0.72458, +0.29154, −0.11094 | 2 of 4 |
| `binance BTC` | −0.58685, +0.82128, +0.26947 | **2 of 3** |

**Both routes alternate. Neither is characterised by its single-holdout reading.**

## What this invalidates, and what it does not

**Invalidated:** round 390's fleet table as a description of *routes*. "Three
gross-negative, two indistinguishable from zero, one positive" describes **one
window each**. On the two routes now measured across multiple holdouts, the sign
is unstable on both.

**Not invalidated:** round 391/392's core conclusion. The claim there was that
the positive reading **does not replicate** — and that survives, because
`binance BTC`'s does not replicate either. If anything this strengthens it: sign
instability is the general pattern, not a property of one route.

Also unchanged: nothing is profitable. `binance BTC`'s best net across three
holdouts is **+0.00025** — breakeven, at 4.200 trades/week. That is the second
non-negative net found in this arc, after `exness XAU`'s +0.00095 (r392), and
both occur at frequencies the joint objective rejects.

## A second route on the frequency question

Trades/week: H3 4.900, H2 4.200, **H1 7.661**. The newest holdout is clearly the
busiest, as on gold (r392) — but **not monotone**, since the older H3 exceeds
H2. So the "rises toward the present" trend has directional support on a second
route and **is not the clean monotone sequence gold showed**.

## What is proven, and what is not

Proven:

- The three `binance BTC` holdout rows above, disjoint and pinned.
- Two of three gross readings are positive; round 390 recorded the route as
  gross-negative from H1 alone.
- Best net across the three: +0.00025 at 4.200 trades/week.

Not proven, and deliberately not claimed:

- **That `binance BTC` has edge.** Two of three positive with a mean near zero
  is the same shape as `exness XAU` — instability, not edge.
- That the other four routes alternate too. Untested; that is now a known gap
  rather than an assumption, and it is the same gap I criticised.
- That the frequency trend generalises. Two routes, directionally consistent,
  one monotone and one not.
- That my earlier fleet conclusion was wrong in its *direction*. It was wrong in
  its *confidence*: single-holdout readings do not characterise routes either
  way.

## Named next step

Any future statement about a route's gross sign needs at least three disjoint
holdouts before it is written down. The four untested routes would take two
rounds; whether that is worth doing depends on what the answer would change,
and on the current evidence it would change nothing — every route measured more
than once alternates around zero.
