## 1. Unify the replay path

- [x] 1.1 Replace the `ledger.on_kline` loop in
  `crates/finance-research/src/daily_profit_gate.rs:376-412` with the
  `construct` → `evaluate_historical` → `execution_target` → `execute_target`
  sequence used at `crates/finance-research/src/portfolio_measurement.rs:184-208`,
  extracting the shared sequence into one function called by both.
  → verify: `rg -n "ledger.on_kline" crates/finance-research/src` reports the
  `legacy_selected_rule` control only, and no other replay site.
- [x] 1.2 Remove `conflicts_with = "daily_profit_gate"` from
  `crates/finance-research/src/main.rs:264` and delete the doc-comment sentence
  that justified it.
  → verify: a run with both `--daily-profit-gate` and
  `--portfolio-minimum-hold-decisions 288` exits without a CLI conflict error.
- [x] 1.3 **Correctness gate.** Add a test asserting that, at the deployed
  default hold and over one fixed window, the gate replay and the `one_target`
  replay produce **identical** trade count and realized PnL.
  → verify: the test fails if `construct` or the risk layer is removed from
  either path.
- [x] 1.4 Keep `legacy_selected_rule` in the gate output as an explicitly
  labelled control.
  → verify: gate JSON contains both the Portfolio-faithful figures and the
  legacy control, with distinct names.

## 2. Joint-objective metrics on that path

- [x] 2.1 Extend `ExecutionFootprint`
  (`crates/finance-research/src/portfolio_measurement.rs:23-28`) with profit
  factor, win rate, Sharpe, Sortino, max drawdown, longest negative-day streak,
  SQN, decision rate and cost-to-gross ratio, reusing the gate's existing
  implementations rather than adding second versions.
  → verify: `rg -n "fn sharpe|fn sortino|fn sqn" crates/finance-research/src`
  finds one definition each.
- [x] 2.2 Bucket daily metrics in `Asia/Ho_Chi_Minh`, matching
  `daily_profit_gate.rs:340,402`.
  → verify: a test pins one day boundary against the operational timezone.
- [x] 2.3 Report every new metric as absent rather than zero when its inputs are
  insufficient (no trades, no losing trades, fewer than two daily returns).
  → verify: a zero-trade fixture yields nulls, not zeros.

## 3. Disjoint out-of-sample

- [x] 3.1 Add `--walk-forward-segments N` producing N contiguous segments, each
  evaluated after fitting only on bars strictly before it.
  → verify: a test asserts segment boundaries are contiguous, disjoint, and
  cover the window exactly once.
- [x] 3.2 Report segments individually; never pool them into one figure.
  → verify: output contains N segment records and no aggregate PnL across them.
- [x] 3.3 Assert no-look-ahead across segments, reusing the closed-bar filter
  (`crates/finance-research/src/klines.rs:246`) and the `close_time`-sorted
  replay order.
  → verify: a test fails if any segment's evaluation observes a bar at or after
  its own end.
- [x] 3.4 Keep the trailing-holdout mode as the default.
  → verify: an invocation without the new flag produces byte-identical output to
  the current build on one fixed window.

## 4. Per-trade audit trail

- [x] 4.1 Derive `Serialize` on `SimulatedTrade`
  (`crates/finance-core/src/trading_modes.rs:1548-1562`) without changing any
  field semantics.
  → verify: `cargo test -p finance-core --timeout` equivalent passes unchanged.
- [x] 4.2 Add `--emit-trades <path>`, off by default, writing one JSON record per
  closed trade with entry/exit time, price, side, quantity, fees, slippage,
  funding and exit reason.
  → verify: for one fixed run, the emitted records' summed PnL equals the
  reported `realized_pnl` to floating-point tolerance.

## 5. Refuse unsupportable rows

- [x] 5.1 Detect a required input that is unavailable for the route and report
  the strategy as `excluded` with a reason and no score, instead of running it
  with a defaulted value.
  → verify: on a route where `taker_base_vol` is absent, the five
  `taker_imbalance` entries are reported excluded and carry no PnL.
- [x] 5.2 A row with `trades == 0` reports `realized_pnl = 0.0`, with any
  funding accrual in a separate explicitly named field.
  → verify: no output row has `trades == 0` and non-zero `realized_pnl`.
- [x] 5.3 Collapse wrapper variants whose threshold provably cannot bind because
  the inner strategy's entry condition saturates the filtered metric, reporting
  one entry rather than several identical ones.
  → verify: `min_strength_0_5/0_7/0_9_keltner_reversion_20_2_5` appear as a
  single entry; `heikin_ashi_momentum` variants remain distinct.

## 6. Trading-safety and delivery

- [x] 6.1 Confirm no live trading semantics changed: no edit to
  `PortfolioConstructionState`, `PortfolioRiskLayer`, or `trading_modes`
  execution logic beyond the additive `Serialize`.
  → verify: the diff touching `crates/finance-core` contains only the derive.
- [x] 6.2 Run the full local check set with hard timeouts, per
  `.agents/rules/coding-and-verification.md`.
  → verify: fmt, clippy, `cargo test` across affected crates all pass.
- [x] 6.3 Annotate the affected research rounds rather than reinterpreting them
  silently: gate verdicts in rounds 335, 336, 337 and every `--daily-profit-gate`
  result described a different configuration.
  → verify: a correction banner names those rounds in `raw/researcher/`.
- [ ] 6.4 Re-run one previously-blocked configuration end to end — a hold-bearing
  setting with a gate score — and record it as the first holdout-scored
  Portfolio configuration.
  → verify: the run completes, reports a gate verdict, and the round 371
  ~2x understatement is quantified against the unified path.
  → blocked: no Finance MW/research runtime is available in the current local
  environment; the deterministic shared-path regression and correction banner
  are complete, but a networked holdout rerun must be performed after Claude
  verification on a host with the production data route.
