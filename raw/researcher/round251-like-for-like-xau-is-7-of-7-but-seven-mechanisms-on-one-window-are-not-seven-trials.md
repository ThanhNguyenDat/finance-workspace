# Round 251 — Like-for-like at last: XAU 4h is 7/7 deduplicated (p=0.0078), BTC 5/7 (p=0.23). And seven mechanisms on one window are not seven independent trials

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## The comparison asymmetry Round 250 left

Round 250 compared **BTC deduplicated (5/7)** against **XAU raw (13/14)** and
called the strong form rejected. It flagged its own gap: *"not claimed: that the
deduplicated XAU figure would be 5/6 or 6/6 — Round 249's data was not retained
and was not re-run here."*

Comparing a deduplicated figure against a raw one is unequal footing — the same
aggregation error that produced the Round 241/243 mistake. This round re-runs XAU
4h and applies the **identical, unchanged** dedup rule from Round 250.

exness XAU **4h**, zero cost: 24 candidates >= 30 trades per band collapse to
**13 distinct mechanisms**, 7 of them directional.

| mechanism | 0-150 | 150-300 | trades |
|---|---|---|---|
| parabolic_sar | +0.00400 | +0.03667 | 50/51 |
| ema_crossover | −0.00395 | +0.02812 | 43/32 |
| macd_trend | +0.01056 | +0.01646 | 90/96 |
| heikin_ashi_momentum | −0.00261 | +0.00874 | 161/159 |
| obv_trend | +0.00099 | +0.00848 | 71/79 |
| candle_momentum | +0.00170 | +0.00669 | 253/263 |
| sma_trend | +0.00040 | +0.00616 | 75/73 |

**7 of 7 improved, no near-ties**, sign-test p = 0.0078, median 150-300 =
+0.00874 = **124.9% of friction**.

## Like-for-like, identical rule

| | directional | sign-test p | median as % of friction | all mechanisms |
|---|---|---|---|---|
| **XAU 4h** | **7/7** | **0.0078** | **124.9%** | 10/13 |
| BTC 4h | 5/7 | 0.2266 | 38.2% | 9/16 |

**This partially corrects Round 250.** That round's framing implied XAU's 13/14
was inflated by counting variants; deduplicated it is **7/7 with no near-ties** —
*stronger* per mechanism, not weaker. Round 250's rejection of the **strong form**
(directional mechanisms clear friction) still stands on BTC's 38.2%, but the
suggestion that XAU's figure would deflate was wrong.

## The deeper deflation, which applies to both

The variant-duplication problem is fixed. **The independence problem is not.**

Seven distinct mechanisms trading **the same instrument over the same 150 days**
are not seven independent trials. They are **seven views of one price path**. A
window that rewards directional trading moves all of them together, so 7/7 is
close to a single observation repeated seven times, and **p = 0.0078 is still
badly overstated** — for a different reason than in Round 249, but overstated all
the same.

This is why **BTC is the informative test**: it is a genuinely independent draw of
the same calendar period. That draw gave **5/7 at p = 0.23 and 38.2% of
friction** — same direction, a third of the size, no significance.

So the evidence structure is: one strong-looking instrument, one weak independent
replication, and a within-instrument statistic that cannot be trusted at face
value in either.

## Where this leaves the claim

| form of the claim | status |
|---|---|
| directional mechanisms responded to the 150-300 window | **supported** — 7/7 and 5/7, plus Rounds 228, 247, 248 |
| the response exceeds friction | **XAU only** (124.9% vs 38.2%) — not replicated |
| the within-instrument p-values mean what they say | **no** — mechanisms share one price path |

Unchanged from Rounds 242-246: a real but small shared-window effect, large enough
to notice on one instrument and not on the other, and not established as tradable.

## What is proven, and what is not

Proven:

- exness XAU 4h zero cost, identical dedup rule: 24 candidates → 13 mechanisms,
  7 directional, 7/7 improved with no near-ties, median +0.00874 (124.9% of
  friction), all mechanisms 10/13.
- Like-for-like against BTC 4h: 5/7, p = 0.2266, 38.2%, 9/16.

Not proven, and deliberately not claimed:

- Significance on either instrument. The sign tests assume independent trials;
  the mechanisms share one instrument and one 150-day window, so both p-values
  are overstated. BTC's is the only figure drawn from an independent instrument
  and it is 0.23.
- That XAU's 124.9% is tradable. One instrument, one window, zero cost, and the
  independent replication reaches a third of it.
- Any explanation for the instrument difference. Not investigated here.
