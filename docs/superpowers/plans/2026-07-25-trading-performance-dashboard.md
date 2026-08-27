# Trading Performance Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current implementation-heavy `/trade` page with a performance-first dashboard for evaluating and improving each bot rule.

**Architecture:** Keep trade selection and page composition in `TradeLayerPage`, move deterministic performance-series calculations into a tested utility, and render the cumulative realized PnL in a focused SVG component. Reuse existing calendar, order, history, access-control, and summary utilities so no backend or dependency change is required.

**Tech Stack:** React 19, TypeScript 5.9, Vite 8, Vitest, Testing Library, existing finance-web CSS.

---

## File Structure

- Create `web/src/utils/tradePerformance.ts`: chronological realized-PnL series, payoff ratio, sample-confidence, and side breakdown helpers.
- Create `web/src/utils/tradePerformance.test.ts`: boundary and ordering regression tests for performance helpers.
- Create `web/src/components/CumulativePnlChart.tsx`: presentational SVG chart for cumulative realized PnL.
- Create `web/src/components/CumulativePnlChart.test.tsx`: chart empty-state and accessible-label tests.
- Modify `web/src/pages/TradeLayerPage.tsx`: performance-first composition, compact rule selector, analysis tabs, live-position panel, and role-gated diagnostics/order actions.
- Create `web/src/pages/TradeLayerPage.test.tsx`: selected-rule filtering, tab switching, and access-control regressions.
- Modify `web/src/App.css`: responsive dashboard, chart, rule selector, tabs, breakdown, and compact live-position styles.

### Task 1: Lock performance calculations

**Files:**
- Create: `web/src/utils/tradePerformance.test.ts`
- Create: `web/src/utils/tradePerformance.ts`

- [x] **Step 1: Write failing helper tests**

Cover chronological close-time ordering, cumulative values, peak-to-trough drawdown points, payoff ratio with and without losses, sample labels at `0`, `29`, `30`, `99`, and `100`, and long/short grouping.

```ts
expect(buildCumulativePnlSeries(trades).map(point => point.value)).toEqual([3, 1, 5]);
expect(getSampleConfidence(29)).toEqual({ label: 'Low sample', tone: 'warn' });
expect(getSampleConfidence(30)).toEqual({ label: 'Developing', tone: 'neutral' });
expect(getSampleConfidence(100)).toEqual({ label: 'Established', tone: 'positive' });
expect(calculatePayoffRatio({ avgWin: 6, avgLoss: 2 })).toBe(3);
```

- [x] **Step 2: Run the helper test and verify it fails**

Run:

```bash
cd web && npm test -- src/utils/tradePerformance.test.ts
```

Expected: failure because `tradePerformance.ts` does not exist.

- [x] **Step 3: Implement the deterministic helpers**

Export:

```ts
export interface CumulativePnlPoint {
  tradeNumber: number;
  closeTs: number;
  value: number;
  drawdown: number;
}

export function buildCumulativePnlSeries(trades: Trade[]): CumulativePnlPoint[];
export function calculatePayoffRatio(metrics: Pick<TradeMetricsSummary, 'avgWin' | 'avgLoss'>): number;
export function getSampleConfidence(totalTrades: number): {
  label: 'Low sample' | 'Developing' | 'Established';
  tone: 'warn' | 'neutral' | 'positive';
};
export function groupTradesBySide(trades: Trade[]): { long: Trade[]; short: Trade[] };
```

Sort a copied array by `exit_ts ?? entry_ts`, accumulate PnL, track the peak, and store `peak - cumulative` as drawdown.

- [x] **Step 4: Run helper tests**

Run:

```bash
cd web && npm test -- src/utils/tradePerformance.test.ts
```

Expected: all helper tests pass.

### Task 2: Add the cumulative realized PnL chart

**Files:**
- Create: `web/src/components/CumulativePnlChart.test.tsx`
- Create: `web/src/components/CumulativePnlChart.tsx`

- [x] **Step 1: Write failing component tests**

Verify that an empty series renders `No closed trades yet`, and a populated series renders an SVG with `aria-label="Cumulative realized PnL"` plus first/latest summary labels.

