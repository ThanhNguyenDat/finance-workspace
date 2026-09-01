# Trading Dashboard Development Playbook

Use this as a searchable reference after reading the parent `SKILL.md`. Read
only the sections matching the screen, data contract, and interaction in scope.

Use this skill for changes under `web/src/pages/trade`, trading navigation,
trading metrics presentation, journal analytics, or production verification of
`https://finance.thanhne.io.vn/trading`.

## Read first

1. Read repository `AGENTS.md` and `README.md`.
2. Read `.agents/rules/coding-and-verification.md`.
3. Read the current Finance Live Action protobuf and Finance MW gateway types
   before inventing a metric or interpreting a source value.
4. Inspect the selected execution context: scope, run, interval, decision policy,
   data origin, execution mode, metrics source, sequence, and freshness.

## Truthful metric rules

- Never alter or relabel raw PnL in the UI to make a business target appear met.
- Treat Alpha and Portfolio ledger values as simulated unless the typed source is
  explicitly `broker_reconciled` or `mt5_reconciled`.
- Derived metrics must state their input scope and limitations. A daily metric
  derived from retained closed trades is not automatically a complete 90-day
  holdout report.
- A missing Sortino, cost-drag, stress, regime, statement, or reconciliation
  field remains unavailable. Do not synthesize a passing value.
- Count raw strategy families by stable strategy identity, not by parameter
  variant, interval, worker, or replay/forward duplicate.
- Keep source, scope, sequence, observed time, market-event time, and freshness
  visible wherever a number may otherwise look authoritative.

## Monitoring information hierarchy

A trading-bot monitor is an operational product, not only a performance report.
Arrange information in this order unless the route has a narrower purpose:

1. **Safety and freshness** — runtime health, execution halt state, broker/data
   connectivity, stale snapshot warnings, reconciliation state, and the exact
   scope being observed.
2. **Account outcome** — equity, realized and unrealized PnL, daily PnL, ROI with
   its denominator, drawdown, costs, funding or swap, and broker-truth status.
3. **Open risk** — positions, exposure, leverage, margin, liquidation distance,
   stop coverage, concentration, and correlated risk.
4. **Strategy behavior** — active strategy families, weights, signals, regime,
   recent decisions, promotion readiness, and disabled or degraded strategies.
5. **Market and data pipeline** — price context, volatility, Kline freshness,
   ingest lag, gaps, and upstream readiness.
6. **Detailed evidence** — orders, fills, closed trades, reconciliation residuals,
   logs, and drill-down history.

A red safety condition must remain visible above positive PnL. Do not let a good
headline number hide stale data, reconciliation failure, excessive drawdown, or
an execution halt.

## Information ownership and de-duplication

Every identity, context value, metric, control, and insight has one primary home.
A secondary appearance is allowed only when it adds a different decision or a
clear drill-down path.

- The application header owns global navigation and compact instrument context.
  The route content owns the one primary page heading and description. Do not
  repeat the route title in both surfaces.
- The page heading owns selected scope identity. Do not repeat the same symbol,
  portfolio, trade count, and PnL in the topbar, page header, card header, and
  every table row.
- Do not render a table column for a dimension that is invariant in the current
  response contract. A single-symbol history response does not need an
  `Instrument` cell repeated for every row.
- Give each headline metric one decision-grade presentation. A supporting chart
  may show the same measure over time, but do not add another equal-weight card
  that restates the same scalar.
- Research and promotion readiness belongs below the live operations view or in
  a collapsed/detail surface. It must not displace bot state, freshness, current
  risk, and today's outcome from the first viewport.
- Hide or disable controls that have no action: reset without active filters,
  pagination with one page, and recovery actions when the ledger is simply empty.
- When two sections need the same live metric stream, subscribe once in their
  nearest common owner and pass the typed snapshot down. Duplicate WebSocket or
  REST subscriptions on one route are a correctness and resource bug.
- A lane comparison uses bounded unary snapshots for every registered scope,
  never one WebSocket per variant. Rank normalized backend metrics (profit
  factor, win rate, expectancy, then drawdown) ahead of absolute PnL, retain
  partial successful rows when one scope is unavailable, and label Alpha or
  Portfolio results as simulated rather than broker truth.

## Layout selection framework

