# Round 442 — NEEDS-MORE-RESEARCH: web search surfaces two genuinely new mechanisms (statistical-arbitrage spread trading, Hurst-exponent regime filter) — design survey confirms both are HIGH-buildability reusing round437/round130 infra, neither implemented/backtested this round

Classification: **NEEDS-MORE-RESEARCH**. Zero containers, zero backtest
compute, zero code changes to `finance-live-action`. This round follows the
current `/quant-research` command's mandate: when the internal backlog
(`index.md` mục 3's ~90 closed candidates plus mục 0.5's 4 post-round432
directions, all confirmed closed as of round441) has no open lead, a web
search for a genuinely new, literature-backed mechanism is required before
concluding NO-CHANGE again. Round440/441 did not do this search step; this
round does it and finds two candidates specific and different enough from
everything already closed to be worth recording.

## Continuation context

Iteration in `quant-research-state state` read 241 at round start
(coordinator per-session attempt counter — the launcher's own bookkeeping,
distinct from the round-file sequence per the playbook's documented
divergence, e.g. round413/424-426/440/441). `git status --short` was clean
in `finance-workspace` at HEAD matching the round441 commit
(`f7f9715`); `finance-live-action` was clean at `5bd2634` (round439's CLI
commit — round440/441 touched no code). No recovery work needed this round.

## Why NO-CHANGE was not repeated a third time

