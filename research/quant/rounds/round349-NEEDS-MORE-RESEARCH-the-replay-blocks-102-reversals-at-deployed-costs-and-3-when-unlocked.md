# ATTRIBUTED — THE GAIN IS COST, NOT THE UNLOCK (Round 350)

This file's confound is now addressed without the missing flag. Holding `--fee-bps 5`, the
reversal cost crosses the 10 bps ceiling only between slippage 0.5 and 0, so slippage
**2.0 / 1.0 / 0.5** all stay **blocked** (rejections 102 / 96 / 97) and measure the **pure cost
slope with the action space fixed**. Extrapolating them to 5.0 bps predicts **−0.78532**; the
actual unlocked point is **−0.91662**, so **Δ = −0.13130**, inside the registered 0.15 band.

**The 31% gain here is the cost slope, not the unlock — and the unlock's own contribution is
negative.** The reading this file flagged as unsupported ("production's gate costs PnL") is
refuted in sign.

Caveat carried forward: a nearest-pair extrapolation gives Δ = −0.18446, above the threshold, and
the **ungated** ledger moves −0.11237 over the same step, so the effect is **not resolved** — the
defensible statement is a range of roughly −0.13 to −0.18. See `round350-REJECTED-unlocking-reversals-does-not-explain-the-gain-the-cost-slope-does-and-the-gate-if-anything-hurts.md`.

---

# Round 349 — NEEDS-MORE-RESEARCH: the replay's own counters show **102 execution-cost rejections at deployed costs and 3 when the reversal crosses the ceiling** — a 34x drop that confirms Round 348 directly. Unlocking barely changes the trade count but improves realized PnL **31%**, and I cannot separate the gate from the cost.

Classification: **NEEDS-MORE-RESEARCH** — the mechanism is confirmed and quantified, but the
attribution is confounded and the design that would resolve it needs a flag the CLI does not
have. Two bounded Docker sweeps (exactly the 2-container budget), **XAU-first**.

## The gap Round 348 named, and the counter I had overlooked

Round 348 closed with: *"how many reversals the replay would take if unlocked, or what fraction
of decisions are reversals at all… needs a per-trade audit trail, which is audit item L4 and is
not serialized."*

That was too pessimistic. The plain (non-gate) `--json` output carries
**`risk_rejected_counts`** — per-gate rejection tallies straight from the replay's risk layer
(`portfolio_measurement.rs:255`). No per-trade trail is needed to count rejections.

**Pre-registered as a partition:** let **R** = `execution_cost` rejections the replay records on
`exness XAU` @300 at deployed costs.
- **R ≥ 10** → reversals are a material part of the stream and the gate is a first-order shaper
  of the measured strategy;
- **R < 10** → reversals are rare, and the large PnL differences Rounds 344-345 saw must come
  mostly from something else.

## Result — R = 102, and it collapses to 3 on unlocking

`exness XAU`, `--days 300`, deployed band, `minimum_hold_decisions 36`, **55,045 decisions**,
identical window; the only difference is `--slippage-bps`:

| | deployed 5+2 bps<br>(reversal **14.0** → blocked) | `--slippage-bps 0` → 5+0<br>(reversal **10.0** → allowed) |
|---|---|---|
| **`execution_cost` rejections** | **102** | **3** |
| as a share of decisions | 0.19% | 0.01% |
| as a share of executed trades | **36%** | 1% |
| `one_target` trades | 280 | 277 |
| `one_target` realized PnL | **−1.3222** | **−0.9166** |
| `legacy_selected_rule` trades (ungated) | 355 | 338 |
| trade_reduction_fraction | 0.2113 | 0.1805 |
| other gates (`risk`, `halt`, `freshness`, `reconciliation`) | **0** | **0** |

**R = 102. The pre-registered "material" branch fires.** Round 348's mechanism is confirmed from
the replay's own counters: **99 of 102 rejections disappear** when the reversal cost drops from
14.0 to exactly 10.0 bps. Every other gate is at zero in both runs — `execution_cost` is the
only gate that ever fires here.

The right denominator is trades, not decisions: **one blocked reversal for roughly every three
executed trades.**

## Two things this changes about how to read the arc

**The gate is not a frequency lever — it is an action-quality lever.** Unlocking reversals moves
the trade count by only **−1.1%** (280 → 277) while realized PnL improves **31%**
(−1.3222 → −0.9166). Blocking a reversal does not remove a trade; the Portfolio simply does not
act on that decision and takes some other action later. Every band and frequency result in this
arc was read as if trade count were the lever; here the count barely moves and the outcome moves
a third.

**There is a second, gate-free cost-feedback path, and it is measurable.**
`legacy_selected_rule` executes outside the risk layer entirely, and its trade count still moved
**355 → 338 (−4.8%)** between the two runs. That change cannot be the gate. It is the residual
sensitivity Round 345 found and Round 348 could not explain — now isolated to a ledger that the
gate never touches, which is a much cleaner handle on it than anything before.

## What I cannot conclude — and it is the important part

The unlocked arm changed **two things at once**: slippage fell from 2 bps to 0 (cheaper
execution) **and** reversals became permitted (different action space). The 31% PnL improvement
cannot be attributed between them from this pair.

Separating them needs a run with **costs held at deployed and the ceiling raised** — the CLI
exposes `--fee-bps` and `--slippage-bps` but **no flag for `max_total_cost_bps`**, so the clean
experiment cannot be run without a code change. That is the concrete follow-up.

I am specifically **not** claiming that production's execution-cost gate costs 31% of PnL. That
reading is available from the table and it is not supported.

## What is proven, and what is not

Proven:

- `exness XAU` @300, deployed band, hold 36, 55,045 decisions: deployed costs →
  `execution_cost` 102 rejections, `one_target` 280 trades / realized PnL −1.32216,
  `legacy_selected_rule` 355 trades, trade_reduction_fraction 0.21127; `--slippage-bps 0` →
  **3** rejections, 277 trades / **−0.91662**, 338 trades, 0.18047.
- All other risk gates recorded **0** rejections in both runs.
- `risk_rejected_counts` is available in the plain `--json` output and needs no per-trade trail.

Not proven, and deliberately not claimed:

- **Any split of the 31% PnL improvement between "cheaper execution" and "reversals allowed".**
  The arm changes both; the disentangling run needs a `max_total_cost_bps` flag that does not
  exist.
- **That production's gate is costing PnL.** Same confound, and the comparison arm specifies a
  cost production does not have.
- **What the 3 residual rejections at `--slippage-bps 0` are.** A reversal there prices at
  exactly 10.0 bps, which passes a strict `>`. Precision or sizing effects are plausible; **I did
  not investigate**, and I am not guessing.
- That 102 is the number of reversals *attempted*. It is the number of **rejections recorded**;
  whether one decision can be rejected repeatedly across consecutive klines is untested, and if
  it can, 102 over-counts distinct reversal opportunities.
- That these full-window figures compare to the gate rounds. `one_target` covers the whole 300
  days (280 trades); the `--daily-profit-gate` numbers cover the 51-day holdout (42 trades).
- Any promotion. Nothing here changes a configuration, and both arms lose money.
