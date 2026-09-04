# Round 436 — REJECTED: cross-route correlation-aware allocation looks like it helps on both disjoint windows raw, but an honest permutation control shows the timing signal does not survive out-of-sample

Classification: **REJECTED**. Two Docker containers per window (4 total, both `exness XAU`
and `bybit XAUT`, matched-window pairs launched together), one SSH tunnel opened and
closed, zero production writes.

## What was tested

Index item 4 (`research/quant/index.md` section 0.5): cross-route correlation-aware
allocation — reduce combined exposure when realized correlation between two routes'
*Portfolio PnL* spikes, to manage simultaneous-drawdown risk. Fully open before this
round (no design survey, no backtest). Chosen over items 2/3 (cross-instrument lead-lag,
volatility-scaled sizing) because, unlike those, this direction is measurable **without**
new engine code: it only needs each route's already-independently-computed daily PnL
series (`--daily-profit-gate --json`'s `daily_results` array), combined as a research-only
post-hoc overlay. `PositionSizing`/`PortfolioRiskLayer` are confirmed unmodified — each
route runs its own independent `DecisionScope`/`PortfolioRiskLayer` instance
(`finance-api/src/trading_api.rs:928-953`, `finance-core/src/execution_decision.rs:15-22`),
so no shared cross-route risk state exists in production today; this round does not touch
that.

Route pair: `exness XAU` and `bybit XAUT`, the same pair Round 342 flagged (price
correlation +0.996, Portfolio PnL correlation +0.287) — the natural test case for a
correlation-timing overlay.

## Method

Pre-specified **before** looking at any result (single configuration, no grid search, to
avoid the cherry-picking this loop forbids):

- Rolling lookback `L = 10` trading days of `return_fraction` (causal: correlation for
  day *t* uses only days `[t-L, t)`, never day *t* itself).
- Threshold `τ = 0.5`: when rolling correlation of the two routes' daily PnL exceeds 0.5,
  scale the combined portfolio's exposure that day to `0.5×`; otherwise `1.0×`.
- Combined portfolio = equal-weight blend of the two routes'
  `return_fraction` (`0.5×(ret_A + ret_B)`), scaled by the day's weight.
- Two **disjoint** windows via `--as-of` (same mechanism validated round 382/391/429-431):
  - Window A (earlier): `--as-of 2026-05-26T18:40:00Z --days 500` — reuses round429's
    exact cutoff for both routes as a matched-window control. Holdouts:
    `exness` 2026-02-16→2026-05-26 (86 days), `bybit` 2026-03-05→2026-05-26 (83 days).
  - Window B (later, "now"): `--days 500`, no `--as-of`. Holdouts:
    `exness` 2026-05-28→2026-09-04 (84 days), `bybit` 2026-05-27→2026-09-04 (101 days).
  - Both routes launched together within each window (round 361's matched-launch lesson).
- Intersection of trading days only (gold CFD has weekend gaps, crypto does not):
  70 shared days in Window A, 84 in Window B.
- **Sanity check against prior evidence**: whole-window (non-rolling) PnL correlation on
  the same data — Window A **+0.4185** (n=70), Window B **+0.2838** (n=84) — closely
  matches Round 342's independently-measured **+0.287**. Confirms the pipeline reproduces
  a previously-validated figure before trusting anything new built on top of it.

## Raw result (before the control)

| Window | Baseline Sharpe | Corr-scaled Sharpe | Baseline Sortino | Corr-scaled Sortino | Baseline max DD | Corr-scaled max DD |
|---|---|---|---|---|---|---|
| A (70d, 24/70 days scaled) | −6.168 | **−4.994** | −6.451 | −5.515 | 0.00011 | 0.00008 |
| B (84d, 20/84 days scaled) | −4.751 | **−4.556** | −5.282 | −5.129 | 0.00011 | 0.00009 |

Both windows show the scaled portfolio less negative on every metric — looked like a
consistent, replicating improvement.

## Why that reading is wrong: the permutation control

Sharpe/Sortino are **scale-invariant under uniform scaling** — multiplying every day's
return by the same constant leaves the ratio unchanged (mean and sd both scale together).
So a flat exposure cut can only shrink magnitude, never move Sharpe; any Sharpe change
here must come from **which specific days** got scaled down, not from the average amount
of exposure removed. That is exactly the question a fixed reduction amount cannot answer,
and exactly what the correlation rule claims to know.

Control: for each window, draw 2000 random equal-sized subsets of eligible
(post-warm-up) days, apply the identical 0.5× scaling to that random subset instead of
the correlation-selected one, and locate the correlation-selected Sharpe within that null
distribution.

- **Window A**: correlation-selected Sharpe (−4.994) beats **97.5%** of random draws
  (random mean −5.957, range [−7.778, −4.479]) — looks like a real, non-random effect.
- **Window B**: correlation-selected Sharpe (−4.556) beats only **61.4%** of random draws
  (random mean −4.669, range [−6.244, −3.400]) — indistinguishable from chance.

One window shows a signal, the disjoint later window does not. This is the same
single-window-then-fails-to-replicate pattern this arc has hit repeatedly (round 331's
band optimum, round 334's frequency coincidence, round 341's gross trough — "a shape
measured on one window is a statement about that window"). By that established standard,
an effect must survive a second disjoint window before being named a feature; this one
did not.

## Why it would not have been actionable even if it had replicated

Both scaled portfolios remain deeply Sharpe-negative (−4.99 best case) — nowhere near the
gate's `minimum_sharpe_ratio: 1.0`. This is structurally the same finding as the whole
hold/band exposure-reduction lever family (rounds 328-367): **cutting exposure shrinks
loss magnitude, it does not create edge.** A correlation-timed cut is mechanically just a
different trigger for the same lever this arc has already shown, six times over, cannot
turn a negative-Sharpe combined book positive. The permutation result adds a second,
independent line of evidence for the same conclusion: even the *timing* of the cut carries
no reliable information here, not just its magnitude.

## What was NOT tested (scope discipline, matching round 434/435's standard)

- No production code changed. No new `PositionSizing` variant, no shared risk-gate touch —
  this was entirely a post-hoc overlay computed outside the engine on already-independent
  per-route outputs.
- Only one `(L, τ, scale)` configuration was run, pre-specified before any result was
  seen, specifically to avoid a multi-configuration search that would make a "PROMOTE"
  reading meaningless (this loop's non-negotiable: no cherry-picking, no p-hacking).
  A different threshold/lookback could in principle behave differently, but the permutation
  method here — not the specific numbers — is the reusable artifact: any future correlation-
  timing claim on this or another route pair should be run through the same random-subset
  control before being trusted, because raw before/after deltas on a scale-invariant ratio
  are otherwise not diagnostic of *timing* value at all.
- Item 3 (volatility-scaled sizing, round 435) and item 2 (cross-instrument lead-lag,
  round 434) remain open per their own design surveys; this round did not touch either.

## What is proven, and what is not

Proven (Docker-executed, two disjoint matched-window pairs, permutation-tested):

- The `exness XAU`/`bybit XAUT` PnL-correlation pipeline reproduces round 342's prior
  correlation figure closely (+0.284 vs +0.287 on the more recent window).
- A single pre-specified correlation-timed 0.5× exposure-reduction rule produces a raw
  Sharpe/Sortino/drawdown improvement in both of two disjoint windows, but that
  improvement is statistically indistinguishable from a random equal-sized day selection
  in the more recent (later, "now") window (61st percentile) and only distinguishable in
  the older window (97.5th percentile) — the effect does not replicate.
- Even the more favorable reading never approaches gate-passing Sharpe.

Not proven, and deliberately not claimed:

- That no correlation-aware allocation design could ever help — only this one
  parameterization, on this one route pair, was tested.
- That a genuine cross-route joint-risk mechanism (as opposed to this backtest-only
  overlay) is architecturally safe to add to production — that would still need the same
  kind of blast-radius survey rounds 434/435 did for their mechanisms, not attempted here
  since the result closes the question before reaching that step.
