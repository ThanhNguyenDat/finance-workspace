# System-wide review: how to actually use the data already being generated

Full-system review requested by user (2026-08-13), framed around the
project's real target: find/validate which Alpha strategy×interval and which
Portfolio sizing rule performs best, eventually run live with real capital,
safely bounded by risk. Investigation only — nothing in this doc has been
applied to code. Spans `finance-live-action` (core) and `finance-mw`
(dashboard).

**Headline finding**: the pieces needed for real, performance-driven
decision-making already exist in the codebase — a real weighted-decision
engine, a real strategy-scoring pipeline, even a CI gate that evaluates
profitability — but none of them are connected to the live decision loop,
which still runs on hand-picked constants. This is the single highest-value
thing to fix relative to the stated goal.

---

## Priority 1 (highest impact): the live decision engine never consults real performance

### What's live today

`MultiTimeframePortfolioPolicy::survival_first_default`
(`crates/finance-core/src/trading_modes.rs:408-441`) is what actually builds
the policy used in production (constructed once at
`crates/finance-api/src/trading_api.rs:779-780`, feeding the shared
`MultiTimeframeEvidenceBook` every Portfolio rule reads,
`trading_api.rs:962-965`). It hardcodes:

```rust
// trading_modes.rs:425-434
BTreeMap::from([
    ("5m".to_string(), 0.08), ("15m".to_string(), 0.12), ("30m".to_string(), 0.10),
    ("1h".to_string(), 0.15), ("2h".to_string(), 0.15), ("4h".to_string(), 0.18),
    ("12h".to_string(), 0.12), ("1d".to_string(), 0.10),
]),
```

and splits strategy weight equally (`strategy_weight = 1.0 /
strategy_names.len()`, `:409-413`). This is the same static-placeholder
pattern already documented for the `weights()` *display* endpoint in
`raw/multi-timeframe-interval-gap.md` — except this is the real decision
math, not just a UI-facing readout. **Nothing downstream of Alpha's raw
per-candle signal is ever scored by realized PnL, win rate, or drawdown.**
Every interval and strategy is worth exactly what its hardcoded constant
says, forever, regardless of how it actually performs.

### The pieces to wire together already exist

**A real weighted-decision engine, unused in production.**
`PortfolioDecisionPolicy` (`trading_modes.rs:253-343`, verified directly)
already takes an arbitrary `strategy_weights: BTreeMap<String, f64>` and
computes a proper weighted score against a threshold
(`minimum_weighted_score`) to decide long/short/hold
(`decide()`, `:267-336`). It's referenced nowhere in `finance-api` — only in
`crates/finance-core/tests/trading_modes.rs`. This is the exact shape a
performance-derived weight map would plug into.

**A real strategy-scoring pipeline, disconnected from the live path.**
`crates/finance-research/src/sweep.rs` (verified directly, lines 1-45+)
computes exactly the metrics needed:

```rust
pub struct SplitScore {
    pub split: String, pub trades: u64, pub realized_pnl: f64,
    pub win_rate: Option<f64>, pub profit_factor: Option<f64>,
    pub max_drawdown: f64, pub funding_paid: f64,
}
pub struct StrategyScore {
    pub strategy: String, pub interval: String, pub splits: Vec<SplitScore>,
}
```

with `survives_selection()` requiring the strategy to be profitable on
**both** train and validation splits before holdout is even consulted
(`:41-45`, holdout deliberately withheld from selection to avoid
overfitting to it — good practice, already in place). But
`finance-research` is a standalone offline binary
(`crates/finance-research/src/main.rs`) with no code dependency back into
`finance-api`/`finance-core`. It only runs via manual
`workflow_dispatch` (`.github/workflows/portfolio-research.yaml`,
`universe-research.yaml` — **no `schedule:` trigger on either**), and its
output is uploaded only as a CI artifact JSON. Nothing reads it back into
`weights()` or `MultiTimeframePortfolioPolicy`.

**CI already certifies the live config as unprofitable — and nothing acts on it.**
Verified directly: `portfolio-research.yaml:159` has a step literally named
*"Assert the current losing system is rejected with complete metrics"*,
asserting `.passed == false` / `.portfolio.passed == false` (`:167,180`)
against a gate built from the actual deployed checkpoint config, evaluated
over a 90-day holdout. This is treated as the *expected, passing* CI
outcome — a regression test that the gate correctly flags today's live
config as a loser, not a trigger that changes anything. So by the project's
own automated criteria, the currently-live strategy/interval/sizing
selection is not validated as profitable, and it keeps running unchanged
because nothing consumes that verdict.

