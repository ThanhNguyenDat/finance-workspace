# Round 375 — REJECTED: Alpha-input count **does not** explain the guard advantage. The fleet-complete record is **5 of 6 routes positive**, and the sweep's effective breadth is **71–74, not 77**.

Classification: **REJECTED** — a pre-registered prediction failed on the one
route never used to form it. **Zero containers** — code reading plus logs
already held. Executes the audit Round 374 named.

## Registered question 1 — is the taker failure bounded?

Round 374 found five `taker_imbalance` strategies silently degraded into a
permanent short on four routes, and named the audit: does the same failure mode
exist elsewhere? Registered: other all-split-zero-trade strategies → the mode is
broader than Round 374 assumed; only the taker family → Round 374's scope is
complete.

| route | ids | dead (0 trades, all splits) | thin (<20 holdout) | phantom PnL | live |
|---|---|---|---|---|---|
| `binance BTC` | 77 | **0** | 0 | 0 | 77 |
| `binance XAU` | 77 | **0** | 6 | 0 | 77 |
| `bybit XAUT` | 77 | 5 | 2 | 5 | 72 |
| `exness XAU` | 77 | 5 | 2 | 5 | 72 |
| `exness BTC` | 77 | 5 | 1 | 5 | 72 |
| `bybit BTC` | 77 | 5 | 0 | 5 | 72 |

**Exactly five strategies, exactly the taker family, exactly the four
non-Binance routes. Nothing else has zero trades anywhere.** Round 374's scope
is complete.

## The contamination risk that does not exist

The 77-strategy sweep and the Portfolio replay are fed from **different**
strategy sets: `crates/finance-research/src/main.rs:629-630` builds
`candidates()` for `strategy_scores` and `production_candidates(&instrument)`
for the Portfolio, and `:573` uses `production_candidates` again for the replay.

**The dead taker strategies never reach the Portfolio.** Every Portfolio
measurement in this arc is unaffected by Round 374's defect. This was a real
risk — five permanently-short signals feeding the Portfolio on four routes would
have contaminated forty rounds of measurements — and it is ruled out by the call
sites, not by assumption.

## A second degeneracy, provable from the code

`min_strength_0_5 / 0_7 / 0_9_keltner_reversion_20_2_5` return **byte-identical
splits on all six routes** — including Binance, so this is not a data gap.

`strategies.rs:1152-1165`: the strategy emits a signal only when
`kline.close <= channel.lower` or `kline.close >= channel.upper`, and then sets

```rust
let strength = ((kline.close - channel.middle).abs() / half_width).min(1.0);
```

A band breach means `|close − middle| ≥ half_width`, so the ratio is ≥ 1 and
**`strength` is identically 1.0 for every signal this strategy ever emits**.
`MinStrengthFilterStrategy` drops signals with `strength < min_strength`
(`:3561`), so for any threshold ≤ 1.0 it **drops nothing**. Three sweep entries
are one behaviour, by construction.

The wrapper is not broken in general: on `heikin_ashi_momentum` the same three
thresholds give three distinct behaviours (88 / 38 / 21 holdout trades on
`binance BTC`). It is a no-op **specifically when the inner strategy's entry
condition saturates its own strength metric** — a failure mode that could exist
in other wrapper/strategy pairs and has not been audited.

**Effective sweep breadth**, distinct split-signatures out of 77 ids:

| routes | distinct | collapsed |
|---|---|---|
| both Binance | **74** | 3 |
| the other four | **71** | 6 |

Round 373's family collapse to 62 was more aggressive than either figure, so its
corrected verdict of **NONE** is unaffected.

## Registered question 2 — does Alpha-input count explain the guard advantage?

`production_candidates` (`strategies.rs:24-118`) gives the Portfolio a
**route-dependent** number of Alpha inputs: `candle_momentum` and
`rsi_mean_reversion` everywhere, plus three MTF variants on `binance BTC` and
`exness BTC`, plus one on `exness XAU`, plus **nothing** on the other three.

