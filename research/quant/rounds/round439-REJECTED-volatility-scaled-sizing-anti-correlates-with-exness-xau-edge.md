# Round 439 — REJECTED: `PositionSizing::VolatilityScaled` wired into `finance-research`'s CLI and honestly backtested on `exness XAU` — decisively worse than both deployed sizing baselines at two `max_multiplier` values, and the mechanism is anti-correlated with this Alpha's edge, not merely miscalibrated

Classification: **REJECTED**. This round executes round435/438's named next
step for the last open item in `research/quant/index.md` section 0.5 (item
3, volatility-scaled sizing): add `finance-research` CLI flags for
`PositionSizing::VolatilityScaled` (round438, commit `524ac5c`,
`finance-live-action`), then run the honest holdout backtest that program
explicitly deferred. **Item 3 is now closed** — section 0.5 has no open item
left.

## What this round implemented (`finance-live-action`)

`crates/finance-research/src/execution_rules.rs`:

- `ResearchExecutionRuleValues` gained three fields: `target_volatility:
  Option<f64>`, `sizing_periods: usize`, `max_multiplier: f64` — read only
  when `sizing_mode` is `volatility_scaled`, ignored otherwise (doc comments
  on each field explain the split from the pre-existing `atr_periods`, which
  is `ProtectiveLevels::AtrMultiple`'s own window, not the sizing mode's).
- `selected_rule` gained a `"volatility_scaled"` match arm mirroring the
  existing `equity_fraction`/`risk_fraction` arms: validates
  `sizing_value` (`target_fraction`) is in `(0, 1]`, `target_volatility` is
  present/finite/positive (a config error, not a silent default — there is
  no historically justified fallback), `sizing_periods` is nonzero, and
  `max_multiplier` is finite and `>= 1.0`, then constructs
  `PositionSizing::VolatilityScaled { target_fraction, target_volatility,
  periods: sizing_periods, max_multiplier }`. Unlike `risk_fraction`, no
  protective-kind restriction is added — round438's own design closes with
  `VolatilityScaled` decoupled from `ProtectiveLevels::AtrMultiple`
  specifically so it can pair with the deployed `Fractional` kind, and
  nothing in the formula requires a particular protective kind.
- 6 new unit tests: supports `volatility_scaled` with `Fractional`
  protective (matches deployed pairing), supports it with `None` protective
  (demonstrates the decoupling round438 built, unlike `risk_fraction` which
  the existing code rejects for non-`Fractional`), and rejects missing
  `target_volatility`, zero `sizing_periods`, and a sub-1.0 `max_multiplier`
  each with the correct typed error.

`crates/finance-research/src/main.rs`:

- Three new CLI flags: `--portfolio-target-volatility <f64>` (unset by
  default — required only when `--portfolio-sizing-mode volatility_scaled`
  is selected), `--portfolio-sizing-periods` (default 14), and
  `--portfolio-max-multiplier` (default 3.0). Doc comments cite round435/438
  and explain these are research-only — `PositionSizing::VolatilityScaled`
  is still not constructible from production configuration
  (`PortfolioExecutionValues`/`deployment_rules.rs`/env vars untouched, per
  round438's explicit scope boundary, which this round also leaves
  untouched).
- Wired into the existing `ResearchExecutionRuleValues` construction site
  the CLI already uses for every other Portfolio-level flag.

Five other `ResearchExecutionRuleValues` construction sites in
`execution_rules.rs`'s and `portfolio_measurement.rs`'s own test modules
needed the three new required fields added (`target_volatility: None,
sizing_periods: 14, max_multiplier: 1.0` — inert for their `equity_fraction`/
`fixed_notional`/`risk_fraction` test cases).

