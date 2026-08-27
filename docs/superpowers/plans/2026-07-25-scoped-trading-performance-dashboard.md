# Scoped Trading Performance Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add future-safe trading scope/run identity, propagate truthful execution context from finance-live-action to finance-web, and replace the cluttered Trading page with a scope-aware performance view that never presents signal-only state as Portfolio or Live results.

**Architecture:** `finance-mw` owns durable `TradingScope`, `TradingRun`, and trade-to-run persistence. `finance-live-action` emits a typed execution context with every WebData snapshot; finance-mw maps it into the HTTP/WebSocket contract; finance-web selects and renders one context at a time. Existing trade mode and raw JSON contracts remain compatible while new typed fields are additive.

**Tech Stack:** Go 1.24, Ent, Atlas, protobuf/gRPC, Rust/Tokio/Tonic, React 19, TypeScript, Vitest, Testing Library, Vite.

---

## Repository Boundaries

- Primary repository: `/home/lap13330/Desktop/finance-eco-system/software/finance-mw`
- Upstream WebData repository: `/home/lap13330/Desktop/finance-eco-system/software/finance-live-action`
- The protobuf files `proto/web_data.proto` must remain byte-for-byte equivalent across both repositories after generation.
- Existing user changes in `prompts/` are outside this plan and must not be modified or staged.

## File Structure

### finance-mw

- Create `internal/persistence/trading/ent/schema/trading_scope.go`: stable aggregation and authorization identity.
- Create `internal/persistence/trading/ent/schema/trading_run.go`: runtime session identity and execution truth.
- Modify `internal/persistence/trading/ent/schema/trade.go`: optional `run_id` for additive migration.
- Modify `proto/trade.proto`: optional run identity on create/list contracts.
- Modify `proto/web_data.proto`: typed execution context on snapshots and metric requests/responses.
- Modify `internal/mapper/trade.go`: map optional run UUID without breaking legacy trades.
- Modify `internal/repository/trade/repository.go` and `db_repository.go`: filter by run when supplied.
- Modify `internal/interfaces/http/trading_gateway.go`: map typed context.
- Modify `internal/interfaces/http/controllers/trading_controller.go`: include context in WebSocket payloads.
- Modify `web/src/types/index.ts`: typed execution context and scope-aware trade state.
- Modify `web/src/hooks/useTradingData.ts`: retain contexts from snapshots.
- Create `web/src/utils/tradingScope.ts`: derive truthful UI lanes and select a default context.
- Modify `web/src/pages/TradeLayerPage.tsx`: simplified scope-aware layout.
- Modify `web/src/App.css`: compact toolbar, four KPI cards, chart-first responsive layout.

### finance-live-action

- Modify `proto/web_data.proto`: same additive typed contract.
- Modify `crates/finance-api/src/config.rs`: parse and validate execution context environment.
- Modify `crates/finance-api/src/trading_api.rs`: expose immutable runtime context.
- Modify `crates/finance-api/src/grpc.rs`: attach context to snapshots and metrics.
- Modify `docker/compose*.yaml` and environment examples only where required to declare the current signal-only runtime truth.

## Task 1: Add Durable Scope and Run Persistence

**Files:**
- Create: `internal/persistence/trading/ent/schema/trading_scope.go`
- Create: `internal/persistence/trading/ent/schema/trading_run.go`
- Modify: `internal/persistence/trading/ent/schema/trade.go`
- Test: `internal/persistence/trading/ent/schema/trading_scope_test.go`
- Generated: `internal/persistence/trading/ent/**`
- Create: `migrations/trading/<timestamp>_add_trading_scopes_and_runs.sql`

- [ ] **Step 1: Write failing schema contract tests**

Add tests that inspect Ent descriptors and require:

