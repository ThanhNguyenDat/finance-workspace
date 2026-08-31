# Round 310 — NEEDS-MORE-RESEARCH: the live weights put `5m` **2.1x-7.8x below uniform** on every route and amplify Round 309's entry/trend asymmetry from 1.67x to **2.21x-5.96x**. The mechanism is already documented; the magnitudes are not.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered prediction was confirmed
decisively, and the result quantifies a mechanism the codebase already describes.
**Zero containers**; narrow read-only production evidence plus two local code reads.

## The caveat Round 309 left

Round 309 closed with: *"the adaptive reweighting of Round 300 moves `interval_weights`
away from the uniform 1/8 continuously, so the structural 1.67x bound applies to the
**initial** policy, not necessarily to the live one."*

**Registered before reading:** the live weights have drifted materially — at least one
interval sits outside [0.10, 0.15], i.e. more than 20% off the uniform 0.125. If they
were all still ≈0.125 the reweighting would be inert in practice, which would also make
Round 300's weight-path confound far less serious than I have been treating it.

## The live weights, all six routes

| route | `5m` | vs uniform | `1d` | vs uniform | entry sum | trend sum | **ratio** |
|---|---|---|---|---|---|---|---|
| `binance BTC/USDT` | 0.0412 | **3.0x low** | 0.1549 | 1.24x | 0.3114 | 0.6886 | **2.21x** |
| `exness BTC/USD` | 0.0408 | **3.1x low** | 0.1550 | 1.24x | 0.3083 | 0.6917 | **2.24x** |
| `bybit BTC/USDT` | 0.0588 | 2.1x low | **0.4145** | **3.32x** | 0.1763 | 0.8237 | **4.67x** |
| `binance XAU/USDT` | 0.0479 | 2.6x low | **0.4311** | **3.45x** | 0.1437 | 0.8563 | **5.96x** |
| `exness XAU/USD` | **0.0161** | **7.8x low** | 0.2081 | 1.66x | 0.2524 | 0.7476 | **2.96x** |
| `bybit XAUT/USDT` | 0.0571 | 2.2x low | 0.3030 | 2.42x | 0.2755 | 0.7245 | **2.63x** |

**The prediction is confirmed on every route.** Nothing is near uniform: `5m` is
**down-weighted on all six**, `1d` is **up-weighted on all six**, and on
`binance XAU` a single interval carries **43% of all weight**.

**Round 309's asymmetry is amplified, not bounded.** Its structural figure was
5/3 = 1.67x from uniform weights; the live entry:trend ratios run **2.21x to 5.96x**,
mean **3.45x**. Round 309 observed a sample ratio of 2.59x and could not explain why it
exceeded 1.67x — the live weights supply the direction and the order of magnitude. They
do not reproduce 2.59x exactly, and should not: the score ratio also depends on which
strategies had non-Hold evidence at each moment.

**A consequence neither round had:** with `minimum_role_score = 0.10`, **no route's `5m`
interval can clear the threshold on its own** — its maximum possible contribution runs
0.0161 to 0.0588. The primary decision interval can no longer move the entry gate by
itself anywhere in the fleet; the entry role now depends on `15m`/`30m` carrying
non-Hold evidence.

## An exact arithmetic confirmation

Round 307 recorded `exness XAU`'s `entry_score` as **−0.016109519172610748**. Its live
`5m` interval weight is **0.016109519172610748** — **identical to sixteen decimal
places**.

That pins the arithmetic exactly: at that moment `candle_momentum` (strategy weight
**1.0**, see below) contributed a single full-strength signal at `5m`, and `15m` and
`30m` contributed nothing. It also confirms `role_scores()` behaves precisely as read
in Round 309.

## Strategy weights have collapsed too