The dashboard references supplied by the repository owner represent reusable
layout patterns. Translate their information architecture into the existing
Finance visual system; do not copy a third-party dashboard pixel-for-pixel or
commit reference artwork unless its reuse rights are established.

### 1. KPI-first layout

Use when an operator must understand the bot in a few seconds.

- Put no more than five to eight decision-grade KPIs in the first viewport.
- Prefer safety, daily outcome, drawdown, exposure, and data freshness over
  decorative totals.
- Every KPI must expose its scope, period, source, and stale or unavailable state.
- A KPI should link or scroll to the evidence that explains it.

Best fit: `/trading/overview` and compact mobile monitoring.

### 2. Overview-to-detail layout

Use the sequence `KPI → trend → analysis → evidence table`.

- Start with the current condition.
- Follow with the time-series behavior that produced it.
- Add diagnostic comparisons or distributions.
- End with the ledger, fills, or reconciliation rows supporting the conclusion.

Best fit: performance review, drawdown investigation, strategy evaluation, and
broker-parity analysis.

### 3. Sidebar-filter layout

Use only when the user repeatedly changes at least four persistent dimensions,
such as account, broker, symbol, strategy, interval, workflow, run, and date.

- Desktop may use a collapsible filter rail with applied-filter count and clear
  action.
- Mobile must use a sheet or drawer; never reserve permanent horizontal space
  for a filter sidebar.
- Keep the current scope visible even when the filter surface is closed.
- Expensive filters must be deferred, debounced, or server-side and must not
  block route transitions.
- Normalize free-text ledger filters on both the query and indexed fields.
  Treat case, surrounding whitespace, underscores, and ASCII or Unicode
  dash variants equivalently so visually identical setup names match.

Best fit: journal, reconciliation, multi-account portfolio, and strategy research
views. A small filter set remains in a compact top bar instead.

### 4. Grid-card layout

Use a consistent card grid when several monitoring modules have comparable
importance.

- Align card titles, update times, empty states, and action placement.
- Use a small set of approved spans rather than arbitrary card dimensions.
- Do not force every metric into its own card; group tightly related values.
- Keep the primary chart wider than secondary diagnostic cards.

Best fit: the bot operations overview with runtime, PnL, positions, strategy,
market, and pipeline modules on one screen.

### 5. Two-column layout

Use when one region provides context for another.

- Common patterns are `overview + detail`, `position list + selected position`,
  `strategy list + strategy evidence`, and `filter summary + results`.
- Give the analytical or selected-detail column more width.
- Collapse to one column on narrow screens without changing the reading order.
- Do not use two columns merely to fill whitespace.

Best fit: position monitoring, strategy inspection, execution diagnostics, and
reconciliation review.

### 6. Storytelling layout

Use for a finite review or incident narrative, not as the primary always-on
operations screen.

- Sequence sections as `what happened → why → impact → evidence → action`.
- Use annotations and concise automatic insights only when their derivation is
  deterministic and inspectable.
- Finish with a concrete next action or promotion/blocking decision.
- Avoid prose that presents correlation as causation.

Best fit: daily or weekly bot reports, drawdown postmortems, and strategy
promotion evidence.

### 7. Drill-down layout

Use when aggregate signals must lead to progressively narrower evidence.

- Preserve the parent scope and filters while navigating deeper.
- Make cards, chart points, buckets, and table rows actionable when a meaningful
  child view exists.
- Prefer route or URL state for shareable analysis; use transient modal detail
  only for small, non-navigational inspections.
- Breadcrumbs must include account or portfolio, symbol, strategy, run, and
  interval when those dimensions determine the numbers.

Best fit: KPI → strategy → trade → fill/reconciliation and account → position →
order workflows.

## Recommended composition for Finance trading routes

Use a deliberate combination rather than selecting one pattern for every page:

| Route or surface | Primary composition |
| --- | --- |
| `/trading/overview` | KPI-first + grid-card + overview-to-detail |
| `/trading/chart` | Full-height trading terminal + price/volume panes + evidence dock |
| `/trading/journal` | Compact filter bar or filter drawer + paginated evidence table + row drill-down |
| `/trading/distribution` | Overview-to-detail + two-column chart/statistics + drill-down to matching trades |
| Strategy monitoring | Grid-card inventory + two-column selected-strategy detail + drill-down |
| Position and execution monitoring | KPI-first safety strip + two-column position/detail + order/fill drill-down |
| Broker reconciliation | KPI-first parity summary + overview-to-detail residual analysis + evidence table |
| Daily or weekly report | Storytelling layout built from the same typed metrics, never a separate truth model |

