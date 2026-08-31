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

# Round 314 — REJECTED: the cost-driven diagnosis does **not** generalise. `binance BTC` still loses at **zero** execution cost — its raw edge is negative.

Classification: **REJECTED** — my pre-registered prediction failed, and it failed in the
**opposite direction** to Round 313's. Two bounded Docker sweeps (exactly the
2-container budget), same fixed-`--days` design. BTC-scoped: Round 313's first named
limit was that it had tested one route.

## The limit Round 313 named

Round 313 found `exness XAU`'s Portfolio layer **profitable at zero execution cost**
(+1.0997 against −2.4441 deployed) and closed by naming the obvious gap: *"That this
generalises. One route, one window, one instrument. `binance BTC`, `exness BTC`,
`bybit BTC`, `bybit XAUT` and `binance XAU` were not tested."*

`binance BTC` is the flagship instrument and the busiest route, so it goes first.

**Registered before running:** `binance BTC` also shows positive gross edge —
`one_target.realized_pnl > 0` at 0/0 bps — with the edge a similar fraction of
round-trip cost (roughly 15-60%). Refuted if the zero-cost PnL is negative. I noted
before running that Round 96 found BTC Alpha candidates reaching only **PF 0.91-1.06**
at zero cost — straddling break-even — so this was a real test rather than a
formality.

## The result: refuted

`binance BTC/USDT`, `--days 360`, identical in every respect except execution cost:

| fee / slippage | trades | **realized_pnl** | pnl/trade | guard-free pnl | guard-free trades | cost rejections |
|---|---|---|---|---|---|---|
| **0 / 0** | 479 | **−0.4432** | **−0.00093** | −2.0053 | 616 | 0 |
| 5 / 2 (deployed) | 460 | −3.6776 | −0.00799 | −6.8053 | 659 | 85 |

**At zero execution cost `binance BTC` still loses.** Both measures stay negative. Its
gross edge per trade is **−0.00093** — the raw signal is unprofitable before any
friction, so **no cost reduction can make this route profitable.** Break-even would
require a **113%** cost cut, which is not a thing.

## The two routes disagree, and both of my predictions were wrong

| route | zero-cost PnL | deployed PnL | gross/trade | edge ÷ cost | residual at zero cost |
|---|---|---|---|---|---|
| `exness XAU/USD` | **+1.0997** | −2.4441 | **+0.00281** | **+30.1%** | **POSITIVE** |
| `binance BTC/USDT` | **−0.4432** | −3.6776 | **−0.00093** | **−13.1%** | **NEGATIVE** |

Round 313 predicted XAU would stay negative and it went **positive**. Round 314
predicted BTC would go positive and it stayed **negative**. **Both pre-registrations
failed, in opposite directions** — which is worth recording as a caution about my own
priors on this question rather than as a pair of unlucky guesses.

**There is no single fleet-wide diagnosis.** Round 93's "structural ceiling" reading
holds on **BTC** and fails on **XAU**; Round 313's "cost-driven" reading holds on
**XAU** and fails on **BTC**.

## What both routes do share

Cost dominates the loss on **both**:

- `exness XAU`: cost destroys **3.5438** of PnL — **145%** of the deployed loss, which
  is why removing it flips the sign.
- `binance BTC`: cost destroys **3.2344** — **88%** of the deployed loss, leaving a
  residual **−0.4432** on the wrong side of zero.

So "cost is the dominant term" is true fleet-wide on these two routes. What differs is
only whether the residual underneath it is positive. That distinction is the whole
practical question: on XAU a large enough cost reduction reaches break-even; on BTC
nothing does.

## What is proven, and what is not

Proven:

- `binance BTC` at 360 days, same day, same config apart from cost: 479 trades /
  −0.4432 at 0/0 bps and 460 / −3.6776 at 5/2; guard-free 616 / −2.0053 and
  659 / −6.8053; `execution_cost` rejections 0 and 85.
- Gross edge per trade −0.00093 on `binance BTC` against +0.00281 on `exness XAU`
  (Round 313, identical design and window).
- Cost accounts for 88% of the deployed loss on `binance BTC` and 145% on
  `exness XAU`.

Not proven, and deliberately not claimed:

- **Anything about the remaining four routes.** `exness BTC`, `bybit BTC`,
  `bybit XAUT` and `binance XAU` have had no cost ablation. Two routes disagreeing is a
  reason to expect heterogeneity, not a basis for predicting any third.
- That `binance BTC` cannot be made profitable. What is shown is that **cost reduction
  alone** cannot do it on this configuration and window — a different signal, band or
  candidate set is untested here.
- That the split is by **instrument** rather than by **broker** or route. XAU-on-Exness
  against BTC-on-Binance differs in both; `exness BTC` would separate them and was not
  run.
- Any magnitude claim. As in Round 313, the figures are in the simulator's notional
  units under `fixed_notional` sizing and `starting_equity` is not the right
  denominator; only the **sign** and the **ratio to cost** are being asserted.
- Anything about PF, win rate, Sharpe, Sortino, drawdown or streak. `one_target` does
  not report them (Round 84's standing limitation), so this is a PnL-only comparison
  and is **not** the joint-objective evaluation the loop asks for.
- That either result is window-independent. Both are single `--days 360` windows;
  Rounds 300-312 do not touch this A/B, but they do mean neither *level* should be
  quoted as the route's true edge.
