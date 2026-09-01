# Round 327 — NEEDS-MORE-RESEARCH: the fleet is **complete**. `exness XAU` is still uniquely positive before costs on the **matched five**, the frequency-Sharpe relation strengthens to **ρ = −0.900** — and my own pre-registered significance threshold was **mis-specified**.

Classification: **NEEDS-MORE-RESEARCH** — the primary pre-registration holds across five
matched routes; the secondary criterion was wrong arithmetic on my part and the corrected
reading leaves the relation an observation. Two bounded Docker sweeps (exactly the
2-container budget), **XAU included**.

## The gaps Round 326 named

*"Anything about `bybit BTC` or `binance XAU`. Two of six routes still have no gate run;
`binance XAU` cannot reach `--days 500` at all (262 days of history)."* And the
frequency-versus-Sharpe observation was underpowered at n = 4.

This round runs **`bybit BTC` at 500 days** — the fifth cell of the matched set — and
**`binance XAU` at 250 days**, the only depth it can reach, reported separately.

**Pre-registered:**
1. `exness XAU` remains the **only** matched route with positive `gross_pnl_before_costs`.
   Refuted if `bybit BTC` is also positive.
2. With n = 5, if |ρ| ≥ 0.9 the exact two-sided p reaches 0.0167 and the frequency
   relation becomes significant at 5%.

## The completed matched fleet

All at `--days 500`, deployed costs, holdout starting **2026-05-22**:

| route | days | trades | tr/wk | pos-day | streak | Sortino | Sharpe | cost÷gross | **gross** | net |
|---|---|---|---|---|---|---|---|---|---|---|
| **`exness XAU/USD`** | 84 | 126 | 8.95 | 0.429 | 4 | −1.152 | **−0.814** | 1.38 | **+0.6000** | −0.2283 |
| `bybit XAUT/USDT` | 101 | 64 | 4.48 | 0.366 | **14** | −1.972 | −1.402 | **30.35** | −0.0135 | −0.4219 |
| **`bybit BTC/USDT`** | 101 | 172 | **12.04** | 0.386 | 8 | −5.447 | **−4.955** | 1.12 | **−1.2653** | −2.6862 |
| `binance BTC/USDT` | 101 | 312 | 21.84 | 0.416 | 7 | −6.817 | −6.753 | 1.20 | −1.7909 | −3.9406 |
| `exness BTC/USD` | 101 | 351 | **24.58** | 0.406 | 6 | −7.514 | **−7.558** | 1.12 | −2.1633 | −4.5772 |

**Pre-registration 1 holds:** `exness XAU` is the only matched route with positive gross
PnL before costs. `bybit BTC` comes back at **−1.2653** and fails `gross_pnl_positive`
like the other three.

**Sharpe is negative on all five matched routes**, and on all seven route-windows gated
so far.

## `binance XAU`, reported separately

It cannot reach 500 days (262 days of 5m history), so it is **not in the matched set**:

| route | holdout | days | trades | tr/wk | Sortino | Sharpe | cost÷gross | **gross** | net |
|---|---|---|---|---|---|---|---|---|---|
| `binance XAU/USDT` @250 | 07-11→08-30 | **51** | 29 | 4.06 | −1.298 | −0.879 | 2.41 | **+0.0797** | −0.1125 |

Its holdout is **51 days — below the gate's own 90-day minimum**, which it fails
explicitly. But its gross is **positive (+0.0797)**.

**That matters for how the fleet claim is phrased.** "The only route positive before
costs" is true **on the matched set**; across all six routes at whatever depth each can
reach, **two** are positive — `exness XAU` on a 84-day matched holdout and `binance XAU`
on a 51-day sub-minimum one. I am stating both rather than keeping the tidier sentence.

Note `binance XAU` also fits the frequency pattern: 4.06 trades/week and Sharpe −0.879,
among the least-bad.

## The frequency relation, and my mis-specified threshold

Sorted by trade rate across the five matched routes:

| route | tr/week | Sharpe | gross |
|---|---|---|---|
| `bybit XAUT` | 4.48 | −1.402 | −0.0135 |
| `exness XAU` | 8.95 | **−0.814** | **+0.6000** |
| `bybit BTC` | 12.04 | −4.955 | −1.2653 |
| `binance BTC` | 21.84 | −6.753 | −1.7909 |
| `exness BTC` | 24.58 | −7.558 | −2.1633 |

**Spearman(trades/week, Sharpe) = −0.900**, up from −0.800 at n = 4. The ordering is
**one adjacent swap from perfect** — only `exness XAU` and `bybit XAUT` are transposed.

**But my pre-registered threshold was wrong.** I registered that |ρ| ≥ 0.9 would reach
p = 0.0167 at n = 5. It does not. Computing the exact permutation distribution:

| \|ρ\| ≥ | exact two-sided p (n = 5) |
|---|---|
| 1.0 | **0.0167** |
| **0.9** | **0.0833** |
| 0.8 | 0.1333 |
| 0.7 | 0.2333 |

Only a **perfect** ρ = ±1.0 reaches 0.0167 at this sample size. The observed −0.900 gives
**p = 0.0833** — closer than the 0.3333 at n = 4, still **not significant at 5%**, and
still an observation. I registered a criterion I had not computed, and I am recording
that rather than quietly reporting the corrected number.

## What is proven, and what is not

Proven:

- `bybit BTC` daily-profit-gate at `--days 500`: 172 trades, 12.04/week, Sharpe −4.955,
  Sortino −5.447, gross **−1.2653**, net −2.6862, `passed=false`.
- `binance XAU` at `--days 250`: 51-day holdout, 29 trades, 4.06/week, Sharpe −0.879,
  gross **+0.0797**, `passed=false` including `minimum_holdout_days`.
- Across the five matched routes, `exness XAU` is the only one with positive gross;
  Sharpe and Sortino are negative on all five.
- Spearman(trades/week, Sharpe) = −0.900 on the matched five, exact two-sided p = 0.0833;
  the exact distribution gives p = 0.0167 only at |ρ| = 1.0.

Not proven, and deliberately not claimed:

- **That trade frequency causes worse risk-adjusted performance.** ρ = −0.900 with
  p = 0.083 on five routes that differ in instrument, broker and market type. Round 274's
  ATR-band lever agrees in direction by an independent method; neither is causal evidence.
- That `binance XAU`'s positive gross is comparable to `exness XAU`'s. Its holdout is 51
  days, below the gate's own minimum, on a route whose live checkpoint market data ends
  2025-12-25 (Rounds 207, 306). It is reported, not weighed.
- That the matched holdouts are identical in length. `exness XAU` has 84 observed days
  against 101 for the others — the gold CFD weekend closure, unchanged from Round 326.
- Any candidate improvement or promotion. **All six routes fail the gate**, every one on
  Sharpe, Sortino, positive-day ratio and cost÷gross.
- SQN, information ratio or maximum consecutive losing trades — still unavailable
  (Round 324).
