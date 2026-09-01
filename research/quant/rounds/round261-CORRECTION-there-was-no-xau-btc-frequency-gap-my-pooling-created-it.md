# Round 261 — CORRECTION: there is no XAU/BTC frequency gap to explain. My own pooling in Rounds 259-260 created it.

Classification: **REJECTED** — the hypothesis' operational conclusion fails, and so
does its premise. Read-only production evidence. **Zero containers.**

## The question, and the pre-committed hypothesis

Round 260 closed with: *"The XAU/BTC gap is now known **not** to be market hours.
Nothing here says what it is."*

The hypothesis, and its falsifiable predictions, were **written to disk before any
trade history was pulled** (`precommit_r261.md`, iteration 56): the deployed
protective band is *fractional* and identical on every route (STOP 0.01 / TAKE
0.02, confirmed live in Round 259), while BTC is ~2.4x as volatile per bar as XAU
— so a band fixed in price fraction takes longer to reach on XAU, closing fewer
positions for a purely structural reason.

- **P1** — XAU median hold > BTC median hold, by roughly the inverse volatility
  ratio (~2.4x).
- **P2** — XAU shows a higher share of closes that did *not* hit stop or take.
- **P3** — if P1 and P2 hold, the frequency gap follows from the one-size band.

Evidence: the `paper-backtest-fixed-pct` ledgers, which carry the **complete
trade history with entry and exit timestamps** — 392 trades on exness XAU and 473
on binance BTC, each spanning ~361 days.

## P1 — partially confirmed, and weaker than predicted

| | exness XAU | binance BTC | ratio |
|---|---|---|---|
| median hold | **8.46 h** | **6.17 h** | **1.37x** |
| mean hold | 19.17 h | 10.96 h | 1.75x |
| p75 hold | 21.92 h | 13.58 h | 1.61x |
| median 4h volatility | 0.433% | 1.036% | predicted **2.39x** |

The direction is right and the magnitude is **clearly short** of what the
volatility ratio predicts — 1.37x against 2.39x. P1 is partially confirmed and I
am not rounding it up.

## P2 — strongly confirmed

| close reason | exness XAU | binance BTC |
|---|---|---|
| stop_loss | 32.1% | 59.0% |
| take_profit | 20.4% | 27.1% |
| **target_flat (band not hit)** | **47.4%** | **14.0%** |

**Nearly half of XAU's trades never reach the protective band; on BTC it is one in
seven.** The fixed fractional band is far less binding on the quieter instrument.
This is a real structural difference in *how* trades close, and it is the one part
of the hypothesis that survives cleanly.

## P3 — refuted, because the premise is false

Over their own ~1-year spans:

| route | trades | span | **closes / week** |
|---|---|---|---|
| exness XAU | 392 | 361 d | **7.60** |
| binance BTC | 473 | 362 d | **9.14** |

**A ratio of 1.20x — not the ~3x gap Rounds 259 and 260 spent two rounds
characterising.** And the live counts are ordinary draws from these rates:
exness XAU expected 2.09 and observed 1 (P(X≤1) = 0.38); BTC pooled expected 7.52
and observed 10 (P(X≥10) = 0.23). Neither is remotely extreme.

There was no gap to explain. P3 is withdrawn along with the question it answered.

## Where the false gap came from — my own pooling

| route | lifetime trades |
|---|---|
| exness BTC | 485 |
| binance BTC | 479 |
| exness XAU | **395** |
| bybit BTC | 316 |
| binance XAU | **8** |
| bybit XAUT | **3** |

Rounds 259 and 260 pooled the three XAU routes against the three BTC routes. But
the "XAU pool" mixed **one mature route** (395 lifetime trades, comparable to every
BTC route) with **two near-dormant ones** (8 and 3 lifetime trades). Pooling a
mature route with two that have barely traded in their lifetimes produces a low
average that describes nothing.

**That pooling was mine, in both rounds, and it was wrong.** Round 260 even
computed an exposure correction for it and reported that the gap "survives the
correction essentially intact" — which was true and beside the point, because the
gap was compositional, not exposure-related. Correcting the denominator could
never have found that; only looking at the routes separately does.

The rule this earns: **before pooling routes, check that they are comparable on
lifetime activity, not only on exposure.** Equal observation time does not make a
dormant route and a mature route poolable.

## The consequence for Target 3

On the long run, both mature routes are **above** the 7/week bar:

| route | closes/week | margin over Target 3 |
|---|---|---|
| exness XAU | 7.60 | **+8.6%** |
| binance BTC | 9.14 | +30.6% |

This is the **opposite** of what the live XAU point estimate suggested, and XAU's
7.60/week sits right on top of Round 92's backtest figure of ~7.2-7.3/week over 18
months — an independent agreement from a different data path.

Rounds 259 and 260 were right to refuse a Target 3 verdict. The reason turns out
to be stronger than their confidence intervals: the pooled XAU rate they were
declining to call was not measuring what its label said.

## What is proven, and what is not

Proven:

- Hold-time distributions and close-reason splits above, from complete
  ~1-year trade histories (392 and 473 trades).
- Long-run rates 7.60/week (exness XAU) and 9.14/week (binance BTC), ratio 1.20x.
- The live 46.1-hour counts are consistent with those rates (p = 0.38 and 0.23).
- Lifetime trade counts per route, showing `binance XAU` at 8 and `bybit XAUT` at 3.

Not proven, and deliberately not claimed:

- That the long-run rates are *live* rates. These are the `paper-backtest-*` seed
  ledgers — the same strategy and configuration, a full year, but **backtest**.
  The live window is still 46 hours and still cannot settle Target 3.
- **Why `binance XAU` and `bybit XAUT` are near-dormant.** 8 and 3 lifetime trades
  is a different phenomenon from "trades less often", and this round does not
  explain it. It is now the better-posed question that replaces the one Round 260
  left open.
- That P2's structural difference has any consequence for the *rate*. It changes
  how trades close; the rates are 1.20x apart, so it evidently does not change the
  rate much on these two routes.
- That XAU clears Target 3. 7.60/week is a backtest figure with an **8.6% margin** —
  thin, and consistent with Round 92 having called the margin thin.
- Anything about PnL. Not examined.
