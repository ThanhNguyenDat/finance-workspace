# WINDOW-INDEPENDENCE OF THE DOMINANT DAY IS REFUTED (Round 343)

This file called `2026-08-12` the worst day on `exness XAU` *"at both the 500- and 900-day
windows and at every band — band-independent **and** window-independent on that route."* Two
more windows at the deployed band refute the second half. At 300/500/900/1200 days the same
session measures **−0.0545 / −0.1796 / −0.1796 / +0.0015** — it even changes sign — and the
worst day is `2026-08-21` at 300 days and `2026-07-16` at 1200. All four holdouts contain all
three dates.

This is the per-kline weight refit (round 300) reaching the daily array: **daily results may
not be compared across windows.** This file's cross-route day comparisons were each made
*within* one window and stand; the window-independence claim does not. See `round343-NO-CHANGE-exness-xau-gross-is-positive-across-four-windows-and-the-gold-decorrelation-is-a-deliberate-ensemble-difference.md`.

---

# ANSWERED WITH PRICE DATA (Round 342)

This file's open question — why gold inverts between venues on 2026-06-10 — is answered, and
**not** in the direction it listed first. A narrow read-only query shows the two gold
instruments' daily returns correlate at **r = +0.996**, and on that day both fell together:
`XAUT` **−4.00%**, `XAU` **−4.23%**. There was **no price divergence**.

So the inversion is produced by the **Portfolio layer's own per-route decisions**: on one −4%
gold session, with prices moving as one, it made +0.2197 on the CFD route and lost −0.1694 on
the spot route. Across the whole holdout the pair's price correlation is +0.996 while its
Portfolio-PnL correlation is **+0.287**. See `round342-NEEDS-MORE-RESEARCH-the-two-gold-routes-track-each-other-at-0-996-in-price-and-0-287-in-portfolio-pnl.md`.

---

# Round 341 — REJECTED: the trough **does not replicate** on a different window — the 0.33 gross gap collapses to 0.05. And single-day dominance is **general to every route**, with 2026-06-10 the **worst** day on `bybit XAUT` and the **best** day on `exness XAU`.

Classification: **REJECTED** — my pre-registered persistence prediction failed, and it takes
part of Round 340's reading with it. Two bounded Docker sweeps (exactly the 2-container budget)
plus **zero-container** analysis of six gate runs already saved from Rounds 335-337. **XAU-first.**

## Pre-registration, stated as a partition this time

Round 340 characterised a smooth unimodal gross trough on `bybit XAUT` @500 with its floor at
0.0125 and called the feature structural. It also found `2026-06-10` dominating every band's
net. A `--days 300` window has a holdout starting **2026-07-01** — after that day — and lets
both questions be probed at once.

