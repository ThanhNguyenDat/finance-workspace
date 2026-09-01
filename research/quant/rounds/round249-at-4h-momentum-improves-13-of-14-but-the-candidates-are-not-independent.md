# CORRECTION (Round 250)

The strong form of this file's lead — **directional mechanisms at 4h exceeding
friction** — **fails independent replication on BTC**. With the deduplication
this file called for, BTC 4h gives **5/7 improved, sign-test p = 0.2266**, and a
median of **38.2% of friction** against XAU's 169% — a **4.4x shortfall** with no
significance; across all 16 distinct mechanisms it is **9/16**, a coin flip.

Also relevant to this file's own count: the sign test **counts near-ties as
wins** (BTC's heikin_ashi reads -0.00109 -> -0.00106 and scores as improved), so
13/14 here is inflated by an unknown number of such cases.
The measurements below stand; the escalation does not.
See `round250-btc-4h-fails-to-replicate-the-momentum-result-magnitude-off-by-4x.md`.

---

# Round 249 — At 4h, 13 of 14 trend/momentum candidates improve in the 150-300 band — and the nominal p-value is badly overstated because the candidates are variants of each other

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## Why this combination

Two of the session's better-supported findings had never been combined: Round 218
measured **4h** as far less cost-bound than 5m, and Round 248 measured the
**directional families** as the ones that responded to the 150-300 window. Rounds
247-248 ran only at 5m.

exness XAU **4h**, zero cost, candidates with >= 30 trades in both bands:

| family | n | median 0-150 | median 150-300 | improved | 150-300 as % of friction |
|---|---|---|---|---|---|
| breakout | **2** | −0.01585 | +0.02714 | 2/2 | 387.8% |
| **trend/momentum** | **14** | −0.00007 | **+0.01183** | **13/14** | **169.0%** |
| other | 5 | +0.00073 | −0.00394 | 2/5 | −56.3% |
| reversion | 3 | −0.00170 | −0.01300 | 0/3 | −185.7% |

Only trend/momentum has a usable population — breakout collapses to **n=2** at 4h
because most of its candidates fall below the trade floor, so this round cannot
compare families the way Round 248 did at 5m.

## The result, and the caveat that has to come first

**13 of 14 trend/momentum candidates improved**, with trade counts comfortably
above the floor (median 68 and 76 per band, minimum 32). A naive one-sided sign
test gives **p = 0.0009**.

**That p-value is badly overstated and should not be quoted.** The 14 candidates
are **not independent** — they are largely variants of the same few mechanisms:

- `candle_momentum_10bps`, `candle_momentum_30bps`,
  `candle_momentum_session_london_ny_overlap`,
  `candle_momentum_session_exclude_asian`,
  `candle_momentum_rv_regime_filter_10_50_1.1` — five variants of one signal
- `sma_trend_20`, `sma_trend_50` — one mechanism, two parameters
- `macd_trend_12_26_9`, `macd_trend_5_13_5` — one mechanism, two parameters
- `heikin_ashi_momentum_1`, `heikin_ashi_momentum_3` — one mechanism
- `parabolic_sar`, `ema_crossover_5_20`, `obv_trend_20` — three distinct

That is roughly **5-6 genuinely distinct mechanisms**, not 14 independent draws.
At n=6 a 5/6 or 6/6 result carries p ≈ 0.1 or 0.016 — suggestive, nowhere near
0.0009.

**Stated plainly: 13/14 looks stronger than it is, and I am not going to present
it as significance.** Rounds 230, 232 and 248 all caught me presenting a number
at this evidence level as a finding; the pattern here is the same shape.

## What is genuinely notable

Two things survive the deflation:

1. **The median improvement is large** — +0.01183 per trade, **169% of friction**.
   This is the first family-level figure in the session to exceed friction, on a
   population whose trade counts all clear the floor.
2. **The direction is consistent with the independent evidence.** Round 228
   measured efficiency and drift doubling across this transition; Round 218
   measured edge per trade growing with interval. A directional regime showing up
   more strongly at 4h than at 5m is what both would predict.

## The conflict this creates with Round 248

At **5m**, trend/momentum did *not* survive the per-candidate check (15/24, median
flat). At **4h** it is 13/14 with a large median. Either the effect is genuinely
interval-dependent — plausible, since Round 218 showed edge per trade grows with
interval while friction stays flat — or one of the two readings is sample noise.

This round cannot settle that. It is the clearest open question the thread now
has.

## Named next steps

1. **Deduplicate to distinct mechanisms** (one representative per family of
   variants) and re-run the sign test at both intervals. That is the honest
   version of the test I ran here.
2. **Repeat on BTC 4h.** If the same ~5-6 distinct mechanisms improve there too,
   the interval-dependence reading strengthens considerably.

## What is proven, and what is not

Proven:

- exness XAU 4h, zero cost, >= 30 trades per band: trend/momentum n=14, median
  −0.00007 → +0.01183, 13 of 14 improved, trade counts median 68/76 and minimum
  32/36.
- Breakout has only n=2 at 4h; reversion 0/3; other 2/5.

Not proven, and deliberately not claimed:

- Statistical significance. The nominal p=0.0009 assumes 14 independent
  candidates; there are roughly 5-6 distinct mechanisms, and the honest figure is
  an order of magnitude weaker.
- That 169% of friction means the family is tradable. It is one 150-day window on
  one instrument at zero cost, and Round 248's 5m reading of the same family
  disagrees.
- Any family comparison at 4h. Only trend/momentum has a usable population there.
