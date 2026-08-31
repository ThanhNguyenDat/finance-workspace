# Round 267 — `trend_score` cannot move faster than 1h *by configuration*, and `minimum_role_score` demands up to 70% of a route's entire entry budget

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence plus local
code inspection. **Zero containers.**

## Round 266's unmeasured quantity, answered analytically instead of by waiting

Round 266 closed on: *"not claimed that accumulating samples will work — it depends
on `trend_score` moving at all over longer spans, which is exactly what is
unmeasured."* Accumulating that over dozens of rounds was the obvious route. It is
not necessary: **the answer is configuration, readable now.**

`role_scores()` (`trading_modes.rs:1042-1069`) partitions evidence by
`policy.required_intervals`, mapping each interval to `Entry` or `Trend`. Read from
the live checkpoints, that map is **identical on all four routes**:

```
ENTRY : 5m, 15m, 30m
TREND : 1h, 2h, 4h, 12h, 1d
```

**`trend_score` therefore cannot update faster than an hourly close** — and, weighted
by `interval_weights`, **84-89% of the trend budget sits in 4h/12h/1d**, which cannot
change for hours to a day:

| route | ENTRY budget | TREND budget | share of TREND in 4h+12h+1d |
|---|---|---|---|
| binance XAU (8 trades) | 0.1437 | 0.8564 | **88.8%** |
| bybit XAUT (3 trades) | 0.2933 | 0.7068 | **84.2%** |
| exness XAU (395 trades) | 0.2523 | 0.7475 | 68.4% |

That fully accounts for Round 266's observation without any accumulation, and the
third sample confirms it: **`trend_score` is unchanged to four decimals on all four
routes across all three samples spanning 37 minutes.**

## The severity of the entry gate, quantified

`entry_score` is a weighted sum over the entry intervals only, so its **maximum
attainable magnitude is the entry interval-weight budget**. `minimum_role_score` is
0.1 on every route. So the gate demands:

| route | entry budget | 0.1 as a share of the maximum possible entry_score |
|---|---|---|
| **binance XAU** | 0.1437 | **69.6%** |
| exness XAU (healthy) | 0.2523 | 39.6% |
| bybit XAUT | 0.2933 | 34.1% |

**`binance XAU` must reach roughly 70% of its theoretical maximum entry score to pass
gate 1** — nearly double what the healthy `exness XAU` needs. Its three observed
`entry_score` readings are +0.0722, +0.0722, +0.0121, and its gate reason was
`entry_score_below_threshold` **all three times**.

## The two low-trade routes fail differently

| route | 3 samples: gate reason | entry | trend |
|---|---|---|---|
| binance XAU | `below`, `below`, `below` | +0.0722, +0.0722, +0.0121 | −0.3476 (pinned) |
| bybit XAUT | `conflict`, `conflict`, `conflict` | +0.1038, +0.1969, +0.1969 | −0.5023 (pinned) |

`binance XAU` fails the **threshold**; `bybit XAUT` clears it comfortably and fails
the **sign conflict** against the largest pinned trend in the set. **Not one
mechanism — two.** Notably `bybit XAUT` has the *loosest* entry constraint of the
three (34.1%), so the threshold story cannot be what limits it.

## Why this is still not a result

The healthy routes trip the same gates in the same samples: `binance BTC` went
`conflict, conflict, below`, and `exness BTC` went `below, below, trend_below`. **All
four routes hold, for a mix of reasons**, consistent with the 99.3-99.8% hold rate
Round 265 measured across every route.

And `interval_weights` carry the same confound Round 263 raised for
`strategy_weights`: they are **outputs of the reweighting formula**, fed by ledgers
holding 7 and 1 seed trades. `binance XAU`'s unusually concentrated weights
(1d = 0.4311, entry budget 0.1437) may be a symptom of the near-empty seed rather
than an independent cause. **A snapshot still cannot resolve that direction.**

## What is proven, and what is not

Proven:

- `role_scores()` partitions by `policy.required_intervals`
  (`trading_modes.rs:1042-1069`), and that map is ENTRY 5m/15m/30m, TREND
  1h/2h/4h/12h/1d, identical on all four routes read.
- Entry/trend weight budgets and the 4h+12h+1d shares tabulated above.
- `minimum_role_score = 0.1` equals 69.6% / 39.6% / 34.1% of the maximum attainable
  entry score on those three routes.
- `trend_score` unchanged to four decimals on four routes across three samples over
  37 minutes; the sample log now holds 12 observations.

Not proven, and deliberately not claimed:

- That either mechanism **causes** the low lifetime trade counts. Three samples per
  route, and the healthy routes trip the same gates. Round 264 showed all six routes
  decide at identical cadence and Round 261 showed the live rate gap is noise.
- That the weight concentration is a cause rather than a symptom of the seed. Same
  confound as Round 263, unresolved.
- That `trend_score` never moves. It cannot move faster than 1h **by configuration**;
  how often it actually moves over hours or days is still unmeasured, and the sample
  log is the way to find out.
- Anything about PnL, Target 3, the seed spans, or the stalled backfill. Rounds
  261-266 stand unchanged.
