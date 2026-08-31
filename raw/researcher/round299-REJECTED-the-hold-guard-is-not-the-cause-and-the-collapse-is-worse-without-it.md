# UNRELIABLE — METHOD DEFECT (Round 300)

Every **Portfolio-layer slice rate** in this file comes from **nested differencing**
of `--days` runs, and Round 300 found that method invalid for Portfolio counters: the
Portfolio refits its interval and strategy weights **on every kline** from cumulative
Alpha performance (`portfolio_decision_replay.rs:317`), so two runs of different
length carry **different weights over every bar they share**. A difference between a
540-day and a 360-day run is therefore not "what happened in `[360,540]`".

The weight-free Alpha layer, which *is* cleanly nested (76 of 77 strategies strictly
monotone), shows **no** corresponding variation — 3,773.9 / 3,560.4 / 3,499.5 trades
per week across the same slices, a 4.5% spread against the Portfolio's 7-17x.

Treat this file's Portfolio slice rates as **unreliable pending re-derivation** — not
as disproved; a method defect removes evidence, it does not establish the opposite.
Coverage facts, single-window measurements and live production readings in this file
are unaffected. See
`round300-DATA-ISSUE-portfolio-weights-refit-every-kline-so-nested-differencing-does-not-isolate-a-calendar-period.md`.

---

# Round 299 — REJECTED: the hold guard is **not** the cause of the `exness XAU` near-stoppage. Without the guard the collapse is **17x**, not 7x.

Classification: **REJECTED** — the pre-registered hold-guard hypothesis fails. **Zero
containers, zero SSH**: every number comes from the four JSON reports Rounds 297-298
already produced, plus one local code read. XAU-first.

## The pre-registration

Round 298 left the near-stoppage confirmed and unexplained: `exness XAU`'s
`[360,540]` slice returns **19 trades from 33,672 decisions** where the adjacent
`[540,720]` returns **133 from 32,818** — matched inputs, 7.0x output.

The obvious remaining candidate is the one lever that sits between a decision and a
trade: the **3.00h `minimum_hold_decisions = 36` guard** in
`PortfolioConstructionState::construct`. Round 82 established that
`legacy_selected_rule` runs **the same rule on the same decision stream with the
guard bypassed**, so the guard's contribution is directly measurable.

**Registered before inspecting `legacy_selected_rule`:**

- **H1 (guard is the cause)** — the guard-free measure does **not** collapse:
  `legacy_selected_rule`'s `[360,540]` rate lands within a factor of **2** of its
  `[540,720]` rate.
- **H2 (upstream)** — the guard-free measure collapses by a comparable factor (≥4x),
  which **excludes** the guard and puts the suppression upstream, in the
  decision-to-target stream.

I predicted **H2**, on the grounds that the guard gates reversals against a *fixed*
36-decision threshold and cannot manufacture a 7x swing between two 180-day periods
whose decision cadence is matched.

## The measure is what Round 82 says it is

`trade_reduction_fraction` reproduces `1 − one_target / legacy_selected_rule` exactly
at all four windows, so the two differ by the guard and nothing else:

| window | `one_target` | `legacy_selected_rule` | reported reduction | computed |
|---|---|---|---|---|
| 260d | 254 | 328 | 0.2256 | 0.2256 |
| 360d | 374 | 462 | 0.1905 | 0.1905 |
| 540d | 393 | 471 | 0.1656 | 0.1656 |
| 720d | 526 | 627 | 0.1611 | 0.1611 |

## H1 fails: without the guard, the collapse is worse

| slice | `one_target` /week | **guard-free /week** |
|---|---|---|
| [260,360] | 8.40 | 9.38 |
| **[360,540]** | **0.74** (19 trades) | **0.35** (**9 trades**) |
| [540,720] | 5.17 | 6.07 |
| **ratio [540,720] / [360,540]** | **7.0x** | **17.3x** |

**Nine trades in 180 days with the guard switched off.** The guard is not suppressing
the period — removing it makes the collapse **more than twice as deep**. H1 fails, H2
holds, and **the hold guard is excluded**.

