# Round 258 — The predictable part of the market is the wrong part: `|drift|` never persists (5-150d), volatility always does, and only `|drift|` drives the edge

Classification: **REJECTED** — regime switching is closed at every horizon tested,
not only at 150 days. **Zero containers**; one read-only Timescale query over the
full five-year 4h series for both instruments.

## The one thing Round 257 left open

Round 257 rejected regime switching but flagged its own limit: *"regime switching
was tested at the 150-day band horizon only. A shorter regime horizon was not
examined and is not ruled out."*

A regime switcher needs one thing: the **next** period's trend magnitude. That is a
pure price-data question, so it can be scanned across many horizons with no
backtest at all — and at short horizons with real statistical power (364 windows at
5 days, against the 7 that Rounds 255-257 had).

**Method validity is not assumed.** Volatility is included as a **positive
control**: volatility clustering is a textbook stylized fact, so if the method
cannot recover it in the same windows, the method is broken and any null is
meaningless.

## Result — the control fires, the variable of interest does not

Lag-1 Spearman on non-overlapping windows tiled back from the present, 20 000-shuffle
permutation p, fixed seed:

| horizon | XAU n | XAU \|drift\| | XAU efficiency | XAU **volatility (control)** | BTC \|drift\| | BTC efficiency | BTC **volatility (control)** |
|---|---|---|---|---|---|---|---|
| 5d | 364/365 | +0.044 | −0.056 | **+0.506 (p<0.0001)** | +0.027 | −0.051 | **+0.532 (p<0.0001)** |
| 10d | 182 | −0.020 | −0.099 | **+0.606 (p<0.0001)** | +0.062 | −0.105 | **+0.504 (p<0.0001)** |
| 20d | 91 | +0.031 | −0.098 | **+0.518 (p<0.0001)** | −0.099 | −0.110 | **+0.570 (p<0.0001)** |
| 30d | 61/60 | +0.081 | −0.026 | **+0.539 (p<0.0001)** | −0.213 | −0.148 | **+0.535 (p<0.0001)** |
| 50d | 36 | +0.135 | −0.104 | **+0.403 (p=0.019)** | −0.106 | −0.180 | **+0.500 (p=0.003)** |
| 75d | 24 | −0.216 | −0.325 | +0.144 | −0.145 | −0.147 | **+0.598 (p=0.003)** |
| 100d | 18 | −0.392 | −0.498 (p=0.044) | **+0.561 (p=0.022)** | −0.154 | −0.233 | +0.333 |
| 150d | 12 | +0.045 | +0.100 | +0.536 | −0.564 | −0.609 (p=0.048) | +0.255 |

**`|drift|` — the quantity a switcher needs — is non-significant at 0 of 16
instrument-horizon cells.** The control is significant at 12 of 16, most of them at
p < 0.0001. The method plainly detects persistence when persistence exists.

Efficiency reaches nominal p < 0.05 in 2 of 16 cells. With 16 tests roughly 0.8 are
expected by chance, and **both are negative** — anti-persistence, the wrong sign for
a switcher even if they were real. They are not treated as findings.

## The closing argument — the forecastable variable is the wrong one

Volatility persists strongly. So does it drive the edge? Recomputed on the same
seven 150-day bands as Rounds 255-256, from an independent full-history data pull:

| | edge vs **\|drift\|** (unforecastable) | edge vs **volatility** (forecastable) |
|---|---|---|
| XAU | **+0.857 (p = 0.0238)** | +0.357 (p = 0.444) |
| BTC | **+0.857 (p = 0.0238)** | +0.107 (p = 0.840) |

**The variable that drives the edge does not persist. The variable that persists
does not drive the edge.**

That is why regime switching fails, and it fails structurally rather than for want
of a better horizon or a cleverer signal: markets offer a forecast of *how much
price will move* and no forecast of *how far it will get*, and the strategy edge
depends only on the second.

As a robustness note, the `|drift|` figures here are tiled from the full five-year
series rather than the 1050-day pull Rounds 255-256 used, so the band values differ
slightly (XAU B1 15.8% here against 12.81% there) — and the Spearman is **+0.857 on
both instruments either way**, unchanged to three decimals.

## Where the thread now stands

Rounds 242-258 are closed, and the closure is complete rather than provisional:

- the "favourable window" is trend magnitude (R255-256, ρ = +0.857 ×2 instruments);
- magnitude, not direction (R256);
- confirmed against a pre-committed counter-trend control that moves the opposite
  way (R257, +1.000 vs −0.900);
- the regime variable does not persist at **any** horizon from 5 to 150 days on
  either instrument, verified against a working positive control (this round);
- and the only regime variable that does persist is uncorrelated with the edge.

Nothing here changes the standing result that loss ≈ trade count × a near-constant
and that no Portfolio-construction lever improves per-trade economics.

## What is proven, and what is not

Proven:

- Full 4h history loaded for both instruments (XAU 8011 bars, BTC 10977 bars,
  2021-08-26 → 2026-08-28/29).
- The 48-cell scan above, with volatility significant at 12 of 16 cells and
  `|drift|` at 0 of 16.
- Edge vs `|drift|` Spearman +0.857 (p = 0.0238) on both instruments; edge vs
  volatility +0.357 (p = 0.444) and +0.107 (p = 0.840).

Not proven, and deliberately not claimed:

- That no forecast of `|drift|` exists. **Lag-1 autocorrelation on one variable is a
  narrow search.** A multivariate or exogenous predictor was not tested, and this
  rules out simple persistence rather than all predictability.
- That the two nominally significant efficiency cells are noise. They are
  *consistent* with noise given 16 tests and they point the wrong way; neither
  observation proves them spurious.
- That volatility is useless to the Portfolio generally. What is shown is that it
  does not rank these bands by edge — position sizing or risk control is a separate
  question that was not examined here.
- Anything about horizons below 5 days or above 150. The scan has those bounds.
- Any tradable conclusion. The edges used are the zero-cost gross figures from
  Rounds 254-257.
