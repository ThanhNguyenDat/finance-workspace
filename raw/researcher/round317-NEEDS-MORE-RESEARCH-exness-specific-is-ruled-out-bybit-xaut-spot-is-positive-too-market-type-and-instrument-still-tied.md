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

# Round 317 — NEEDS-MORE-RESEARCH: **"Exness-specific" is ruled out.** `bybit XAUT` spot is positive too, with the **highest edge-to-cost ratio in the fleet**. Market type and instrument are still tied — and the cell that would settle it cannot be run at this window.

Classification: **NEEDS-MORE-RESEARCH** — a pre-registered decision rule fired cleanly
and eliminated a second candidate; two remain confounded. Two bounded Docker sweeps
(exactly the 2-container budget), same fixed-`--days` design. **XAU-first.**

## The cell Round 316 named

Round 316 ruled out **broker** (two different exchanges on perpetual futures both
negative, 20% apart) and named what was left: *"`bybit XAUT` is spot on a broker
already represented here, so it would add a third market type without re-using
Binance — the natural next cell, and still unrun."*

Following Rounds 315-316, **no directional prediction** — the interpretation is
pre-registered instead:

| `bybit XAUT` zero-cost | conclusion |
|---|---|
| positive, both measures agreeing | **"Exness-specific" ruled out**; "non-perpetual" or "XAU" survives |
| negative, both measures agreeing | only Exness CFD is positive → the edge is **venue-specific to Exness CFD** |
| measures disagree in sign | ambiguous, as on `exness BTC` — no conclusion |

## The result

`bybit XAUT/USDT` (spot), `--days 360`, identical except execution cost:

| fee / slippage | trades | **realized_pnl** | pnl/trade | guard-free pnl | guard-free trades | cost rejections |
|---|---|---|---|---|---|---|
| **0 / 0** | 278 | **+0.3427** | **+0.00123** | **+0.0936** | 315 | 0 |
| 5 / 2 (deployed) | 251 | −0.6070 | −0.00242 | −0.2463 | 311 | 86 |

**Positive, both measures agreeing.** The rule fires: **"Exness-specific" is ruled
out.** A third market type, on a different broker, also has positive raw edge.

Its **edge-to-cost ratio is 33.8% — the highest of any route measured**, ahead of
`exness XAU`'s 30.1%. It also has the smallest deployed loss (−0.6070) simply because
it trades least.

## All five cells

| route | broker | market type | asset | zero-cost | gross/trade | guard-free | agree |
|---|---|---|---|---|---|---|---|
| `exness XAU/USD` | exness | cfd | XAU | +1.0997 | **+0.00281** | +1.5993 | yes |
| `exness BTC/USD` | exness | cfd | BTC | +0.5634 | **+0.00111** | −0.4548 | **NO** |
| **`bybit XAUT/USDT`** | **bybit** | **spot** | **XAU** | **+0.3427** | **+0.00123** | **+0.0936** | **yes** |
| `bybit BTC/USDT` | bybit | perpetual_future | BTC | −0.3654 | **−0.00114** | −1.0816 | yes |
| `binance BTC/USDT` | binance | perpetual_future | BTC | −0.4432 | **−0.00093** | −2.0053 | yes |

| grouping | cells | result |
|---|---|---|
| **market type** | cfd (2) / spot (1) **positive**; perpetual_future (2) **negative** | clean split, 5/5 |
| **asset** | XAU (2) **positive**; BTC (3) **mixed** | fits only if `exness BTC` is discounted |

## Why it is still not settled

The two survivors are confounded by which cells exist:

- **The only within-instrument contrast** is BTC across market types: `+0.00111` on
  cfd against `−0.00114` and `−0.00093` on perpetuals. That favours **market type** —
  but it rests entirely on `exness BTC`, the one cell whose two measures disagree in
  sign (Round 315).
- **There is no within-market-type contrast that favours instrument.** CFD has XAU and
  BTC and both are positive — no sign change. Perpetual has only BTC — no XAU to
  compare against.

**The cell that would settle it is `binance XAU/USDT` — XAU on a perpetual future.**
Negative would give market type outright; positive would give instrument.

**And it cannot be run at this window.** `binance XAU` has **262 days** of 5m history
(first bar 2025-12-11, Round 297) and has been frozen since 2025-12-26 (Round 207), so
`--days 360` is impossible and any shorter window breaks strict comparability with
these five cells. That is a hard limit of the available data, recorded here rather
than worked around.

## What is proven, and what is not

Proven:

- `bybit XAUT/USDT` at 360 days, same day, same config apart from cost: 278 trades /
  **+0.3427** at 0/0 bps and 251 / −0.6070 at 5/2; guard-free 315 / +0.0936 and
  311 / −0.2463; `execution_cost` rejections 0 and 86.
- Gross edge per trade across five cells: +0.00281, +0.00111, +0.00123, −0.00114,
  −0.00093.
- Edge-to-cost ratios: 33.8% (`bybit XAUT`), 30.1% (`exness XAU`), 11.1%
  (`exness BTC`), −13.1% (`binance BTC`), −16.8% (`bybit BTC`).
- Grouped by market type the five cells split cleanly; grouped by asset they do not.
- `binance XAU` has 262 days of 5m history, so the discriminating cell cannot be run
  at `--days 360`.

Not proven, and deliberately not claimed:

- **That market type causes the sign.** It survives two eliminations (broker in
  Round 316, Exness-specificity here) and fits 5/5 cells — but the instrument
  hypothesis also fits once `exness BTC` is set aside, and market type remains a
  *label* on a bundle of venue differences this design cannot decompose.
- That `exness BTC` belongs on the positive side. Its measures still disagree, and the
  argument favouring market type leans on exactly that cell.
- That `bybit XAUT`'s 33.8% is the fleet's best opportunity. It has the fewest trades
  (278 at zero cost against 391-508 on the busier routes), so its per-trade figure is
  the noisiest, and 33.8% still means a **~66% cost cut** to break even.
- Any magnitude, PF, win rate, Sharpe, Sortino, drawdown or streak. Unchanged from
  Rounds 313-316: `one_target` reports PnL only (Round 84), units are the simulator's
  notional, `starting_equity` is not the denominator.
- That any level is window-independent. All five cells are single `--days 360` windows.
