# Round 433 — REJECTED: short-term k-bar return reversal fails on both routes across all 5 variants and all 3 splits

**Layer:** Alpha
**Instruments:** `exness XAU/USD` (cfd), `binance BTC/USDT` (perpetual future)
**Classification:** REJECTED

## Context

Round 432 (2026-09-04) audited the full ~90-candidate existing search space
and found no open, untested Alpha or Portfolio direction. Immediately after,
the user proposed two genuinely new mechanisms not present anywhere in that
history (`research/quant/index.md` section 0.5, commit `3e92cfe`):

1. **Short-term k-bar return reversal** — classic autocorrelation reversal:
   after `k` consecutive same-direction closes, fade the run. Buildable now
   with the existing `Strategy` trait.
2. **Cross-instrument lead-lag** — blocked: `Strategy::evaluate` takes one
   kline of one instrument at a time (`finance-strategy/src/engine.rs:30`),
   with no second-instrument data path. Needs an engine change before it is
   testable; not attempted this round.

This round implements and backtests direction 1.

## Implementation

Added `KBarReturnReversalStrategy` to
`finance-live-action/crates/finance-research/src/strategies.rs` (research-only
candidate registry, not wired into any live worker). Mechanism: track the
last `k+1` closes per instrument; if all `k` consecutive per-bar returns are
strictly positive, signal `EnterShort`; if all strictly negative, signal
`EnterLong`; otherwise no signal. An optional `minimum_cumulative_move`
threshold exists in the struct (left at `0.0` this round — the run-length
condition alone is the mechanism under test; a move-floor is a separate,
untested lever).

Mechanistically distinct from every existing reversal/mean-reversion
candidate in the file: `CandleReversionStrategy` fades a single candle
regardless of prior history; `RsiMeanReversionStrategy`/`rsi_2_10_90` react
to a bounded oscillator crossing a fixed level; `BollingerReversionStrategy`/
`KeltnerReversionStrategy` react to a volatility-band touch. This strategy
reacts only to the **sign sequence** of the last `k` returns — a run length,
not a level or band.

Registered 5 variants in `strategies::candidates()` (the plain discovery
sweep grid, scored via `--json` train/validation/holdout, not the production
Portfolio ensemble):

- `kbar_return_reversal_2`, `_3`, `_5` — base signal, k swept 2/3/5, no
  threshold.
- `sma10_trend_filtered_kbar_return_reversal_3` — k=3 wrapped in the same
  same-timeframe SMA(10) trend-agreement filter already validated on other
  reversion candidates in this grid (e.g. `rsi_2_10_90`).
- `session_london_kbar_return_reversal_3` — k=3 wrapped in the same
  08:00-14:00 UTC London-session filter used elsewhere
  (`session_vwap_reversion_london_*`).

`cargo build -p finance-research` compiled cleanly; `cargo test -p
finance-research strategies::` — 62/62 passed, including
`every_candidate_carries_a_unique_name` (confirms no name collision from the
5 new entries).

## Backtest

Docker `finance-research-local:latest` built from
`docker/Dockerfile-research` (includes this change), run via the read-only
SSH tunnel to production Finance MW (`ssh -f -N -L 18086:localhost:8086 my`),
`--cpus=2 --network host`, one container per route (2 total, within the
2-container/round cap), each started detached (`-d --rm`) with `docker logs
-f` piped to a file before waiting, per the playbook's leaked-container
lesson (round 124-125). Both confirmed removed via `docker ps -a --filter
"ancestor=finance-research-local:latest"` after `docker wait`. Tunnel closed
and confirmed via `ss -tlnp` at the end.

Plain `--json` sweep (default train/validation/holdout split), `--days 500`,
5m interval:

- `exness XAU/USD` cfd: `candle_count` 97,472; holdout 98.98 calendar days
  (2026-05-28 → 2026-09-04).
- `binance BTC/USDT` perpetual: `candle_count` 143,998 (matches round 361's
  recorded value for this exact route/window, confirming the window is the
  expected one); holdout 99.997 calendar days (2026-05-27 → 2026-09-04).

### Results (profit_factor, train / validation / holdout)

| Variant | exness XAU | binance BTC |
|---|---|---|
| `kbar_return_reversal_2` | 0.0956 / 0.1554 / 0.1085 | 0.2146 / 0.2255 / 0.1985 |
| `kbar_return_reversal_3` | 0.2203 / 0.3085 / 0.2314 | 0.3881 / 0.4062 / 0.3278 |
| `kbar_return_reversal_5` | 0.6275 / 0.4488 / 0.5219 | 0.6800 / 0.6980 / 0.6426 |
| `sma10_trend_filtered_..._3` | 0.8218 / 0.5858 / 0.6505 | 0.7280 / 0.7699 / 0.6405 |
| `session_london_..._3` | 0.5203 / 0.4726 / 0.4849 | 0.5521 / 0.6797 / 0.5846 |

Every one of the 30 cells (5 variants × 2 routes × 3 splits) has PF strictly
below 1.0. Best single cell observed: `sma10_trend_filtered` on `exness XAU`
train, PF 0.8218 — still a loss, and it is the *train* split, not
validation/holdout.

## Reading

**The shape is monotone and consistent across both routes, and it points
away from an edge, not toward one.** PF rises with `k` (2 → 3 → 5) on both
routes as the run-length filter gets stricter and the trade count collapses
(XAU: 9,996 → 4,180 → 838 train trades; BTC: 14,998 → 6,327 → 1,256), but it
never crosses 1.0 — the same "extending a filter drives PnL toward, not past,
break-even as activity disappears" pattern this program already closed for
the Portfolio-layer hold guard (round 363: "Extending a hold indefinitely
drives PnL to zero from below — arithmetic, not a strategy"). Here it is an
Alpha-layer entry-condition strictness parameter, but the same arithmetic
applies: fewer, more-selective trades approach the fee/slippage floor from
below, not evidence of a real reversal edge.

Neither wrapper closes the gap. The SMA(10) trend filter is the single best
performer on both routes but still loses on every split; the session filter
is worse than the SMA filter and, on XAU, worse than the unfiltered k=5 base.

No cherry-picking: all 5 variants, both routes, all 3 splits are reported
above; none is omitted.

## Classification: REJECTED

The mechanism (fade a run of `k` consecutive same-direction closes) is
cleanly falsified on both priority routes (XAU, then BTC), at every tested
`k` and both tested filter wrappers, on train, validation, and holdout alike.
This closes direction 1 of the two new mechanisms logged after round 432.

Direction 2 (cross-instrument lead-lag) remains open and blocked on an
engine change (`Strategy::evaluate` has no second-instrument data path) —
untouched this round, tracked in `index.md` section 0.5 for a future design
round.

## Cleanup

- `git status --short` clean in `finance-live-action` after the source
  change was reviewed (no uncommitted state left — see note below on
  disposition of the code change).
- `git fetch origin main -q && git rev-parse HEAD origin/main` checked in
  `finance-live-action` before ending the round.
- Two Docker containers removed (`--rm`, confirmed via `docker ps -a`).
- SSH tunnel closed, confirmed via `ss -tlnp` (no listener on 18086).

Research evidence updated: this file,
`research/quant/reports/optimize_loop_update_v2.csv` (10 new rows, round
433), `research/quant/index.md` (section 0.5 closed out, closed-directions
table updated).