The default live-monitor first viewport should answer these questions without
scrolling on a desktop viewport:

1. Is the bot, market data, and broker connection healthy and fresh?
2. Is trading active, halted, simulated, or broker-executed?
3. What is today's realized and unrealized outcome after known costs?
4. What is the current drawdown and open exposure?
5. Which position or strategy requires attention now?

## Trading chart workspace

The canonical market workspace is `/trading/chart`. Keep `/trading/data`,
`/trading/data/klines`, `/data`, and `/data/klines` as redirects only.

- Reuse Lightweight Charts with candles in pane 0, volume in pane 1, and
  optional removable/resizable oscillator panes after them.
- Default to candles, volume, current price, typed position levels, and the
  latest signal. Historical trades and Memory/DB diagnostics are opt-in.
- Show only typed entry, stop, target, liquidation, and mark values. Never
  invent pending orders, fills, or broker truth; keep the source visible.
- Indicators are pure browser presentation utilities with unit tests and
  never feed Alpha, Portfolio, Risk, or execution decisions.
- Open a bounded recent window: about 180 bars for 5m, 150 for 15m–1h,
  and 100 for 4h–1d; preserve range while older history lazy-loads.
- Cap retained trade markers at 240 trade pairs to protect the main thread.
- Full screen uses the browser Fullscreen API and keeps all controls usable.
- A TradingView-style claim requires functional drawing controls, not decorative icons.
  The initial supported set is cursor/pan, trend line, horizontal and vertical
  lines, rectangle, price/time measure, and text annotations with undo/redo,
  lock, hide, remove-last, and clear controls.
- Drawings are stored in domain coordinates so pan, zoom, resize, and lazy history
  loading do not detach them from price/time. Browser-local persistence must be
  labeled as browser-local and scoped by symbol, interval, and execution scope;
  do not imply account/server synchronization until a typed backend contract exists.
- Bound a chart to 120 retained drawings and 50 undo snapshots so annotations do
  not create unbounded browser work. Mobile drawing controls remain at least 44px.
- Do not display clickable BUY/SELL quotes without typed bid/ask data, and do not
  turn a presentation drawing into an Alpha, Risk, or execution input.
- Keep Strategy as `Strategy Lab`; Chart is the primary monitoring route.
- The chart identity area exposes a lane pill row (Alpha/Portfolio/Live/...,
  from `lanesWithContexts`) and, only when the current lane has more than one,
  a workflow pill row (Realtime/Backtest, from `workflowsForLane`). A lane
  never hides itself from a lack of same-workflow data — switching lane keeps
  the current workflow when the target lane has it, via
  `pickContextForLaneWorkflow`, and otherwise falls back to that lane's
  realtime-first default. The first-load default context is realtime-first
  within a lane (`selectDefaultContext` in `utils/tradingScope.ts`); backtest
  is opt-in through the workflow pill, never the initial view.

## Interaction and visual rules

- Canonical routes are `/trading/overview`, `/trading/chart`,
  `/trading/journal`, and `/trading/distribution`; preserve reviewed compatibility redirects.
- Mobile interactive controls must be at least 44 by 44 CSS pixels.
- Mobile application headers use fixed 44-pixel side controls around one flexible
  identity column. Do not combine 44-pixel controls, vertical padding, and a
  shorter fixed header height.
- The persistent sidebar header and application topbar must consume the same
  `--header-h` token, use explicit border-box heights, and align their lower
  borders within one CSS pixel in browser geometry tests.
- Move refresh, theme, role, and logout into the mobile overflow menu when keeping
  them inline would truncate page or instrument identity.
- Use visual hierarchy, spacing, typography, and semantic status tokens before
  adding decorative color. Reserve red, amber, and green for state and outcome.
- Charts require units, time zone, comparison period, source, and a usable empty
  or stale state. Tooltips must not be the only place critical values appear.
- R-multiple histograms reserve `BE` for exact zero only. Small positive R
  values use their own range, boundaries agree with outlier semantics, and a
  zero-count bucket renders no artificial minimum-height bar.
