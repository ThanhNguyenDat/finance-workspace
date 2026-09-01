# Round 312 — REJECTED: the confound gets **worse** with depth, not better. One day moves **+50 trades** at 900 days against +5 at 260 — and `binance BTC`'s Target 3 verdict **straddles the bar**.

Classification: **REJECTED** — my pre-registered prediction failed, and with it the
corollary I drew from Round 311's own mechanism. Two bounded Docker sweeps (exactly the
2-container budget). BTC-scoped: this tests the route carrying the fleet's last
unqualified pass.

## The prediction, and why I made it

Round 311 closed by naming what it had not done: *"it explains the direction and the
mechanism; it does not predict −42 trades at nine days, and I did not attempt a
quantitative model."*

That mechanism makes a corollary I can test. Quality is `1 − min(trades/20, 1)` for a
loser, floored at 0.05. As a window lengthens, **every** interval eventually passes 20
trades, every quality hits the floor, and `normalize_or_uniform_weights` returns them
to **uniform 1/8** — so there should be less weight trajectory left to perturb.

**Registered before running:** at 900/901 days the one-day perturbation moves
`one_target` by **fewer than 5 trades** in magnitude — smaller than the +5 measured at
260/261 in Round 302. Refuted at ≥5 or if negative.

## The result

| `--days` | candles | **`one_target`** | legacy | grid | cost | Alpha 5m | **rate/week** | margin |
|---|---|---|---|---|---|---|---|---|
| 900 | 259,198 | **862** | 1,178 | 12,414 | 62 | 1,110,899 | **6.704** | **−4.2%** |
| 901 | 259,486 | **912** | 1,251 | 13,370 | 68 | 1,112,168 | **7.085** | **+1.2%** |

**One extra day moves `one_target` by +50 trades.** The genuine content of that day at
the route's own 900-day rate is **0.96 trades** — a **52x** overshoot. `legacy_selected_rule`
moves +73 and `legacy_grid` +956 (+7.7%) from the same single day.

**The prediction is refuted, and by a factor of ten:**

| perturbation | Δ `one_target` | Δ rate |
|---|---|---|
| 260 → 261 days (Round 302) | **+5** | +1.04% |
| **900 → 901 days** (this round) | **+50** | **+5.68%** |

**The confound is 10x larger at the deeper window.** Round 311's maturity argument
predicts the opposite, so that mechanism is at best **incomplete**: it explains why
short windows over-weight long intervals, but it does not explain why perturbation
sensitivity *grows* with depth. I am not proposing a second mechanism — Rounds 279-284
are the standing reason, and I have just watched one of my own mechanisms make a wrong
prediction.

The Alpha control behaves as always: **4.406 trades per added candle**, against 4.628
on the same route in Round 302 — consistent, positive, monotone.

## `binance BTC` no longer has a clean pass

Every window measured on this route today, at the deployed config:

| `--days` | trades | rate/week | margin | verdict |
|---|---|---|---|---|
| 260 | 350 | 9.423 | +34.6% | pass |
| 261 | 355 | 9.521 | +36.0% | pass |
| 270 | 313 | 8.115 | +15.9% | pass |
| 280 | 334 | 8.350 | +19.3% | pass |
| **900** | **862** | **6.704** | **−4.2%** | **FAIL** |
| **901** | **912** | **7.085** | **+1.2%** | pass |

**Five pass, one fails, and the bar sits between two windows one day apart.** Spread
across the six: **34.3%** of the mean.

Two things must be separated here, and Rounds 302 and 305 did not have to:

- **The level** at 900 days (6.7/week against 9.4 at 260) may be **genuine history**.
  Round 293 already measured this route's deeper slices lower — 6.26/week at
  `[360,540]` — so a long window averaging in quieter years is expected, not a defect.
- **The straddle** is **not** genuine. 6.704 and 7.085 come from windows differing by
  one day; the bar falls between them purely on measurement noise.

So `binance BTC`'s pass is a property of **recent** windows. Rounds 302 and 305
recorded it as a pass with a shrinking cushion; it should now read as **pass on
260-280-day windows, undetermined at depth** — the same status `exness XAU` reached in
Round 304, arrived at from the other direction.

## What is proven, and what is not

Proven:

- `binance BTC` at the deployed config, same day, same endpoint: `one_target` = 862 at
  900 days and 912 at 901; rates 6.704 and 7.085/week.
- One-day Δ `one_target` = **+50** at 900/901 against **+5** at 260/261 — a **10x**
  larger response at the deeper window, and a 52x overshoot against the day's own
  content.
- `legacy_selected_rule` +73, `legacy_grid` +956, `execution_cost` +6 over the same day.
- Alpha 5m 1,110,899 → 1,112,168 = 4.406 trades per added candle, monotone.
- Across six same-day windows the rate runs 6.704-9.521/week, spread 34.3% of the mean,
  with five passes and one fail.
- realized_pnl −5.10 and −3.79 — negative on both.

Not proven, and deliberately not claimed:

- **Any mechanism for why sensitivity grows with depth.** Round 311's maturity argument
  predicts the opposite and has just failed a test; I am not replacing it with a guess.
- That `binance BTC` fails Target 3. It passes on five of six windows, and the 900-day
  level plausibly reflects genuinely quieter historical periods (Round 293). What is
  claimed is that **the verdict is not window-independent**, which is a different and
  weaker statement.
- That the 900-day level is trustworthy as a *level*. It is one window, and Rounds
  300-305 apply to it as much as to any other.
- That +50 is the worst case. One perturbation, one depth pair; Round 304 already
  showed these numbers only grow as the probe widens.
- Anything about `exness BTC`, `bybit BTC` or `binance XAU` — still no perturbation run
  on three of six routes.
