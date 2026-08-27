---
name: trading-mode-synchronization
description: Preserve the finance ecosystem's Alpha strategy-by-interval ledgers and synchronized aggregate Portfolio/Live execution. Use when changing trading contexts, multi-timeframe evidence, historical replay order, realtime kline handling, scoped trade metrics, no-lookahead behavior, or the Alpha/Portfolio/Live selectors in finance-mw and finance-live-action.
---

# Trading Mode Synchronization

Keep one contract across the web gateway and trading engine:

- Alpha is one independent ledger for every `strategy × interval`, run raw: no
  protective levels, a constant notional, holding until the signal reverses. It
  answers "is this signal any good", so nothing may confound it with a rule.
- Portfolio is one rules-based aggregate of synchronized Alpha ledger state. Sizing and
  protective levels are part of a rule, so Portfolio is a grid of them.
- Live follows the same aggregate decision clock, with broker execution replacing
  simulated execution.

## Non-negotiable invariants

1. Never collapse Alpha contexts across strategy or interval.
1b. A replayed ledger hands its closing state to the forward ledger it is paired
    with, so one lane reads as a single continuous series. Pair them where the
    contexts are built: every Portfolio rule shares a policy, a strategy and an
    interval, so matching on attributes points all of them at one ledger. Seed
    only an untouched forward ledger, and seed on checkpoint restore as well as on
    replay commit, or a mispairing can only be repaired by replaying a year.
1c. Balance carries forward, the trade list does not. Copying the closed trades
    held a second unbounded history per strategy and interval and crash-looped
    workers on memory; readers join the two series instead.
1d. Historical Portfolio replay hands its shared evidence book and last processed
    primary close to the untouched forward runtime together with construction
    state. A ledger-only handoff starts realtime without the last fully closed
    `1d` evidence; the first `5m` boundary can then remain pending until a future
    daily close that is too new to satisfy it, blocking every later boundary.
2. Never create independent Portfolio trades per interval. Intervals are evidence
   lanes feeding one Portfolio ledger on the primary `5m` execution clock.
3. Portfolio evidence comes from persistent Alpha positions, not directly from a raw
   signal emitted on the current candle.
4. At decision time, every configured strategy must have evidence for every
   required interval.
5. Evidence must be the latest fully closed candle at the decision timestamp.
   Reject future, missing, stale, and previous-boundary evidence.
6. Support both exact close timestamps and exchange-inclusive timestamps ending
   in `999ms`.
7. At a shared close timestamp, advance replay from small to large interval:
   `5m → 15m → 1h → 4h`. Hold the primary candle pending until the complete
   synchronized bundle is ready.
8. Realtime arrival order must not change the result. If `5m` arrives first,
   queue it; when the other intervals arrive, execute queued primary candles
   once in event-time order.
9. Persist pending primary candles, their evidence snapshots, and the last
   processed primary close in worker checkpoints.
10. Scope UI history and metrics by execution context identity (`scope_id` and
    `run_id`). Portfolio/Live use the primary `5m` metrics clock; Alpha uses its own
    context interval.
11. Snapshot streams carry live state only. Closed-trade history is unbounded
    and is served by the unary `ListHistoryTrades` call, never embedded in a
    stream message. The ledger appears twice — `history_trades_json` and the
    `trades` array inside `trade_state_json` — so check both when auditing size.
12. `finance-mw` holds exactly one upstream gRPC snapshot stream per worker and
    fans it out to browser clients. Adding viewers must not add upstream streams.
13. Replayed ledgers are versioned by `HISTORICAL_REPLAY_CONTRACT_VERSION`. Any
    change to alpha/portfolio replay decisions must bump it, or restored checkpoints
    will pin the old results until their Redis TTL expires. A bump replays every
    worker, so deploy the admission gate before the bump, never after.
14. Simulated PnL must match what the broker would report before any metric built
    on it means anything. USDT-M perpetuals charge funding on notional every eight
    hours whether or not a trade closes, take the taker fee on market and
    stop-market fills, and count a breakeven trade as neither win nor loss.
15. A reversal is one action. Closing on an opposite decision and waiting for the
    next candle leaves the ledger flat through a candle the decision already
    called, and enters it late.
16. Comparing strategies requires a constant notional. Sizing off equity compounds
    the account into the result, so two strategies with identical signals score
    differently because an early loss shrinks every later position.
17. Pair-health monitoring must distinguish inherited replay state from forward
    activity. Forward performance includes the replay baseline and an open position
    may have been copied at continuation; count only the forward ledger's own trades,
    ignore inherited position timestamps, and grant container replacement a grace
    derived from that pair's historical trade cadence.
