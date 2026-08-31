# Round 388 — NEEDS-MORE-RESEARCH: gold's short bias is an **entry-count** effect. Hold duration behaves the **same on every route**, so the guard and the risk layer are ruled out.

Classification: **NEEDS-MORE-RESEARCH**. **Zero containers**, from records
already held. OPS transaction unchanged, in `FINAL_VERIFY`.

## First, a correction to my own named next step

Round 387 said the next test was to read each production candidate's long/short
signal distribution "using the Alpha sweep already present in every run's
`strategy_scores`". **That data does not exist.** `strategy_scores` entries carry
only `interval`, `strategy` and per-split `trades`, `realized_pnl`,
`profit_factor`, `win_rate`, `max_drawdown`, `funding_paid` — **no side field of
any kind**. I proposed a test without checking the input was available.

## The decomposition that is available, and it localises the bias

Exposure skew factors exactly into entry count × mean duration:

| route | entries L / S | mean hold h L / S | **entry skew** | **duration skew** | exposure skew |
|---|---|---|---|---|---|
| **`exness XAU`** | 147 / 255 | 36.7 / 42.9 | **1.735×** | 1.171× | 2.032× |
| `binance BTC` | 467 / 424 | 10.1 / 14.0 | **0.908×** | 1.388× | 1.260× |
| `bybit BTC` | 491 / 360 | 10.3 / 13.6 | **0.733×** | 1.318× | 0.966× |

(Identity check: 1.735 × 1.171 = 2.032; 0.908 × 1.388 = 1.260; 0.733 × 1.318 =
0.966 — each matches the observed exposure skew exactly.)

**Duration skew is consistent everywhere: shorts are held 17–39% longer on all
three routes.** That is a shared property of the machinery and it cannot explain
a route-specific bias.

**Entry skew is where gold diverges completely.** Both BTC routes enter **long**
more often (0.908×, 0.733×); gold enters **short 1.735× more often than long**.
Gold is not "more skewed in the same direction" — it is skewed **the other way**.

**So the bias originates at entry, not in how long positions are held.** The
minimum-hold guard, which gates reversals and therefore acts on duration, is
ruled out as its source, as is anything downstream that only extends positions.

## One more observation, not attributable

`risk_rejected_counts` fires on exactly one gate everywhere — `execution_cost` —
at **118 on gold**, 63 on `binance BTC`, 39 on `bybit BTC`. Gold has 3× the
cost rejections of `bybit BTC`. The counts are **not split by side**, so this
cannot be attributed to the skew; it is recorded because gold being the extreme
on both counts is worth remembering, not because it explains anything.

## What is proven, and what is not

Proven:

- `strategy_scores` contains no side information (schema inspected).
- The entry/duration decomposition above, with the identity verified on all
  three routes, on matched pinned windows.
- Duration skew 1.171× / 1.388× / 1.318×; entry skew 1.735× / 0.908× / 0.733×.
- `execution_cost` rejection counts 118 / 63 / 39.

Not proven, and deliberately not claimed:

- **What generates the entry skew.** The decomposition says *where* the bias
  lives, not *why*. The ensemble-composition candidate from round 387 (three
  production candidates on gold against five on BTC, gold's unique extra being
  an oscillator) remains named and untested.
- That the guard is irrelevant to the result. It is ruled out as the *source of
  the side skew*; it still has the large effect on PnL measured in r371–r375.
- That two BTC routes are two observations. Same instrument, near-identical
  prices (r276) — closer to one.
- Anything from the rejection counts. Not side-split; no attribution attempted.

## Named next step, this time checked against what exists

The decision stream's side is observable in the **emitted trade records** only
after the guard and risk layer have acted. To see the *pre-guard* side
distribution, the `legacy_selected_rule` control would need its own trade export
— `--emit-trades` currently exports the guarded path only. Confirming that, and
whether the control is skewed the same way, is a **code-reading question first**:
if the legacy stream is also 1.7× short on gold, the bias is upstream in the
Alpha ensemble; if it is balanced, the Portfolio's aggregation introduces it.
