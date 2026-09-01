# GATE VERDICT QUALIFIED (Round 336)

Gate results in this file come from `exness XAU`, where **all seven non-5m intervals fail
`input_continuity` at both 500 and 900 days**. `minimum_holdout_days` passes at 900 days
(151 observed days) but the continuity checks do not, so **no configuration on this route
can pass the gate at any window measured**.

The band comparisons and relative rankings here are unaffected — a structural check failing
identically across every configuration cannot reorder them. What does not hold is reading
any run in this file as a **gate verdict**. See `round336-DATA-ISSUE-exness-xau-can-never-pass-the-gate-at-any-window-and-binance-btc-is-the-first-gate-eligible-route-measured.md`.

---

# Round 328 — REJECTED: raising trade frequency **does not create edge — it multiplies cost**. Gross PnL is flat across a **7.3x** frequency range while net loss rises **142x**. A within-route controlled test.

Classification: **REJECTED** — raising trade frequency as a route to meeting Target 3 is
closed. My pre-registered ordering held on both axes. Two bounded Docker sweeps (exactly
the 2-container budget), **XAU-first**.

## Turning a correlation into a controlled test

Rounds 326-327 found, across routes, that the busiest routes have the worst Sharpe —
ρ = **−0.900**, exact p = 0.083 on five routes that differ in instrument, broker and
market type. That is a correlation over confounded units, and I said so.

The clean version is **within one route**: change only the frequency lever, hold the
route, the window and the holdout fixed, and score on the joint objective. Round 274
established the ATR protective band as a frequency lever (2.43x trades on `exness XAU`);
a **wider** fractional band should move frequency the other way.

**Pre-registered:** if the tension is real within a route, Sharpe orders **inversely**
with trades/week — wide > deployed > ATR in Sharpe, and wide < deployed < ATR in
frequency. Refuted if either ordering is violated.

## The ladder

`exness XAU/USD`, `--days 500`, deployed costs, **identical holdout**
2026-05-22 → 2026-08-28 (84 observed days). Only the protective band changes.

| band | trades | tr/wk | pos-day | streak | Sortino | **Sharpe** | cost÷gross | **gross** | net |
|---|---|---|---|---|---|---|---|---|---|
| **wide fractional 0.02/0.04** | 96 | **6.82** | 0.417 | 5 | −0.155 | **−0.096** | **1.05** | **+0.6067** | **−0.0301** |
| deployed fractional 0.01/0.02 | 126 | 8.95 | 0.429 | 4 | −1.152 | −0.814 | 1.38 | +0.6000 | −0.2283 |
| **ATR 1.5/3.0** | 703 | **49.94** | **0.095** | **16** | −14.802 | **−23.225** | **7.25** | **+0.6839** | **−4.2751** |

**Both orderings hold. The prediction is confirmed.**

## The mechanism, stated plainly

| quantity | wide → ATR |
|---|---|
| trades per week | **7.32x** (6.82 → 49.94) |
| **gross PnL before costs** | **1.13x** (+0.6067 → +0.6839) — **+12.7%** |
| cost ÷ gross | **6.90x** (1.05 → 7.25) |
| **net loss** | **142x** (−0.0301 → −4.2751) |

**Gross edge is essentially flat across a 7.3x frequency range.** The lever does not
find more profitable opportunities; it finds more *trades*, each carrying the same
round-trip cost. Cost scales with count, gross does not, and the net collapses.

This explains Round 274's earlier finding (2.43x frequency for 2.27x loss, per-trade PnL
almost unchanged) and converts Rounds 326-327's cross-route correlation into a
**within-route, single-holdout, single-variable** result.

## Target 1 and Target 3 are in direct conflict on this route

| band | trades/week | Target 3 | net | Sharpe |
|---|---|---|---|---|
| wide | **6.82** | **misses the 7/week bar by 2.6%** | **−0.0301** | **−0.096** |
| deployed | 8.95 | meets it | −0.2283 | −0.814 |

**The configuration nearest break-even is the one that fails Target 3.** Meeting the bar
costs **7.6x the net loss** and **8.5x the Sharpe** on this holdout. That is not a
framing choice; it is what the two configurations measure.

## Why this is not a promotion

The wide band is tempting — near break-even, better on every risk metric — and it is
**not** a promotable candidate:

- **It still fails the gate.** Sharpe −0.096 against a required +1.0, positive-day ratio
  0.417 against 0.55, cost÷gross 1.05 against 0.5. It loses less; it does not pass.
- **One route, one window, one holdout.** Rounds 318-321 established that route-level
  results are window-sensitive, and nothing here has been re-measured at another window.
- **It sacrifices a stated objective.** Adopting it would trade Target 3 for a smaller
  Target 1 loss, which is a decision about priorities, not a research finding.

The promotion gate's first condition — defensible evidence of an **improvement** — is
not met by a configuration that merely loses less while failing every threshold. Kept at
**research-only**, as the gate requires.

## What is proven, and what is not

Proven:

- `exness XAU` at `--days 500`, identical holdout 2026-05-22 → 2026-08-28: wide
  fractional 96 trades / 6.82 per week / Sharpe −0.096 / net −0.0301; deployed 126 /
  8.95 / −0.814 / −0.2283; ATR 703 / 49.94 / −23.225 / −4.2751.
- `gross_pnl_before_costs` +0.6067, +0.6000, +0.6839 across a 7.32x frequency range —
  a spread of 12.7%.
- cost ÷ gross 1.05, 1.38, 7.25; maximum negative-day streak 5, 4, **16**; positive-day
  ratio 0.417, 0.429, **0.095**.
- All three configurations fail the gate.

Not proven, and deliberately not claimed:

- **That this generalises to other routes.** One route. The five other routes were not
  laddered, and Rounds 320-321 showed route-level results moving with the window.
- That the wide band would hold up at another window. It was measured at `--days 500`
  only; Round 322 showed the deployed arm's behaviour changing materially with depth.
- That the wide band is an improvement. It fails the gate on three checks and drops
  below Target 3. **No promotion is proposed.**
- That gross edge is *exactly* constant. It moved 12.7% across the range — small against
  a 7.32x frequency change, not zero, and I have not tested whether that 12.7% is
  meaningful.
- Any causal claim about the cross-route ρ = −0.900. This round supports its direction
  within one route; it does not license reading the cross-route correlation as causal.
