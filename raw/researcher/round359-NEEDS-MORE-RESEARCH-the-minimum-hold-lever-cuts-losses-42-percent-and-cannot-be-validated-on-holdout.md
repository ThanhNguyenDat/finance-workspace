# THE LEVER TOUCHES EDGE, NOT ONLY COST — AND IT IS STILL CLOSED (Round 363)

The question this arc could not decompose is answered on `exness XAU` @300: net PnL **per trade**
improves **−0.005824 → −0.003030 (48%)** from hold 36 to 288, while **funding cost per trade
rises** (−0.000354 → −0.000409). Cost moving *against* the improvement means the surviving trades
are genuinely better — the first mechanism in this arc that visibly touches the **edge**.

It is still not a candidate: the loss shrinks mostly by trading less (−60% of trades), per-trade
loss never approaches zero, and frequency collapses to **2.52/week** against a 7.0 bar.
See `round363-REJECTED-the-hold-lever-shrinks-the-loss-by-trading-less-and-its-endpoint-is-no-activity-not-profit.md`.

---

# LADDER SATURATES AT 72; THE XAUT ARM IS VERIFIED SAME-WINDOW (Round 360)

Extending the ladder on a verified-identical window (143,998 candles at all three points):
`binance BTC` hold **36 → 72 → 144** gives **−4.74869 → −2.74744 → −2.65041**. The second
doubling buys **3.5%** where the first bought **42.1%**, and it drops the rate to **5.15
trades/week — failing Target 3**, which hold 72 cleared at 7.24. **Hold 72 is the
joint-objective point among tested values**; 144 is nearly free in PnL and expensive in frequency.

This file's comparisons are checked and safe: the `bybit XAUT` 36/72 pair and the `binance BTC`
36/72 pair each share a **143,998**-candle window. See `round360-DATA-ISSUE-cross-round-comparisons-drift-and-legacy-is-a-free-drift-control-the-hold-ladder-saturates-at-72.md`.

---

# Round 359 — NEEDS-MORE-RESEARCH: doubling the minimum-hold guard from **36 to 72** cuts `binance BTC`'s loss by **42%** and `bybit XAUT`'s by **21%**, while `binance BTC` still clears Target 3 at **7.24/week**. It is the first substantial improvement this arc has found — and it **cannot be validated on holdout**, by construction.

Classification: **NEEDS-MORE-RESEARCH** — the pre-registered test passed on both routes, the
effect is large and monotone, and the OOS evidence the promotion gate requires is structurally
unobtainable with the current CLI. Two bounded Docker sweeps (exactly the 2-container budget).

## Why this lever, and why now

Round 358 found the minimum-hold guard is a **first-order** effect where it bites: on
`binance BTC` it cuts the loss **41%** against the guard-free stream, on `bybit XAUT` **19.8%**.
Every lever this arc has tuned was the protective band. `--portfolio-minimum-hold-decisions` is a
**deployed, tunable production parameter** (currently 36) that had never been moved.

**Pre-registered as a partition:** hold 72 improves `one_target` realized PnL on **both** routes
against hold 36 → the lever is helpful where the guard bites and deserves a ladder; **either** is
worse → not a reliable lever.

## Result — both improve, and the ladder is monotone

`--days 500`, deployed band, plain `--json`:

| route | configuration | trades | trades/week | `one_target` PnL | vs guard-free |
|---|---|---|---|---|---|
| `bybit XAUT` | guard-free (`legacy`) | 309 | 4.33 | −1.96680 | — |
| `bybit XAUT` | **hold 36 (deployed)** | 247 | 3.46 | −1.57738 | +19.8% |
| `bybit XAUT` | **hold 72** | 215 | 3.01 | **−1.24701** | **+36.6%** |
| `binance BTC` | guard-free (`legacy`) | 990 | 13.86 | −8.07260 | — |
| `binance BTC` | **hold 36 (deployed)** | 689 | 9.65 | −4.74869 | +41.2% |
| `binance BTC` | **hold 72** | 517 | **7.24** | **−2.74744** | **+66.0%** |

**Both improve. The registered branch fires.** The step from 36 to 72 is worth **+20.9%** on
`bybit XAUT` and **+42.1%** on `binance BTC`, and the effect is **monotone** across all three
points on each route.

**And on `binance BTC` the joint objective survives the step**: 7.24 trades/week still clears the
7.0 Target 3 bar, having fallen from 9.65. That is the first time in this arc that a lever
improved PnL materially **without** immediately breaking the frequency target. `bybit XAUT` fails
Target 3 at every hold (4.33 → 3.46 → 3.01), so the improvement there is not a candidate.

**Both routes still lose.** −2.74744 and −1.24701 are smaller losses, not profits.

## The blocker, and it is structural

`--portfolio-minimum-hold-decisions` **conflicts with** `--daily-profit-gate`
(`main.rs:255-263`), because the gate does not model the construction guard at all (Round 356).
**So this lever cannot be scored on a holdout with the current CLI.** Every number above is
**full-window `one_target`**, which is not the out-of-sample evidence the promotion gate's first
condition requires.

That is not a reason to weaken the gate — it is the reason this stays at
NEEDS-MORE-RESEARCH despite being the largest improvement the arc has produced. The concrete
unblocking step is a code change: let the gate accept a hold value and model the construction
guard, or expose a holdout-restricted `one_target`.

## What is proven, and what is not

Proven:

- The six-row table above, from plain `--json` runs at `--days 500` on the deployed band.
- Hold 36 → 72: `bybit XAUT` −1.57738 → −1.24701 (247 → 215 trades); `binance BTC` −4.74869 →
  −2.74744 (689 → 517 trades).
- `binance BTC` at hold 72 trades 7.24/week, above the 7.0 Target 3 bar; `bybit XAUT` is below it
  at every hold tested.
- The flag conflict at `main.rs:255-263`.

Not proven, and deliberately not claimed:

- **That hold 72 is better out of sample.** It is not measurable on a holdout here at all, so the
  question is open rather than answered — and full-window improvement from a parameter chosen
  after seeing the window is exactly the kind of result this loop distrusts.
- **That the lever is monotone beyond 72.** Three points per route in one direction; 144 and
  beyond are untested, and Rounds 330-335 showed a band lever that looked monotone and then
  turned.
- That it transfers to `exness XAU`. The guard moves PnL only 0.4% there (Round 358), so the same
  step would likely do little — **untested this round**, and the obvious next run.
- That either route becomes viable. Both still lose, `bybit XAUT` misses Target 3 by 2.3x, and
  `binance BTC`'s gross was **negative** at this window (Round 342) — a smaller loss on negative
  gross is not a path to profit.
- One window, one step, two routes. Round 352's nesting caveat applies to any follow-up.
- Any promotion. Condition 1 of the promotion gate — defensible OOS/holdout evidence — **cannot
  currently be met for this parameter**, so PROMOTE is not available regardless of effect size.
