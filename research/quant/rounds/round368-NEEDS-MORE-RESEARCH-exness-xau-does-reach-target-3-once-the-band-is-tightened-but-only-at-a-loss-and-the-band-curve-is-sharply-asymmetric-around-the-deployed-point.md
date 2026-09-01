# GENERALISATION REFUTED (Round 369)

This file's asymmetry — tightening buys frequency cheaply, widening buys PnL —
**does not hold on `binance BTC`**, the test this file itself named as its next step.

Expressed as a cost ratio `|dPnL%| / |dfreq%|` from the deployed band:

| route | tighten | widen | cheap direction |
|---|---|---|---|
| `exness XAU` (this file) | 0.046 | 2.385 | **tightening, by 52x** |
| `binance BTC` (r369) | **1.052** | **0.561** | **widening, by 1.9x** |

**The ordering inverts.** On `binance BTC` tightening costs +19.16% frequency for
-20.15% PnL — nearly one-for-one, and nearly twice as expensive per unit of frequency
as widening. The per-trade gradient reverses sign too: best at the **tightest** band on
`binance BTC`, best at the **widest** on this route.

This file's measurements stand, and so does its caution that they are one route, one
window, in-sample. What fails is the generalisation. See
`round369-REJECTED-the-band-asymmetry-inverts-between-routes-tightening-is-52x-cheaper-on-exness-xau-and-1-9x-more-expensive-on-binance-btc.md`.

---

# Round 368 — NEEDS-MORE-RESEARCH: `exness XAU` **does** reach Target 3 once the band is tightened — but only at a loss. The band curve is **sharply asymmetric around the deployed point**, and one untested cell buys **+29.6% frequency for an indistinguishable PnL cost**.

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker runs (exactly the
2-container budget), `exness.cfd.XAU.USD` @300, both `candle_count` **57,934**.
Corrects a premise in Round 367; corroborates its conclusion on a second route.

## The registered question

Round 367 bounded break-even frequency on `binance BTC` and closed on the claim
that this was *"the route best placed to break"* the profit/frequency
incompatibility, because it was the only route ever observed above 7.0
trades/week. **That premise was about the settings tested, not about the route.**
`exness XAU` had never been run at a band tighter than the deployed 0.01/0.02.

Pre-registered as a partition, before running — on `exness XAU` @300, hold 36,
band **0.005/0.01**:

- **≥ 7.0 trades/week** → the route *can* reach Target 3, and we learn the PnL
  price of doing so;
- **< 7.0** → Target 3 is unreachable on this route in the tested family.

**Registered answer: YES — 10.43 trades/week.** The premise in Round 367 is
corrected.

## The completed `exness XAU` frontier

All seven cells at `candle_count` 57,934 / 57,933 (same window; the two new runs
are byte-identical in window to each other and to the existing grid):

| band | hold | trades | trades/week | `one_target` PnL | PnL/trade | Target 3 |
|---|---|---|---|---|---|---|
| **0.005/0.01** | 36 | 447 | **10.43** | −2.71794 | −0.006080 | **PASS** |
| **0.0075/0.015** | 36 | 350 | **8.17** | −1.59396 | **−0.004554** | **PASS** |
| 0.01/0.02 *(deployed)* | 36 | 270 | 6.30 | −1.57256 | −0.005824 | fail |
| 0.01/0.02 | 72 | 229 | 5.34 | −1.00705 | −0.004398 | fail |
| 0.02/0.04 | 36 | 186 | 4.34 | −0.40571 | −0.002181 | fail |
| 0.01/0.02 | 144 | 164 | 3.83 | −0.70183 | −0.004279 | fail |
| 0.02/0.04 | 288 | 83 | 1.94 | **+1.17395** | +0.014144 | fail |

**Two cells clear the bar. Both lose money.** The only profitable cell trades
1.94/week.

## Break-even is even further below the bar here than on `binance BTC`

The lowest-frequency losing cell is 3.83/week (−0.70183); the only profitable
cell is 1.94/week. So on this route break-even lies in **(1.94, 3.83)
trades/week — at most 3.83, which is 45.3% below the 7.0 bar.**

| route | break-even bound | shortfall vs 7.0 |
|---|---|---|
| `binance BTC` (r367) | ≤ 5.24/week | 25% |
| **`exness XAU`** (this round) | **≤ 3.83/week** | **45%** |

