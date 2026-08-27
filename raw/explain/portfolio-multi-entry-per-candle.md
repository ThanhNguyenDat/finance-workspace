# Portfolio shows multiple entries inside a single 12h candle (BTC, 2026-02-23)

Reported by user: on the Portfolio lane, one 12h candle for BTC around
2026-02-23 has several entries, not one. Investigated by reading the
decision/execution code in
`/home/lap17204/Desktop/finance/finance-live-action` and cross-checking
against real data on production (`https://finance.thanhne.io.vn`, read-only,
already-authenticated admin session — Trade Journal + Chart pages, Portfolio
lane, BTC/USDT). No code changed.

## Verified against production data

Trade Journal → Layer=Portfolio → BTC/USDT, filtered by Rule:

- `fixed-pct` and `compounding-10pct` both report **169 closed trades total**,
  with **identical dates, entry prices and exit prices** — only the PnL
  column differs (position-size scaling). This confirms
  `raw/portfolio-rule-trade-count-imbalance.md`'s note that all 3 rules
  "consume the same decision target": one shared decision engine drives every
  rule's ledger (`trading_api.rs:728-729`, `:1592`), sizing is the only thing
  that varies per rule.
- For **23/02/2026** specifically, both rules show **4 closed trades that
  day**, all `Buy`:
  - `65,702.84 → 66,346.59` (+0.88%, Win)
  - `64,728.34 → 65,362.55` (+0.88%, Win)
  - `67,452.99 → 67,102.30` (‑0.62%, Loss)
  - `67,587.81 → 67,236.43` (‑0.62%, Loss)
- The day before, **24/02/2026**, shows 7 `Buy` trades, 6 of them losses at
  the same ~‑0.62% level, one win — a same-direction re-entry/stop-out chain
  within one calendar day (well inside a single 12h window).

So the report is confirmed: this isn't a UI artifact, real Portfolio entries
do cluster multiple-per-day, and therefore multiple-per-12h-candle.

## Root cause: Portfolio's execution cadence is 5m, not 12h

12h is one of 8 *evidence* intervals the ensemble reads
(`EVALUATED_INTERVALS`, `trading_api.rs:34`), not the interval Portfolio
actually opens/closes positions on. The interval it executes on is whatever
`INTERVAL` the runtime process is configured with — and BTC never overrides
it:

- Default when unset: `"5m"` (`crates/finance-api/src/config.rs:74`).
- `docker/compose.large-cap.yaml`'s BTC service
  (`live-action-binance-perpetual-future-btc-usdt`) sets `BASE_ASSET`,
  `QUOTE_ASSET`, `INSTRUMENT_INIT_SIDE` but no `INTERVAL` — so it runs on the
  5m default.
- Confirmed live: the Chart page's scope badge for BTC/USDT · Portfolio ·
  Runtime reads **"5m"**.

A Portfolio decision only executes (can open/close a position) when the
incoming kline's timeframe matches that primary interval:

```rust
// trading_api.rs:1541-1549
if !portfolio_scope_ids.is_empty()
    && kline.timeframe == self.interval          // == "5m" for BTC
    && inner
        .last_portfolio_primary_close_time
        .is_none_or(|last_close| kline.close_time > last_close)
{
    ...
}
```

So Portfolio can re-evaluate and act up to every 5 minutes, gated only by
multi-timeframe synchronization
(`pending.evidence.is_synchronized(close_time)`, same block) and the holding
rules below — 12h is purely a slower confirming input into that same 5m
decision, never the trading clock itself. Any 12h candle can therefore
legitimately contain several entries by design, not by accident.

## Compounding factor: re-entry cooldown is asymmetric

`DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS = 12`
(`crates/finance-core/src/trading_modes.rs:82`) — at 5m cadence, 12 decisions
= 1 hour. But it is not a uniform cooldown; it only applies after a
**protective** stop/take exit:

```rust
// trading_modes.rs:230-238 — PortfolioConstructionState::observe_execution
pub fn observe_execution(&mut self, outcome: TargetExecutionOutcome) {
    if outcome == TargetExecutionOutcome::ProtectiveExit {
        ...
        self.decisions_since_target_change = 0;
        self.waiting_after_protective_exit = true;   // blocks instant re-entry
    }
}
```

```rust
// trading_modes.rs:200-207 — PortfolioConstructionState::construct
let next = if decision.exit {
    self.decisions_since_target_change = 0;
    self.waiting_after_protective_exit = false;      // NOT set on explicit exits
    PortfolioTarget::from_decision(decision, TargetPosition::Flat)
} else if ...
```

