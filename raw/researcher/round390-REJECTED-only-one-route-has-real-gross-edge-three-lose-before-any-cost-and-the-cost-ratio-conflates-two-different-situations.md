# CHARACTERISATION INVALIDATED (Round 397)

This file's fleet table - "three routes gross-negative, two indistinguishable from zero,
one positive" - rests on **one holdout per route**, and round 397 shows that is not enough
to characterise a route either way.

`binance BTC`, recorded here as gross-negative from a single holdout, is gross-**positive**
on two of three disjoint holdouts: **-0.58685, +0.82128, +0.26947**.

Both routes now measured more than once alternate in sign:

| route | gross across holdouts | positive |
|---|---|---|
| `exness XAU` | +0.66471, -0.72458, +0.29154, -0.11094 | 2 of 4 |
| `binance BTC` | -0.58685, +0.82128, +0.26947 | **2 of 3** |

This file's *direction* was not wrong so much as its *confidence*: I applied the
disjoint-holdout test only to the positive result and accepted the negatives at face
value, which is a selection asymmetry regardless of which way it points. The
interpretation warning about `cost_to_gross_pnl_ratio` with a negative denominator stands
unchanged. See
`round397-DATA-ISSUE-i-tested-only-the-positive-result-on-disjoint-holdouts-the-negative-ones-are-just-as-unstable.md`.

---

# Round 390 — REJECTED: only **one** route has real gross edge. Three lose **before any cost**. The cost ratio conflates two entirely different situations, and I nearly built a conclusion on it.

Classification: **REJECTED** — round 389's named hypothesis is refuted. Two
containers (the budget), cleaned up; three routes read from held gate logs.

## The hypothesis, and its refutation

Round 389 measured `cost_to_gross_pnl_ratio` = 1.5677 on `exness XAU` and named
the test: *"if the ratio is above 1.0 everywhere, the fleet has real edge that is
uniformly too small to pay its friction."*

Five routes, holdout, Portfolio-faithful path, pinned window:

| route | **gross** | cost drag | net | cost/gross | sharpe | pos-day | trades/wk |
|---|---|---|---|---|---|---|---|
| **`exness XAU`** | **+0.66471** | 1.04205 | −0.37734 | 1.5677 | −0.810 | 0.401 | 6.232 |
| `bybit XAUT` | **+0.01363** | 0.32477 | −0.31114 | 23.8348 | −1.163 | 0.359 | 3.454 |
| `binance XAU` | **−0.39816** | 0.22512 | −0.62329 | 0.5654 | −4.561 | 0.407 | 4.794 |
| `binance BTC` | **−0.58685** | 1.19027 | −1.77712 | 2.0282 | −2.482 | 0.398 | **7.661** |
| `bybit BTC` | **−0.89289** | 1.56287 | −2.45576 | 1.7503 | −3.234 | 0.425 | **8.517** |

**The ratio is above 1.0 on four of five — and the hypothesis is still wrong**,
because on **three of them there is no edge to be too small**. Those routes lose
**before a single basis point of cost is applied**.

## The interpretation trap I walked into

`cost_to_gross_pnl_ratio` is only meaningful when **gross > 0**. With a negative
denominator it still produces a plausible-looking number — `binance XAU`'s 0.5654
would *pass* the 0.5-ish threshold band on a route whose gross is **−0.398** —
and `bybit XAUT`'s 23.83 is arithmetic on a gross of **+0.0136**, which is
indistinguishable from zero, not an edge being swamped 24×.

So a ratio above 1.0 conflates:

1. **real edge, swamped by costs** — `exness XAU`, and only `exness XAU`;
2. **no edge at all** — `binance BTC`, `bybit BTC`, `binance XAU`.

Round 389's reading was correct **for the route it measured** and I flagged the
single-route limit there. The fleet does not share it. The gate itself is not at
fault: it carries `gross_pnl_positive` as a **separate check**, which is exactly
the guard my interpretation needed and did not use.

## The sharper picture: frequency and edge sit on opposite routes

Two routes **pass** Target 3 on holdout at the deployed configuration —
`bybit BTC` at **8.517**/week and `binance BTC` at **7.661**/week. Both have
**negative gross**.

The one route with meaningful gross edge, `exness XAU`, trades **6.232**/week and
fails.

**The routes that trade enough have no edge; the route with edge does not trade
enough.** That is the joint objective failing on both axes at once, measured
correctly for the first time.

## What is proven, and what is not

Proven:

- The five-route table above, all on the Portfolio-faithful holdout path.
- Exactly one route has gross above 0.02: `exness XAU` at +0.66471.
- Three routes are gross-negative; `binance BTC` and `bybit BTC` pass Target 3
  on holdout while being gross-negative.
- `exness XAU`'s figures are identical across a pinned and an unpinned gate run
  of the same window (r383 and r386), a consistency check that happens to hold.

Not proven, and deliberately not claimed:

- **That `exness BTC` fits either group.** It is the sixth route and was not
  measured this round.
- That gross edge is stable. One holdout each; r382 established that small
  window changes move route PnL by percent-scale amounts, and these gross
  figures are small.
- That `bybit XAUT`'s +0.01363 is edge. It is closer to zero than to
  `exness XAU`'s figure by a factor of 49, and I am treating it as no edge.
- Any cause for three routes being gross-negative. Not investigated here.
- That the Target 3 passes are new information about frequency. They are the
  **holdout** rate; r371 measured 6.80/week full-window on `binance BTC`, so the
  trailing period simply trades more densely (r383 measured that directly).

## Named next step

Measure `exness BTC` to complete the fleet, then stop measuring: if five of six
routes have no gross edge on holdout, the question is no longer which
Portfolio-layer knob to turn but **whether the Alpha ensemble produces edge on
any route other than `exness XAU`** — and rounds 373/374 already showed the
Alpha layer's own holdout scan survives no conservative test.