The suppression therefore sits **upstream of Portfolio construction**, in the stream
of targets the strategies produce. That is a real narrowing: Rounds 289-298 had
eliminated data, coverage, decision cadence, σ², trend magnitude, trend efficiency and
measurement drift, all of which are *inputs*; this is the first elimination inside the
**pipeline**.

Note also that the guard's overall bite **shrinks** monotonically with window length
(0.2256 → 0.1905 → 0.1656 → 0.1611). A mechanism whose influence is fading cannot be
the one producing a deep-window anomaly.

## Two method facts established along the way

Both were assumed by Rounds 289-298 and neither had been checked.

**1. The decision stream does not depend on window length.** `main.rs` builds the
Portfolio candidate set with `strategies::production_candidates(&instrument)`, whose
only argument is the instrument identity: the strategy list and every threshold
(`candle_momentum` minimum_move 0.001, `rsi_mean_reversion` 14/30/70, and the
instrument-specific MTF additions) are **hard-coded, not fitted on the train split**.
So a 540-day run is not a re-fitted model; it is the same model over a longer series.
Had the candidates been trained per window, every cumulative difference in this series
would have been comparing two different models, and the whole method would have
collapsed. It does not.

**2. `legacy_grid` must never be differenced — and Round 299 nearly did.** Its
cumulative trade count **decreases** with window length: 3,250 → 5,092 → **4,860** →
6,880. A cumulative counter over nested windows cannot decrease, so the quantity is
not cumulative in the required sense. The reason is visible in the report:
`legacy_grid` carries **`ledgers: 4`** and the capital rule set
`fixed-pct, compounding-pct, fixed-atr, compounding-atr` — constant across all four
windows, so this is not a changing rule set, but **two of the four compound equity**.
A longer window starts earlier, so the compounded equity path differs and later trade
sizes and admissibility differ with it (the geometric decay of Round 90).
`risk_rejected_counts.execution_cost` inherits the same non-monotonicity
(93 → 181 → **160** → 248).

`one_target` and `legacy_selected_rule` each carry `ledgers: 1` under
`fixed_notional` sizing, are equity-path-independent, and are monotone across all four
windows. **Those two are differenceable; the grid and the risk-rejection counters are
not.**

## One caveat this round creates against itself

The hold guard is **stateful** — `decisions_since_target_change` carries forward — so
a 540-day run enters its final 360 days with different guard state than a fresh
360-day run does. Differencing `one_target` therefore carries a state-carryover
confound that a guard-free measure does not. This is the first time I have named it.

It does not weaken the result: the collapse is **larger** on `legacy_selected_rule`,
which has no guard state at all. If anything, the guard's carryover was mildly
*masking* the anomaly.

## What is proven, and what is not

Proven:

- `trade_reduction_fraction` equals `1 − one_target/legacy_selected_rule` at all four
  windows, confirming the two measures differ only by the hold guard.
- Guard-free cumulative counts 328 / 462 / 471 / 627 at 260/360/540/720 days, giving
  slice rates 9.38 / **0.35** / 6.07 per week and a `[540,720]:[360,540]` ratio of
  **17.3x** against `one_target`'s 7.0x.
- `strategies::production_candidates` takes only the instrument identity; its
  strategies and thresholds are hard-coded and independent of `--days`.
- `legacy_grid` trade counts 3,250 / 5,092 / 4,860 / 6,880 — non-monotone in window
  length — with `ledgers: 4` and a constant capital rule set containing two
  equity-compounding rules; `execution_cost` rejections 93 / 181 / 160 / 248, likewise
  non-monotone.

Not proven, and deliberately not claimed:

- **Any cause** for the near-stoppage. The guard is excluded; nothing is established
  in its place, and I am not proposing a mechanism. Rounds 279-284 remain the standing
  reason, and this round is exactly the shape of evidence that makes speculation
  tempting.
- That "upstream of Portfolio construction" identifies a component. It excludes one
  named guard; the target stream, the role-score gates, the cost gate and the
  strategies themselves are all still inside the surviving region and none was tested.
- That the guard is irrelevant generally. It removes 16-23% of trades at every window
  measured; what is rejected is the guard as the explanation for **this slice**.
- That `one_target`'s differencing is confound-free. The state-carryover caveat named
  above stands and was not quantified.
- Any Target 3 verdict change. Historical slices only.
