# Round 188 — Architecture proposal: incorporate the confirmed swing/1d signals as additional TREND-role strategies, not a new Portfolio bucket

## Context

Round 172-180 definitively confirmed `mtf_stochastic_14_3_30_70_sma50_trend_filtered`
(4h/1d swing, BTC) has a real, sizeable edge (PF 1.50-2.43 across splits,
full 5-year sample, cross-broker). Round 181-187 confirmed a second,
smaller-effect BTC candidate at the same 1d timescale (`mtf_rsi_*_trend_filtered`,
5m base but its edge is really coming from the 1d filter component, PF
1.01-1.54). Both writeups left the "how to deploy" question explicitly
open, flagged as needing a real design pass rather than a rushed
implementation. This round does that design pass — analysis only, nothing
implemented or deployed.

## Three options considered

**Option A — Separate low-frequency Portfolio bucket.** Run the swing
strategy as an independent target/position alongside the existing 5m
Portfolio target. Requires a second `PortfolioConstructionState` (or a
generalized N-bucket structure) per instrument, separate capital
allocation and risk tracking. Biggest architecture change of the three —
multiple concurrent positions per instrument is new territory for this
codebase. Not analyzed further this round; flagged as the "if nothing
else works" fallback.

**Option B — Trend-bias/gate wrapping the 5m entries.** Use the swing
signal's live directional bias to filter which 5m entries fire (e.g. only
take long 5m entries when the swing bias is long). Round 181 already
tested a *naive* version of this (plain 1d SMA trend, not the actual
confirmed stochastic-based signal) — results were clean-falsified on XAU,
ambiguous-then-modestly-positive on BTC. A *correct* version would need to
replicate the actual confirmed entry logic as a bias input rather than a
different, simpler SMA filter — nontrivial to build correctly, and Round
181's results already suggest naive versions of this idea don't obviously
help.

**Option C — Register the swing strategy as an additional strategy in
`production_candidates()`, contributing TREND-role evidence (recommended
starting point).** Confirmed via code read: `required_intervals` maps `4h`
to `EvidenceTimeframeRole::Trend` uniformly across every route (same
`survival_first_default()` mapping used everywhere,
`trading_modes.rs:477`). `MultiTimeframeTrendFilterStrategy` (the wrapper
type the swing candidate already uses) only produces a signal on candles
matching its own `base_interval` (4h) — it naturally contributes evidence
at exactly the "4h" trend-role slot and stays silent (Hold) at every other
interval, requiring **zero changes to `trading_modes.rs`** (not touching
Round 167's floor fix or the reweight formula at all). This is purely an
additive strategy-registration change in `deployment_rules.rs`/`strategies.rs`,
architecturally the smallest and lowest-risk of the three options.

Mechanically: `mature_alpha_strategy_quality` already exists specifically
to reward real, observed-positive performance over time — adding a
genuinely profitable strategy here is exactly what this mechanism is
*for*, categorically different from Round 65's rejected proposal
(subscribing an already-confirmed-*losing* strategy just to farm the
untested-benefit-of-doubt quality). This is the opposite case: a
confirmed-*winning* strategy earning real weight through real performance.

## The one real risk with Option C: the "benefit of doubt" accumulation window

`mature_alpha_strategy_quality` requires `trade_count >=
PERFORMANCE_CONFIDENCE_TRADES` (20) before it stops returning the
benefit-of-doubt default and starts reflecting real performance
(`alpha_performance_quality`/`mature_alpha_strategy_quality`,
`trading_modes.rs:524-568`). At the swing candidate's own confirmed
frequency (~0.35 trades/week), **accumulating 20 real live trades would
take roughly 57 weeks — over a year.** During that entire window, the new
strategy's `strategy_weight` would sit at the *same* elevated
benefit-of-doubt quality (`1.0`, maximal) as any genuinely untested
strategy — meaning it would carry outsized trend-role influence for over a
year before its own live track record could confirm or contradict the
backtest-derived confidence. This is a real, honest risk: backtest
confirmation (however thorough) is not the same as live performance, and a
strategy influencing `trend_score` at full untested-strength for a year
before self-correcting is a genuine exposure — not a reason to reject the
option, but a reason not to rush it in without a mitigation plan.

**Possible mitigations, not evaluated in depth this round:**
1. A shorter, strategy-specific `PERFORMANCE_CONFIDENCE_TRADES` override
   for genuinely backtest-confirmed strategies — but this cuts against the
   principle of trusting only *observed* performance, and picking a
   different threshold per strategy needs its own justification.
2. Deploy with a capped/reduced initial `strategy_weight` contribution
   (not full 1.0 benefit-of-doubt) specifically for *new* strategy
   registrations, decaying to the standard formula once real trades
   accumulate — a bigger, more careful code change than the base Option C
   idea, needs its own design pass.
3. Accept the risk as-is, reasoning that the backtest confirmation (3
   independent measurements, cross-broker, large final sample) is already
   unusually strong evidence for this program — stronger than the
   "recently-registered untested strategy" case the benefit-of-doubt
   mechanic was originally designed to be cautious about.

## Recommendation

**Do not implement this round.** Option C is the most promising path
(smallest change, correct mechanical fit, doesn't touch Round 167's
formula), but the benefit-of-doubt accumulation risk deserves an explicit
decision, not a default. Logging as a concrete, scoped Todo for a future
round or for direct owner input: proceed with Option C accepting the
~1-year benefit-of-doubt exposure (mitigation 3), or design a mitigation
first (1 or 2). Either way, this is now a well-scoped decision rather than
an open-ended "figure out an architecture" question — the actual mechanism
(add as a `production_candidates()` entry, TREND role, no core-algorithm
changes needed) is concrete and ready to implement once the benefit-of-doubt
question is resolved one way or the other.
