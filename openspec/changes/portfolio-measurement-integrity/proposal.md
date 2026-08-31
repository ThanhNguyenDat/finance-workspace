## Why

The quant research loop has run 170 iterations without a promotable candidate.
Rounds 351–375 established that the reason is not an absence of candidates but a
**measurement defect**: the tool cannot score the configuration it reports on.

Four findings, each cited with evidence in `raw/researcher/`:

- **The holdout gate scores a different configuration than the one being
  optimised.** `crates/finance-research/src/daily_profit_gate.rs:408` replays
  decisions with `ledger.on_kline(...)` only — no
  `PortfolioConstructionState::construct`, no `PortfolioRiskLayer` — whereas the
  Portfolio-faithful path at
  `crates/finance-research/src/portfolio_measurement.rs:184-208` applies both.
  Consequently `crates/finance-research/src/main.rs:264` declares
  `portfolio_minimum_hold_decisions` as `conflicts_with = "daily_profit_gate"`,
  so **no configuration carrying a minimum-hold value can ever obtain a holdout
  score**. Round 371 measured the size of the discrepancy: on
  `binance.perpetual_future.BTC.USDT` at 900 days the gate scores a stream
  losing −9.90557 while the deployed path loses −4.81958.
  (`raw/researcher/round356-*.md`, `round371-*.md`)
- **No out-of-sample period is independent.** Holdout is the trailing 20% of the
  requested window, so every `--days` value yields a holdout nested inside or
  containing every other. There is no walk-forward.
  (`raw/researcher/round352-*.md`)
- **The joint objective cannot be evaluated on the Portfolio path.**
  `ExecutionFootprint` (`portfolio_measurement.rs:23-28`) exposes only `ledgers`,
  `trades`, `realized_pnl` and `funding_paid`. Profit factor, win rate,
  Sharpe/Sortino, drawdown, negative-day streak, SQN, decision rate and
  cost-to-gross ratio exist only inside the gate — that is, only on the path that
  does not model the Portfolio.
- **Two classes of row are silently wrong.** A strategy whose required input is
  absent is degraded into a constant-side signal rather than excluded
  (`taker_base_vol` is 0.00% on four of six routes, making `buy_ratio`
  identically 0 and every threshold fire the same side forever), and the
  resulting zero-trade rows report a non-zero `realized_pnl` equal to
  `-funding_paid`. A wrapper is also a silent no-op when the inner strategy's
  entry condition saturates the metric it filters on.
  (`raw/researcher/round374-*.md`, `round375-*.md`)

Correctness is the reason for this change, not throughput: the tool currently
publishes gate verdicts, holdout claims and scorecard metrics that do not
describe the configuration named alongside them.

## What Changes

- Route the daily-profit gate's replay through the same construction-guard and
  risk-layer path used by `one_target`, and remove the CLI conflict that
  forbids a minimum-hold value under the gate.
- Emit the full joint-objective scorecard from the Portfolio-faithful path
  rather than only from the gate path.
- Add anchored walk-forward evaluation producing **disjoint** out-of-sample
  segments, alongside the existing single trailing holdout.
- Serialize per-trade execution records behind an explicit flag so fills can be
  reconciled against market data.
- Report a strategy whose required input is unavailable as **excluded**, and
  never attach a non-zero `realized_pnl` to a row with zero trades without an
  explicit funding-only marker.

## Capabilities

### New Capabilities

- `portfolio-measurement-integrity`: the research tool measures the
  configuration it names, on out-of-sample data that is genuinely out of sample,
  with the metrics the joint objective requires, and refuses to publish a score
  it cannot support.

## Impact

- Affected repository: `finance-live-action` only.
- Affected components: `crates/finance-research` (`daily_profit_gate.rs`,
  `portfolio_measurement.rs`, `main.rs`, `sweep.rs`, `split.rs`,
  `strategies.rs`) and additive serialization on
  `crates/finance-core/src/trading_modes.rs`.
- **No change to live trading behaviour.** `PortfolioConstructionState`,
  `PortfolioRiskLayer` and the `trading_modes` execution semantics are not
  modified; this change reuses them from an additional call site and adds
  serialization. `finance-mw`, `finance-web`, `finance-broker` and `mt5` are
  untouched.
- No database, migration, API, deployment or market-data change.
- Rollback is a normal Git revert; the tool is a research CLI with no persistent
  production state.
