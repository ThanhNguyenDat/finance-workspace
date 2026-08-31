# Round 276 — QUALIFICATION: σ² governs hold duration, not Portfolio frequency. `bybit BTC` runs at 5.55/week on identical volatility and also fails Target 3.

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps (exactly the
2-container budget). The pre-registered refutation criterion fired.

## The demanding test, registered before the runs

Round 275 confirmed the σ² law but admitted its test was **favourable**: the pair was
chosen far apart in volatility, giving σ² a large signal. The demanding version is
the opposite, and it was written to disk before either container launched
(`precommit_r276.md`):

> The three BTC routes' 5m volatilities are 0.14218%, 0.14371%, 0.14406% — a **1.3%
> spread**, so σ² predicts their frequencies within ~2.7% of each other. `binance BTC`
> is already at 9.42/week. **Prediction: both new routes inside 8.9-10.0/week.
> Refuted/qualified if either lands outside 8.0-11.0.**

| route | vol (5m) | trades | **/week** | pnl/trade | Target 3 |
|---|---|---|---|---|---|
| exness BTC/USD | 0.14218% | 364 | **9.80** | −0.00996 | PASS |
| binance BTC/USDT | 0.14371% | 350 | 9.42 | −0.00971 | PASS |
| **bybit BTC/USDT** | 0.14406% | 206 | **5.55** | −0.01149 | **FAIL** |

**`exness BTC` landed inside the band. `bybit BTC` landed at 5.55 — far outside.**
Frequency spread **1.77x** against a volatility spread of 1.013x (σ² → 1.027x).

**The criterion I set fired. The law is qualified: σ² is not the whole story for
Portfolio frequency.**

## The reconciliation — and it was already in Round 272

Round 272 established the identity `frequency = occupancy × 168 / hold`. Round 273
then showed σ² governs **hold** (hold × σ² constant to 16% across six routes), and
Rounds 273/275 quietly treated that as governing **frequency**. It does not, because
**occupancy is a second, independent term** — and Round 272 measured occupancy
varying from 59.6% to 86.7%, a **1.45x spread**, across routes.

So `bybit BTC` can sit at identical volatility, hold for a σ²-consistent duration,
and still trade far less often if it is in position a smaller fraction of the time.
Round 275's clean 2.8% hit was partly luck: `binance XAU` (63.5%) and `binance BTC`
(59.6%) happen to have **similar occupancy**, so the occupancy term nearly cancelled
and σ² alone predicted well.

Consistent with this, `bybit BTC` was already the **worst fit** in Round 273's table
(hold × σ² = 0.2520 against `binance BTC`'s 0.2263, an 11% deviation) — but its
Portfolio frequency deviates by **77%**, far more. The extra factor therefore acts
at the Portfolio layer, not in exit timing.

**I have not measured `bybit BTC`'s occupancy.** The reconciliation above is
arithmetically forced by the identity but the specific term is untested, and after
Rounds 252/254/261/263 I am not presenting a fitting explanation as a measurement.

## The operational picture, updated

`one_target` under deployed parameters, 260 days unless noted:

| route | /week | Target 3 (≥7) |
|---|---|---|
| exness BTC | 9.80 | pass |
| binance BTC | 9.42 | pass |
| exness XAU | 7.06 (360d) | pass by **0.9%** |
| **bybit BTC** | **5.55** | **FAIL** |
| **binance XAU** | **3.63** | **FAIL** |
| bybit XAUT | not measured | — |

**Two of five measured routes fail Target 3, and a third passes by under 1%.** And
this breaks Round 275's tidy reading — the failure is *not* confined to low-volatility
instruments. `bybit BTC` is as volatile as the two passing BTC routes and still
fails.

## What is proven, and what is not

Proven:

- The prediction and its refutation criterion were on disk before launch.
- `one_target`, deployed parameters, matched 260-day window: exness BTC 364 trades
  (9.80/week), bybit BTC 206 (5.55/week).
- Frequency spread 1.77x across three routes whose volatility spreads 1.3%.
- Two of five measured routes fail Target 3.

Not proven, and deliberately not claimed:

- **That occupancy explains `bybit BTC`.** It is the only free term in an identity
  that must balance, but it was **not measured on that route**. That is the next
  round's first job.
- That σ² is wrong about hold duration. Round 273's evidence stands; what is
  qualified is the step from hold to frequency, which Rounds 273 and 275 took without
  justifying it.
- That `bybit BTC` fails Target 3 in production. 260-day backtest, same caveat as
  Round 275.
- Any cause for a route-level occupancy difference. Not investigated.
- Anything about `bybit XAUT`, still unmeasured under `one_target`.
