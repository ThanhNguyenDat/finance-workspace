# CORRECTION (Round 243)

The **"two routes, two different diseases"** conclusion below is **withdrawn**.
Round 243 band-decomposed BTC the way Round 242 did XAU: BTC's most recent 450
days are **positive** (+0.00078/trade, 11% of friction), close to XAU's
+0.00107 (15%). Its full-window negative comes entirely from the two older bands
(-0.00142 and -0.00095). Both routes have the **same shape** — oldest negative,
most recent positive — and I reached the opposite conclusion by comparing XAU's
decomposed picture against BTC's undecomposed aggregate, the same aggregation
error Round 242 had just corrected for XAU.
The measurements in this file stand; the interpretation does not.
See `round243-btc-recent-band-is-positive-too-the-two-diseases-claim-was-wrong.md`.

---

# Round 241 — Portfolio gross edge measured over the full five years: XAU is +5% of friction and BTC is **negative with zero costs**

Classification: **NO-CHANGE**. Two bounded Docker sweeps.

## What was measured, and the trap avoided

Rounds 213-217 and 234 established the narrative "positive gross edge, destroyed
by friction". Every one of those measurements was either Alpha-layer or, in Round
234's case, the Portfolio gate on **holdout only** (~360 days). The Portfolio
layer's gross edge over the **full 1,800-day window** had never been measured.

`one_target`, 5m, 1,800 days, hold 36, with all costs zeroed:

| route | trades (costed) | net PnL | trades (zero-cost) | **gross PnL** | **gross per trade** |
|---|---|---|---|---|---|
| exness XAU | 830 | −5.262 | 1,787 | +0.683 | **+0.00038** |
| binance BTC | 3,825 | −28.183 | 3,312 | **−2.658** | **−0.00080** |

**The trap, stated before the result is read:** the costed and zero-cost runs
produce *different trade counts* — 830 vs 1,787 on XAU, a 2.2x difference. Costs
shift execution prices, which changes which positions hit their protective levels
and therefore the entire trade sequence. **A gross-minus-net subtraction across
these runs is invalid**, exactly the non-orthogonality error of Round 214. Each
run's per-trade figure is computed from its own count and nothing is subtracted.

(This also stands as a methodology note: cost settings materially change trade
counts at the Portfolio layer, unlike the history length which Round 226 proved
is clean.)

## The result qualifies the session's central narrative

**BTC's deployed Portfolio policy loses money with zero fees, zero slippage and
zero funding** — −0.00080 per trade over 3,312 trades. Not "the edge is smaller
than friction"; over five years there is no edge to be smaller.

**XAU's gross edge is positive but negligible**: +0.00038 per trade against a
friction of roughly 0.0070 — about **5% of friction**.

Round 234's gate reported *both* routes with positive gross PnL (+0.475 XAU,
+0.281 BTC), but that gate evaluates **holdout only**. So:

| | holdout ~360d (Round 234 gate) | full 1,800d (this round) |
|---|---|---|
| XAU gross | positive, cost/gross 3.22 | positive, ~5% of friction |
| BTC gross | positive, cost/gross 48.2 | **negative** |

**"Positive gross edge killed by friction" is a recent-window property.** It is
true for XAU on both spans and true for BTC only on the recent one. Over the full
history BTC's Portfolio signal is negative before any cost is charged.

That is consistent with Round 227's walk-forward, which measured the two oldest
XAU segments as negative, and with Round 225's finding that the best BTC candidate
was weak over 900→180 days ago. The system looks better the more recent the window
you evaluate it on, and this round shows that effect is strong enough to flip the
sign of BTC's gross edge.

## What this does to the model

Rounds 236-240 built the model "loss = trades × a constant, and no Portfolio lever
moves the constant". That stands — it was measured on costed runs and this round
does not touch it.

What changes is the interpretation of *why* the constant is negative. For XAU it
is friction dominating a small real edge. **For BTC over the full window it is not
friction at all** — the signal is negative to begin with, and friction merely
deepens it. Two routes, two different diseases, previously described as one.

## What is proven, and what is not

Proven:

- `one_target`, zero costs, 1,800 days: exness XAU gives 1,787 trades and +0.683
  (+0.00038/trade); binance BTC gives 3,312 trades and −2.658 (−0.00080/trade).
- Costed and zero-cost runs differ in trade count by 2.2x (XAU) and 1.15x (BTC),
  so cross-run subtraction is invalid at this layer.

Not proven, and deliberately not claimed:

- A clean gross/friction split for either route. The differing counts prevent it;
  only each run's own per-trade figure is quoted.
- That Round 234's gate is wrong. It measures a different span and both readings
  are internally consistent; the disagreement *is* the finding.
- That XAU's +0.00038 is meaningfully positive. It is 5% of friction on one
  window, and Rounds 230-232 showed figures at this scale are not distinguishable
  from noise without a spread, which was not computed here.
