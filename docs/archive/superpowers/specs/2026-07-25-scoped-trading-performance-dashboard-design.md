# Scoped Trading Performance Dashboard Design

## Goal

Redesign the finance-web trading dashboard so operators can evaluate a bot without mixing results from different brokers, accounts, strategies, or execution environments.

The default view must answer:

1. Is the selected bot profitable in the selected execution scope?
2. What drawdown and trade quality produced that result?
3. Which recent trades should be investigated?

The design must support future multi-broker, multi-account, multi-portfolio, and multi-bot operation without encoding unrelated concepts in a single trade-mode enum.

## Current-State Findings

The current trade model and dashboard are not sufficiently scoped:

- persisted trades contain `symbol_id` and a flat `mode` of `demo`, `backtest`, or `live`;
- the trade service can filter by mode, but the web-data contract drops mode and forwards opaque JSON;
- frontend trade and trade-state types do not contain mode, broker, account, portfolio, bot, or run identity;
- dashboard metrics are selected by symbol and rule, so independent accounts or bot instances can be aggregated accidentally;
- the current runtime payload is not necessarily a broker-reconciled execution ledger.

Adding only a `paper` enum value would address the immediate label but would not prevent future cross-account or cross-bot aggregation.

## Domain Semantics

> **Semantic correction (2026-07-27):** the earlier definition of Alpha as a
> sample dataset is superseded by
> [Trading Decision Pipeline](../../../specs/trading-decision-pipeline.md).
> Alpha is now an atomic strategy-by-interval simulated-execution lane. A sample
> dataset, when needed, is only a data source and must not be presented as a
> trading mode.

The following concepts remain separate:

- **Portfolio**: weighted-ensemble decisions evaluated over historical replay or
  live market data with simulated execution.
- **Live**: a realtime bot whose orders, positions, and PnL are reconciled with a funded broker account.
- **Backtest**: a historical workflow. Atomic runs appear under Alpha and
  weighted-ensemble runs appear under Portfolio rather than as a peer mode.
- **Alpha**: independent simulated execution for each valid strategy and
  interval signal over historical replay or live market data, without
  cross-strategy voting.
- **Legacy**: historical data that cannot be mapped deterministically to a trading scope.

The UI derives Portfolio and Live labels from typed run properties instead of persisting a single catch-all UI mode.

## Canonical Identity Model

### TradingScope

`TradingScope` is the stable identity used for authorization and performance aggregation.

Required fields:

- `scope_id`
- `owner_id`, representing the user or tenant that owns the scope
- `venue_id`, representing the broker, exchange, or internal simulator
- `execution_account_id`, referencing an internal paper or live ledger account
- optional `broker_account_id`, required for broker-executed Live scopes
- `portfolio_id`
- `bot_id`
- `strategy_id`
- `strategy_version` as a string
- `market_type`
- created and updated timestamps

An account identifier exposed to the UI must use a safe display label and must not reveal credentials or sensitive broker identifiers.

Portfolio scopes use an internal simulated ledger account and do not require a broker account. Live scopes require a broker account that belongs to the same owner as the scope.

### TradingRun

`TradingRun` records one runtime session, deployment, or experiment beneath a scope.

Required fields:

- `run_id`
- `scope_id`
- `workflow`: `realtime` or `backtest`
- `execution`: `signal_only`, `simulated`, or `broker`
- `data_origin`: `market`, `demo`, or `legacy`
- lifecycle status
- `started_at`
- optional `stopped_at`

The contract derives these primary lanes:

- Alpha: `workflow=realtime|backtest`, `execution=simulated`,
  `data_origin=market`, `decision_policy=atomic_signal`
- Portfolio: `workflow=realtime|backtest`, `execution=simulated`,
  `data_origin=market`, `decision_policy=weighted_ensemble`
- Live: `workflow=realtime`, `execution=broker`, `data_origin=market`
- Unclassified research: `workflow=backtest` without a recognized decision policy
- Legacy: `data_origin=legacy`

Portfolio and Alpha are both simulated executions over market data, so the current
three axes cannot distinguish them safely. The additive decision-pipeline
contract must include `decision_policy=atomic_signal|weighted_ensemble`. Alpha is
`atomic_signal`; Portfolio and Live are `weighted_ensemble`. Until that field is
available, the UI may expose a navigable, truthful unavailable view but must not
infer or fabricate a Alpha/Portfolio run.

`signal_only` is an explicit non-ledger state for runtimes that evaluate strategies but do not execute or simulate orders. Signal-only runs cannot appear as Portfolio or Live performance.

### Trade

Every new trade references `run_id`. Scope identity is obtained through the run.

Trade remains responsible for order and result facts such as:

- symbol;
- side, quantity, leverage, entry, and exit;
- realized PnL and return;
- broker order and position identifiers when applicable;
- close reason and timestamps.

