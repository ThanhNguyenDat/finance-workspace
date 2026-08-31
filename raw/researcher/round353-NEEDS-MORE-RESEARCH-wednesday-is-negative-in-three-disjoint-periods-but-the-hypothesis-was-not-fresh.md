# CLOSED — THE STRUCTURE ARGUMENT IS WORTH p = 0.60 (Round 355)

This file's headline evidence — Wednesday negative in **all three disjoint thirds** with stable
magnitude — is **not evidence**. A permutation test (20,000 shuffles of weekday labels, counts
fixed) puts *"some weekday negative in all three thirds"* at **p = 0.6013**: it happens by chance
six times in ten, because each weekday is negative in a third with probability a little over ½
and there are five of them.

The magnitude statistic, with the selection of Wednesday-as-worst-of-five priced in, gives
**p = 0.0532** — it **fails** the registered α = 0.05. (Testing Wednesday by name would have given
0.0112, 4.8x smaller, and flipped the verdict.) Friday is p = 0.1996.

**The weekday direction is closed.** This file's arithmetic stands; the inference does not.
See `round355-REJECTED-the-weekday-lead-closes-a-permutation-test-puts-negative-in-all-three-thirds-at-p-0-60.md`.

---

# DOES NOT TRANSFER — THE PATTERN INVERTS ON BTC (Round 354)

This file's within-route replication stands. What it does **not** support is any systematic
reading: applied to routes the hypothesis was never formed on — a genuinely fresh test — the
pattern **inverts**. Ranked within each route at @1800: Wednesday is **worst** on `exness XAU`
(−0.01603) and **best or second-best** on `exness BTC` (−0.01196) and `binance BTC` (−0.01148);
Friday is **best** on `exness XAU` (+0.01043) and **worst** on both BTC routes (−0.04116,
−0.04547).

Also, this file's decisive open question moved one step: an activity proxy shows Wednesday is
**less** active than average (0.824 vs 0.845) with a day-level win rate of **0.429 against
0.540** and 1.20x larger moves — pointing to **edge, not cost**. Gross by weekday is still
unobtainable, because any cost setting low enough to isolate it also unlocks reversals (round
348). See `round354-REJECTED-the-weekday-pattern-inverts-on-btc-routes-and-my-registered-criterion-was-vacuous.md`.

---

# Round 353 — NEEDS-MORE-RESEARCH: **Wednesday is negative in all three disjoint thirds** of a single 306-day holdout, at a stable −0.019 / −0.015 / −0.014 per day — **20.3x** the overall daily mean. Both registered hypotheses replicate. But neither hypothesis was **fresh**, and that is the finding's ceiling.

Classification: **NEEDS-MORE-RESEARCH** — a signal that survives the strongest test this tooling
allows, sitting on hypotheses the previous round had already seen in the verification data.
**Zero containers**; analysis of one saved run.

## Getting disjoint periods after Round 352 said they were impossible

Round 352 established that **every holdout is nested** — all end at "now", so no two `--days`
values give disjoint out-of-sample periods. That is true *across runs*.

It is not true *within* one run. A **single** replay's `daily_results` array can be split into
disjoint sub-periods, and because it is one replay the values are internally consistent — which
Round 343 showed they are **not** across runs. `exness XAU` @1800 gives a 306-day holdout, so
three disjoint 102-day thirds from one consistent computation.

**Pre-registered as two partitions**, both strict and single-hypothesis (Round 352's aggregate
criterion masked a sign flip, so no aggregation this time):

- **H1** — the weekday with the **highest** mean PnL in third 1 has **positive** mean in **both**
  third 2 and third 3 → replicates; fails in either → does not.
- **H2** — **Wednesday** has **negative** mean in **both** third 2 and third 3 → the
  negative-Wednesday observation Round 352 made but never registered replicates; otherwise not.

## Result — both replicate

`exness XAU` @1800, holdout 2025-09-04 → 2026-08-29, thirds at 2025-12-31 and 2026-04-30:

