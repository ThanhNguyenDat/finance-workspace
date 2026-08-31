# LADDER EXTENDED TO 288 — AND THE DIRECTION IS CLOSED (Round 363)

The ladder does **not** stop at 144: hold **288** gives **−0.32723** (108 trades, **2.52/week**),
another **+53.4%** on PnL and **+29.2%** on PnL *per trade*. So the quality gain is real and the
per-trade series is **lumpy** (+24.5%, +2.7%, +29.2%), which refutes the expectation that
everything past 72 is pure trade removal.

**But the direction is closed as a candidate.** Cumulatively 36 → 288 the loss shrinks **79.2%**
while trades fall **60.0%** and frequency goes **6.30 → 2.52 per week** — a 2.8x Target 3 miss —
and per-trade loss is still clearly negative (**−0.003030**) at the deepest point. The endpoint is
**no activity, not profit**. See `round363-REJECTED-the-hold-lever-shrinks-the-loss-by-trading-less-and-its-endpoint-is-no-activity-not-profit.md`.

---

# Round 362 — NEEDS-MORE-RESEARCH: the hold ladder **saturates on `binance BTC` but not on `exness XAU`** — 72 → 144 gains **3.5%** there and **+30.3%** here. Cumulatively 36 → 144 is **+55.4%** on XAU, bought with **39% fewer trades** on a route that already fails Target 3.

Classification: **NEEDS-MORE-RESEARCH** — a valid, same-window result that extends the lever and
sharpens its cost, still blocked from promotion by the same tooling gap. Two bounded Docker
sweeps (exactly the 2-container budget), **XAU-first**.

## The question

Round 360 found the ladder **saturates** on `binance BTC`: 72 → 144 bought only **3.5%** and
broke Target 3. Whether that is a property of the lever or of the route was untested.

**Pre-registered, validity gate first:** identical `candle_count` **and** identical
`legacy_selected_rule` across the two arms (both launched together). **Given validity:** hold 144
improves on hold 72 by **≥ 10%** relative → the XAU ladder keeps going, unlike BTC's; **< 10%** →
it saturates by 72 here too.

## Validity gate — passed

| check | hold 72 | hold 144 |
|---|---|---|
| `candle_count` | **57,933** | **57,933** |
| `legacy_selected_rule` | 345 trades, **−1.633800** | 345 trades, **−1.633800** |

## Result — the ladder keeps going on XAU

`exness XAU` @300:

| hold | trades | trades/week | `one_target` PnL | step gain | `execution_cost` rejections |
|---|---|---|---|---|---|
| 36 (deployed)\* | 270 | 6.30 | −1.57256 | — | 97 |
| 72 | 229 | 5.34 | −1.00705 | +36.0% | 71 |
| **144** | **164** | **3.83** | **−0.70183** | **+30.3%** | 30 |

\* the 36 point is from Round 361 at 57,929 candles — see the note below.

**Delta +0.30523, relative +30.3% — the "keeps going" branch fires**, against `binance BTC`'s
**3.5%** at the same step. **The saturation is route-specific, not a property of the lever.**

Cumulatively **36 → 144 is +55.4%** on this route (−1.57256 → −0.70183).

## What it costs, and what cannot be decomposed

Frequency falls **6.30 → 3.83 per week, a 39% cut**, on a route that **already failed Target 3 at
every hold**. So the XAU ladder buys PnL with frequency the route cannot spare — the same shape as
`bybit XAUT`, and unlike `binance BTC`, which was the one route where hold 72 kept the bar.

**Whether the gain is added edge or merely removed cost is not determinable here.** The plain
`--json` path reports `realized_pnl` (net) only, and zeroing costs to expose gross would drop the
reversal cost below the 10 bps gate and change the action space (Round 348) — the same block that
stopped the gross-by-weekday question in Round 354. Trades fall 39% while PnL improves 55%, which
is *consistent with* more than pure cost removal, but I cannot separate them and am not claiming
it.

## A refinement to the drift rule

Round 361 measured a **36-candle** window shift moving `exness XAU` PnL by **0.25040**. This
round's hold-72 arm sits at **57,933** candles against Round 361's **57,929** — a **4-candle**
shift — and reproduces **−1.00705 with 229 trades exactly**.

So **drift is not proportional to the shift**: 4 candles moved nothing, 36 candles moved 18.9% of
the scale. A small shift can be inert if the extra bars produce no decisions. **That does not
license comparing across rounds** — it means the `candle_count` check is the right guard precisely
because the effect is unpredictable. The 36-hold row above is quoted from Round 361 across a
4-candle gap on that empirical basis, and the 72 → 144 comparison this round needs no such
argument.

## What is proven, and what is not

Proven:

- Validity gate: 57,933 candles and `legacy` 345 trades / −1.633800 in both arms.
- `exness XAU` @300: hold 72 → 229 trades / −1.00705; hold 144 → **164 trades / −0.70183**;
  +30.3%.
- `binance BTC` @500 at the same step gained 3.5% (Round 360) — the ladders differ by route.
- The hold-72 arm reproduced exactly (−1.00705, 229 trades) across a 4-candle window shift.

Not proven, and deliberately not claimed:

- **That the gain is edge rather than cost.** Not decomposable with the current tooling.
- **That the ladder does not saturate beyond 144 on XAU.** Untested; `binance BTC` looked monotone
  at 72 and was nearly flat by 144, so extrapolation is exactly the mistake to avoid.
- That the 36-hold row is strictly same-window with the other two. It is quoted across a 4-candle
  gap, justified empirically by the 72-arm reproducing exactly — **the 72 → 144 comparison, which
  is what was registered, is fully in-round**.
- That this helps the joint objective. Frequency drops 39% on a route already failing Target 3 by
  a wide margin at every hold tested.
- Any promotion. Unchanged and structural: `--portfolio-minimum-hold-decisions` conflicts with
  `--daily-profit-gate`, so **no holdout score exists for this parameter** and promotion condition
  1 cannot be met.