| route | Alpha inputs |
|---|---|
| `binance BTC`, `exness BTC` | 5 |
| `exness XAU` | 3 |
| `binance XAU`, `bybit XAUT`, `bybit BTC` | **2** |

A 2.5× spread — and the only route with a **negative** guard advantage
(`binance XAU`, r372) is a 2-input route, while the largest measured advantage
was on a 5-input route. That is a hypothesis, so I registered it on the five
routes already measured and tested it on **`bybit BTC`, which had never had its
advantage computed**:

> if input count drives the advantage, `bybit BTC` (2 inputs) should land
> **below** the 3- and 5-input routes (+68.7%, +51.3%, +28.7%). Above → refuted.

**`bybit BTC`: +56.9%. Above two of the three. The hypothesis is refuted.**

The groups overlap badly: 2-input routes span **−31.9% to +56.9%**; 3-and-5-input
routes span **+28.7% to +68.7%**.

## The fleet-complete guard advantage

| route | Alpha inputs | `one_target` | `legacy` | advantage | % of loss |
|---|---|---|---|---|---|
| `exness XAU` | 3 | −0.70835 | −2.25984 | +1.55149 | **+68.7%** |
| **`bybit BTC`** | 2 | −3.76933 | −8.74651 | +4.97718 | **+56.9%** |
| `binance BTC` | 5 | −4.81958 | −9.90557 | +5.08599 | **+51.3%** |
| **`exness BTC`** | 5 | −4.84586 | −6.79682 | +1.95096 | **+28.7%** |
| `bybit XAUT` | 2 | −2.03343 | −2.49876 | +0.46533 | **+18.6%** |
| `binance XAU` | 2 | −1.44149 | −1.09279 | −0.34870 | **−31.9%** |

**Five of six production routes positive, one negative** — the settled version of
r371/r372, at the deployed configuration on one window per route. `exness BTC`
and `bybit BTC` are measured here for the first time.

## What is proven, and what is not

Proven:

- Exactly 5 strategies have zero trades in all splits, on exactly the four
  non-Binance routes; no other strategy does, on any route.
- `main.rs:573` and `:629-630` feed the Portfolio from `production_candidates`
  and `strategy_scores` from `candidates()` — disjoint paths.
- `min_strength` cannot filter `keltner_reversion`: entry requires a band
  breach, which forces `strength = 1.0` (`strategies.rs:1152-1165`, `:3561`).
- Effective breadth 74/77 on Binance routes, 71/77 on the other four.
- The six-route advantage table above; `bybit BTC` +56.9% against a registered
  prediction of "below +28.7%".

Not proven, and deliberately not claimed:

- **That input count is irrelevant.** Refuted as *the* explanation on six routes,
  one window, one configuration each. A weaker contribution is not excluded and
  is not tested by this design.
- That anything explains the advantage. Round 372 refuted trade frequency
  (ρ = +0.143); this round refutes input count. **No mechanism is offered and
  two candidates are now eliminated.**
- That 5/6 positive means the guard is generally beneficial. One window per
  route, in-sample, `legacy` is a control rather than a deployable alternative,
  and the negative route is the one with the least data (r372).
- That other wrapper/strategy pairs are sound. Only `min_strength` × two inner
  strategies was checked; the saturating-strength failure mode is unaudited
  elsewhere.
- Anything about the 71–74 breadth figure's effect on Round 373. It is *less*
  conservative than the 62-family collapse already applied there, so it changes
  nothing — it does not rehabilitate any result.

## Named next step

Audit the remaining wrapper/strategy pairs for the saturating-strength no-op:
for every wrapped strategy, check whether its entry condition forces the metric
its wrapper filters on. That is a code-reading round, **zero containers**, and it
bounds how much of the sweep's apparent breadth is real.
