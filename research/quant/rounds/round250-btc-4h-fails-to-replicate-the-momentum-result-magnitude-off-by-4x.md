# QUALIFICATION (Round 251)

This file compared **BTC deduplicated (5/7)** against **XAU raw (13/14)** —
unequal footing, as it acknowledged. Round 251 re-ran XAU 4h with the identical
dedup rule: **7/7 improved, no near-ties, p=0.0078, median 124.9% of friction**.
So XAU's figure did **not** deflate under deduplication — it is stronger per
mechanism, and this file's implication otherwise was wrong.

**The rejection of the strong form still stands**: BTC reaches 38.2% of friction
against XAU's 124.9%, a 3.3x gap with no significance. And Round 251 adds the
deflation that applies to *both*: seven mechanisms on one instrument over one
150-day window are seven views of one price path, not seven independent trials,
so both p-values are overstated.
See `round251-like-for-like-xau-is-7-of-7-but-seven-mechanisms-on-one-window-are-not-seven-trials.md`.

---

# Round 250 — BTC 4h does not replicate Round 249: deduplicated sign test p=0.23 and the magnitude is 4.4x smaller

Classification: **REJECTED** — the strong form of Round 249's lead fails
independent replication. Two bounded Docker sweeps.

## The two steps Round 249 named, run together

Round 249 found 13 of 14 trend/momentum candidates improving at XAU 4h with a
median of 169% of friction, and named its own fixes: **deduplicate to distinct
mechanisms**, and **repeat on BTC 4h**. This round does both, on BTC — the
independent instrument, which is the more informative of the two.

**The deduplication rule was fixed before looking at any outcome:** collapse every
candidate to its mechanism stem (`candle_momentum`, `sma_trend`, `macd_trend`,
`heikin_ashi_momentum`, `ema_crossover`, `parabolic_sar`, `obv_trend`, …) and keep
the **highest-trade-count** variant of each. That rule cannot select for a
favourable result because trade count is independent of the band comparison.

binance BTC **4h**, zero cost, candidates with >= 30 trades in both bands: 36
candidates collapse to **16 distinct mechanisms**.

## Result — the replication fails on magnitude and on significance

Directional mechanisms, one representative each:

| mechanism | representative | 0-150 | 150-300 | trades |
|---|---|---|---|---|
| obv_trend | obv_trend_20 | −0.00556 | +0.00730 | 108/122 |
| candle_momentum | candle_momentum_10bps | −0.00348 | +0.00517 | 419/410 |
| macd_trend | macd_trend_5_13_5 | −0.00294 | +0.00346 | 136/136 |
| parabolic_sar | parabolic_sar_0_02_0_02_0_2 | −0.00462 | +0.00268 | 78/71 |
| heikin_ashi_momentum | heikin_ashi_momentum_1 | −0.00109 | −0.00106 | 211/235 |
| sma_trend | sma_trend_20 | +0.00675 | **−0.00211** | 80/95 |
| ema_crossover | ema_crossover_5_20 | +0.02905 | **−0.00902** | 42/51 |

| measure | **XAU 4h** (Round 249) | **BTC 4h** (this round) |
|---|---|---|
| improved (directional) | 13/14 raw, ~5-6 distinct | **5/7 deduplicated** |
| sign-test p | 0.0009 nominal, ~0.1 deflated | **0.2266** |
| median 150-300 as % of friction | **169.0%** | **38.2%** |
| all mechanisms improved | — | **9/16** (coin flip) |

**The strong form of the claim — that directional mechanisms at 4h clear friction
in the favourable band — is rejected.** BTC's median reaches 38% of friction, a
**4.4x shortfall** against XAU's 169%, and the deduplicated sign test is
**p = 0.23**, nowhere near significance. Across all 16 mechanisms it is 9/16, an
exact coin flip.

**The weak form survives and is unremarkable**: more directional mechanisms
improved than not (5/7), consistent with the directional-regime description from
Rounds 228 and 247-248, but this is what that description already predicted and it
carries no new weight.

## Two details worth recording

- `heikin_ashi_momentum_1` is counted as "improved" on −0.00109 → −0.00106 — a
  difference in the fifth decimal, both negative. **The sign test counts near-ties
  as wins**, which inflates counts like 13/14 and 5/7. Round 249's 13/14 almost
  certainly contains such cases too.
- The two mechanisms that *reversed* are the two with the largest positive 0-150
  values (`ema_crossover_5_20` +0.02905 → −0.00902, `sma_trend_20` +0.00675 →
  −0.00211). That is the shape of mean reversion in the estimates themselves,
  i.e. regression to the mean, not a mechanism story.

## Where this leaves the thread

Rounds 242-248 established a shared favourable window (150-300 days ago) that
favoured directional mechanisms — that stands, supported from several independent
directions. Round 249's escalation of it into "at 4h, directional mechanisms
exceed friction" does **not** survive contact with the second instrument.

The honest position is the one Rounds 242-246 reached and this round returns to:
**a real but small window effect, shared across instruments, not large enough
anywhere to cover friction.**

## What is proven, and what is not

Proven:

- BTC 4h zero cost, >= 30 trades per band: 36 candidates, 16 distinct mechanisms.
- Directional subset 5/7 improved, sign-test p = 0.2266, median 150-300
  +0.00268 = 38.2% of friction.
- All 16 mechanisms: 9 improved.
- The two largest reversals are the two with the largest prior-band values.

Not proven, and deliberately not claimed:

- That XAU's 169% was wrong. It was measured; it simply does not replicate on the
  second instrument, and a result that appears on one instrument and not the other
  is what Round 205 and Round 224 both taught this program to reject.
- That the deduplicated XAU figure would be 5/6 or 6/6. Round 249's data was not
  retained and was not re-run here; the ~5-6 mechanism estimate is from its own
  candidate list, not a recomputation.
- Anything about 5m. This round is 4h only.