- [x] **Step 2: Run the component test and verify it fails**

Run:

```bash
cd web && npm test -- src/components/CumulativePnlChart.test.tsx
```

Expected: failure because the component does not exist.

- [x] **Step 3: Implement the SVG chart**

Accept:

```ts
interface CumulativePnlChartProps {
  points: CumulativePnlPoint[];
}
```

Render a responsive `viewBox="0 0 720 240"` SVG with:

- horizontal zero line
- area fill to zero
- positive or negative line tone based on the latest value
- start, zero, and latest value labels
- latest trade marker
- explicit empty state

Use only SVG and existing CSS variables.

- [x] **Step 4: Run component tests**

Run:

```bash
cd web && npm test -- src/components/CumulativePnlChart.test.tsx
```

Expected: all chart tests pass.

### Task 3: Compose the performance-first Trading page

**Files:**
- Create: `web/src/pages/TradeLayerPage.test.tsx`
- Modify: `web/src/pages/TradeLayerPage.tsx`

- [x] **Step 1: Write failing page behavior tests**

Mock `useAppContext` with two rule states and verify:

- default content includes `Trading Performance`, `Realized PnL`, `Maximum Drawdown`, and `Cumulative Realized PnL`
- changing the selected rule updates the displayed PnL and trade count
- `Trades` reveals the history table
- `Diagnostics` reveals execution details for admin
- implementation identifiers are absent for member

- [x] **Step 2: Run the page test and verify it fails**

Run:

```bash
cd web && npm test -- src/pages/TradeLayerPage.test.tsx
```

Expected: assertions fail against the old page structure.

- [x] **Step 3: Replace the old page composition**

Implement:

- compact header with symbol, selected rule, and position badges
- button-based rule selector
- five-card KPI row
- cumulative chart and live-position grid
- collapsible quick order for roles allowed to order
- `Overview`, `Breakdown`, `Trades`, and `Diagnostics` tabs
- overview calendar plus payoff diagnostics
- long/short metric cards
- history table
- role-gated diagnostic identifiers

Remove the large catalog, default Rule Contract cards, default execution cards, and the 30-bar PnL card.

- [x] **Step 4: Run the page and focused helper/component tests**

Run:

```bash
cd web && npm test -- src/pages/TradeLayerPage.test.tsx src/components/CumulativePnlChart.test.tsx src/utils/tradePerformance.test.ts
```

Expected: all focused tests pass.

### Task 4: Add responsive presentation

**Files:**
- Modify: `web/src/App.css`

- [x] **Step 1: Add scoped dashboard styles**

Add classes for:

```text
trade-performance-header
trade-rule-switcher
trade-performance-stats
trade-performance-main
cumulative-pnl-chart
trade-analysis-tabs
trade-payoff-grid
trade-side-breakdown
trade-live-actions
```

Use existing color variables, borders, font sizes, radius, and breakpoints. At widths below `900px`, stack the main analysis columns. At widths below `640px`, allow horizontal tab scrolling and stack KPI cards.

- [x] **Step 2: Run lint and build**

Run:

```bash
cd web && npm run lint && npm run build
```

Expected: ESLint exits successfully and Vite produces `dist/`.

### Task 5: Full regression validation

**Files:**
- Verify all changed files.

- [x] **Step 1: Run the complete web test suite**

Run:

```bash
cd web && npm test
```

Expected: all Vitest suites pass.

- [x] **Step 2: Check formatting and diff scope**

Run:

```bash
git diff --check
git status --short
git diff --stat
```

Expected: no whitespace errors; only the planned web files plus pre-existing unrelated user changes appear.

- [x] **Step 3: Commit the implementation**

Run:

```bash
git add web/src/utils/tradePerformance.ts web/src/utils/tradePerformance.test.ts web/src/components/CumulativePnlChart.tsx web/src/components/CumulativePnlChart.test.tsx web/src/pages/TradeLayerPage.tsx web/src/pages/TradeLayerPage.test.tsx web/src/App.css docs/superpowers/plans/2026-07-25-trading-performance-dashboard.md
git commit -m "feat(web): prioritize bot performance analytics"
```