Context fields may be denormalized later for measured query-performance needs, but `TradingScope` and `TradingRun` remain canonical.

## Identity and Aggregation Rules

- Performance metrics always group by `scope_id`.
- `run_id` provides session drill-down, provenance, and audit correlation.
- Portfolio, Live, Backtest, Alpha, and Legacy results are never combined implicitly.
- Changing account, bot, strategy version, or environment changes the selected scope and recomputes every metric consistently.
- A trade without a recognized scope cannot enter Portfolio or Live metrics.
- Broker/account ownership is validated server-side; a client-provided scope identifier is not trusted on its own.
- Redis keys, WebSocket stream identities, checkpoints, and metric projections include `scope_id`.

## API and Streaming Contracts

### Typed context

The web-data contract gains a typed execution-context block containing:

- scope and run identifiers;
- safe broker/account display metadata;
- portfolio and bot identifiers;
- strategy identifier and version;
- workflow, execution, data origin, and reconciliation status.

Existing opaque JSON fields remain temporarily for compatibility, but no new domain behavior is added only to those blobs.

### Queries

History and performance requests accept `scope_id` as the primary filter and may accept `run_id` for drill-down.

Legacy filters such as symbol, interval, side, and old mode remain supported during migration. They cannot authorize access or override scope isolation.

### Realtime data

Each snapshot and incremental event carries `scope_id`, `run_id`, sequence information, and source/reconciliation status. The client discards events that do not match the active scope.

Multiple scopes may share a physical stream connection, but their state is keyed independently.

### Live order safety

Live order requests include:

- `scope_id`;
- an idempotency key or stable client order identifier;
- the intended symbol and order parameters.

The server resolves the broker account from the authorized scope, validates ownership, records audit correlation, and rejects scope/account mismatches.

## Dashboard Information Architecture

### Scope toolbar

The top toolbar selects one context at a time:

1. environment: `Alpha`, `Portfolio`, or `Live`;
2. broker account or portfolio;
3. bot and strategy version;
4. symbol or `All symbols`.

The operating hierarchy is `Alpha → Portfolio → Live`. Alpha is the default when it
exists, followed by Portfolio and Live. Historical runs remain inside their
decision lane, and each run stays isolated by scope. Alpha results must never be
mixed directly into Portfolio or Live performance.

When a lane has no active run, it remains navigable and presents a truthful
empty state. It must not display another lane's metrics.

Legacy data is available through an explicit `Legacy / Unscoped` view and is excluded from Portfolio and Live.

### Primary summary

Only four KPI cards appear above the fold:

- Net realized PnL;
- Maximum drawdown;
- Profit factor;
- Win rate.

Closed-trade count and selected time range appear as compact context rather than another card. The current Readiness card is removed.

### Primary analysis

The cumulative realized PnL chart occupies most of the main area. It is labelled as cumulative realized PnL rather than account equity unless actual equity snapshots are available.

A compact position panel shows the open position for the active scope:

- symbol and side;
- entry, stop loss, and take profit;
- open time;
- source and reconciliation state.

The panel must not show a Live result as authoritative when it is only a runtime estimate.

### Secondary analysis

The first section below the chart is recent closed trades. Secondary tabs contain:

- Breakdown;
- Calendar;
- full trade history.

Long/short analysis and calendar views are secondary. Implementation paths and runtime diagnostics are admin-only and remain outside the main performance flow.

## Data Truth and Status Labels

Readiness is not a primary performance metric. Data quality appears only when it changes interpretation or requires action.

Allowed status labels include:

- `Broker reconciled`;
- `Runtime estimate`;
- `Signal only — no execution ledger`;
- `Simulated execution`;
- `Independent strategy simulations`;
- `Legacy / Unscoped`;
- `Stale`.

Live PnL receives the normal Live presentation only after broker reconciliation. Runtime-estimated PnL remains explicitly labelled.

## Backward-Compatible Migration

### Phase 1: Add identity tables

- Add `trading_scopes`.
- Add `trading_runs`.
- Add nullable `run_id` to trades.
- Add indexes for scope/run history access.
- Keep existing trade mode and version fields unchanged.

### Phase 2: Extend contracts

- Add optional typed context to protobuf and web-data responses.
- Add optional `scope_id` and `run_id` filters.
- Preserve existing JSON payloads and legacy request fields.
- Reject unknown enum values explicitly rather than mapping them to empty strings.

### Phase 3: Dual-write

- New runtimes create or resolve a scope and create a run.
- New trades persist `run_id`.
- Existing consumers continue to receive the legacy payload while new consumers adopt typed context.
- Broker reconciliation supplies broker order, position, and account facts for Live runs.

### Phase 4: Deterministic backfill

