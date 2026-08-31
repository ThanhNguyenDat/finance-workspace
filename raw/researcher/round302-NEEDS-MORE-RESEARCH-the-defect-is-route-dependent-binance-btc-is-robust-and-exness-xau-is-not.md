# QUALIFIED (Round 312)

`binance BTC`'s Target 3 pass recorded here is a property of **260-280-day windows**.
At **900 days** the same route returns **6.704/week (−4.2%, FAIL)** and at **901 days**
**7.085/week (+1.2%, pass)** — the bar falls between two windows one day apart. The
*level* at depth may be genuine history (Round 293 measured this route's deeper slices
lower); the *straddle* is measurement noise. Read the verdict as **pass on recent
windows, undetermined at depth**. See
`round312-REJECTED-the-confound-grows-with-depth-one-day-moves-50-trades-at-900d-and-binance-btc-straddles-the-bar.md`.

---

# CORRECTED (Round 305)

The `binance BTC` sensitivity used here — **1.04%** from a one-day perturbation, giving
a **33x** cushion over its Target 3 margin — is **15x too small**. Extending the ladder
to 270 and 280 days (Round 305) produced a **−42 trade** nesting violation and a rate
spread of **15.9%**, which equals that route's smallest margin (+15.9%). The pass still
holds on 4 of 4 windows; the *cushion* does not. Read every one-day sensitivity in this
file as a floor. See
`round305-REJECTED-binance-btc-sensitivity-is-15x-the-one-day-figure-and-its-safe-margin-is-gone.md`.

---

# Round 302 — NEEDS-MORE-RESEARCH: the measurement defect is **route-dependent**. `binance BTC` is robust — its ladder reproduces **exactly** — while `exness XAU`'s Target 3 pass is not robust to window choice.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered prediction held, and the
result qualifies the blanket unreliability Round 300 applied. Two bounded Docker
sweeps (exactly the 2-container budget). XAU analysis from data already on disk; the
containers went to BTC, the next priority and where the Target 3 passes live.

## The limit Round 301 named against itself

Round 301 closed with: *"I measured the floor on `exness XAU` and I am **not**
transferring the number to BTC … the same one-day perturbation on those routes has not
been run."* This runs it.

**Registered before running:** if the majors' Target 3 pass is robust, `binance BTC`'s
rate at `--days 260` and `--days 261` differs by **< 2%**. Refuted at ≥ 5%.

## Part 1 — `binance BTC` is robust, and its recorded ladder reproduces exactly

| `--days` | candles | **`one_target`** | legacy | grid | cost | decisions | Alpha 5m |
|---|---|---|---|---|---|---|---|
| 260 | 74,878 | **350** | 502 | 4,584 | 52 | 74,338 | 315,121 |
| **261** | 75,166 | **355** | 503 | 4,578 | 53 | 74,626 | 316,454 |

One extra day: **+288 candles, +288 decisions, `one_target` +5.** The genuine content
of one day at ~9.6/week is **1.37 trades**, so the confound contributes roughly
**+3.6** — against `exness XAU`'s **−7** on a day worth 0.11 trades.

**Target 3 rates: 9.423/week at 260 days, 9.521/week at 261 — a change of +1.04%.**
The prediction holds. Both clear the 7/week bar by **+34.6%** and **+36.0%**, margins
an order of magnitude larger than the perturbation sensitivity.

The nesting violation is still present — `legacy_grid` goes 4,584 → **4,578** — so the
mechanism Round 300 found is there. It is simply **small** here.

**And the recorded ladder reproduces exactly.** Round 292 recorded `binance BTC`'s
`[0,180]` at 9.61/week and `[180,260]` at 9.01/week, which imply a 260-day cumulative
of **350.1 trades**. Today's independent 260-day run returns **350**. Against
`exness XAU`, whose 360-day count moved 363 → 374 (+3.03%) between rounds, that is a
different quality of measurement.

## Part 2 — `exness XAU`'s Target 3 pass is not robust to window choice

