# THE MECHANISM IS A GATE CROSSING, NOT A COST REDUCTION (Round 348)

`--slippage-bps 0` drops the **reversal** cost from 14 bps to exactly **10.0 bps**, the ceiling
of the execution-cost gate the replay shares with production (strict `>`, so 10.0 passes). It
therefore **unlocks direct reversals that deployed costs forbid** — a change of action space, not
merely of cost. That is why the trade count moved 42 → 38 and gross changed while `--fee-bps 0`
(4.0 bps, also unlocked) behaved differently again.

So "zero slippage is profitable" reads more precisely as *"zero slippage unlocks a strategy
production cannot run at deployed costs."* This file's caution against misquoting the +0.1315
stands, and now has a mechanism. See `round348-DATA-ISSUE-the-cost-flags-move-reversals-across-a-10bps-gate-which-explains-rounds-344-345-and-346.md`.

---

# MECHANISM REFUTED, SENSITIVITY WORSE THAN STATED (Round 345)

The path this file named as likely — the `realized_pnl > 0` gate in
`alpha_performance_quality` — is **refuted**. A `--fee-bps 4.9` run (a 0.1 bps cut, **1.4%** of
the round trip, far too small to flip any sign) adds a trade, moves gross **+14.8%**, raises
total cost **+14.4%** at a *lower* rate, and leaves net 11.4% worse. The feedback is not
threshold-gated; what replaces it is **not** established.

This strengthens this file's core point and weakens its headline number: net across the fee
ladder is **non-monotone** — −0.04538 / −0.05056 / **+0.14423** / −0.03635 at 5.0 / 4.9 / 3.0 /
0.0 bps — so "zero slippage is profitable" is one point on a chaotic curve whose *larger* cost
cut (fee 0.0) is **not** profitable. See `round345-REJECTED-the-cost-feedback-is-not-a-threshold-a-0-1-bps-fee-change-moves-gross-15-percent-and-the-replay-is-chaotic.md`.

---

# Round 344 — DATA-ISSUE: `--fee-bps` and `--slippage-bps` **change the decision stream**, so no cost-component attribution from this tool is identified. The smoking gun: removing fees leaves the trade count at 42 and drops **gross — which is measured before costs — by 79%**.

Classification: **DATA-ISSUE** — the measurement design does not identify what it appears to,
which affects the reading of every `--fee-bps` / `--slippage-bps` comparison in this loop. My
pre-registered threshold also failed. Two bounded Docker sweeps (exactly the 2-container
budget), **XAU-first**, on the closest-to-break-even window.

## The question and the pre-registration

Round 343 measured `exness XAU` @300 at gross **+0.3391** against cost **0.3845** — cost is
113% of gross, the smallest gap on record. Deployed costs are fee 5 bps, slippage 2 bps,
funding 1 bps, so slippage is **28.6%** of the bps. Round 214 claimed slippage dominates the
cost effect; Round 215 corrected it to a super-additive interaction.

**Pre-registered as a partition:** setting `--slippage-bps 0` cuts `total_cost_drag` by
**≥ 50%** → slippage dominates; **< 50%** → it does not.

## Result — refuted at the threshold, and the design is broken underneath

`exness XAU`, `--days 300`, deployed band, identical holdout (2026-07-01 → 2026-08-28, 51
observed days):

| run | trades | tr/wk | **gross** | cost drag | **net** | Sharpe | Sortino | cost÷gross |
|---|---|---|---|---|---|---|---|---|
| deployed (5 / 2 / 1 bps) | 42 | 5.05 | +0.33907 | 0.38445 | −0.04538 | −0.249 | −0.374 | 1.134 |
| **`--slippage-bps 0`** | **38** | 4.57 | +0.33666 | **0.20521** | **+0.13146** | **+0.913** | **+1.592** | **0.610** |
| **`--fee-bps 0`** | 42 | 5.05 | **+0.07177** | 0.10812 | −0.03635 | −0.259 | −0.438 | 1.507 |

**Slippage removal cuts cost by 46.6% — under the 50% line. The prediction is refuted.** It is
still far above slippage's 28.6% share of the bps, so slippage is disproportionately expensive;
it just does not clear the threshold I registered.

