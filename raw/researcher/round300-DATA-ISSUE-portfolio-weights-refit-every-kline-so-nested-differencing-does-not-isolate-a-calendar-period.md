# QUALIFIED (Round 302)

The blanket unreliability above is **route-dependent in magnitude**. On `binance BTC`
the defect is small: a one-day perturbation moves the Target 3 rate by **+1.04%**, and
Round 292's recorded slices imply a 260-day cumulative of 350.1 against an independent
**350** measured in Round 302 — an exact reproduction. On `exness XAU` it is severe: a
**negative** one-day response, a 5.5% perturbation spread, and a **1.87x** swing in the
single-window rate between 180 and 360 days.

The mechanism is instrument-independent; its magnitude is not. Differenced slices stay
unestablished everywhere, but `binance BTC`'s single-window numbers are corroborated
rather than merely unreliable. See
`round302-NEEDS-MORE-RESEARCH-the-defect-is-route-dependent-binance-btc-is-robust-and-exness-xau-is-not.md`.

---

# Round 300 — DATA-ISSUE: the Portfolio refits its weights **on every kline** from cumulative performance, so nested differencing does not isolate a calendar period. The Alpha layer says the market was normal.

Classification: **DATA-ISSUE** — a defect in the measurement method that Rounds
289-299 are built on, found in code and corroborated numerically. **Zero containers,
zero SSH**: two local code reads plus the four JSON reports Rounds 297-298 already
produced. XAU-first.

This round retracts a claim I made one round ago and undermines a method I have run
for eleven rounds. Both are stated plainly below.

## Part 1 — Correcting Round 299 at the code level

Round 299 concluded, as one of two "method facts", that **the decision stream does not
depend on window length**, reasoning from `strategies::production_candidates(&instrument)`
taking only the instrument identity.

The candidate set is indeed static. **The weights over it are not.**
`crates/finance-research/src/portfolio_decision_replay.rs:317`, inside the per-kline
replay loop:

```rust
evidence.reweight_from_alpha_performance(&alpha_performance(&ledgers));
```

This runs **on every kline**, and `alpha_performance(&ledgers)` is the **cumulative**
performance of the Alpha ledgers since the window start.
`TradingPolicy::reweight_from_alpha_performance` (`finance-core/src/trading_modes.rs:517-556`)
recomputes both `interval_weights` and `strategy_weights` from it.

So the Portfolio's weights at any calendar bar are a function of **everything that
came before it in that run**. A 540-day run and a 360-day run hold **different weights
at every bar they share**. Round 299's generalisation from "the candidates are static"
to "the decision stream is window-independent" was wrong, and I am withdrawing it.

This is the "self-reinforcing weight loop" Round 263 suspected without locating. It is
now located.

## Part 2 — The numbers already said so, and I mis-explained them

Under a path-independent decision stream, every cumulative counter over nested windows
must be non-decreasing. Two are not:

| counter | 260d | 360d | 540d | 720d |
|---|---|---|---|---|
| `legacy_grid.trades` | 3,250 | 5,092 | **4,860** | 6,880 |
| `risk_rejected_counts.execution_cost` | 93 | 181 | **160** | 248 |

Round 299 attributed the grid's decrease to its two equity-**compounding** capital
rules. That explanation does not cover the second row: **`execution_cost` is a gate
count, with no equity sizing in it at all.** Weight-path dependence covers both. I am
correcting my own attribution: compounding may contribute, but the general cause is
Part 1.

## Part 3 — The control that settles it: the Alpha layer is weight-free

`strategy_scores` reports each Alpha strategy's own ledger, simulated independently of
Portfolio weights. Summing `splits[*].trades` per strategy gives a **weight-free
cumulative counter** over exactly the same windows.

It behaves as a nested counter must:

- **76 of 77** 5m strategies are strictly monotone across 260/360/540/720 days.
- The single exception (`candle_reversion_60bps`, 76 / 81 / 86 / **84**) loses **2
  trades out of 379,212**.
- Totals: 143,757 / 197,670 / 289,224 / 379,212 — strictly monotone.

And it says the market was ordinary:

