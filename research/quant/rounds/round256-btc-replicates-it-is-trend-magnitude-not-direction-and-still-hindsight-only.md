# Round 256 — BTC replicates at ρ=+0.857: it is trend **magnitude**, not direction, and it stays hindsight-only

Classification: **REJECTED** — signed drift is rejected as the variable, and the
ex-ante null is confirmed on the independent instrument. Two bounded Docker sweeps
(BTC), one read-only Timescale query.

## The test Round 255 named

Round 255 found `|drift| → edge` at Spearman +0.857 on XAU but flagged that it
could not separate **signed drift** from **trend magnitude**: six of XAU's seven
bands had positive drift, so the two are nearly the same variable there. BTC was
named as the obvious next test.

BTC tiled identically (`--days 1050` at 1/7, `--days 750` at 0.2, plus Round 254's
three) gives seven contiguous 150-day bands on the **same calendar boundaries as
XAU**, and — decisively — **two genuine downtrend bands**:

| band | period | drift | efficiency | edge |
|---|---|---|---|---|
| B1 1050-900d | 2023-10-14 → 2024-03-12 | **+167.75%** | 0.2861 | +0.00493 |
| B2 900-750d | 2024-03-12 → 2024-08-09 | **−15.90%** | 0.0225 | +0.00407 |
| B3 750-600d | 2024-08-09 → 2025-01-06 | +65.96% | 0.1032 | +0.00630 |
| B4 600-450d | 2025-01-06 → 2025-06-05 | +5.60% | 0.0085 | −0.00969 |
| B5 450-300d | 2025-06-05 → 2025-11-02 | +6.37% | 0.0143 | −0.00000 |
| B6 300-150d | 2025-11-02 → 2026-04-01 | **−38.22%** | 0.0589 | +0.00564 |
| B7 150-0d | 2026-04-01 → 2026-08-29 | +12.99% | 0.0261 | −0.00205 |

## Finding 1 — the relationship replicates exactly

| predictor | XAU ρ | XAU p | BTC ρ | BTC p |
|---|---|---|---|---|
| **\|drift\|** | **+0.857** | **0.0238** | **+0.857** | **0.0238** |
| signed drift | +0.857 | 0.0238 | **+0.143** | **0.783** |
| efficiency | +0.500 | 0.267 | +0.786 | 0.048 |

Two independent instruments, seven non-overlapping bands each, **the same
coefficient to three decimal places**. Fisher's method on the two independent
tests: χ² = 14.95, df = 4, **combined p = 0.0048**.

## Finding 2 — it is magnitude, not direction

This is the separation XAU could not make. On BTC, the instrument that **can**
tell them apart:

- `|drift| → edge`: **+0.857** (p = 0.024)
- `signed drift → edge`: **+0.143** (p = 0.78) — nothing.

On XAU both read +0.857 only because XAU has a single negative-drift band, which
makes the two variables nearly identical there. **On the only instrument where the
question is answerable, direction carries no information and magnitude carries all
of it.**

A note against a misreading I nearly recorded: a naive "both instruments agree in
sign" tally gives 2/2 for signed drift as well, because +0.143 is positive. That
tally is meaningless at that magnitude, and it is not evidence for direction.

This closes, from a third angle, the long/short question of Rounds 252-253 — and it
explains why those rounds kept finding instrument-level disagreement on direction:
they were testing the wrong variable.

## Finding 3 — the relation is ordinal *within* an instrument, not cardinal *across*

Same calendar band, B6 (2025-11 → 2026-04):

| | \|drift\| | edge |
|---|---|---|
| XAU | 19.63% | +0.00987 |
| BTC | 38.22% | +0.00564 |

**BTC trended 1.95x more and earned 57% of XAU's per-trade edge.** `|drift|` ranks
bands *inside* one instrument; it does not put two instruments on one scale.

That resolves the open question Round 252 raised and Rounds 253-255 left standing —
"why did XAU respond 3.3x more than BTC" — as **the wrong question**. There is no
shared scale on which to compare the two responses, so the "gap" was an artifact of
treating an ordinal within-instrument relation as a cardinal cross-instrument one.

## Finding 4 — the ex-ante null replicates

| predictor | → BTC edge(t+1) | Spearman | perm p |
|---|---|---|---|
| edge(t) | | **−0.600** | 0.242 |
| \|drift\|(t) | | −0.314 | 0.564 |
| drift(t) | | −0.086 | 0.919 |
| efficiency(t) | | −0.314 | 0.564 |

**All four non-significant, all four negative** — as on XAU, where they were +0.086,
−0.371, −0.371, +0.314. Contemporaneous +0.857 on both instruments; forecast, nothing
on either. If anything BTC hints at *anti*-persistence.

## The honest reading: this is close to a tautology

Trend-following mechanisms earn more in periods where the instrument trended more.
Stated that way it is nearly a definition, and that is the point: **the band
pattern that Rounds 242-255 spent fourteen rounds characterising is largely a
restatement of how much the market moved in one direction during the band.**

It explains the pattern, and it explains why the pattern is worthless: the band's
trend magnitude is only known once the band is over, and nothing available at the
band's start forecasts it on either instrument.

Round 255 closed this direction operationally on one instrument. **It is now closed
on two, with the mechanism identified and the ex-ante null replicated.** Nothing
here changes the standing result that loss ≈ trade count × a near-constant and that
no Portfolio-construction lever improves per-trade economics.

## What is proven, and what is not

Proven:

- BTC's seven contiguous 150-day bands with the drift, efficiency and edge values
  tabulated above, on the same calendar boundaries as XAU's.
- `|drift| → edge` Spearman +0.857, exact permutation p = 0.0238 on BTC, identical
  to XAU; Fisher combined p = 0.0048 across the two independent instruments.
- On BTC, signed drift → edge is +0.143 (p = 0.78) against |drift|'s +0.857.
- Same calendar band B6: BTC |drift| 1.95x XAU's, BTC edge 57% of XAU's.
- All four lagged predictors of BTC's next-band edge are non-significant and
  negative.

Not proven, and deliberately not claimed:

- That `|drift|` and efficiency are separate pieces of evidence. **Efficiency is
  |drift| divided by total path length** — they share a numerator by construction,
  so their two correlations must not be added up.
- That the relationship is causal, or that seven bands from one price path are
  seven independent trials. They are non-overlapping, which is better than the
  Round 251 situation, but adjacent bands can share a regime. The honest
  independent unit is **2 instruments**.
- Any tradable edge. Every figure is zero-cost and gross of fees, slippage and
  funding.
- That no ex-ante predictor exists. Four quantities on six transitions per
  instrument rules out a strong effect, not a subtle one.
- That the tautology reading is complete. It fits, and it is the simplest
  explanation, but "trending markets favour trend-following" was not independently
  tested here against a non-trend-following control population.