From Round 301's three runs, no new containers:

| `--days` | trades | **rate/week** | margin over the 7.0 bar |
|---|---|---|---|
| 360 | 374 | 7.272 | **+3.9%** |
| **361** | **367** | **7.116** | **+1.7%** |
| 365 | 392 | 7.518 | **+7.4%** |

The route **passes on all three** — but the spread from window choice alone is
**5.5%**, which is **larger than the smallest margin (+1.7%)**. A slightly different
arbitrary `--days` could plausibly place this route below the bar.

Worse, the window-length dependence is far bigger than the perturbation noise:

| route | short window | longer window | ratio |
|---|---|---|---|
| **`exness XAU`** | 180d → **3.89/week** | 360d → **7.27/week** | **1.87x** |
| `binance BTC` | 180d → 9.61/week | 260d → 9.42/week | **0.98x** |

**`exness XAU` reports nearly double the trade rate depending on how long a window you
ask for; `binance BTC` reports the same rate to 2%.** For `exness XAU` there is no
window-independent backtest Target 3 rate, and quoting one without its `--days` is
meaningless. For `binance BTC` the rate is stable across every window length measured.

## What this does to Round 300's banners

Round 300 marked every differenced Portfolio slice in Rounds 289-299 **unreliable**,
uniformly. That was the right call on the evidence then, and I am not withdrawing it —
but it is now too broad in one direction and correctly aimed in another:

- On **`binance BTC`** the defect is present but small: ~1% rate sensitivity, an exact
  ladder reproduction, and a Target 3 margin 30x the noise. Its recorded numbers are
  better than "unreliable"; they are **corroborated at the single-window level**.
- On **`exness XAU`** the defect is severe: a *negative* one-day response, a 5.5%
  perturbation spread and a 1.87x window-length swing. Everything differenced on that
  route stays unreliable, and its marginal Target 3 pass should be read as
  **undetermined**, not as a pass.

The mechanism is instrument-independent — the weights refit on every kline in every
run — but **its magnitude plainly is not**, and Round 300 had no way to know that from
one route.

## What is proven, and what is not

Proven:

- `binance BTC` at the deployed config, same day, same endpoint: `one_target` = 350 at
  260 days and 355 at 261 days; rates 9.423 and 9.521/week; change +1.04%.
- Alpha 5m 315,121 → 316,454 (+1,333 over +288 candles = 4.628/candle);
  `one_target` +0.0174/candle.
- `legacy_grid` 4,584 → 4,578 — the nesting violation is present on BTC too, and small.
- Round 292's recorded `binance BTC` slices imply a 260-day cumulative of 350.1; the
  independent run today returns 350.
- `exness XAU` Target 3 rates 7.272 / 7.116 / 7.518 per week at 360 / 361 / 365 days;
  spread 5.5%; smallest margin over the bar +1.7%.
- `exness XAU` 180d → 3.89/week against 360d → 7.27/week (1.87x); `binance BTC`
  180d → 9.61 against 260d → 9.42 (0.98x).

Not proven, and deliberately not claimed:

- **Why the defect is small on one route and large on the other.** BTC has 288 bars/day
  against XAU's 194, more trades and a different candidate set — I did not test any of
  these and I am not proposing a mechanism.
- That `binance BTC`'s *differenced deep slices* are now trustworthy. One perturbation
  at 260/261 days says nothing about a 180-day gap at 540-720 days; Round 293's 10-trade
  `[540,720]` slice remains unestablished.
- Anything about `exness BTC`, `bybit BTC`, `bybit XAUT` or `binance XAU`. Four of six
  routes have had no perturbation run at all.
- That `exness XAU` fails Target 3. It passes on all three windows measured; what is
  claimed is that the **margin is smaller than the measurement's own window
  sensitivity**, so the pass is not established, not that it is refuted.
- That either route is profitable. Both lose money; `binance BTC` returns
  realized_pnl −3.40 and −3.56 on the two windows. Target 1 is untouched here.
