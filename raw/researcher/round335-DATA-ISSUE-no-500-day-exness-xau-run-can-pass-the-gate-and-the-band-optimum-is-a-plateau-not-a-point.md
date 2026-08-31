# CAVEAT RESOLVED (Round 336)

This file's open caveat — *"whether the seven interval-continuity checks also fail at 900
days is **untested**"* — is now closed: **they do**. At `--days 900` `exness XAU` passes
`minimum_holdout_days` (151 observed days) but still fails `input_continuity` on all seven
non-5m intervals, and harder (15m: 628 unverified gaps over 27,659 candles). **No gate
verdict on this route at any measured window is pass-eligible.**

The failure is **route-specific, not universal**: `binance BTC` at 500 days reports **zero
gaps of any kind on all eight intervals** and no continuity failure. See `round336-DATA-ISSUE-exness-xau-can-never-pass-the-gate-at-any-window-and-binance-btc-is-the-first-gate-eligible-route-measured.md`.

---

# Round 335 — DATA-ISSUE: **no** `exness XAU` run at `--days 500` can pass the gate, for two reasons that have nothing to do with trading performance. And the band optimum is a **plateau**, not a point — with the volatility-predicted 0.0119 inside it.

Classification: **DATA-ISSUE** — every 500-day gate verdict in Rounds 330 and 334 is
structurally ineligible to pass, so those rounds produced valid **relative rankings** and
invalid **gate verdicts**. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**.

## The question this round set out to answer

Round 334 left one thing explicitly open: *"only two intermediate points were tested and
the **lower** one won, so the true optimum could sit at or below 0.0119"*, and *"the exact
ranking of the three middle points is **not** established."*

**Pre-registered before running:** the nets at 0.011/0.022 and 0.0115/0.023 lie strictly
between 0.01/0.02's −0.2283 and 0.0125/0.025's −0.0121 — i.e. the climb from 0.01 to
0.0125 is smooth and monotone. **Refuted** if either lands outside that bracket, which
would show the fine ordering is noise-dominated.

## What the gate output actually says

Both runs failed, and the failure list is longer than the one I have been reporting:

```
minimum_holdout_days, positive_day_ratio, median_daily_pnl, sortino_ratio,
sharpe_ratio, cost_to_gross_pnl_ratio,
input_continuity_failed: 12h, 15m, 1d, 1h, 2h, 30m, 4h
```

Two of these are **not performance failures**:

1. **`minimum_holdout_days`.** The holdout spans 98.5 calendar days but only
   **84 observed days** against a threshold of 90. `exness XAU` is a CFD — weekends are
   closed — so a 500-day window structurally cannot supply 90 observed holdout days. At
   `--days 900` the holdout reaches 151 observed days (Round 331) and this check passes.
2. **`input_continuity_failed` on all seven non-5m intervals.** The gap metadata is
   unambiguous: 5m has **356 verified session gaps and 0 unverified**, while every higher
   timeframe carries hundreds of **unverified** gaps — 15m alone reports 344 unverified
   gaps / 15,154 candles, 1h 342 / 3,782, 30m 342 / 7,572. The Portfolio requires all
   eight intervals, so the gate flags each one.

**Consequence: no configuration of any kind can pass the gate on this route at 500 days.**
Rounds 330 and 334 both said the best configuration "still fails the gate" and attributed
it to Sharpe, positive-day ratio and cost÷gross. That attribution was **incomplete** — two
structural checks were failing underneath, and I did not report them. The performance
comparisons in those rounds remain valid **as relative rankings on a common window**; their
gate verdicts do not mean what I implied.

I am recording this against my own reporting, not against the tool: the failure list was in
the output all along and I quoted only the part that fit the story I was telling.

## The pre-registered test: the bracket holds, and the optimum is flat

| band | trades | tr/wk | gross | cost drag | **net** | Sharpe | Sortino | pos-day | cost÷gross |
|---|---|---|---|---|---|---|---|---|---|
| 0.01 / 0.02 (deployed) | 126 | 8.95 | +0.6000 | — | −0.2283 | −0.814 | −1.152 | 0.429 | 1.38 |
| **0.011 / 0.022** | 115 | 8.17 | **+0.7559** | 0.8100 | −0.0541 | −0.193 | −0.308 | 0.393 | 1.072 |
| **0.0115 / 0.023** | 110 | 7.82 | +0.7201 | 0.7324 | **−0.0122** | **−0.045** | −0.072 | 0.405 | **1.017** |
| 0.0125 / 0.025 | 108 | 7.67 | +0.7121 | — | **−0.0121** | −0.041 | −0.066 | 0.405 | 1.02 |
| 0.015 / 0.03 | 107 | 7.60 | +0.6499 | — | −0.0724 | −0.230 | −0.361 | 0.417 | 1.11 |
| 0.02 / 0.04 | 96 | 6.82 | +0.6067 | — | −0.0301 | −0.096 | −0.155 | 0.417 | 1.05 |
| 0.04 / 0.08 | 86 | 6.11 | +0.4460 | — | −0.1396 | −0.445 | −0.725 | 0.429 | 1.31 |

