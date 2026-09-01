# RANGE CORRECTED (Round 319)

The **30.1%** edge-to-cost ratio and **70%** required cost cut quoted here are the
**most pessimistic** of three windows. Re-deriving at 250 and 500 days (Round 319, using
this file's cost-per-trade of 0.00935) gives **50.5%** and **59.1%**, so the honest range
is roughly **30-60%**, needing a **41-70%** cut. The direction is unchanged — the edge
covers cost at no window measured — but the single figure understates it. Note the 250
and 500 ratios are **estimates**: the deployed cost arm was not re-run at those windows.
See `round319-NEEDS-MORE-RESEARCH-the-sign-is-window-robust-on-the-strongest-cell-but-the-magnitude-swings-2x.md`.

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

# QUALIFIED (Round 314)

This result **does not generalise**. The same fixed-`--days` cost ablation on
`binance BTC` (360 days, same design) returns **−0.4432 at zero execution cost** —
still a loss, with gross edge **−0.00093/trade** against XAU's +0.00281. On BTC the
raw signal is unprofitable before any friction, so no cost reduction reaches break-even
(it would need a 113% cut).

Cost dominates on both routes — 145% of the deployed loss on XAU, 88% on BTC — but only
XAU's residual is positive. Read this file as a **route-specific** finding, not a fleet
diagnosis. See
`round314-REJECTED-the-cost-driven-diagnosis-does-not-generalise-binance-btc-still-loses-at-zero-cost.md`.

---

# Round 313 — REJECTED: the Portfolio layer has **positive gross edge**. The loss is cost-driven, not signal-driven — but the edge is only **30%** of round-trip cost, and the deployed config sits at **70% of the cost gate's hard cap**.

Classification: **REJECTED** — my pre-registered prediction failed. Two bounded Docker
sweeps (exactly the 2-container budget), XAU-first. A **fixed-`--days` A/B** — the one
comparison type Rounds 300-312 leave untouched.

## Why this, and why now

Thirteen rounds have gone into trade-frequency measurement. Target 1 —
profitability — is the **first-listed** priority, and this arc has never asked its
central question: **is the loss cost-driven or signal-driven?**

Round 96 ran a cost ablation, but on the **Alpha sweep table** (per-candidate PF, BTC,
5 years). The **Portfolio layer** — `one_target`, the only Portfolio-faithful measure
(Round 82) — has never been cost-ablated. And Round 308 established that an A/B at a
**fixed `--days`** stays methodologically clean after the whole Round 300-312 confound,
because that confound only breaks comparisons *across* window lengths.

**Registered before running:** `one_target.realized_pnl` stays **negative** at zero
execution cost — the loss is signal-driven, matching Round 93's "structural ceiling"
reading and Round 274's finding that per-trade loss barely moved when frequency
changed 2.4x. Refuted if it comes back ≥ 0.

## The result: refuted

`exness XAU/USD`, `--days 360`, identical in every respect except execution cost:

| fee / slippage (bps) | `one_target` trades | **realized_pnl** | pnl/trade | guard-free pnl | guard-free trades |
|---|---|---|---|---|---|
| **0 / 0** | 391 | **+1.0997** | **+0.00281** | **+1.5993** | 472 |
| 5 / 2 (deployed) | 374 | −2.4441 | −0.00654 | −1.9787 | 462 |
| 10 / 4 | **0** | — | — | −4.9873 | 443 |

**At zero execution cost the Portfolio layer makes money.** Both measures flip sign —
`one_target` +1.0997 and the guard-free `legacy_selected_rule` +1.5993. The prediction
is refuted, and the "structural ceiling" reading does **not** hold at the Portfolio
layer: **the loss is cost-driven.**

## But the edge is small relative to the cost it must clear

| | value |
|---|---|
| gross edge per trade | **+0.00281** |
| net result per trade | −0.00654 |
| cost per trade (14 bps round trip) | 0.00935 |
| **gross edge as a share of round-trip cost** | **30.1%** |

Two independent estimates of what it would take to break even:

- **`one_target`, two points:** round-trip cost must fall to **4.2 bps** — a **70% cut**.
- **Guard-free, three points:** the cost curve is near-linear (slopes −0.2556 and
  −0.2149 per bps, 17% apart) and crosses zero at **6.3-6.8 bps** — a **~51% cut**.

So the honest statement is not "the strategies work, costs are in the way". It is:
**there is a real but small gross edge, worth roughly a third to a half of what
execution currently costs.** Closing that is a venue, spread and fee question, not a
parameter-tuning question — nothing in the Portfolio config reaches it.

## A hard limit discovered by the 2x run

The `10 / 4` arm is **degenerate, and that is itself the finding**: `one_target`
returns **zero trades** with **66,025** `execution_cost` rejections. `CostGatePolicy`
caps total cost at **`max_total_cost_bps = 10.0`**, and 10 + 4 = 14 bps one-way clears
it on every fill.

**The deployed 7 bps one-way therefore sits at 70% of a hard cap that stops the route
entirely.** A broker or market condition worsening execution by ~43% would silently
take a route to zero trades rather than to worse trades. Recorded as an observation of
the current configuration's headroom — **investigation only, not applied**.

## What is proven, and what is not

Proven:

- `exness XAU` at 360 days, same day, same config apart from cost: `one_target`
  391 trades / +1.0997 at 0/0 bps, 374 / −2.4441 at 5/2, and **0 trades** at 10/4.
- `legacy_selected_rule` 472 / +1.5993, 462 / −1.9787, 443 / −4.9873 across the same
  three settings — a near-linear cost curve crossing zero at 6.3-6.8 bps round trip.
- Gross edge per trade +0.00281 against a round-trip cost of 0.00935 — **30.1%**.
- `execution_cost` rejections 0 / 181 / 66,025 across the three settings;
  `max_total_cost_bps = 10.0`.

Not proven, and deliberately not claimed:

- **That this generalises.** One route, one window, one instrument. `binance BTC`,
  `exness BTC`, `bybit BTC`, `bybit XAUT` and `binance XAU` were not tested, and
  Round 96's Alpha-layer result was on BTC, not this.
- That it is a *clean* ablation. Cost changes the decision stream too — 391 trades
  against 374 — because the cost gate rejects differently. This measures "what the
  system does at zero cost" against "what it does at deployed cost", which is the right
  question but not a pure counterfactual on a fixed trade set.
- **Any claim about economic significance.** The absolute figures are in the
  simulator's notional units under `fixed_notional` sizing; `starting_equity = 10,000`
  is **not** the right denominator and I am not quoting a return on it. What is
  established is the **sign** and the **ratio to cost**, not a magnitude anyone should
  size a position from.
- Anything about PF, win rate, Sharpe, Sortino, drawdown, streak or SQN at zero cost.
  `one_target` reports only trades, realized_pnl, funding and ledgers — Round 84's
  standing limitation.
- That a 51-70% cost cut is achievable. It is what break-even would require; whether
  any venue offers it was not investigated.
- That Round 96 is contradicted. That round measured Alpha-layer PF on BTC and found
  cost explained most of the gap to PF = 1 — the same direction. This extends it to the
  Portfolio layer on XAU and puts a number on the shortfall.
