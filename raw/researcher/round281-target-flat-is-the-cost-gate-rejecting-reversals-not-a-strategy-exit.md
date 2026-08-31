# CORRECTION (Round 282)

This file's central claim — that every `target_flat` close is a risk-gate emergency
close via `force_flat()` — is **refuted by its own prediction**. `force_flat` sets
`waiting_after_protective_exit = true` (`trading_modes.rs:285`), so a `target_flat`
close would have to be followed by a 3h wait.

The pairwise test (Round 282): after `target_flat`, re-entry is immediate **100% of
the time on all three routes** (median 0.08h, n = 66/18/186); after a protective close
it is **never** immediate (0.0%, n = 903). So `target_flat` comes from the
`decision.exit == true` branch of `construct()`, which sets that flag **false** — not
from the risk layer.

What survives: the measured `execution_cost` counters (98 vs 11), the fact that no
other gate fires, and the policy comment that a reversal prices at 14bps against a
10bps limit. The **correlation** with `target_flat` share stands and is unexplained;
the **causal path** asserted here does not. See
`round282-CORRECTION-target-flat-is-not-force-flat-the-pairwise-test-refutes-round-281.md`.

---

# Round 281 — `target_flat` is not a strategy exit. It is the execution-cost gate rejecting a **reversal** at 14bps against a 10bps limit.

Classification: **NEEDS-MORE-RESEARCH**. Local code inspection plus two bounded
Docker sweeps (exactly the 2-container budget).

## Round 280's named next step, and where it leads

Round 280 ended on: *"Where `decision.exit == true` originates. I did not locate it;
`hold()` is not it. That is the first concrete thing to find next."*

**It does not originate anywhere on the Portfolio path.** Both branches of
`PortfolioConstructionState::decide()` set `exit: false` — the passing branch
(`trading_modes.rs:864`) and `hold()` (`1103`). The only site that sets it from
evidence is `alpha_decision()` (`trading_api.rs:3372`), which builds a
**single-strategy** decision for the `demo-*` ledgers, not the Portfolio.

So on the Portfolio path a target can become Flat only via `force_flat()`. That
function has **exactly one caller**:

```
portfolio_risk.rs:533 → .force_flat(format!("risk_{}_emergency_close", rejection.gate.as_str()))
```

**Every `target_flat` close on a Portfolio ledger is a risk-gate emergency close.**

## Verified against the risk counters, not left as inference

| route | one_target trades | **execution_cost rejections** | other gates | ledger `target_flat` share |
|---|---|---|---|---|
| exness XAU | 256 | **98** | all zero | **47.6%** |
| bybit BTC | 206 | **11** | all zero | **5.8%** |

Rejection ratio **98/11 = 8.9x** against a `target_flat` ratio of **47.6/5.8 = 8.2x**.
Every other gate — `execution_freshness`, `execution_halt`, `performance_halt`,
`position_reconciliation`, `risk` — is **zero on both routes**. The only gate that
ever fires is `execution_cost`.

## And the source says exactly why

`portfolio_risk.rs:205-211`:

```rust
execution_cost: CostGatePolicy {
    max_snapshot_age_ms: 5_000,
    max_future_skew_ms: 500,
    // One simulated market fill costs 5bps fee + 2bps slippage by
    // default. A reversal prices both legs and is rejected at 14bps.
    max_total_cost_bps: 10.0,
},
```

A single fill is 7bps and passes. **A reversal prices both legs at 14bps and is
rejected**, so the Portfolio cannot flip a position directly — the gate forces it
flat instead. This is deliberate and the comment says so.

## What this corrects

Rounds 261, 277, 279 and 280 all read `target_flat` as "the signal went flat" — a
benign strategy exit. **It is a rejected reversal.** The close-reason mix is not
telling us how often the strategy decides to stand aside; it is telling us **how
often the Portfolio tries to reverse and is refused on cost**.

It also supplies the mechanism Round 280 looked for and could not find, in the
**opposite direction** to the one Round 280 refuted: a *larger* entry budget clears
the 0.1 threshold more often → more decisions with a definite side → more reversal
attempts → more cost-gate rejections → more `target_flat` closes. Budgets 0.3114 /
0.3063 / 0.1763 against flat shares 14.0% / 15.2% / 5.8% run the right way for that
chain.

## What is proven, and what is not

Proven:

- Both Portfolio `decide()` branches set `exit: false`; `alpha_decision` is the
  single-strategy path.
- `force_flat()` has exactly one caller, the risk layer's emergency close.
- `execution_cost` rejections 98 vs 11 against `target_flat` shares 47.6% vs 5.8%
  (8.9x vs 8.2x); every other gate zero on both routes.
- The policy default is `max_total_cost_bps: 10.0` with the quoted comment stating a
  reversal costs 14bps and is rejected.

Not proven, and deliberately not claimed:

- **The entry-budget → reversal-attempt link.** The verified chain runs from
  `force_flat` to the cost gate to reversals. That a larger entry budget produces
  more reversal attempts is the plausible completion and is **not measured** — Round
  280 already had one entry-budget story refuted, and this is a second one built on
  three points.
- That this is a defect. The comment shows the 14bps rejection is intended. Whether
  a Portfolio that can never reverse directly is the *desired* behaviour is a design
  question, not a research finding, and I am not raising it as a fault.
- That the counter and ledger percentages should match exactly. 98/256 = 38.3% against
  the ledger's 47.6%; different windows and different samples. The **ratio across
  routes** is the evidence, not the levels.
- Anything about routes other than the two measured here.
