# Portfolio's "Multi-timeframe evidence" panel never populates

Revised after deeper code verification — the first draft of this spec
conflated two different symptoms under one "bug." One of them turned out to be
correct behavior once traced to its source; the other is still a real,
unresolved gap. This version separates them and focuses the investigation on
the one that's actually still open.

**2026-08-12 update**: Codex landed
`finance-live-action#81` (`b78dd7f`, "expose every evaluated interval in
runtime state") since the previous revision of this doc. It fixes exactly
what Symptom A originally flagged — `weights()` and `readiness()` now loop
over all of `EVALUATED_INTERVALS` instead of reporting only `self.interval`.
Good fix for the backend gap, but it changes `weights()`'s response shape in
a way that reopens the *frontend* symptom Symptom A was about — see the new
"Symptom A — reopened by #81" section below. Symptom B is untouched by this
PR (the diff only touches `weights()`/`readiness()`, not `ingest()`,
`portfolio_evidence`, or anything that feeds `interval_status`) and remains
exactly as described further down.

Touches `/home/lap17204/Desktop/finance/finance-live-action` (Rust) for
Symptom B; the new frontend regression below is in
`/home/lap17204/Desktop/finance/finance-mw` (`web/src/pages/StrategyLayerPage.tsx`).

## Symptom A — "Active interval" only shows 2 of 8 intervals: reopened by #81

Original diagnosis (kept for context — still accurate about *why* the old
behavior looked the way it did): `weights()` only ever reported
`self.interval`, and `current_weights` was never a real computed
weighted-ensemble value — always a static `1/N` split over whatever
strategies are registered, labeled `"current_source": "registered_strategies"`.
That part hasn't changed in #81; only the *looping* changed:

```rust
// crates/finance-api/src/trading_api.rs, weights(), after b78dd7f
let intervals = EVALUATED_INTERVALS.iter().map(|interval| {
    let current_weights = self.strategy_names.iter()
        .map(|name| (name.clone(), json!(weight)))   // still static 1/N, still unconditional
        .collect::<serde_json::Map<_, _>>();
    (interval.to_string(), json!({ ..., "current_weights": current_weights, "last_updated_ts": last_kline.map_or(0, ...), ... }))
}).collect();
json!({ self.instrument_key.clone(): intervals })
```

The consequence: `weights()` now returns a `current_weights` entry — **always
non-empty**, regardless of whether that interval has ever received a kline —
for **all 8 intervals**, every time. That's a real improvement for whatever
consumer wants per-interval registered-strategy info, but it silently
invalidates the frontend's only signal for "does this interval actually have
runtime data":

```ts
// web/src/pages/StrategyLayerPage.tsx:48-55
const availableIntervals = useMemo(
  () => INTERVALS.STRATEGY.filter(interval => {
    const state = instrumentWeights[interval];
    return Boolean(state && Object.keys(state.current_weights).length > 0)
      || trades.some(trade => trade.interval === interval);
  }),
  [instrumentWeights, trades],
);
```

Before #81, this filter accidentally worked, because `instrumentWeights[interval]`
was only ever populated for the one interval the backend reported
(`self.interval`) — every other interval was simply absent from the map, so
`state` was `undefined` and the `Boolean(state && ...)` check failed
naturally. After #81, `instrumentWeights` has an entry for all 8 intervals
unconditionally, and `current_weights` is non-empty for every one of them —
so this filter now returns `true` for all 8 intervals regardless of whether
they've ever evaluated anything. Concretely: BTC/XAU only run a 5m primary
interval today, but the "Active interval" tab strip will now show all 8 tabs
(`5m 15m 30m 1h 2h 4h 12h 1d`) with only `5m` ever actually populated —
exactly the "obsolete catalog" UX bug that
`StrategyLayerPage.test.tsx`'s `'shows only intervals backed by runtime data
and no obsolete Python catalog'` test was written to prevent, just caused by
real backend data now instead of a stale Python catalog. That existing test
doesn't catch this regression because its mock hand-crafts `strategyWeights`
with only a `5m` key present — it doesn't simulate the new
"non-empty-for-every-interval" shape #81 actually produces.

**Suggested fix** (not applied — this doc is a review finding, not a patch):
swap the gate from "`current_weights` is non-empty" (always true now) to
"`last_updated_ts > 0`" (`web/src/types/index.ts:81`), since that field is
still genuinely sourced per-interval from that interval's own kline store
(`inner.klines.get(*interval)...last kline`, `trading_api.rs`, inside the new
`weights()` loop) — it's the one field in the response that still
distinguishes "this interval has real data" from "this interval is just
listed because the backend now enumerates all 8 unconditionally." One
`Object.keys(...).length > 0` → `state.last_updated_ts > 0` swap at
`StrategyLayerPage.tsx:51`, plus updating the existing test's mock to also
give every listed interval a non-empty `current_weights` (matching the real
contract) so it actually exercises the new failure mode instead of the old
one.

(`readiness()`'s equivalent expansion — `strategy_layer.intervals[interval].weight_state_ready`
etc. — was checked too: currently nothing in the frontend reads
`runtimeReadiness.strategy_layer` or `.data_layer` per-interval fields at all
(`grep` across `web/src` outside test files turns up only the type
definition and the plumbing that stores the value, no rendering/gating
logic), so that half of #81 is inert on the frontend today and not a live
regression — flagging only in case a future feature starts reading it and
assumes non-emptiness means freshness the same way `weights()`'s field did.)

## Symptom B — "Multi-timeframe evidence" panel: completely empty, still unexplained

This is the real open question. Checked live, repeatedly, ~15 minutes apart,
for **both** BTC/USDT and XAU/USDT, Portfolio lane: the panel
(`signal.interval_status`) shows nothing at all —

> "No evidence bundle yet — Portfolio hasn't evaluated ... since the runtime
> last restarted."

— every time, not just once. Portfolio is supposed to emit a fresh decision
(and therefore a fresh `interval_status` snapshot) every time its primary
interval's candle closes (`kline.timeframe == self.interval`,
`trading_api.rs:1487` — every 5 minutes for BTC/XAU today). Seeing the exact
same "never evaluated since restart" message across multiple checks spanning
more than one 5-minute candle is the part worth treating as suspicious, not
just "still warming up."

### Ruled out (verified, not guessed)

- **Interval string mismatch between Go producer and Rust consumer** — checked
  byte-for-byte across both languages (Go's `intervalToString`,
  `internal/interfaces/worker/utils.go:33-56`, and Binance's own WS payload
  interval string at `binance_ws_service.go:251`, vs. Rust's
  `MarketSubscription.topic()`/`MarketEventV2`, `crates/finance-core/src/market_event.rs:164-274`,
  which explicitly **rejects** non-canonical casing rather than silently
  accepting a mismatch, per `rejects_non_canonical_asset_or_interval_casing`
  test at `market_event.rs:371-380`). All 8 intervals use identical lowercase
  literals on both sides. Not the cause.
- **`ingest()` silently dropping evidence** — read the full body
  (`crates/finance-core/src/trading_modes.rs:503-549`). It returns
  `Result<bool, MultiTimeframeEvidenceError>`, and **every error is logged**,
  not swallowed: both call sites (`trading_api.rs:1482` and `:1486`) do
  `if let Err(error) = ....ingest(item) { tracing::warn!(%error, "Discarding
  invalid ... portfolio evidence"); }`.
- **Config/feature-flag reducing the interval set** — `EVALUATED_INTERVALS`
  (`trading_api.rs:34-35`) is an unconditional `const`, used as-is to build
  Kafka subscriptions (`main.rs:605-624`) and Alpha contexts (`:695-706`). No
  override exists anywhere in the repo.

### Fast diagnostic to run first

1. **Check whether Portfolio is evaluating at all.** `readiness()`
   (`trading_api.rs:2722-2765`) exposes `strategy_layer.intervals[self.interval].update_count`,
   sourced from `inner.evaluation_count` (`trading_api.rs:1620`, incremented
   once per evaluation). This is already fetched by the frontend as
   `runtimeReadiness` (`web/src/types/index.ts`'s `RuntimeIntervalReadiness.update_count`).
   Check this value for BTC/XAU right now, and again a few minutes later:
   - **Not increasing** → Portfolio's evaluation loop itself isn't running
     (crash-loop, stuck task, or the process restarting on a tighter cycle
     than expected — check container restart counts/`FailingStreak`, not just
     "is the container up," per the observability lessons already captured in
     the repository-delivery skill: a hung/crash-looping worker still reports
     a healthy container).
   - **Increasing normally** → evaluation is happening but
     `portfolio_evidence`/`interval_status` isn't reflecting it — narrow
     further to `pending_portfolio_primaries` / `last_portfolio_primary_close_time`
     gating (`trading_api.rs:1488-1499`) possibly never flipping to "ready to
     emit," or a `signal_states` broadcast path issue between
     `inner.portfolio_evidence` and whatever ultimately serializes into
     `signal.interval_status` on the wire to finance-mw/web.
2. **grep runtime logs for `"Discarding invalid"`** (the `tracing::warn!`
   sites above) for BTC/XAU. Present → evidence is being built and rejected,
   read the specific `MultiTimeframeEvidenceError` variant it names. Absent →
   evidence for Portfolio's primary interval isn't even being attempted,
   which points at `alpha_position_evidence`/`strategy_interval_evidence`
   (`trading_api.rs:2091-2125`, `:2926+`) not producing items in the first
   place — worth checking whether `ledgers.get(&context.scope_id)`
   (`:2107`) is actually finding a match for Portfolio's own context, not just
   Alpha's.

## What "done" looks like

- Symptom A (reopened by #81): swap `StrategyLayerPage.tsx:51`'s
  `current_weights`-non-empty check for `last_updated_ts > 0`, update the
  `'shows only intervals backed by runtime data'` test's mock to give every
  interval a non-empty `current_weights` (matching #81's real shape) so it
  actually guards against the new failure mode, then reopen `/trading/strategy`
  for BTC/XAU and confirm only intervals with real kline history get a tab.
- Symptom B (still open, unaffected by #81): confirmed live: does
  `evaluation_count`/`update_count` for BTC/XAU's primary interval actually
  increase over time, or is it stuck? That single check determines whether
  this is "Portfolio genuinely isn't running" (ops/restart issue) vs.
  "Portfolio runs but evidence never reaches `interval_status`" (a real code
  bug in the evidence→signal wiring) — cite whichever it is with file:line
  before writing a fix.
- Manual verification once both are fixed: reopen `/trading/strategy` for
  BTC/USDT and XAU/USDT, Portfolio lane, and confirm "Multi-timeframe
  evidence" shows all 8 interval rows (role/weight/state) — not the current
  fully-empty state — and that the rows update across successive 5-minute
  primary-candle closes, while the "Active interval" tab strip above it still
  shows only intervals actually backed by data.
