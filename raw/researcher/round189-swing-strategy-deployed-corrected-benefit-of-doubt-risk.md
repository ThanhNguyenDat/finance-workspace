# Round 189 — Production check-in on Round 183's XAU stall (too early to conclude), correction of Round 188's risk analysis, and deployment of the confirmed swing candidate

## Part 1 — XAU/binance stall re-check (Round 183/184's action item)

Re-read all 4 routes' checkpoints from Redis:

```
                    decisions_since_target_change   state
XAU/binance         69,629 (was 69,610)             flat, protective_exit_waiting_for_fresh_insight
BTC/binance         224 (was 206)                   flat, protective_exit_waiting_for_fresh_insight
Exness/BTC          12                               SHORT, gate_passed (weighted_score -0.50, 40 contributors)
Exness/XAU          15                               LONG, gate_passed (weighted_score +0.73, 24 contributors)
```

Only ~19-30 more decision cycles have elapsed on the Binance routes since Round
183/184's check — far short of the "1-2 days" the action item asked for
(the compaction between rounds compressed much less wall-clock time than
expected). **Not yet a resolved verdict either way** — XAU/binance is still
stuck, but this is not new information; Round 184 already computed the
live `entry_score` was close (-0.012 vs the 0.10 gate) and explained this
needs a genuine directional-agreement moment, not a fixed number of cycles.
Both Exness routes have exited and cleanly re-entered with real gated
positions in the meantime — expected baseline behavior (they were never
stuck the way the Binance routes were), useful only as confirmation the
Round 167 deploy has no regression on routes that were already healthy.
**Action carried forward unchanged: re-check XAU/binance and BTC/binance's
`decisions_since_target_change` again in 1-2 real days.**

## Part 2 — Correcting Round 188's "benefit-of-doubt" risk analysis

