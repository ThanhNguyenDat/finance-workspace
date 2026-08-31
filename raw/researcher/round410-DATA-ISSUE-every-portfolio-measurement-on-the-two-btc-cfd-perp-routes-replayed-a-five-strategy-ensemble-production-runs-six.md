# Round 410 — DATA-ISSUE: every Portfolio measurement on `binance BTC` and `exness BTC` replayed a **five**-strategy ensemble; production runs **six**. The conclusion survives; the scope does not.

Classification: **DATA-ISSUE**. **Zero containers**, code read plus arithmetic
on results already held.

## The chain

- Round 375 verified the research Portfolio replay is fed by
  `production_candidates` — and I treated that as reassurance.
- Round 408 found `production_candidates` has **drifted** from the live
  configuration: both BTC routes run a seventh strategy it omits.
- Round 409 asserted in passing that "the Portfolio replay does not consume it".

That assertion is **load-bearing** and this round checks it. Confirmed in code:
**both** replay paths — the gate at `main.rs:617` and the measurement path at
`main.rs:678` — call `strategies::production_candidates(&instrument)`.

| route | research ensemble | live ensemble | |
|---|---|---|---|
| `binance BTC` | **5** | **6** | **different** |
| `exness BTC` | **5** | **6** | **different** |
| `exness XAU` | 3 | 3 | same |
| `binance XAU`, `bybit XAUT`, `bybit BTC` | 2 | 2 | same |

So **every Portfolio holdout number this arc produced on `binance BTC` and
`exness BTC` measures an ensemble production does not run.** Not wrong — valid
measurements of a smaller ensemble — but not descriptions of production.

## Which results this touches

**Affected:** the `binance BTC` and `exness BTC` rows of round 390's fleet table
and round 375's guard-advantage table; round 397's three-holdout `binance BTC`
series; round 399's `exness BTC` point.

**Unaffected:** everything on `exness XAU`, including round 389's scorecard,
round 394's Alpha-to-Portfolio comparison, and — importantly — **rounds 391 and
392's four-holdout series**, which carries the arc's central conclusion. Also
unaffected: `binance XAU`, `bybit XAUT`, `bybit BTC`, whose two-strategy
ensembles are identical in both definitions.

## The conclusion survives the split

The pooled nine-holdout series, separated:

| subset | n | mean gross | 95% interval | |
|---|---|---|---|---|
| all nine (r399) | 9 | +0.19085 | [−0.16974, +0.55144] | includes zero |
| **matching production** | **5** | **+0.11809** | **[−0.36502, +0.60120]** | **includes zero** |
| not matching | 4 | +0.28180 | [−0.32821, +0.89180] | includes zero |

**Restricting to the five holdouts whose ensemble matches production leaves the
same answer.** The interval widens, as it must at n=5, and still contains zero.

So this is a **scope correction, not a result correction**. What four of nine
points describe changes; what the series says does not.

## What is proven, and what is not

Proven:

- Both research Portfolio replay paths call `production_candidates`.
- The mirror gives 5 strategies on the two affected routes where production
  gives 6; the other four routes agree.
- The three pooled statistics above.

Not proven, and deliberately not claimed:

- **That the affected measurements would differ materially with the seventh
  strategy included.** That strategy trades 0.43/week and lost on holdout
  (r409); its marginal effect on a Portfolio replay is **unmeasured**, and a
  low-frequency loser could plausibly change little or change the decision
  stream substantially. I have not run it.
- That the mirror should be changed. It may be deliberate; round 408 found no
  comment either way, and the fix belongs to whoever owns the deployment
  contract.
- That the n=5 interval is trustworthy. Five holdouts from two routes with
  overlapping fitted histories — the independence caveat from round 398 applies
  more strongly, not less.
- That gold is representative. It is unaffected by this defect, which is a
  statement about coverage, not about generality.

## Named next step

The measurable version is one run: replay `binance BTC` with the live
six-strategy ensemble and compare against the five-strategy figure on the same
pinned window. That requires the research mirror to carry the seventh strategy,
which is a code change — so it belongs with the release decision, not before it.
