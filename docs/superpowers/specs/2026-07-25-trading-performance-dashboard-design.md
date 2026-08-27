# Trading Performance Dashboard Design

## Goal

Redesign the finance-web Trading page so its default view answers three questions quickly:

1. Is the selected bot rule profitable?
2. What risk and sample size produced that result?
3. Which trades or periods should be investigated to improve the rule?

The page is a performance dashboard first. Rule implementation details and order execution controls are secondary.

## Scope

This change covers the existing `/trade` page in finance-web.

It reuses the current trade-layer state, rule state, trade history, calendar, formatting helpers, and access controls. It does not add a backend endpoint, persist new data, introduce a chart dependency, or claim metrics that the current payload cannot calculate reliably.

## Design Principles

- Lead with performance and risk, not implementation architecture.
- Label realized trade data accurately. A cumulative realized PnL series is not called an equity curve unless account equity data exists.
- Show win rate only beside payoff and sample-size context.
- Keep the live position visible without allowing it to dominate the historical analysis.
- Preserve access-controlled implementation details, but place them behind a diagnostics view.
- Use the existing visual language and responsive layout.

## Information Architecture

### Header and rule selector

The compact page header shows:

- Trading Performance
- active symbol
- live position state
- selected rule

A horizontal rule selector replaces the large searchable catalog. Each rule option shows its user-facing title and current position badge. This keeps comparison fast while removing registry paths and descriptive catalog content from the default flow.

### Performance summary

The first row contains five metrics:

- Realized PnL
- Maximum drawdown in realized PnL units
- Profit factor
- Win rate with wins and losses
- Closed trades with a sample-confidence label

Sample confidence is deliberately simple:

- fewer than 30 trades: `Low sample`
- 30 to 99 trades: `Developing`
- at least 100 trades: `Established`

The dashboard does not imply statistical significance.

### Primary analysis

The primary area is split into:

- cumulative realized PnL chart with a zero baseline and drawdown summary
- compact live-position panel

The cumulative chart is derived from trades ordered by close time. It shows the full selected-rule history rather than only the last 30 trade outcomes.

The live-position panel shows side, entry, stop loss, take profit, open time, and quick order only when the current role is allowed to place orders. Quick order is collapsed behind an explicit action to prevent accidental visual clutter.

### Analysis tabs

Four tabs structure the remaining information:

- `Overview`: performance calendar and payoff diagnostics.
- `Breakdown`: long/short performance comparison.
- `Trades`: full selected-rule trade history.
- `Diagnostics`: rule profile, intervals, execution path, and implementation identifiers where the role permits them.

The default tab is `Overview`.

## Metrics and Data Flow

The selected rule maps its frontend catalog identifier to the existing backend rule identifier. Trades are sourced from the selected rule state when present and otherwise from the symbol trade state, then filtered by backend rule identifier.

Derived metrics use `summarizeTrades`:

- total and gross PnL
- wins and losses
- win rate
- average win and average loss
- profit factor
- best and worst trade
- maximum realized-PnL drawdown

Additional presentation-only calculations:

- cumulative realized PnL points ordered by close time
- payoff ratio as average win divided by average loss
- long/short summaries using the same metric helper
- sample-confidence label based on closed-trade count

Missing trades produce zero-valued summaries and an explicit empty chart state. Infinite profit factor is rendered as `∞`.

## Component Boundaries

- `TradeLayerPage` owns rule selection, tab selection, data selection, and page composition.
- `CumulativePnlChart` renders cumulative realized PnL and has no knowledge of rules or application context.
- `TradeCalendarSection` remains responsible for daily grouping and calendar interaction.
- `TradeHistoryTable` remains responsible for trade rows.
- `TradeOrderPanel` remains responsible for broker order actions.
- `summarizeTrades` remains the single metric-calculation helper.

No new global state is introduced.

## Responsive Behavior

- Desktop: KPI cards stay in one compact row; analysis uses a wide chart and narrow position panel.
- Tablet: KPI cards wrap; analysis columns become equal width.
- Mobile: all sections stack; tabs remain horizontally scrollable; chart labels remain readable.

## Testing

Regression tests cover:

- cumulative PnL calculation in chronological close order
- drawdown and payoff metrics
- sample-confidence labels at boundary values
- selected-rule filtering
- tab content switching
- diagnostics visibility for permitted and non-permitted roles
- empty trade history rendering

Validation requires:

- targeted Vitest tests
- full web test suite
- ESLint
- TypeScript and Vite production build

## Acceptance Criteria

- `/trade` opens on a performance-first overview.
- Realized PnL, drawdown, profit factor, win rate, and trade sample size are visible without scrolling on a typical desktop viewport.
- The primary chart shows cumulative realized PnL for the selected rule in chronological order.
- Rule selection updates every performance section consistently.
- Technical rule contract and execution details are absent from the default overview.
- Full trade history is available under `Trades`.
- Existing role-based implementation-detail restrictions remain enforced.
- No backend contract or new runtime dependency is required.
