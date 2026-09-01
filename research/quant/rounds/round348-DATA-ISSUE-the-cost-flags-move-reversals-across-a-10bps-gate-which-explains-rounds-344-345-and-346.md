# SCOPE CORRECTED — THE GATE PATH HAS NO RISK LAYER (Round 356)

This file explained rounds 344 and 345's fee-ladder jumps by the **10 bps reversal gate**. Those
two rounds were **`--daily-profit-gate` runs**, and the gate path
(`daily_profit_gate.rs:376-412`) replays decisions straight into a ledger with **no
`PortfolioRiskLayer` at all** — so that gate could not have fired in them. **The attribution of
the r344/r345 ladder to the reversal threshold is withdrawn.**

What stands: rounds **349 and 350** used plain `--json`, where the risk layer *is* active, and
round 349 measured the rejections directly (**102 → 3**). The threshold mechanism is real on the
`one_target` path; it simply is not what moved the gate-run ladder — that was the cost-feedback
path, which round 350 measured on the ungated ledger. See `round356-DATA-ISSUE-the-daily-profit-gate-omits-the-construction-guard-and-the-risk-layer-so-it-scores-a-different-configuration.md`.

---

# QUANTIFIED FROM THE REPLAY'S OWN COUNTERS (Round 349)

This file said counting reversals *"needs a per-trade audit trail… audit item L4"*. **It does
not** — the plain `--json` output carries `risk_rejected_counts`
(`portfolio_measurement.rs:255`). Measured on `exness XAU` @300, deployed band, 55,045 decisions:
**102 `execution_cost` rejections at deployed costs, 3 with `--slippage-bps 0`** (reversal 14.0 →
10.0 bps). **99 of 102 disappear**, every other gate is 0 in both runs, and the rate is **one
blocked reversal per ~3 executed trades**.

Two refinements: the gate is an **action-quality** lever, not a frequency one — unlocking moved
the trade count only −1.1% while realized PnL improved **31%**; and a **gate-free** cost-feedback
path is now isolated — the ungated `legacy_selected_rule` ledger still moved 355 → 338 trades,
which is this file's unexplained residual, on a ledger the gate never touches. See `round349-NEEDS-MORE-RESEARCH-the-replay-blocks-102-reversals-at-deployed-costs-and-3-when-unlocked.md`.

---

# Round 348 — DATA-ISSUE: the cost flags don't just change costs, they **move reversals across a 10 bps gate**. That single threshold explains Rounds 344, 345 and 346 — and my "Divergence 2" was **wrong**: the replay *does* model the gate.

Classification: **DATA-ISSUE** — `--fee-bps` and `--slippage-bps` silently change the Portfolio's
**action space**, not just its costs, which invalidates the naive reading of every cost-flag
comparison in this loop. **Zero containers**; read-only code inspection plus production log
evidence. **XAU-first** in consequence.

## First, a correction to my own claim

The observability audit recorded **Divergence 2**: *"production enforces an `execution_cost`
risk gate at 10 bps… **the research replay has no such gate**."* **That is wrong.**

`finance-research/src/portfolio_measurement.rs:170-181` builds a `PortfolioRiskLayer` with
`PortfolioRiskPolicy::widened_for_simulation(...)`, and that function
(`finance-core/src/portfolio_risk.rs:272-307`) widens **only** the notional and leverage limits —
it leaves `execution_cost.max_total_cost_bps = 10.0` (`:210`) untouched. `evaluate_historical`
(`:411-417`) calls `evaluate_execution_cost(&input, is_reversal)` whenever the target opens new
risk (`:446-452`), and `risk_layer.execution_target(...)` returns `None` on rejection, so nothing
executes. **The replay applies the same 10 bps ceiling as production.** Divergence 2 is
withdrawn.

## What the gate actually is, in practice

With the default rate components all zero — `spread_cost_bps`, `market_impact_bps`,
`latency_cost_bps` = 0.0 (`portfolio_risk.rs:248-250`) — the projected cost reduces to

```
projected_bps = (fee_bps + slippage_bps) × leg_multiplier      leg_multiplier = 2 for a reversal
```

(`portfolio_risk.rs:624, 643-648`), rejected on a **strict** `total_cost_bps > max_total_cost_bps`
(`execution_cost.rs:243`). The policy comment states the consequence outright:
*"One simulated market fill costs 5bps fee + 2bps slippage by default. **A reversal prices both
legs and is rejected at 14bps.**"* (`portfolio_risk.rs:206-209`).

At deployed costs a single leg is 7 bps and passes; **a reversal is 14 bps and is rejected**.

**Production observation confirms this is the gate's *only* behaviour.** Across every retained
`warn` log on all six route workers:

| route | warn files | `execution_cost` rejections | projected cost |
|---|---|---|---|
| `bybit BTC` | 7 | **213** | 14 bps |
| `binance BTC` | 8 | 87 | 14 bps |
| `exness BTC` | 2 | 66 | 14 bps |
| **`exness XAU`** | 6 | **3** | 14 bps |
| `bybit XAUT` | 2 | 0 | — |
| `binance XAU` | 8 | 0 | — |