Round 367's *conclusion* now holds on two routes, and on the second one by a
wider margin. Its *premise* about which route was best placed was wrong; the
answer happens to survive it.

## The finding worth carrying forward: the band curve is asymmetric

Around the deployed point, the two directions are not symmetric at all:

| step from deployed | Δ trades/week | Δ total PnL |
|---|---|---|
| **tighten** 0.01/0.02 → 0.0075/0.015 | **+29.6%** (6.30 → 8.17) | **−1.36%** (−1.57256 → −1.59396) |
| widen 0.01/0.02 → 0.02/0.04 | −31.1% (6.30 → 4.34) | +74.2% (−1.57256 → −0.40571) |

The tightening step is the first cell in this arc where **frequency rose
materially and PnL did not move materially**. The 0.02140 PnL difference is
**4.7 trades' worth** of that cell's own per-trade PnL, on 350 trades — a
difference at the scale of a handful of individual fills, not a regime change.
Per-trade economics actually *improved* 21.8% (−0.005824 → −0.004554).

**On this window the deployed band is not on an efficient frontier in the
tightening direction.** That is a Portfolio-layer knob raising frequency
without a corresponding PnL cost — the shape the arc has been looking for and
has not found in 60+ rounds. It is not a candidate: the cell still **loses
money**, so there is nothing to promote. It is a direction.

## Two generalisations that both fail on this route

Per-trade PnL along the band axis at hold 36 runs
**−0.006080 → −0.004554 → −0.005824 → −0.002181** for bands
0.005 / 0.0075 / 0.01 / 0.02. **Non-monotone.** Round 367 already refuted
"wider is better per trade" using `binance BTC`; it now fails on `exness XAU`
too, in a different way — not by sign reversal but by non-monotonicity. The
+62.5% improvement r364/r367 cited for the 0.01→0.02 step is real and is **one
step of a curve that turns twice.**

Frequency does not order PnL here either: 4.34/week (−0.40571) beats 3.83/week
(−0.70183).

## What is proven, and what is not

Proven:

- `exness XAU` @300 at band 0.005/0.01, hold 36: 447 trades, 10.43/week,
  `one_target` PnL −2.71794. At 0.0075/0.015: 350 trades, 8.17/week, −1.59396.
- Both new runs report `candle_count` 57,934, matching the existing grid cells.
- The seven-cell frontier as tabulated; break-even bounded in (1.94, 3.83).
- The tightening step gives +29.6% trades against a 1.36% total-PnL change.
- Per-trade PnL is non-monotone in band on this route.

Not proven, and deliberately not claimed:

- **That the tightening step is free.** It is one cell, one route, one window,
  **full-window `one_target` — in-sample**. "Indistinguishable" here means
  *small relative to per-trade scale*, which is a magnitude argument, **not a
  significance test**; no test was run and none is available from a single
  deterministic replay.
- **That band 0.0075/0.015 is better than the deployed band.** Its total PnL is
  slightly *worse* and it is still negative. Nothing here recommends a config
  change.
- That break-even is a route constant. Bounded on **this window only**;
  r331/r334/r341 each showed such boundaries moving with the window.
- That the asymmetry has a mechanism. The replay is deterministic (r351), so
  this is input sensitivity rather than sampling noise — but **no mechanism is
  offered**, and the same non-monotonicity that makes the curve interesting
  also makes a two-point slope a weak summary of it.
- That `binance BTC` behaves the same way. Its band curve was measured at
  0.01/0.02 and 0.02/0.04 only; **the tightening direction is untested there**,
  and r367 showed the two routes disagree in sign on the widening direction.

## Named next step

Run the **tightening direction on `binance BTC`** (band 0.0075/0.015 and
0.005/0.01 at hold 36, one window, one round). If the asymmetry reproduces on a
route that disagreed about widening, it is a property of the band knob; if it
does not, it is another route-specific artifact and the arc's negative result
stands unqualified.

Holdout behaviour is unchanged and structural for hold-bearing configurations
(no gate score → promotion condition 1 unmeetable). **The band-only cells in
this round are at the default hold**, so a gate score for them is in principle
obtainable and has not been attempted — noted, not claimed.