Round432's audit and round433/436/437/439's closure of all four
post-round432 directions is real and still holds — nothing in `index.md`
reopened. But the current command text (see command source, "Nếu backlog nội
bộ... không còn hướng nào mở, trước khi kết luận NO-CHANGE, dùng web search
tìm cơ chế Alpha hoặc Portfolio-construction mới") requires a web-search
attempt before a repeat NO-CHANGE, and neither round440 (DATA-ISSUE, spent on
recovering an uncommitted skill file) nor round441 (NO-CHANGE, explicitly
re-audited only `index.md`) actually ran that search. This round runs it.

## Web search: two candidates found

Two queries, both returning concrete, well-established quant mechanisms not
present anywhere in `index.md` mục 3's closed-candidate table or mục 0.5's
four post-432 directions:

1. **Statistical arbitrage / pairs trading on a mean-reverting spread**
   between two cointegrated instruments (Engle-Granger / Johansen framing;
   sources: QuantInsti EPAT pairs-trading writeup, Analytics Vidhya "Stat Arb
   with Pairs Trading and Backtesting", `arxiv.org/pdf/2309.16008` "Optimal
   Entry and Exit with Signature in Statistical Arbitrage",
   `arxiv.org/pdf/1701.05016` "Mean-Reverting Portfolio Design with Budget
   Constraint"). Core idea: construct a spread from two co-moving
   instruments, trade its deviation from equilibrium expecting reversion —
   long the underperformer / short the outperformer when the spread
   deviates, close on reversion to the mean.
2. **Hurst-exponent regime detection** for gating trend-following vs.
   mean-reversion signals (sources: Macrosynergy "Detecting trends and mean
   reversion with the Hurst exponent", quantneuraledge "Hurst Exponent
   Trading Indicator: Identify Trending vs Ranging Markets"). Core idea: a
   rolling rescaled-range (R/S) estimator on log returns; H > 0.5 signals a
   trending/persistent regime, H < 0.5 signals mean-reverting/anti-persistent
   — commonly used at H > 0.55 / H < 0.45 thresholds to gate which family of
   strategy is allowed to fire.

## Why each is different from everything closed in `index.md`

**Statistical-arbitrage spread trading vs. round436's "cross-route
correlation-aware allocation" (closed, REJECTED):** round436 never traded a
spread — it scaled the *combined exposure* of `exness XAU` + `bybit XAUT`
down by a fixed factor on days their rolling PnL correlation was high, using
each route's own already-existing decision stream. It is a Portfolio-layer
exposure overlay, not an Alpha-layer entry mechanism, and it never bets on
convergence between the two routes' *prices*. Stat-arb spread trading is the
opposite structure: a new Alpha-layer `Strategy` that reads both instruments'
prices, constructs `spread = log(price_leader) - log(price_follower)` (or a
regression-hedged variant), and enters/exits based on the spread's own
z-score — a directional bet the two prices will re-converge, not an exposure
throttle on independently-generated signals. It is also different from
round433's `KBarReturnReversalStrategy` (single-instrument, own-return
reversal) and round437's `CrossInstrumentLeadLagStrategy` (single-instrument
follower entries driven by a *return* feature from the leader, not a
convergence bet on the *price relationship* between the two).

**Hurst-exponent regime filter vs. existing "regime" usage in `index.md`:**
grepping `index.md` for "regime" turns up ~15 hits (rounds 130, 228,
245, 383-388 and others) but every one uses "regime" as a *descriptive*
label for an observed pattern (e.g. "this looks like a regime effect, not an
edge") — none of them build or test an actual regime-*detection* technique
as a tradeable filter. The one concrete precedent,
`RealizedVolatilityRegimeFilterStrategy` (round130,
`crates/finance-research/src/strategies.rs:3660-3897`), gates an inner
strategy's signal on a short/long **ATR-ratio expansion** regime — a
volatility-level regime, not a trend-vs-mean-reversion regime. The Hurst
exponent measures something structurally different (serial-correlation
persistence of returns via a rescaled-range statistic across a rolling
window, not the magnitude of price movement), and it has never been computed
or tested anywhere in this program. It is also distinct from every trend
filter already closed (`MultiTimeframeTrendFilterStrategy`,
`SmaTrendFilterStrategy` — both closed round94, SMA/ADX-style directional
filters, not persistence-of-returns filters).

## Design survey: buildability

Read `crates/finance-research/src/{main.rs,strategies.rs,klines.rs}` in
`finance-live-action` (commit `5bd2634`, clean working tree) to check what
already exists for each mechanism, following round434/435's precedent of
determining exact buildability from code before committing container budget.

### Statistical-arbitrage spread — HIGH buildability, reuses round437 infra directly

Unlike round434's original survey of cross-instrument lead-lag (which found
the *engine* had no two-instrument path at all), the infra a spread strategy
needs was built for and by round437's `CrossInstrumentLeadLagStrategy` and
is already generic, not lead-lag-specific:

- CLI already accepts an arbitrary second instrument: `--leader-broker`/
  `--leader-market-type`/`--leader-base-asset`/`--leader-quote-asset`
  (`main.rs:335` and surrounding `Args` fields), all four required together
  by `clap`.
- `main.rs:450-462` constructs the `leader_instrument` `InstrumentIdentity`
  from those flags and rejects `leader.key() == instrument.key()`
  (`main.rs:466-469`).
- `main.rs:470-484` loads the leader's own candle series via the same
  `klines::load_at` (`klines.rs:220`) already used for the primary
  instrument — no new loading code needed.
- `main.rs:502-509` merges the two series chronologically by `close_time`
  (reusing `merge_multi_timeframe_klines`, `main.rs:45-59`, the same
  no-lookahead ordering `finance-api::historical_replay::replay_order` uses
  in production) and runs `split::split_chronologically` on the merged
  stream — train/validation/holdout for a two-instrument backtest already
  works mechanically.
- The only genuinely new code needed is (a) a new `Strategy` struct
  (`SpreadReversionStrategy` or similar) mirroring
  `CrossInstrumentLeadLagStrategy`'s shape (`strategies.rs:310-420`): same
  `Mutex<VecDeque<f64>>` rolling-window pattern, same strict-before
  `last_leader_feature: Mutex<Option<(DateTime<Utc>, f64)>>` no-lookahead
  guard (`strategies.rs:388-399`) so a follower bar only ever reads a
  leader feature whose `close_time` is strictly earlier than its own — but
  computing a rolling spread z-score (rolling mean/std of `log(leader_close)
  - log(follower_close)` over a window) instead of a k-bar cumulative
  return, and (b) a sibling candidate-list function + ~50-line main.rs wiring
  block mirroring `cross_instrument_leadlag_candidates`
  (`strategies.rs:441-465`) and its call site (`main.rs:891-895,937-939`).
  Given `exness XAU` and `bybit XAUT` are literally the same underlying
  asset (gold) on two venues with independently-confirmed +0.996 raw-price
  correlation (round342, re-confirmed round436), a hedge ratio near 1.0 is a
  reasonable starting assumption to validate empirically before trusting a
  regression-estimated beta — cheaper first cut than building a rolling
  OLS/Kalman hedge-ratio estimator this program has no precedent for.
- Evaluation path: same as round437 — `--daily-profit-gate` only evaluates
  the deployed *Portfolio* decision policy (`main.rs:255-263`, `--gate-strategy`
  removed round55), so an arbitrary new Alpha candidate can only be scored
  on PF/win-rate via the plain sweep, not Sharpe/Sortino/streak. Report that
  honestly, same as round437 did, not invent an extended-metrics number.

### Hurst-exponent regime filter — HIGH buildability, reuses round130 infra directly

`RealizedVolatilityRegimeFilterStrategy` (`strategies.rs:3660-3897`) is a
structurally exact precedent: a wrapper `Strategy` holding
`inner: Box<dyn Strategy>` plus rolling `Mutex<VecDeque<f64>>` state for
highs/lows/closes (`strategies.rs:3660-3688`), computing a regime statistic
on every `evaluate()` call from a capped rolling window
(`capacity = self.long_period * 2 + 10`, `strategies.rs:3715-3747`) using
only that instrument's own already-closed bars — then gating (or not) the
inner strategy's emitted signal on the computed regime value
(`strategies.rs:3749` onward). A `HurstRegimeFilterStrategy` needs the same
wrapper shape, the same rolling `VecDeque<f64>` of closes, and a **new**
statistic function — a rescaled-range (R/S) Hurst-exponent estimator over
log returns in the rolling window — in place of the ATR-ratio calculation.
No engine change, no new CLI flags beyond an inner-strategy selector +
threshold values (mirroring `--higher-timeframe-interval`'s existing pattern
for opting into a wrapped/filtered candidate set). Fully single-instrument
and fully causal (the window is always strictly historical relative to the
bar being evaluated, same as every other rolling-window strategy in this
file) — no lookahead-design risk of the kind that blocked round434/435 from
implementing in-round.

## Why this round stops at the design, not the implementation

Per the current command text: "Chỉ kết luận NO-CHANGE khi web search cũng
không tìm được cơ chế nào đủ cụ thể và khác biệt... không implement ngay
trong cùng round tìm ra ý tưởng trừ khi đã đủ ngân sách backtest của round
(ưu tiên ghi ý tưởng lại cho round sau nếu không chắc)." Both mechanisms
above are HIGH-buildability by code-reading standards, but neither has had a
single line of Rust written or a unit test run yet — writing a new
`Strategy` implementation, wiring it into the CLI, and getting a trustworthy
first backtest number all in the remainder of this round would repeat the
exact rushed-implementation failure mode round434/435 were written to avoid
(the MTF `open_time`-vs-`close_time` lookahead bug fixed at `3c16745`,
round84's silent gate under-widening). Recording the idea now, precisely
scoped, and implementing it as a dedicated round next is the safer default
the command text explicitly prefers when not certain the round's remaining
budget covers a full implement+test+backtest cycle.

## Conclusion

The internal backlog (`index.md` mục 3 and mục 0.5) remains fully closed —
that conclusion is unchanged and does not need re-litigating every round.
What changes this round: two new, specific, literature-backed mechanisms are
now recorded as open leads (index.md mục 0.5 items 5 and 6, appended below),
each with a concrete, code-verified buildability assessment and named next
step. No promotion, no implementation, no production change, zero backtest
compute spent.

## Named next steps (either may be picked up independently next round)

1. **Statistical-arbitrage spread** (`exness XAU` / `bybit XAUT`): implement
   `SpreadReversionStrategy` (rolling log-price-ratio spread + z-score entry/
   exit, strict-before no-lookahead guard mirroring
   `CrossInstrumentLeadLagStrategy`), a sibling `candidates()` function, and
   the ~50-line main.rs wiring block; unit test the no-lookahead guard and
   the z-score computation the way round437 tested tie/out-of-order leader
   feeds (7 new unit tests); run `cargo test --workspace --exclude
   finance-redis`; only then spend a Docker container on train/validation/
   holdout PF/win-rate via the plain sweep (same honest-metrics-only scope
   round437 accepted).
2. **Hurst-exponent regime filter**: implement `HurstRegimeFilterStrategy`
   (rolling R/S Hurst estimator, wrapper shape copied from
   `RealizedVolatilityRegimeFilterStrategy`), pick a small set of existing
   inner strategies to wrap (start with ones already closed on their own,
   e.g. Donchian/Keltner from round88/91, to test whether Hurst-gating
   rescues a mechanism this program already rejected unconditionally), unit
   test the R/S calculation against a synthetic series with a known Hurst
   exponent before trusting it on real data, then backtest train/validation/
   holdout.
