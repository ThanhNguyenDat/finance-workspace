# HEADLINE RETRACTED (Round 374)

This file's only surviving signal - `taker_imbalance`, the one family positive on both
instruments at p = 0.0115 - is a **phantom**. Its four positive cells have **`trades = 0`
in every split**.

`taker_base_vol` is populated on **100.00%** of Binance bars and **0.00%** of bybit and
exness bars, so on those four routes `buy_ratio` is identically 0, which satisfies
`buy_ratio <= 1.0 - threshold` for **every** threshold - the strategy emits EnterShort on
every bar forever, the side never changes, nothing ever closes, and the reported
`realized_pnl` is **exactly `-funding_paid`** on a never-closed position (verified on all
12 zero-trade cells, split-proportional 3:1:1).

Recomputed with `trades > 0` required:

| | this file | corrected |
|---|---|---|
| positive holdout cells | 39/462 | **27/462** |
| families at >= 4 of 6 routes | 6 | 5 |
| **positive on both instruments** | **taker_imbalance** | **NONE** |

**The correct answer to this file's conservative test is NONE**, and its p = 0.0115
describes nothing. Worse, `sweep.rs:43-46` already implements `survives_selection()`
requiring `trades > 0` on train and validation and deliberately excluding holdout - both
guards this file's hand-rolled scan failed to reproduce.

This file's structural findings stand: `strategy_scores` does carry real
train/validation/holdout splits at deployed costs, it is config-independent, and the
selection-on-holdout blocker is real. See
`round374-DATA-ISSUE-round-373s-only-surviving-signal-is-a-phantom-taker-volume-is-absent-on-four-routes-and-the-strategy-degrades-into-a-permanent-short.md`.

---

# Round 373 — NEEDS-MORE-RESEARCH: the **Alpha layer already carries the holdout structure the Portfolio layer lacks**. A cross-route signal that looks overwhelming under a naive null **collapses to one marginal family** once near-duplicate routes are collapsed.

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker runs (exactly the
2-container budget) completed the fleet; the other four routes were read from
logs already held. First round in this arc to reach the Alpha layer.

## The finding that made this round cheap

Every run's JSON already contains `strategy_scores`: **77 strategies × three
splits (`train` / `validation` / `holdout`)**, each with `realized_pnl`,
`trades`, `profit_factor`, `win_rate`, `max_drawdown` and `funding_paid`, at the
**same deployed costs** as the Portfolio run (fee 5bps, slippage 2bps, funding
1bps).

Verified: `strategy_scores` is **byte-identical (sha256) between the corner and
deployed Portfolio configurations on the same route and window**, so the Alpha
layer is independent of Portfolio band/hold and every log from every past round
already carries it.

The split is a clean trailing 20%: on `binance BTC` @900, train 155,519 +
validation 51,840 + **holdout 51,839** = 259,198 = `candle_count`, holdout
covering **180.0 calendar days**.

**The Alpha layer therefore has exactly the out-of-sample structure that the
Portfolio layer cannot supply (r356) — and it has been sitting in every run
this arc has ever made.**

## Fleet-complete holdout results

| route | candles | positive holdout / 77 | best holdout | best strategy |
|---|---|---|---|---|
| `binance BTC` | 259,198 | 5 | +1.4373 | `sma10_trend_filtered_fibonacci_golden_zone_100` |
| `exness BTC` | 259,084 | 9 | +1.8836 | `opening_range_breakout_london_60m` |
| `bybit BTC` | 259,198 | 6 | +1.3527 | `opening_range_breakout_london_60m` |
| `binance XAU` | 75,672 | 3 | +0.4690 | `bollinger_keltner_squeeze_20_2_0_1_0` |
| `bybit XAUT` | 145,921 | 9 | +0.6074 | `min_strength_0_7_heikin_ashi_momentum_10` |
| `exness XAU` | 174,251 | 7 | +1.5199 | `sma10_trend_filtered_fibonacci_golden_zone_100` |

**39 of 462 route-strategy cells positive (8.4%).**

## My registered criterion was nearly vacuous — the fifth such defect

I registered: *"any strategy positive on holdout on ≥ 2 of the six routes?"*
Answer: yes, six of them, at 4/6 routes each.

**Under pure chance, with the same per-route counts, P(some strategy reaches ≥ 2
routes) = 0.9999.** The criterion could essentially not have failed. This is the
same defect as r354, and the fifth in this arc (r327, r330, r340, r354, r373).
Recorded before the result, not after.

The statistic that does discriminate is the **number** of strategies at ≥ 4/6:
observed 6, null mean 0.045, **P < 1e-5**. That is the number the round would
have reported if I had stopped there. I did not.

