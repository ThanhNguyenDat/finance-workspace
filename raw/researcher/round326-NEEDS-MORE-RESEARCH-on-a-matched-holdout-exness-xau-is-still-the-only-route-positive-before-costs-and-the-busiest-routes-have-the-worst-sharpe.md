# Round 326 — NEEDS-MORE-RESEARCH: on a **matched holdout**, `exness XAU` is still the **only route positive before costs**. And the two **busiest** routes have the **worst Sharpe** — a tension with Target 3, on four points.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered test survives its own named
weakness; a frequency-versus-risk tension appears but is underpowered. Two bounded
Docker sweeps (exactly the 2-container budget), **XAU-first**.

## The gap Round 325 named

Round 325 closed with: *"`exness XAU`'s two [holdouts] are different periods, so its
cross-route comparison of gross sign is **not** matched — running `exness XAU` at 500
days would fix that and was not done."*

That is the load-bearing weakness in the fleet's one positive claim. This round runs
**`exness XAU` at `--days 500`** to match, and spends the second container on
**`exness BTC`**, the sign-ambiguous cell from Round 315, which had never been gated.

**Pre-registered:** if `exness XAU` is still the **only** route with positive
`gross_pnl_before_costs` when the holdout is matched, the claim survives; if it comes
back negative, "the only route positive before costs" was a **period artifact** and
falls.

## The matched-holdout fleet

All four at `--days 500`, deployed costs, holdout starting **2026-05-22**:

| route | holdout end | days | trades | tr/wk | pos-day | streak | Sortino | Sharpe | cost÷gross | **gross** | net |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **`exness XAU/USD`** | 08-28 | 84 | 126 | 8.95 | 0.429 | 4 | −1.152 | **−0.814** | 1.38 | **+0.6000** | −0.2283 |
| `bybit XAUT/USDT` | 08-30 | 101 | 64 | 4.48 | 0.366 | **14** | −1.972 | −1.402 | **30.35** | −0.0135 | −0.4219 |
| `binance BTC/USDT` | 08-30 | 101 | 312 | 21.84 | 0.416 | 7 | −6.817 | −6.753 | 1.20 | −1.7909 | −3.9406 |
| **`exness BTC/USD`** | 08-30 | 101 | 351 | **24.58** | 0.406 | 6 | **−7.514** | **−7.558** | 1.12 | **−2.1633** | **−4.5772** |

**`exness XAU` remains the only route with positive gross PnL before costs (+0.6000).**
The pre-registration holds — the claim was not a period artifact. All three others fail
the gate's `gross_pnl_positive` check.

**Holdout match, stated honestly:** the start dates are identical; `exness XAU` ends
2026-08-28 (84 observed days) while the others end 2026-08-30 (101). That is the gold
CFD weekend closure — `exness BTC` is also an Exness CFD and *does* trade the weekend, so
the difference is the instrument's market calendar, not a design flaw. Much better
matched than Round 325, **not exact**, and not fixable.

## Sharpe is now negative on six of six route-windows

| route-window | Sharpe |
|---|---|
| `exness XAU` @360 | −2.329 |
| `exness XAU` @500 | −0.814 |
| `exness XAU` @900 | −0.861 |
| `exness BTC` @500 | **−7.558** |
| `bybit XAUT` @500 | −1.402 |
| `binance BTC` @500 | −6.753 |

Six of six, plus positive-day ratio below 0.55 and cost÷gross above 0.5 on all six. As
in Round 325, none of this involves differencing across windows.

`exness BTC` is the **worst route in the fleet** on this holdout: the highest trade rate
(24.58/week), the worst Sharpe and Sortino, and the most negative gross and net. It also
fails `holdout_interval_continuity`, which the other three do not.

## The observation worth flagging: busier is worse

Sorted by trade rate on the matched holdout:

| route | tr/week | Sharpe | gross |
|---|---|---|---|
| `bybit XAUT` | 4.48 | −1.402 | −0.0135 |
| `exness XAU` | 8.95 | −0.814 | **+0.6000** |
| `binance BTC` | 21.84 | −6.753 | −1.7909 |
| `exness BTC` | 24.58 | −7.558 | −2.1633 |

**The two routes above 20 trades/week have Sharpe near −7; the two below 9 have Sharpe
near −1.** Spearman(trades/week, Sharpe) = **−0.80**, exact two-sided **p = 0.333** on
n = 4 — **not significant**, and I am recording it as an observation only.

It matters because it points the opposite way to **Target 3**, which pushes trade
frequency **up**. If the direction is real, raising frequency would move routes toward
the `exness BTC` corner. Four points cannot establish that, and Round 274 already found
a frequency lever that bought 2.43x trades for 2.27x loss — consistent in direction,
independent in method. I am **not** claiming a causal relationship.

## What is proven, and what is not

Proven:

- `exness XAU` and `exness BTC` daily-profit-gate at `--days 500`, deployed costs, both
  `passed=false`; holdouts start 2026-05-22 on all four routes measured.
- Metrics as tabulated, including `exness XAU` gross **+0.6000** / Sharpe −0.814, and
  `exness BTC` gross **−2.1633** / Sharpe **−7.558** / 24.58 trades per week.
- `gross_pnl_positive` passes only on `exness XAU`; the other three fail it.
- Sharpe and Sortino are negative on all six route-windows gated so far; positive-day
  ratio is below 0.55 and cost÷gross above 0.5 on all six.
- Spearman(trades/week, Sharpe) = −0.80 across the four matched-holdout routes, exact
  two-sided p = 0.333.

Not proven, and deliberately not claimed:

- **That trade frequency causes worse risk-adjusted performance.** Four points, p = 0.33,
  and the routes differ in instrument, broker and market type as well as in rate. Round
  274's independent finding points the same way; neither establishes causation.
- That the holdouts are exactly matched. `exness XAU` has 84 observed days against 101
  for the others, because gold CFD does not trade weekends. The start dates match.
- Anything about `bybit BTC` or `binance XAU`. Two of six routes still have **no** gate
  run; `binance XAU` cannot reach `--days 500` at all (262 days of history).
- That `exness XAU`'s positive gross is economically meaningful. +0.6000 in the
  simulator's notional units over 84 days, on a route whose net is −0.2283 and whose
  cost÷gross is 1.38 — it still needs costs cut by roughly 28% just to break even on
  this holdout, and the gate requires cost÷gross ≤ 0.5.
- Any candidate improvement or promotion. Every route fails the gate.
