# "THE GUARD BARELY MATTERS HERE" WAS THE WRONG READING (Round 361)

This file measured guard-at-36 against guard-free on `exness XAU` at **0.44%** and that was taken
to mean the route is insensitive to the guard. **It is not.** On a validity-gated same-window
test, moving the parameter **36 → 72** on that route improves `one_target` PnL by **+36.0%**
(−1.57256 → −1.00705).

The two quantities differ: the **first** 36 decisions of hold are worth roughly nothing there, the
**next** 36 are worth 36%. A missing level effect says nothing about the parameter's marginal
leverage. This file's cross-route measurements stand; only the inference about `exness XAU`'s
sensitivity is withdrawn. See `round361-NEEDS-MORE-RESEARCH-the-hold-lever-transfers-to-exness-xau-at-36-percent-on-a-validity-gated-same-window-test.md`.

---

# THE GUARD IS ALSO A TUNABLE LEVER (Round 359)

This file showed the minimum-hold guard is a first-order effect where it bites. Moving it —
**36 → 72**, a deployed production parameter that had never been tuned — improves `one_target`
PnL by **+42.1%** on `binance BTC` (−4.74869 → −2.74744) and **+20.9%** on `bybit XAUT`
(−1.57738 → −1.24701), monotone across all three points on each route. On `binance BTC` the
frequency still clears Target 3 at **7.24/week**.

Both routes still lose, and the lever **cannot be scored on a holdout** — `--portfolio-minimum-hold-decisions`
conflicts with `--daily-profit-gate` precisely because the gate does not model the guard. See
`round359-NEEDS-MORE-RESEARCH-the-minimum-hold-lever-cuts-losses-42-percent-and-cannot-be-validated-on-holdout.md`.

---

# Round 358 — REJECTED: Round 356's *"the guard is immaterial in magnitude"* is **specific to `exness XAU`**. On `binance BTC` the minimum-hold guard cuts the loss by **41%**. And Round 357's live-rate comparison used a **biased denominator** — correcting it flips the direction.

Classification: **REJECTED** — a pre-registered extension of my own Round 356 finding fails, and a
statistical error in Round 357 is found and corrected. Two bounded Docker sweeps (exactly the
2-container budget) plus narrow read-only production inspection.

## Part 1 — the guard's impact does not generalise

Round 356 measured `|one_target − legacy| / |legacy|` on `exness XAU` at 0.44% / 3.83% / 1.94%
across three windows and concluded the gate's omission of the construction guard is *immaterial in
magnitude*. That was three windows on **one route**.

**Pre-registered as a partition:** D = the maximum of that ratio over two routes never tested for
it. **D ≥ 0.20** → the guard materially changes outcomes elsewhere and Round 356's conclusion does
not generalise; **D < 0.20** → it extends.

`--days 500`, deployed band, `minimum_hold_decisions 36`, plain `--json`:

| route | `one_target` | `legacy` | trade reduction | `one_target` PnL | `legacy` PnL | **rel. diff** |
|---|---|---|---|---|---|---|
| **`binance BTC`** | 689 | 990 | **0.3040** | **−4.74869** | **−8.07260** | **0.4118** |
| **`bybit XAUT`** | 247 | 309 | 0.2006 | −1.57738 | −1.96680 | **0.1980** |
| `exness XAU` @300 (r356) | 280 | 355 | 0.2113 | −1.32216 | −1.32799 | 0.0044 |

**D = 0.4118 — MATERIAL.** On `binance BTC` the guard removes 30% of trades and cuts the loss by
**41%** (−8.07 → −4.75). On `bybit XAUT` it removes 20% of trades and 19.8% of the loss.

**So the gate — which scores the guard-free stream (Round 356) — systematically overstates losses
on routes where the guard bites.** Its BTC verdicts are **pessimistic** by a large margin, and its
`exness XAU` verdicts happen to be nearly right because on that route the guard changes trade
count without changing PnL. Round 356's "immaterial" claim is withdrawn as a general statement and
kept as an `exness XAU` observation.

## Part 2 — Round 357's rate comparison was measured wrong

Round 357 computed live trade rates as *closes ÷ (last entry − first entry)*. **That denominator
conditions on the events themselves** — a classic bias — and it inflates the rate. The correct
denominator is the **observation window**.

