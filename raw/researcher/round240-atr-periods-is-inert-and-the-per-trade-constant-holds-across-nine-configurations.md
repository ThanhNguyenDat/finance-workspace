# Round 240 — `--portfolio-atr-periods` varied at last and found inert, closing the last open Rule 1 item; and the per-trade constant now holds across nine configurations

Classification: **NO-CHANGE**. Two bounded Docker sweeps.

## The last open Rule 1 item

The backlog has carried `--portfolio-atr-periods` as "the one genuinely open item
in Rule 1" for many rounds, at low priority because production uses `fractional`.
Round 239 ran ATR at periods 14 only and left the period itself untested.

The model built over Rounds 236-239 makes a prediction here: varying a protective
parameter should change **trade count** but not the **per-trade constant**.

exness XAU/USD 5m, 1,800 days, `one_target`, hold 36, `atr_multiple` 2.0/4.0:

| atr_periods | trades | trades / week | PnL | PnL per trade |
|---|---|---|---|---|
| 7 | 1,443 | 5.61 | −9.743 | −0.00675 |
| 14 | 1,433 | 5.57 | −9.459 | −0.00660 |
| 28 | 1,409 | 5.48 | −8.917 | −0.00633 |

**The parameter is inert on both axes.** Trade count moves 1.02x across a 4x
change in period; per-trade loss moves 6.3%, inside the 14% band. The trend is
monotone and tiny — a longer ATR window gives marginally fewer and marginally
better trades.

Honest note on what this tests: the model predicted "count moves, constant does
not". The constant indeed did not move, but the **count barely moved either**, so
this is a weak confirmation rather than a strong one. What it does settle is the
backlog item: **`atr_periods` is not a lever**, and it can stop being listed as
open.

## The complete per-trade constant, nine configurations

Every Portfolio-layer measurement from Rounds 236-240:

| configuration | trades | PnL | **PnL per trade** |
|---|---|---|---|
| BTC hold=36, fractional | 3,825 | −28.183 | −0.00737 |
| BTC hold=144, fractional | 1,793 | −12.204 | −0.00681 |
| XAU hold=12, fractional | 907 | −6.121 | −0.00675 |
| XAU hold=36, fractional (production) | 830 | −5.262 | −0.00634 |
| XAU fractional 0.005/0.010 | 831 | −5.293 | −0.00637 |
| **XAU fractional 0.020/0.040** | 275 | −2.876 | **−0.01046** |
| XAU atr 2/4 p7 | 1,443 | −9.743 | −0.00675 |
| XAU atr 2/4 p14 | 1,433 | −9.459 | −0.00660 |
| XAU atr 2/4 p28 | 1,409 | −8.917 | −0.00633 |

Across all nine, trade counts span **275 to 3,825 — a 13.9x range**.

- All nine: per-trade loss spans −0.00633 to −0.01046, a 39.5% spread.
- **Excluding the single configuration that moved it** — fractional 0.020/0.040,
  the wide fixed stop from Round 238 — the other eight span **−0.00633 to
  −0.00737**, a **14.1% band**, mean **−0.00666**, standard deviation **0.00032**.

**Two instruments, two brokers, hold 12 to 144, three protective mechanisms, ATR
periods 7 to 28, and a 13.9x range in trade count — and the loss per trade is
−0.0067 ± 5% in eight of nine cases.**

One lever out of five moved it, and that one made it **65% worse**.

## What this settles

The Portfolio-construction search is complete for the levers this program has.
Every configuration reachable through hold, protective kind, protective width and
ATR period produces the same per-trade loss, and total loss follows trade count
almost mechanically. Round 239's marginal-equals-average result explains why:
there is no subset or configuration of trades whose economics differ.

The remaining ways out are outside this layer entirely — a different Alpha signal
with genuinely positive per-trade edge (Rounds 231-232 measured the population's
persistence at ~1.5x chance), or lower real friction (Rounds 213-215 measured the
available cost levers as worth approximately nothing). Neither is a Portfolio
parameter.

## What is proven, and what is not

Proven:

- exness XAU 5m, atr_multiple 2.0/4.0: periods 7 / 14 / 28 give 1,443 / 1,433 /
  1,409 trades and −9.743 / −9.459 / −8.917.
- Per-trade loss across those three: −0.00675 / −0.00660 / −0.00633, a 6.3%
  spread.
- Across nine Portfolio configurations spanning 13.9x in trade count, eight sit in
  a 14.1% per-trade band (mean −0.00666, sd 0.00032); the ninth is the wide fixed
  stop at −0.01046.

Not proven, and deliberately not claimed:

- That this is a strong test of the model. The lever moved neither quantity, so it
  confirms weakly; the strong tests remain Rounds 237 (hold) and 239 (ATR adding
  trades).
- That the constant holds outside the measured envelope. Nine points, one interval
  (5m), one window per instrument.
- Anything about ATR on BTC, or about multiples other than 2.0/4.0.