### Fix direction (not applied — investigation only)

Wire `sweep`'s per-(strategy, interval) `SplitScore` — or an equivalent
computed live from each Alpha ledger's own `SimulatedPerformance` — into a
periodically-recomputed `BTreeMap<String, f64>` fed to either
`PortfolioDecisionPolicy` (already shaped for this) or
`MultiTimeframePortfolioPolicy`'s `interval_weights`/`strategy_weights`,
replacing the hardcoded constants in `survival_first_default`. Separately,
consider adding a `schedule:` trigger to the research workflows so scoring
isn't purely manual. Exact mechanism (batch recompute vs. rolling online
update, how often, what happens when a rule fails `survives_selection()`
mid-flight) is a design call for whoever picks this up.

---

## Priority 2 (confirmed bug, already documented separately)

`risk-2pct` Portfolio rule is structurally blocked by an unscaled risk gate
— full writeup already in `raw/portfolio-rule-trade-count-imbalance.md`.
Not repeated here; still open.

---

## Priority 3: Multi-timeframe evidence panel empty (Symptom B) — new leads

Previously undiagnosed in `raw/multi-timeframe-interval-gap.md`. This pass
found the actual pipeline and two concrete suspects, verified directly:

**The pipeline is real, not a frontend-only concept.**
`MultiTimeframeEvidenceBook` (`trading_modes.rs:488-757`) is fully
implemented — `ingest()`, `interval_state()`, `interval_status()`,
`decide()` — and wired into the live path (`trading_api.rs:1524-1539` on
each closed kline, `:1669` writing `interval_status` into `signal_states` on
every evaluation). So an empty panel means the pipeline isn't *reaching*
execution for BTC/XAU, not that it doesn't exist.

**Suspect A — 200-vs-1 kline warmup asymmetry gates the write.** Verified
directly:

```rust
// trading_api.rs:1422-1431
fn history_requirement(&self, interval: &str) -> usize {
    if interval == self.interval {
        self.required_history_klines   // 200 for the primary interval
    } else {
        1                               // every other interval
    }
}
```

The write that populates `signal_states` (`record_evaluation_with_no_lookahead`,
`:1669-1692`) only runs once `HistoryGateState::is_ready()` is true
(gated at `main.rs:784`). If evaluation is persistently not reaching
`Ready`, the whole panel stays empty. Worth checking directly: is
`inner.evaluation_count` (the field `readiness()` also reads, `:2822`)
actually incrementing live for BTC/USDT and XAU/USDT, or stuck at 0.

**Suspect B — gap recovery resets global state on any single interval's blip.**
`trading_api.rs:1349-1359`: a missed candle on *any* one of the 8 intervals
clears that interval's evidence **and** resets `inner.evaluation_count = 0`
globally. A transient gap on an unrelated interval (e.g. 12h) can make the
whole evaluation loop look permanently stuck to any diagnostic that reads
`evaluation_count`.

**`readiness()` is fully decorative — confirmed directly, do not trust it
as a diagnostic.** Read in full (`trading_api.rs:2786-2848`):
`weight_state_ready` is the constant `!self.strategy_names.is_empty()` —
identical for all 8 intervals, never varies with real per-interval state
(`:2821`). `signal_ready` is one instrument-wide bool duplicated into every
interval's row (`:2788`, `:2826`). Neither reflects `HistoryGateState`
(Suspect A) or `IntervalEvidenceState` (the real evidence states). Grep
confirms nothing in `web/src` outside test files reads
`runtimeReadiness.strategy_layer`/`.data_layer` per-interval fields — this
signal is dead on both the producing and consuming end. The gate that
actually matters for `weighted_ensemble` is a **separate, unrelated**
mechanism: `synchronization_failure()` (`trading_modes.rs:617-663`), which
requires every required interval's `IntervalEvidenceState` to be `Fresh`.
Two same-named "readiness" concepts exist in this codebase; don't conflate
them when debugging.

**Fix direction (not applied)**: instrument `main.rs:784`'s `is_ready()`
branch and the gap-recovery reset path with per-interval logging/metrics to
confirm which suspect is live; consider scoping the gap-recovery reset
(Suspect B) to only the affected interval instead of the whole evaluation
counter.

---

## Priority 4: dashboard doesn't let the user compare — the actual point of the data

The project's goal is comparing strategies/rules against each other, but the
UI only ever shows one scope's ledger at a time:

