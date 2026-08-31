# Round 244 — Carving XAU's recent band into thirds: the sign is broad (3/3 positive) but the magnitude is decaying, and the newest 150 days are effectively zero

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## The limitation Round 243 named

Round 243 closed with: *"not claimed: statistical significance of the recent
positive bands... the spread here is across nested windows, not independent
samples."*

The available substitute for a significance test is to carve the recent band into
**disjoint sub-periods** and ask whether the edge is broad or carried by one
stretch. Same nested-subtraction technique, licensed by Round 226.

exness XAU/USD 5m, `one_target`, hold 36, all costs zero:

| window | trades | gross PnL | gross per trade |
|---|---|---|---|
| 150 days | 175 | +0.015 | +0.00008 |
| 300 days | 473 | +0.557 | +0.00118 |
| 450 days | 693 | +0.741 | +0.00107 |

## The three disjoint sub-bands

| sub-band (days ago) | trades | gross PnL | **gross per trade** | % of friction (~0.0070) |
|---|---|---|---|---|
| 300-450 | 220 | +0.184 | +0.00084 | 12.0% |
| 150-300 | 298 | +0.542 | **+0.00182** | **26.0%** |
| **0-150** | 175 | +0.015 | **+0.00008** | **1.2%** |

**Two readings, and both matter.**

**The sign is broad.** All three disjoint sub-periods are positive — 3 of 3. The
recent edge is not an artifact of one lucky stretch, which is the strongest
statement available without a real significance test.

**The magnitude is decaying, and the newest stretch is effectively zero.** Going
forward in time: 12.0% → 26.0% → **1.2%** of friction. The most recent 150 days
produce **+0.015 total gross PnL across 175 trades** — positive in sign,
indistinguishable from zero in substance.

## What this does to the recent-edge story

Rounds 242-243 established "a small positive gross edge confined to the most
recent ~450 days, worth 11-15% of friction, on both instruments". That statement
is now too flattering for XAU: **the 15% figure is an average over a period whose
most recent third contributes ~1%.**

Restated honestly for XAU:

> The positive gross edge is real in sign across three disjoint sub-periods, but
> it is concentrated in the 150-450 day range and has decayed to approximately
> zero in the most recent 150 days.

That matters more than the aggregate because the newest sub-band is the one that
predicts what deployment would experience now.

## What is proven, and what is not

Proven:

- exness XAU 5m zero-cost `one_target`: 150d gives 175 trades and +0.015; 300d
  gives 473 and +0.557; 450d gives 693 and +0.741.
- Disjoint sub-bands: 300-450 +0.00084, 150-300 +0.00182, 0-150 +0.00008 per
  trade — all positive.

Not proven, and deliberately not claimed:

- That the decay is a trend rather than three draws. Three sub-bands with 175-298
  trades and no confidence intervals; Round 230's lesson applies to the ordering
  of magnitudes even though the sign pattern (3/3) is what is being claimed.
- That the newest sub-band is *negative*. It is positive, just negligibly so; the
  claim is "indistinguishable from zero", not "has turned".
- That BTC behaves the same way. **Not carved — the obvious next round**: BTC's
  0-450 band read +0.00078 in Round 243, and whether its newest third is also near
  zero is unmeasured.
- Independence. The sub-bands are disjoint in calendar time but obtained by
  subtracting nested runs, leaning on Round 226 as flagged in Rounds 242-243.
