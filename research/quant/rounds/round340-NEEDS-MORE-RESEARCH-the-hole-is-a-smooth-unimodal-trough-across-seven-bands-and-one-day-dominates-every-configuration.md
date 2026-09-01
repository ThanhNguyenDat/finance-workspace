# STRUCTURAL, BUT ONLY WITHIN THIS WINDOW (Round 341)

This file concluded *"the feature is structural, and the deployed band sits on its floor."*
That needs narrowing. The smooth unimodal shape does establish the trough is **not
configuration noise within its window** — that argument stands. It does **not** establish that
the trough is a stable property of the route: at `--days 300` the 0.0125-versus-0.02 gross gap
collapses from **0.3272 to 0.0476**, and both bands turn negative. Read "structural" as
"structural within this window".

Round 340's other results are unaffected: the daily-array findings (the 37/101 invariance is
coincidence; one day dominates every band) hold, and Round 341 extends the second to **every
route measured** — including the finding that `2026-06-10` is the **best** day on `exness XAU`
while it is the worst on `bybit XAUT`. See `round341-REJECTED-the-trough-does-not-replicate-on-a-different-window-and-single-day-dominance-is-general-with-gold-inverting-between-venues.md`.

---

# Round 340 — NEEDS-MORE-RESEARCH: the "hole" is a **smooth unimodal trough** across seven bands, not a sharp hole — which makes it much harder to dismiss. And **one calendar day, 2026-06-10, is the worst day at every band measured**, worth 3.6x the entire net loss of the best configuration.

Classification: **NEEDS-MORE-RESEARCH** — the feature is now well characterised, still
unexplained, still not actionable. Two bounded Docker sweeps (exactly the 2-container budget)
plus **zero-container** analysis of the `daily_results` arrays already saved from Rounds 338
and 339. **XAU-first**, on the gate-eligible route.

## Pre-registration, and a defect in it

Round 339 established a low-gross region at 0.01-0.0125 on `bybit XAUT` and said its edges were
*"where the grid stops"*. Two containers at 0.009 and 0.015 probe those edges.

**Pre-registered:** the hole is narrow → 0.009 returns gross **≥ +0.15** and 0.015 returns
gross **≥ +0.15**. Refuted if either returns **≤ +0.1**.

**That pre-registration is defective and I am recording it as such.** The interval
`(+0.1, +0.15)` was assigned to **neither** branch, and 0.015 landed inside it at **+0.1414**.
This is the third pre-registration defect in this loop — Round 327 registered an uncomputed
p-value, Round 330 registered a bound on the wrong variable, and this one leaves a gap between
the confirm and refute regions. The fix is the same each time: state the criterion as a
partition, not two separate inequalities.

## The seven-band picture — a smooth trough, not a hole

`bybit XAUT/USDT` spot, `--days 500`, identical holdout (2026-05-22 → 2026-08-30, 28,799
candles, 101 observed days), no continuity failures on any run:

| band | trades | tr/wk | **gross** | cost drag | per-trade cost | net | Sharpe | streak |
|---|---|---|---|---|---|---|---|---|
| 0.005 / 0.01 | 148 | 10.36 | **+0.2662** | 1.0998 | 0.00743 | −0.8336 | −3.074 | 5 |
| 0.008 / 0.016 | 84 | 5.88 | **+0.2518** | 0.7047 | 0.00839 | −0.4529 | −1.655 | 13 |
| **0.009 / 0.018** | 70 | 4.90 | **+0.1561** | 0.7139 | 0.01020 | −0.5578 | −1.893 | 13 |
| 0.01 / 0.02 **(deployed)** | 64 | 4.48 | **−0.0135** | 0.4069 | 0.00636 | −0.4204 | −1.397 | 13 |
| 0.0125 / 0.025 | 48 | 3.36 | **−0.0682** | 0.3162 | 0.00659 | −0.3843 | −1.279 | 13 |
| **0.015 / 0.03** | 41 | 2.87 | **+0.1414** | 0.2719 | 0.00663 | −0.1305 | −0.397 | 13 |
| 0.02 / 0.04 | 28 | 1.96 | **+0.2590** | 0.3185 | 0.01137 | −0.0595 | −0.171 | 21 |

Read down the gross column: **0.2662 > 0.2518 > 0.1561 > −0.0135 > −0.0682 < +0.1414 <
+0.2590.** Perfectly unimodal, with a single minimum at 0.0125 and **monotone shoulders on both
sides**.

**That changes the reading.** Round 339 called it a narrow hole with edges at grid resolution;
with the shoulders filled in it is a **smooth trough**, and the descent into it and the climb
out of it each pass through intermediate values in order. Configuration noise does not produce
a monotone descent across three points followed by a monotone ascent across three more. The
feature is structural, and the deployed band sits on its floor.

