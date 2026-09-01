# CORRECTION (Round 279)

This file's `≤3.05h` "at the floor" bucket **conflated two populations**. Round 279
traced the code path this file said was untraced (`trading_modes.rs:238-264`): the 3h
guard gates **only re-entries after a protective exit**. After a plain flat exit,
`starts_initial_position` is true and the next gate pass opens a position
**immediately, bypassing the guard**.

Measured: the ≤0.2h gap fraction equals the flat-exit fraction **exactly** on three
routes (14.0/14.0, 5.8/5.8, 47.6/47.6) and the **0.2-2.9h band is empty** on all
three. So this file's "half to two-thirds re-enter at the earliest moment the guard
permits" is wrong: on `exness XAU` the guard is involved in **17.6%** of re-entries,
not 64.7%.

This file's *measurements* stand — the flat durations, the occupancy validation, the
tail statistics. The interpretation of the floor does not. See
`round279-CORRECTION-the-guard-gates-only-post-protective-re-entries-and-the-gap-band-is-empty.md`.

---

# Round 278 — Flat time is pinned at exactly the hold guard for half of all re-entries; occupancy is set by the length of the tail beyond it

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence.
**Zero containers.**

## Round 277's open question, decomposed one level further

Round 277 measured occupancy (43.3%-86.7%) and said plainly that **what drives it is
not known**. Occupancy is not a primitive: since a position is either open or flat,

```
occupancy = hold / (hold + flat)
```

`hold` is already accounted for by σ² (Round 273). So the free quantity is **flat
time**, and it is measurable *independently* — from the gap between one trade's
`exit_at` and the next trade's `entry_at`, not by rearranging occupancy.

| route | n | mean hold | mean flat | **occ. from flat** | **occ. measured** | overlaps |
|---|---|---|---|---|---|---|
| binance BTC | 473 | 10.96h | 7.43h | **59.6%** | **59.6%** | 0 |
| bybit BTC | 311 | 12.14h | **15.94h** | **43.2%** | **43.3%** | 0 |
| exness BTC | 481 | 10.89h | 7.19h | **60.2%** | **60.3%** | 0 |
| exness XAU | 392 | 19.17h | **2.96h** | **86.6%** | **86.7%** | 0 |

The independent computation reproduces measured occupancy to within 0.1pp on all
four routes, and no positions overlap. The decomposition is validated, not assumed.

## The finding: flat time has a hard floor at the hold guard

`minimum_hold_decisions = 36` at a 5m decision interval is **36 × 5 = 180 min =
3.00h**. Median flat time:

| route | **median flat** | mean flat | mean/median | **re-entries at the floor (≤3.05h)** | **flats > 12h** | occupancy |
|---|---|---|---|---|---|---|
| exness XAU | **3.00h** | 2.96h | 0.99 | **64.7%** | **2.0%** | 86.7% |
| binance BTC | **3.00h** | 7.43h | 2.48 | 52.5% | 15.5% | 59.6% |
| exness BTC | **3.04h** | 7.19h | 2.37 | 50.0% | 13.5% | 60.3% |
| **bybit BTC** | **4.29h** | 15.94h | 3.71 | **26.8%** | **27.7%** | 43.3% |

**Median flat time is 3.00h on two routes and 3.04h on a third — exactly the hold
guard.** Between half and two-thirds of all re-entries happen at the *earliest moment
the guard permits*. The guard is not a rarely-touched safety limit; it is the
binding constraint on most re-entries.

**Occupancy is then set almost entirely by the tail beyond the floor.** Order the
routes by "fraction at the floor" (64.7 / 52.5 / 50.0 / 26.8) or inversely by
"fraction waiting over 12 hours" (2.0 / 15.5 / 13.5 / 27.7) and you recover the
occupancy ordering (86.7 / 59.6 / 60.3 / 43.3). `bybit BTC` re-enters immediately
only half as often as its BTC siblings and waits over 12 hours twice as often.

## An incidental corroboration of Round 80

Round 80 raised `minimum_hold_decisions` from 12 to 36 and measured a ~34% loss
reduction. This round shows why the effect was so large: the guard sets a **hard
floor that more than half of all re-entries sit exactly on**, so moving it from 1h to
3h directly delays the majority of re-entries. That mechanism was inferred in Round
80; it is now visible in the trade timings.

## What is proven, and what is not

Proven:

- Flat durations measured independently reproduce occupancy to 0.1pp on four routes,
  with zero overlapping positions.
- Median flat time 3.00h / 3.00h / 3.04h / 4.29h against a 3.00h hold guard.
- Re-entries at the floor: 64.7% / 52.5% / 50.0% / 26.8%; flats over 12h: 2.0% /
  15.5% / 13.5% / 27.7%.
- Those two orderings match the occupancy ordering across all four routes.

Not proven, and deliberately not claimed:

- **What creates the long tail.** This round moves the question from "why does
  occupancy differ" to "why do some routes wait far beyond the guard", which is
  narrower but still open. Round 267 found `trend_score` cannot change faster than an
  hourly close with 84-89% of its weight in 4h/12h/1d, so an adverse pinned trend
  would block entries for many hours — **consistent with a 27.7% tail over 12h, and
  entirely untested.** I am flagging the link, not asserting it.
- That the guard *causes* the floor rather than coinciding with it. The match is
  exact on three routes, which is strong, but no code path was traced to confirm the
  guard gates re-entry as well as reversal.
- That lowering the guard would raise occupancy usefully. It would raise trade count,
  and Rounds 274/275 showed per-trade cost does not improve with frequency — Round 80
  moved this lever in the *opposite* direction for exactly that reason.
- Anything about `binance XAU` or `bybit XAUT`, whose n is 7 and 1. Excluded here.