| weekday | third 1 mean | third 2 mean | third 3 mean | stable? |
|---|---|---|---|---|
| Mon | −0.00734 | **+0.01795** | −0.01246 | no — flips twice |
| Tue | −0.01350 | +0.00053 | −0.00121 | no |
| **Wed** | **−0.01895** | **−0.01486** | **−0.01428** | **yes — negative in all three** |
| Thu | −0.00901 | +0.00884 | +0.01413 | no — flips |
| **Fri** | **+0.00057** | **+0.00829** | **+0.02176** | **yes — positive in all three** |
| Sat* | +0.00055 | +0.00316 | 0.00000 | — |

\* the UTC+7 tail of the Friday session (audit L3), not a trading day.

**H1**: third 1's best weekday is **Friday** (+0.00057). Third 2 **+0.00829**, third 3
**+0.02176** — both positive. **Replicates.**

**H2**: Wednesday is **−0.01486** and **−0.01428**. **Replicates** — and it is negative in third 1
too, at −0.01895, so **all three disjoint periods agree with strikingly stable magnitude.**

Only Wednesday and Friday are stable; Monday and Thursday each flip sign between thirds.

## The size of it

Wednesday is 51 of 306 days (16.7%) and carries **−0.81767** of a holdout whose total net is
**−0.24159**. Its mean daily PnL is **−0.016033 against an overall −0.000790 — 20.3x worse than
the average day.**

Arithmetically, the holdout without Wednesdays sums to **+0.57608**.

**That number is an accounting exercise and not a backtest**, for the same reason Round 340 gave:
removing a losing subset after the fact is not a strategy. What makes this different from Round
340's single-day case is that the subset was **named in advance and verified on two further
disjoint periods** — which is why it is worth recording at all.

## The ceiling: neither hypothesis was fresh

This is the limitation that decides the classification.

| period | seen by Round 352's analysis? |
|---|---|
| third 1, 2025-09-04 → 2025-12-31 | partly — only 2025-09-04 → 2025-11-02 lies outside @1500's holdout |
| third 2, 2026-01-01 → 2026-04-30 | **yes** — inside @1200, @1500 and @1800 |
| third 3, 2026-05-01 → 2026-08-29 | **yes** — inside all of them |

**H2 exists because Round 352 observed Wednesday as consistently worst — on tables that already
covered thirds 2 and 3.** H1's discovery third is likewise mostly ground Round 352 walked. So the
design is sound and the **data is not out-of-sample with respect to the hypothesis**. A clean test
needs a hypothesis fixed before the verifying days are ever looked at, which cannot be
constructed retroactively — only prospectively, on days that do not yet exist.

And even a clean result would not be promotable from here: **the CLI has no weekday filter**, so
the candidate cannot be run end-to-end without a code change, and `exness XAU` remains
gate-ineligible on the seven continuity checks at every window.

## What is proven, and what is not

Proven:

- The weekday-by-third table above, from a single `exness XAU` @1800 replay (306 holdout days,
  thirds of 102 each).
- H1 and H2 as registered both replicate: Friday positive in thirds 2 and 3; Wednesday negative
  in thirds 2 and 3 (and in third 1).
- Wednesday: 51 days, sum −0.81767, mean −0.016033 against an overall mean of −0.000790 (20.3x);
  the holdout excluding Wednesdays sums to +0.57608 against an actual net of −0.24159.
- Monday and Thursday change sign between thirds; Wednesday and Friday do not.

Not proven, and deliberately not claimed:

- **That this is an out-of-sample result.** Thirds 2 and 3 were both inside the tables that
  suggested the hypotheses. The design is disjoint; **the hypotheses are not fresh**, and that is
  the honest ceiling on it.
- **That excluding Wednesday would produce +0.57608.** Removing a day removes its trades, which
  changes the Portfolio's subsequent state — Round 349 showed blocking an action does not simply
  subtract it. The figure is arithmetic on a fixed array.
- **Anything about gross by weekday.** `daily_results` carries `realized_pnl`, which is **net**.
  Whether Wednesday's edge is negative or merely more expensive is **not determinable** from this
  array, and that distinction decides whether a filter would help at all.
- Any cause. No market or session mechanism was examined; a mid-week effect on gold has plausible
  stories and none of them was tested.
- That it transfers to another route or the deployed 5m configuration at another window. One
  route, one run, one band.
- Any promotion. Not testable end-to-end without a code change, not fresh, and on a
  gate-ineligible route.
