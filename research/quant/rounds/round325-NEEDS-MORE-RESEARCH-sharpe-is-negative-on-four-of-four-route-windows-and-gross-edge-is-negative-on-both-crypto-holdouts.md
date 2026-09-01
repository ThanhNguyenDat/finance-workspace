# Round 325 — NEEDS-MORE-RESEARCH: **Sharpe and Sortino are negative on four of four route-windows** — the first fleet-level statement that needs no differencing. And **gross edge before costs is negative** on both crypto holdouts.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered fleet criterion is met; a
new period effect opens. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first** among the routes that can reach the window.

## The limit Round 324 named

Round 324 delivered the session's first joint-objective evaluation but on one route:
*"Anything about the other five routes. One route. The gate was not run on
`binance BTC`, `exness BTC`, `bybit BTC`, `bybit XAUT` or `binance XAU`."*

This round adds **`bybit XAUT`** (the other XAU route that can reach a deep window;
`binance XAU` has only 262 days) and **`binance BTC`** (the flagship), both at
`--days 500` so their holdouts match exactly.

**Pre-registered, following Rounds 315-317's practice of registering the
interpretation:** if Sharpe is negative on **every** route measured, that is a
fleet-level property of the deployed policy that depends on **no window comparison** —
the first such statement this arc can make. If any route shows positive Sharpe, the
fleet is heterogeneous on the joint objective too.

## The four scorecards

| route / window | holdout | days | trades | tr/wk | pos-day | streak | Sortino | Sharpe | cost÷gross | **gross** | net |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `exness XAU` @360 | 06-19→08-28 | 60 | 86 | 8.51 | 0.417 | 4 | −3.104 | −2.329 | 9.89 | **+0.0535** | −0.4750 |
| `exness XAU` @900 | 03-04→08-28 | 151 | 174 | 6.85 | 0.404 | 5 | −1.179 | −0.861 | 1.53 | **+0.7812** | −0.4118 |
| **`bybit XAUT` @500** | **05-22→08-30** | 101 | 64 | **4.48** | 0.366 | **14** | −1.972 | −1.402 | **30.35** | **−0.0135** | −0.4219 |
| **`binance BTC` @500** | **05-22→08-30** | 101 | 312 | **21.84** | 0.416 | **7** | **−6.817** | **−6.753** | 1.20 | **−1.7909** | −3.9406 |

Thresholds: tr/wk ≥ 7 · pos-day ≥ 0.55 · streak ≤ 5 · Sortino ≥ 1 · Sharpe ≥ 1 ·
cost÷gross ≤ 0.5 · gross > 0.

## The fleet-level result

**Four of four route-windows fail on the same four checks**, with no differencing
anywhere in the derivation:

- **Sharpe negative on 4/4**: −2.33, −0.86, −1.40, **−6.75**
- **Sortino negative on 4/4**: −3.10, −1.18, −1.97, **−6.82**
- **positive-day ratio below 0.55 on 4/4**: 0.417, 0.404, 0.366, 0.416
- **cost ÷ gross above 0.5 on 4/4**: 9.89, 1.53, 30.35, 1.20

The pre-registration is met. After an arc in which nearly every route-level claim turned
out to be window-scoped, **this one is not** — each scorecard is computed independently
on its own holdout, so nothing here rests on comparing windows.

## Gross edge is negative on both crypto holdouts

`gross_pnl_before_costs` — the gate's own pre-cost figure — is **−0.0135** on
`bybit XAUT` and **−1.7909** on `binance BTC`, and the gate's dedicated
`gross_pnl_positive` check **fails on both**. It **passes on `exness XAU` at both
windows** (+0.0535, +0.7812).

**This is not a contradiction of Round 320.** That round measured `one_target` at zero
cost over the **whole** 500-day window and got **+0.5945** (`bybit XAUT`) and
**+1.7176** (`binance BTC`). The gate measures the **last ~101 days only**. Positive
over 500 days and negative over the most recent 101 is arithmetically consistent — it is
a **period** difference, not a measurement disagreement, and I am not treating it as one.

What it does say is that on the **most recent** stretch — the one a deployed system is
actually living in — the two crypto routes have negative edge **before any cost at all**.
`exness XAU` remains the only route positive before costs on every measurement taken.

## Two other observations

**`binance BTC` trades 21.84/week on the recent holdout** — comfortably above the
7/week bar and far above the 8.1-9.5/week Round 305 measured over full windows. On the
recent period, Target 3 is not this route's problem.

**"No prolonged loss" fails on both new routes.** Maximum negative-day streak is **14**
on `bybit XAUT` and **7** on `binance BTC` against a limit of 5; `exness XAU` came in at
4 and 5. That objective is named explicitly in the standing brief
("không lỗ kéo dài") and this is the first time it has been measured.

## What is proven, and what is not

Proven:

- `bybit XAUT` and `binance BTC` daily-profit-gate at `--days 500`, deployed costs, both
  `passed=false` on an identical holdout 2026-05-22 → 2026-08-30 (101 observed days).
- Metrics as tabulated, including Sharpe −1.4017 and −6.7530, Sortino −1.9718 and
  −6.8166, negative-day streaks 14 and 7, trades/week 4.48 and 21.84.
- `gross_pnl_before_costs` −0.013455 and −1.790875; the `gross_pnl_positive` check fails
  on both and passes on `exness XAU` at 360 and 900 days.
- Across all four scorecards Sharpe, Sortino, positive-day ratio and cost÷gross fail
  their thresholds.

Not proven, and deliberately not claimed:

- **That the crypto routes have negative raw edge in general.** The gate's holdout is a
  *different period* from Round 320's full window; both readings can be correct. No
  reconciliation is offered and none is needed.
- That the four-of-four Sharpe result covers the fleet. Three routes, four
  route-windows. `exness BTC`, `bybit BTC` and `binance XAU` have had **no** gate run.
- That the holdouts are comparable across routes. The two new runs share a holdout
  exactly; `exness XAU`'s two are different periods, so its cross-route comparison of
  gross sign is **not** matched — running `exness XAU` at 500 days would fix that and
  was not done.
- Any candidate improvement, or any promotion. The gate fails everywhere; that is
  evidence of a problem, not a validated change.
- SQN, information ratio or max consecutive losing trades — still unavailable
  (Round 324).
