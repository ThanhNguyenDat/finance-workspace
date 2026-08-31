# Round 374 — DATA-ISSUE: Round 373's only surviving signal is a **phantom**. `taker_base_vol` is absent on four of six routes, and the strategy silently degrades into a **permanent short that never closes**.

Classification: **DATA-ISSUE**. **Zero containers** — resolved entirely from code,
logs already held, and one narrow read-only production query. Retracts the
headline of Round 373.

## What Round 373 claimed, and what it actually measured

Round 373's conservative instrument-level test left exactly one survivor:
`taker_imbalance`, positive on both instruments, p = 0.0115. Its holdout values
were `+0.1520 / +0.2695 / +0.2700 / +0.2700` on `bybit XAUT`, `exness XAU`,
`exness BTC`, `bybit BTC` — identical across all three thresholds, which Round
373 flagged as a "degeneracy" but did not resolve.

**Those four cells have `trades = 0` in every split.** The strategy never closed
a single trade on any of those routes, and Round 373 counted its `realized_pnl`
as a positive holdout result anyway.

## The mechanism, confirmed end to end

`crates/finance-research/src/strategies.rs:246-256`:

```rust
if kline.volume <= 0.0 { return None; }
let buy_ratio = (kline.taker_buy_volume / kline.volume).clamp(0.0, 1.0);
let signal_type = if buy_ratio >= self.threshold { EnterLong }
                  else if buy_ratio <= 1.0 - self.threshold { EnterShort }
                  else { return None };
```

Production data, read-only, 5m bars over 30 days:

| broker | route | bars | `volume > 0` | `taker_base_vol > 0` | coverage |
|---|---|---|---|---|---|
| binance | BTC/USDT perp | 8,639 | 8,639 | 8,639 | **100.00%** |
| binance | XAU/USDT perp | 8,639 | 8,639 | 8,639 | **100.00%** |
| bybit | BTC/USDT perp | 8,639 | 8,639 | **0** | **0.00%** |
| bybit | XAUT/USDT spot | 8,639 | 8,620 | **0** | **0.00%** |
| exness | BTC/USD cfd | 8,638 | 8,638 | **0** | **0.00%** |
| exness | XAU/USD cfd | 5,578 | 5,578 | **0** | **0.00%** |

`volume` is populated everywhere; **`taker_base_vol` is populated only on
Binance.** So on the other four routes `buy_ratio ≡ 0`, which satisfies
`buy_ratio <= 1.0 - threshold` for **every** threshold ≥ 0.5. The strategy emits
**EnterShort on every bar, forever, identically for all three thresholds**. The
fade variant mirrors it to EnterLong.

The side therefore never changes, so **no position is ever closed**:
`trade_count` stays 0 while a single open position accrues funding for the whole
period. `settle_funding` (`crates/finance-core/src/trading_modes.rs:2067-2070`)
returns early only when there is *no* position — here there is one — and books
the accrual at `:2135`.

Verified on all **12** zero-trade split-cells: `realized_pnl == −funding_paid`
**exactly**, and the amounts are split-proportional —
`0.8100 / 0.2700 / 0.2700` = **3 : 1 : 1**, precisely the 60/20/20 split.

So the "positive holdout PnL" was funding received on a phantom perpetual short.

## Round 373's numbers, recomputed with `trades > 0` required

| | Round 373 method | `trades > 0` |
|---|---|---|
| positive holdout cells | 39 / 462 | **27 / 462** |
| families at ≥ 4 of 6 routes | 6 | 5 |
| **positive on both instruments** | **`taker_imbalance`** | **NONE** |

**The correct answer to Round 373's conservative test is NONE.** No mechanism
family is positive on holdout on both instruments once cells that never traded
are excluded. Round 373's p = 0.0115 does not describe anything.

Per-route positive counts fall 5/3/9/7/9/6 → **5/3/6/4/6/3**; the three Binance
cells are unaffected because that route has no zero-trade strategies.

