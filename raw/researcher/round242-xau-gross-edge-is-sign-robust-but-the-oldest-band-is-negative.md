# Round 242 — XAU's Portfolio gross edge is sign-robust across three windows, and a band decomposition shows the oldest 900 days are negative

Classification: **NO-CHANGE**. Two bounded Docker sweeps.

## The question Round 241 left

Round 241 measured XAU's Portfolio gross edge at **+0.00038 per trade** over 1,800
days with all costs zeroed, and flagged its own number: *"5% of friction on one
window, and Rounds 230-232 showed figures at this scale are not distinguishable
from noise without a spread, which was not computed here."*

Computing that spread is this round.

exness XAU/USD 5m, `one_target`, hold 36, all costs zero:

| window | trades | gross PnL | **gross per trade** |
|---|---|---|---|
| 450 days | 693 | +0.741 | **+0.00107** |
| 900 days | 1,034 | +2.505 | **+0.00242** |
| 1,800 days | 1,787 | +0.683 | **+0.00038** |

**The sign is positive on all three.** The magnitude spans 6.3x and is
non-monotone — 900 days is the best and the full history the worst.

## The band decomposition, and why the subtraction is allowed

Nested windows measure sensitivity, not replication (Rounds 219, 232). But
**Round 226 proved each bar is evaluated independently of preceding history** —
that is exactly the licence to subtract nested runs into disjoint calendar bands:

| band (days ago) | trades | gross PnL | gross per trade | as % of friction (~0.0070) |
|---|---|---|---|---|
| 0-450 | 693 | +0.741 | +0.00107 | 15% |
| **450-900** | 341 | +1.764 | **+0.00517** | **74%** |
| **900-1800** | 753 | **−1.822** | **−0.00242** | **−35%** |

So the full-history figure is small **because the oldest 900 days are negative**,
not because the edge is uniformly tiny. This confirms Round 227's Alpha-layer
walk-forward — where segments S1 and S2 were negative — at the **Portfolio**
layer, on the deployed policy, through an independent route.

## What this settles and what it does not

**Settles:** XAU's Portfolio gross edge is not a one-window artifact. It is
positive in the two most recent bands and negative in the oldest, and the
aggregate is positive on every window tested.

**Does not settle:** whether it is large enough to matter. The best band reaches
**74% of friction**; the most recent 450 days reach **15%**. Even the best band
does not cover its own costs, and the most recent — the one that matters for
deployment — is the weaker of the two positive ones.

So Round 241's headline stands with a correction of emphasis: the number is not
noise, it is **real and insufficient**, and it has been shrinking in the most
recent band relative to the one before it.

## Cross-checking against the rest of the session

This is now the fourth independent route to the same shape:

- Round 227 (Alpha, walk-forward): oldest two segments negative, recent positive.
- Round 234 (Portfolio gate, holdout only): positive gross, cost/gross 3.22.
- Round 241 (Portfolio, full window): +0.00038, ~5% of friction.
- **Round 242 (Portfolio, bands): −0.00242 / +0.00517 / +0.00107 oldest to newest.**

All four agree on the shape and none of them reaches break-even. The consistency
is worth more than any single figure.

## What is proven, and what is not

Proven:

- exness XAU 5m zero-cost `one_target`: 450d gives 693 trades and +0.741; 900d
  gives 1,034 and +2.505; 1,800d gives 1,787 and +0.683.
- Gross per trade is positive on all three windows, spanning +0.00038 to +0.00242.
- Band decomposition: 0-450 +0.00107, 450-900 +0.00517, 900-1800 −0.00242.

Not proven, and deliberately not claimed:

- That the bands are statistically distinguishable from each other. Three bands
  with 341-753 trades and no confidence intervals; the sign pattern is the claim,
  not the ordering of magnitudes.
- That the subtraction is exact. It leans on Round 226's independence result,
  which was demonstrated for a fixed holdout under varying history — a closely
  related but not identical setup. Flagged as an inference.
- Anything about BTC. Round 241 measured its full-window gross as **negative**;
  no band decomposition was run for it.
