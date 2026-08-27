# Portfolio trades carry no per-strategy attribution — Strategy Lab's contribution panel is silently broken

Spec for implementing this directly. Touches `/home/lap17204/Desktop/finance/finance-live-action` (Rust), `/home/lap17204/Desktop/finance/finance-mw` (Go, JSON passthrough only), and `/home/lap17204/Desktop/finance/finance-mw/web` (TS).

## The bug (confirmed live, not guessed)

`/trading/strategy` (Strategy Lab, `web/src/pages/StrategyLayerPage.tsx`) shows two numbers that should agree but don't, for the Portfolio lane (BTC/USDT · Portfolio · Realtime · compounding-10pct):

1. Top stats row: **"Net PnL $2.59 · 2 closed trades"** — real, correct.
2. "Strategy contribution" panel (subtitle: *"Compare allocation with realized results"*), one row per sub-strategy currently weighted into the ensemble (Candle Momentum 50%, Rsi Mean Reversion 50%): **both rows show 0 trades / $0.00 PnL.**

Confirmed via the actual trade records in the browser — both trades have:

```json
{ "strategy": "weighted-strategies", "rule_id": "weighted-strategies" }
```

Neither field ever names `candle_momentum` or `rsi_mean_reversion`. The panel's per-strategy grouping (`web/src/utils/tradeMetrics.ts:69-77`, `groupTradesByStrategy`) keys purely on `trade.strategy` — correct for Alpha (one ledger per strategy × interval, so `trade.strategy` really is the strategy id), structurally incapable of attributing anything for Portfolio, where every trade's `strategy` is the shared ensemble rule name. The UI gives no indication this is a data-availability gap rather than "no activity yet" — it just quietly shows zeros next to a real $2.59 total, which is what made this look like a bug in the frontend rather than what it actually is: attribution data that was never recorded.

## Root cause, exact location

`SimulatedTrade.strategy` (`crates/finance-core/src/trading_modes.rs:1188`) comes from `SimulatedLedger.strategy`, written once at construction (`SimulatedLedger::new`, `trading_modes.rs:1290`; assigned into the trade in `build_trade`, `1876`: `strategy: self.strategy.clone()`).

For every Portfolio context — realtime and backtest alike — that ledger is constructed with the **literal string `"weighted-strategies"`**, not any sub-strategy id:

```rust
// crates/finance-api/src/trading_api.rs:737
let mut realtime = context.simulated_child(&format!("paper-{rule_id}"), "weighted-strategies", DecisionPolicyKind::WeightedEnsemble);
// crates/finance-api/src/trading_api.rs:746
let mut backtest = context.simulated_child_with_workflow(&format!("paper-backtest-{rule_id}"), "weighted-strategies", WorkflowKind::Backtest, ...);
```

`rule_id` here (`"fixed-pct"`, `"risk-2pct"`, `"compounding-10pct"` — from `execution.rule_id`, `deployment_rules.rs` / `config.rs:244,395+`) only labels which *sizing/protective rule lane* this is (`paper-{rule_id}`); it was never meant to disambiguate strategies and can't.

Both JSON fields the frontend reads are the same value (`history_trade_json`, `trading_api.rs:3149-3164`):

```rust
"strategy": trade.strategy,
"rule_id": trade.strategy,
```

Alpha doesn't have this problem — its ledgers are one per `strategy × interval`, so `context.strategy_id.clone()` (`trading_api.rs:858`) really is the strategy.

## The data already exists at decision time — it's just discarded before reaching the trade

`MultiTimeframeEvidenceBook.evidence: BTreeMap<interval, BTreeMap<strategy_name, StrategyIntervalEvidence>>` (`trading_modes.rs:478-482`) holds every contributing strategy's raw evidence per decision tick. `interval_status()` (`697-745`) / `role_scores()` (`747-774`) already compute each strategy's weighted score contribution (`StrategyEvidenceStatus.score`, `356-364`; formula at `727-729`: `side.score(strength) * interval_weight * strategy_weight`). This is live today at `trading_api.rs:1536,1618` and surfaced only as a transient debug snapshot in `signal_states` JSON (`1618-1640`) — **never attached to `PortfolioDecision`** (`trading_modes.rs:44-59` — fields are `weighted_score`, `contributor_count: usize`, `intervals: Vec<String>`, no strategy identities) or to `PortfolioTarget` (`106-113`, same shape via `from_decision`, `127-136`). So the attribution is computed, then thrown away every tick, forever.

