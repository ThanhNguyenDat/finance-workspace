# Round 398 — NEEDS-MORE-RESEARCH: pooled gross across seven disjoint holdouts is **not distinguishable from zero**. The frequency tradeoff is directionally present but at **p = 0.13** — and I chose that threshold knowing its null was 13%.

Classification: **NEEDS-MORE-RESEARCH**. **Zero containers**, from holdouts
already measured.

## The measured version of "alternates around zero"

Seven disjoint holdout gross readings — four on `exness XAU` (r391/r392), three
on `binance BTC` (r397):

`+0.66471, −0.72458, +0.29154, −0.11094, −0.58685, +0.82128, +0.26947`

**Mean +0.08923, sd 0.59160, se 0.22360. Approximate 95% interval
[−0.34903, +0.52749] — includes zero.**

Every previous statement of this was qualitative ("the shape of noise",
"alternates around zero"). This is the number, and it says the pooled gross edge
across seven genuinely out-of-sample periods **cannot be distinguished from
nothing**. The interval is also wide enough to admit an edge of ±0.5, so it does
not establish absence either.

## The tradeoff test, and the threshold I should not have accepted

The arc's most-repeated claim — profitability and trade frequency trade off
(r363, r367) — was established entirely on **full-window, in-sample parameter
sweeps**, where frequency was moved deliberately. These seven holdouts vary
frequency **naturally**, at a fixed configuration, which is a different and
stronger test.

| holdout | trades/wk | net PnL |
|---|---|---|
| `exness XAU` H4 | 1.963 | −0.37140 |
| `exness XAU` H3 | 2.176 | **+0.00095** |
| `exness XAU` H2 | 3.020 | −1.20812 |
| `binance BTC` H2 | 4.200 | **+0.00025** |
| `binance BTC` H3 | 4.900 | −0.15914 |
| `exness XAU` H1 | 6.232 | −0.37734 |
| `binance BTC` H1 | 7.661 | −1.77712 |

**Spearman ρ = −0.5000**, landing exactly on the registered threshold. Exact
permutation p (all 5,040 permutations) = **0.1333**.

I computed that null **before** running and registered the threshold anyway,
because at n = 7 the alternatives were worse: ρ ≤ −0.714 gives p = 0.044 but
costs most of the power. **Choosing a criterion with a 13% false-positive rate
and then reporting "the criterion was met" would be misleading**, so I am not
reporting it that way.

**The tradeoff is directionally present and not established.** One shuffling in
seven produces this or stronger.

What the table does show without any test: **the two least-negative results
(+0.00095 and +0.00025) sit at 2.176 and 4.200 trades/week, and the two worst
(−1.20812, −1.77712) sit at 3.020 and 7.661.** The worst result is the busiest
holdout; the best two are not the quietest.

## What is proven, and what is not

Proven:

- The seven-holdout gross series, its mean +0.08923 and 95% interval
  [−0.34903, +0.52749].
- Spearman ρ(trades/week, net) = −0.5000 with exact permutation p = 0.1333.
- The frequency/net table above.

Not proven, and deliberately not claimed:

- **That there is no gross edge.** The interval includes zero *and* includes
  ±0.5. Seven observations cannot separate those.
- **That the frequency tradeoff holds out of sample.** ρ = −0.50 at p = 0.13 is
  a direction, not a result, and I am recording my own threshold choice as the
  weakness it is — the ninth pre-registration issue in this arc, and the first
  where the null was simulated correctly and the threshold was simply too
  permissive for the sample size available.
- That the seven holdouts are independent. Two routes, and within each route the
  fitted history up to each cutoff overlaps. The interval and the permutation
  test both assume more independence than the data has, so both are optimistic.
- That r363/r367's in-sample tradeoff is wrong. It is measured differently and
  this does not contradict it; it fails to confirm it out of sample.

## Named next step

n = 7 is the binding constraint on every question left, and it grows only by
running more disjoint holdouts on the four untested routes — about two rounds
for six or seven more points. That would tighten the interval by roughly a third
and take the permutation test to a usable p-range. **It is the only remaining
backtest work that would change what can be said**, and it is worth doing only
if a fleet-level statement about gross edge matters more than the current
answer, which is "not distinguishable from zero on the two routes measured".
