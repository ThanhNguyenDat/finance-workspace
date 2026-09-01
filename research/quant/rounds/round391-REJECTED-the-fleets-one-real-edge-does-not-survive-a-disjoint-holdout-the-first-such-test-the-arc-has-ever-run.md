# Round 391 — REJECTED: the fleet's one real gross edge **does not survive a disjoint holdout** — the first genuinely disjoint out-of-sample test this arc has ever been able to run.

Classification: **REJECTED** — the pre-registered criterion fired. Two
containers (the budget), cleaned up.

## The test r352 declared impossible

Round 352 established that every holdout in this arc is **nested**: holdout is
the trailing 20% of `--days`, so no two `--days` values give disjoint
out-of-sample periods. That blocker stood for 39 rounds.

`--as-of`, added by the measurement transaction for an unrelated reason
(reproducibility, r382), **dissolves it**: shifting the cutoff back by exactly
one holdout length produces a holdout that does not overlap the original at all.

| | holdout | gross | net | cost/gross | trades/wk |
|---|---|---|---|---|---|
| original | 2026-03-04 → 2026-08-31 | **+0.66471** | −0.37734 | 1.5677 | 6.232 |
| **disjoint** | **2025-09-04 → 2026-03-04** | **−0.72458** | −1.20812 | 0.6673 | 3.020 |

**No overlap.** The second holdout ends exactly where the first begins.

**Registered answer: the gross edge is −0.72458. NOT POSITIVE.**

## What that means

`exness XAU` was the only route in the fleet with meaningful gross edge — round
390 measured five routes and found one. This round completes the sixth
(`exness BTC`, gross +0.09272, cost/gross 9.55, i.e. no usable edge) and then
tests the one that mattered on data it had never touched.

**It reverses sign.** The +0.66471 was a property of that six-month period, not
of the configuration.

So, stated plainly: **after 186 iterations, with the measurement finally
correct — Portfolio-faithful replay, holdout-restricted, pinned window,
hold-bearing configuration, full joint-objective scorecard — there is no
demonstrated gross edge anywhere in the fleet on genuinely unseen data.**

Trade frequency is not stable either: 6.232/week on one holdout, **3.020** on the
adjacent one. The same halving that r382 warned about, on a quantity Target 3 is
judged by.

## The fleet, complete

| route | gross (holdout) |
|---|---|
| `exness XAU` | +0.66471 → **−0.72458 on the disjoint holdout** |
| `exness BTC` | +0.09272 |
| `bybit XAUT` | +0.01363 |
| `binance XAU` | −0.39816 |
| `binance BTC` | −0.58685 |
| `bybit BTC` | −0.89289 |

Three negative, two indistinguishable from zero, and the one positive figure
does not replicate.

## On the transaction that made this possible

The measurement change is vindicated by this round in the way that matters: its
whole purpose was to make a defensible out-of-sample judgement possible, and the
first such judgement it enabled is **negative**. That is the correct outcome of
doing measurement properly, and it is worth more than the 60 rounds of
parameter search that preceded it.

## What is proven, and what is not

Proven:

- The two `exness XAU` holdouts are disjoint (2025-09-04 → 2026-03-04 and
  2026-03-04 → 2026-08-31) and give gross −0.72458 and +0.66471.
- `exness BTC` holdout gross +0.09272, net −0.79258, cost/gross 9.55.
- The six-route gross table above.

Not proven, and deliberately not claimed:

- **That the configuration has no edge.** Two holdouts on one route is two
  observations. The claim is that the one positive result **does not replicate**,
  not that a negative result is established.
- That the other five routes would also reverse. Untested on a disjoint holdout;
  three of them are negative on the holdout already measured, so there is
  nothing to reverse.
- That disjoint holdouts are now cheap and general. Shifting the cutoff back
  costs one full run per holdout and consumes history; a 900-day window admits
  roughly four such disjoint 180-day holdouts before running out of data on the
  deepest route, and fewer on `binance XAU` (r208).
- Any cause for the sign reversal. Gold rose through the later period and was
  flatter earlier (r385 measured +105% across the full window); I have not
  decomposed the two holdouts' drift and am not attributing.

## Named next step

Run the remaining two disjoint holdouts on `exness XAU` — the history supports
about four in total. If gross is negative on three of four, the route's single
positive reading is noise and the Portfolio-layer search is finished as an
edge-finding exercise. That is two rounds of work and it settles the question
the arc has been circling since round 313.
