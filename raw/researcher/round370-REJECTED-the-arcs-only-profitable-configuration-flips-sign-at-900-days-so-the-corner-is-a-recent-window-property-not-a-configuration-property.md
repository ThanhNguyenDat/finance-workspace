# CORNER CLOSED ON BOTH ROUTES (Round 371)

This file refused to predict whether the corner also fails on `binance BTC`. It does:
at 900 days on that route the corner scores **-2.95541**. The corner's positive PnL is a
**recent-window property on both routes**, and the question is closed.

This file's other observation is strengthened rather than qualified. The corner's
advantage over the `legacy` control is now positive in **4/4 measurements across two
routes and two window depths** (+2.24338, +1.55149, +1.86003, +5.08599), and the
**largest** belongs to the **deployed** configuration, not the corner - so the effect is
the construction guard plus risk layer itself, not the searched corner. See
`round371-NEEDS-MORE-RESEARCH-the-construction-guard-is-the-arcs-first-cross-route-cross-window-stable-effect-and-binance-btcs-target-3-pass-fails-at-900-days.md`.

---

# Round 370 — REJECTED: the arc's **only profitable configuration flips sign at 900 days**. The corner is a property of the recent window, not of the configuration.

Classification: **REJECTED** — my pre-registered criterion fired against the
arc's own strongest positive result. Two bounded Docker runs (exactly the
2-container budget), `exness.cfd.XAU.USD` at band 0.02/0.04, hold 288.

## The pre-registration

The corner (band 0.02/0.04, `minimum_hold_decisions` 288) is the **only
configuration in 60+ rounds with positive PnL at deployed costs**: +1.17395 on
`exness XAU` @300 (r365), and it transferred to `binance BTC` @500 at +0.37527
(r366). Both measurements are **full-window and in-sample**, and — as r331,
r334 and r341 each showed for band-axis structure — nothing in this arc had ever
tested the corner on a window it was not selected on.

Registered before running, on `exness XAU` at the same band and hold:

- **positive at both @500 and @900** → the sign is window-robust across a 3x
  range, which materially strengthens the corner;
- **negative at either** → the corner is a window artifact and the arc's only
  positive result is not a property of the configuration.

**Observed: @500 +0.79730, @900 −0.70835. The criterion fired.**

## The three windows

| days | candles | bar-days | coverage | trades/week (cal.) | `one_target` PnL | `legacy` control |
|---|---|---|---|---|---|---|
| 300 (r365) | 57,934 | 201.2 | 67.1% | 1.94 | **+1.17395** | — |
| **500** *(new)* | 96,686 | 335.7 | 67.1% | 1.93 | **+0.79730** | −1.44608 |
| **900** *(new)* | 174,251 | 605.0 | 67.2% | 1.27 | **−0.70835** | −2.25984 |

The sign survives 300 → 500 and **fails at 900**. This is consistent with what
the arc already established about edge on this layer — r241 ("Portfolio gross
edge is a recent-window property"), r244 ("the recent edge is broad in sign but
decaying") — and it now applies to the one configuration that had escaped that
verdict.

## The honest nuance: relatively robust, absolutely not

Against the `legacy_selected_rule` control (the free drift control from r360 —
same decision stream fed straight to the ledger, no construction guard and no
risk layer), the corner is **better at every window measured**, including the
one where it loses money:

| window | corner | legacy | corner advantage |
|---|---|---|---|
| 500 | +0.79730 | −1.44608 | +2.24338 |
| 900 | −0.70835 | −2.25984 | +1.55149 |

So the guard-plus-band configuration **does** something real and it does it at
both windows. What does not survive is the thing that mattered: **crossing zero.**
A configuration that is reliably less bad than the control, and still negative
over 900 days, is not a candidate.

## A definitional issue this round exposed

`exness` CFD gold has **67.1% bar coverage of calendar time** at all three
windows — the trading calendar (r337), not a data defect, and remarkably stable
across windows. The arc's trades-per-week convention divides by **calendar**
weeks, so on this route it understates activity by **1.49x** relative to bar
time (e.g. 1.94 vs 2.89/week @300).

This does not change any verdict in this round, and it does not change any
comparison made *within* the arc's convention. It does mean that **whether
`exness XAU` clears the 7/week Target 3 bar depends on a definition nobody has
fixed** — a 1.49x factor on the route where Target 3 has been closest to
ambiguous (r285, r286, r304). Recorded as an open definitional question, **not**
as a re-scoring of any past result.

## What is proven, and what is not

Proven:

- `exness XAU`, band 0.02/0.04, hold 288: @500 → 96,686 candles, 138 trades,
  +0.79730; @900 → 174,251 candles, 163 trades, **−0.70835**.
- The `legacy` control is negative at both windows (−1.44608, −2.25984) and the
  corner beats it at both.
- Bar coverage is 67.1% / 67.1% / 67.2% across the three windows.

Not proven, and deliberately not claimed:

- **What the older period contributed.** The windows are nested (r352), and
  r300 established that **nested differencing is invalid for Portfolio
  counters** — weights refit on every kline, so two runs of different length
  carry different weights over every bar they share. I am therefore **not**
  computing "the older 400 days cost −1.506", and no such number appears above.
- That the corner fails on `binance BTC` too. Untested there at other windows;
  r369 showed the two routes disagree about band-axis structure, so it could go
  either way and I am not predicting.
- That 900 days is the "right" window. It is one more window, not a verdict on
  which horizon is representative. r321 already noted the deep windows are the
  pessimistic end.
- A mechanism for the flip. The replay is deterministic (r351), so this is a
  genuine property of the longer window rather than sampling noise — but no
  mechanism is offered.
- That the corner is worthless. It beats the control at every window measured.
  What is refuted is the claim that it is **profitable**, which was the only
  reason it was interesting.

## Where the arc stands

Every positive Portfolio-layer result found in this arc has now either failed to
generalise across routes (r364, r367, r369) or failed to hold its sign across
windows (this round). Nothing is promotable, and the two structural blockers are
unchanged: hold-bearing configurations still have **no gate score** (r356,
promotion condition 1), and every holdout in the arc is **nested** (r352).