```go
func TestTradingScopeDefinesStableIdentityFields(t *testing.T) {
	fields := fieldNames(TradingScope{}.Fields())
	require.ElementsMatch(t, []string{
		"id", "owner_id", "venue_id", "execution_account_id",
		"broker_account_id", "portfolio_id", "bot_id", "strategy_id",
		"strategy_version", "market_type", "created_at", "updated_at",
	}, fields)
}

func TestTradingRunDefinesExecutionTruthFields(t *testing.T) {
	fields := fieldNames(TradingRun{}.Fields())
	require.Contains(t, fields, "scope_id")
	require.Contains(t, fields, "workflow")
	require.Contains(t, fields, "execution")
	require.Contains(t, fields, "data_origin")
	require.Contains(t, fields, "status")
}

func TestTradeRunIDIsOptionalDuringMigration(t *testing.T) {
	runID := fieldDescriptor(t, Trade{}.Fields(), "run_id")
	require.True(t, runID.Optional)
	require.True(t, runID.Nillable)
}
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
go test ./internal/persistence/trading/ent/schema -run 'TestTrading(Scope|Run)|TestTradeRunID' -count=1
```

Expected: FAIL because the two schemas and `run_id` do not exist.

- [ ] **Step 3: Implement the minimum schemas**

Use UUID primary identifiers and string ownership fields to avoid cross-database foreign keys. Define constrained enums:

```go
field.Enum("workflow").Values("realtime", "backtest"),
field.Enum("execution").Values("signal_only", "simulated", "broker"),
field.Enum("data_origin").Values("market", "demo", "legacy"),
field.Enum("status").Values("starting", "running", "stopped", "failed"),
```

Add `field.UUID("run_id", uuid.UUID{}).Optional().Nillable()` to `Trade`.

Add indexes for:

```text
trading_scopes(owner_id, venue_id, execution_account_id, bot_id, strategy_id, strategy_version, market_type)
trading_runs(scope_id, started_at)
trades(run_id, close_at)
```

- [ ] **Step 4: Generate Ent code and migration**

Run:

```bash
go generate ./internal/persistence/trading/ent
./scripts/database.py hash trading
./scripts/database.py diff trading --to ent://internal/persistence/trading/ent/schema
./scripts/database.py validate trading
```

Expected: generated Ent code compiles and the Trading migration stream validates.

- [ ] **Step 5: Run GREEN verification**

Run:

```bash
go test ./internal/persistence/trading/ent/schema ./internal/persistence/trading/ent/...
go test ./internal/repository/trade
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add internal/persistence/trading/ent migrations/trading
git commit -m "feat(trading): add execution scopes and runs"
```

## Task 2: Carry Run Identity Through the Trade Service

**Files:**
- Modify: `proto/trade.proto`
- Modify: `internal/mapper/trade.go`
- Modify: `internal/repository/trade/repository.go`
- Modify: `internal/repository/trade/db_repository.go`
- Test: `internal/mapper/trade_test.go`
- Test: `internal/repository/trade/db_repository_test.go`
- Generated: `internal/pb/trade.pb.go`
- Generated: `internal/pb/trade_grpc.pb.go`

- [ ] **Step 1: Write failing mapper and query tests**

Require a valid run UUID to map into Ent and list filters:

```go
func TestTradeProtoToEntMapsRunID(t *testing.T) {
	runID := uuid.New()
	runIDString := runID.String()
	symbolID, err := uuid.NewV7()
	require.NoError(t, err)
	item, err := TradeProtoToEnt(&pb.Trade{
		SymbolId: symbolID.String(),
		RunId: &runIDString,
	})
	require.NoError(t, err)
	require.NotNil(t, item.RunID)
	require.Equal(t, runID, *item.RunID)
}

func TestTradeProtoToEntRejectsInvalidRunID(t *testing.T) {
	symbolID, symbolErr := uuid.NewV7()
	require.NoError(t, symbolErr)
	invalid := "not-a-uuid"
	_, err := TradeProtoToEnt(&pb.Trade{
		SymbolId: symbolID.String(),
		RunId: &invalid,
	})
	require.Error(t, err)
}
```

Repository query tests must assert that `RunID` adds a `trade.run_id = ?` predicate without changing legacy queries.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
go test ./internal/mapper ./internal/repository/trade -run 'RunID|RunId' -count=1
```

Expected: FAIL because protobuf and repository query fields do not exist.

- [ ] **Step 3: Extend the additive protobuf contract**

Append fields without renumbering existing fields:

```proto
message ListTradesRequest {
  // existing fields 1-6
  optional string run_id = 7;
}

