# Portfolio: `risk-2pct` and `compounding-10pct` show ~1 trade each, `fixed-pct` has full history

Reported by user: on the Portfolio lane's Rule selector, only one of the 3
configured rules (`fixed-pct`) has real trade history; the other two
(`risk-2pct`, `compounding-10pct`) each show just 1 trade. Two independent,
code-verified causes — not one shared bug. Touches
`/home/lap17204/Desktop/finance/finance-live-action` only.

## Background: the 3 rules

`configured_portfolio_rules()` (`crates/finance-api/src/deployment_rules.rs:27-109`)
runs 3 Portfolio execution rules concurrently, per instrument (so 3 ledgers ×
2 running instruments = 6 total today, BTC/USDT + XAU/USDT):

| rule_id | sizing | notional formula | added |
|---|---|---|---|
| `fixed-pct` (derived, `id: None`) | `FixedNotional(5.0)` | constant $5 | pre-existing production config (predates this file; verified against running containers 2026-08-09 per the module doc comment, `deployment_rules.rs:5-7`) |
| `risk-2pct` | `RiskFraction(0.02)` | `equity * risk_fraction / stop` | commit `42d5449`, 2026-08-09 17:27 |
| `compounding-10pct` | `EquityFraction(0.10)` | `equity * fraction` | commit `e189a46`, 2026-08-09 17:31 |

All 3 share the identical protective pair (`stop: 0.005, take: 0.010`,
`deployment_rules.rs:36-37,57-58,79-80` — deliberate, "so all three isolate
the sizing choice... as the variable being compared", per the comment at
`:71-73`) and the same `starting_equity: 10_000.0`. They all consume the
**same** decision target — `portfolio_policy` is built once and applied to
every rule's ledger (`trading_api.rs:728-729`, used inside the per-rule loop
`:732-769`) — so entry/exit *timing* should track closely across all 3; only
position size should differ.

## Cause 1 (confirmed bug): `risk-2pct` is structurally blocked by an unscaled risk gate

`PositionSizing::RiskFraction`'s notional formula
(`crates/finance-core/src/trading_modes.rs:1073-1087`):

```rust
Self::RiskFraction(risk_fraction) => {
    let ProtectiveLevels::Fractional { stop, .. } = protective else { return 0.0; };
    if !stop.is_finite() || stop <= 0.0 { return 0.0; }
    (equity.max(0.0) * risk_fraction.max(0.0)) / stop
}
```

For `risk-2pct`: `equity=10_000.0`, `risk_fraction=0.02`, `stop=0.005` →
`notional = 10_000 * 0.02 / 0.005 = $40,000` per position.

Every rule's pre-trade risk gate is built the same way, in the per-rule loop
(`trading_api.rs:757-758`):

```rust
let mut risk_policy = PortfolioRiskPolicy::default();
risk_policy.risk.max_leverage = f64::from(simulation.leverage);
```

Only `max_leverage` is overridden per rule. Every other limit stays at
`PortfolioRiskPolicy::default()`'s hardcoded values
(`crates/finance-core/src/portfolio_risk.rs:208-213`):

```rust
max_order_notional: 1_000.0,
max_order_equity_fraction: 0.10,
max_instrument_notional: 2_000.0,
max_account_gross_notional: 5_000.0,
max_account_net_notional: 3_000.0,
```

The gate (`crates/finance-core/src/risk.rs:123-202`) checks both
`order_notional` and `order_equity_fraction` via `enforce()`
(`risk.rs:312-322`, a strict `projected <= maximum`):

- `order_notional` = $40,000 vs. `max_order_notional` = $1,000 → **fails**.
- `order_equity_fraction` = $40,000 / $10,000 = 4.0 vs. `max_order_equity_fraction`
  = 0.10 → **fails**.

