# "WIDER IS BETTER PER TRADE" DOES NOT GENERALISE EITHER (Round 367)

This file refuted the constant-per-trade rule by showing the wide band improves `exness XAU`
per-trade economics **+62.5%**. The tempting replacement fails too: the **same** widening at hold
36 on `binance BTC` makes per-trade economics **worse** — −0.006892 → **−0.008199 (−19.0%)**.

The band's per-trade effect is **not universal in sign**. See `round367-REJECTED-no-band-hold-setting-is-both-profitable-and-at-target-3-the-break-even-frequency-is-25-percent-below-the-bar.md`.

---

# THE BAND AND HOLD LEVERS COMPOSE — AND THE CORNER TURNS POSITIVE (Round 365)

This file measured the band's per-trade effect at hold 36 as **+62.5%**. At hold **288** the same
band step is worth **+566.8%** and **crosses zero**: `band 0.02/0.04 + hold 288` gives
`one_target` **+1.17395** on 83 trades (**+0.014144 per trade**) — the first positive full-window
PnL at deployed costs in this arc. All five cells share `candle_count` 57,934.

So the two levers are **distinct, not the same mechanism**, and they compose super-additively.
The corner also trades **1.94 per week — a 3.6x Target 3 miss** — has **no holdout score and
cannot have one**, and was found by a ~16-cell search on one window. See `round365-NEEDS-MORE-RESEARCH-band-and-hold-compose-super-additively-into-the-first-positive-pnl-at-deployed-costs.md`.

---

# Round 364 — REJECTED: the standing rule *"loss ≈ trade count × a near-constant"* is **refuted** for the fractional band. Widening 0.01/0.02 → 0.02/0.04 makes each trade **62.5% better**, while funding cost per trade rises **47%** — the gain is **quality, not count**.

Classification: **REJECTED** — a rule this arc has carried since Round 96 fails on a
validity-gated same-window test. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**.

## Applying Round 363's instrument to a closed direction

Round 363 produced a technique: when the gross/cost split is unobtainable, **net PnL per trade
plus `funding_paid` per trade** separates "fewer trades" from "better trades" — because funding is
the one cost component that provably varies with holding time, and if it moves *against* an
improvement then the improvement is not cost removal.

The band direction was closed in Rounds 330-341 on gate runs, and the standing economic rule since
Round 96 — restated in Round 274 — is that **per-trade economics are near-constant across band
settings**, so the band only buys frequency and pays for it proportionally. That rule had never
been tested with this instrument on the `one_target` path.

**Pre-registered as a partition:** Q = net PnL per trade. **|ΔQ| / |Q_deployed| ≥ 5%** → the band
changes trade quality and the constant-per-trade rule fails; **< 5%** → it holds and the band is a
pure frequency/cost knob.

## Validity

`candle_count` **57,934** in both arms — identical window. **Note the control differs from Round
363's**: `legacy_selected_rule` is *not* invariant here (345 → 214 trades, −1.633800 → −0.845140),
because the band affects the ungated ledger too. The `candle_count` match is what establishes the
window; there is no free drift control for a band comparison.

## Result

`exness XAU` @300, hold 36:

| band | trades | trades/week | `one_target` PnL | **PnL/trade** | funding/trade |
|---|---|---|---|---|---|
| 0.01/0.02 (deployed) | 270 | 6.30 | −1.57256 | **−0.005824** | −0.000354 |
| **0.02/0.04** | 186 | 4.34 | **−0.40571** | **−0.002181** | **−0.000522** |

**Q changes by 62.5% — far past the 5% line. The registered branch fires and the constant
per-trade rule is refuted.**

Decomposing the **74.2%** PnL improvement:

- trades **−31.1%**
- **PnL per trade +62.5%**
- funding per trade **−47.4% (worse)** — cost per trade *rose*, so per-trade **gross** improved by
  more than the net figure

**Most of the gain is quality, not count.** That is the opposite profile to the hold ladder:

| lever (same route, window, hold/band held fixed) | Δ trades | Δ PnL/trade | dominated by |
|---|---|---|---|
| hold 72 → 144 (Round 363) | −28.4% | **+2.7%** | count |
| **band 0.01 → 0.02 (this round)** | −31.1% | **+62.6%** | **quality** |

Two levers that cut trades by almost the same amount do completely different things to the trades
that remain.

## What this does and does not reopen

Round 274's measurement stands as a measurement — it used an **ATR** band on a **different window**
and found 0.93x per-trade. What fails is the **generalisation** it drew: *"what survives any
calibration is the per-trade constant."* On the fractional band at this route and window the ratio
is **0.37x**, not 0.93x.

It does **not** reopen the band as a candidate on the evidence here:

- **Still a loss.** −0.40571 over 300 days.
- **Target 3 still fails**, and by more: 6.30 → **4.34 per week** against a 7.0 bar the route
  already missed.
- **This is full-window `one_target`**, not a holdout score. Rounds 330-341 closed the band on
  **holdout** gate runs, and those verdicts are not overturned by a full-window number.
- The direction of the effect **agrees** with the gate runs anyway (Round 335's refined @500 grid
  also improved with width: −0.2283 at 0.01 against −0.0301 at 0.02), so this is a sharper reading
  of the same direction, not a contradiction of it.

## What is proven, and what is not

Proven:

- Identical `candle_count` (57,934) across both arms.
- `exness XAU` @300, hold 36: 0.01/0.02 → 270 trades / −1.57256 / −0.005824 per trade /
  −0.000354 funding per trade; 0.02/0.04 → 186 / −0.40571 / **−0.002181** / **−0.000522**.
- Q changes 62.5%; the PnL improvement decomposes as −31.1% trades and +62.5% per trade with
  funding per trade 47.4% worse.
- The contrast with Round 363's hold step at nearly the same trade reduction.

Not proven, and deliberately not claimed:

- **That the band is a viable candidate.** Full-window, still losing, and Target 3 gets worse.
- **That per-trade quality improves without limit with width.** Two points. Rounds 330-341 found
  an interior optimum on the gate path and a trough, so width is not monotone there.
- That the improvement is edge rather than an unobserved cost component. Funding is the only cost
  that provably varies here and it moves against the improvement; fee and slippage per trade are
  not separately observable — the argument is **directional, not a decomposition** (same standing
  limit as Round 363).
- That Round 274 is wrong. Its ATR measurement stands; only the generalisation to all band
  calibrations fails.
- Any promotion. No holdout evidence, and the joint objective moves the wrong way.
