# CORRECTION (Round 261)

This file corrected the XAU/BTC gap for **exposure** and reported that the gap
"survives the correction essentially intact". That was arithmetically true and
beside the point: **the gap was compositional, not exposure-related.** The "XAU
pool" mixed `exness XAU` (395 lifetime trades) with `binance XAU` (8) and
`bybit XAUT` (3). Correcting the denominator could never have revealed that; only
looking at the routes separately does.

Over their own ~1-year histories the mature routes run 7.60 closes/week
(exness XAU) against 9.14 (binance BTC) — **1.20x, not 3x** — and both are above
the 7/week bar.

This file's *measurements* stand: durable-log completeness on 6 of 6 routes, the
per-route bar counts, and the finding that only one of three XAU routes is
weekend-closed. Its closing line — "the XAU/BTC gap is now known not to be market
hours; nothing here says what it is" — is superseded: there was no gap. See
`round261-CORRECTION-there-was-no-xau-btc-frequency-gap-my-pooling-created-it.md`.

---

# Round 260 — Durable log verified complete on all six routes, and the weekend bias Round 259 flagged explains 5.9% of the XAU/BTC gap

Classification: **NO-CHANGE** — two caveats Round 259 raised against itself are now
closed, and neither changes a conclusion. Read-only production evidence.
**Zero containers.**

Round 259 established that Target 3 needs roughly 3.3 more days of observation to
resolve. Twenty minutes have passed, so re-reading the counts would add nothing.
What *can* be finished now are the two limitations Round 259 wrote against its own
result.

## Caveat 1 — closed: the log is complete on all six routes, not two

Round 259 verified durable-log **completeness** (not merely the atomicity invariant
Round 207 checked) on two of six routes, and said so. The same check on the
remaining four:

| route | ledger trades | retained | log closes | result |
|---|---|---|---|---|
| bybit BTC/USDT | 316 | 5 | 3 | 2 pre-deploy absent, **3 after-deploy all present** |
| bybit XAUT/USDT | 3 | 2 | 1 | 1 pre-deploy absent, **1 after-deploy present** |
| exness BTC/USD | 485 | 4 | 3 | 1 pre-deploy absent, **3 after-deploy all present** |
| binance XAU/USDT | 8 | 1 | 1 | **1 after-deploy present** |

**No mismatch on any route.** Every retained ledger trade with `exit_at` at or after
the deployment boundary (worker start, 2026-08-27T14:35Z) appears in the durable log
with a matching timestamp; every retained trade before it is absent, as it must be.

Combined with Round 259's two routes, the durable Portfolio trade log is now
verified **complete on 6 of 6 routes** — the property Round 207 explicitly did not
establish.

## Caveat 2 — closed and quantified: the weekend bias is real and small

Round 259 flagged that its 46.1-hour window contains a weekend boundary which
"suppresses the XAU CFD routes specifically — a bias against XAU that the point
estimates do **not** correct for."

The correction needs the tradable exposure per route, which is countable directly as
closed 5m bars in the window:

| route | market | bars in window | coverage | closes | corrected /week | uncorrected |
|---|---|---|---|---|---|---|
| binance BTC/USDT | 24/7 | 554 | 100.0% | 4 | 14.6 | 14.6 |
| exness BTC/USD | 24/7 | 554 | 100.0% | 3 | 10.9 | 10.9 |
| bybit BTC/USDT | 24/7 | 554 | 100.0% | 3 | 10.9 | 10.9 |
| binance XAU/USDT | 24/7 | 554 | 100.0% | 1 | 3.6 | 3.6 |
| bybit XAUT/USDT | 24/7 | 554 | 100.0% | 1 | 3.6 | 3.6 |
| exness XAU/USD | **weekend-closed** | **353** | **63.7%** | 1 | **5.7** | 3.6 |

**Only one of the three XAU routes is weekend-closed.** `binance XAU/USDT` is a
perpetual future and `bybit XAUT/USDT` is spot Tether Gold; both ran 24/7 with
**554 bars — identical exposure to every BTC route — and closed once each.**

Exposure-weighted pools:

| pool | closes / bars | corrected /week | 95% CI | verdict |
|---|---|---|---|---|
| BTC (3 routes) | 10 / 1662 | 12.13 | [5.82, 22.31] | **undetermined** |
| XAU (3 routes) | 3 / 1461 | **4.14** | [0.85, 12.10] | **undetermined** |

At BTC's exposure the XAU routes would have produced **3.41 closes against BTC's
10**. The closure therefore accounts for **0.41 of the 7.00-close gap — 5.9% of
it.**

**The bias is real, it moves XAU's pooled rate from 3.6 to 4.14/week, and it
changes nothing**: XAU is still below the 7/week bar on the point estimate, still
undetermined at 95%, and the XAU/BTC gap survives the correction essentially
intact. Round 259 was right to flag it and right not to lean on it.

## A clarification worth recording

`binance.perpetual_future.XAU.USDT` has **554 bars in the window and a full 2016
bars in the last complete week** — complete 24/7 kline coverage. Round 206's
description of that route as "frozen since 2025-12-26" refers to its **Portfolio
ledger not trading**, not to missing market data. A future round should not read
"frozen route" as a data gap; the data was always there, the strategy simply was
not closing positions. Round 259 recorded that it traded once on 2026-08-28.

## What is proven, and what is not

Proven:

- Durable-log completeness on the four routes Round 259 did not check, with no
  mismatch; 6 of 6 routes now verified.
- Closed 5m bar counts per route in the observation window (554 for five routes,
  353 for `exness.cfd.XAU.USD`) and for the last full week (2016 and 1380).
- Exposure-corrected pooled rates: BTC 12.13/week [5.82, 22.31], XAU 4.14/week
  [0.85, 12.10]; the weekend closure accounts for 5.9% of the gap.
- `binance.perpetual_future.XAU.USDT` has complete kline coverage.

Not proven, and deliberately not claimed:

- **Any Target 3 verdict.** Both pools remain undetermined at 95% after the
  correction, exactly as before it. This round did not move that question and was
  not able to — it is blocked on elapsed time, not on analysis.
- That exposure measured in closed bars is the right denominator for Target 3. It
  is the right denominator for *"does the strategy fire often enough given the
  chances it had"*; if the operational requirement is calendar decisions per week
  regardless of market hours, the **uncorrected** column is the one that counts and
  `exness XAU` reads 3.6/week, not 5.7. Both are shown because the target's
  intended denominator is not something this round can settle.
- That the XAU/BTC gap has an explanation. It is now known **not** to be market
  hours. Nothing here says what it is.
- Anything about PnL or profitability. Not examined this round.
