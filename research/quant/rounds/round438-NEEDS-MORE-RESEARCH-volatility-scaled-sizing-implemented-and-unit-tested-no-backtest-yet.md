# Round 438 — NEEDS-MORE-RESEARCH: `PositionSizing::VolatilityScaled` implemented and unit-tested in `finance-live-action`; no backtest run this round, matching round435's own sequencing

Classification: **NEEDS-MORE-RESEARCH**. This round executes round435's named
next step for the last open item in `research/quant/index.md` section 0.5
(item 3, volatility-scaled sizing): implement the sizing mode with a
justified fallback/clamp, unit-test it as thoroughly as `RiskFraction`, and
stop — no Docker container, no backtest number — exactly as round435
specified ("1 round riêng implement ... TRƯỚC KHI bất kỳ round nào chạy
Docker backtest dùng sizing mode này").

## What round435 left open

Two design questions blocked any trustworthy backtest number for this mode:

1. `PositionSizing::notional()`/`SimulationConfig::executable_notional()` are
   called from four places with no ledger/ATR context (`portfolio_risk.rs`'s
   `widened_for_simulation` and its two pre-trade gates, `config.rs`'s
   `apply_leverage_constraints`). What should a context-free call return for
   a volatility-scaled mode — it must not under-widen the live risk gate
   (round84's failure class for `EquityFraction`/`RiskFraction`) while
   staying finite enough for `bracket_for_notional` to resolve.
2. Inverse-volatility sizing diverges as realized ATR approaches zero
   (`target_volatility / realized_volatility → ∞`) and needs an explicit,
   justified ceiling, not an invented constant.

## What this round implemented (`finance-live-action`, commit `524ac5c`)

`crates/finance-core/src/trading_modes.rs`:

- New variant `PositionSizing::VolatilityScaled { target_fraction,
  target_volatility, periods, max_multiplier }`. Notional = `equity *
  target_fraction * scalar`, where `scalar = clamp(target_volatility /
  realized_volatility, 0.0, max_multiplier)`.
- **Answer to design question 1**: `PositionSizing::notional()` (unchanged
  signature, used by every no-ledger caller) now delegates to a new
  `notional_with_volatility(equity, protective, realized_volatility:
  Option<f64>)`, and the `None`/no-data branch returns `max_multiplier` — the
  literal largest notional this mode can ever request. Every existing
  no-ledger call site (`widened_for_simulation`, the two pre-trade gates,
  `apply_leverage_constraints`'s bracket lookup) therefore always sees the
  true worst case, so widening/bracket-selection can never be narrower than
  what a real position might need — closing the exact failure shape round84
  hit for `EquityFraction`/`RiskFraction`.
- **Answer to design question 2**: `max_multiplier` (finite, `>= 1.0` by
  construction) is that same worst-case ceiling — one value answers both
  questions rather than two independently invented constants.
- `SimulationConfig::executable_notional_with_volatility` mirrors
  `executable_notional`'s existing `RiskFraction` margin clamp
  (`desired.min(equity * leverage)`) for `VolatilityScaled` too, so a
  saturated scalar still cannot request more than the account can finance.
- ATR tracking (`record_true_range`/`average_true_range`) was previously
  hard-coupled to `ProtectiveLevels::AtrMultiple` (the periods came from
  `self.config.protective`, so `Fractional`/`None` protective never recorded
  true range at all). Generalized via `SimulationConfig::true_range_retention()`,
  which returns `Some(periods)` when either the protective kind or the sizing
  mode needs ATR (retaining the larger requested window), or `None`
  otherwise — preserving the exact previous no-op fast path for today's
  deployed `Fractional` protective with non-volatility-scaled sizing.
  `average_true_range` now takes `periods` as a parameter instead of reading
  it from `protective` internally, so `VolatilityScaled` can pair with
  `Fractional` (the deployed kind) or `None`, not only `AtrMultiple`.
- `SimulatedLedger::open_position` computes `realized_volatility = atr /
  kline.close` from the ledger's own tracked ATR before sizing. **When the
  window has not warmed up yet (`average_true_range` returns `None`),
  `open_position` returns early — no position opens.** This mirrors the
  existing `protective_offsets`'s `AtrMultiple` warm-up guard a few lines
  below rather than inventing a new cold-start behavior: a real ledger
  refuses to size at an assumed volatility instead of reusing the
  max-multiplier ceiling that no-ledger callers use for widening. The two
  design answers are deliberately different: the ceiling is correct for
  bounding a structural cap, and wrong for what a real order should do when
  the market's actual current volatility is simply unknown yet.

`crates/finance-core/src/portfolio_risk.rs`: added `VolatilityScaled` to the
two `matches!` arms that already treat `EquityFraction`/`RiskFraction` as
"equity-dependent sizing" for gate-cap widening — same treatment, same
justification, one line each.

## Unit tests (14 new, `crates/finance-core/tests/trading_modes.rs`)

Formula-level (no ledger): fallback ceiling with no reading; inverse scaling
at 0.5x/2x/4x the target volatility; explicit clamp at `max_multiplier` when
realized volatility is 100x below target; degenerate readings (`0.0`,
negative, `NaN`, `+inf`) all fall back to the ceiling rather than producing a
`NaN`/`inf` notional; the margin clamp binds identically to `RiskFraction`'s
existing one.

Ledger-level (real `SimulatedLedger`, `periods: 3`): three klines of
constant true range 2.0 confirm the position stays flat for the first two
(warm-up) and opens on the third at the exact predicted notional (scalar
1.0, matching a plain `EquityFraction` baseline); a second test runs three
separate ledgers at true range 1.0 / 8.0 / 0.02 confirming the calm case
sizes 2x, the turbulent case sizes 0.25x, and the extremely calm case
saturates at the `max_multiplier` ceiling rather than exploding — the
concrete, ledger-level demonstration of the round435 ATR-to-zero concern
being bounded. One ledger test deliberately pairs `VolatilityScaled` with
`ProtectiveLevels::Fractional` (not `AtrMultiple`) to demonstrate the
decoupling this round exists to deliver.

`cargo test -p finance-core --test trading_modes`: 64/64 green.
`cargo test -p finance-core --test portfolio_risk`: 12/12 green (unaffected).
`cargo test --workspace --exclude finance-redis`: all green, zero failures.
`cargo fmt -p finance-core`: clean. `cargo clippy -p finance-core
--all-targets`: no new findings (2 pre-existing, unrelated `enums.rs`
findings confirmed via `git stash` to predate this diff, left untouched per
scope discipline, same two round437 already noted a superset of).

## What this round deliberately did NOT do

- **No production wiring.** `PortfolioExecutionValues`/`config.rs`'s
  `sizing_mode` string parsing, `deployment_rules.rs`, and any env var are
  untouched — `PositionSizing::VolatilityScaled` is not constructible from
  configuration anywhere yet, only from Rust code (this round's tests).
  Nothing in production or research CLI behavior changed.
- **No CLI wiring in `finance-research`.** The backtest CLI cannot select
  this sizing mode yet.
- **No Docker backtest, no PF/Sharpe/holdout number.** Per round435's
  explicit sequencing, that is deliberately the next round's job, not this
  one's.

## Next step

A follow-up round adds `finance-research` CLI flags for this sizing mode
(mirroring how `--portfolio-stop-value`/`--portfolio-atr-periods` already
expose `ProtectiveLevels::AtrMultiple`), then runs the honest
train/validation/holdout backtest this program requires before calling
anything an improvement. Candidate parameter grid to start from:
`target_fraction` at the deployed `EquityFraction`'s baseline (0.10),
`target_volatility` near the ATR/price ratios already observed in this arc's
`exness XAU`/`binance BTC` history (round 333 measured `exness XAU`'s 500-day
segment ATR volatility at 0.05590 %/5m — convert to the same fractional units
this variant uses), and `max_multiplier` at a conservative 2.0-3.0 pending a
sensitivity check.