message Trade {
  // existing fields 1-22
  optional string run_id = 23;
}
```

Run:

```bash
make proto-gen
```

- [ ] **Step 4: Implement strict mapping and filtering**

Parse non-empty run identifiers with `uuid.Parse`. Unknown or malformed values return `InvalidArgument`; they must not become empty SQL filters.

Add `RunID *uuid.UUID` to the repository query and extend the repository's
existing parameterized SQL stream builder with a bound `run_id = $N`
predicate. The stream API returns `*sql.Rows`, so switching this path to an
Ent query is outside this additive change.

- [ ] **Step 5: Run GREEN verification**

Run:

```bash
go test ./internal/mapper ./internal/repository/trade ./internal/interfaces/grpc/servers/trade
go vet ./internal/mapper ./internal/repository/trade ./internal/interfaces/grpc/servers/trade
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add proto/trade.proto internal/pb internal/mapper internal/repository/trade internal/interfaces/grpc/servers/trade
git commit -m "feat(trading): propagate trade run identity"
```

## Task 3: Define the Shared Typed Execution Context Contract

**Files:**
- Modify in both repositories: `proto/web_data.proto`
- Create: `internal/contracts/web_data_contract_test.go`
- Generated in finance-mw: `internal/pb/webdata/web_data.pb.go`
- Generated in finance-mw: `internal/pb/webdata/web_data_grpc.pb.go`
- Generated in finance-live-action through: `crates/finance-api/build.rs`

- [ ] **Step 1: Add a contract parity test**

In finance-mw, add `internal/contracts/web_data_contract_test.go` that compares the two source proto files:

```go
func TestWebDataProtoMatchesFinanceLiveAction(t *testing.T) {
	_, filename, _, ok := runtime.Caller(0)
	require.True(t, ok)
	repoRoot := filepath.Clean(filepath.Join(filepath.Dir(filename), "..", ".."))
	upstream := filepath.Join(repoRoot, "..", "finance-live-action", "proto", "web_data.proto")
	if _, err := os.Stat(upstream); errors.Is(err, os.ErrNotExist) {
		t.Skip("finance-live-action sibling repository is unavailable")
	}
	local, err := os.ReadFile(filepath.Join(repoRoot, "proto", "web_data.proto"))
	require.NoError(t, err)
	remote, err := os.ReadFile(upstream)
	require.NoError(t, err)
	require.Equal(t, string(remote), string(local))
}
```

Resolve paths from the package working directory so the test remains deterministic in the workspace; skip with an explicit message only when the sibling repository is absent in isolated CI.

- [ ] **Step 2: Extend both proto files identically**

Add:

```proto
message ExecutionContext {
  string scope_id = 1;
  string run_id = 2;
  string owner_id = 3;
  string venue_id = 4;
  string execution_account_id = 5;
  optional string broker_account_id = 6;
  string portfolio_id = 7;
  string bot_id = 8;
  string strategy_id = 9;
  string strategy_version = 10;
  string market_type = 11;
  Workflow workflow = 12;
  Execution execution = 13;
  DataOrigin data_origin = 14;
  string display_name = 15;
}

enum Workflow { WORKFLOW_UNSPECIFIED = 0; WORKFLOW_REALTIME = 1; WORKFLOW_BACKTEST = 2; }
enum Execution {
  EXECUTION_UNSPECIFIED = 0;
  EXECUTION_SIGNAL_ONLY = 1;
  EXECUTION_SIMULATED = 2;
  EXECUTION_BROKER = 3;
}
enum DataOrigin {
  DATA_ORIGIN_UNSPECIFIED = 0;
  DATA_ORIGIN_MARKET = 1;
  DATA_ORIGIN_DEMO = 2;
  DATA_ORIGIN_LEGACY = 3;
}
```

Append `ExecutionContext context = 6` to `TradingSnapshot`, optional `scope_id` and `run_id` filters to history/metrics requests, and `ExecutionContext context = 11` to `TradingMetricsSnapshot`.

- [ ] **Step 3: Generate and compile both repositories**

Run:

```bash
cd /home/lap13330/Desktop/finance-eco-system/software/finance-mw && make proto-gen
cd /home/lap13330/Desktop/finance-eco-system/software/finance-live-action && cargo test -p finance-api --no-run
```

Expected: both generated contracts compile.

- [ ] **Step 4: Run parity and protobuf tests**

Run:

```bash
cd /home/lap13330/Desktop/finance-eco-system/software/finance-mw && go test ./internal/contracts ./internal/pb/...
```

Expected: PASS.

- [ ] **Step 5: Commit in each repository**

```bash
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-live-action add proto crates/finance-api
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-live-action commit -m "feat(api): add typed execution context"
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-mw add proto internal/pb
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-mw commit -m "feat(api): add typed execution context"
```

## Task 4: Emit Truthful Context From finance-live-action

**Files:**
- Modify: `finance-live-action/crates/finance-api/src/config.rs`
- Modify: `finance-live-action/crates/finance-api/src/trading_api.rs`
- Modify: `finance-live-action/crates/finance-api/src/grpc.rs`
- Test: inline unit tests in those modules

- [ ] **Step 1: Write failing config tests**

Use a pure parser rather than mutating process environment in parallel tests:

```rust
#[test]
fn execution_context_defaults_to_signal_only_market_runtime() {
    let context = ExecutionContextConfig::from_values(ContextValues {
        broker: "binance",
        market_type: "perpetual_future",
        symbol: "BTCUSDT",
        ..Default::default()
    }).unwrap();

    assert_eq!(context.execution, ExecutionKind::SignalOnly);
    assert_eq!(context.workflow, WorkflowKind::Realtime);
    assert_eq!(context.data_origin, DataOriginKind::Market);
}