`starts_initial_position` (line 211-212) only requires
`current_target.position == Flat && !waiting_after_protective_exit` to bypass
the holding-period check entirely. So:

- Exit via protective stop/take → next same-direction entry is blocked for up
  to 1 hour (12 × 5m decisions).
- Exit via an explicit non-protective strategy signal → **zero cooldown**,
  the very next 5m decision can re-enter immediately.

Both paths still fit several times inside one 12h window — the ‑0.62% losses
recur at roughly the fractional protective stop (`stop: 0.005` in
`deployment_rules.rs`, minus fees/slippage ≈ ‑0.62%), consistent with the
24/02 and 23/02 loss legs above being genuine stop-outs, each eligible to
re-enter about an hour later once price kept meeting the entry condition.

## One more thing worth knowing before reading Feb 2026 as "history"

`compounding-10pct` and `risk-2pct` were only added to the codebase on
2026-08-09 (`raw/portfolio-rule-trade-count-imbalance.md`), yet the journal
shows them with trades dated back to Feb/Mar 2026. That's expected, not a
data bug: at every process startup, when `historical_replay_enabled` is set,
`bootstrap_historical_replay` (`crates/finance-api/src/historical_replay.rs`,
invoked from `main.rs:540-572`) replays up to `historical_replay_days`
(default 365) days of real historical klines through the **current** rule
configuration and commits the result straight into the same "Realtime"
ledgers the Trade Journal reads. So the 23/02/2026 entries reflect today's
strategy/rule parameters applied retroactively to that day's real BTC price
action — not a literal log of orders placed live on that date (no
`compounding-10pct` rule existed to place them). `fixed-pct` predates this
and may have some genuinely live-placed trades mixed into the same replayed
range; the journal doesn't currently distinguish "replayed" from "live" rows
at all — flagging as a separate, smaller gap, not the one asked about here.

## Follow-up: how does the UI show it if a candle has ~100 entries?

User follow-up question after the above: "so what if there are 100 entries?"
Checked the two places entries are actually rendered
(`/home/lap17204/Desktop/finance/finance-mw`, `web/src`):

**Chart page (`web/src/components/Klines.tsx`)** — trades become markers on
the candlestick series. Two limits interact:

1. `nearestCandleTime()` (`Klines.tsx:124-130`) snaps every trade's exact
   `entry_ts`/`exit_ts` down to the currently-displayed candle it falls
   inside. On a 12h chart, every entry inside that 12h window collapses onto
   the **same** marker `time` — there is no per-trade x-offset.
2. `markersRef.current?.setMarkers(markers)` uses `lightweight-charts`'
   `createSeriesMarkers` plugin (confirmed by reading the installed
   `node_modules/lightweight-charts@5.2.0` renderer,
   `fillSizeAndY()`/`SeriesMarkersRenderer`): markers sharing one bar index
   are not hidden or overwritten, they **stack** — each additional
   `belowBar`/`aboveBar` marker on the same bar is pushed further away by an
   accumulating per-bar offset (`offsets._internal_aboveBar` /
   `_internal_belowBar`, incremented by each marker's shape height +
   margin). So ~100 entries in one 12h candle renders as a tall vertical
   tower of ~100 stacked arrows growing away from that single bar (plus up
   to 100 more `inBar` exit circles at the close price) — not silently
   dropped, but not readable either, and it dwarfs every neighboring candle
   that only has 0-2 markers.
3. Total markers are capped globally at `MAX_TRADE_MARKERS = 240`
   (`Klines.tsx:105`), keeping only the most recent 240 by `entry_ts`
   (`Klines.tsx:822-823`, `.slice(-MAX_TRADE_MARKERS)`) — no on-chart
   indication when older trades get dropped from the marker set. 100 entries
   in a single candle alone would still fit under 240, but combined with
   markers elsewhere on the visible range it can silently start truncating
   the oldest ones with no "N markers hidden" affordance.

**Trade Journal table (`web/src/pages/trade/TradingJournalPages.tsx`)** —
unaffected by density: it's a real paginated list
(`DEFAULT_JOURNAL_PAGE_SIZE = 100`, selectable 50/100/250,
`TradingJournalPages.tsx:36-37,606`), so 100 entries just span one or two
pages. No overlap risk here.

**Calendar view (`web/src/pages/trade/TradeCalendarSection.tsx`)** — also
unaffected: a day cell shows an aggregated count badge (`{trades.length}t`,
`TradeCalendarSection.tsx:113`), not one mark per trade, so a 100-trade day
just reads "100t" on its tile.