## Why that p-value is wrong, and what survives

The independence null treats the six routes as six independent trials. **They are
not.** r276 measured the three BTC routes' volatility identical to three decimal
places; r342 measured the two gold routes at 0.996 correlation in price. Three
BTC routes and three gold routes are closer to **two** independent units.

Collapsing the 77 ids into **62 mechanism families** (parameter variants of one
mechanism are not independent trials either) and requiring a family to be
positive on **≥ 2 of an instrument's 3 routes** to count for that instrument:

| instrument | families positive |
|---|---|
| BTC | `atr_breakout`, `orb_london`, `taker_imbalance` |
| gold | `bk_squeeze`, `heikin_ashi_mom`, `sma10_fib`, `taker_imbalance` |
| **both** | **`taker_imbalance` — one family** |

Null mean 0.012; **P(≥ 1 family on both instruments) = 0.0115.**

**The overwhelming result becomes a single family at p = 0.0115.** Every other
hit turns out to be *one instrument's* effect that spilled onto a single route
of the other:

| family | pattern |
|---|---|
| `atr_breakout_14_3_0` | all three BTC routes + `exness XAU` |
| `sma10_fib` | all three gold routes + `binance BTC` |
| `bk_squeeze` | all three gold routes + `exness BTC` |

Each is "works on one instrument, plus one route of the other" — which is what a
real single-instrument effect looks like **and** what near-duplicate data looks
like. These measurements cannot distinguish the two.

## The one survivor has a degeneracy

`taker_imbalance` is the only family to clear the conservative test, and it is
also the family with a measurement oddity: the sweep contains **five** variants
(`0_55`, `0_60`, `0_70`, `fade_0_55`, `fade_0_60`), and their split signatures
are **five distinct values on both Binance routes but only two distinct values
on the other four routes** — the three non-fade thresholds return identical
numbers there (`+0.1520`, `+0.2695`, `+0.2700`, `+0.2700` on holdout).

So the threshold parameter is **inert on four of six routes** — route-dependent,
unlike r351's universally inert `--interval`. The single survivor of the
conservative test is the one whose parameterisation partly collapses. That is
not a refutation; it is a reason to look at the mechanism before trusting it.

## The blocker follows to the Alpha layer

These six strategies were **selected by looking at holdout PnL**. The holdout is
therefore consumed as a selection set for them, and the cross-instrument
replication is a partial defence rather than a clean confirmation.

Worse, a fresh holdout is not available: the holdout is the trailing 20% of the
window, so **every `--days` value produces a holdout nested inside or containing
this one** — r352's finding, now shown to apply to the Alpha layer too. All six
routes are consumed.

**The only genuinely unseen data is forward time.** This cannot be confirmed
today.

## What is proven, and what is not

Proven:

- `strategy_scores` carries 77 strategies × train/validation/holdout at deployed
  costs, and is sha256-identical across Portfolio configurations on the same
  route and window.
- The six-route holdout table above; 39/462 cells positive (8.4%).
- Six strategies / four families positive on ≥ 4 of 6 routes; naive null P < 1e-5.
- Instrument-collapsed: exactly one family (`taker_imbalance`) positive on both
  instruments; null P = 0.0115.
- `taker_imbalance`'s five variants give five distinct split signatures on both
  Binance routes and two on the other four.

Not proven, and deliberately not claimed:

- **That any of these strategies has edge.** They were selected on the holdout
  they are scored on. p = 0.0115 on a single family, after collapsing a much
  larger apparent effect, is a **hypothesis**, not a result.
- **That 0.0115 is the right p-value either.** It assumes families are
  exchangeable and that two instruments are two independent units; both are
  approximations, and I have not shown the instrument collapse is the correct
  one rather than merely more conservative than the alternative.
- That the Alpha layer is where the edge is. What is shown is that it has
  **measurable holdout structure**, which the Portfolio layer does not — a
  statement about measurability, not about profitability.
- That these holdout PnLs would survive the Portfolio's construction guard and
  risk layer. They are Alpha-ledger numbers; nothing here runs them through
  `one_target`.
- Anything about `binance XAU`'s three positives specifically: that route has
  75,672 candles (262.8 bar-days, its full venue horizon, r208/r372) so its
  holdout is ~53 days against 180 elsewhere.

## Named next step

Re-run the identical six-route holdout scan **after enough forward time has
passed that the trailing 20% contains bars none of these strategies were
selected on** — the only unseen data available. Meanwhile the useful cheap work
is mechanism-level: read what `taker_imbalance` computes and why its threshold
is inert on four routes, which is a code-reading question, not a backtest round.