| route | strategy weights |
|---|---|
| `binance BTC` | `candle_momentum` 0.521, `rsi_mean_reversion` 0.479, **all four `mtf_*` exactly 0.0** |
| `exness BTC` | `candle_momentum` 0.515, `rsi_mean_reversion` 0.485, **all four `mtf_*` exactly 0.0** |
| `bybit BTC` | `candle_momentum` 0.525, `rsi_mean_reversion` 0.475 |
| `binance XAU` | `candle_momentum` 0.386, `rsi_mean_reversion` 0.614 |
| **`exness XAU`** | **`candle_momentum` 1.0**, `mtf_stochastic_5m_4h_sma5` 0.0, `rsi_mean_reversion` 0.0 |
| `bybit XAUT` | `rsi_mean_reversion` 0.826, `candle_momentum` 0.174 |

**`exness XAU`'s Portfolio decision is carried by one strategy.** And every `mtf_*`
entry is at exactly 0.0, independently reconfirming Rounds 206-207 from live policy
state.

## The mechanism is already known, and deliberately left in place

I am **not** presenting this as a discovery. `deployment_rules.rs:218-240` already
documents it: `alpha_performance_quality` returns **1.0 when `trade_count == 0`**
(`trading_modes.rs:593-595`) — a "benefit of the doubt" rule — so intervals with no
Alpha trading history receive the *maximum* quality while intervals that actually trade
are scored on their real, losing performance and fall toward the
`INTERVAL_QUALITY_FLOOR = 0.05` (`:453`). That note names the resulting "pathological
all-entry-intervals-zeroed pattern", records that the zombie `mtf_*` strategies are
propping up decision frequency "by not yet having accumulated 20 role-interval
evaluations", and states the fix direction: *"a deliberate, explicit interval-weight
floor in `reweight_from_alpha_performance` (not an accidental one from zombie
strategies)"*.

What this round adds is the **current magnitude on all six routes** and its
**interaction with `minimum_role_score`**, which that note does not cover. Note also
that Round 309's role-normalisation idea is a **different** lever from the
interval-weight floor named above — one fixes the entry/trend scale, the other fixes
which intervals earn weight. Both remain **investigation only, not applied**.

## What is proven, and what is not

Proven:

- Live `interval_weights` and `strategy_weights` for all six routes, as tabulated,
  read from the production checkpoints at 2026-08-30 ~05:35Z.
- `5m` is below the uniform 0.125 on every route (0.0161-0.0588); `1d` is above it on
  every route (0.1549-0.4311).
- Live entry:trend weight-sum ratios 2.21 / 2.24 / 4.67 / 5.96 / 2.96 / 2.63, against
  the uniform-weight structural value of 1.67.
- No route's `5m` weight reaches `minimum_role_score` = 0.10.
- `exness XAU`'s Round 307 `entry_score` equals its live `5m` interval weight to 16
  decimal places.
- `exness XAU` carries `candle_momentum` at 1.0 and every other strategy at 0.0; all
  `mtf_*` entries are 0.0 on both routes that carry them.
- `alpha_performance_quality` returns 1.0 at `trade_count == 0`
  (`trading_modes.rs:593-595`); `INTERVAL_QUALITY_FLOOR = 0.05` (`:453`); the behaviour
  and its consequences are documented at `deployment_rules.rs:218-240`.

Not proven, and deliberately not claimed:

- **That this weighting is wrong.** It is documented as a known, deliberately-accepted
  trade-off. I measured its current magnitude; I did not evaluate whether a different
  weighting would trade better, and Round 308 established the tooling cannot.
- That the weights explain Round 309's 2.59x sample ratio *quantitatively*. They
  explain its direction and order; the residual depends on per-moment strategy
  evidence.
- That `5m` being unable to clear the threshold alone is harmful. It is a structural
  fact of the current configuration; whether the entry gate should be movable by the
  primary interval is a design question, untested.
- That the weights are stable. This is one snapshot; the reweighting runs on every
  kline, so these values move continuously.
- Anything about `binance XAU`'s weights being meaningful. Its market data has been
  frozen since 2025-12-25 (Rounds 207, 306), so its 0.4311 on `1d` may reflect a stalled
  ledger rather than live performance. Recorded, not interpreted.