## The codebase already had the right gate, and I bypassed it

`crates/finance-research/src/sweep.rs:43-46`:

```rust
pub fn survives_selection(&self) -> bool {
    [Split::Train, Split::Validation].iter().all(|split| {
        self.split(*split)
            .is_some_and(|score| score.trades > 0 && score.realized_pnl > 0.0)
    })
}
```

with the doc comment *"A candidate has to earn on data it was chosen from before
holdout is worth reading. Holdout is deliberately not consulted here."*

**`trades > 0` is already required, and holdout is deliberately excluded from
selection** — both of the errors Round 373 made. I reimplemented selection by
hand over the raw `strategy_scores` array and reproduced neither guard. That is
the finding I am least comfortable recording and the most useful one here.

## The concrete defect — not applied, investigation only

Two separable problems, neither touching live trading:

1. **Silent degradation.** A strategy whose required input is absent should be
   **excluded**, not turned into a constant-side signal. Nothing in the output
   marks these four routes' taker cells as unrunnable; they appear as ordinary
   rows with a plausible small positive number.
2. **Zero-trade rows carry non-zero `realized_pnl`.** Funding on a never-closed
   position is arguably real cash, but a row reporting `trades: 0`,
   `win_rate: null`, `profit_factor: null` and `realized_pnl: +0.27` invites
   exactly the error Round 373 made.

**No production exposure.** `production_candidates`
(`crates/finance-research/src/strategies.rs:24-78`) deploys only
`candle_momentum`, `rsi_mean_reversion` and route-specific MTF stochastic
variants — **`taker_imbalance` is never deployed on any route**, and it does not
appear in `crates/finance-api/src/deployment_rules.rs`. This is a research-sweep
measurement defect, not a trading-safety issue.

Fix direction, **not applied — investigation only**: guard the strategy (and its
fade twin) to return `None` when the taker field is absent rather than treating
absence as `buy_ratio = 0`; separately decide whether the ingestion should carry
`taker_base_vol` for bybit and exness at all. Which of those is the right minimal
change depends on whether those venues expose the field, which I have not
established.

## What is proven, and what is not

Proven:

- `taker_base_vol` coverage 100.00% on both Binance routes and 0.00% on the
  other four, over 30 days of 5m bars, while `volume` is populated everywhere.
- All five `taker_imbalance` variants report `trades = 0` in all three splits on
  those four routes, with `realized_pnl == −funding_paid` exactly in all 12
  zero-trade cells, split-proportional 3:1:1.
- Requiring `trades > 0` takes Round 373 from 39 to 27 positive cells and from
  one both-instrument family to **none**.
- `sweep.rs:43-46` already requires `trades > 0` on train and validation and
  excludes holdout from selection.
- `taker_imbalance` does not appear in `production_candidates` or
  `deployment_rules.rs`.

Not proven, and deliberately not claimed:

- **That the remaining 27 positive cells mean anything.** They are still
  selected on the holdout they are scored on (Round 373's blocker, unchanged),
  and no family survives the conservative test. This round removes a false
  positive; it does not create a true one.
- That bybit or exness *can* supply taker volume. Not checked — the query
  measures what is stored, not what the venues expose.
- That the effective sweep breadth is 72 everywhere. Five strategies are dead on
  four routes; I have not audited the other 72 for silently-degraded inputs, and
  the same failure mode could exist elsewhere.
- That funding accrual on a never-closed position is itself wrong. It may be
  correct accounting presented in a misleading row.
- Anything about Round 373's other five families beyond their recount; they were
  never the survivors of the conservative test.

## Named next step

Audit the remaining strategies for the same failure mode: for each route, count
strategies with `trades == 0` across all splits and check whether their inputs
exist in `public.klines`. That is a log-and-query round like this one, **zero
containers**, and it bounds how much of the 77-strategy sweep is actually live
on each route.