18. Leverage metadata and liquidation inputs cross the service boundary without
    broker secrets. `finance-mw` owns account-aware leverage-range/risk-tier caching
    and returns only normalized constraints; `finance-live-action` owns the selected
    isolated leverage. Liquidation may consume only a positive, venue-timestamped
    mark price, never a kline close or last trade. New position metrics must remain
    optional at the web gateway until every worker version emits them.
19. This is about `finance-live-action`'s own consumption/evaluation boundary —
    how `finance-mw` persists klines to Postgres/Redis is a separate concern with
    its own rules and is out of scope here. Every path inside `finance-live-action`
    that merges more than one interval into a shared ledger or evidence book —
    replay stream, realtime evaluation, **or a Kafka consumer polling multiple
    interval topics/partitions** — must order strictly by event close-time (small
    interval first on a tie, invariant 7), never by which source happened to
    produce data first. Kafka guarantees order only within one partition, never
    across topics or partitions, so applying whatever `poll()` returns in arrival
    order is the exact arrival-order violation invariant 8 already forbids; it has
    just moved from the in-memory queue down into the consumer loop, where it is
    easier to miss. Re-sort or buffer-and-release by close-time at the consumption
    boundary itself — do not rely on downstream evaluation logic to fix ordering a
    Kafka poll already broke. Prove this with an adversarial-order test: feed the
    same events shuffled (or strictly reverse-interval) through the consumption
    boundary and assert the resulting ledger/evidence state is byte-identical to
    feeding them in correct close-time order — an in-order-only test cannot catch
    this class of bug.
    An interval that produced zero events for the requested/current window must be
    rejected, never silently treated as "caught up" or "confirmed empty" —
    `commit_historical_replay`'s `replayed_count == 0 => false` is the pattern. A
    single merged batch may legitimately commit some intervals and leave others
    pending; that is the safe outcome when one interval's source data simply did
    not arrive, not partial failure and not a lookahead bug. "No data yet" and
    "verified current" are different states and must stay distinguishable to every
    downstream reader.

## Selecting a strategy

Testing many candidates against one window and keeping the best selects the
luckiest, not the best: with a hundred candidates several look significant on
noise alone. Score in `finance-research`, choose on train and validation, and
treat holdout as a readout that took no part in choosing. The first sweep proved
the point immediately: a candidate near breakeven on validation collapsed on
holdout.

Read profit factor and win rate when comparing, never absolute PnL, which moves
with sizing alone. Two rules differing only in size showed the same 0.65 profit
factor and PnL of -16 against -2787.

## Where the layers actually are

Against the standard **Universe → Alpha → Portfolio Construction → Risk
Management → Execution**, this system has four of the five running and one built
but unwired:

| Stage | State |
|---|---|
| Universe | Static by design: one worker per `BASE_ASSET`/`QUOTE_ASSET` pair, with the existing compatibility key routed by `TRADING_GRPC_UPSTREAM_BY_SYMBOL`. |
| Alpha | Independent strategy-by-interval simulated ledgers. |
| Portfolio Construction | `MultiTimeframeEvidenceBook` and `MultiTimeframePortfolioPolicy`, degenerate at one symbol and one position. |
| Risk Management | Wired and active on Portfolio (simulated execution): `PortfolioRiskLayer` (`crates/finance-core/src/portfolio_risk.rs`) runs six gates in deterministic order before every Portfolio order — execution cost, risk limits (notional/leverage/open-order caps), performance halt (daily/rolling loss, drawdown, loss-streak), execution halt (incl. the operator kill switch, `ExecutionHalt`), execution freshness, and position reconciliation — called directly from `trading_api.rs`, rejections recorded and surfaced. The last two gates (execution freshness, position reconciliation) report `waiting_for_broker` until Live has a real broker position/mark-price to reconcile against; the other four are live on Portfolio today. |
| Execution | `SimulatedLedger` and `finance-broker`. |

Alpha and Portfolio are the canonical lane names. Portfolio currently fuses
Portfolio Construction with simulated Execution; keep that boundary explicit
until the portfolio-construction prompt splits the target decision from its
execution rule.

## Portfolio can run more than one execution rule concurrently

