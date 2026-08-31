# SCOPE NARROWED (Round 408)

This file's coverage claim describes `production_candidates` in `crates/finance-research` -
which is a **research-side mirror** called only from the research CLI (`main.rs:617`, `:678`).
**No live code calls it.** The live binary is `finance-api`, whose strategy set comes from
`deployment_rules::configured_alpha_strategies`.

**The two have drifted.** On `binance BTC` and `exness BTC` the live configuration carries a
**seventh** strategy the mirror does not: `mtf_stochastic_4h_1d_sma50` (k14, d3, 30/70, trend
50, base **4h** / higher **1d**). Confirmed in live trade payloads, whose
`contributing_strategies` list **six** names on both BTC routes against the mirror's five.

So "six of six, coverage complete" is true **of the mirror**. Production runs **seven**
distinct configurations, and the seventh has never been scored at its own intervals - every
MTF run in this arc used `5m`/`4h`. `exness XAU` is unaffected: both definitions give three.
See
`round408-DATA-ISSUE-the-research-mirror-has-drifted-from-the-live-configuration-production-runs-a-seventh-strategy-nobody-has-scored.md`.

---

# Round 406 — DATA-ISSUE: the coverage gap is **zero**. I repeated, in round 395, the exact mistake I had written into the skill in round 394.

Classification: **DATA-ISSUE** — a correction to my own rounds 394 and 395.
**Zero containers**, from runs already held.

## The mistake

Round 394 concluded production's gold candidate "has no analogue in the research
library" and proposed a code change. Round 395 narrowed that to "one missing
parameter variant" and still called it a real gap.

**`mtf_stochastic_9_3_35_65_sma5_trend_filtered` is in the sweep.**
`strategies.rs:4230-4238`:

```rust
Labelled::new(
    "mtf_stochastic_9_3_35_65_sma5_trend_filtered",
    Box::new(MultiTimeframeTrendFilterStrategy::new(
        base_interval, higher_interval,
        Box::new(StochasticStrategy::new(9, 3, 35.0, 65.0)),
        5,
    )),
),
```

Production's gold config is `k_period: 9, d_period: 3, oversold: 35.0,
overbought: 65.0, trend_period: 5`. **Identical.** The comment directly above the
sweep entry reads *"further on the already-deployed SMA5 config"* — it was added
precisely to cover it.

**The coverage gap is zero. There is nothing to implement.** Round 394's proposed
change is fully retracted.

Worse than the wrong conclusion: after round 394 I wrote into the skill *"Match
production strategies to sweep entries by PARAMETER, not by id."* In round 395 I
matched by name again, found no `mtf_stochastic_5m_4h_sma5`, and concluded a gap
existed. **I recorded the lesson and then repeated the mistake in the very next
round.**

## All six production candidates, measured

Holdout 2026-03-04 → 2026-08-31:

| production config | `exness XAU` | `binance BTC` |
|---|---|---|
| `candle_momentum` (10bps) | −21.08420 / 3262 | — |
| `rsi_mean_reversion` (14/30/70) | −6.56068 / 819 | — |
| **`mtf_stochastic` sma5** *(gold prod)* | **−0.05076 / 189** | −2.12836 / 300 |
| `mtf_stochastic` sma10 *(BTC prod)* | −1.32247 / 140 | **−0.92104 / 192** |
| `mtf_macd` 5/13/5 sma10 *(BTC prod)* | −1.56472 / 140 | −1.50073 / 192 |
| `mtf_candle_momentum` sma10 *(BTC prod)* | −0.96677 / 122 | −0.53536 / 180 |

**Every measured cell is negative.** Coverage of production by the research sweep
is complete, and nothing production runs is profitable on this holdout.

## The first production choice this arc has found to be right

Production uses **trend-5 on gold** and **trend-10 on BTC**. On this holdout:

| core (k9 d3 35/65) | on `exness XAU` | on `binance BTC` |
|---|---|---|
| trend **5** | **−0.05076** | −2.12836 |
| trend **10** | −1.32247 | **−0.92104** |

**Production's route-specific choice is the better of the two on both routes** —
by 26× on gold and 2.3× on BTC. The trend period is also a large lever generally:
within the stochastic family, variants differing only in trend period span
**1.27 to 1.51** in holdout PnL.

Under a coin flip, getting both routes right is p = 0.25 — **not significant**,
and it is one holdout. But it is the first configuration decision in this arc
that verifies rather than failing to.

## What is proven, and what is not

Proven:

- The sweep entry's constructor arguments match production's gold config exactly.
- The six-row table above; every measured cell negative.
- Within the stochastic family, trend-period-only variants span 1.27–1.51 in
  holdout PnL.
- Production's trend choice is the better of the two tested on both routes.

Not proven, and deliberately not claimed:

- **That production's configuration is good.** Its candidates all lose; the
  trend choice is merely the better of two losing options.
- That the trend result generalises. **One holdout**, two routes, two values of
  one parameter. p = 0.25 under chance for the pair.
- That the sweep covers production on all six routes. The two generic candidates
  and the four MTF configs are all present; I have not enumerated whether any
  route carries a candidate I have not looked for — which is exactly the failure
  mode of this round.

## Named next step

None from this thread — coverage is complete and the answer is uniform. The
standing constraint holds: everything actionable is blocked on the release
decision, on a definition for Target 2, or on forward time.