## The fix

### 1. finance-live-action (Rust)

**a. New evidence-book method** — add near `role_scores` (`trading_modes.rs:747`):

```rust
/// Each contributing strategy's weighted score at `as_of`, summed across
/// intervals — the per-strategy counterpart of `role_scores`'s per-role
/// aggregation. Used to attribute a Portfolio decision back to the
/// strategies that produced it.
pub fn strategy_contributions(&self, as_of: KlineTs) -> Vec<(String, f64)> {
    // same interval/evidence walk as role_scores(), keyed by
    // item.strategy_name and summed instead of grouped by role
}
```

**b. Carry it on the decision/target** — add a field to both:

```rust
// trading_modes.rs:44-59, PortfolioDecision
pub contributing_strategies: Vec<(String, f64)>,

// trading_modes.rs:106-113, PortfolioTarget
pub contributing_strategies: Vec<(String, f64)>,
```

Populate in `MultiTimeframeEvidenceBook::decide` (`549-582`) via the new method; forward through `PortfolioTarget::from_decision` / `from_decision_and_current_position` (`127-159`, both already build the target field-by-field from the decision). `PortfolioConstructionState::construct` (`194-221`) already clones the whole decision into the target, so no change needed there.

**c. Call sites** — no new code needed beyond (a)/(b); the field rides along once the structs carry it:
- Realtime: `trading_api.rs:1535-1537` (`pending.evidence.decide(close_time)` → `inner.portfolio_construction.construct(decision.clone())`).
- Historical replay: the post-`refactor.md` shared-driver shape (`driver.evidence.decide(...)` / `driver.construction.construct(...)`, ~lines 195-196 of `apply_historical_portfolio_kline_with_no_lookahead`). If this spec lands before that refactor, wire it into the current (pre-refactor) per-rule `HistoricalPortfolioReplay.evidence`/`.construction` instead — same method call, just a different owning struct.

**d. Persist on the open position, not just the tick** — `SimulatedLedger::apply_target` (`1585-1609`) calls `self.open_position(kline, target_side)` (`1608`), discarding `target` entirely. A trade's **entry** attribution is the meaningful one (not whatever the evidence book says at close time, which may have drifted). Change `open_position`'s signature to also take the target (or just the attribution slice):

```rust
// trading_modes.rs:1518-1583, open_position — add a parameter
fn open_position(&mut self, kline: &Kline, side: DecisionSide, contributing_strategies: Vec<(String, f64)>) { ... }
```

and store it on a new field on the position struct (`SimulatedPosition`, `trading_modes.rs:1158-1184`, alongside `stop_loss_price` etc.):

```rust
pub contributing_strategies: Vec<(String, f64)>,
```

Update the one call site (`1608`) to pass `target.contributing_strategies.clone()`.

**e. Read it off at close** — `build_trade` (`1866-1888`) currently does `strategy: self.strategy.clone()` (ledger-level, `1876`, unchanged — still the rule-lane label, still correct for that purpose). Add a new trade field reading from the **position**, not the ledger:

```rust
// trading_modes.rs:1186-1199, SimulatedTrade — new field
pub contributing_strategies: Vec<(String, f64)>,

// build_trade, ~1876 — new line
contributing_strategies: position.contributing_strategies.clone(),
```

**f. Alpha is unaffected/additive** — Alpha's single-strategy `PortfolioDecision` naturally produces a one-entry `contributing_strategies` vector (itself, weight 1.0). No behavior change, just a redundant-but-harmless field for Alpha trades.

### 2. finance-mw (Go) — JSON passthrough only, no .proto change

Trade records travel as opaque JSON (`webdata.JsonPayload{ json: string }`, `proto/web_data.proto:13-14,41`), built from `history_trade_json` / `ledger_trade_state` (`trading_api.rs:3149-3164` / `~3064-3149`) which serialize `SimulatedTrade` to `serde_json::Value`. finance-mw's Go gateway (`internal/interfaces/http/trading_gateway.go:218-233`) does a pure `parseJSONPayload(resp.GetJson())` passthrough — no typed Go struct in between. **No `.proto` file changes, no `finance-live-action-contract.sha` pin bump** (`finance-mw/.github/workflows/ci-cd.yml:473-483`) — the contract-parity check only watches `.proto` diffs.

