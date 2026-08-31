# MECHANISM FOR THE NON-ADDITIVITY (Round 344)

This file's "super-additive, no single lever exists" now has a **mechanism**, and the
conclusion holds for a stronger reason than it was argued on. The cost flags are **not
exogenous**: on `exness XAU` @300, `--fee-bps 0` left the trade count at exactly 42 and dropped
`gross_pnl_before_costs` — a quantity measured *before* costs — by **79%**, and
`--slippage-bps 0` moved the count 42 → 38. Cheaper execution makes more strategies profitable,
which changes the per-kline Alpha weights (round 300), which changes what the Portfolio trades.

So a `--fee-bps` / `--slippage-bps` delta is a **joint** cost-and-decision effect. No run in
this arc supports a per-component cost attribution. See `round344-DATA-ISSUE-the-cost-flags-change-the-decision-stream-so-cost-component-attribution-is-not-identified.md`.

---

# ⚠️ CORRECTION (Round 214)

Part 2's first proposed lever — **maker instead of taker execution**, on the
reasoning that "more than half the round-trip cost is the taker premium" — was
tested in Round 214 and **does not hold**. Varying `--fee-bps` alone with
slippage and funding constant gives 2 -> 3 -> 4 passing candidates at 5 -> 2 -> 0
bps: the taker->maker step gains exactly one candidate, by moving a train split
from 0.99 to 1.05. Almost the entire cost effect in this file's 2-vs-14 result
comes from **slippage**, not fees. The 2-vs-14 measurement itself stands.
See `round214-maker-is-not-the-lever-slippage-dominates-not-fees.md`.

---

# Round 213 — Funding measured directly (and Round 212's "bias has a direction" was wrong), plus: transaction cost, not indicator choice, is what fails gold at 4h

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps, both
differencing against the saved 1,800-day baseline so the only variable is the
cost model.

## Part 1 — Round 212's inference, now measured

Round 212 inferred from PF/PnL sign contradictions that `profit_factor` excludes
funding. The direct test: rerun the identical sweep with `--funding-rate-bps 0`
and difference it against the default (1.0 bps).

**231 cells compared. 222 changed their PnL. Not one changed its PF.** Every
single PF delta is exactly 0.00. That is as clean a confirmation of the code
reading as this tool can produce: funding moves the PnL column and is invisible
to the PF column.

### Materiality is high

| measure | value |
|---|---|
| \|funding\| as share of \|reported PnL\| — median | **16.4%** |
| — p75 / p90 / max | 51.8% / 100% / 600% |
| cells where \|funding\| **exceeds** \|reported PnL\| | **22 (9.9%)** |
| cells where removing funding **flips the sign of PnL** | **25 (11.3%)** |

For roughly one cell in nine, whether the strategy made or lost money is decided
by the funding model rather than by the trading signal — while the metric the
promotion bar reads cannot see any of it.

### ⚠️ Correcting Round 212

Round 212 wrote: *"The bias has a direction. Funding accrues with holding time,
so the metric systematically flatters exactly the kind of candidate the program
has been selecting for."*

**That was wrong, and this round's measurement refutes it.** Funding is signed by
position side — shorts receive it at a positive rate:

| | cells | total effect of removing funding |
|---|---|---|
| funding was a **cost** | 108 | +19.88 |
| funding was a **credit** | **114** | −24.65 |
| net | 222 | −4.77 |

It is a credit slightly more often than a cost. There is no systematic optimistic
bias. The correct characterisation is worse for interpretation, not better: PF and
PnL differ by an amount that is **large, two-sided and uncorrelated with the
signal** — noise injected into one column that the other cannot see. A one-way
bias could at least be reasoned about; this cannot.

### A second, smaller defect found in the same diff

`taker_imbalance_0_55`, `_0_60`, `_0_70` report **train trades = 0 with PnL
+1.62**; the `taker_imbalance_fade_*` variants report **0 trades with PnL −1.62**.
Both go to exactly 0.00 at zero funding.

Zero closed trades cannot produce realised PnL. What is happening is funding
accruing on a position that opened and never closed inside the split, booked into
`realized_pnl`. Carry on an open position is unrealised; labelling it "realised"
is wrong regardless of which PF convention one prefers.