**Verification**: `cargo build -p finance-research`: clean (1 pre-existing
unrelated warning, `split.rs`'s `selectable`). `cargo test -p
finance-research execution_rules`: 11/11 green (5 pre-existing + 6 new).
`cargo test --workspace --exclude finance-redis`: all green, zero failures.
`cargo fmt -p finance-research -- --check`: clean. `cargo clippy -p
finance-research --all-targets`: 9 warnings, all pre-existing and unrelated
to this diff (dead code in `split.rs`, a `filter_map`/`bool::then` style
lint in `daily_profit_gate.rs`, generated-proto enum-variant-name lints, and
a `result_large_err` lint in `klines.rs` — none in the files this round
touched).

## Backtest methodology

Read-only SSH tunnel (`ssh -f -N -L 18086:localhost:8086 my`), image rebuilt
from the new source (`docker build -f docker/Dockerfile-research -t
finance-research-local:latest .`). Four sequential Docker containers (never
more than one running at once, per the playbook's gRPC single-slot-gate
rule), each `-d --cpus=2 --memory=4g --memory-swap=6g --network host`, logs
captured with `docker logs` before `docker rm`. Route: `exness XAU` (cfd,
USD) — this program's priority-1 instrument. `--interval 5m --days 500`,
`--daily-profit-gate` (holdout-only extended metrics: Sharpe/Sortino/streak/
frequency/cost-ratio — the only branch besides `one_target` that reflects
real Portfolio-construction settings, per round82). Protective pinned to the
deployed pair: `--portfolio-protective-kind fractional --portfolio-stop-value
0.01 --portfolio-take-value 0.02` (round83's live values; the CLI's own
`default_value_t` is a stale 0.005/0.010 and must be overridden explicitly,
same requirement round427-431 documented). `--portfolio-minimum-hold-
decisions` left unset (defaults to the deployed
`DEFAULT_PORTFOLIO_MINIMUM_HOLD_DECISIONS = 36`).

All four runs report identical `candle_count=97472`,
`train_candle_count=58483`, `validation_candle_count=19494`,
`holdout_candle_count=19495`, holdout `2026-05-28T09:35:00Z` →
`2026-09-04T09:09:59.999Z` — the playbook's mandatory drift check passes, no
window mismatch between arms.

### Baselines (both deployed, run at the same window for direct comparison)

1. **`fixed-pct`** (production's primary selected rule,
   `deployment_rules.rs`'s `id: None` entry): CLI defaults, `sizing_mode
   fixed_notional`, `sizing_value 5.0`.
2. **`compounding-10pct`** (also concurrently deployed,
   `deployment_rules.rs`'s `id: Some("compounding-10pct")` entry):
   `--portfolio-sizing-mode equity_fraction --portfolio-sizing-value 0.10`
   — the **sizing-matched** baseline for the candidate below, since both use
   the same 0.10 base fraction and differ only in whether that fraction is
   scaled by realized volatility.

### Candidate: `volatility_scaled`, two `max_multiplier` sensitivity points

`--portfolio-sizing-mode volatility_scaled --portfolio-sizing-value 0.10`
(same `target_fraction` as `compounding-10pct`) `--portfolio-target-volatility
0.0009597 --portfolio-sizing-periods 14 --portfolio-max-multiplier {3.0, 2.0}`.

**`target_volatility` source, and a correction to round438's own text**:
round333's independent Timescale query (read-only, 5m log-return std-dev on
`exness.cfd.XAU.USD`, zero containers) measured two segments: **recent 0-500
days: 0.09597%**, and **older 500-900 days: 0.05590%**. Round438's "next
step" paragraph named "round 333 measured `exness XAU`'s 500-day segment ATR
volatility at 0.05590%" — that value is actually round333's **older**
500-900-day segment, not the 500-day one. Since this round's own `--days
500` window *is* round333's recent segment, the internally-consistent
external reference is **0.09597%** (→ `0.0009597` fractional), which is what
this round used. Using the older, calmer segment's lower number instead
would have systematically depressed the scalar (since realized volatility
during the tested window would then exceed the reference most of the time),
compounding the anti-correlation this round found for an unrelated,
avoidable reason — worth flagging explicitly so a future round does not
repeat round438's citation.

## Results

| Config | trades | trades/wk | Sharpe | Sortino | gross PnL (pre-cost) | net PnL | cost/gross ratio | ulcer | skew | kurtosis |
|---|---|---|---|---|---|---|---|---|---|---|
| `fixed-pct` (deployed) | 111 | 7.850 | -1.0130 | -1.4302 | 0.40447 | -0.28400 | 1.70215 | 4.02e-5 | 0.2693 | -0.2752 |
| `compounding-10pct` (deployed, sizing-matched) | 111 | 7.850 | -1.0116 | -1.4284 | 80.60439 | -57.22565 | 1.70996 | 0.00799 | 0.2707 | -0.2734 |
| `volatility_scaled`, max_mult **3.0** | 111 | 7.850 | **-1.8673** | **-2.4961** | **15.14865** | **-103.17867** | **7.81108** | 0.00889 | 0.2359 | 0.8698 |
| `volatility_scaled`, max_mult **2.0** | 111 | 7.850 | -1.8703 | -2.4997 | 14.77631 | -103.35474 | 7.99462 | 0.00889 | 0.2360 | 0.8683 |

All four share the identical 111-trade / 7.850-per-week decision stream —
expected, since a Portfolio-layer sizing change cannot move which decisions
the Alpha layer emits or when. `trades_per_week` clears Target 3 (7.0) in
every row; `target1_profitable` fails in every row (all four are net-losing,
consistent with this entire program's Alpha-layer finding, round393/366).

## Why this is REJECTED, not a calibration problem

Two facts rule out "wrong `max_multiplier`" as the explanation:

1. **The two sensitivity points are nearly identical** (Sharpe -1.8673 vs
   -1.8703, net PnL -103.179 vs -103.355) despite a 33% change in the
   ceiling (3.0x → 2.0x). If occasional ceiling-clamped spikes were driving
   the result, tightening the ceiling would move the numbers materially. It
   barely moves them — the **average** scalar, not the tail, sets the
   outcome.
2. **Pure linear rescaling does not reproduce this pattern.**
   `fixed-pct` (≈$5 notional) and `compounding-10pct` (≈$1000+ notional,
   ~200x larger) have **nearly identical** `cost_to_gross_pnl_ratio` (1.702
   vs 1.710) and Sharpe/Sortino (-1.013/-1.430 vs -1.012/-1.428) — exactly
   what linear scaling predicts, since fees/slippage/funding scale with
   notional the same way PnL does, so their ratio is scale-invariant.
   `volatility_scaled` uses the **same** 0.10 base fraction as
   `compounding-10pct` yet its `cost_to_gross_pnl_ratio` is **4.6x higher**
   (7.811 vs 1.710) and its `gross_pnl_before_costs` **collapsed 81%**
   (15.149 vs 80.604) while net PnL **worsened 80%** (-103.179 vs -57.226).
   A uniform rescaling cannot produce that gap — only a *per-trade* size
   variation that is **anti-correlated with the trade's own edge quality**
   can: realized-volatility-based sizing is systematically **undersizing
   this Alpha's better trades and oversizing its weaker/costlier ones** on
   this route and window. That is the opposite of vol-targeting's intended
   effect (constant risk contribution regardless of regime), and it is a
   property of the mechanism on this Alpha, not an artifact of the chosen
   ceiling.

## Scope of this evidence

Single route (`exness XAU`, this program's priority-1 instrument), single
holdout window (no second disjoint `--as-of` window run this round). Given
the result is decisively negative in both directions of the one open
sensitivity axis (`max_multiplier`) and mechanistically explained rather
than a borderline reading, this round follows this program's established
precedent of not requiring multi-window reconfirmation before closing a
clearly-losing mechanism (round91 Keltner, round93 Heikin-Ashi, round372's
guard reversal all closed on comparably single-window, mechanistically-clear
evidence). A `binance BTC` cross-check was **not** run this round: it would
need an independent BTC realized-volatility reference measurement first
(round333's Timescale method was XAU-only), and this program's rule against
inventing unlabeled constants applies as much to a guessed BTC
`target_volatility` as to any other fabricated number. If this direction is
revisited, that measurement is the correct starting point, not a second XAU
window.

## Cleanup

All four containers removed (`docker ps -a --filter
"ancestor=finance-research-local:latest"` confirmed empty after the round).
SSH tunnel closed (`pkill -f "ssh -f -N -L 18086"`, confirmed via `ss -tlnp
| grep 18086` returning nothing). `git status --short` clean in both repos
before ending the round (checked after committing below).
