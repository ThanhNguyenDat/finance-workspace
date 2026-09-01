# RESOLVED (Round 221)

This file measured the 2.07x volatility gap and declined to attribute how much of
the time gradient was artifact. Round 221 made the attribution by charging the
recent segment its volatility-implied friction: the holdout ratio falls
**0.659 -> 0.318**, still well above the old era's **-0.029**. The gradient is
roughly **half artifact, half real** — this file's suspicion was right in
direction and too pessimistic in degree.
See `round221-half-artifact-half-real-volatility-adjusted-4h-ratio-is-0.32.md`.

---

# Round 220 — The recent-period advantage rides on a 2.07x volatility increase while modelled friction stayed flat

Classification: **DATA-ISSUE**. A modelling limitation with a measured magnitude
and a known direction. Two bounded Docker sweeps plus one read-only query.

## Two questions, one answer

Round 219 showed the edge/friction ratio at 4h is a **range** across splits
(−0.029 train, +0.158 validation, +0.659 holdout) and asked for a walk-forward.

**Tooling note first:** a true walk-forward is not expressible with the current
flags. `--train-ratio` and `--validation-ratio` move the partition boundaries but
the holdout is always the **tail** of the window, and `--days` only moves the
start. There is no way to place a holdout segment in the middle of history. So
the requested experiment cannot be run as specified — recorded so the next round
does not rediscover it.

What *can* be varied is holdout **length**, which answers the more pointed
question: is the favourable holdout a short recent spike, or a broad regime?

## Result 1 — a time gradient, not a cliff

4h / 1,800 days, cells with >= 30 trades:

| partition | train | validation | holdout | holdout span |
|---|---|---|---|---|
| holdout = last 20% | −0.029 (47% pos) | +0.158 (56%) | **+0.659** (70%) | ~360d |
| holdout = last 40% | −0.061 (47% pos) | +0.151 (59%) | **+0.452** (55%) | ~720d |

Doubling the holdout drops the ratio 0.659 → 0.452 and the positive share
70% → 55%. Train and validation barely move under repartitioning (−0.029/−0.061,
+0.158/+0.151) — they are stable; only the holdout is sensitive.

Read across the window rather than by split name, the picture is a monotone
gradient in time: **older data ≈ −0.03 to −0.06, middle ≈ +0.15, recent ≈ +0.45
to +0.66.** The edge-to-friction ratio has been improving across the five years.

## Result 2 — and most of that gradient is volatility against a fixed toll

Realized volatility of the same series, by the same segments (median absolute 4h
log return, 7,880 bars, 2021-09-24 to 2026-08-28):

| segment | bars | median \|4h return\| | median bar range | vs train |
|---|---|---|---|---|
| train (first 60%) | 4,728 | 0.1521% | 0.385% | 1.00x |
| validation (60-80%) | 1,576 | 0.1820% | 0.456% | 1.20x |
| **holdout (last 20%)** | 1,576 | **0.3143%** | **0.769%** | **2.07x** |
| holdout (last 40%) | 3,152 | 0.2377% | 0.593% | 1.56x |

**Gold's 4h volatility roughly doubled between the early and recent parts of the
window. Modelled friction over the same segments moved 0.00693 → 0.00713, i.e.
+3%.**

Edge per trade scales with the size of the moves being traded. Friction in this
model does not scale with anything — it is a fixed basis-point toll. So a
doubling of volatility mechanically lifts the ratio even with no improvement in
the signal whatsoever.

Volatility does not explain *all* of it: normalising edge per trade by segment
volatility still leaves the recent segments ahead. But that residual is not the
point. **The point is the direction of the modelling error.** In real markets
spread and slippage widen with volatility; a fixed-bps friction model therefore
**understates** friction precisely in the high-volatility recent segment — the
one carrying the favourable result. Correcting for it can only shrink the recent
advantage, never grow it.

## What this does to the last four rounds

Rounds 217-219 built a story: the gap is ~18x at 5m, ~3x at 1h, and best at 4h.
Round 219 already corrected the 4h magnitude from "1.5x" to a −0.03..+0.66 range.
This round adds that **the favourable end of that range sits in the segment where
the friction model is least trustworthy**, and quantifies how much less
trustworthy: 2.07x the volatility, 1.03x the modelled friction.

The interval *ordering* is not affected — 5m, 1h and 4h were all measured over
the same window and share the same volatility profile, so the comparison between
them is internally consistent. What is affected is any absolute claim about how
close 4h is to break-even.

This is the concrete form of Round 215's standing caveat. "Friction is a model,
not a measurement" was an abstract disclaimer for five rounds. It now has a
measured magnitude and a known sign.

## What is proven, and what is not

Proven:

- 4h/1800d with holdout at 20% vs 40%: holdout ratio +0.659 vs +0.452, positive
  share 70% vs 55%; train and validation are stable across the repartition.
- Median absolute 4h return by segment: 0.1521% / 0.1820% / 0.3143%, a 2.07x
  train-to-recent increase, against modelled friction moving +3%.
- A true walk-forward with an interior holdout cannot be expressed by the current
  CLI flags.

Not proven, and deliberately not claimed:

- How much of the gradient is volatility and how much is genuine. Volatility
  normalisation leaves a residual; no attempt was made to attribute it, and the
  train base being negative makes ratio-of-ratios arithmetic unreliable.
- What real friction was in each segment. That would need actual fills, which
  this system has never produced (production runs simulated `paper-*` ledgers).
  The claim here is directional, not quantified: fixed-bps friction understates
  high-volatility periods.
- That the interval ordering is wrong. It is not challenged by this round.
