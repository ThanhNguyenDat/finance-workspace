# Round 434 — NEEDS-MORE-RESEARCH: cross-instrument lead-lag design survey confirms the blocker is engine-wide (subscription + ledger + live path), not just the `Strategy::evaluate` signature — and sketches a backtest-only path that avoids it

Classification: **NEEDS-MORE-RESEARCH**. Zero containers, zero backtest
compute — this round is a targeted design survey, the exact next step
round432 named and left undone: "Chưa có round nào làm việc này; đây là
hướng mở duy nhất còn lại từ đề xuất 2026-09-04" for cross-instrument
lead-lag. This round reads code only (`finance-live-action`), on both the
replay and live paths, to determine precisely how large the architecture
change would need to be before any backtest of this idea can be trusted —
and to check whether a smaller, backtest-only prototype could get an honest
first read on the underlying edge before committing to that larger change.

## What round432 already established

`crates/finance-strategy/src/engine.rs:30` — `Strategy::evaluate(&self,
kline: &Kline)` accepts exactly one `Kline` of one instrument. Round432
flagged this as the blocker and stopped there, deferring the "how much
would actually need to change" question to a dedicated round.

## What this round adds: the blocker is not the trait signature alone

Read `crates/finance-core/src/kline.rs`, `crates/finance-api/src/
historical_replay.rs`, and `crates/finance-strategy/src/engine.rs`
end to end. Three independent points in the pipeline assume exactly one
instrument, not just the trait method:

1. **`Kline` itself carries no second-instrument field**
   (`crates/finance-core/src/kline.rs:9-23`) — `instrument`, `timeframe`,
   OHLCV only. There is no side-channel on the type a lead-lag strategy
   could read a second series from without a schema change that touches
   every consumer of `Kline` (ledger, serialization, gRPC proto mapping),
   not just strategies.

2. **The replay bootstrap is scoped to one `MarketSubscription` end to
   end.** `historical_strategy_engine(subscription: &MarketSubscription)`
   (`historical_replay.rs:169`) builds the `StrategyEngine` from
   `configured_alpha_strategies(subscription)` — one instrument in, one
   engine out. `bootstrap_pending_intervals` merges only
   `pending_intervals: Vec<String>` — interval labels — of that single
   subscription's own instrument (`historical_replay.rs:165-260`); every
   `ReplayStream` it opens is constructed with `&subscription.instrument()`
   (`historical_replay.rs:210-218`), and critically **`alpha_ledgers` is a
   `BTreeMap<String, _>` keyed by `kline.timeframe` alone**
   (`historical_replay.rs:264-269`, consumed at `historical_replay.rs:305`
   `alpha_ledgers.get_mut(&kline.timeframe)`). Two instruments sharing an
   interval string (e.g. both have a `5m`) would collide on that map today;
   making the merge genuinely multi-instrument means re-keying every
   ledger/count/no-lookahead structure in this function by
   `(instrument, interval)`, not only adding a second stream to the merge
   loop. The `ReplayStream` struct does already carry its own `instrument:
   InstrumentIdentity` field per stream (`historical_replay.rs:396-400`),
   so the *merge* mechanics (chronological, `close_time`-ordered, tie-break
   already implemented) are close to instrument-agnostic already — it is
   everything downstream of the merge (ledger keys, portfolio driver,
   commit logic) that assumes one instrument.

3. **The live path shares the same constraint, independently.**
   `StrategyEngine::evaluate_all` / `evaluate_all_quiet`
   (`crates/finance-strategy/src/engine.rs:303-311`) take one `&Kline`, and
   `StrategyEngine::with_configured_strategies` is built once per
   subscription the same way the replay path builds it. This is not a
   replay-bootstrap-only quirk that a smarter merge could route around; the
   one-`Kline`-in constraint is the engine's contract on both the
   historical and the live code path, so any production-deployable fix
   changes shared code, not one caller.

Net effect: this is engine architecture work spanning `finance-core`
(schema), `finance-api` (subscription/replay scoping, ledger keying), and
`finance-strategy` (the trait itself) — consistent with round432's estimate
that this is "việc lớn hơn hẳn" the k-bar reversal item, but now with the
specific blast radius identified instead of just the trait line.

## What already exists that a smaller, backtest-only prototype could reuse

`crates/finance-research/src/main.rs:29-46` (`merge_multi_timeframe_klines`)
already does a chronological, `close_time`-ordered, no-lookahead-correct
merge of two *interval* series of the **same** instrument, with the same
tie-break rule as production's `replay_order`. The research CLI already
loads klines for an arbitrary `InstrumentIdentity` via `klines::load_at`
(`main.rs:127-150`), and `strategies.rs` already hosts research-only
`Strategy` implementations that never touch production
(`KBarReturnReversalStrategy`, round433, is the most recent precedent).

That suggests a **feasibility-only** path that does not require the
engine-wide change above: a new research-only binary/mode that (a) loads
both instruments' `5m` klines over the same window via the existing
`klines::load_at`, (b) aligns them on an as-of basis (secondary instrument's
last-closed bar strictly before the primary bar's `close_time` — never the
concurrent or later bar, to stay no-lookahead-safe), (c) computes a
precomputed lagged-return feature from the secondary series, and (d) feeds
primary-instrument signals generated from that feature through the
*existing* cost/execution/split machinery
(`execution_rules.rs`/`portfolio_measurement.rs`/`split.rs`) that every
other research strategy already uses for realistic PnL and train/validation/
holdout separation — without going anywhere near `Strategy::evaluate`,
`Kline`, or the subscription/ledger code above. This would answer "does the
underlying lead-lag edge exist at all" cheaply, *before* anyone commits to
the engine-wide change, which is the right order (cheap edge check first,
expensive plumbing only if the edge check clears).

## Why this round stops at the design, not the prototype

The alignment step in (b) above is exactly the kind of code this program has
repeatedly found subtle lookahead bugs in when built quickly (round337's
continuity-vs-venue confusion, the MTF merge `open_time`-vs-`close_time` bug
that invalidated seven live strategies for months before commit `3c16745`,
round348's discovery that cost flags silently gate reversal decisions). BTC
trades 24/7 while XAU/FX sessions gap on weekends and holidays, so the
as-of join has real edge cases (stale secondary bar spanning a weekend,
DST-driven session-close skew) that deserve a dedicated round to design,
implement, and unit-test in isolation — not to be improvised inside the same
round as this survey, and not defensible to backtest and report a number
from in the time remaining here. Writing that alignment code carelessly to
produce a number this round would repeat exactly the class of mistake this
corpus exists to avoid.

## Conclusion

Cross-instrument lead-lag remains the one genuinely open, not-yet-tested
direction in the corpus (per round432). This round narrows it from "needs a
design round" to a concrete, scoped next step: build the backtest-only,
as-of-aligned prototype in `finance-research` (not `finance-live-action`
production code) as a dedicated round, get one honest train/validation/
holdout read on whether BTC-leads-XAU (or the reverse) has any edge at all,
and only pursue the engine-wide production change (item 1-3 above) if that
prototype clears. No promotion, no implementation, no production change,
no backtest compute spent this round.

## Named next step

A dedicated round: implement the as-of-aligned lagged-return feature +
research-only `Strategy` (or bespoke signal function reusing
`execution_rules`/`portfolio_measurement`/`split`) for BTC/binance leading
XAU/exness (and the reverse direction) at `5m`, with explicit handling for
secondary-series session gaps, and report train/validation/holdout PF/
Sharpe/Sortino honestly before any decision to invest in the engine-wide
change described above.
