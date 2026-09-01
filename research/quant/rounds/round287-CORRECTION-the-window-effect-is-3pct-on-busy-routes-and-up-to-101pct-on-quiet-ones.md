# Round 287 — CORRECTION: the window effect is 3-5% only on the busiest routes. On quiet routes it is 43% and 101%.

Classification: **REJECTED** — my pre-registered band and Round 286's "safe by margin"
reasoning both fail. Two bounded Docker sweeps (exactly the 2-container budget).

## Measuring what Round 286 admitted it had only argued

Round 286 closed by conceding that the three wide Target 3 failures were measured on
**one window each**, and that calling them safe because their margins exceed a 3-5%
window effect was *"an argument, not a measurement."* This round measures the two XAU
failures (XAU-first priority).

The prediction and its criteria were on disk before launch (`precommit_r287.md`):
**binance XAU inside 3.2-4.1/week, bybit XAUT inside 2.2-2.7/week.**

| route | 260d | second window | result | **shift** | in predicted band | Target 3 |
|---|---|---|---|---|---|---|
| binance XAU/USDT | 3.63 | 180d ¹ | **2.06** | **−43.2%** | **NO** | FAIL |
| bybit XAUT/USDT | 2.42 | 360d | **4.86** | **+100.9%** | **NO** | FAIL |

¹ `binance XAU`'s klines begin 2025-12-11 (~262 days), so a *longer* window does not
exist — the second window had to be shorter. A data limit, not a choice.

## Both predictions missed, and badly

`bybit XAUT` **doubled**. `binance XAU` fell by nearly half. My band assumed the 3-5%
effect Round 286 measured; the real effect on these routes is **43% and 101%**.

| route | trades in the smaller window | window effect |
|---|---|---|
| exness BTC | 481 | −4.6% |
| binance BTC | 459 | −5.3% |
| exness XAU | 254 | +3.2% |
| **binance XAU** | **53** | **−43.2%** |
| **bybit XAUT** | 250 | **+100.9%** |

**Round 286's 3-5% figure was generalised from the two highest-frequency routes and
does not hold on quiet ones.** I made that generalisation and used it to argue three
routes were safely classified; the argument is refuted.

## What survives and what does not

**The FAIL verdicts survive.** Neither route came near 7/week on either window
(2.06-3.63 and 2.42-4.86), and my pre-registration named "reaching 7/week" as the
picture-changing outcome. It did not happen.

**The margins do not survive.** Round 285's table records `bybit XAUT` at −65% below
the bar; on the 360-day window it is **−31%**. The pass/fail split holds for these two
routes; the *distances* quoted alongside it are unreliable on low-frequency routes and
should not be read as measures of confidence.

**Round 286's safety argument is withdrawn.** `bybit BTC` — the narrowest failure at
−21%, and still on **one window** because two containers cannot cover three routes —
is now the least secure verdict in the table, not a safe one. A +101%-class swing
would clear the bar.

## What is proven, and what is not

Proven:

- `binance XAU` 53 trades / 2.06 per week at 180 days (per-trade −0.01434);
  `bybit XAUT` 250 trades / 4.86 per week at 360 days (per-trade −0.00357).
- Window effects of −43.2% and +100.9%, against −4.6%/−5.3%/+3.2% on the three
  higher-frequency routes.
- Both routes fail Target 3 on both windows measured.

Not proven, and deliberately not claimed:

- **That `bybit BTC` would survive a second window.** It is untested and is now the
  verdict I would trust least. That is the next round's obvious target.
- That the effect is *caused* by low trade counts. The correlation with trade count is
  clean across five routes, but `bybit XAUT` had 250 trades — comparable to
  `exness XAU`'s 254, which moved only 3.2%. So trade count alone does not explain it.
- That either route's true rate is any of these numbers. Two windows per route bracket
  2.06-3.63 and 2.42-4.86; that is the honest range, not a point estimate.
- That Round 285's pass/fail split is wrong. It is not challenged here — only the
  margins beside it, and only on the quiet routes.