So essentially every new-position attempt by `risk-2pct` gets rejected at the
risk gate. Rejection only blocks the *new* leg — risk-reducing closes are
exempt (`portfolio_risk.rs:449-480`) — so this isn't crashing or erroring
anywhere, it's silently staying flat. `risk-2pct`'s equity would need to
first crash below ~$250 for `$250 * 0.02 / 0.005 = $1,000` to clear the cap,
which won't happen from a standing-flat ledger. This will not "even out over
time" — it's a structural mismatch between the rule's sizing config and its
risk policy, introduced when `risk-2pct` was added (`42d5449`) without
scaling `risk_policy.risk` to match.

**Fix direction** (not applied — investigation only): scale
`max_order_notional`/`max_order_equity_fraction` (and probably
`max_instrument_notional`) per rule based on its own sizing config, the same
way `max_leverage` is already overridden per rule at `trading_api.rs:758` —
e.g. size the cap to comfortably cover the rule's own worst-case notional at
`starting_equity`, not a single shared default meant for the $5 fixed-notional
rule. Where exactly this override belongs (a field on
`PortfolioExecutionConfig`, or derived automatically from `sizing_mode`/
`sizing_value` at construction) is a design call for whoever picks this up —
flagging the mechanism and location, not prescribing the exact API.

## Cause 2 (not a bug, needs confirming): `compounding-10pct` is new, not blocked

`compounding-10pct` sizes to `equity * 0.10 = $1,000` — exactly at the
`max_order_notional`/`max_order_equity_fraction` boundary, and `enforce()` is
`<=` so this **passes** the gate. It isn't structurally blocked like
`risk-2pct`.

Its low trade count is better explained by recency: it only started running
concurrently on 2026-08-09 (`e189a46`), ~3 days before this report
(2026-08-12) — a much shorter window than `fixed-pct`'s pre-existing
history. There's no `created_at`/timestamp on `ExecutionContext`/scope itself
to confirm this precisely at runtime (`grep -rn "struct ExecutionContext"` in
finance-core shows no such field); the ~3-day window comes from git history
on `deployment_rules.rs` alone.

**Worth double-checking before assuming "just needs more time"**: since
`compounding-10pct` shares the exact same decision timing as `fixed-pct`
(same `portfolio_policy`, `trading_api.rs:728-729`), its trade count over the
same ~3-day window should track `fixed-pct`'s cadence closely. If it's
showing far fewer trades than "3 days' worth of fixed-pct's rate" would
predict, that gap isn't explained by anything found in this pass and is worth
checking against a second possible issue found while investigating (unverified,
flagging only):

`list_history_trades` (`trading_api.rs:384-406`) falls back when both
`scope_id` and `run_id` are omitted:

```rust
let context = if request.scope_id.is_none() && request.run_id.is_none() {
    self.state.runtime.portfolio_context().unwrap_or(self.state.runtime.context())
} else {
    self.state.runtime.resolve_context(...).expect(...)
};
```

`portfolio_context()` (`trading_api.rs:987-993`) returns the **first**
matching Portfolio context in insertion order — always `fixed-pct`, since
`configured_portfolio_rules()` pushes it first (`deployment_rules.rs:31`,
before `risk-2pct`/`compounding-10pct`). If any caller (frontend or
otherwise) ever queries trade history without `scope_id` — e.g. a race before
the selected Rule variant's `scope_id` resolves — it silently gets
`fixed-pct`'s data with no error, which could *mask* `compounding-10pct`'s
real (possibly higher) trade count rather than the count actually being low.
Not confirmed as happening; worth ruling in/out before concluding
`compounding-10pct`'s low count is purely recency.

## What "done" looks like

- `risk-2pct`: scale its risk policy to its own sizing so it can actually
  open positions, then confirm live it starts producing trades at a similar
  cadence to the other 2 rules.
- `compounding-10pct`: confirm whether its trade count over its ~3-day window
  roughly matches `fixed-pct`'s rate over the same window. If yes, no fix
  needed — it just needs to keep running. If no, check whether the
  `scope_id`-omitted fallback in `list_history_trades` is masking its real
  count anywhere in the request path (frontend or gRPC caller) before
  assuming a second sizing/gating bug.
