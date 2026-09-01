# CORRECTED (Round 312)

The maturity argument here makes a corollary that **fails**: if long windows mature every
interval and return the weights to uniform, a deep-window perturbation should be
*smaller*. Round 312 measured `binance BTC` at 900/901 days and got **+50 trades from
one day** — **10x** the +5 at 260/261, and a 52x overshoot against that day's real
content. The mechanism explains why short windows over-weight long intervals; it does
**not** explain why sensitivity grows with depth, so treat it as **incomplete**. No
replacement mechanism is offered. See
`round312-REJECTED-the-confound-grows-with-depth-one-day-moves-50-trades-at-900d-and-binance-btc-straddles-the-bar.md`.

---

# Round 311 — NEEDS-MORE-RESEARCH: every strategy is a confirmed loser, so `alpha_performance_quality` reduces to **`1 − trades/20`**. The weights are a pure **trade-count** function — and that is the mechanism of the Round 300 confound.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered prediction held, and it
supplies the first *mechanistic* explanation for a confound I have only ever
demonstrated numerically. **Zero containers, zero SSH**: one local code read plus the
live weights already captured in Round 310.

## What the quality function actually computes

`alpha_performance_quality` (`trading_modes.rs:589-617`), with
`PERFORMANCE_CONFIDENCE_TRADES = 20.0` (`:431`):

```text
confidence = clamp(trade_count / 20, 0, 1)
if confidence == 0  -> return 1.0
empirical  = 0.0 unless realized_pnl > 0 && gross_profit > 0
return (1 - confidence) + confidence * empirical
```

**Every strategy on every route is a confirmed loser** — that has held across this
entire session, and `realized_pnl` was negative on all four windows in Round 305 and
all six in Rounds 306-307. So `empirical` is **exactly 0.0** everywhere, and the whole
function collapses to:

```text
quality = 1 - min(trade_count / 20, 1)      (floored at 0.05 for intervals)
```

**Performance does not enter the weighting at all.** An interval's weight is decided
**only by how many Alpha trades it has generated**, and it decreases monotonically in
that count. Zero trades earns the maximum 1.0; twenty or more earns exactly 0.0, floored
to `INTERVAL_QUALITY_FLOOR = 0.05` (`:453`).

## The live weights reconstruct exactly

Round 310 read the production weights without explaining them. On the three routes that
carry exactly two strategies, the whole vector inverts cleanly — floored intervals pin
the normalisation constant, and every other interval yields an implied trade count:

| route | `1d` | `12h` | next highest | everything else |
|---|---|---|---|---|
| `bybit BTC/USDT` | **12.9 trades** | 16.0 | — | ≥ 20 (mature) |
| `binance XAU/USDT` | **11.0 trades** | 16.0 | `4h` 17.1 | ≥ 20 (mature) |
| `bybit XAUT/USDT` | **14.7 trades** | 15.6 | `15m` 17.2 | ≥ 20 (mature) |

Each reconstruction closes to its own normalisation constant exactly (sum of raw
qualities = T on all three).

**Every up-weighted interval is up-weighted for one reason: it has not yet made 20
trades.** `1d` sits at 11-15 trades on all three, and carries **30-43%** of the total
weight. Not one of them earned it on performance — performance contributes zero by
construction.

## Why this is the Round 300 confound

Rounds 300-305 established that changing `--days` changes the decision stream, measured
it at up to −42 trades from a nine-day perturbation, and never explained *why*. This is
why.

In a replay the Alpha ledgers start **empty**, so an interval's maturity is a function
of how many bars the window gives it:

| interval | bars in a 180-day 24/7 window | minimum window to *possibly* reach 20 trades |
|---|---|---|
| `5m` | 51,840 | hours |
| `1h` | 4,320 | — |
| `12h` | 360 | **10 days of bars**, realistically far more |
| `1d` | **180** | **20 days of bars**, realistically far more |

`5m` saturates confidence almost immediately in any window and lands on the floor.
`1d` may not reach 20 trades at all — at 11-15 trades in production after months, it
plainly has not.

**So the shorter the window, the less mature the long intervals, the higher their
weight, and the more trend-dominated the decision stream.** The weight vector is a
function of window length *by construction*, and it moves in a predictable direction.
That is the mechanism, and it also explains why Round 310 found live entry:trend ratios
of 2.21x-5.96x against the uniform 1.67x: the long intervals are structurally the
immature ones.

## What this does not change

The behaviour is **already documented as deliberate**. `deployment_rules.rs:218-240`
names the `trade_count == 0 → quality = 1.0` "benefit of the doubt" rule, calls the
result "pathological", and records that the zombie `mtf_*` strategies prop up decision
frequency "by not yet having accumulated 20 role-interval evaluations". Round 310 quoted
that note for the *strategy* weights; this round shows the identical arithmetic drives
the *interval* weights, and reconstructs it numerically.

The `normalize_or_uniform_weights` comment (`:630-645`) also explains why the floor
exists: without it, a route whose strategies have all matured into confirmed losers gets
every weight at zero, `role_scores()` returns 0.0, the gate can never clear, and the
route can never decide again. The floor is a deliberate deadlock guard, not an accident.

**No promotion.** Nothing here is a defect to fix — it is a documented trade-off — and
Round 308 established the parameters cannot be simulated anyway.

## What is proven, and what is not

Proven:

- `PERFORMANCE_CONFIDENCE_TRADES = 20.0` (`trading_modes.rs:431`);
  `INTERVAL_QUALITY_FLOOR = 0.05` (`:453`); `alpha_performance_quality` returns 1.0 at
  zero trades and `(1 - confidence) + confidence * empirical` otherwise (`:589-617`),
  with `empirical` **exactly 0.0** unless `realized_pnl > 0`.
- With every strategy losing, quality reduces to `1 - min(trade_count/20, 1)` — a
  function of trade count alone, independent of performance magnitude.
- The live interval weights on `bybit BTC`, `binance XAU` and `bybit XAUT` reconstruct
  exactly from that formula, implying `1d` trade counts of 12.9, 11.0 and 14.7 and
  `12h` counts of 16.0, 16.0 and 15.6, with every other interval at or past 20.
- Bar counts per interval in a 180-day window as tabulated; `1d` cannot reach 20 trades
  in a window shorter than 20 days of bars.

Not proven, and deliberately not claimed:

- **That the implied trade counts are exact.** They are inverted from three normalised
  weight vectors under the assumption that the floored intervals are exactly at the
  floor and that all strategies on a route are losers. Both are well-supported, but the
  counts are *implied*, not read.
- That this fully accounts for the Round 300 confound's **magnitude**. It explains the
  direction and the mechanism; it does not predict −42 trades at nine days, and I did
  not attempt a quantitative model.
- That the weighting is wrong or should change. It is documented as deliberate, the
  floor is a deliberate deadlock guard, and Round 308 established that no alternative
  can be simulated with current tooling.
- Anything about the six-strategy routes (`binance BTC`, `exness BTC`). Their vectors
  were not inverted here — more free parameters, and I did not want to fit rather than
  solve.
- That `binance XAU`'s numbers mean anything about live behaviour. Its market data has
  been frozen since 2025-12-25 (Rounds 207, 306), so its ledger counts are stale by
  construction; it is included because the arithmetic closes, not as live evidence.