**The bracket prediction holds.** Net climbs 0.01 → 0.011 → 0.0115 as
−0.2283 → −0.0541 → −0.0122, monotone, and the steps are **large** — 0.174 then 0.042,
one to two orders of magnitude above the 0.01-scale gaps Round 334 worried might be noise.
**The rising side of the curve is real signal, not configuration-to-configuration jitter.**

**And the top is a plateau.** 0.0115 (−0.01225) and 0.0125 (−0.0121) are the same number to
within 1.2%, with matching Sharpe (−0.045 / −0.041), matching positive-day ratio (0.405),
matching streak (4) and matching cost÷gross (1.017 / 1.02). The optimum is a **flat region
spanning at least 0.0115-0.0125**, not the point Round 334 reported.

**The volatility-scaled prediction of 0.0119 falls inside that plateau.** Round 334 could
only say the argument "located the region"; the region is now measured, and the prediction
is inside it rather than merely near a single best point.

## Two structural facts the seven-point grid now supports

**Frequency is perfectly monotone in band width** — 8.95, 8.17, 7.82, 7.67, 7.60, 6.82,
6.11 across all seven points, no exceptions. The band-to-frequency map is clean even where
the net curve is not, which is why frequency is the right coordinate for reading this lever
(Round 332's rule, reconfirmed on a finer grid).

**Gross and net peak at different bands.** Gross is highest at **0.011** (+0.7559) and falls
away on both sides; cost drag falls monotonically with trade count (0.8100 → 0.7324). Net
therefore peaks **wider** than gross, at 0.0115-0.0125, where the shrinking cost has caught
up with the shrinking gross. The lever's optimum is set by that crossover, not by an edge
maximum.

**It is still a loss.** The best net on the plateau is −0.0121 with cost÷gross > 1.0 —
execution cost still exceeds gross edge at every point on this seven-band grid.

## What is proven, and what is not

Proven:

- `exness XAU`, `--days 500`, identical holdout (2026-05-22 → 2026-08-28, 19,346 candles):
  0.011/0.022 → 115 trades / 8.17 per week / gross +0.7559 / cost 0.8100 / net −0.05409 /
  Sharpe −0.193 / Sortino −0.308; 0.0115/0.023 → 110 / 7.82 / +0.7201 / 0.7324 / −0.01225 /
  −0.0449 / −0.0716.
- The gate's own failure list on both runs includes `minimum_holdout_days` (84 observed days
  against 90) and `input_continuity_failed` on all seven non-5m intervals.
- Gap metadata: 5m = 356 verified session gaps, 0 unverified; 15m = 344 unverified gaps
  across 15,154 candles; 1h = 342 / 3,782; 30m = 342 / 7,572.
- Net is monotone increasing across 0.01 → 0.011 → 0.0115 and flat between 0.0115 and
  0.0125; trades per week is monotone decreasing across all seven bands.

Not proven, and deliberately not claimed:

- **That the higher-timeframe gaps are a data defect.** `unverified` means the gap was not
  confirmed as a session gap, not that data is missing. On a CFD with closed weekends most
  of these are very likely genuine session gaps that the metadata has not verified at those
  intervals. **I did not investigate the classifier**, and I am not asserting either
  interpretation.
- **That the 900-day runs are free of the continuity failure.** Only `minimum_holdout_days`
  is known to differ there (151 observed days). Whether the seven interval-continuity checks
  also fail at 900 days is **untested** — if they do, no gate verdict on this route means
  what it appears to.
- That 0.0115-0.0125 contains the true optimum. Nothing was run between 0.011 and 0.0115, or
  between 0.0125 and 0.015; the plateau's edges are where the grid stops, not where the
  curve turns.
- **The ranking on the falling side.** 0.015 (−0.0724) is still worse than both neighbours.
  This round tested only the rising side; the non-monotonicity Round 334 flagged is
  untouched and remains unexplained.
- Any promotion. Every point on this grid loses money with cost exceeding gross edge, and no
  500-day run is eligible to pass the gate in the first place.