Add the field to both JSON builders on the finance-live-action side:

```rust
// trading_api.rs:3149-3164, history_trade_json, and ~3064-3149, ledger_trade_state
"contributing_strategies": trade.contributing_strategies,
```

Serialize as `[[name, weight], ...]` (pairs), not an object — weights aren't guaranteed unique-keyed if a strategy could theoretically appear twice in a decision window, and array-of-pairs is simpler to consume identically on both the Go and TS sides.

### 3. finance-mw/web (TypeScript)

**a. Type** — `web/src/types/index.ts`, `interface Trade` (currently ~line 1-14):

```ts
contributing_strategies?: [string, number][];
```

**b. Attribution logic — `web/src/utils/tradeMetrics.ts`, `groupTradesByStrategy` (69-77)**

This is the actual consumer fix, and it's a **product decision, not just a code change** — flag it explicitly rather than silently picking one:

- **Option A — proportional split.** A trade with `contributing_strategies: [["candle_momentum", 0.6], ["rsi_mean_reversion", 0.4]]` contributes 60% of its PnL to Candle Momentum's bucket and 40% to Rsi Mean Reversion's. Most accurate, but "Strategy contribution"'s existing per-row `{trades: N}` count (`StrategyLayerPage.tsx`'s `strategyRows`, ~51-60, via `summarizeTrades`) stops being a whole-number trade count once a trade can fractionally belong to multiple buckets — `summarizeTrades` (`tradeMetrics.ts`) would need either a weighted-PnL mode or the row to show weighted $ contribution without a trade *count* at all.
- **Option B — dominant-only.** Attribute the whole trade to whichever strategy had the highest weight in `contributing_strategies` at entry. Keeps `summarizeTrades`'s existing whole-trade-count semantics unchanged (a trade belongs to exactly one bucket), simpler, but "loses" the minority contributor's share entirely — a strategy that's *always* the 40% partner would show 0 trades forever, even though B doesn't have Portfolio's current *complete* blindness (it'd show up as the entry when it happens to dominate).

Recommend **Option B** to start (smaller, additive change to `groupTradesByStrategy`'s existing whole-trade grouping; matches the existing UI's whole-trade-count expectations exactly) with a follow-up note in the code that Option A is the more correct long-term answer once `summarizeTrades` supports weighted/fractional trades.

```ts
// tradeMetrics.ts — replace the body of groupTradesByStrategy
export function groupTradesByStrategy(trades: Trade[]): Record<string, Trade[]> {
  return trades.reduce<Record<string, Trade[]>>((acc, trade) => {
    const key = dominantContributor(trade) ?? trade.strategy;
    if (!acc[key]) acc[key] = [];
    acc[key].push(trade);
    return acc;
  }, {});
}

function dominantContributor(trade: Trade): string | undefined {
  const contributions = trade.contributing_strategies;
  if (!contributions || contributions.length === 0) return undefined;
  return contributions.reduce((best, current) => (current[1] > best[1] ? current : best))[0];
}
```

`dominantContributor` returning `undefined` (old trades recorded before this field existed, or Alpha trades where `trade.strategy` is already correct) falls back to today's `trade.strategy` behavior unchanged — this must stay backward-compatible for trades already persisted before the backend change ships.

**c. Nothing else needs to change in `StrategyLayerPage.tsx`** — `tradesByStrategy` / `strategyRows` (47-60) already consume `groupTradesByStrategy`'s output generically; fixing the grouping function is sufficient.

## Verification

- finance-live-action: unit test asserting a Portfolio trade opened while `candle_momentum` dominated the entry decision carries `contributing_strategies` with that strategy's weight highest, and that Alpha trades still carry a single-entry vector matching `trade.strategy`.
- finance-mw/web: unit test for `groupTradesByStrategy` — a Portfolio-shaped trade list where every trade shares one `strategy`/`rule_id` but has distinct `contributing_strategies` dominant entries groups correctly per dominant contributor, not all into one bucket; a trade with no `contributing_strategies` (old data) falls back to `trade.strategy`.
- Manual: after both sides ship, re-open `/trading/strategy` on the Portfolio lane that currently shows the $2.59/2-trades vs. 0-trades mismatch and confirm the two sub-strategy rows now sum to the top-level total.
