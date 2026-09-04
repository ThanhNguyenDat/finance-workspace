# Round 435 — Volatility-scaled sizing (vol-targeting): design survey confirms this is a shared production risk-gate change, not a narrow research-only addition

Classification: **NEEDS-MORE-RESEARCH**. Zero containers, zero backtest compute
— code read only (`finance-core`, `finance-api`, `finance-research`).

## What was tested

Index item 3, logged 2026-09-04 (commit `dcdb9ce`), user-proposed direction:
scale position notional inversely with recent realized volatility (high-vol
route/regime → smaller size, low-vol → larger size), holding risk-per-trade
roughly constant over time. Explicitly distinct from `equity_fraction`/
`risk_fraction` (closed, Round 89-90/151-152): those scale with *account
equity*, never read market volatility. Item 4 (cross-route correlation-aware
allocation) was **not** touched this round — the index note says pick one of
the two per round to avoid factorial risk before either stands independently
validated; this round picked item 3.

## Where the mechanism has to live

`finance-core/src/trading_modes.rs`'s `SimulatedLedger` already tracks a
rolling ATR from real candles, causally: `record_true_range` is called on
every kline whether or not a position is open (`:1720`, `:1751`), pushes into
`true_ranges: VecDeque<f64>` (`:1627`), and `average_true_range()` (`:2022-2032`)
averages the last `periods` values, returning `None` during warm-up. This is
the *only* built-in volatility measure in the engine and it is already used
for exactly this kind of purpose: `protective_offsets` reads it to size an
`AtrMultiple` stop/take (`:2016-2017`), gated by `?` so a warming-up ledger
places no stop rather than a wrong one. A vol-scaled sizing mode would read
the same `self.average_true_range()` from inside `open_position` (`:1908-1923`,
where `self.config.executable_notional(self.equity)` is currently called) —
mechanically straightforward, no lookahead risk, since it is the same
backward-only accumulator the ATR protective-stop path already trusts.

## Why this is not the same shape as Round 433's addition

Round 433 added `KBarReturnReversalStrategy` as a new `Strategy` impl — pure
signal generation, zero interaction with sizing or risk code, safe to add and
test in isolation. Sizing is architecturally different: `PositionSizing`
(`trading_modes.rs:1358-1409`) and its `notional()` method, plus
`SimulationConfig::executable_notional()` (`:1261-1269`), are **shared** between
the live runtime and every research measurement path, and are called from
places that have no ledger and therefore no ATR history:

- `finance-core/src/portfolio_risk.rs:272-308`
  (`PortfolioRiskPolicy::widened_for_simulation`) — calls
  `executable_notional(starting_equity)` once, before any kline is seen, to
  widen the pre-trade risk-gate caps so `equity_fraction`/`risk_fraction`
  orders are not rejected. The method's own doc comment (`:260-271`) names the
  exact production bug this code exists to prevent: **Round 84** found
  research's `one_target` silently rejected ~100% of `equity_fraction`/
  `risk_fraction` decisions because the risk gate was never widened for
  equity-dependent sizing — the `fixed_notional` rule looked fine only because
  its $5 order never neared the unwidened caps. This is the single most
  relevant precedent for a new equity/volatility-dependent sizing mode: get
  the gate-widening fallback wrong and the failure mode is silent, not a
  crash.
- `finance-core/src/portfolio_risk.rs:622,664,691,694,809` — further pre-trade
  risk-gate sizing checks, same no-ledger-context constraint.
- `finance-api/src/config.rs:439-475` (`apply_leverage_constraints`) — calls
  `sizing.notional(starting_equity, protective)` at config-validation time to
  pick a maintenance-margin leverage bracket via `bracket_for_notional`.
- `finance-api/src/trading_api.rs:5424-5427,5486-5489` — unit tests exercising
  the same risk-gate path (not itself a blast-radius concern, but confirms the
  call is on the production code path, not a test-only shim).