- `tradingScope.ts`'s `laneVariants`/`laneVariantAxes` already compute every
  Alpha strategy×interval and every Portfolio rule as discrete identities,
  but every consumer (`TradingScopeSwitcher.tsx`, `LedgerScopeFilter.tsx`)
  is single-select. There is no table/chart that fetches multiple scopes at
  once and ranks them side by side.
- `tradeMetrics.ts`'s `summarizeTrades` computes `avgWin`, `avgLoss`,
  `bestTrade`, `worstTrade` (plus others) that `StrategyLayerPage.tsx` never
  renders in either the stats row (`:122-151`) or the leaderboard chips
  (`:184-198`) — cheap win, since these are exactly the numbers that
  distinguish strategies.
- The Go backend already computes `win_rate`/`profit_factor`/`gross_profit`/
  `gross_loss` server-side per scope (`trading_controller.go:172-188`,
  mirrored in `types/index.ts:218-233`, validated in
  `tradingMetricsSnapshot.ts:99-113`) — but only `max_drawdown` is ever read
  anywhere in `web/src` outside tests. A comparison table could pull these
  directly instead of re-deriving from raw trade lists client-side.
- PnL/win-rate/profit-factor logic is independently reimplemented in three
  places (`tradeMetrics.ts`, `TradingJournalPages.tsx`'s `summarize`,
  `tradePerformance.ts`) with no shared source of truth. Notably
  `TradingJournalPages.tsx` computes **expectancy** and **win/loss
  streaks** — valuable for ranking — that the strategy-comparison-facing
  `tradeMetrics.ts` lacks.

**Fix direction (not applied)**: a "Compare" view driven by
`laneVariants`/`laneVariantAxes` that fetches metrics for every variant in
one lane and renders them as a ranked table (win rate, profit factor,
expectancy, max drawdown, trade count), pulling from the backend's
already-computed `TradingPerformanceMetrics` rather than re-deriving
client-side. This is the dashboard-side counterpart to Priority 1 — once
the engine picks winners automatically, the UI should let the user see why.

---

## Priority 5 (deprioritized): alternative data sources

User asked separately about adding TVL or historical news to improve
win-rate. Noted here for completeness, explicitly lower priority than
Priorities 1-4 above since it requires a new ingestion pipeline, not a
config/wiring change:

- **TVL doesn't apply** — it's a DeFi protocol metric; neither live
  instrument (BTC/USDT, XAU/USDT) is a DeFi token with a TVL figure to
  track.
- **News/macro sentiment is plausible** (Fed/CPI/geopolitical for XAU,
  regulatory/on-chain events for BTC), but the hard part is sourcing
  genuinely **point-in-time** historical data — anything backfilled after
  the fact reintroduces lookahead bias, which this codebase is otherwise
  careful about (`no-lookahead` guarantees already enforced in historical
  replay).
- User has flagged a **free-only budget constraint** for this. Of the
  sources considered, **GDELT** (gdeltproject.org) is free and publishes
  with real point-in-time timestamps, making it the only one of the
  options considered that's both free and backtest-safe out of the box.
  Paid options (Alpha Vantage News Sentiment, Finnhub) were considered but
  are not a fit given the budget constraint. This would still need its own
  ingestion + alignment pipeline against the existing kline timeline — a
  separate, larger design task, not scoped further here.
- **Any external API call needs a local cache, not a call-per-request
  pattern** — user's explicit requirement. Free-tier sources like GDELT
  have their own rate limits, and repeatedly re-fetching the same
  historical window (e.g. every backtest re-run over the same date range)
  would hammer someone else's infrastructure for no new information. Fetch
  once per (source, time window), persist locally in a **DB table** keyed
  by date/instrument (user's explicit preference — not a flat file), and
  have both live ingestion and historical backtests read from that local
  store first — only reach out externally for genuinely new data. This
  applies to live polling too: poll on a fixed schedule and cache the
  result rather than fetching on every evaluation tick.

---

## What "done" looks like, per priority

- **P1**: a periodically-recomputed performance-derived weight map feeds
  `PortfolioDecisionPolicy` or `MultiTimeframePortfolioPolicy`, replacing
  the hardcoded constants; research workflows run on a schedule, not only
  on manual dispatch.
- **P2**: see `raw/portfolio-rule-trade-count-imbalance.md`.
- **P3**: confirm via `evaluation_count` instrumentation whether Suspect A
  (warmup gate) or Suspect B (gap-recovery reset) is actually blocking
  BTC/XAU; fix whichever is confirmed.
- **P4**: a cross-scope comparison view exists in the dashboard, backed by
  the backend's existing per-scope metrics rather than client-recomputed
  ones.
- **P5**: not scoped for implementation yet — revisit only after P1-P4.