#[test]
fn broker_execution_requires_broker_account_id() {
    let result = ExecutionContextConfig::from_values(ContextValues {
        execution: Some("broker"),
        ..Default::default()
    });
    assert!(result.is_err());
}
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cargo test -p finance-api execution_context -- --nocapture
```

Expected: FAIL because execution-context config does not exist.

- [ ] **Step 3: Implement immutable runtime context**

Add `ExecutionContextConfig` to `AppConfig`, validate allowed enum strings, and derive a stable legacy scope/run identity only when explicit identifiers are absent. The derived context must remain `signal_only`; it must never claim Portfolio or Live.

Expose the context through `TradingRuntime` as immutable data.

- [ ] **Step 4: Attach context to gRPC snapshots**

Map config enums explicitly to protobuf enums. Set context on:

- `TradingSnapshot`;
- `TradingMetricsSnapshot`.

Validate optional request scope/run filters. A non-empty mismatch returns `Status::not_found` rather than silently returning another scope.

- [ ] **Step 5: Run GREEN verification**

Run:

```bash
cargo fmt --check
cargo test -p finance-api execution_context
cargo test -p finance-api grpc
cargo clippy -p finance-api --all-targets -- -D warnings
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add crates/finance-api proto
git commit -m "feat(runtime): publish execution context"
```

## Task 5: Map Context Through finance-mw HTTP and WebSocket

**Files:**
- Modify: `internal/interfaces/http/controllers/trading_controller.go`
- Modify: `internal/interfaces/http/trading_gateway.go`
- Test: `internal/interfaces/http/trading_gateway_test.go`
- Test: `internal/interfaces/http/server_test.go`

- [ ] **Step 1: Write failing mapping tests**

Construct a protobuf snapshot with a context and require the mapped HTTP snapshot:

```go
func TestParseSnapshotMapsExecutionContext(t *testing.T) {
	snapshot := validSnapshot()
	snapshot.Context = &webdata.ExecutionContext{
		ScopeId: "scope-1",
		RunId: "run-1",
		Execution: webdata.Execution_EXECUTION_SIGNAL_ONLY,
		DataOrigin: webdata.DataOrigin_DATA_ORIGIN_MARKET,
	}
	result, err := parseSnapshot(snapshot)
	require.NoError(t, err)
	require.Equal(t, "scope-1", result.Context.ScopeID)
	require.Equal(t, "signal_only", result.Context.Execution)
}
```

Server tests require `execution_context` inside WebSocket snapshot data.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
go test ./internal/interfaces/http/... -run 'ExecutionContext|Snapshot' -count=1
```

Expected: FAIL because controller DTOs do not contain context.

- [ ] **Step 3: Implement explicit mapping**

Add a typed controller DTO with snake-case JSON fields. Map unspecified protobuf values to `unspecified`; do not guess Portfolio or Live.

Pass optional scope/run filters from HTTP query → gateway → protobuf for history and trading metrics.