Every one of these calls `notional()`/`executable_notional()` with only
`(equity[, protective][, leverage])` — never a volatility figure — and this
is a **documented, deliberate** constraint already, not an oversight:
`RiskFraction`'s own doc comment (`:1363-1374`) rules out pairing it with
`AtrMultiple` protective levels for exactly this reason ("`AtrMultiple`'s stop
only exists once a ledger has seen enough range, which every non-ledger
caller of `notional`... cannot supply"). A volatility-scaled sizing mode hits
the identical constraint one layer up: the sizing figure itself, not just the
stop distance, would depend on ledger-only state.

## Two unresolved design questions, neither answerable by running a backtest

1. **What does `notional()` return when there is no ATR context** (every call
   site above)? It must not *under*-widen the live risk gate — repeating the
   exact Round 84 failure class the code comment warns about in place — but
   any fallback value is a guess until justified. `apply_leverage_constraints`
   makes an arbitrary guess actively harmful: it feeds `notional()`'s return
   into `bracket_for_notional(notional)`, which has no bracket for an
   unbounded value, so a "return something very large" fallback (safe for the
   risk-gate-widening call) would make config validation fail outright at
   startup for this call site.
2. **Notional is unbounded as realized ATR → 0.** `RiskFraction` has the same
   inverse-of-a-distance shape and is explicitly capped at
   `executable_notional`'s `.min(equity.max(0.0) * f64::from(self.leverage.max(1)))`
   (`:1264-1266`) — the same cap would need to apply here, but even leverage-capped,
   a quiet-regime notional could still be large relative to what the strategy
   was ever tested at. Bounding it further needs an explicit floor-volatility
   or max-size-multiple parameter, and choosing one without evidence is
   exactly the kind of fabricated-input this loop's rules forbid.

Neither question is a backtest question — both are contract-safety questions
about the shared risk-gate/config-validation call sites, and both must be
settled and unit-tested (mirroring `RiskFraction`'s existing coverage in
`crates/finance-core/tests/trading_modes.rs:1268-1291` and
`crates/finance-core/tests/portfolio_risk.rs:198-271`) before any `one_target`
number involving this sizing mode is trustworthy.

## Why this round stops at the survey

Writing the notional formula and a plausible-looking gate-widening fallback
quickly, to produce one backtest number this round, would repeat a failure
mode this program has already paid for twice: Round 84's silent risk-gate
under-widening (cited directly in the code this survey read), and the
MTF `open_time`-vs-`close_time` lookahead bug fixed at `3c16745` (cited by
Round 434 for the same reason, applied here to a different code path).
Round 434 used exactly this reasoning to stop at a design survey for
cross-instrument lead-lag rather than rush an alignment routine in the same
round it would be measured in; the same discipline applies here, on a
mechanism whose failure mode (silently wrong live order sizing, in either
direction) is more consequential than a wrong Alpha signal.

## Concrete next step

A dedicated implementation round, separate from any round that reports a
`one_target` number for this mode:

1. Add `PositionSizing::VolatilityScaled { target_risk_fraction: f64, atr_periods: usize }`
   (or equivalent) to `trading_modes.rs`.
2. Decide and justify the no-ATR-context fallback used by
   `notional()`/`executable_notional()` at the call sites above — it must
   satisfy both constraints simultaneously: never under-widen the live risk
   gate (Round 84's constraint) and remain finite enough for
   `bracket_for_notional` to resolve a leverage bracket (`config.rs`'s
   constraint).
3. Add an explicit, justified maximum-notional clamp for the low-volatility
   case, analogous to `RiskFraction`'s leverage cap.
4. Implement the real per-position computation inside `open_position` using
   `self.average_true_range()`, gated the same way `protective_offsets`
   already gates `AtrMultiple` warm-up.
5. Add unit tests mirroring `RiskFraction`'s coverage (both the sizing
   formula and the risk-gate-widening behavior) — full `cargo test --workspace
   --exclude finance-redis` green — **before** any round runs a Docker backtest
   using this mode.
6. Only then: a `finance-research` CLI flag, a train/validation/holdout
   `one_target` sweep on `binance BTC` first (per the loop's XAU-then-BTC
   resource priority, BTC is used here because it has the deepest, gap-free
   history — Round 336 — for isolating the sizing effect from data-continuity
   confounds), sized against the deployed `equity_fraction`/`risk_fraction`
   controls.

## What is proven, and what is not

Proven (code-read, cited by file:line, no execution):

- The volatility input this mechanism needs already exists in the engine,
  computed causally, with an established warm-up-gating precedent.
- `PositionSizing`'s `notional()`/`executable_notional()` are shared by the
  live runtime's pre-trade risk gate and by every research measurement path,
  called from four production/config sites with no ledger context — this is
  documented in the code itself, including a named prior incident (Round 84)
  for exactly this class of change.

Not proven, and deliberately not claimed:

- That volatility-scaled sizing would help or hurt PnL, Sharpe, drawdown, or
  Target 3 frequency on any route — no backtest was run.
- Any concrete fallback/clamp formula — none is proposed as a number here;
  Section "Concrete next step" states what must be decided, not what to use.
- That this is architecturally harder than item 4 (cross-instrument lead-lag,
  Round 434) — it is a different kind of hard: item 4 is blocked by
  engine-wide schema/replay assumptions (`Kline` has no second-instrument
  field), this is blocked by an unresolved but boundable safety contract on
  existing shared code. This one does not need a new engine capability, only
  a justified, tested design.