Round 188 proposed registering the confirmed swing candidate
(`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, 4h base / 1d SMA50 filter)
as an additional TREND-role strategy, but stopped short of implementing it,
citing one risk: a brand-new strategy registration would carry "full
untested-strength trend-role influence" via a `1.0` benefit-of-doubt
`strategy_weight` for the ~1 year it takes to accumulate 20 real trades at
this signal's ~0.35/week frequency.

**Re-reading `trading_modes.rs:587-593` this round shows that framing is
wrong.** `mature_alpha_strategy_quality` — the function that actually
produces `strategy_weight` (how much a strategy's own score counts toward
`entry_score`/`trend_score`) — returns exactly `0.0` for any strategy below
`PERFORMANCE_CONFIDENCE_TRADES` (20), full stop:

```rust
fn mature_alpha_strategy_quality(performance: SimulatedPerformance) -> f64 {
    if performance.trade_count < MultiTimeframePortfolioPolicy::PERFORMANCE_CONFIDENCE_TRADES as u64
    {
        return 0.0;
    }
    alpha_performance_quality(performance)
}
```

The `1.0` benefit-of-doubt only exists in `alpha_performance_quality`, which
feeds `interval_quality` (the interval's own aggregate weight across all its
configured strategies), not `strategy_quality`. So a brand-new strategy's
own contribution to `entry_score`/`trend_score` — `interval_weight ×
strategy_weight × score` — is **exactly zero** until it has 20 real trades,
because `strategy_weight` is zero. This is the opposite of "full untested
influence": it's zero influence, matching the "trust only observed
performance" principle the mechanism was supposedly at risk of violating.

The real (much milder) effect: `MultiTimeframeTrendFilterStrategy::evaluate`
(`crates/finance-strategy/src/multi_timeframe_trend_filter.rs:77-118`) only
ever returns `Some` on candles matching its own `base_interval` (4h here) —
every other interval, including its own `higher_interval` (1d, which only
updates internal trend state), always gets `None`. So this strategy will
*permanently* show `trade_count=0` at the 7 non-4h intervals (not just
during a ramp-up year), contributing a flat `1.0` benefit-of-doubt term to
`interval_quality`'s raw sum at each of those. This is not new or unique to
this strategy — every existing `mtf_*` "zombie" strategy in
`configured_extra_strategies` already does exactly this at every interval
that isn't its own base interval (confirmed via the same code path). Adding
one more strategy is a small, already-familiar marginal dilution of relative
interval weights, not a novel risk.

**Conclusion: the benefit-of-doubt risk that blocked Round 188's
recommendation does not apply the way it was described. Proceeding with
Option C this round**, on this corrected understanding — not on the
original (overstated) risk framing.

## Part 3 — Implementation

Registered `mtf_stochastic_4h_1d_sma50` (`StrategyKind::MultiTimeframeTrendFilteredStochastic`,
base_interval=4h, higher_interval=1d, k=14, d=3, oversold=30, overbought=70,
trend_period=50/SMA50 — the exact params behind the confirmed swing
candidate) in `crates/finance-api/src/deployment_rules.rs`'s
`configured_extra_strategies`, scoped to both BTC venues only
(`is_binance_btc_perpetual` and `is_exness_btc_cfd` — the two instruments
the swing candidate was actually validated against; XAU was never part of
its evidence base and Round 181 separately falsified the related-but-
different 5m+1d-filter idea on XAU). Both instruments now register 6
strategies total (2 base + 4 extra) instead of 5.

Updated 3 golden tests that hardcoded the old "3 extra strategies" count:
`binance_btc_perpetual_gets_all_three_extra_strategies` →
`..._all_four_extra_strategies`, same rename for the Exness BTC equivalent,
and `historical_replay_uses_all_subscription_configured_strategies`'s
expected strategy-name list.

Full local verification (Docker, `--cpus=3`):
`cargo fmt --check` clean; `cargo test --workspace --exclude finance-redis`
— finance-api 211/211, finance-core 78/78, finance-research 54/54,
finance-strategy 87/87 (+130 in an earlier same-crate integration-test
binary), all other workspace crates green, 0 failures.

Commit `fa23f16` pushed, CI green.

## Part 4 — Production verification found and fixed a second, deeper bug

Direct Redis checkpoint reads immediately after `fa23f16` deployed showed
Binance BTC's live `strategy_weights` was **missing `mtf_stochastic_4h_1d_sma50`
entirely** (5 keys, not 6), while Exness BTC had it correctly (at `0.0`).
Root cause: `restore_checkpoint_state` (`crates/finance-api/src/trading_api.rs`)
wholesale-replaces the freshly-built `MultiTimeframePortfolioPolicy` (which
has every currently configured strategy via `survival_first_default`) with
whatever `strategy_weights` key set was persisted in the checkpoint —
`reweight_from_alpha_performance` only ever recomputes quality for keys
already present in that map. A strategy added to `deployment_rules.rs`
after a route's checkpoint was last written is therefore permanently
invisible to that route's live weights after a restart, unless the
checkpoint happens to get invalidated for an unrelated reason (which is
what let Exness BTC pick it up by chance this time — its checkpoint had
independently reset, evidenced by its very recent `decisions_since_target_change=12`
short entry). **This is not new to this deploy** — the same gap has
structurally applied to every extra strategy ever added to a long-running
route in this program's history.

Fixed with `MultiTimeframePortfolioPolicy::sync_strategy_roster` (+ a
`MultiTimeframeEvidenceBook` pass-through), called unconditionally right
after checkpoint restore with the currently configured strategy names.
Inserts any missing name at `0.0` — exactly what `mature_alpha_strategy_quality`
already computes for `trade_count == 0`, so this changes no scoring
behavior, only makes previously-invisible strategies start maturing
normally; never removes an existing key; a no-op when the policy was
freshly built rather than restored. Added a regression test
(`finance-core/tests/trading_modes.rs`) proving a new key gets added at
exactly `0.0` without disturbing an existing strategy's already-computed
weight, and that a second call (e.g. a second restart with no roster
change) is idempotent.

Full local verification green (`cargo fmt --check`, `cargo test --workspace
--exclude finance-redis`, all crates 0 failures). Commit `2d8cfa7` pushed,
CI green (`build-and-push`/`deploy-app` both succeeded). Production
verification: all 6 containers on exact SHA `2d8cfa7`, healthy. Re-read
both BTC routes' checkpoints post-deploy — **both now show
`mtf_stochastic_4h_1d_sma50` in `strategy_weights` at `0.0`, every other
strategy's weight numerically unchanged** — confirms the fix works and the
swing candidate is now genuinely live on both BTC routes, maturing
normally toward its first real-performance reweight at 20 trades.

Note: the `Production Live Action Verification` CI workflow failed on
`fa23f16`'s own deploy (3rd occurrence of the already-documented flaky
retry-budget pattern — all 3 health probes returned 200 on every attempt).
Independently confirmed a false alarm via direct SSH/Redis checks both
immediately after `fa23f16` and again after `2d8cfa7`.
