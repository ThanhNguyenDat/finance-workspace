# RATIO RECOMPUTED FROM MEASURED ARMS (Round 322)

The edge-to-cost ratios here reuse the 360-day cost-per-trade at the other windows.
Round 322 measured the deployed arm at 700 and 900 days: the true ratios are **30.1%,
43.7% and 24.3%** at 360 / 700 / 900 — the **700-day estimate was wrong by 32%**, and
the measured points need a **56-76%** cost cut.

More importantly, `cost/trade` is **not constant** (0.00632-0.01002, a 1.58x range)
because the deployed arm trades **4.3% / 21.1% / 43.5%** less than the zero-cost arm as
the window deepens — so `edge ÷ cost` absorbs a **trade-selection change**, not only a
cost. The 59.1% figure at 500 days remains an unverified estimate. See
`round322-DATA-ISSUE-the-edge-to-cost-ratio-is-contaminated-by-trade-selection-that-grows-with-depth.md`.

---

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

# WINDOW-SCOPED, AND ONE CELL FLIPS (Round 320)

`binance BTC`'s raw edge is **−0.4432 at 360 days and +1.7176 at 500 days**, with both
measures agreeing at *both* windows. So this file's conclusions hold at 360 days and
**one of its cells has the opposite sign at 500**. Any statement here of the form
"perpetuals are negative" or "the cost-driven diagnosis does not generalise" is
**360-day specific**.

Round 320 also shows **measure-agreement does not imply window-stability** — they are
independent properties. Of three routes tested across windows, only `exness XAU` is
stable in both sign and measure. See
`round320-REJECTED-binance-btc-raw-edge-flips-sign-at-500-days-so-the-perpetual-negative-rule-is-a-360-day-artifact.md`.

---

# Round 319 — NEEDS-MORE-RESEARCH: on the strongest cell the **sign is window-robust** — positive at 250, 360 and 500 days on both measures. The **magnitude is not**: per-trade edge swings **2.0x**, and with it the headline edge-to-cost ratio.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered interpretation fired on the
"window-robust" branch, which **partially un-scopes** Round 318's blanket caution. Two
bounded Docker sweeps (exactly the 2-container budget), **XAU-first**.

## Why this test

Round 318 found that `bybit XAUT`'s two measures agree positive at 360 days and
disagree at 250, concluded that raw-edge sign is **not** a window-independent property,
and scoped every conclusion in Rounds 313-317 to the 360-day window.

That caution is only useful if I know **how broad** it is. If even the strongest cell
flips, the whole cost-ablation arc describes windows rather than routes. If only the
marginal cells move, the arc's main claim survives and the caution belongs on the
near-zero cells.

`exness XAU` is the test: the largest positive cell, both measures agreeing, and the
XAU priority route.

**Pre-registered:**

| outcome | conclusion |
|---|---|
| positive on both measures at all three windows | the positive edge is **window-robust** across 250-500 days |
| `one_target` flips sign at any window | even the strongest cell is window-dependent; the arc describes windows, not routes |
| `one_target` stays positive but measures disagree somewhere | **partial** stability |

## The result

`exness XAU/USD`, zero execution cost, same day:

| `--days` | candles | trades | **`one_target`** | pnl/trade | guard-free | guard-free trades | agree |
|---|---|---|---|---|---|---|---|
| **250** | 48,220 | 304 | **+1.4354** | **+0.00472** | +1.5226 | 380 | **yes** |
| 360 | 69,681 | 391 | **+1.0997** | **+0.00281** | +1.5993 | 472 | **yes** |
| **500** | 96,794 | 549 | **+3.0359** | **+0.00553** | +4.1558 | 668 | **yes** |

**Positive on both measures at all three windows.** The rule fires: on this route the
sign is **window-robust across 250-500 days**.

## Where the instability actually lives

Every zero-cost cell measured so far, sorted by whether the two measures agree:

| \|`one_target`\| | cells | disagreements |
|---|---|---|
| **≥ 1.0** | 3 (all `exness XAU`) | **0** |
| **< 1.0** | 6 | **2** (`exness BTC` @360, `bybit XAUT` @250) |

So **large magnitude has always come with agreement**, while small magnitude is a coin
flip — four of the six small cells agree and two do not. This refines, without
rescuing, the hypothesis Round 318 offered and then contradicted: magnitude appears
**sufficient** for stability, not necessary. With only three cells above the line that
is a weak observation, and I am recording it as one.

**So Round 318's scoping was right for the marginal cells and too broad for this one.**
`exness XAU`'s positive raw edge — the single strongest claim of Rounds 313-317 — is
not a 360-day artifact.

## But the magnitude moves a great deal, and that matters

Per-trade gross edge: **+0.00472 / +0.00281 / +0.00553** at 250 / 360 / 500 days — a
**1.97x range**, and 360 days happens to be the *lowest* of the three.

Round 313's headline was that the edge is worth **30.1%** of round-trip cost, needing a
**70% cost cut** to break even. Re-deriving that at each window, using the 360-day
cost-per-trade of 0.00935 (an **estimate** elsewhere — the deployed arm was not re-run
at 250 or 500):

| window | edge ÷ cost | cost cut needed |
|---|---|---|
| 250d | **50.5%** | 50% |
| 360d | **30.1%** | 70% |
| 500d | **59.1%** | 41% |

**The number Round 313 quoted is the most pessimistic of the three**, and the honest
range is roughly **30-60%**, requiring a **41-70%** cost cut. That is a materially
different picture from a single figure, and it changes the conclusion's tone without
changing its direction: the edge still does not cover costs at any window measured.

## What is proven, and what is not

Proven:

- `exness XAU` at zero cost, same day: 250d → 304 trades / +1.4354 / guard-free
  +1.5226; 360d → 391 / +1.0997 / +1.5993; 500d → 549 / +3.0359 / +4.1558. All six
  values positive.
- Per-trade gross edge +0.00472, +0.00281, +0.00553 — a 1.97x range across the three
  windows.
- Across all nine zero-cost cells measured, 0 of 3 with `|one_target| ≥ 1.0` disagree
  between measures, against 2 of 6 below 1.0.

Not proven, and deliberately not claimed:

- **That sign stability generalises to other routes.** One route, three windows. The
  routes that actually flipped (`bybit XAUT`) and disagreed (`exness BTC`) were not
  re-tested here, and Round 318's caution stands for them.
- That magnitude *causes* agreement. Three cells above the 1.0 line, all the same
  route — this is a pattern in a small sample, not a rule, and Round 318 already had one
  magnitude hypothesis contradicted.
- That the sign is robust outside 250-500 days. Rounds 304 and 312 showed the window
  confound grows with depth; 900 days was not tested here.
- **That the 30-60% range is measured.** Only the 360-day point has its own
  cost-per-trade; the other two reuse it. The deployed arm at 250 and 500 was not run,
  so those ratios are estimates and the range is indicative.
- Any change to the profitability conclusion. The edge fails to cover cost at every
  window measured; what moves is how large the required cost cut is.
- Any PF, win rate, Sharpe, Sortino, drawdown or streak. Unchanged since Round 313.
