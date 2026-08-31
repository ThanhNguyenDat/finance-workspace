# Round 309 — NEEDS-MORE-RESEARCH: one threshold, two different scales. `entry_score` sums **3** intervals and `trend_score` sums **5**, so `minimum_role_score = 0.10` is a coin-flip cut on one role and a light filter on the other.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered prediction held, and the
structural finding underneath it cannot be measured further with current tooling.
**Zero containers, zero SSH**: two local code reads plus the 26 accumulated samples in
`raw/researcher/signal-state-samples.csv`.

## The question Round 308 handed forward

Round 308 closed with: *"`entry_trend_conflict` dominates the blocks, which makes it
the more interesting parameter — and it has no threshold at all, so it is a different
kind of question entirely. **Not examined.**"*

**Registered before computing:** the conflict rate is **not distinguishable from 50%**
— i.e. the two role scores' signs behave like independent coin flips. Significantly
below 50% would mean the filter is selecting genuinely aligned setups; significantly
above would mean the roles are structurally opposed.

## How the two roles are actually built

`role_scores()` (`trading_modes.rs:1042-1069`) partitions **by interval**, not by
strategy: every required interval carries an `Entry` or `Trend` tag, and the *same*
strategy set contributes to whichever role its interval belongs to. The production map
(`trading_modes.rs:477-496`) is:

| role | intervals | count | weight each |
|---|---|---|---|
| **Entry** | `5m`, `15m`, `30m` | **3** | 1/8 |
| **Trend** | `1h`, `2h`, `4h`, `12h`, `1d` | **5** | 1/8 |

`minimum_role_score` is set to `0.10` at `trading_modes.rs:501`, and is compared
against **both** sums unchanged (`:850`, `:853`).

**The two sums are not on the same scale.** With uniform 1/8 weights, a fully aligned
trend role can reach 5/3 = **1.67x** what a fully aligned entry role can. So one scalar
threshold necessarily means two different things.

## What the samples show

**Conflict rate.** 16 of 26 samples conflict (**61.5%**); on the 21 distinct
`(route, entry_score, trend_score)` states, 11 of 21 (**52.4%**). Exact two-sided
binomial against 50%: **p = 0.327** on all samples, **p = 1.000** on distinct states.

**The prediction holds: the dominant blocking condition fires at a rate
indistinguishable from a coin flip.** That is not evidence the filter is useless — it
says the two scores' *signs* carry no detectable mutual information in this sample, and
with 21 states it could not detect much.

**Scale.** The asymmetry is larger than the interval counts alone predict:

| | mean | min | max |
|---|---|---|---|
| `\|entry_score\|` | **0.1067** | 0.0090 | 0.2125 |
| `\|trend_score\|` | **0.2767** | 0.0105 | 0.7476 |

**Ratio of means 2.59x**, against a structural maximum of 1.67x, and
`|trend| > |entry|` in **21 of 26** samples. The trend aggregate is larger both because
it has more intervals *and* because its constituent signals cancel less — long-timeframe
strategies agree with one another more than short-timeframe ones do.

**So the threshold binds asymmetrically, and hard on one side.** Mean `|entry_score|` is
**0.1067 — essentially sitting on the 0.10 threshold**, so roughly half of all entry
scores fail it by construction. Mean `|trend_score|` is **2.6x above** it. Counted
directly: 8 of 26 samples are sub-threshold on entry against 6 of 26 on trend, and the
entry-side block labels outnumber the trend-side ones 7 to 4.

**Per-route conflict rate is very uneven**, though on six samples each and heavily
autocorrelated:

| route | conflicts |
|---|---|
| `exness BTC` | **0/6** |
| `exness XAU` | 0/1 |
| `binance XAU` | 4/6 |
| `bybit XAUT` | 5/6 |
| `binance BTC` | **6/6** |
| `bybit BTC` | 1/1 |

The route that never conflicts (`exness BTC`) is also the one observed passing the gate
most often. With this sample that is a coincidence worth noting, not a result.

## The design observation, recorded and not acted on

A **normalised** role score — dividing each role's sum by the number of intervals in
that role, or by the sum of its interval weights — would make `minimum_role_score` mean
the same thing for both roles. Today it does not, and the entry side absorbs almost all
of the cut.

This is **investigation only — not applied**. It is a code change in
`finance-live-action`, not Claude's to make, and it cannot be evaluated first: Round 308
established that `minimum_role_score` has no research CLI flag, and normalisation is not
a parameter at all. **No promotion:** the gate's first condition — defensible OOS,
holdout or walk-forward evidence — cannot be met for a change that cannot be simulated.

## What is proven, and what is not

Proven:

- `role_scores()` partitions by interval (`trading_modes.rs:1042-1069`); production
  assigns `5m`/`15m`/`30m` to Entry and `1h`/`2h`/`4h`/`12h`/`1d` to Trend, all at
  weight 1/8 (`:477-496`), with `minimum_role_score` = 0.10 (`:501`) compared against
  both sums unchanged (`:850`, `:853`).
- 26 samples: 16 sign conflicts (61.5%); 21 distinct states: 11 conflicts (52.4%);
  exact two-sided binomial p = 0.327 and 1.000 against 50%.
- Mean `|entry_score|` 0.1067 against mean `|trend_score|` 0.2767 — 2.59x, above the
  1.67x the interval counts alone allow; `|trend| > |entry|` in 21 of 26 samples.
- 8 of 26 samples sub-threshold on entry, 6 of 26 on trend.
- Per-route conflict counts as tabulated.

Not proven, and deliberately not claimed:

- **That `entry_trend_conflict` is uninformative.** The test says the two *signs* are
  indistinguishable from independent on **21 distinct states** — that is low power, and
  sign independence says nothing about whether the trades it blocks would have been
  profitable. That question needs a simulation I cannot run.
- That normalising the role scores would improve anything. It would make the threshold
  consistent; whether consistency helps PnL, PF, drawdown or frequency is **untested**
  and untestable with the current tool.
- That the per-route conflict split is real. Six samples per route, minutes apart, with
  repeated identical `trend_score` values — this is a description of one afternoon.
- Any Target 3 or profitability claim. Unchanged from Rounds 306-308.
- That the 2.59x scale gap is stable. It is the mean of 26 autocorrelated samples on
  five routes, and the adaptive reweighting of Round 300 moves `interval_weights` away
  from the uniform 1/8 continuously, so the structural 1.67x bound applies to the
  *initial* policy, not necessarily to the live one.
