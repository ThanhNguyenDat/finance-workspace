# SCOPED TO 360 DAYS (Round 318)

Round 318 ran a matched-window control and it **failed**: `bybit XAUT`'s two measures
agree positive at 360 days (+0.3427 / +0.0936) but **disagree at 250 days**
(+0.6346 / −0.1791). A route's raw-edge sign — and whether its measures agree on it —
is **not window-independent**.

So this file's conclusions describe **the `--days 360` window**, not "the fleet". The
fixed-window A/B remains clean *within* a window (Round 308); what Round 318 shows is
that its conclusions **do not transfer between** windows. See
`round318-DATA-ISSUE-the-control-fails-raw-edge-sign-does-not-transfer-across-windows.md`.

---

# Round 315 — REJECTED: the split is **not** by instrument. `exness BTC` is positive too — but its sign **flips between measures**, and broker is perfectly confounded with market type.

Classification: **REJECTED** — my pre-registered prediction failed, the **third
consecutive** failure on this question. Two bounded Docker sweeps (exactly the
2-container budget), same fixed-`--days` design.

## The cell Round 314 named

Round 314 closed with: *"That the split is by **instrument** rather than by **broker**
or route. XAU-on-Exness against BTC-on-Binance differs in both; **`exness BTC` would
separate them** and was not run."*

That is the unique cell completing both comparisons — it holds broker fixed against
`exness XAU`, and instrument fixed against `binance BTC`.

**Registered before running:** `exness BTC`'s zero-cost `one_target.realized_pnl` is
**negative**, like `binance BTC` — the split follows the **instrument**. Refuted if
positive. The basis was Round 96, which found BTC Alpha candidates at zero cost
performing near-identically across the two brokers (donchian 0.96/0.96, keltner
1.02/1.06, heikin 0.98/0.91 binance/exness) — broker-similar on BTC, which points at
instrument.

## The result: refuted

`exness BTC/USD` (cfd), `--days 360`, identical except execution cost:

| fee / slippage | trades | **realized_pnl** | pnl/trade | guard-free pnl | guard-free trades | cost rejections |
|---|---|---|---|---|---|---|
| **0 / 0** | 508 | **+0.5634** | **+0.00111** | **−0.4548** | 636 | 0 |
| 5 / 2 (deployed) | 488 | −4.3201 | −0.00885 | −6.2155 | 669 | 95 |

**`exness BTC` is positive at zero cost on `one_target`.** The prediction fails, and
**the split is not by instrument.**

## But it is not cleanly by broker either

| route | broker | market type | zero-cost `one_target` | gross/trade | edge ÷ cost | zero-cost guard-free | signs agree? |
|---|---|---|---|---|---|---|---|
| `exness XAU/USD` | exness | cfd | +1.0997 | **+0.00281** | +30.1% | +1.5993 | yes |
| **`exness BTC/USD`** | exness | cfd | **+0.5634** | **+0.00111** | +11.1% | **−0.4548** | **NO** |
| `binance BTC/USDT` | binance | perpetual_future | −0.4432 | **−0.00093** | −13.1% | −2.0053 | yes |

Two things stop this from being a broker rule.

**1. `exness BTC`'s sign is measure-dependent.** It is the only route where
`one_target` (+0.5634) and the guard-free `legacy_selected_rule` (−0.4548) **disagree
in sign**. On the other two routes both measures agree. So the cell that decides the
question is precisely the cell whose answer is not robust.

**2. Broker and market type are perfectly confounded.** Every positive route is
**exness + cfd**; the only negative one is **binance + perpetual_future**. Nothing in
this sample separates "Exness" from "CFD". `bybit BTC` (perpetual_future) or
`bybit XAUT` (spot) would — neither was run.

And it is a **gradient, not a binary**: +0.00281 → +0.00111 → −0.00093 per trade. Even
the best cell converts only **30%** of its round-trip cost.

## Three predictions, three failures

| round | prediction | outcome |
|---|---|---|
| 313 | `exness XAU` stays negative at zero cost | **positive** — refuted |
| 314 | `binance BTC` goes positive | **negative** — refuted |
| 315 | `exness BTC` stays negative (instrument split) | **positive** — refuted |

Three consecutive pre-registrations on this one axis, all wrong, twice in opposite
directions. I am recording that as an explicit finding about **my own priors**: I have
no working model of where raw edge lives in this fleet, and I should stop offering
directional predictions on it until something other than intuition supplies one.

## What is proven, and what is not

Proven:

- `exness BTC/USD` at 360 days, same day, same config apart from cost: 508 trades /
  **+0.5634** at 0/0 bps and 488 / −4.3201 at 5/2; guard-free 636 / **−0.4548** and
  669 / −6.2155; `execution_cost` rejections 0 and 95.
- Gross edge per trade: +0.00281 (`exness XAU`), +0.00111 (`exness BTC`), −0.00093
  (`binance BTC`) — all at `--days 360` with identical design.
- `exness BTC` is the only one of the three where `one_target` and the guard-free
  measure disagree in sign at zero cost.

Not proven, and deliberately not claimed:

- **That the split follows the broker.** It aligns with broker on `one_target`, but
  the deciding cell is sign-ambiguous and broker is perfectly confounded with market
  type in this sample.
- **That it follows market type.** Same confound, read the other way.
- Anything about `bybit BTC`, `bybit XAUT` or `binance XAU`. Three of six routes still
  have no cost ablation, and the two that would break the broker/market-type confound
  are among them.
- That `exness BTC` has usable edge. +0.00111/trade is **11.1%** of its round-trip
  cost — it would need a ~89% cost cut, worse than `exness XAU`'s 51-70%, and its sign
  does not survive a change of measure.
- Any magnitude claim, PF, win rate, Sharpe, Sortino, drawdown or streak. Unchanged
  from Rounds 313-314: `one_target` reports PnL only (Round 84), the units are the
  simulator's notional, and `starting_equity` is not the right denominator.
- That any of these levels is window-independent. All are single `--days 360` windows.
