# COVERAGE GAP RETRACTED (Round 406)

The gap this file names does not exist. **`mtf_stochastic_9_3_35_65_sma5_trend_filtered`
is in the sweep** (`strategies.rs:4230-4238`), built as
`StochasticStrategy::new(9, 3, 35.0, 65.0)` with trend period `5` - **identical** to
production's `mtf_stochastic_5m_4h_sma5`. The comment above it reads "further on the
already-deployed SMA5 config"; it was added to cover exactly this.

**The coverage gap is zero and there is nothing to implement.** Round 394's proposed change
and round 395's narrowed "one missing variant" are both withdrawn.

The cause was matching by production `id` rather than by constructor arguments - the very
lesson round 394 recorded and round 395 then repeated. Its holdout score is **-0.05076 over
189 trades**: negative, like every other production candidate. See
`round406-DATA-ISSUE-the-coverage-gap-is-zero-i-repeated-a-mistake-i-had-already-written-into-the-skill.md`.

---

# Round 394 — REJECTED: production's own gold candidates lose on **every** disjoint holdout. And the Portfolio layer removes **98.6%** of that loss — it is not the problem.

Classification: **REJECTED** — production's deployed candidates are
indistinguishable from the library base rate. **Zero containers**, from runs
already held.

## A lookup error of mine, caught and corrected mid-round

My first attempt reported that **none** of production's three gold candidates
appear in the 75-strategy sweep, and would have concluded the two sets are
disjoint. That was wrong: I searched by production's `id` strings while the
sweep uses parameterised labels. Verified against `strategies.rs`:

| production (gold) | sweep label | match |
|---|---|---|
| `candle_momentum`, `minimum_move: 0.001` | `candle_momentum_10bps` = `CandleMomentumStrategy::new(0.001)` | **exact** |
| `rsi_mean_reversion`, 14 / 30 / 70 | `rsi_mean_reversion_14_30_70` | **exact** |
| `mtf_stochastic_5m_4h_sma5` | — | **absent; the sweep has no `mtf_` entries at all** |

Two of three are testable. I did **not** report the vacuous "0 of 0" my broken
lookup produced.

## The test

Re-registered for the six cells actually available (2 candidates × 3 disjoint
holdouts), **before reading any outcome** — only the cell count changed:

- **≥ 3 of 6** → beats the library base rate. Null (p = 0.076): **0.0074**.
  Power against a coin-flip effect: **0.656**.

| production candidate | H1 | H2 | H3 |
|---|---|---|---|
| `candle_momentum` (0.001) | −21.08420 / 3262 | −23.23038 / 3184 | −11.27030 / 1561 |
| `rsi_mean_reversion` (14/30/70) | −6.56068 / 819 | −5.35702 / 784 | −6.13148 / 809 |

**0 of 6 positive.** Expected under the library base rate: 0.46. **Consistent
with it** — production's candidates are not better than a random library member,
and they are not measurably worse either.

They lose on **every** out-of-sample period, at scale: `candle_momentum` loses
−0.00646 per trade across 3,262 holdout trades.

## The number that reframes the arc

On H1's holdout, the two production Alpha candidates together lose **−27.64488
across 4,081 trades**. The Portfolio, fed by them, loses **−0.377343 across 160
trades**.

| | Alpha inputs | Portfolio output | change |
|---|---|---|---|
| total loss | −27.64488 | −0.37734 | **−98.6%** |
| trades | 4,081 | 160 | −96.1% |
| **per trade** | −0.006774 | −0.002358 | **−65.2%** |

**The Portfolio layer removes 98.6% of the loss it is handed, and it improves
per-trade economics by 65% — not only by trading less.** Both axes.

So the conclusion 60 rounds of Portfolio-knob search was circling is the
opposite of what the search assumed. **The Portfolio layer is not where the
problem is.** It is doing substantial, measurable work. It starts from inputs
that lose money on every out-of-sample period tested, and the best any selector
can do with such inputs is lose less.

## What is proven, and what is not

Proven:

- The parameter identity of two production gold candidates with two sweep
  entries, read from `strategies.rs`.
- Their holdout results on three disjoint periods: 0 of 6 positive.
- The H1 Alpha-to-Portfolio comparison: −27.64488/4081 → −0.377343/160.
- The sweep contains no `mtf_` entries, so production's third gold candidate has
  no analogue in the research library.

Not proven, and deliberately not claimed:

- **That production's candidates are worse than the library.** 0 of 6 against an
  expectation of 0.46 is consistent with the base rate, not below it.
- **That the Portfolio layer "works".** It reduces a loss; it does not create a
  gain, and r391/r392 showed its own gross edge does not replicate. "Not the
  problem" is not "the solution".
- That the 98.6% figure generalises. One route, one holdout, two of three
  inputs — and the third, untestable one also feeds the Portfolio, so the
  comparison omits part of what it actually consumed.
- Anything about `mtf_stochastic_5m_4h_sma5`. It is deployed on gold and has
  never been scored by any research round in this arc.

## Named next step

The untested production candidate is the gap worth closing: `mtf_stochastic_5m_4h_sma5`
is deployed on gold and has **no** research coverage. Adding the three
production MTF configurations to `candidates()` is a small, well-scoped change
that would let the sweep score what is actually running — and it is the first
change this arc has identified whose value does not depend on finding edge.
