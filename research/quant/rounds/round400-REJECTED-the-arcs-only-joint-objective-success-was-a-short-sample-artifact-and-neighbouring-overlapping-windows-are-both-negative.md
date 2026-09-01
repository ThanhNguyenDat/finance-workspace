# Round 400 — REJECTED: the arc's only joint-objective success was a **short-sample artifact**. Neighbouring, heavily overlapping windows are **both negative**.

Classification: **REJECTED** — the pre-registered criterion fired. Two
containers (the budget), cleaned up. Closes the thread round 399 opened.

## First, a constraint I had to state before testing

Round 399 named "re-run `bybit XAUT` at a cutoff giving a ≥ 90-day holdout".
**That is not obtainable for a holdout ending at 2026-03-04** — the route's
history does not reach far enough back, and holdout length is 20% of whatever
loads. So the test became: does the positive reading survive when the window
**slides**, rather than when it lengthens?

## The result

| cutoff | holdout | days | gross | **net** | trades/wk | ≥90d |
|---|---|---|---|---|---|---|
| 2026-01-15 | 2025-11-20 → 2026-01-15 | 55.7 | −0.18472 | **−0.25888** | 2.513 | no |
| **2026-03-04** | **2025-12-28 → 2026-03-04** | **65.3** | +0.46972 | **+0.06359** | **7.073** | no |
| 2026-04-15 | 2026-01-31 → 2026-04-15 | 73.7 | +0.14300 | **−0.45686** | 9.021 | no |
| 2026-08-31 | 2026-05-21 → 2026-08-31 | 101.3 | +0.01363 | **−0.31114** | 3.454 | **yes** |

**Both neighbours are negative**, and they are not distant tests: the
2026-04-15 window **overlaps the positive one by about 33 days** and still comes
out at −0.45686.

**Registered answer: the +0.06359 is window-specific.** It is the short-sample
effect the 90-day minimum exists to catch, and round 399 was right to refuse to
count it.

## The instability underneath

Trades per week across these four windows: **2.513, 7.073, 9.021, 3.454** — on
windows that **overlap each other substantially**. The Target 3 verdict on this
route flips between clear fail (2.51) and clear pass (9.02) on a cutoff shift of
a few weeks.

And **only one of the four holdouts meets the 90-day minimum at all**. On this
route the gate can effectively only score the most recent cutoff; every earlier
one is disqualified by length before its numbers matter.

## Not pooled

These two new readings are **not** added to the nine-holdout series from round
399. They are overlapping windows on a route already represented there, so
treating them as independent points would inflate n with correlated data — the
error round 398 already flagged the existing series for.

The pooled estimate stands where round 399 left it: **n = 9, mean +0.19085, 95%
interval [−0.16974, +0.55144], includes zero.**

## What is proven, and what is not

Proven:

- The four-window table above, all pinned cutoffs on the Portfolio-faithful
  gate path.
- The two neighbouring windows are negative; the 2026-04-15 window overlaps the
  positive one by roughly 33 days.
- Only the 2026-08-31 cutoff yields a ≥ 90-day holdout on this route.
- Trades/week spans 2.513 to 9.021 across overlapping windows.

Not proven, and deliberately not claimed:

- **That `bybit XAUT` cannot be profitable.** Four short windows on one route
  say the one positive reading does not survive a window slide; they do not
  establish a negative property of the route.
- That the 33-day overlap makes the comparison strong. Overlapping windows share
  data, so their disagreement is *more* telling than independent ones would be —
  but it is one route and four readings.
- That the frequency instability is specific to this route. `exness XAU` and
  `binance BTC` also varied by 3x across holdouts (r392, r397); this route is
  the most extreme measured, on the shortest windows.
- Anything new about the pooled interval. Unchanged from round 399 by design.

## Named next step

The `bybit XAUT` thread is closed. Of the backtest questions this arc can still
answer, the honest list is now short: two or three more disjoint holdout points
on `exness BTC` and `bybit BTC`, which would take the pooled series to n ≈ 12
and narrow the interval by perhaps a further sixth. On the current estimate that
would not change the answer, so it is worth doing only as confirmation, not as
inquiry.
