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

# Round 321 — NEEDS-MORE-RESEARCH: the arc's **one surviving claim holds across 250-900 days** — ten of ten values positive. But the two deepest windows give the two **lowest** edge-to-cost ratios.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered interpretation fired on the
"robust" branch, substantially strengthening the only claim Round 320 left standing.
Two bounded Docker sweeps (exactly the 2-container budget), **XAU-first**.

## The limit Round 320 named

Round 320 demolished most of the cost-ablation arc: `binance BTC`'s raw edge flips sign
between 360 and 500 days, so the "perpetuals are negative" rule is a 360-day artifact,
and `bybit XAUT`'s measures disagree at 2 of 3 windows. It closed with: *"That
`exness XAU` will stay stable outside 250-500 days. Rounds 304 and 312 showed the window
confound grows with depth and **900 days remains untested** on this measure."*

That is the whole remaining question. `exness XAU` is the **only** usable cell left; if
it fails at depth, nothing in the arc survives as a route-level claim. And 900 days is
exactly where Round 312 measured the perturbation confound at **10x** its 260-day size
on `binance BTC` — so this is a hard test, not a formality.

**Pre-registered:** all five windows positive on both measures → robust across
250-900 days; any window with negative `one_target` → nothing in the arc survives;
positive but disagreeing somewhere → the claim narrows to the agreeing windows.

## The result

`exness XAU/USD`, zero execution cost, same day, five windows:

| `--days` | candles | trades | **`one_target`** | gross/trade | **guard-free** | guard-free trades | agree |
|---|---|---|---|---|---|---|---|
| 250 | 48,220 | 304 | **+1.4354** | +0.00472 | **+1.5226** | 380 | yes |
| 360 | 69,681 | 391 | **+1.0997** | +0.00281 | **+1.5993** | 472 | yes |
| 500 | 96,794 | 549 | **+3.0359** | +0.00553 | **+4.1558** | 668 | yes |
| **700** | 135,548 | 645 | **+1.7832** | +0.00276 | **+2.8799** | 759 | **yes** |
| **900** | 174,394 | 715 | **+1.7386** | +0.00243 | **+2.6777** | 830 | **yes** |

**Ten of ten values positive; the two measures agree at all five windows.** The rule
fires: `exness XAU`'s positive raw edge is **robust across 250-900 days** — a 3.6x range
of window lengths, including the depth where the confound is worst.

That is a real result. After Round 320 removed the market-type story, the perpetual-
negative rule and the `bybit XAUT` cell, this is what is left of the arc — and it is now
tested far more widely than anything else in it.

## The magnitude still is not robust, and the deep end is the pessimistic end

| `--days` | trades/week | gross/trade | edge ÷ cost* |
|---|---|---|---|
| 250 | 8.51 | +0.00472 | **50.5%** |
| 360 | 7.60 | +0.00281 | 30.1% |
| 500 | 7.69 | +0.00553 | **59.1%** |
| 700 | 6.45 | +0.00276 | 29.6% |
| **900** | 5.56 | **+0.00243** | **26.0%** |

\* using the 360-day cost-per-trade of 0.00935; an **estimate** at the other four
windows, since the deployed arm was only run at 360.

Per-trade edge spans **2.27x** (0.00243-0.00553), wider than the 1.97x Round 319 saw
over three windows. Round 319's "30-60%" range should now read **26-59%**, requiring a
**41-74%** cost cut.

**The two deepest windows give the two lowest ratios** — 29.6% and 26.0%. There is no
monotone trend across all five (50.5, 30.1, 59.1, 29.6, 26.0), so I am not claiming the
ratio declines with depth. What is fair to say is that the optimistic end of the range
comes from the shallower windows, and the deep end is uniformly pessimistic.

Trade rate also falls with depth (8.51 → 5.56/week). That is consistent with Round 293's
lower deep slices and is **not** a new finding; Rounds 300-312 apply to those rates as
much as to any other.

## What is proven, and what is not

Proven:

- `exness XAU` at zero cost, same day, five windows: `one_target` +1.4354 / +1.0997 /
  +3.0359 / +1.7832 / +1.7386 and guard-free +1.5226 / +1.5993 / +4.1558 / +2.8799 /
  +2.6777 at 250 / 360 / 500 / 700 / 900 days. All positive; measures agree throughout.
- Gross edge per trade 0.00243-0.00553, a 2.27x range.
- Edge-to-cost ratios 26.0-59.1% under the stated cost-per-trade estimate.
- Trade rate 8.51 / 7.60 / 7.69 / 6.45 / 5.56 per week across the five windows.

Not proven, and deliberately not claimed:

- **That any other route has a stable raw-edge sign.** One route. Round 320 showed
  `binance BTC` flips and `bybit XAUT` disagrees at 2 of 3 windows; `exness BTC`,
  `bybit BTC` and `binance XAU` have one window each. This does not generalise and I am
  not extending it.
- **That the ratio declines with depth.** The sequence is not monotone. The deep windows
  being the two lowest is an observation on five points, not a trend.
- That the 26-59% range is measured. Only the 360-day point has its own
  cost-per-trade; the other four reuse it, so those four ratios are estimates.
- Any change to the profitability conclusion. The edge covers cost at **no** window
  measured; the range only says how large the required cut is.
- Any explanation for why `exness XAU` is the stable one. Round 315 recorded that I have
  no working model of where raw edge lives, and nothing here supplies one.
- Any PF, win rate, Sharpe, Sortino, drawdown, streak or SQN. `one_target` reports PnL
  only (Round 84), so this remains a PnL-only result and **not** the joint-objective
  evaluation the loop asks for.
