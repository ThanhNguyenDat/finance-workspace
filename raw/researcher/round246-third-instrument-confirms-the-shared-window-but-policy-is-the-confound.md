# Round 246 — A third instrument peaks in the same calendar window (3/3), and its most recent band is clearly negative — but the shared Portfolio policy is a confound I cannot separate

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## The discriminating test Round 245 named

Round 245 found XAU and BTC both strongest in the **150-300 days ago** band and
called it suggestive-not-established, naming the test: run a third instrument.

**bybit XAUT/USDT** was chosen — gold (the priority instrument), a genuinely
different venue and asset (spot Tether Gold, not a CFD), and calibrated as an
independent source in Round 210.

bybit XAUT/USDT 5m, `one_target`, hold 36, all costs zero:

| window | trades | gross PnL | gross per trade |
|---|---|---|---|
| 150 days | 150 | −0.325 | −0.00217 |
| 300 days | 398 | +1.371 | +0.00345 |

| sub-band (days ago) | trades | gross per trade | % of friction |
|---|---|---|---|
| **0-150** | 150 | **−0.00217** | **−31.0%** |
| **150-300** | 248 | **+0.00684** | **+97.7%** |

## Result — 3 of 3, and the third case is the sharpest

| instrument | 0-150 | 150-300 | stronger |
|---|---|---|---|
| exness XAU (CFD gold) | +0.00008 | +0.00182 | 150-300 |
| binance BTC (crypto perp) | +0.00056 | +0.00204 | 150-300 |
| **bybit XAUT (spot Tether Gold)** | **−0.00217** | **+0.00684** | **150-300** |

Three unrelated instruments on three different brokers, all strongest in the same
150-day calendar window. bybit XAUT is the sharpest case: its strong band reaches
**97.7% of friction** — the closest to break-even any measurement in this session
has produced — and its most recent band is **clearly negative** at −31%.

**Null probability, stated precisely rather than rounded in my favour:** this was
a *two-band* comparison per instrument, so under a coin-flip null, 3/3 in the same
direction is **1 in 8 (12.5%)**. On the two instruments where three bands exist
(Round 244-245), both peaking in the same one of three is **1 in 9**. Round 245
promised "1-in-9"; the test I actually ran on the third instrument was two-band,
so the honest combined statement is those two figures, not a single stronger one.

## The confound I cannot separate, and it matters

All three instruments run the **same strategy registry and the same Portfolio
decision policy**. The instruments are independent; **the policy is not**.

So two explanations remain observationally equivalent here:

1. **Market regime** — the 150-300 day window was favourable across assets, and
   any reasonable strategy would have shown it.
2. **Shared policy** — this particular policy happened to suit that period, and
   it would look the same on any instrument because it *is* the same policy.

Nothing measured so far distinguishes them. Round 228 already found that no single
price statistic (volatility, autocorrelation, efficiency, drift, range, body
ratio) tracks the transitions, which weakens the pure-regime story slightly, but
it does not settle it.

**The separating test would need a genuinely different policy** — a mechanically
unrelated strategy family evaluated over the same bands. If a different policy
also peaks at 150-300, regime; if it peaks elsewhere, the shared policy is doing
the work. That is a real experiment and it has not been run.

Until then the claim stays at: **the effect is shared across instruments, and its
source is not identified.**

## What this does to the deployment picture

The practical reading is unchanged and slightly worse. Whatever produced the
150-300 window has passed: the most recent 150 days read **+1.2%** (XAU), **+8.0%**
(BTC) and **−31.0%** (bybit XAUT) of friction. Two near zero, one clearly
negative.

## What is proven, and what is not

Proven:

- bybit XAUT 5m zero-cost `one_target`: 150d gives 150 trades and −0.325; 300d
  gives 398 and +1.371.
- Sub-bands: 0-150 −0.00217 (−31.0% of friction), 150-300 +0.00684 (+97.7%).
- All three instruments are stronger in 150-300 than in 0-150 — 3 of 3, null
  probability 1/8 for this two-band form.

Not proven, and deliberately not claimed:

- That this is a market regime. The shared Portfolio policy is an unseparated
  confound and the distinguishing experiment has not been run.
- Conventional statistical significance. 150-248 trades per band, no confidence
  intervals, and 1/8 is suggestive at best.
- That the designs are identical across instruments. XAU and BTC were carved into
  three bands, bybit XAUT into two.
- Independence of the bands. Nested subtraction, leaning on Round 226 as flagged
  since Round 242.
