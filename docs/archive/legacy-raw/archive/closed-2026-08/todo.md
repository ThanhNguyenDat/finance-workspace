# TODO

## finance-live-action: Portfolio multi-rule replay (Phase 2) — done

Completed by the shared-driver refactor: historical replay now owns one shared
evidence/construction/primary-kline driver and one ledger/risk-state replay per
configured rule. Targets are computed once, rule outcomes are folded into the
shared construction only after the full fan-out, and commit assigns that shared
construction at most once. The startup conflict guard was removed and replay
contract version 19 forces checkpoints produced by the old semantics to replay.

### Historical investigation

Phase 1 (done) adds support for running multiple concurrently-configured
Portfolio execution rules (sizing/protective/leverage variants) in realtime,
each as its own independent scope/ledger — same pattern Alpha already uses
per strategy × interval. Historical replay is required to be disabled
(`HISTORICAL_DEMO_REPLAY_ENABLED=false`) whenever more than one Portfolio
rule is configured, because of a real bug found during investigation:

`commit_historical_portfolio_replay` (crates/finance-api/src/trading_api.rs,
~line 1879) unconditionally overwrites the single shared
`RuntimeInner.portfolio_construction` every time one `HistoricalPortfolioReplay`
finishes. With N independently-configured rules, each currently gets its own
fully independent `HistoricalPortfolioReplay` (its own `evidence` +
`construction`, built from `crates/finance-api/src/historical_replay.rs`'s
`bootstrap_pending_intervals`). Whichever rule's replay commits last silently
clobbers the warm-start state the other rules' replays produced. All N
replays *should* converge to an identical evidence/construction end-state
(since Portfolio's aggregate target is derived purely from Alpha evidence,
independent of any one rule's sizing/protective config — invariant 3 in the
trading-mode-synchronization skill), but that convergence isn't structurally
enforced or tested; it's an assumption that a future correctness change could
silently break.

### Implemented fix

Decouple "the shared evidence/construction/target replay driver" (one
instance, matching the runtime's already-correct realtime design where
`target = inner.portfolio_construction.construct(decision)` is computed once
per decision tick and then applied to every rule's own risk layer/ledger) from
"N independent ledgers" that each just execute that one shared target sequence
with their own sizing/protective/risk config.

Concretely:
- Replay the shared evidence/construction driver exactly once per historical
  window (not once per rule).
- For each configured Portfolio rule, replay only its own `SimulatedLedger`
  against the shared driver's target sequence, using that rule's own
  `PortfolioRiskLayer`/`PortfolioRiskState` for risk-gated execution sizing.
- `commit_historical_portfolio_replay` then seeds the shared
  `portfolio_construction`/`portfolio_evidence` exactly once (from the shared
  driver), and separately continues each rule's own forward ledger from its
  own replayed ledger — no cross-rule clobbering possible by construction.

### Also still open from Phase 1's investigation, worth re-checking once this lands

- `crates/finance-api/src/grpc.rs`'s legacy no-arg `GetTradeState` RPC
  (grpc.rs:366-373) and `ListHistoryTrades` with no `scope_id`/`run_id`
  filter (grpc.rs:387-391) both still fall back to "the" one Portfolio scope
  via the singular `portfolio_context()` helper — with N rules configured,
  these two legacy endpoints only ever describe one arbitrarily-chosen rule.
  finance-mw still calls `GetTradeState` today
  (`internal/interfaces/http/trading_gateway.go:203-213`). Decide whether
  these need a scope-selecting parameter or should be deprecated in favor of
  the already-scope-generic `GetTradingMetrics`/`ListHistoryTrades` (with
  filters) paths once callers migrate.
- `PortfolioConstructionState.minimum_holding_decisions` is a single shared
  value across every configured rule (Phase 1 made it a top-level `AppConfig`
  field instead of per-`PortfolioExecutionConfig`, since the construction
  state itself is one shared instance). If a genuine need for per-rule
  hysteresis ever comes up, that requires the same driver/ledger split as
  above, since it's the same shared-instance constraint.
