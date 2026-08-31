# HEADLINE WITHDRAWN (Round 404)

This file concluded that production trades 2-4x faster than the backtest holdout rate. It
does not. The live trade log **pools three paper sizing configurations** per route -
`paper-fixed-pct`, `paper-compounding-10pct`, `paper-risk-2pct` - and this file counted all
three as one.

They share a **single decision stream**: every `(entry_at, exit_at, side, close_reason)`
tuple is identical across the three scopes (3 of 3 on `exness XAU`, 6 of 6 on
`binance BTC`). They differ only in position size, by up to **1,372x**.

So the distinct trade counts are **3 and 6**, not 9 and 18, and per configuration the live
rate **overlaps** the backtest holdout rate on both routes. **The 2-4x gap was exactly the
3x pooling factor.**

This file's rising-frequency explanation is neither confirmed nor needed - there is no
discrepancy left to explain. Its verification that the log is append-only, its window
anchoring, and its sensitivity check all stand; what failed was not reading the payloads.
See
`round404-DATA-ISSUE-round-403s-live-rate-was-inflated-exactly-3x-by-pooling-three-paper-sizing-scopes-of-one-decision-stream.md`.

---

# Round 403 — NEEDS-MORE-RESEARCH: production trades **2–4× faster** than the backtest holdout rate on **all three BTC routes** — the first live-versus-backtest comparison this arc has had enough data to make.

Classification: **NEEDS-MORE-RESEARCH**. **Zero containers**; narrow read-only
production reads plus one code check.

## Why this is possible now and was not before

Rounds 306 and 357 tried this and failed: the live trade log held **1–6 closes**,
too few to validate any rate. It now holds **60 closes across six routes**.

The log is safe to count from: `crates/finance-redis/src/trade_log.rs` contains
**only `ZADD`** — no trim, no expiry, no delete — so it holds every close since
the worker began writing.

## The comparison

Observation window anchored on the earliest close across **all six** routes
(a route-independent anchor): **3.91 days = 0.559 weeks**. Exact Poisson 95%
intervals on the live rate:

| route | closes | live /wk (95% CI) | backtest holdout /wk | |
|---|---|---|---|---|
| `exness XAU` | 9 | 7.4 – 30.6 | 6.232 | live higher |
| `binance XAU` | 3 | 1.1 – 15.7 | 4.797 | overlaps |
| `bybit XAUT` | 3 | 1.1 – 15.7 | 3.454 | overlaps |
| **`binance BTC`** | 18 | **19.1 – 50.9** | 7.661 | **live higher** |
| **`bybit BTC`** | 12 | **11.1 – 37.5** | 8.517 | **live higher** |
| **`exness BTC`** | 15 | **15.0 – 44.3** | 5.794 | **live higher** |

The anchor conditions on events — the bias rounds 357/358 caught — so the window
is a **lower** bound and every live rate an **upper** bound. Re-running with a
window one day longer:

**Three routes still hold: `binance BTC` (15.2–40.6), `bybit BTC` (8.8–29.9),
`exness BTC` (12.0–35.3).** All three BTC routes, under both assumptions. The
three gold routes overlap once the window is widened.

## The alternative explanation, which this arc's own findings support

**Frequency rises toward the present.** Round 392 measured 1.963 → 6.232
trades/week across four disjoint holdouts on `exness XAU` (3.17×); round 397
found the same direction on `binance BTC`.

Production's window is the **last 3.9 days**. The backtest's holdout is the
**last 180 days**, ending on the same date. If the rate is rising, a 4-day
window sits at the top of that trend while a 180-day average sits below it —
**which could account for the entire discrepancy without the backtest being
wrong about anything**.

I am naming that as the **leading** explanation, not a caveat. Concluding "the
backtest understates production" would require comparing like with like, and
these two windows differ by a factor of 46 in length on a quantity the arc has
already shown to be trending.

## What is proven, and what is not

Proven:

- Six production trade-log keys hold 9 / 3 / 3 / 18 / 12 / 15 closes; the log
  is append-only (`ZADD` only, no trim or expiry).
- The observation window from the earliest cross-route close is 3.91 days.
- Poisson 95% intervals as tabulated; three BTC routes exceed their backtest
  holdout rate under both window assumptions.

Not proven, and deliberately not claimed:

- **That the backtest understates production.** The trend explanation above is
  untested and sufficient on its own.
- That production and the backtest run the same effective configuration. Not
  verified this round; a configuration difference would produce the same
  signature.
- Anything about the two 3-close routes. Three events cannot distinguish
  anything, and their intervals span an order of magnitude.
- That 3.91 days is the true window. It is a lower bound anchored on an event;
  the log's actual start was not established, and I did not read worker uptime
  to avoid widening a narrow read.
- Any implication for Target 3. A live rate above the bar over four days is not
  a Target 3 pass — the objective's frequency criterion has never been defined
  over a four-day sample.

## Named next step

The clean test is like-for-like: measure the backtest's trade rate over a window
matching production's, rather than over a 180-day holdout. That needs a
short-window run whose other properties (warm-up, holdout length) would then be
disqualifying — so the honest version is the opposite direction: **wait, and
recount the live log when it spans 30+ days.** That is the forward-time thread
this arc has repeatedly named, and it is now actually collecting data.
