# EXTENDED TO 900 DAYS (Round 321)

`exness XAU`'s positive raw edge now holds at **five** windows — 250, 360, 500, **700
and 900 days** — positive on both measures at every one (ten of ten values). The claim
is robust across a 3.6x range of window lengths, including the depth at which Round 312
measured the perturbation confound at its worst.

The **magnitude** range widens: per-trade edge spans **2.27x** and the edge-to-cost
ratio runs **26-59%** (needing a **41-74%** cut), with the two deepest windows giving
the two lowest ratios. See
`round321-NEEDS-MORE-RESEARCH-the-one-surviving-claim-holds-across-250-to-900-days-but-the-deep-windows-are-the-pessimistic-end.md`.

---

# Round 320 — REJECTED: `binance BTC`'s raw edge **flips sign** at 500 days. The "perpetuals are negative" rule is a **360-day artifact**, and measure-agreement does **not** buy window-stability.

Classification: **REJECTED** — Round 314's central claim fails at another window. Two
bounded Docker sweeps (exactly the 2-container budget).

## What was being tested

Round 319 showed `exness XAU`'s positive sign is window-robust across 250-500 days and
partially un-scoped Round 318 on that basis — while naming the limit: *"That sign
stability generalises to other routes. One route, three windows. The routes that
actually flipped (`bybit XAUT`) and disagreed (`exness BTC`) were not re-tested."*

This round spends one container on **`bybit XAUT` at 500 days** — completing three
windows on the flip-prone XAU route — and one on **`binance BTC` at 500 days**, the
flagship *negative* cell that Round 314's whole conclusion rests on.

**Pre-registered:** for `bybit XAUT`, ≥1 of 3 windows with disagreeing measures means
the route is chronically unstable and claims from it are unusable. For `binance BTC`,
negative and agreeing at both windows would show sign stability generalises beyond
`exness XAU` and is not confined to large magnitude.

## The result

Zero execution cost, same day, three windows per route:

| route | `--days` | trades | **`one_target`** | gross/trade | guard-free | measures agree |
|---|---|---|---|---|---|---|
| `exness XAU/USD` | 250 | 304 | +1.4354 | +0.00472 | +1.5226 | yes |
| `exness XAU/USD` | 360 | 391 | +1.0997 | +0.00281 | +1.5993 | yes |
| `exness XAU/USD` | 500 | 549 | +3.0359 | +0.00553 | +4.1558 | yes |
| `bybit XAUT/USDT` | 250 | 192 | +0.6346 | +0.00331 | **−0.1791** | **NO** |
| `bybit XAUT/USDT` | 360 | 278 | +0.3427 | +0.00123 | +0.0936 | yes |
| **`bybit XAUT/USDT`** | **500** | 349 | +0.5945 | +0.00170 | **−0.2936** | **NO** |
| `binance BTC/USDT` | 360 | 479 | **−0.4432** | **−0.00093** | −2.0053 | yes |
| **`binance BTC/USDT`** | **500** | 515 | **+1.7176** | **+0.00334** | +0.3089 | **yes** |

### `binance BTC` flips

**−0.4432 at 360 days, +1.7176 at 500 days — and both measures agree at both windows.**
Its gross edge per trade goes from **−0.00093** to **+0.00334**, which at 500 days
exceeds `exness XAU`'s 360-day +0.00281.

**Round 314's central claim — "`binance BTC`'s raw signal is unprofitable before any
friction, so no cost reduction can make this route profitable" — is true at 360 days
and false at 500.**

And it settles something Round 319 left implicit: **measure-agreement and
window-stability are independent properties.** `binance BTC` agrees at both windows and
still flips. Agreement tells you the two measures see the same thing *at that window*;
it says nothing about another.

### `bybit XAUT` is chronically unstable

Its `one_target` sign is positive at all three windows, but the guard-free measure runs
**−0.1791 / +0.0936 / −0.2936** — **disagreeing at 2 of 3 windows.** By the
pre-registered rule, claims resting on that route are **unusable**.

## What this does to Rounds 314-317

The five-cell picture was measured entirely at 360 days. Of the three routes now tested
for window-stability, **only one is usable**:

| route | sign across windows | measures | verdict |
|---|---|---|---|
| `exness XAU` | positive 3/3 | agree 3/3 | **usable** |
| `bybit XAUT` | `one_target` positive 3/3 | **disagree 2/3** | unusable |
| `binance BTC` | **flips**: − at 360d, + at 500d | agree 2/2 | **window-scoped** |

So:

- **Round 314's "cost-driven does not generalise" is itself window-scoped.** At 500
  days `binance BTC` looks like the Exness routes did at 360.
- **Round 316's "broker is ruled out, both perpetuals negative" is 360-day specific.**
  One of those two perpetuals is positive at 500 days.
- **Round 317's clean market-type split is 360-day specific** for the same reason.
- **Round 319's partial un-scoping was based on the one route that turned out to be the
  exception.** Round 318's original caution was closer to right than Round 319 allowed.

The one claim that survives unqualified is `exness XAU`'s positive raw edge, stable in
sign and measure across 250-500 days.

## What is proven, and what is not

Proven:

- `binance BTC` at zero cost, same day: 360d → 479 trades / −0.4432 / guard-free
  −2.0053; **500d → 515 trades / +1.7176 / guard-free +0.3089**. Both windows have
  agreeing measures; the sign differs.
- `bybit XAUT` at zero cost: `one_target` +0.6346 / +0.3427 / +0.5945 at 250/360/500,
  guard-free −0.1791 / +0.0936 / −0.2936 — measures disagree at two of three windows.
- Gross edge per trade for `binance BTC`: −0.00093 at 360d, +0.00334 at 500d.

Not proven, and deliberately not claimed:

- **That `binance BTC` has positive raw edge.** It has one at 500 days and not at 360.
  What is established is that **the sign is window-dependent**, which is weaker and
  more damaging than either single reading.
- **Any market-type or instrument conclusion.** Rounds 316-317 are now known to rest on
  a window at which one of their cells has the opposite sign. I am not proposing a
  replacement rule.
- That `exness XAU` will stay stable outside 250-500 days. Rounds 304 and 312 showed
  the window confound grows with depth and 900 days remains untested on this measure.
- Which window is "right". None is privileged; the arc has no way to choose one, and
  that is the honest state.
- Any magnitude, PF, win rate, Sharpe, Sortino, drawdown or streak. Unchanged since
  Round 313.