**Pre-registered as a partition** (applying Round 340's own lesson):
- gross(0.0125) is **at least 0.10 below** gross(0.02) → the trough persists;
- gap **under 0.10** → it does not.

At 500 days that gap is **0.3272** (−0.0682 against +0.2590).

## The trough does not persist

`bybit XAUT/USDT` spot, `--days 300`, holdout 2026-07-01 → 2026-08-30, 61 observed days,
`2026-06-10` confirmed absent, no continuity failures:

| band | trades | tr/wk | **gross** | cost | net | Sharpe | pos-day | streak |
|---|---|---|---|---|---|---|---|---|
| 0.0125 / 0.025 | 45 | 5.25 | **−0.1757** | 0.2892 | −0.4650 | −2.746 | 0.410 | 5 |
| 0.02 / 0.04 | 31 | 3.62 | **−0.1282** | 0.2038 | −0.3319 | −1.734 | 0.459 | 6 |

**The gap is 0.0476 — well under the 0.10 line. The trough does not replicate.** At 500 days
the two bands differ by 0.3272 in gross; at 300 days they differ by 0.0476, a **7x collapse**.

And the level moves with the window too: at 500 days these bands measure −0.0682 and **+0.2590**;
at 300 days they measure **−0.1757 and −0.1282**. Both are now negative.

## What that costs Rounds 338-340

**Round 340 concluded "the feature is structural, and the deployed band sits on its floor."**
That needs narrowing. The smooth unimodal shape does establish that the trough is **not
configuration noise within its window** — that argument stands. It does **not** establish that
the trough is a stable property of the route, and this window says it is not. "Structural"
should have been "structural within this window".

**Round 338's correction of Round 337 also needs qualifying.** Round 338 refuted "`exness XAU`
is the only route with positive gross" by measuring +0.2662 and +0.2590 on `bybit XAUT`. At 300
days both bands tested on that route are **negative**. So the gross *sign* on this route is
window-dependent, and neither Round 337's claim nor Round 338's correction of it is a stable
statement about the route.

This is Round 331's lesson arriving a third time: **a shape measured on one window is a
statement about that window.** I have now re-learned it for the optimal band (Round 331), for
the optimal frequency (Round 334), and for the trough (here).

## A design limit I cannot argue away

The 300-day holdout excludes `2026-06-10` **and** is a shorter, later, differently-conditioned
period (61 observed days against 101). The design **conflates** the two. It answers the
persistence question it was registered on, and it **cannot** attribute the trough's
disappearance to the excluded day. I am not claiming that it can.

## Zero-container: single-day dominance is general, and gold inverts between venues

The `daily_results` arrays from six gate runs saved in Rounds 335-337 were already on disk:

| run | days | net | worst day | worst PnL | share of net | best day | best PnL |
|---|---|---|---|---|---|---|---|
| `exness XAU` @500 b=0.011 | 84 | −0.0541 | **2026-08-12** | −0.1530 | 282.8% | **2026-06-10** | **+0.2097** |
| `exness XAU` @500 b=0.0115 | 84 | −0.0122 | **2026-08-12** | −0.1205 | 983.4% | **2026-06-10** | **+0.2197** |
| `exness XAU` @900 deployed | 151 | −0.4110 | **2026-08-12** | −0.1796 | 43.7% | 2026-04-01 | +0.1869 |
| `binance BTC` @500 | 101 | −3.9407 | **2026-06-05** | −0.4667 | 11.8% | **2026-06-15** | +0.1685 |
| `exness BTC` @500 | 101 | −4.5624 | **2026-06-05** | −0.4108 | 9.0% | **2026-06-15** | +0.1697 |
| `bybit XAUT` @500 | 101 | −0.4204 | **2026-06-10** | −0.1694 | 40.3% | 2026-08-05 | +0.1874 |

Three things fall out:

1. **Every route has a dominant day**, so Round 340's finding is not specific to `bybit XAUT`.
   On `exness XAU` it is `2026-08-12`, and it is the worst day at **both** the 500- and 900-day
   windows and at every band — band-independent *and* window-independent on that route.
2. **The two BTC venues agree**: `2026-06-05` is the worst day and `2026-06-15` the best on
   both `binance` and `exness`. Same underlying, same days, independent venues.
3. **The two gold routes invert.** `2026-06-10` is the **worst** day on `bybit XAUT`
   (−0.1694 to −0.2184 across bands) and the **best** day on `exness XAU` (+0.2097, +0.2197).
   Same underlying, same session, opposite sign.

And the concentration is remarkably uniform: the **top five days carry 14.4% to 19.7%** of
total absolute daily PnL on every one of the five runs measured, across three instruments and
two window lengths.

## What is proven, and what is not

Proven:

- `bybit XAUT` @300, holdout 2026-07-01 → 2026-08-30, 61 observed days, no continuity failures:
  0.0125/0.025 → 45 trades / 5.250 per week / gross −0.17571 / cost 0.28925 / net −0.46496 /
  Sharpe −2.7459; 0.02/0.04 → 31 / 3.617 / −0.12816 / 0.20378 / −0.33194 / −1.7343.
- The 0.0125-versus-0.02 gross gap is 0.3272 at 500 days and 0.0476 at 300 days.
- The worst-day and best-day table above, read from saved run output.
- Top-five-day share of absolute daily PnL: 18.3%, 14.4%, 19.7%, 18.3%, 19.5%.

Not proven, and deliberately not claimed:

- **That excluding 2026-06-10 caused the trough to disappear.** The window differs in length,
  period and conditions. The design cannot separate these and I am not asserting it can.
- **Why gold inverts between venues on 2026-06-10.** Divergence between tokenized XAUT and the
  XAU/USD CFD, opposite Portfolio positioning, and different session coverage are all
  consistent with the observation. **I queried no market data and inspected no positions.**
- That the trough is absent at every other window, or present at any. Two windows on one route.
- That `bybit XAUT` has no gross edge. Two bands at 300 days are negative; two other bands at
  500 days are +0.26. **Both readings are window-scoped**, which is exactly the point.
- That the uniform top-five concentration means anything causal. Five runs, and a heavy-tailed
  daily PnL distribution would produce a similar number without any shared mechanism.
- Any promotion. Every configuration measured this round loses money.
