# GATE VERDICT QUALIFIED (Round 336)

Gate results in this file come from `exness XAU`, where **all seven non-5m intervals fail
`input_continuity` at both 500 and 900 days**. `minimum_holdout_days` passes at 900 days
(151 observed days) but the continuity checks do not, so **no configuration on this route
can pass the gate at any window measured**.

The band comparisons and relative rankings here are unaffected — a structural check failing
identically across every configuration cannot reorder them. What does not hold is reading
any run in this file as a **gate verdict**. See `round336-DATA-ISSUE-exness-xau-can-never-pass-the-gate-at-any-window-and-binance-btc-is-the-first-gate-eligible-route-measured.md`.

---

# Round 331 — REJECTED: the band **optimum moves with the window**. At 900 days the **deployed** band is best, not the 0.02/0.04 that won at 500. Parameter tuning on one window does not transfer.

Classification: **REJECTED** — my pre-registered claim that the lever's shape is
window-robust fails. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**.

## The gap Round 330 named

Round 330 found an interior optimum at 0.02/0.04 on `exness XAU` and named its limit:
*"That this holds on other routes or windows. **One route, `--days 500` only.**"*

Given that Rounds 318-322 found nearly every route-level result window-fragile, the
question is whether a **parameter optimum** is any sturdier. This round re-runs the two
decisive bands at **`--days 900`**, where the holdout is 151 days and clears the gate's
own 90-day minimum — methodologically better than 500 days, which gives XAU only 84.

**Pre-registered:** if the lever's shape is window-robust, then at 900 days the
0.02/0.04 band beats **both** the deployed 0.01/0.02 and the wider 0.04/0.08 on net, and
no configuration is positive. Refuted if the ordering changes or any net turns positive.

## The result

`exness XAU/USD`, `--days 900`, deployed costs, holdout 2026-03-04 → 2026-08-28
(151 observed days):

| band | trades | tr/wk | pos-day | streak | Sortino | Sharpe | cost÷gross | gross | **net** |
|---|---|---|---|---|---|---|---|---|---|
| 0.04 / 0.08 | 109 | 4.29 | 0.391 | 5 | −1.793 | −1.384 | 37.27 | **−0.0207** | **−0.7931** |
| 0.02 / 0.04 | 128 | 5.04 | 0.397 | 5 | −1.134 | −0.788 | 1.95 | +0.4933 | −0.4695 |
| **0.01 / 0.02 (deployed)** | 174 | 6.85 | 0.404 | 5 | −1.179 | **−0.861** | 1.53 | **+0.7812** | **−0.4118** |

**The ordering changes. The deployed band has the best net at 900 days** (−0.4118),
beating 0.02/0.04 (−0.4695). The prediction is refuted.

## Side by side

| band | tr/wk @500 | net @500 | gross @500 | tr/wk @900 | net @900 | gross @900 |
|---|---|---|---|---|---|---|
| 0.04 / 0.08 | 6.11 | −0.1396 | +0.4460 | 4.29 | **−0.7931** | **−0.0207** |
| 0.02 / 0.04 | 6.82 | **−0.0301** | +0.6067 | 5.04 | −0.4695 | +0.4933 |
| 0.01 / 0.02 (deployed) | 8.95 | −0.2283 | +0.6000 | 6.85 | **−0.4118** | +0.7812 |

**Best at 500 days: 0.02/0.04. Best at 900 days: the deployed band.** Round 330's
"interior optimum at 0.02/0.04" is **500-day specific**, and its shape differs too — an
interior optimum at 500 days, monotone-improving-with-frequency across these three points
at 900.

That is a meaningful escalation of this arc's central problem. Rounds 318-322 showed
route-level *signs* were window-fragile; this shows **the optimal parameter setting is
window-fragile as well**. Tuning a parameter on one window does not transfer to another,
even on the same route.

## What does replicate

Three things hold at both windows:

- **No configuration is profitable.** Six configurations across two windows, every net
  negative. The lever cannot reach break-even at either.
- **The widest band tested is the worst at both windows.**
- **Widening destroys gross, and worse at depth.** For 0.04/0.08, gross runs **+0.4460**
  at 500 days and **−0.0207** at 900 — it goes *negative*, so at that window the wide
  band is not merely giving up edge, it has none left before costs.

## What is proven, and what is not

Proven:

- `exness XAU` at `--days 900`, holdout 2026-03-04 → 2026-08-28: 0.04/0.08 → 109 trades /
  4.29 per week / gross −0.0207 / net −0.7931; 0.02/0.04 → 128 / 5.04 / +0.4933 /
  −0.4695; deployed 0.01/0.02 → 174 / 6.85 / +0.7812 / −0.4118.
- The best-net band is 0.02/0.04 at 500 days and 0.01/0.02 at 900 days.
- All six configurations across the two windows have negative net; all fail the gate.

Not proven, and deliberately not claimed:

- **That the deployed band is optimal at 900 days.** It is the best of the *three tested*
  there; nothing tighter than 0.01/0.02 was run at that window, so the optimum could sit
  below it.
- **That saturation occurs at 900 days.** 0.08/0.16 was not run at this window, so the
  Round 330 saturation finding is untested here and I am not carrying it over.
- Any conclusion about other routes. `exness XAU` only; `binance BTC`'s ladder was never
  extended downward at any window.
- That the frequency-multiplies-cost mechanism (Rounds 328-329) is affected. That was
  measured across a 5-8x frequency range including the ATR band; this round compares
  three points in a narrow low-frequency band, where the picture is evidently different.
  The two are not in conflict, and I am not treating this as evidence against it.
- Any promotion. Every configuration at both windows fails the gate.
