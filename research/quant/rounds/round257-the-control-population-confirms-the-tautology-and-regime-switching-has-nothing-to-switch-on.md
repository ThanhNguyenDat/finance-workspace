# Round 257 — The control population moves the opposite way (+1.000 vs −0.900), and regime switching has nothing to switch on

Classification: **REJECTED** — the regime-switching follow-up is rejected, and the
tautology reading of Rounds 255-256 is confirmed against a **pre-committed** control
population. Two bounded Docker sweeps (XAU), one read-only Timescale query.

## The gap Round 256 named

Round 256 closed with: *"the tautology reading fits and is the simplest
explanation, but 'trending markets favour trend-following' was not independently
tested here against a non-trend-following control population."*

If the reading is right, the prediction is sharp and falsifiable: the trend group's
`|drift| → edge` correlation is positive (established, +0.857 on both instruments),
and a **counter-trend** group's must be **negative**. If the counter-trend group
also came out positive, the finding would be about the bands, not about trend
following, and the tautology reading would be wrong.

**The grouping was written to disk before any sweep was launched this round**
(`precommit_groups.json`, committed at iteration 52 with the prediction stated),
specifically so the assignment could not be tuned to the outcome. Two mechanisms
were excluded there as **arithmetic mirrors** — `candle_reversion` is the exact
negation of `candle_momentum`, `taker_imbalance_fade` of `taker_imbalance` — since
their correlation is forced by construction and is not evidence.

## Result — the two populations move in opposite directions

exness XAU 4h, five contiguous 150-day bands (B3-B7), zero cost, mechanisms with
≥30 trades in **all five** bands:

| group | n | B3 | B4 | B5 | B6 | B7 | ρ vs \|drift\| | perm p |
|---|---|---|---|---|---|---|---|---|
| \|drift\| | | 9.03% | 26.72% | 19.62% | 19.63% | 6.90% | | |
| **trend-following** | 6 | +0.00115 | +0.01134 | +0.00304 | +0.00987 | −0.00017 | **+1.000** | **0.0167** |
| **counter-trend (genuine)** | 3 | −0.00014 | −0.01246 | −0.01124 | −0.00394 | +0.00419 | **−0.900** | 0.0833 |
| other (no prediction made) | 3 | −0.00098 | +0.00775 | +0.01299 | +0.00661 | −0.00149 | +0.700 | 0.2333 |

**The trend group is perfectly monotone in |drift| — ρ = +1.000, the maximum
attainable on five points (p = 0.0167). The genuine counter-trend group is
ρ = −0.900, the opposite sign and nearly as clean.**

The counter-trend group's edge is **negative in four of five bands**, and its single
positive band is **B7 — the lowest-|drift| band in the set**. Reversion mechanisms
lose in trending bands and earn only in the quiet one. That is the exact mirror of
the trend story, from an independent population that is not an arithmetic negation
of it.

The pre-committed prediction is confirmed. **The band effect is a restatement of
how much the instrument trended**, and Rounds 242-255's fourteen-round hunt for a
"favourable window" was tracking that and nothing else.

## The obvious follow-up, and why it dies immediately

Two complementary populations — one earning in trending bands, one in quiet bands —
invites a regime-switching Portfolio: run trend mechanisms when the market trends,
reversion mechanisms when it does not.

That requires knowing the **next** band's trend magnitude. It does not persist:

| | \|drift\|(t) → \|drift\|(t+1) | Spearman | Pearson | perm p |
|---|---|---|---|---|
| XAU | | −0.314 | −0.052 | 0.564 |
| BTC | | −0.143 | −0.325 | 0.803 |

**Both non-significant and both negative on both instruments.** A regime switcher
at this horizon has nothing to switch on — it would be choosing its population from
a variable that carries no information about the period it would be trading.

This is the same wall Rounds 255 and 256 hit from the other side: the relationship
is strong, replicated, mechanistically explained, and **entirely contemporaneous**.

## Where the thread stands

The Round 242-255 direction is closed, and now so is its most natural extension:

- the "favourable window" is trend magnitude (Rounds 255-256, ρ = +0.857 on two
  instruments, Fisher p = 0.0048);
- it is magnitude, not direction (Round 256, signed drift +0.143 on the instrument
  that can separate them);
- it is a restatement of what trend-following *means* — confirmed here against a
  pre-committed control that moves the opposite way;
- nothing forecasts it one band ahead, and neither does the regime variable a
  switcher would need.

Nothing here changes the standing result that loss ≈ trade count × a near-constant
and that no Portfolio-construction lever improves per-trade economics. Every figure
is zero-cost and gross.

## What is proven, and what is not

Proven:

- Group assignment and prediction were written to disk before any sweep ran this
  round.
- XAU B3-B7 band drifts reproduce Round 255's values exactly (+9.03%, +26.72%,
  +19.62%, +19.63%, −6.90%) from an independently launched pair of runs.
- Trend group (n=6) ρ = +1.000 vs |drift|, perm p = 0.0167; genuine counter-trend
  group (n=3) ρ = −0.900, perm p = 0.0833; counter-trend edge negative in 4 of 5
  bands with its only positive band the lowest-|drift| one.
- `|drift|` does not persist band to band: XAU −0.314 (p = 0.56), BTC −0.143
  (p = 0.80).

Not proven, and deliberately not claimed:

- Significance for the counter-trend group. **p = 0.0833 is not significant**, and
  with five bands the floor is 0.0167 — the result is the sign and the magnitude of
  ρ, not a p-value.
- That the two groups are independent tests. They share the same five bands and one
  price path, and a counter-trend population is loosely the complement of a trend
  one even when it is not an arithmetic negation. This is a **consistency check on
  a pre-committed prediction**, not a second independent confirmation.
- That three counter-trend mechanisms are a representative control. Only
  `rsi`, `stochastic` and `engulfing_pattern` cleared ≥30 trades in all five bands;
  `rsi_mean_reversion` did not.
- That regime switching fails at every horizon. It was tested at the **150-day band
  horizon only**. A shorter regime horizon was not examined and is not ruled out —
  though nothing in Rounds 249-257 suggests it would behave differently.
- One instrument. BTC was not re-run for the control test; the budget went to
  getting five contiguous XAU bands rather than three on each.