- Wide ledgers scroll inside their card rather than forcing document overflow.
- A ledger `Layer` filter selects an authorized Alpha or Portfolio execution
  context and lets the scoped history request replace the rows; it never merges
  trades from multiple contexts in the browser. A `Setup` filter is row-level,
  uses `rule_id` with strategy only as a compatibility fallback, and normalizes
  case, whitespace, underscores, and dash variants consistently across tables.
- Never mount an unbounded trade ledger into the DOM. Paginate or virtualize
  large datasets, cap expensive chart points, reuse formatters, and defer
  full-ledger search so live snapshot updates cannot freeze the browser.
- A regression fixture must use at least 2,000 trades and assert that the journal
  renders no more than the configured page size at once.
- Support both dark and light themes, mobile and desktop viewports.
- Keep trading analytics usable when the selected scope has no closed trades,
  no position, or an unavailable metrics snapshot.
- Increment the `finance-web-contract` marker in `web/index.html` only when the
  production verifier's required public bundle contract changes. Keep the
  verifier script and marker in the same reviewed change.

## Dashboard update checklist

For every material dashboard update, update this skill in the same pull request
when the change teaches a reusable layout rule, performance limit, metric
semantic, interaction pattern, or production-verification requirement.

Before implementation, record:

- the operator question the page answers;
- the selected layout pattern and why competing patterns were rejected;
- the first-viewport KPIs and their typed sources;
- the drill-down path from summary to evidence;
- desktop and mobile filter behavior;
- expected maximum data volume and rendering strategy;
- empty, stale, degraded, unauthorized, and reconciliation-failure states;
- the primary owner for every repeated context value or metric;
- whether an existing data subscription can be lifted and shared rather than
  duplicated.

A screenshot can validate composition but cannot prove data semantics,
performance, authorization, or production delivery.

## Required checks

Run focused tests first, then the repository web gate:

```bash
cd web
npx vitest run \
  src/components/Header.test.tsx \
  src/components/ChartDrawingLayer.test.tsx \
  src/components/chartDrawings.test.ts \
  src/components/Klines.behavior.test.tsx \
  src/Container.test.tsx \
  src/pages/DataLayerPage.test.tsx \
  src/pages/trade/TradingJournalPages.test.tsx \
  src/pages/trade/TradingJournalPerformance.test.tsx \
  src/pages/trade/TradingBusinessTargetsPanel.test.tsx \
  src/utils/chartIndicators.test.ts
npm run lint
npm run build
npm run test:browser

cd ..
timeout --signal=TERM --kill-after=5s 1m \
  bash scripts/tests/test_verify-production-web.sh
```

Every browser test uses a hard timeout through the package script. Review every
new or changed Playwright baseline before committing it. Do not use automatic
snapshot updates as approval; the generated image is evidence to inspect.

Node 26 exposes experimental process-level web storage without a backing file.
If an otherwise unrelated jsdom sweep fails at every `window.localStorage.clear()`
and prints `--localstorage-file was not provided`, rerun the bounded suite with
`NODE_OPTIONS=--no-experimental-webstorage`. This lets jsdom own browser storage;
do not patch individual tests or accept those failures as application regressions.

For layout changes, browser coverage must include:

- dark and light themes;
- mobile and desktop viewports;
- no document-level horizontal overflow;
- keyboard and touch access to filters and drill-down actions;
- a large-data fixture for tables or charts affected by the change;
- the primary empty, stale, and degraded states.

## Delivery and production evidence

1. Push the scoped branch and require Finance MW CI/CD to pass, including the
   Finance Live Action protobuf parity job.
2. Merge only after the pull request is current and mergeable.
3. Let the main workflow publish the immutable web image and deploy it through
   Coolify; never patch the server directly.
4. Require terminal `production/web-verification=success` on the exact source
   SHA. `.github/workflows/verify-web.yml` checks that the
   immutable image exists and that the public HTML plus JavaScript bundle contain
   the versioned dashboard contract and visible target labels. Its ten-minute
   retry boundary treats a stale bundle as a deployment failure.
5. When the UI consumes live metrics, retain the existing production trading
   verifier for login, authorization, typed metrics, and upstream health.
6. If raw PnL is unchanged, state that explicitly: a UI release can add new
   derived evidence without changing trading history or strategy behavior.