Two facts were verified this round, both of which Round 357 flagged as unread:

- **The writer is append-only.** `finance-redis/src/trade_log.rs` contains `ZADD` only — no
  `ZREMRANGEBYRANK`, no `ZREMRANGEBYSCORE`, no `EXPIRE`, no `DEL`. There is **no cap**, so the
  Round 357 follow-up ("wait and re-read") is valid.
- **Three entries really are one trade.** The payloads show the same `entry_at`
  2026-08-26T00:04:59.999Z, `exit_at`, entry and exit price under **three paper scopes** —
  `paper-risk-2pct`, `paper-compounding-10pct`, `paper-fixed-pct` — differing only in `quantity`
  and `realized_pnl`. **Round 357's counts were right**: closes = entries ÷ 3.

Redis started **2026-08-22 05:26 UTC** (uptime 8 days, `loading: 0`). Correcting the denominator:

| window | `exness XAU` | `binance BTC` | `bybit BTC` | `exness BTC` |
|---|---|---|---|---|
| **8.67 d** (Redis uptime) — live/wk | 0.81 | 4.84 | 3.23 | 3.23 |
| 95% CI | [0.02, 4.50] | [1.78, 10.54] | [0.88, 8.27] | [0.88, 8.27] |
| backtest/wk | 5.05 **OUT** | 21.84 **OUT** | 12.11 **OUT** | 24.58 **OUT** |
| **3.40 d** (worker uptime) — live/wk | 2.06 | 12.35 | 8.24 | 8.24 |
| 95% CI | [0.05, 11.47] | [4.53, 26.89] | [2.24, 21.09] | [2.24, 21.09] |
| backtest/wk | 5.05 in | 21.84 in | 12.11 in | 24.58 **OUT** |

Under the **full Redis window, five of six routes have their backtest rate outside the live 95%
interval, all in the direction of the backtest predicting far more trading than happens** — 4.5x
to 7.6x. Under the **worker window**, only `exness BTC` is outside.

**Which window is right is not resolvable from the retained data.** The first entries appear
2026-08-27/28, matching the worker deploy; but the one `exness XAU` trade has `entry_at`
**2026-08-26**, before that deploy, which shows a position survived the restart and says nothing
about when logging began. **So the verdict is genuinely undetermined**, and Round 357's "no
inconsistency detected" was reached with the wrong denominator rather than by this reasoning.

## A free confirmation from the live payload

The single `exness XAU` close carries
`contributing_strategies: [candle_momentum −0.6296, mtf_stochastic_5m_4h_sma5 0.0,
rsi_mean_reversion 0.0]`.

**Two of the three deployed strategies carried weight exactly 0.0 on a live trade.** The weight
collapse this arc inferred from `alpha_performance_quality` (all-loser strategies drive
`empirical` to 0) is visible in production, on a real closed trade — the first direct evidence for
it outside the replay. The trade held 2.6 days, closed `take_profit`, `return_fraction` +1.88%.

## What is proven, and what is not

Proven:

- The three-route guard table above; D = 0.4118.
- `trade_log.rs` writes with `ZADD` only; no trim, expiry or delete anywhere in the module.
- Trade-log payloads: one economic trade written under three paper scopes with identical
  entry/exit and differing quantity — closes = entries ÷ 3.
- Redis start 2026-08-22 05:26 UTC, uptime 8 days, `loading: 0`, `aof_enabled: 0`.
- Both Poisson tables above.
- The live `contributing_strategies` weights on the one `exness XAU` close.

Not proven, and deliberately not claimed:

- **Which observation window applies.** The two candidates give opposite verdicts and the retained
  data does not settle it. I am **not** reporting a live-versus-backtest discrepancy as a finding.
- That the guard would improve the gate's BTC verdicts by 41%. That figure is **full-window
  `one_target` versus `legacy`**, not a holdout gate metric; the direction is established, the
  size for the gate's own window is not.
- That the guard's bite is a route property. Three routes, one window each except `exness XAU`;
  and on `exness XAU` the guard cut 21% of trades while moving PnL 0.4%, so trade-count and PnL
  effects are clearly separable and neither predicts the other.
- That two-of-three zero weights is typical. **One live trade.**
- Any promotion. Every configuration measured still loses.