- [ ] **Step 4: Run GREEN verification**

Run:

```bash
go test ./internal/interfaces/http/... -count=1
go vet ./internal/interfaces/http/...
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add internal/interfaces/http
git commit -m "feat(web): expose execution context"
```

## Task 6: Add Scope Derivation and Selection to finance-web

**Files:**
- Modify: `web/src/types/index.ts`
- Modify: `web/src/context/AppContext.tsx`
- Modify: `web/src/hooks/useTradingData.ts`
- Create: `web/src/utils/tradingScope.ts`
- Create: `web/src/utils/tradingScope.test.ts`
- Modify: `web/src/pages/TradeLayerPage.test.tsx`

- [ ] **Step 1: Write failing scope utility tests**

Cover the category boundaries:

```ts
it('maps realtime simulated market context to paper', () => {
  expect(getTradingLane(context({
    workflow: 'realtime',
    execution: 'simulated',
    data_origin: 'market',
  }))).toBe('portfolio');
});

it('maps realtime broker market context to live', () => {
  expect(getTradingLane(context({
    workflow: 'realtime',
    execution: 'broker',
    data_origin: 'market',
  }))).toBe('live');
});

it('does not present signal-only as paper or live', () => {
  expect(getTradingLane(context({ execution: 'signal_only' }))).toBe('runtime');
});

it('prefers paper, then live, then runtime, then demo', () => {
  expect(selectDefaultContext(contexts).scope_id).toBe('paper-scope');
});
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd web && npm test -- src/utils/tradingScope.test.ts
```

Expected: FAIL because the utility does not exist.

- [ ] **Step 3: Implement typed context storage**

Add:

```ts
export type TradingWorkflow = 'unspecified' | 'realtime' | 'backtest';
export type TradingExecution = 'unspecified' | 'signal_only' | 'simulated' | 'broker';
export type TradingDataOrigin = 'unspecified' | 'market' | 'demo' | 'legacy';
export type TradingLane = 'portfolio' | 'live' | 'runtime' | 'alpha' | 'legacy' | 'backtest';
```

Use the WebSocket snapshot `contexts` array as the complete authoritative available set for the current source. In the current finance-live-action/gateway architecture this set is singleton or empty; future multi-context selection requires upstream source authorization/list support. Keep selection utilities future-ready, but do not aggregate observed scoped snapshots as authorization. Clear scope-specific state when a selected scope disappears or becomes unauthorized.

- [ ] **Step 4: Run GREEN verification**

Run:

```bash
cd web && npm test -- src/utils/tradingScope.test.ts src/context/AppContext.test.tsx
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/types web/src/context web/src/hooks web/src/utils
git commit -m "feat(web): model trading execution scopes"
```

## Task 7: Simplify the Trading Performance Page

**Files:**
- Modify: `web/src/pages/TradeLayerPage.tsx`
- Modify: `web/src/pages/TradeLayerPage.test.tsx`
- Modify: `web/src/App.css`
- Reuse: `web/src/components/CumulativePnlChart.tsx`
- Reuse: `web/src/components/TradeHistoryTable.tsx`

- [ ] **Step 1: Write failing behavior tests**

Require:

```ts
it('renders only the four primary KPI cards', () => {
  renderPage();
  expect(screen.getByText('Net PnL')).toBeInTheDocument();
  expect(screen.getByText('Maximum Drawdown')).toBeInTheDocument();
  expect(screen.getByText('Profit Factor')).toBeInTheDocument();
  expect(screen.getByText('Win Rate')).toBeInTheDocument();
  expect(screen.queryByText('Readiness')).not.toBeInTheDocument();
  expect(screen.queryByText('Closed Trades')).not.toBeInTheDocument();
});

it('labels signal-only runtime without presenting paper or live performance', () => {
  renderPage({ execution: 'signal_only' });
  expect(screen.getByText('Signal only — no execution ledger')).toBeInTheDocument();
  expect(screen.queryByRole('tab', { name: 'Portfolio' })).toHaveAttribute('aria-disabled', 'true');
  expect(screen.queryByRole('tab', { name: 'Live' })).toHaveAttribute('aria-disabled', 'true');
});

it('updates chart, metrics, and recent trades from the selected scope', async () => {
  renderPageWithPortfolioAndLive();
  await user.click(screen.getByRole('tab', { name: 'Live' }));
  expect(screen.getByTestId('active-scope')).toHaveTextContent('Live Account');
  expect(screen.getByText('$420')).toBeInTheDocument();
});
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
cd web && npm test -- src/pages/TradeLayerPage.test.tsx
```

