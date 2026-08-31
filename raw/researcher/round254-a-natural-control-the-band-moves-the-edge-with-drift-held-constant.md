# CORRECTION (Round 255)

This file's centrepiece — the "natural control" showing XAU's B5/B6 bands at
identical drift (+19.62% / +19.63%) with a 3.25x edge difference — was **over-read**,
and I called it "the strongest single piece of evidence in this thread".

Round 255 extended XAU to **seven contiguous 150-day bands** and measured what this
file did not: across all seven, **|drift| ranks the bands almost exactly as the edge
ranks them** (Spearman +0.857, exact permutation p = 0.0238; only B1/B3 transposed).
The B5/B6 pair is ordered *correctly* by that relation — 19.62 < 19.63 and
+0.00304 < +0.00987. What is anomalous is the **magnitude**, not the direction.

So this file's conclusion that drift cannot be what moves the edge does **not**
stand. The correct, narrower statement: **drift magnitude ranks the bands well and
does not pin down the edge level.** This is the Round 230 failure mode at the band
level — declaring a variable irrelevant from the two or three bands one run happened
to produce, without measuring every band the tooling can reach.

Round 255 also found the 300-150 day window is **not unique** — B4 (600-450d,
+0.01134) is higher than B6 (+0.00987) — and that **no ex-ante predictor forecasts
the next band**, which closes this direction operationally.

This file's *measurements* stand; its interpretation does not. See
`round255-CORRECTION-the-window-is-neither-unique-nor-predictable-and-drift-does-explain-it.md`.

---

# Round 254 — A natural control: XAU's two oldest bands have identical drift, and the edge still differs 3.25x

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps (`--days 450`,
index thirds, 4h, zero cost) plus one read-only Timescale query. This is the
300-450 band experiment Round 253's budget note named; the invocation fix worked.

## What the third band was for

Round 253 refuted the long/short explanation by relabeling retained data, and
named its own limit: **within an instrument, calendar band and trend direction
were perfectly confounded** — each instrument had exactly two bands, one up and
one down, so no within-instrument comparison could separate them. A third band
breaks that, because three bands cannot all have distinct drift signs.

Both sweeps now cover the **same calendar window** with matched boundaries, which
Rounds 249-253 never had:

| band | period | XAU drift | XAU eff | BTC drift | BTC eff |
|---|---|---|---|---|---|
| train (450-300d) | 2025-06-05 → 2025-10-31 | **+19.62%** | **0.1005** | +6.37% | 0.0143 |
| validation (300-150d) | 2025-10-31 → 2026-04-01 | **+19.63%** | **0.0560** | −38.22% | 0.0589 |
| holdout (150-0d) | 2026-04-01 → 2026-08-28 | −6.90% | 0.0248 | +12.99% | 0.0261 |

## The natural control

**XAU's train and validation bands have effectively identical drift: +19.62% and
+19.63%, 0.01 percentage points apart.** They are both uptrends of the same size,
five months each, on the same instrument. And the *older* band is the **more**
efficient of the two — 0.1005 against 0.0560, a factor of 1.79.

The directional-mechanism edge is not remotely the same:

| | train (450-300d) | validation (300-150d) |
|---|---|---|
| drift | +19.62% | +19.63% |
| efficiency | 0.1005 | 0.0560 |
| **median directional edge** | **+0.00304** | **+0.00987** |

**Drift is held constant, efficiency points the wrong way, and the edge is still
3.25x higher in the later band.** This is not a relabeling argument like Round
253's — it is a genuine controlled comparison, and it is the strongest single
piece of evidence in this thread that what moves the edge is *when*, not *what
the market was doing*.

## The band pattern replicates on the new carve

Directional mechanisms, per-mechanism band comparisons:

| comparison | XAU | BTC | instruments agreeing | pooled | nominal p |
|---|---|---|---|---|---|
| validation > train | **6/6** | 6/7 | **2/2** | 12/13 | 0.0034 |
| validation > holdout | **6/6** | 5/7 | **2/2** | 11/13 | 0.0225 |
| holdout > train | 3/6 | 2/7 | — | 5/13 | — |

The middle band is the peak on both instruments, and the two outer bands are
indistinguishable from each other. Medians against the friction constant (0.0070)
used by Rounds 249-253:

| | train | validation | holdout |
|---|---|---|---|
| XAU (n=6) | +0.00304 (43.4%) | **+0.00987 (141.0%)** | −0.00017 (−2.5%) |
| BTC (n=7) | −0.00000 (−0.0%) | **+0.00564 (80.6%)** | −0.00205 (−29.3%) |