- Backfill only when broker, account, bot, strategy version, and run provenance can be determined reliably.
- Create synthetic legacy runs for deterministic cohorts when necessary.
- Assign unresolved rows to `Legacy / Unscoped`.
- Never infer Portfolio or Live from incomplete historical data.

### Phase 5: Enable the scoped dashboard

- Enable Portfolio and Live scope selection after new writes and realtime streams are scope-aware.
- Keep the legacy view separate.
- Compare projection totals with source ledgers before making the new dashboard the default.

### Phase 6: Deprecate legacy contracts

- Stop expanding opaque JSON contracts.
- Remove old mode-based dashboard behavior only after all consumers use typed context.
- Retain compatibility wrappers for a defined deprecation window.

## Idempotency and Consistency

- Live broker trades use a uniqueness boundary based on scope plus broker order/trade identity.
- Simulated trades use run plus stable client order identity.
- Duplicate messages do not create duplicate trades or double-count metrics.
- Scope/run metadata is immutable for a persisted execution event.
- Reconciliation corrections are auditable and do not silently move a trade between scopes.
- Stream sequence handling is independent per scope.

## Authorization

- Every scope belongs to a tenant or authorized owner.
- List, history, metrics, stream, and order endpoints enforce scope ownership server-side.
- Account selectors return safe labels, not credentials.
- Admin diagnostics do not bypass trade/account isolation.
- Cross-scope aggregation requires an explicit authorized portfolio query.

## Error and Empty States

- No configured Portfolio scope: explain that Portfolio uses weighted multi-interval
  decisions, Rules/Risk gates, and a simulated ledger without broker
  credentials.
- No configured Live scope: do not suggest Live data exists.
- No configured Alpha scope: explain that Alpha evaluates each strategy and
  interval independently and that no simulation run is active.
- Signal-only scope: explain that performance cannot be calculated until a paper or broker ledger is connected.
- Scope has no closed trades: show zero metrics and an explicit empty chart.
- Stale stream: retain the last snapshot with a visible stale label.
- Unknown or unauthorized scope: reject the request and clear scope-specific client state.
- Unreconciled Live source: label values as runtime estimates.

## Testing

### Domain and persistence

- create and resolve stable scopes;
- create separate runs beneath one scope;
- prevent trades from changing run/scope identity;
- verify unique/idempotent trade writes;
- verify migration and rollback behavior;
- verify deterministic and unresolved legacy backfills.

### API and streaming

- typed context round-trips through gRPC, HTTP, and WebSocket;
- legacy clients continue to work during migration;
- events for one scope cannot update another scope;
- unauthorized account and scope access is rejected;
- Live order requests enforce scope ownership and idempotency;
- reconciliation status is preserved.

### Metrics

- two accounts trading the same symbol remain isolated;
- two bot instances using the same strategy remain isolated;
- multiple runs aggregate correctly by scope;
- Portfolio, Live, Alpha, Backtest, and Legacy never mix;
- duplicate events do not change totals.

### Web

- scope selectors update all cards, chart, position, and trade rows together;
- Portfolio is the default when available, otherwise Live;
- Alpha is navigable as an isolated atomic-simulation lane;
- Readiness is absent from the primary dashboard;
- runtime-estimated and broker-reconciled Live data have distinct labels;
- diagnostics remain access-controlled;
- responsive layouts preserve the scope context.

## Observability and Rollout

Track:

- unscoped trade count;
- trades and positions by workflow/execution/data-origin;
- reconciliation lag and failures;
- duplicate/idempotency conflicts;
- stream drops and stale snapshots by scope;
- metric mismatches between projections and broker or simulated ledgers.

Rollout uses a feature flag for the scoped dashboard. The flag is enabled only after:

- new writes carry run identity;
- stream state is scope-isolated;
- authorization tests pass;
- Portfolio projection totals match the simulated ledger;
- Live projection totals match broker reconciliation within an agreed tolerance.

## Acceptance Criteria

- Portfolio and Live performance cannot be mixed accidentally.
- Two accounts, bot instances, strategy versions, or runs remain distinguishable.
- Backtest data stays outside the operating dashboard.
- Alpha and Legacy data are explicitly labelled and excluded from Portfolio and Live performance.
- The default desktop view contains only the scope toolbar, four primary KPIs, cumulative PnL, open position, and recent trades.
- Readiness is removed from the primary view.
- Live PnL is not presented as broker truth before reconciliation.
- Existing clients continue operating throughout the additive migration.
- The system supports adding another broker without changing the meaning of existing scope or run fields.

## Out of Scope

- implementing a new backtest research dashboard;
- portfolio-level allocation and risk optimization;
- replacing broker reconciliation logic;
- redesigning unrelated navigation sections;
- deleting legacy contracts before the migration window closes.