**But neither arm is a clean decomposition, and the fee arm proves it.** Removing the fee left
the trade count at **exactly 42** and dropped `gross_pnl_before_costs` from **+0.33907 to
+0.07177 — a 79% fall in a quantity measured *before* costs are charged.** A cost parameter
cannot change pre-cost gross on a fixed set of trades. The trades are therefore **not** the same
trades: same count, different entries and exits.

The slippage arm shows it more plainly still — the trade count moved **42 → 38**.

The mechanism is the one Round 300 established: the Portfolio refits interval and strategy
weights on every kline from cumulative Alpha performance, and
`alpha_performance_quality` gates on `realized_pnl > 0 && gross_profit > 0`. **Cheaper
execution makes more strategies profitable, which changes their weights, which changes what the
Portfolio trades.** Cost is not an exogenous parameter in this replay; it feeds back into the
decision stream.

**Consequence: `total_cost_drag` deltas across cost settings cannot be attributed to the cost
component that was changed.** Every `--fee-bps` / `--slippage-bps` comparison in this loop —
Rounds 213, 214, 215 and this one — measures a *joint* change in cost and decisions. Round 215's
"super-additive, no single lever exists" was the right conclusion; this round supplies the
mechanism, and shows the non-additivity is not a curiosity but a structural property of the
replay.

## The number that will be tempting to misquote

At zero slippage this Portfolio is **profitable**: net **+0.1315**, Sharpe **+0.913**, Sortino
**+1.592** (clearing the gate's 1.0 Sortino bar), cost÷gross **0.610**. **This is the first
positive net measured anywhere in this arc.**

It must not be read as "the strategy works if we fix execution":

- Zero slippage is **not achievable**. It is a counterfactual, not a target.
- The run is **confounded** — 38 trades against 42, a different decision stream, per the above.
- It still fails the gate: Sharpe 0.913 < 1.0, cost÷gross 0.610 > 0.5, positive-day ratio
  0.353 < 0.55, and the route is gate-ineligible at every window anyway (7 continuity checks).
- One window, and it is the window that already flattered this route (Round 343).

What it does establish, carefully: at this window the entire deficit is **the same order as the
slippage line**. Whether any of that is recoverable is an execution-quality question in
`finance-broker` / `mt5`, not a Portfolio-layer question, and nothing here says it is
recoverable.

## What is proven, and what is not

Proven:

- `exness XAU` @300, identical holdout, deployed band: `--slippage-bps 0` → 38 trades / 4.572
  per week / gross +0.33666 / cost 0.20521 / net **+0.13146** / Sharpe +0.9134 / Sortino
  +1.5923 / cost÷gross 0.6095; `--fee-bps 0` → 42 trades / 5.053 / gross **+0.07177** / cost
  0.10812 / net −0.03635 / Sharpe −0.2595 / cost÷gross 1.5065.
- Slippage removal cuts total cost drag by 46.6%, against a 28.6% share of the bps.
- Removing the fee changed pre-cost gross by −79% at an unchanged trade count of 42.
- The deployed run's `simulation_config` carries fee 5.0, slippage 2.0, funding 1.0 bps.

Not proven, and deliberately not claimed:

- **Any per-component cost attribution.** That is precisely what this round shows the tool
  cannot deliver. The 46.6% and 71.9% figures are **joint** cost-and-decision effects and must
  be quoted as such.
- That zero slippage would be profitable in production. It is a counterfactual on a confounded
  run at one window on a gate-ineligible route.
- That the feedback runs only through `alpha_performance_quality`. That is the known path that
  would produce it (Round 300, `trading_modes.rs:589-617`); **I ran no controlled test isolating
  it**, and I did not inspect per-strategy weights in either run.
- That Rounds 213-215's conclusions are wrong. Their *measurements* stand; what this round
  removes is the ability to read any of them as a clean per-component decomposition — which is
  close to what Round 215 concluded on its own evidence.
- Any promotion. No achievable configuration is profitable, and this route cannot produce a gate
  verdict.
