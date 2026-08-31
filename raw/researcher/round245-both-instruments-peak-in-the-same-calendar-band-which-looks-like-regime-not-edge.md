# Round 245 — BTC carved into thirds: 2/3 positive, and both instruments peak in the *same* calendar window

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## The test Round 244 named

Round 244 carved XAU's recent 450 days into three disjoint sub-bands (3/3
positive, decaying to ~1% of friction in the newest) and named the follow-up:
do the same for BTC, whose 0-450 band read +0.00078.

binance BTC/USDT 5m, `one_target`, hold 36, all costs zero:

| window | trades | gross PnL | gross per trade |
|---|---|---|---|
| 150 days | 233 | +0.130 | +0.00056 |
| 300 days | 569 | +0.817 | +0.00144 |
| 450 days | 716 | +0.558 | +0.00078 |

| BTC sub-band (days ago) | trades | gross PnL | gross per trade | % of friction |
|---|---|---|---|---|
| 300-450 | 147 | −0.259 | **−0.00176** | −25.1% |
| 150-300 | 336 | +0.687 | **+0.00204** | **+29.2%** |
| 0-150 | 233 | +0.130 | **+0.00056** | +8.0% |

**BTC is 2/3 positive**, not 3/3 like XAU — its oldest recent-band third is
negative.

## The finding: the two instruments peak in the same calendar window

| sub-band (days ago) | **XAU** per trade | **BTC** per trade |
|---|---|---|
| 0-150 | +0.00008 (1.2%) | +0.00056 (8.0%) |
| **150-300** | **+0.00182 (26.0%)** | **+0.00204 (29.2%)** |
| 300-450 | +0.00084 (12.0%) | −0.00176 (−25.1%) |

The **150-300 day** band is the strongest on **both** instruments, and the two
values are within **12%** of each other (+0.00182 vs +0.00204) despite being
different assets on different brokers.

**That co-location is the round's actual content**, and it points somewhere
uncomfortable:

> A genuine *strategy* edge should be instrument-specific and should persist. An
> edge that appears in the **same calendar window across unrelated instruments**
> and fades afterwards looks like a **market regime**, not a strategy property.

Both instruments' newest 150 days are weakly positive (1.2% and 8.0% of friction)
— i.e. the shared strong window has passed.

This is consistent with Round 220's measurement that recent volatility roughly
doubled, and with Round 228's finding that no single price statistic explains the
transitions. It reframes the "small positive recent edge" of Rounds 242-244: it
may be one favourable market period visible through whatever strategy was pointed
at it.

## How strong is the co-location evidence, honestly

With three sub-bands, two instruments peaking in the same one happens **1 time in
3** by chance alone. That is weak on its own. What raises it above coincidence is
that the two peak *magnitudes* also agree within 12% — but two agreeing numbers
is still two numbers.

**Suggestive, not established.** Stated that way deliberately, because Rounds
230 and 232 both caught me presenting a pattern at this evidence level as a
finding.

## The discriminating test for the next round

If this is a regime effect, a **third instrument** should also peak in the
150-300 band. If it is strategy edge, the third instrument's peak should land
wherever its own signal happened to work.

`bybit BTC/USDT` and `bybit XAUT/USDT` are both available and both were
calibrated as independent sources in Round 210. Running either one's three
sub-bands is one container and would move this from 1-in-3 coincidence to
1-in-9 — still not proof, but a real update.

## What is proven, and what is not

Proven:

- binance BTC 5m zero-cost `one_target`: 150d gives 233 trades and +0.130; 300d
  gives 569 and +0.817; 450d gives 716 and +0.558.
- BTC sub-bands: 300-450 −0.00176, 150-300 +0.00204, 0-150 +0.00056 — 2 of 3
  positive.
- The 150-300 band is the maximum on both instruments, at +0.00182 (XAU) and
  +0.00204 (BTC), within 12%.

Not proven, and deliberately not claimed:

- That this is a regime effect. It is the reading the co-location suggests; with
  three bands the coincidence alone is 1-in-3 and no third instrument has been
  checked.
- That the sub-band magnitudes are distinguishable. 147-336 trades each, no
  confidence intervals.
- Independence of the sub-bands. Disjoint in calendar time but obtained by
  subtracting nested runs, leaning on Round 226 as flagged since Round 242.