Production is not limited to exactly one validated Portfolio rule anymore.
`AppConfig.portfolio_executions: Vec<PortfolioExecutionConfig>`
(`../finance-live-action/crates/finance-api/src/config.rs`) accepts several,
configured directly in code — not through an environment variable — via
`deployment_rules::configured_portfolio_rules()`
(`../finance-live-action/crates/finance-api/src/deployment_rules.rs`), each
entry carrying an explicit unique `id` plus its own sizing/protective/leverage.
That file always returns at least the current production default rule as a
literal Rust value; add more entries to it, as a reviewable code change, to run
additional rules concurrently. Alpha strategy variants work the same way via
`deployment_rules::configured_alpha_strategies()`. Every previously-existing
Portfolio/Alpha environment variable (`PORTFOLIO_SIZING_MODE`,
`PORTFOLIO_LEVERAGE`, `SIMULATION_FEE_BPS`, etc., including the single-rule
fallback) has been removed — `deployment_rules.rs` is now the only source of
truth. Each configured rule becomes its own independent Portfolio
scope/ledger/risk layer — the same "N independent ledgers off one shared
decision" shape Alpha already has per strategy × interval:
`PortfolioConstructionState`/`MultiTimeframeEvidenceBook` stay one shared
instance per runtime (the aggregate target every rule then executes at its own
size), while `PortfolioRiskLayer`, `SimulatedLedger`, and
`PortfolioReplaySemantics` (the replay fingerprint's rule-varying half) are
per-rule, keyed by that rule's own scope_id.

Historical replay is safe with any number of configured Portfolio rules. One
`HistoricalPortfolioDriver` owns the evidence book, construction state, and
primary-kline clock for the replay run; N `HistoricalPortfolioRuleReplay`
values own only their rule-specific ledgers and risk states. Each synchronized
target is computed once, fanned out to every rule, and every execution outcome
is folded back into the one driver before construction advances. Commit then
continues every rule ledger independently and assigns the shared construction
at most once, so list order cannot clobber another rule's replay contribution.
Replay contract version 19 invalidates checkpoints created with the old
per-rule construction semantics. Version 21 additionally invalidates forward
state created without the replayed evidence book and primary decision clock.

### Sizing modes

`PositionSizing` (`../finance-live-action/crates/finance-core/src/trading_modes.rs`)
has three variants, each a different answer to "how big is this position":
`FixedNotional` (constant, ignores equity — isolates signal quality, what Alpha
uses), `EquityFraction` (a constant share of current equity, compounding wins
and losses into the next trade's size), and `RiskFraction` (sized so that
*hitting the protective stop* costs exactly the configured equity fraction,
regardless of the stop's distance — the position size is the derived value,
the risk budget is the constant). `RiskFraction` requires
`ProtectiveLevels::Fractional`: its stop is a fixed share of entry price, so
the notional is computable before a position opens; `AtrMultiple`'s stop only
exists once a ledger has accumulated enough range, which the pre-trade risk
gates in `portfolio_risk.rs` (`evaluate_execution_cost`, `evaluate_risk`,
`validate_evaluation` — none of which have ledger history) cannot supply, so
that pairing is rejected in `PortfolioExecutionConfig::from_values`. Production
runs one rule per mode concurrently today (`deployment_rules.rs`), so all
three sizing philosophies replay and execute against the identical evidence
and target sequence and are directly comparable.

## Repository map

- `finance-web`: context selector, strategy/interval selector, scoped history,
  calendar, and metric display.
- `../finance-live-action/crates/finance-core/src/trading_modes.rs`: evidence
  validation and aggregate policy.
- `../finance-live-action/crates/finance-api/src/trading_api.rs`: Alpha ledgers,
  realtime Portfolio barrier, pending queue, checkpoint state, and replay ledgers.
- `../finance-live-action/crates/finance-api/src/historical_replay.rs`: merged
  interval event-time order.

## Change workflow

1. Read both repositories' current status and diffs. Preserve unrelated user
   changes.
2. Trace context identity from backend configuration through API payloads to
   frontend selection and metric queries.
3. Write regression tests before changing execution behavior:
   - old higher-timeframe evidence at a new boundary must fail closed;
   - latest fully closed higher-timeframe evidence between boundaries is valid;
   - `5m` arriving before the synchronized bundle must not tick Portfolio;
   - a later `5m` must not erase an earlier pending boundary;
   - duplicates must not tick Portfolio twice;
   - pending barriers must survive checkpoint serialization;
   - replay must process equal timestamps from `5m` through `4h`;
   - a Kafka consumer fed multiple intervals' events out of poll order (shuffled or
     reverse-interval) must produce the same ledger/evidence state as feeding them
     in close-time order (invariant 19).
4. Make the smallest change that satisfies the invariants. Prefer existing
   ledgers, policies, context identities, and utilities.
5. Keep UI behavior lane-specific:
   - Alpha exposes strategy and interval selection.
   - Portfolio/Live show aggregate results and do not pretend to be one strategy or
     one evidence interval.
6. Verify backend and web independently.

## Required validation

Run the smallest focused tests while iterating, then finish with:

```bash
cd ../finance-live-action
cargo fmt --all -- --check
cargo test -p finance-core
cargo test -p finance-api
cargo clippy -p finance-core -p finance-api --all-targets

cd ../finance-web
npm test -- --run
npm run build
```

If full frontend lint has known unrelated failures, run lint on every modified
frontend file and report the pre-existing failures precisely.

## Stop conditions

Stop only when the changed behavior is covered, full relevant suites pass, the
skill validates, and any remaining risk or unrun check is explicit. Do not
claim deployment unless production was actually updated and inspected.
