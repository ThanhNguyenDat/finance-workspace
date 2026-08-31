# QUALIFICATION (Round 232)

Two adjustments, in opposite directions:

1. **The aggregate finding is confirmed and sharpened.** Pooling twelve
   configurations gives expected 34.19 against observed 53 — ratio **1.55**,
   **z = 3.22**. The lift is small but statistically distinguishable from chance,
   so the population does carry a real persistence signal.
2. **The claim that 'exness BTC 4h+1d at 2.10x is where the signal lives' is
   withdrawn.** The same configuration across brokers, windows and partitions
   spans **0.37 to 2.73** — a 7.3x spread — and 2.10 has z=2.01 while the highest
   z (3.47) belongs to binance 900d 40/20/40, the window where Round 225 measured
   the best candidate collapsing. No configuration can be ranked.

See `round232-the-persistence-signal-is-small-but-real-and-cannot-rank-configurations.md`.

---

# Round 231 — The three-split bar produces only ~1.4x more survivors than chance, and in two runs fewer

Classification: **NO-CHANGE**. No containers — computed from seven saved sweeps.

## The question nobody asked in 230 rounds

The program's central filter is "PF > 1 on all three splits". Rounds 210-230
measured that per-split PF is noisy, that spreads are wide, and that the
conjunction is robust *because* it is a conjunction. What was never measured is
the obvious one: **how many candidates would clear it by chance?**

For each sweep: take the observed per-split pass rate, multiply the three, and
compare the implied count against the observed count.

| run | N | p train | p val | p hold | expected | observed | obs/exp |
|---|---|---|---|---|---|---|---|
| exness XAU 4h 1800d | 77 | 0.195 | 0.247 | 0.351 | 1.30 | 2 | 1.54 |
| exness XAU 4h+1d 1800d | 107 | 0.206 | 0.252 | 0.421 | 2.33 | 2 | **0.86** |
| exness XAU 5m 365d | 77 | 0.091 | 0.091 | 0.078 | 0.05 | 1 | *20.17* |
| exness BTC 4h+1d 1800d | 107 | 0.318 | 0.299 | 0.327 | 3.33 | 7 | **2.10** |
| binance BTC 4h+1d 1800d | 107 | 0.364 | 0.290 | 0.355 | 4.01 | 5 | 1.25 |
| bybit BTC 4h+1d 1800d | 107 | 0.318 | 0.290 | 0.308 | 3.04 | 5 | 1.65 |
| binance BTC 4h+1d 900d | 107 | 0.271 | 0.252 | 0.364 | 2.67 | 1 | **0.37** |
| **total** | | | | | **16.73** | **23** | **1.38** |

The 5m row's 20.17 is not evidence of anything: it is one observed survivor
against an expectation of 0.05, and a single count over a near-zero expectation
has no resolution. Excluding it: expected 16.68, observed 22, **1.32x**.

**Two runs produce fewer survivors than chance** (0.86 and 0.37).

## What this means, stated carefully

The independence assumption is the crux and it cuts one way.

Splits of the same series under the same strategy are **not** independent. A
strategy with persistent edge passes all three *because* the edge persists, which
creates positive dependence and pushes observed above expected. So obs/exp is a
direct measure of how much persistence the population carries — and **1.38x is
the entire persistence signal across seven sweeps and roughly 700
candidate-evaluations.**

If the candidate space held many genuinely persistent strategies, this number
would be 5x or 10x, not 1.38x.

So the conclusion is not "the bar is broken". The bar is doing what a conjunction
does. The conclusion is:

> **The candidate population is overwhelmingly composed of strategies whose
> per-split outcomes are close to independent — which is what a population with
> no persistent edge looks like. The conjunction has almost nothing to find.**

## This explains the whole session

Every strong-looking result in Rounds 222-230 followed the same arc: clear the
bar, then fail the next independent test.

- Round 224's `candle_momentum_rv_regime_filter` cleared on exness, inverted on
  binance and bybit.
- Round 225's cross-broker survivor cleared three brokers and a repartition, then
  failed the 900-day window.
- Round 229's MTF family looked best-ever on one split; Round 230 found −1.954 on
  the adjacent one.

At 1.38x lift, that is the expected behaviour of bar survivors, not a run of bad
luck. They were mostly chance survivors, and each additional independent test
removed them at roughly the rate chance predicts.

The one run that stands out is **exness BTC 4h+1d at 2.10x** — the highest
legitimate value in the table and the run that produced the cross-broker
survivor. Weak, but it is where the little signal there is lives.

## What this does not license

It does not license lowering the bar. A filter that admits chance survivors at
1.38x lift becomes worse, not better, if loosened — the correct response to a
weak filter is more independent tests, which is what Rounds 224-226 did and what
correctly rejected the candidate.

It also does not mean the measurements were wasted. Knowing the lift is 1.38x is
what makes the rejection pattern interpretable rather than dispiriting.

## What is proven, and what is not

Proven:

- Per-split pass rates and observed/expected counts for seven sweeps as tabulated.
- Total observed 23 against 16.73 expected under independence, 1.38x; 1.32x
  excluding the near-zero-expectation 5m row; two runs below 1.

Not proven, and deliberately not claimed:

- That obs/exp is a calibrated statistic. It is a ratio of counts with no
  confidence interval; the per-run values range 0.37-2.10 and several rest on
  single-digit observed counts.
- That no candidate has edge. 1.38x is a population statement; it does not
  identify or exclude any individual.
- That the multiplication is exact. Per-split pass rates are estimated from the
  same 77-107 candidates being tested, so expected and observed are not fully
  independent quantities.