Expected: FAIL on the old five-card layout and missing scope controls.

- [ ] **Step 3: Implement the chart-first layout**

The above-fold order is fixed:

1. compact scope toolbar;
2. four KPI cards;
3. cumulative PnL chart with compact position panel;
4. recent trades;
5. secondary Breakdown and Calendar tabs;
6. admin-only Diagnostics.

Remove the sample-confidence/Readiness presentation from the primary page. Keep sample size as compact chart context. Disable unavailable Portfolio/Live lanes rather than fabricating data.

- [ ] **Step 4: Implement responsive CSS**

Use existing variables and components. Desktop uses a wide chart/narrow position split; tablet wraps KPIs 2×2; mobile stacks controls and content. Do not add dependencies.

- [ ] **Step 5: Run GREEN verification**

Run:

```bash
cd web
npm test -- src/pages/TradeLayerPage.test.tsx src/components/CumulativePnlChart.test.tsx
npm run build
npx eslint src/pages/TradeLayerPage.tsx src/pages/TradeLayerPage.test.tsx src/utils/tradingScope.ts src/utils/tradingScope.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add web/src/pages/TradeLayerPage.tsx web/src/pages/TradeLayerPage.test.tsx web/src/App.css
git commit -m "feat(web): simplify scoped trading performance"
```

## Task 8: Full Verification, Documentation, and Deployment

**Files:**
- Review: `docs/superpowers/specs/2026-07-25-scoped-trading-performance-dashboard-design.md`
- Modify: execution-context defaults in `finance-live-action/docker/env/development.env` and `finance-live-action/docker/env/production.env`

- [ ] **Step 1: Verify finance-live-action**

Run:

```bash
cd /home/lap13330/Desktop/finance-eco-system/software/finance-live-action
cargo fmt --check
cargo test
cargo clippy --workspace --all-targets -- -D warnings
```

Expected: PASS.

- [ ] **Step 2: Verify finance-mw backend and migrations**

Run:

```bash
cd /home/lap13330/Desktop/finance-eco-system/software/finance-mw
gofmt -w internal/mapper internal/repository/trade internal/interfaces/http internal/persistence/trading/ent/schema
go test ./...
go vet ./...
./scripts/database.py validate trading
```

Expected: PASS.

- [ ] **Step 3: Verify finance-web**

Run:

```bash
cd /home/lap13330/Desktop/finance-eco-system/software/finance-mw/web
npm test
npm run build
npx eslint src/pages/TradeLayerPage.tsx src/pages/TradeLayerPage.test.tsx src/components/CumulativePnlChart.tsx src/utils/tradingScope.ts src/utils/tradingScope.test.ts
```

Expected: all tests and targeted lint pass. The known unrelated full-repository lint failures are documented rather than modified.

- [ ] **Step 4: Verify compatibility and dirty-worktree isolation**

Confirm:

```bash
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-mw status --short
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-live-action status --short
```

Expected: only intended commits plus the user's pre-existing finance-mw changes remain.

- [ ] **Step 5: Push and monitor CI/CD**

Push the upstream contract producer first, then finance-mw:

```bash
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-live-action push origin main
git -C /home/lap13330/Desktop/finance-eco-system/software/finance-mw push origin main
```

Watch both GitHub Actions runs to terminal success. If CI fails, inspect failed logs, fix in scope, re-run verification, and push the corrective commit.

- [ ] **Step 6: Verify production**

Verify:

- finance-live-action gRPC service is serving the new additive contract;
- `https://finance.thanhne.io.vn/trade` returns HTTP 200;
- the deployed JS bundle contains `Signal only — no execution ledger` and the scoped toolbar labels;
- the production page does not render a Readiness card;
- Portfolio/Live are not enabled unless an authoritative corresponding context exists.

- [ ] **Step 7: Final commit for any verification-only documentation**

```bash
git add docs
git commit -m "docs(trading): record scoped dashboard rollout"
```

Create this commit only when documentation actually changed.
