# WINDOW-SCOPED, AND ONE CELL FLIPS (Round 320)

`binance BTC`'s raw edge is **−0.4432 at 360 days and +1.7176 at 500 days**, with both
measures agreeing at *both* windows. So this file's conclusions hold at 360 days and
**one of its cells has the opposite sign at 500**. Any statement here of the form
"perpetuals are negative" or "the cost-driven diagnosis does not generalise" is
**360-day specific**.

Round 320 also shows **measure-agreement does not imply window-stability** — they are
independent properties. Of three routes tested across windows, only `exness XAU` is
stable in both sign and measure. See
`round320-REJECTED-binance-btc-raw-edge-flips-sign-at-500-days-so-the-perpetual-negative-rule-is-a-360-day-artifact.md`.

---

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

# Round 316 — NEEDS-MORE-RESEARCH: **broker is ruled out.** Both perpetual-future routes lose at zero cost, on two *different* brokers, 20% apart per trade. Market type survives — but only half the confound is broken.

Classification: **NEEDS-MORE-RESEARCH** — a pre-registered **decision rule** fired
cleanly and eliminated one candidate; the other half of the confound stands. Two bounded
Docker sweeps (exactly the 2-container budget), same fixed-`--days` design.

## No directional prediction this round, on purpose

Round 315 recorded, as an explicit finding about my own priors: *"I have no working
model of where raw edge lives in this fleet, and I should stop offering directional
predictions on it until something other than intuition supplies one."* Three
pre-registrations in a row had failed.

So this round pre-registers the **interpretation** rather than the outcome:

| `bybit BTC` zero-cost result | conclusion |
|---|---|
| negative, both measures agreeing | **market type** tracks the sign, not broker |
| positive, both measures agreeing | **binance specifically** is the outlier; broker tracks the sign |
| measures disagree in sign | ambiguous — no conclusion |

`bybit BTC` is the sharp cell because it holds `market_type = perpetual_future` fixed
while changing the broker away from Binance. It is BTC rather than XAU, and that is a
deliberate departure from the usual XAU-first ordering: `bybit XAUT` is spot, so it
would add a third category without separating the two hypotheses already on the table.

## The result

`bybit BTC/USDT` (perpetual_future), `--days 360`, identical except execution cost:

| fee / slippage | trades | **realized_pnl** | pnl/trade | guard-free pnl | guard-free trades | cost rejections |
|---|---|---|---|---|---|---|
| **0 / 0** | 320 | **−0.3654** | **−0.00114** | **−1.0816** | 411 | 0 |
| 5 / 2 (deployed) | 260 | −2.0694 | −0.00796 | −3.4393 | 339 | 23 |

**Negative, and both measures agree.** The rule fires: **market type tracks the sign.**

## The four cells

| route | broker | market type | zero-cost `one_target` | gross/trade | zero-cost guard-free | measures agree |
|---|---|---|---|---|---|---|
| `exness XAU/USD` | exness | cfd | +1.0997 | **+0.00281** | +1.5993 | yes |
| `exness BTC/USD` | exness | cfd | +0.5634 | **+0.00111** | −0.4548 | **NO** |
| **`bybit BTC/USDT`** | **bybit** | **perpetual_future** | **−0.3654** | **−0.00114** | **−1.0816** | **yes** |
| `binance BTC/USDT` | binance | perpetual_future | −0.4432 | **−0.00093** | −2.0053 | yes |

**Broker is ruled out on the negative side.** Binance and Bybit are different
exchanges, and on the same market type they land at −0.00093 and −0.00114 per trade —
**20% apart**, same sign, both measures agreeing on both routes. Round 315's
"aligns with broker" reading does not survive.

For contrast, the two Exness CFD routes are **87% apart** (+0.00281 against +0.00111),
so the perpetual pair is the tighter cluster of the two.

## What is still confounded

**Every CFD route is Exness.** So on the positive side "cfd" and "exness" remain
tangled exactly as before — this round broke the confound only where two brokers share
a market type. The surviving statement is narrow:

> Two different brokers, both on perpetual futures, both have negative raw edge. The
> two routes with positive `one_target` raw edge are both Exness CFD, and one of them
> is sign-ambiguous across measures.

`bybit XAUT` is spot on a broker already represented here, so it would add a third
market type without re-using Binance — the natural next cell, and still unrun.

## What is proven, and what is not

Proven:

- `bybit BTC/USDT` at 360 days, same day, same config apart from cost: 320 trades /
  **−0.3654** at 0/0 bps and 260 / −2.0694 at 5/2; guard-free 411 / −1.0816 and
  339 / −3.4393; `execution_cost` rejections 0 and 23.
- Gross edge per trade across four cells: +0.00281, +0.00111, −0.00114, −0.00093.
- The two perpetual-future routes sit 20% apart per trade; the two Exness CFD routes
  87% apart.
- `bybit BTC` is the lowest-frequency route measured (320 trades at zero cost against
  391-508 elsewhere), consistent with Round 289.

Not proven, and deliberately not claimed:

- **That market type causes the sign.** It is the only candidate left standing of the
  two tested, on four routes. "Cfd" is still perfectly confounded with "exness", and
  no mechanism has been established — market type is a *label* on a bundle of
  differences (pricing, spread, funding, venue microstructure) that this design cannot
  separate.
- That `exness BTC` belongs on the positive side. Its two measures disagree in sign
  (Round 315), so one of the four cells is not solid.
- Anything about `bybit XAUT` or `binance XAU`. Two of six routes still have no cost
  ablation.
- That funding explains it. Funding was left at the default 1.0 bps on every run and
  contributes at most ~0.11 against PnL of 0.4-4.3 — too small to drive the sign, but
  it was not ablated separately.
- Any magnitude, PF, win rate, Sharpe, Sortino, drawdown or streak. Unchanged from
  Rounds 313-315: `one_target` reports PnL only (Round 84), units are the simulator's
  notional, `starting_equity` is not the denominator.
- That any of these levels is window-independent. All four cells are single
  `--days 360` windows.