### What this does *not* invalidate

**Zero candidates change their all-three-splits verdict when funding is removed.**
The bar reads PF, PF never saw funding, so removing funding cannot move the bar.
No past promotion decision is overturned by this. What is not defensible is
reading the `pnl` and `pf` columns of the same table as if they describe the same
thing — they do not.

## Part 2 — Cost is the binding constraint, measured

Round 93 hypothesised that the PF 0.65-0.85 plateau across unrelated mechanisms
was a fixed cost ceiling rather than indicator weakness, and never isolated it.
The CLI's own doc for `--fee-bps` says "Zero isolates how much of a result is
cost". Second sweep: `--fee-bps 0 --slippage-bps 0 --funding-rate-bps 0`.

| | candidates clearing all three splits (of 77) |
|---|---|
| production costs (5 bps taker + 2 bps slippage + funding) | **2** |
| zero costs | **14** |

**Twelve candidates flip from fail to pass on 7 bps of round-trip cost alone**,
several with large samples:

| candidate | costed t/v/h | cost-free t/v/h | train trades |
|---|---|---|---|
| `heikin_ashi_momentum_1` | 0.58 / 0.95 / 0.86 | 1.03 / 1.61 / 1.18 | 1,137 |
| `candle_momentum_10bps` | 0.54 / 0.67 / 0.88 | 1.02 / 1.16 / 1.29 | 1,540 |
| `macd_trend_5_13_5` | 0.73 / 0.98 / 1.18 | 1.14 / 1.41 / 1.52 | 705 |
| `elder_ray_13` | 0.65 / 0.94 / 0.92 | 1.02 / 1.43 / 1.19 | 608 |
| `parabolic_sar_0_02_0_02_0_2` | 0.74 / 1.28 / 1.33 | 1.02 / 1.67 / 1.62 | 409 |
| `sma_trend_50` | 0.92 / 0.75 / 1.41 | 1.34 / 1.04 / 1.78 | 312 |

Round 93's hypothesis is confirmed quantitatively on gold: **these mechanisms do
carry positive gross edge. The edge is simply smaller than the cost of
harvesting it.** The program's 0-for-15+ record on new indicators is not fifteen
bad ideas; it is one cost constraint met fifteen times.

### Why this is NEEDS-MORE-RESEARCH and not a result

A cost-free backtest is not tradeable and nothing here is promotable. What it does
is redirect the search. The productive levers are the ones that change the
cost-to-edge ratio, none of which have been tested:

1. **Maker instead of taker.** The ledger already models `maker_fee_bps` (2.0)
   against `fee_bps` (5.0) and `liquidity_role`. More than half the round-trip
   cost is the taker premium. No round has ever run a maker-execution comparison.
2. **Fewer, larger trades.** The 12 flipped candidates average several hundred
   trades per split; cost scales with count while edge does not.
3. **Cost sensitivity as a first-class screen**: sweep at 0 / 2 / 5 / 7 bps and
   record the break-even cost per candidate, instead of a single pass/fail at
   production cost.

Each is a concrete next experiment with a defensible design. None is validated
here, so none is promoted.

## What is proven, and what is not

Proven:

- 222 of 231 cells change PnL when funding is zeroed; **0 of 231 change PF**.
- Funding is a credit in 114 cells and a cost in 108; median \|funding\| is 16.4%
  of \|reported PnL\|, exceeds it in 9.9% of cells, and flips its sign in 11.3%.
- Three `taker_imbalance_*` candidates report non-zero PnL with zero closed
  trades; the value vanishes at zero funding.
- 2 of 77 candidates clear the bar at production cost; 14 of 77 at zero cost.

Not proven, and deliberately not claimed:

- That any of the 12 cost-sensitive candidates is tradeable. They are not — they
  pass only in a world with no fees.
- That maker execution is achievable for these signals. The ledger can model it;
  whether these entries would actually fill as maker is a separate question this
  round did not touch.
- Anything outside exness XAU 4h on the 1,800-day window. The cost decomposition
  was not repeated on BTC, on bybit, or at other intervals.
