# Trading Decision Pipeline

> Đây là contract kiến trúc đích. Hành vi production chỉ được coi là đã có
> sau khi code repository sở hữu và deployed SHA chứng minh trong handoff.

## Goal

Define one survival-first trading pipeline in which Alpha produces comparable
strategy evidence, Portfolio validates the combined decision against a simulated
ledger, and Live runs the same decision logic against a broker only after the
required safety gates are proven.

The system may optimize for positive risk-adjusted expectancy and consistent
daily outcomes. It must not promise or force a profit every day. A daily profit
target is telemetry and a risk-scaling input, never a quota that causes the
engine to manufacture trades.

## Modes Versus Internal Layers

The user-facing modes are:

- **Alpha**: every valid closed-kline signal from each `strategy × interval`
  branch creates an independent simulated intent and ledger result. The same
  contract applies to historical replay and forward simulation. Alpha does not
  require agreement between strategies.
- **Portfolio**: strategy and interval evidence is combined into one portfolio
  decision during both historical replay and forward simulation. The full
  Rules/Risk/Cost pipeline runs, then the accepted intent is executed in an
  internal simulated ledger.
- **Live**: the same decision and gate pipeline as Portfolio. The accepted intent
  may reach a broker only through reconciliation, idempotency, freshness,
  execution-cost, halt, and credential boundaries.
- **Runtime**: signal observability only. It has no execution ledger and cannot
  report Portfolio or Live performance.
- **Backtest**: a workflow and data window, not a peer operating mode. Atomic
  backtests appear under Alpha; weighted-ensemble backtests appear under Portfolio.

The layers between Alpha evidence and Portfolio execution are not additional trading
tabs. They are a versioned decision pipeline:

1. **Signal integrity**
   - accept only closed, contiguous, chronologically valid candles;
   - reject stale, future-skewed, duplicated-conflicting, or incomplete input;
   - prevent higher-timeframe look-ahead.
2. **Candidate evidence**
   - maintain results by strategy, interval, symbol, regime, and version;
   - calculate net PnL after fees, spread, slippage, funding, and latency;
   - keep minimum-sample and uncertainty status explicit.
3. **Eligibility and weighting**
   - reject disabled, stale, under-sampled, or breached candidates;
   - derive bounded strategy and interval weights from recent out-of-sample and
     Portfolio evidence;
   - normalize weights and persist the exact version used by each decision.
4. **Market-regime and multi-timeframe fusion**
   - higher intervals provide regime and direction constraints;
   - lower intervals provide entry timing;
   - conflict resolution can reduce conviction or emit `HOLD`; missing
     higher-timeframe state fails closed.
5. **Rules policy**
   - minimum ensemble conviction and minimum risk/reward;
   - liquidity, volatility, spread, funding, trading-session, and cooldown
     filters;
   - duplicate-entry, pyramiding, reverse, reduce, and exit policies;
   - portfolio correlation and existing-exposure rules.
6. **Risk sizing and survival gates**
   - order, symbol, account, gross/net exposure, leverage, and open-order caps;
   - daily and rolling loss, drawdown, consecutive-loss, and strategy-failure
     halts;
   - volatility-aware and uncertainty-aware position sizing;
   - symbol/account/broker/global circuit breakers plus operator kill switch.
7. **Execution feasibility**
   - broker precision and minimum-notional normalization;
   - fee, spread, slippage, market-impact, funding, borrow, and latency budget;
   - source freshness, reconciliation, stable idempotency, and durable audit
     identity.
8. **Ledger and feedback**
   - Portfolio writes the simulated ledger; Live writes and reconciles the broker
     ledger;
   - both feed performance attribution back to candidate evidence;
   - Alpha, Portfolio, and Live ledgers remain isolated.

## Canonical Decision Contract

The current `workflow`, `execution`, and `data_origin` axes cannot distinguish
Alpha from Portfolio because both consume market data and simulate execution. Add an
orthogonal field:

```text
decision_policy = atomic_signal | weighted_ensemble
```

The minimum derivation is:

| Mode | Workflow | Execution | Data origin | Decision policy |
|---|---|---|---|---|
| Alpha | realtime or backtest | simulated | market | atomic_signal |
| Portfolio | realtime or backtest | simulated | market | weighted_ensemble |
| Live | realtime | broker | market | weighted_ensemble |
| Runtime | realtime | signal_only | market | atomic_signal or weighted_ensemble |
| Unclassified research | backtest | simulated | historical/market | unspecified |

Every decision also records strategy, interval, weights, rule-policy version,
risk-policy version, code/config/data versions, stage, and intent sequence.

## Promotion Path

The operational path is:

```text
Alpha historical atomic replay
  → eligibility/evidence gate
  → Portfolio historical ensemble replay
  → Alpha and Portfolio forward validation
  → Live Shadow
  → Capped Canary
  → Approved Live
```

`Live Shadow` and `Capped Canary` belong between Portfolio and unrestricted Live:

- Live Shadow reads live conditions and produces decisions but cannot submit a
  broker order.
- Capped Canary may submit only inside explicit account, symbol, notional, and
  loss limits with automatic rollback.
- Approved Live still remains subject to every gate on every order.

## Survival-First Objective

Order objectives by priority:

1. preserve capital and ledger correctness;
2. obey risk, freshness, reconciliation, and execution constraints;
3. maintain positive net expectancy across declared evaluation windows;
4. improve risk-adjusted return and consistency;
5. pursue daily profit only when valid opportunities pass all prior gates.

Do not loosen thresholds, increase position size, or create a trade merely
because the current day is below a profit target. When a daily target is met,
the policy may reduce new-risk budget or lock a portion of gains; this behavior
must be versioned and tested rather than hard-coded as a universal rule.

## Current Implementation Gap

The runtime now exposes isolated atomic Alpha ledgers and a weighted Portfolio
ledger across configured intervals. Those ledgers are checkpointed and can
continue forward after restart. A deterministic historical bootstrap is still
required to populate a configured lookback window immediately: it must replay
globally ordered closed candles without higher-timeframe look-ahead, seed the
same isolated ledgers, and then hand them to the forward runtime.

The dashboard must therefore:

- keep every mode navigable;
- present historical atomic runs inside Alpha and historical weighted runs
  inside Portfolio;
- show the actual signal runtime only in Runtime;
- show a truthful unavailable state for missing Alpha, Portfolio, or Live runs;
- never use Runtime data as Portfolio/Live performance;
- never imply broker reconciliation or profitability without ledger evidence.

## Acceptance Criteria

- An Alpha result is keyed by strategy and interval and cannot enter Portfolio or Live
  metrics directly.
- Portfolio and Live consume the same versioned ensemble and gate outputs.
- Portfolio never requires broker credentials.
- Live cannot submit from Portfolio, Live Shadow, or a missing-gate state.
- Missing or conflicting higher-timeframe evidence resolves to `HOLD`.
- Costs and funding are included before a candidate is judged profitable.
- Daily-loss and drawdown halts survive restart and block new risk.
- A daily profit target never overrides a failed rule or risk gate.
- The UI never leaks data from one mode into another mode's empty state.
