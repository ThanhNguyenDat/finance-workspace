# THE GENERALISATION FAILS FOR THE FRACTIONAL BAND (Round 364)

This file's measurement stands — an **ATR** band A/B at @360 giving per-trade −0.00712 against
−0.00663, a ratio of **0.93x**. What fails is the generalisation drawn from it: *"what survives any
calibration is the per-trade constant."*

On a validity-gated same-window test (`exness XAU` @300, hold 36, `candle_count` 57,934 both), the
**fractional** band 0.01/0.02 → 0.02/0.04 gives per-trade **−0.005824 → −0.002181**, a ratio of
**0.37x** — trades are **62.5% better**, while funding per trade rises 47%. The gain is
**quality**, not count. See `round364-REJECTED-per-trade-economics-are-not-constant-across-band-settings-the-wide-band-trades-62-percent-better.md`.

---

# CORRECTION (Round 285)

This file recorded `exness XAU` at **7.06 trades/week — "passes Target 3 by 0.9%"** on
a 360-day window. On a matched 260-day window it measures **6.84/week — fails by
2.3%**.

**The verdict flips with the observation window.** This file flagged the margin as
razor-thin; it is thin enough that "pass" is not a stable property of the route.
Neither number is wrong — the correct statement is that `exness XAU` sits **on the
threshold**, and this file's single measurement should not be quoted as a verdict.

Everything else here stands: the ATR A/B (2.43x frequency, 2.27x loss, per-trade 0.93x)
was run on one window with only the band changed, and that comparison is unaffected.
See `round285-the-complete-fleet-target3-table-two-of-six-pass-and-exness-xau-flips.md`.

---

# Round 274 — The ATR band does raise frequency (2.43x), and buys it at 2.27x the loss because per-trade economics are unchanged. Rejected.

Classification: **REJECTED** — the ATR band works as a frequency lever and is not
worth using. Two bounded Docker sweeps (exactly the 2-container budget).

## The question Round 273 flagged

Round 273 closed the "dormant route" thread with a scaling law (hold ∝ 1/σ²) and
flagged one consequence: under a **fixed fractional** band, a route's frequency is
largely set by its volatility, so low-volatility instruments structurally undershoot
Target 3. Rounds 81-82 rejected ATR-scaled bands **on cross-broker PnL grounds**;
the same lever as a **frequency** question was never examined.

Controlled A/B on `exness XAU/USD`, 5m, 360 days, `minimum_hold_decisions 36`,
identical in every respect except the protective band, read from **`one_target`** —
the only Portfolio-faithful measurement (Round 82).

| band | trades | **/week** | realized_pnl | **pnl/trade** | trade_reduction |
|---|---|---|---|---|---|
| fractional 0.01 / 0.02 (deployed) | 363 | **7.06** | −2.5832 | **−0.00712** | 0.195 |
| ATR 1.5x / 3.0x, 14 periods | 883 | **17.17** | −5.8573 | **−0.00663** | 0.612 |

## Result — it works, and that is exactly why it is useless

**Frequency: 2.43x** (7.06 → 17.17/week, comfortably clear of the 7/week bar).
**Loss: 2.27x** (−2.58 → −5.86).
**Per trade: 0.93x — essentially unchanged** (−0.00712 → −0.00663).

The ATR band raises frequency **only by taking more of the same losing trades**. The
per-trade constant sits at −0.0071 and −0.0066, straddling the long-standing −0.0068
that Rounds 234 and 96 established, and the total loss tracks the trade count almost
exactly (2.43x trades, 2.27x loss).

This is the standing result reproduced as a controlled experiment: **loss ≈ trade
count × a near-constant, and no Portfolio-construction lever moves the constant.**
Rounds 80 and 83 improved Target 1 precisely because they *reduced* trades; this
lever does the opposite and pays for it proportionally.

Round 273's flagged question is therefore answered and closed: **ATR is a working
frequency lever and a losing trade, and it reinforces the Rounds 81-82 rejection from
an independent direction.**

## An operational number worth recording

The deployed fractional configuration produces **7.06 trades/week** on `exness XAU`
over 360 days from `one_target`. Target 3's bar is 7/week. **The margin is 0.9%** —
thinner than Round 92's ~7.2-7.3/week estimate, and this is the more authoritative
measurement (`one_target`, 360 days, deployed parameters).

## What is proven, and what is not

Proven:

- The A/B table above: 363 vs 883 trades, −2.5832 vs −5.8573, on an identical window
  and configuration differing only in the protective band.
- Per-trade cost 0.93x between the two bands, against a 2.43x frequency change.
- Deployed configuration yields 7.06 trades/week on this route by `one_target`.

Not proven, and deliberately not claimed:

- **That this compares ATR against fractional at matched barrier width.** It does
  not. 1.5x/3.0x ATR is evidently a *narrower* band than 1%/2% on this instrument —
  that is why frequency rose. A wider multiple would land closer to the fractional
  rate. What survives any calibration is the per-trade constant: **frequency bought
  by re-widening or re-narrowing the band is paid for proportionally**, and that is
  the finding.
- That ATR would behave the same on other routes. **One instrument.** Rounds 81-82
  found ATR's PnL effect *inverted* between Binance and Exness, so cross-broker
  behaviour here is specifically not assumed.
- That 7.06/week is `exness XAU`'s live rate. It is a 360-day backtest under deployed
  parameters; Round 259's live window still cannot settle Target 3.
- That the ATR periods or multiples chosen are optimal. They were picked to preserve
  the deployed 1:2 stop/take ratio, not tuned — and tuning them to maximise frequency
  would only enlarge the loss.
