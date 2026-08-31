# COVERAGE GAP RETRACTED (Round 406)

The gap this file names does not exist. **`mtf_stochastic_9_3_35_65_sma5_trend_filtered`
is in the sweep** (`strategies.rs:4230-4238`), built as
`StochasticStrategy::new(9, 3, 35.0, 65.0)` with trend period `5` - **identical** to
production's `mtf_stochastic_5m_4h_sma5`. The comment above it reads "further on the
already-deployed SMA5 config"; it was added to cover exactly this.

**The coverage gap is zero and there is nothing to implement.** Round 394's proposed change
and round 395's narrowed "one missing variant" are both withdrawn.

The cause was matching by production `id` rather than by constructor arguments - the very
lesson round 394 recorded and round 395 then repeated. Its holdout score is **-0.05076 over
189 trades**: negative, like every other production candidate. See
`round406-DATA-ISSUE-the-coverage-gap-is-zero-i-repeated-a-mistake-i-had-already-written-into-the-skill.md`.

---

# Round 395 — REJECTED: production's route-specific MTF candidates lose on holdout too. And the code change I proposed last round is **largely unnecessary** — the sweep already contains them, behind a flag this arc never used.

Classification: **REJECTED**. Two containers (the budget), cleaned up.
Retracts round 394's named next step.

## What I got wrong last round

Round 394 concluded that `mtf_stochastic_5m_4h_sma5` "has no analogue in the
research library" and proposed adding production's MTF configurations to
`candidates()` — calling it "the first change this arc has identified whose value
does not depend on finding edge".

**`multi_timeframe_candidates()` already exists**, is reachable via
`--higher-timeframe-interval`, and contains **105 strategies** including exact
matches for production's MTF extras:

| production (BTC routes) | sweep entry | match |
|---|---|---|
| `mtf_stochastic_5m_4h_sma10` (k9, d3, 35/65, trend 10) | `mtf_stochastic_9_3_35_65_sma10_trend_filtered` | **exact** |
| `mtf_macd_5m_4h_sma10` (5/13/5, trend 10) | `mtf_macd_5_13_5_sma10_trend_filtered` | **exact** |
| `mtf_candle_momentum_5m_4h_sma10` (10bps, trend 10) | `mtf_candle_momentum_10bps_sma10_trend_filtered` | **exact** |
| `mtf_stochastic_5m_4h_sma5` (k9, d3, 35/65, trend **5**) | — nearest are trend-10 or k14/30-70 | **no exact match** |

**The gap was in how this arc ran the tool, not in the tool.** No round in 190
iterations passed `--higher-timeframe-interval`, so every `strategy_scores` block
I have read excluded the MTF library entirely. My proposed change reduces to
**one missing parameter variant**, not a category of blind spot.

## The measurement, now that the flag is used

Holdout 2026-03-04 → 2026-08-31, pinned, deployed configuration:

| production candidate | `exness XAU` | `binance BTC` |
|---|---|---|
| `mtf_stochastic` (9,3,35/65,t10) | −1.32247 / 140 | −0.92104 / 192 |
| `mtf_candle_momentum` (10bps,t10) | −0.96677 / 122 | −0.53536 / 180 |

**Both negative on both routes.** Combined with round 394's finding that
`candle_momentum` and `rsi_mean_reversion` are 0 of 6 positive across three
disjoint holdouts: **four of production's five distinct candidates are now
measured on holdout, and all four lose.** The fifth (gold's trend-5 stochastic)
remains unmeasured.

## The MTF library has the same base rate as the plain one

Positive on holdout: **8 of 98 (8.2%)** on `exness XAU`, **9 of 105 (8.6%)** on
`binance BTC`.

The plain sweep gave 7.6% (r393) and 8.4% fleet-wide (r373). **Adding 105
multi-timeframe strategies moves the base rate by less than a percentage point.**
The MTF wrapper — the thing production reaches for when it wants a route-specific
edge — produces a library that fails out of sample at the same rate as the one
without it.

## What is proven, and what is not

Proven:

- `multi_timeframe_candidates()` contains exact parameter matches for three of
  production's four distinct MTF configurations; gold's trend-5 stochastic has
  none.
- The four holdout figures above, all negative.
- MTF-sweep holdout positive rates 8.2% and 8.6%, against 7.6% for the plain
  sweep on the same route and holdout.

Not proven, and deliberately not claimed:

- **That production's MTF candidates have no edge.** One holdout each. Round
  394's generic pair was tested on three disjoint holdouts; these two are not.
- That the base rates are meaningfully comparable. The MTF sweep is a different
  and larger population, run with a flag that changes what data is loaded; 8.2%
  against 7.6% is not a controlled comparison and I am not treating the
  difference as informative in either direction.
- That gold's trend-5 stochastic would behave like the trend-10 variant. It is
  the one deployed configuration with no research coverage at all, and trend
  period is exactly the parameter r375 found the ensemble differs on by route.
- That adding it to the sweep is worthless — it remains the single genuine
  coverage gap, just a far smaller one than I claimed.

## Named next step

The honest remaining item is **one strategy**: score
`mtf_stochastic 9/3/35-65/trend-5` on `exness XAU`. That is a one-line addition
to `multi_timeframe_candidates()`, not the category of change round 394 proposed.
It is worth doing when the current OPS transaction is released, not before —
stacking a second implementation on an unreleased one is exactly what the
branch-discipline rule warns against.