So the only place this actually degrades is the **Chart's marker overlay**,
specifically at intervals coarser than the primary interval (12h/1d) when a
lot of entries land in one bucket — table and calendar both already handle
high density fine.

### Confirmed visually on production (not just theory)

Reproduced live: Chart page → BTC/USDT → Portfolio →
`compounding-10pct` → 12h interval, panned back to a cluster of trades around
early May 2026 with several `SHORT` legs close together in time. The result
is not a clean readable tower — the `aboveBar`/`belowBar` text labels
("SHORT entry" repeated) visually overlap each other diagonally, and the
`inBar` exit circles (yellow/red/blue dots for different PnL) bunch into an
unreadable smear on top of the candle:

```
SHORT entry
 SHORT entry
  SHORT SHORT entry
   SHORT entry
    SHORT Exit -6.00
     Exit -8.20
```

(approximated from a zoomed screenshot of the actual cluster — the real
rendering is angled/overlapping text, not neatly stacked lines). So yes:
this does look broken/annoying at that density, confirmed, not just a
theoretical risk from reading the renderer code. It doesn't crash or corrupt
the chart's CSS/layout — the candles and axes stay intact — but the marker
cluster itself is genuinely hard to read once several entries land within
one visible bar.

**Fixed** (frontend only, applied on explicit request — normally this file
stays investigation-only, see the workflow note at the top of this repo's
`.agents/rules/coding-and-verification.md`): `web/src/components/Klines.tsx`,
the trade-marker effect (`~line 793`) now groups `scopedTrades` by
`(nearestCandleTime, side)` for entries and by `nearestCandleTime` for exits
before building markers, instead of pushing one marker per trade. A bar with
N same-side entries now renders a single marker reading `N× LONG entry` (or
the plain `LONG entry` text when N=1, unchanged); exits on one bar collapse
into `N× exit ${netPnl}` showing the bar's net PnL rather than N overlapping
`Exit …` circles. `MAX_TRADE_MARKERS` truncation and the underlying 5m
decision cadence are untouched — this only fixes how already-generated
markers render when several share a bar, not how many trades exist.

Verified: `npm test -- --run` (302/302 passing, including a new regression
test asserting two same-bar trades collapse into one `2× LONG entry` /
`2× exit` marker instead of two), `npx tsc --noEmit`, `npm run lint`, and
`npm run build` all clean. Re-checked live against `finance-mw`'s dev server
(`VITE_API_PROXY_TARGET` defaults to the production API, read-only, no
deploy involved) on the same BTC/Portfolio/`compounding-10pct`/12h cluster
used for the earlier screenshot: the previously illegible overlapping-text
blob now renders as distinct, readable `2× SHORT entry` / `2× exit +8.xx`
lines. Not pushed/deployed — local-only per instruction.

## Assessment

The "multiple entries in one 12h candle" behavior itself is **by design**,
not a bug: Portfolio trades on its fast primary interval (5m for BTC) and
only *reads* 12h as one of several confirming timeframes. Expecting at most
one entry per 12h candle would only hold if Portfolio's execution interval
were 12h, which it isn't for any currently-running instrument.

What *is* a real, arguably-unintended gap, illustrated concretely by the
24/02/2026 chain (6 losing same-direction re-entries in one day): there is no
losing-streak / whipsaw circuit breaker, and the re-entry cooldown only
applies after a protective exit, not after an explicit strategy exit. This
means a choppy, mean-reverting stretch can produce a rapid string of
same-direction stop-outs with only the code path above limiting cadence.

**Fix direction** (not applied — investigation only): if the goal is to
reduce entries-per-window, the lever is `minimum_holding_decisions` /
`waiting_after_protective_exit`, not the 12h interval itself — e.g. extend
the cooldown to explicit exits too, or add a consecutive-loss counter that
raises the required holding period after N losing legs in the same
direction. Whether that's wanted is a strategy-design call, not something to
infer from this one report alone.

## What "done" looks like

- Confirm with the user whether the concern is "this is unexpected" (answer:
  it's by design, documented above) or "this is too much churn" (a real
  tuning question — decide on a re-entry cooldown/circuit-breaker change and
  where it should live).
- If a cooldown change is wanted: extend it to explicit-exit re-entries,
  verify against the same BTC Feb 2026 window that clustered same-direction
  losing entries drop, and add a regression test asserting
  `PortfolioConstructionState::construct` no longer allows an immediate
  same-direction re-entry after a non-protective exit within the holding
  period.
