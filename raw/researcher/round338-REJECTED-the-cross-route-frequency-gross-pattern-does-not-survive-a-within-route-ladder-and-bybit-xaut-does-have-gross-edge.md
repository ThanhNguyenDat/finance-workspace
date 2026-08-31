# GROSS SIGN IS WINDOW-SCOPED (Round 341)

This file corrected round 337's "only `exness XAU` has positive gross" by measuring **+0.2662**
and **+0.2590** on `bybit XAUT`. At `--days 300` both bands tested on that route measure
**negative** gross (−0.1757 and −0.1282). So the gross *sign* on this route is
window-dependent, and neither round 337's claim nor this file's correction of it is a stable
statement about the route. The measurements here stand for their window. See `round341-REJECTED-the-trough-does-not-replicate-on-a-different-window-and-single-day-dominance-is-general-with-gold-inverting-between-venues.md`.

---

# DIP IS REAL, NOISE READING WITHDRAWN (Round 339)

This file called the deployed band's gross of −0.0135 *"consistent with configuration-level
noise of order ±0.28"* and noted no repeat measurement had been run. The neighbours have now
been measured: **0.008/0.016 returns +0.2518 but 0.0125/0.025 returns −0.0682**. **Two
adjacent bands sit at roughly zero gross**, bracketed by +0.25 to +0.27 on both sides — noise
does not produce two adjacent low readings between three high ones.

The ±0.28-noise reading is **withdrawn**. `bybit XAUT` has a narrow **0.01-0.0125 hole** where
its gross edge collapses, and the deployed production band is inside it. This does **not**
change this file's conclusions: gross is still flat across the frequency range outside the
hole, and moving out of it does not improve net (tightening to 0.008 recovers +0.265 gross and
adds +0.298 cost). See `round339-NEEDS-MORE-RESEARCH-the-gross-dip-at-the-deployed-band-is-real-not-noise-and-production-sits-inside-a-narrow-hole.md`.

---

# Round 338 — REJECTED: the cross-route "gross falls with frequency" lead **does not survive** a within-route ladder on a gate-eligible route. Gross is flat at **+0.26 across a 5.3x frequency range** — and `bybit XAUT` does have a gross edge, which Round 337 got wrong by measuring one band.

Classification: **REJECTED** — Round 337's lead is refuted on its own terms, and one of that
round's statements is corrected. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**, on the gate-eligible route.

## The test Round 337 named and could not run

Round 337 recorded a cross-route pattern — gross +0.7820 at 6.85/week, −0.0135 at 4.48,
−1.7909 at 21.84, −2.1476 at 24.58 — and flagged it as a lead only, noting that *"testing it
needs a within-route design on a gate-eligible route, which no round has run yet"* and that it
was already **contradicted** by Round 328's within-route ladders.

`bybit XAUT` is that route: gate-eligible (zero gaps on all eight intervals, Round 337) and
XAU exposure. Two containers move the band in both directions from deployed.

**Pre-registered:** gross at both 0.005/0.01 and 0.02/0.04 stays within **[−0.3, +0.3]** —
i.e. roughly flat, Round 328's reading. **Refuted** if gross moves with frequency beyond that
band, which would give the Round 337 lead within-route support.

## Result — flat, and the prediction holds

`bybit XAUT/USDT` spot, `--days 500`, identical holdout (2026-05-22 → 2026-08-30, 28,799
candles, 101 observed days), no continuity failures on any run:

| band | trades | tr/wk | **gross** | cost drag | net | Sharpe | Sortino | pos-day | **streak** | cost÷gross |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.005 / 0.01 | 148 | **10.36** | **+0.2662** | 1.0998 | −0.8336 | −3.074 | −3.631 | 0.386 | **5** | 4.131 |
| 0.01 / 0.02 (deployed) | 64 | 4.48 | −0.0135 | 0.4069 | −0.4204 | −1.397 | −1.965 | 0.366 | 13 | 30.24 |
| 0.02 / 0.04 | 28 | **1.96** | **+0.2590** | 0.3185 | **−0.0595** | −0.171 | −0.265 | 0.406 | **21** | 1.230 |

**Gross is +0.2662 at 10.36/week and +0.2590 at 1.96/week — a 2.8% difference across a 5.3x
frequency range.** Both inside the pre-registered band. The Round 337 cross-route pattern gets
**no within-route support**, and Round 328's flat-gross reading is reconfirmed on a second
route, this time a gate-eligible one.

The remaining variation is a **dip at the deployed band** (−0.0135), non-monotone and sitting
between two nearly identical values. That is the shape of configuration-level noise of order
±0.28, not of a frequency law.

## The correction this forces on Round 337

Round 337 concluded: *"`exness XAU` is the only route with a positive gross edge."* That was
measured at **one band per route**. On this route, two of three bands give gross **+0.26**;
only the deployed band gives ≈ 0. **`bybit XAUT` does have a gross edge, and Round 337's
"only" is wrong.**

The structural point Round 337 built on that sentence survives in weakened form: every
gate-eligible route measured still fails the gate, and the largest positive gross found
anywhere remains `exness XAU`'s +0.78 — but "the only route with an edge" was an artifact of
single-band sampling, and I am withdrawing it.

## The joint-objective finding worth more than either of the above

Read across the three gate dimensions at once, the bands are in direct conflict:

- **Net is best at 0.02/0.04** (−0.0595, cost÷gross 1.23, Sharpe −0.171) — the only
  configuration on this route within striking distance of break-even.
- **That same band is the worst on frequency** (1.96/week against a 7.0 bar — it misses by
  3.6x) **and the worst on streak** (**21 consecutive negative days** against a threshold of
  5).
- Streak worsens **monotonically as frequency falls**: 5 → 13 → 21 at 10.36 → 4.48 → 1.96 per
  week.

**So on this route the net-best configuration is simultaneously the frequency-worst and the
streak-worst**, and there is no setting of this lever that improves one without destroying the
other two. That is a cleaner statement of the joint-objective conflict than Round 328's, which
was about Target 1 against Target 3 only.

## What is proven, and what is not

Proven:

- `bybit XAUT` @500, identical holdout, no continuity failures: 0.005/0.01 → 148 trades /
  10.360 per week / gross +0.26620 / cost 1.09978 / net −0.83358 / Sharpe −3.0743 / Sortino
  −3.6308 / streak 5; 0.02/0.04 → 28 / 1.960 / +0.25903 / 0.31852 / −0.05950 / −0.1710 /
  −0.2650 / streak 21.
- Gross differs by 2.8% across a 5.3x frequency range on this route.
- `maximum_negative_day_streak` is monotone increasing as frequency falls across the three
  bands.
- Two of three bands on `bybit XAUT` have positive gross.

Not proven, and deliberately not claimed:

- **That gross is frequency-independent as a law.** Two routes (Round 328's and this one),
  one window each. What is established is that the cross-route pattern has **no within-route
  support on the route where it could be tested**.
- That the deployed band's −0.0135 is noise. It is *consistent* with noise of order ±0.28
  given its neighbours; I ran no repeat measurement and cannot separate noise from a genuine
  local dip.
- That `bybit XAUT`'s +0.26 gross is stable. **One window.** Rounds 331-334 showed band
  optima moving with the window on the other route, and nothing here tests that.
- That the streak monotonicity is causal. Fewer trades over a fixed 101-day holdout changes
  how days are classified, and I did not inspect the daily classification to separate a
  mechanical effect from a behavioural one.
- Any promotion. The best net on this route is −0.0595 at 1.96 trades/week with a 21-day
  losing streak — worse on the joint objective than the deployed setting, not better.