## A standing approximation that breaks at this resolution

Rounds 274 onward have used "cost scales with trade count". Per-trade cost across these seven
bands runs **0.00636 to 0.01137 — a 1.8x spread**, and it is not monotone in band width
(0.009 costs 0.01020 per trade on 70 trades while 0.008 costs 0.00839 on 84).

The proportionality is a **useful approximation, not an identity**, and conclusions that depend
on cost differences smaller than ~2x per trade should not lean on it. This does not disturb the
earlier findings, which turned on 2-5x frequency changes.

## Zero-container result 1 — the 37/101 invariance is coincidence, not identity

Round 339 flagged that 0.008, 0.01 and 0.0125 returned **identical** positive-day ratios
(37/101) at 84, 64 and 48 trades, and noted the daily array had not been inspected. It has now
been inspected — the arrays were already in the saved run output, so this cost nothing.

**The day sets are different.** 0.008 and 0.0125 share only **29** of their 37 positive days
(Jaccard 0.644). Across the four bands analysed, pairwise Jaccard runs 0.481-0.689, 23 days are
positive on all four and 35 are negative on all four.

**So the invariance is a coincidence in the count, not the same days recurring.** Round 339's
open question is closed, and it closes as the less interesting of the two possibilities.

## Zero-container result 2 — one day dominates every configuration

**`2026-06-10` is the single worst day at all six bands measured** — −0.2184, −0.1854, −0.2054,
−0.2069, −0.1634, −0.2134 — regardless of band width, trade count or frequency.

| band | net | worst day | worst-day PnL | net excluding it | worst day as share of net loss |
|---|---|---|---|---|---|
| 0.005 | −0.8336 | 2026-06-10 | −0.2184 | −0.6152 | 26.2% |
| 0.008 | −0.4529 | 2026-06-10 | −0.1854 | −0.2675 | 40.9% |
| 0.0125 | −0.3843 | 2026-06-10 | −0.2069 | −0.1774 | 53.8% |
| 0.02 | −0.0595 | 2026-06-10 | −0.2134 | **+0.1539** | **358.6%** |

At the best-net band, **that one day is 3.6x the entire net loss**, and the remaining 100 days
sum to positive.

**This is a statement about concentration, not about profitability.** A configuration is not
profitable because its worst day can be removed — the day is in the sample, the loss is real,
and any route whose result hinges on one session out of 101 is carrying tail risk that the
gate's Sharpe and Sortino numbers are correctly punishing. What it does say is that **this
route's holdout verdict is dominated by a single session**, and that the protective band —
whose whole purpose is bounding per-position loss — did not bound it at any width tested.

## What is proven, and what is not

Proven:

- `bybit XAUT` @500, identical holdout, no continuity failures: 0.009/0.018 → 70 trades / 4.900
  per week / gross +0.15606 / cost 0.71386 / net −0.55781 / Sharpe −1.8931 / Sortino −2.4731 /
  streak 13; 0.015/0.03 → 41 / 2.870 / +0.14140 / 0.27191 / −0.13051 / −0.3974 / −0.6032 /
  streak 13.
- The seven-band gross sequence is unimodal with its minimum at 0.0125 and monotone shoulders.
- Per-trade cost across the seven bands spans 0.00636-0.01137 and is not monotone in band width.
- 0.008 and 0.0125 share 29 of 37 positive days; pairwise Jaccard across four bands is
  0.481-0.689; 23 days positive and 35 negative on all four.
- 2026-06-10 is the worst day at all six bands, and at 0.02/0.04 it is 358.6% of the net loss.

Not proven, and deliberately not claimed:

- **Any cause for the trough.** Seven points characterise its shape and nothing explains it. I
  have no mechanism, and "the shape is smooth" is evidence that it is real, **not** evidence of
  what produces it.
- **That excluding 2026-06-10 makes any configuration profitable.** It does not; the day
  happened. That row is a concentration measurement and must not be quoted as a PnL result.
- **What happened on 2026-06-10.** I did not query market data for that session. Whether it was
  a gap, a spike, a liquidity event or an ordinary day that several positions happened to close
  into is **unknown**.
- That the trough or the single-day dominance appears on any other route or window. **One
  route, one window.** `exness XAU`'s refined grid over the same band range (Rounds 334-335)
  shows no trough, but it is a different instrument, venue and gross regime, so it is not a
  control.
- Any promotion. Every band on this route loses money, and the pre-registration defect above
  means this round's edge probe was weaker than intended.