| slice | **Alpha /week (weight-free)** | Portfolio `one_target` /week | guard-free /week |
|---|---|---|---|
| [260,360] | **3,773.9** | 8.40 | 9.38 |
| **[360,540]** | **3,560.4** | **0.74** | **0.35** |
| [540,720] | **3,499.5** | 5.17 | 6.07 |

**The Alpha rates vary by at most 4.5% around their mean. The Portfolio rates over the
identical slices vary by 7x, and 17x without the hold guard.**

Seventy-seven strategies generated a completely normal amount of activity in
`[360,540]` — 3,560 trades a week against 3,774 and 3,500 in the neighbouring slices.
Whatever the near-stoppage is, **it is not the market going quiet**, and it appears
only in the measure that is path-dependent.

## What this costs

**The nested-differencing method is not valid for Portfolio-layer counters.** A
difference between a 540-day and a 360-day run is not "what happened in `[360,540]`";
it is the difference between two runs carrying different weight trajectories over
every bar, including the 360 days they share.

Treat as **unreliable pending re-derivation** every Portfolio slice rate in Rounds
289-299, and everything built on them: the "window effect is non-stationarity"
framing, the "trend versus swing" classification, the majors' two-year trend, the
fleet spreads, and this round's own subject, the `exness XAU` near-stoppage. The
rounds that *rejected* explanations for those numbers — warm-up (295), volatility
(296), depth-dependence (297), σ² (298) — were testing a quantity that may not measure
a calendar period. Their rejections are not thereby *wrong*; they are aimed at a
target I can no longer vouch for.

## What survives

- **Round 299's main result.** It compares `one_target` against
  `legacy_selected_rule` **within the same run**, where the reduction fraction is
  16-23% at every window. The hold guard cannot produce a 7x or 17x effect whatever
  the differencing does, so "the guard is not the cause" stands on its own.
- **Round 296's verification** that `one_target` measures the whole `--days` window.
  That is about a single run and is unaffected.
- **Live production measurements** (Rounds 207, 259-260). Those count real closed
  trades in Redis; no replay, no weights, no differencing.
- **Alpha-layer results**, which are weight-free by construction.
- Every **coverage** fact: instrument history depths, bars/day, session-gap metadata.

## The tool limitation this exposes

There is no way to get a per-period Portfolio trade count that is comparable across
periods:

- differencing nested runs is invalid, for the reason above;
- running equal-length windows with different end dates would work, but the CLI has
  **no as-of/end-date flag** — every window ends at "now".

So within-route Portfolio time comparison is **not currently measurable** with this
tool. Recording that as a limitation, not as work to be scheduled.

## What is proven, and what is not

Proven:

- `portfolio_decision_replay.rs:317` calls `reweight_from_alpha_performance` inside
  the per-kline loop with cumulative ledger performance;
  `trading_modes.rs:517-556` recomputes `interval_weights` and `strategy_weights`
  from it.
- `legacy_grid.trades` and `risk_rejected_counts.execution_cost` both decrease between
  the 360-day and 540-day runs.
- 5m Alpha cumulative trades 143,757 / 197,670 / 289,224 / 379,212; 76 of 77
  strategies strictly monotone; the exception loses 2 trades.
- Alpha slice rates 3,773.9 / 3,560.4 / 3,499.5 per week, max deviation 4.5% from
  their mean, against Portfolio 8.40 / 0.74 / 5.17.

Not proven, and deliberately not claimed:

- **The magnitude of the confound.** I have shown the weights are path-dependent and
  that two counters violate nesting; I have **not** measured how much the weight
  trajectories actually diverge, and I have no way to with the current tool. It is
  possible the confound is small for `one_target` specifically and the near-stoppage
  is partly real. I cannot tell, which is exactly why the numbers are marked
  unreliable rather than withdrawn.
- That the Portfolio slice findings are **false**. They are **unverified**; a method
  defect removes the evidence, it does not establish the opposite.
- Any cause for the near-stoppage. Less than ever — its very existence is now in
  question.
- That the Alpha layer is a substitute measure for Target 3. It counts Alpha-strategy
  trades across 77 strategies, which has no relationship to Portfolio trade frequency
  and must never be quoted as one.
- Any Target 3 verdict change. Today's verdict rests on recent live data and on
  single-window measurements, neither of which uses differencing.
