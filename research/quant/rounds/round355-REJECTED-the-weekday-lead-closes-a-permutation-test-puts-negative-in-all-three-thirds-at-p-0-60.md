# Round 355 — REJECTED: the weekday lead **closes**. A permutation test puts *"some weekday negative in all three disjoint thirds"* at **p = 0.60** — it happens by chance six times in ten. Wednesday's magnitude is **p = 0.0532**, failing the α I registered, and Friday is **p = 0.20**.

Classification: **REJECTED** — the direction opened in Round 352 and built on in Round 353 is
closed as consistent with chance. **Zero containers**; permutation analysis of one saved run.

## Applying this loop's own lesson before registering anything

The skill's standing rule, learned from Round 327: *compute the permutation distribution before
committing to a threshold*, and build the multiplicity in. Round 353's evidence had two parts, so
both were turned into statistics with the selection cost included:

- **S1** — the **minimum** weekday mean across the five trading weekdays (using the minimum, not
  Wednesday by name, prices in the fact that Wednesday was *chosen* as the worst of five);
- **S2** — *"some weekday is negative in all three disjoint thirds"*, which is what Round 353
  actually reported.

Permutation: shuffle weekday labels across the 257 trading-weekday rows of `exness XAU` @1800,
holding the per-weekday counts fixed, N = 20,000.

**Pre-registered as a partition:** **p < 0.05** → the concentration is not explained by chance on
this route; **p ≥ 0.05** → it is, and the lead closes.

## Result

Observed means: Mon −0.00062, Tue −0.00473, **Wed −0.01603**, Thu +0.00474, **Fri +0.01043**.

| statistic | observed | **p** |
|---|---|---|
| min weekday mean ≤ Wednesday's | −0.01603 | **0.0532** |
| max weekday mean ≥ Friday's | +0.01043 | **0.1996** |
| **some weekday negative in all three thirds** | true | **0.6013** |

**S2 is worthless.** Round 353's headline — Wednesday negative in all three disjoint 102-day
thirds, with stable magnitude — arises **in 60% of random shufflings**. The arithmetic is
unsurprising once stated: with an overall daily mean slightly negative, each weekday is negative
in a given third with probability a little over ½, so ≈0.5³ per weekday and ≈1 − (1−0.125)⁵ ≈ 0.5
across five. The "three disjoint periods agree" structure that made the finding feel solid
**carries almost no information**.

**S1 fails the registered threshold.** p = 0.0532 ≥ 0.05. I registered 0.05 and it does not
pass — that is the whole verdict, and "marginal" is not a result.

**S3, Friday, was never close.** p = 0.1996.

## What multiplicity cost, exactly

Testing Wednesday **by name**, ignoring that it was selected as the worst of five, gives
**p = 0.0112** — comfortably "significant".

The honest, selection-corrected figure is **p = 0.0532**. **Ignoring multiplicity would have made
the p-value 4.8x smaller and flipped the verdict.** This is the concrete cost of the mistake this
loop has now avoided twice, and it is worth keeping the number.

## Where this leaves the direction

Three independent lines now point the same way:

1. **Round 354**: the pattern **inverts** on both BTC routes — Wednesday worst on `exness XAU`,
   best or second-best on `exness BTC` and `binance BTC`; Friday best on `exness XAU`, worst on
   both.
2. **This round**: the structural evidence (S2) is worth nothing, and the magnitude evidence (S1)
   fails its registered threshold.
3. Even a passing result was never actionable — the CLI has **no weekday filter**, gross by
   weekday is **unobtainable** (Round 354), and the route is **gate-ineligible** at every window.

**The weekday direction is closed.** Rounds 352-353's measurements stand as measurements; their
interpretation does not survive a test that prices in how the hypothesis was chosen.

## What is proven, and what is not

Proven:

- Observed weekday means on `exness XAU` @1800 (257 trading-weekday rows, 49 Saturday buckets
  excluded).
- Permutation p-values at N = 20,000 with weekday counts held fixed: min-statistic **0.0532**,
  max-statistic **0.1996**, all-three-thirds statistic **0.6013**.
- The naive single-weekday p for Wednesday is **0.0112**, 4.8x smaller than the corrected figure.

Not proven, and deliberately not claimed:

- **That there is no weekday effect.** p = 0.0532 is a failure to reject, not evidence of absence,
  and 257 rows is a small sample for a per-weekday mean. What is established is that **this
  evidence does not support the claim**.
- That the permutation null is exactly right. Shuffling labels assumes daily PnL is exchangeable
  across weekdays; serial correlation in daily PnL would make the true p **larger**, not smaller,
  so the direction of that approximation does not rescue the result.
- Any correction to Rounds 352-353's arithmetic. Their numbers are unchanged; what fails is the
  inference drawn from them.
- Anything about routes other than `exness XAU` or windows other than @1800 for these p-values.
- Any promotion. The direction is closed, not promoted.