**These are zero-cost, gross figures** — the same basis as Rounds 249-253 and the
same reason they are not tradable claims.

## Both rival explanations fail again, on new data

- **Trend direction** (Round 253's refuted hypothesis): with three bands, XAU's UP
  bands beat its DOWN band, BTC's UP bands *lose* to its DOWN band. **1/2**, the
  same disagreement Round 253 found, now on an additional independent band.
- **Efficiency / directionality magnitude** (Round 252's refuted hypothesis):
  XAU's *most* efficient band (train, 0.1005) is its *worst* directional-edge band
  of the two uptrends. BTC's efficiency does track its edge. **1/2** again.

Neither survives contact with the second instrument. The calendar band is 2/2 on
both comparisons.

## Independent replication of Rounds 250-251

This carve is not the one Rounds 250/251 used (index thirds of a 450-day window
against their 300-day carve), so the shared bands are a genuine replication test:

**Sign preserved in 11/13 mechanisms in the holdout band and 11/13 in the
validation band**, with close magnitudes on the large values
(XAU `parabolic_sar` validation +0.03667 → +0.03421; BTC `obv_trend` +0.00730 →
+0.00703).

**All four sign flips are on near-zero estimates** (XAU `obv_trend` +0.00099 →
−0.00426, XAU `sma_trend` +0.00040 → −0.00368, BTC `sma_trend` −0.00211 →
+0.00542, BTC `ema_crossover` −0.00902 → +0.00564). So: large per-mechanism band
edges replicate; **near-zero ones are not stable to a boundary shift of a few
days** and should never be counted as "wins" in a sign test. Round 250 already
flagged this shape when it counted `heikin_ashi_momentum` as improved on
−0.00109 → −0.00106.

## A small methodological note, deliberately not inflated

The candidate set contains **exact mirror pairs** — `candle_reversion` is the
precise negation of `candle_momentum` on every band, and on BTC
`taker_imbalance_fade` is the precise negation of `taker_imbalance`. A mirror pair
contributes exactly one win and one loss to any "all mechanisms" count by
construction.

I expected this to explain Round 250's "9/16, an exact coin flip". **It does not.**
Excluding mirror pairs moves XAU's all-mechanism count from 9/13 to 8/11 and BTC's
from 11/21 to 9/17 — real, but far too small to change the reading. Recorded as a
counting caveat, not as a correction to Round 250.

## What this does and does not buy

It does **not** produce a tradable edge, and nothing here touches the standing
result that loss ≈ trade count × a near-constant and that no Portfolio-construction
lever improves per-trade economics. The strong band is gross of cost.

What it buys is that the shared-window description is now supported by a
**control** rather than only by correlation, and the two market-property
explanations offered for it have each failed twice on the independent instrument.

The open question is unchanged and now sharper: if the effect is calendar-locked
and not explained by drift or efficiency, **what property of that specific window
is doing the work** — and is it anything that could be known in advance rather
than only in hindsight? A window identifiable only after the fact is worth
nothing operationally, and that remains the reason this thread has produced no
promotion.

## What is proven, and what is not

Proven:

- Matched-calendar three-band statistics for both instruments (table above),
  including XAU train drift +19.62% against validation +19.63%, efficiency 0.1005
  against 0.0560.
- Median directional edge XAU +0.00304 / +0.00987 / −0.00017 (n=6) and BTC
  −0.00000 / +0.00564 / −0.00205 (n=7), zero cost.
- validation > train 6/6 and 6/7; validation > holdout 6/6 and 5/7; both 2/2 across
  instruments.
- Sign agreement with Rounds 250/251 on 11/13 mechanisms in each shared band, with
  all four flips on near-zero estimates.
- Exact mirror pairs exist; removing them moves all-mechanism counts 9/13 → 8/11
  and 11/21 → 9/17.

Not proven, and deliberately not claimed:

- Any tradable edge. Every figure here is gross of fees, slippage and funding.
- That the pooled p-values (0.0034, 0.0225) mean what they say. Six or seven
  mechanisms on one instrument over one band are views of one price path — the
  Round 251 deflation applies unchanged, and the honest independent n is **2
  instruments**, not 13 mechanisms.
- That drift and efficiency are irrelevant in general. What is shown is that
  neither explains *this* band pattern, on two instruments.
- Any explanation for what the 300-150 day window actually had. Still open after
  three refuted candidates.
- That the window is identifiable in advance. Not tested, and this is the
  question that decides whether the thread is worth continuing.
