# Round 266 — Cross-round sampling works, so the loop itself can accumulate the distribution Round 265 could not obtain; and `trend_score` did not move at all in 20 minutes

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence.
**Zero containers.**

## The one thing Round 265 left untried

Round 265 could not build a hold-reason distribution: the reason is absent from
metrics and from logs, and two checkpoint reads minutes apart came back
byte-identical. It recorded one specific escape hatch as untested: *"not claimed
that the checkpoint never refreshes fast enough to sample — two reads in one round
were identical, but a longer-spaced series was not attempted and might work."*

Twenty minutes separate Round 265's read from this one. That is four-plus 5m kline
closes.

## It works — for `entry_score`

| route | entry r265 | entry now | moved | trend r265 | trend now | moved |
|---|---|---|---|---|---|---|
| binance BTC | −0.1707 | **−0.1278** | **YES** | +0.1759 | +0.1759 | **no** |
| binance XAU | +0.0722 | +0.0722 | no | −0.3476 | −0.3476 | **no** |
| bybit XAUT | +0.1038 | **+0.1969** | **YES** | −0.5023 | −0.5023 | **no** |
| exness BTC | −0.0405 | **−0.0119** | **YES** | −0.0693 | −0.0693 | **no** |

**`entry_score` moved on 3 of 4 routes. `trend_score` moved on none.**

So the `/loop` can serve as the sampler: one observation per route per round,
accumulating across rounds into the distribution Round 265 showed cannot be read
directly. That is a workaround for the observability gap, not a fix for it — the
gap recorded in Round 265 stands.

An append-only log now exists at **`research/quant/samples/signal-state-samples.csv`**,
seeded with Round 265's four samples and this round's four. Future rounds should
append one row per route rather than re-deriving this.

### A correction inside this round

My first pass reported **4 of 4 routes moved**. That was wrong. It compared
full-precision live floats against my own 4-decimal transcription of Round 265, so
`binance XAU`'s unchanged +0.0722 / −0.3476 registered as a change. Re-run at the
precision actually recorded, it is **3 of 4**. The table above is the corrected one.

## The finding with more teeth: `trend_score` is frozen

`trend_score` was **identical to four decimals on all four routes** across twenty
minutes, while `entry_score` moved on three of them. The two scores clearly update
on different clocks — `entry_score` on the 5m decision interval, `trend_score`
anchored to higher-timeframe evidence that had not closed in the interval.

This matters because `entry_trend_conflict` (`trading_modes.rs:857`) is a **sign**
comparison. If `trend_score`'s sign is effectively pinned between higher-timeframe
closes, then any route whose `entry_score` fluctuates around zero on the opposite
side of that pin sits in conflict for extended stretches — not by chance per
evaluation, but structurally, until the higher timeframe closes.

The two routes with the smallest lifetime trade counts carry **the largest-magnitude
`trend_score` in the set**, both negative and both stable across the two
observations: `binance XAU` −0.3476 and `bybit XAUT` −0.5023, against the healthy
routes' +0.1759 and −0.0693. Their `entry_score` readings are positive (+0.0722,
+0.1038 → +0.1969), i.e. on the opposite side.

**This is two time points twenty minutes apart. It is a lead, not a result.** After
Rounds 252, 254, 261 and 263 I am not going to present a two-observation pattern as
a mechanism, and the corrected count above is a reminder that I get these wrong when
I hurry.

## What the accumulation would settle

With one sample per route per round, a few dozen rounds gives:

- the hold-reason distribution per route — Round 263's original test;
- how often `trend_score` actually changes, and therefore whether the "pinned sign"
  reading survives;
- whether the dormant routes' `trend_score` is persistently large-and-negative or
  merely was on 2026-08-29.

None of that needs an instrumentation change. It needs rounds.

## What is proven, and what is not

Proven:

- `entry_score` changed on 3 of 4 routes over ~20 minutes; `trend_score` changed on
  0 of 4, to the 4-decimal precision recorded.
- Cross-round checkpoint sampling therefore yields new observations, unlike the
  within-round sampling Round 265 attempted.
- The eight samples now in `research/quant/samples/signal-state-samples.csv`.
- My own first-pass comparison error and its correction.

Not proven, and deliberately not claimed:

- **That `trend_score` is "frozen" in general.** It did not move in one 20-minute
  window on four routes. That is consistent with higher-timeframe anchoring and with
  several other explanations, and it is one window.
- That large negative `trend_score` explains the two routes' low lifetime trade
  counts. Two observations; and Round 264 already showed those routes decide at
  identical cadence and Round 261 showed the live rate difference is noise.
- Any hold-reason distribution. Still n = 2 per route at best.
- That accumulating samples will work — it depends on `trend_score` moving at all
  over longer spans, which is exactly what is unmeasured.
- Anything about PnL, Target 3, the seed spans, or the stalled backfill. Rounds
  261-265 stand unchanged.