**369 rejections, every single one at 14 bps** — the `13.999999999999998` and
`14.000000000000002` variants are float noise on 2 × 7. **Not one rejection at any other value.**
In practice this gate is a **"no direct reversals" rule** and has never fired for anything else.

My pre-registered question — *does an `execution_cost` rejection appear on `exness XAU`?* —
answers **yes** (3 events over 6 retained days, against a backtest trade rate of ~0.7/day, so
order-1 relative to that route's activity). But since the replay models the gate too, the
divergence that question was testing does not exist.

## The prize: one threshold explains Rounds 344, 345 and 346

Projected cost is computed from `input.simulation.fee_bps` and `slippage_bps` — **the very flags
the CLI exposes**. So changing them moves the reversal cost across the 10 bps ceiling:

| run | fee + slippage | reversal cost | `> 10`? | reversals | measured result |
|---|---|---|---|---|---|
| deployed (r343) | 5 + 2 = 7 | **14.0** | yes | **blocked** | 42 trades, net −0.0454 |
| r345 `--fee-bps 4.9` | 4.9 + 2 = 6.9 | 13.8 | yes | blocked | 43 trades, net −0.0506 |
| **r345 `--fee-bps 3.0`** | 3 + 2 = 5 | **10.0** | **no** (strict `>`) | **unlocked** | **38 trades, net +0.1442, Sharpe +0.93** |
| **r344 `--slippage-bps 0`** | 5 + 0 = 5 | **10.0** | **no** | **unlocked** | **38 trades, net +0.1315, Sharpe +0.91** |
| r344 `--fee-bps 0` | 0 + 2 = 2 | 4.0 | no | unlocked | 42 trades, gross +0.0718 |

The two runs that land on **exactly 10.0 bps** — reached by completely different flags — produce
**the same trade count (38)** and near-identical nets (**+0.1442** and **+0.1315**). The two runs
above the ceiling behave like each other (42 and 43 trades, net −0.045 and −0.051). **The ladder
is not chaotic; it is a step function with a threshold at 10 bps.**

This **corrects Round 345**, which called the replay *"chaotically sensitive"* on the strength of
a non-monotone fee ladder. The large jumps are a **discrete gate crossing**, not chaos. What
survives from Round 345 is the smaller residual: fee 4.9 against fee 5.0 both sit above the
ceiling yet differ by one trade and 14.8% of gross — that sensitivity is real and still
unexplained.

It also **reframes Rounds 344 and 346**. "Zero slippage is profitable" is more precisely *"zero
slippage drops the reversal cost to exactly the ceiling, unlocking a strategy production cannot
run at deployed costs."* Every profitable configuration this arc has found —
r344's +0.1315, r345's +0.1442, and r346's no-band +0.4069 — is reachable only by specifying
costs **below production's**, and each thereby buys a different action space.

**Under deployed costs, no configuration has ever been profitable on any route.** That statement
is unchanged and is now better understood.

## What is proven, and what is not

Proven:

- The replay applies the identical execution-cost gate: `portfolio_measurement.rs:170-181`,
  `portfolio_risk.rs:272-307` (widens notional/leverage only), `:210` (`max_total_cost_bps =
  10.0`), `:446-452`, `execution_cost.rs:243` (strict `>`).
- Default `spread_cost_bps`/`market_impact_bps`/`latency_cost_bps` are `0.0`
  (`portfolio_risk.rs:248-250`), so projected cost = `(fee + slippage) × leg_multiplier`, with
  `leg_multiplier = 2` for a reversal (`:624, 643-648`).
- 369 production `execution_cost` rejections across six routes and all retained days, **all at
  14 bps**; per-route counts as tabulated; `exness XAU` has 3.
- The arithmetic in the table above, matched against the measured results of Rounds 343-346.

Not proven, and deliberately not claimed:

- **That the gate is the *only* mechanism behind the cost-flag sensitivity.** Fee 4.9 and fee 5.0
  are both above the ceiling and still differ (42 vs 43 trades, gross +14.8%). Something else
  remains, and Round 345's refutation of the `alpha_performance_quality` sign-gate hypothesis
  still stands.
- **That reversals are the only thing the gate can reject.** With non-zero spread, impact or
  latency components, or a different sizing, a single leg could exceed 10 bps. **Every rejection
  observed in production is at 14 bps**, but the defaults make that the only reachable value on
  these routes — this is an observation about the current configuration, not a proof about the
  gate.
- **How many reversals the replay would take if unlocked**, or what fraction of decisions are
  reversals at all. That needs a per-trade audit trail, which is audit item **L4** and is not
  serialized.
- That the profitable unlocked runs would be profitable in production. They require costs
  production does not have; the point is precisely that they are unreachable.
- Any promotion. Nothing here changes a configuration, and every deployed-cost result still
  loses money.
