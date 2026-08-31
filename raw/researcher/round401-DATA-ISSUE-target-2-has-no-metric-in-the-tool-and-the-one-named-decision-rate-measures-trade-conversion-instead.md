# Round 401 — DATA-ISSUE: **Target 2 has no metric in the tool.** The one named `decision_rate` measures trade conversion instead, and it is absent from the holdout report entirely.

Classification: **DATA-ISSUE**. **Zero containers**, from runs already held.

## Why this round exists

The standing objective names **three** things to optimise jointly:
profitability, **Make Decision rate**, and trade frequency. I have written
`target2_makedecision: n/a` in roughly sixty rounds of CSV **without ever
establishing why**. This round establishes it.

## What `decision_rate` actually is

Verified exactly on every current-build run: **`decision_rate` =
`trades` ÷ `decision_count`.**

| run | candles | decisions | trades | `decision_rate` | decisions/candle |
|---|---|---|---|---|---|
| `exness XAU` @08-31 | 174,254 | 165,689 | 402 | 0.002426 | 0.951 |
| `exness XAU` @03-04 | 173,939 | 165,885 | 279 | 0.001682 | 0.954 |
| `exness XAU` @09-04 | 174,498 | 166,162 | 215 | 0.001294 | 0.952 |
| `binance BTC` @08-31 | 259,201 | 258,914 | 891 | 0.003441 | 0.999 |
| `bybit BTC` @08-31 | 259,201 | 258,914 | 851 | 0.003287 | 0.999 |

That is **trade conversion** — what fraction of decision cycles ends in a trade.
It is **not** decision production: **~95% of closed gold bars and ~99.9% of BTC
bars already yield a decision record**, the overwhelming majority of them Hold.

So the quantity the objective calls "Make Decision rate" — how often the
Portfolio produces an *actionable* decision — is **not** what the field named
`decision_rate` reports.

## And it is absent from the holdout report

`decision_rate` appears on the **non-gate** `one_target` block only. The gate's
`metrics` block does not contain it (checked: `'decision_rate' in metrics` is
False, and it appears nowhere else in the gate report).

**So the nearest available proxy for Target 2 has no holdout measurement path
at all** — full window only, on the report that is not holdout-restricted.
Targets 1 and 3 are both measurable on holdout; Target 2 is not measurable on
holdout even by proxy.

## What the numbers do show

BTC converts decisions into trades at roughly **1.4×** gold's rate (0.00344 and
0.00329 against 0.00243). And gold's conversion **falls by half going back in
time**: 0.002426 → 0.001682 → 0.001294 across three disjoint windows — the same
frequency trend round 392 measured in trades/week, expressed as a ratio and
therefore not explained by window length.

## An error of mine, caught by an assertion

My first pass flagged `binance XAU` as reporting `decision_rate: None` despite
having 134 trades and 75,482 decisions, which would have been a real defect.
It is not: that log is from **round 372**, before the measurement change, and
its `one_target` block has only the four original fields. The key was **absent**,
not null. The assertion caught a genuine inconsistency in my data; investigating
it resolved to a stale log rather than a bug, and I am recording that rather
than quietly dropping the row.

## What is proven, and what is not

Proven:

- `decision_rate == trades / decision_count` exactly, on all five current-build
  runs.
- Decisions per candle 0.951–0.954 on `exness XAU`, 0.999 on both BTC perps.
- `decision_rate` is present on the non-gate `one_target` and absent from the
  gate report.
- Gold's trade conversion across three disjoint windows: 0.002426, 0.001682,
  0.001294.

Not proven, and deliberately not claimed:

- **What "Make Decision rate" should mean.** Rounds 265–270 measured
  `gate_passed` against blocked reasons from live logs, which is one plausible
  definition, but **choosing a definition is not mine to do** — picking one and
  then reporting against it would be inventing the target rather than measuring
  it.
- That the absence from the gate is a defect rather than a deliberate omission.
  The gate scores what its thresholds cover, and there is no Target 2 threshold
  in `thresholds`; adding a metric without a criterion would not make the target
  measurable in the sense that matters.
- That BTC's higher conversion means anything. Two routes of one instrument
  against one route of another, one window each for the BTC pair.
- That the conversion trend is independent evidence. It is the round 392
  frequency trend recomputed on the same runs, not a second observation.

## Named next step

Target 2 needs a **definition** before it needs a metric, and that is a decision
for whoever set the objective, not something a research round should settle.
Until then the honest record is `n/a` **with this reason attached**, rather than
`n/a` unexplained — which is what the last sixty rounds recorded.
