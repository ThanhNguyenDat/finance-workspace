# ⚠️ CORRECTION (Round 213)

The section below headed **"The bias has a direction"** is **wrong**. Round 213
measured funding directly by rerunning the identical sweep at
`--funding-rate-bps 0`: funding is signed by position side, so it is a **credit in
114 cells and a cost in 108** — there is no systematic optimistic bias toward
longer-holding candidates. The defect itself (PF excludes funding, PnL includes
it) is confirmed exactly: 222 of 231 cells changed PnL and **0 changed PF**.
See `round213-funding-measured-and-cost-is-the-binding-constraint-on-gold.md`.

---

# Round 212 — The sweep's profit factor excludes funding while its PnL includes it: 8.1% of all "PF > 1" verdicts are on strategies that lost money

Classification: **DATA-ISSUE**. A concrete measurement defect, found by chasing a
contradiction inside this round's own output. Two bounded Docker sweeps.

## How it surfaced

The round set out to do something else: build a four-window stability profile for
exness XAU 4h, since Round 211 showed a single partition is unreliable. Two new
windows were run (900d, 1,350d) and combined with the saved 500d and 1,800d runs.

| window | candles | train / validation / holdout |
|---|---|---|
| 500d | 2,191 | 1,315 / 438 / 438 |
| 900d | 3,945 | 2,367 / 789 / 789 |
| 1,350d | 5,904 | 3,542 / 1,181 / 1,181 |
| 1,800d | 7,880 | 4,728 / 1,576 / 1,576 |

Of 77 candidates evaluated in all four windows: **68 pass the all-three-splits
bar in zero windows**, 4 in one, 3 in two, 2 in three, **none in all four**.

The best survivor was `ema_crossover_12_26`, clearing the bar in the three
longest windows. Its 1,800-day row is what stopped the round:

```
ema_crossover_12_26  train       148   -0.10   29.7%   1.01
ema_crossover_12_26  validation   45   -0.05   24.4%   1.05
```

**Profit factor above 1 with negative realised PnL.** Those cannot both be true
if PF is gross profit over gross loss, so one of the two numbers is not measuring
what it appears to.

## Root cause, read in the code

`profit_factor` is `gross_profit / gross_loss`
(`crates/finance-research/src/sweep.rs:58-59`), and those two accumulators are
only ever written in `close_position`, bucketed by the sign of a closed trade's
realised PnL.

Funding is settled on a different path
(`crates/finance-core/src/trading_modes.rs:2131-2135`):

```rust
self.equity -= paid;
self.performance.realized_pnl -= paid;
self.performance.funding_paid += paid;
```

It debits equity and `realized_pnl` and records `funding_paid` — and **never
touches `gross_profit` or `gross_loss`**.

So the reported **PnL is net of funding and the reported PF is not**. A strategy
whose gross trade edge is positive but smaller than its carrying cost reports
`PF > 1` and a loss at the same time.

## How often this matters — measured across the whole sweep

All 924 candidate-split-window cells from the four windows:

| | count | share |
|---|---|---|
| cells reporting **PF > 1** | 270 | 29.2% of all cells |
| **of those, with negative realised PnL** | **22** | **8.1% of PF > 1 cells** |
| cells with PF <= 1 but positive PnL | 17 | — |

Worst cases, including several with real sample sizes:

| candidate | split | window | trades | PF | PnL |
|---|---|---|---|---|---|
| `atr_breakout_14_3_0` | train | 1,800d | 20 | **1.55** | −0.20 |
| `candle_momentum_rv_regime_filter_10_50_1` | validation | 1,350d | 141 | 1.01 | −0.10 |
| `cci_breakout_20_100` | train | 900d | 81 | 1.02 | −0.10 |
| `donchian_breakout_55` | train | 1,800d | 44 | 1.05 | −0.18 |
| `min_strength_0_5_heikin_ashi_momentum_10` | train | 1,800d | 6 | 1.12 | −1.14 |

**The bias has a direction.** Funding accrues with holding time, so the gap grows
for strategies that hold longer — the metric systematically flatters exactly the
kind of candidate the program has been selecting for.

## The lead this round found does not survive the fix

`ema_crossover_12_26` on exness XAU 4h, under the current bar and under a
PnL-positive bar:

| window | PF t/v/h | PF bar | PnL t/v/h | PnL bar |
|---|---|---|---|---|
| 500d | 1.60 / 1.99 / 0.57 | fail | +0.57 / +0.44 / −0.50 | fail |
| 900d | 1.07 / 1.94 / 1.07 | **pass** | −0.03 / +0.55 / +0.12 | fail |
| 1,350d | 1.38 / 1.20 / 1.13 | **pass** | +0.98 / +0.15 / +0.22 | **pass** |
| 1,800d | 1.01 / 1.05 / 1.42 | **pass** | −0.10 / −0.05 / +0.79 | fail |

3 of 4 windows on the PF bar, 1 of 4 on the PnL bar. The candidate is **rejected**
— and it is rejected by the very defect it exposed. No promotion.

## What this does and does not invalidate

It **does** mean: the sweep table's `pf` column is not a profitability test on
its own, and any past round that treated "PF > 1 on all three splits" as
"profitable" carried an ~8% false-pass rate on this instrument, skewed toward
longer-holding candidates.

It **does not** mean Rounds 80/83/92 are wrong. Those used `one_target` Portfolio
measurement and PnL figures, not this sweep's PF column. What it does mean is
that their direction — longer holds, wider stops — is the direction this metric
flatters, so a re-check of those levers against a funding-inclusive measure is
worth doing before anyone extends them further.

It is also possible this is a deliberate convention rather than a bug: classical
profit factor is defined on trade results and treats carry separately. That
argument is legitimate, and it is precisely why this is filed as a measurement
issue for a deliberate decision rather than promoted as a fix. What is not
defensible is the current state, where one table prints a funding-inclusive PnL
next to a funding-exclusive PF under headers that invite direct comparison.

## What is proven, and what is not

Proven:

- `profit_factor = gross_profit / gross_loss` (sweep.rs:58-59); funding debits
  `realized_pnl` only (trading_modes.rs:2131-2135).
- 22 of 270 PF>1 cells (8.1%) have negative realised PnL; 17 cells show the
  reverse.
- `ema_crossover_12_26` passes the PF bar in 3 of 4 windows and the PnL bar in 1.
- No candidate of 77 clears the all-three-splits bar in all four windows.

Not proven, and deliberately not claimed:

- The exact funding cost per candidate. `funding_paid` is tracked in
  `SimulatedPerformance` but is not surfaced in the sweep table, so the gap was
  inferred from the PF/PnL sign contradiction, not measured directly.
- Any statement about BTC or other intervals. Only exness XAU 4h was swept.
- That the four windows are independent. They are nested, so the "3 of 4 windows"
  counts measure sensitivity, not replication — the same caveat as Round 211.
