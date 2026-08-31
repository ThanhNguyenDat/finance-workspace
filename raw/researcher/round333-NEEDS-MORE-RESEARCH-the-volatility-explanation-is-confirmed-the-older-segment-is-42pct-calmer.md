# Round 333 — NEEDS-MORE-RESEARCH: the volatility explanation is **confirmed**. The 500-900 day segment is **42% calmer**, and the same band's trade-rate ratio (1.31x) matches the volatility ratio (1.19x) to **10%**.

Classification: **NEEDS-MORE-RESEARCH** — a named mechanism is tested and confirmed on
independent data; its magnitude is only partly pinned down. **Zero containers**; one
narrow read-only Timescale query. **XAU-first**.

## The gap Round 332 named

Round 332 found the optimal *frequency* essentially identical at both windows (6.82/week
at 500 days, 6.85/week at 900) while the band that produced it differed, and offered a
reason with an explicit disclaimer: *"A plausible reason is that the market's volatility
over the two spans differs, so the same fractional band produces a different trade rate —
but **I have not tested that** and am not asserting it."*

That is directly testable with no containers. A fractional band of fixed width triggers
**less** often in a calmer market, so to reach the same trade rate over a calmer window
you need a **tighter** band — which is exactly the observed direction (0.02 at 500 days,
0.01 at 900).

**Pre-registered:** days 500-900 ago have **lower** 5m realized volatility than days
0-500 ago on `exness XAU`. Refuted if higher or equal.

## The measurement

Read-only Timescale, 5m log returns, `exness.cfd.XAU.USD`:

| segment | bars | **vol % per 5m** | mean \|return\| % |
|---|---|---|---|
| recent 0-500 days | 96,738 | **0.09597** | 0.05885 |
| **older 500-900 days** | 77,607 | **0.05590** | 0.03710 |
| whole 0-900 days | 174,345 | 0.08063 | 0.04917 |

**The older segment is 42% less volatile.** The prediction is confirmed. And because the
900-day window contains the 500-day one plus that calmer stretch, its blended volatility
is **16% lower** than the 500-day window's.

## The quantitative check

The sharper test is not the sign but whether the magnitude works. The **deployed** band
0.01/0.02 was run at both windows, so it gives a controlled comparison:

| | 500 days | 900 days | ratio |
|---|---|---|---|
| trade rate (deployed band) | 8.95/week | 6.85/week | **1.307x** |
| realized volatility | 0.09597 | 0.08063 | **1.190x** |

**The two ratios agree to 9.8%.** The same band, run over a 16%-calmer window, produced
31% fewer trades — the direction and roughly the magnitude both match a first-passage
reading, where a fixed fractional barrier is hit less often when moves are smaller.

That is the mechanism Round 332 guessed at, now measured on an independent data source
(Timescale prices) rather than inferred from the backtest's own output.

## What it does not explain

The **optimal band** ratio is 0.02 / 0.01 = **2.00x**, against a volatility ratio of
**1.19x**. Those do not match.

But the grid is coarse — 0.005 / 0.0075 / 0.01 / 0.02 / 0.04, with adjacent points a
factor of 2 apart at the top end — so **2.00x is a grid-resolution upper bound, not a
measured shift**. Nothing between 0.01 and 0.02 was run at either window, and the true
optima could sit much closer together. I am **not** treating this as a discrepancy, and I
am **not** claiming the band scales with volatility.

## What this supports, carefully

It supplies a coherent reading of Round 332's coincidence: if the optimal **frequency** is
a property of the route and the band is only the knob that reaches it, then the band must
move with volatility while the frequency stays put. That is what both windows show.

**Two windows is still two windows.** One route, two spans, one confirmed directional
prediction. It is a mechanism with supporting evidence, not an established law, and
Rounds 296 and 298 both previously rejected volatility as an explanation for *other*
quantities on this same route — so this is a narrow win for volatility, not a general one.

## What is proven, and what is not

Proven:

- `exness XAU` 5m realized volatility: 0.09597% over days 0-500, **0.05590%** over days
  500-900, 0.08063% over days 0-900 (96,738 / 77,607 / 174,345 bars).
- The older segment is 41.8% less volatile than the recent one; the 900-day blend is
  16.0% less volatile than the 500-day window.
- The deployed band's trade rate ratio between the two windows (1.307x) and their
  volatility ratio (1.190x) agree to 9.8%.

Not proven, and deliberately not claimed:

- **That the optimal band scales with volatility.** The 2.00x optimal-band ratio is a
  grid artifact; nothing between 0.01 and 0.02 was tested.
- That ~6.8 trades/week is an optimal frequency in any general sense. Unchanged from
  Round 332 — two windows, one route, coarse grid.
- That volatility explains anything else on this route. Rounds 296 and 298 rejected it
  for within-route rate variation and for the `[360,540]` near-stoppage; this round is
  about the **band-to-frequency mapping only**.
- Any first-passage model. The 1.31x-against-1.19x agreement is consistent with one; I
  fitted nothing and tested no functional form.
- Anything about other routes or about profitability. No configuration measured on this
  route at either window is profitable, and that is untouched here.
