# ⚠️ QUALIFICATION (Round 220)

The favourable end of this file's range (**holdout +0.659 at 4h**) sits in the
segment where the friction model is least trustworthy. Round 220 measured gold's
4h volatility as **2.07x higher** in the last 20% of the window than in the first
60%, while modelled friction moved **+3%**. Since real spread and slippage widen
with volatility, a fixed-bps model understates friction exactly there — so the
recent advantage can only shrink under correction. The interval *ordering* is
unaffected (all intervals share the same window and volatility profile).
See `round220-the-recent-advantage-rides-on-doubled-volatility-and-flat-modelled-friction.md`.

---

# Round 219 — Matched window: the interval ordering survives, the "1.5x gap" does not. It was a holdout-only number and train disagrees

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps (within
budget, after last round's overrun).

## What Round 218 left open, and why it mattered

Round 218 headlined a **~1.5x gap at 4h** (edge/friction ratio 0.659) against
~18x at 5m, and named its own weakness: the 4h figure came from a 1,800-day
window while 5m and 1h came from 365 days, so interval was confounded with
window. The missing measurement was a matched-window comparison.

This round runs **1h on the same 1,800-day window** as the existing 4h data.

## Result 1 — the ordering survives

Holdout, cells with >= 30 trades, identical 1,800-day window:

| interval | cells | median trades | friction/trade | edge/trade | **ratio** |
|---|---|---|---|---|---|
| 1h | 61 | 195 | 0.00701 | +0.00144 | **+0.206** |
| 4h | 40 | 110 | 0.00713 | +0.00470 | **+0.659** |

4h still beats 1h by roughly 3x on matched data. Round 218's *direction* — the
gap narrows as the interval lengthens — holds up under the control it was missing.

## Result 2 — but the magnitude does not survive, and the fault is mine

Splitting the same runs by split rather than reporting holdout alone:

| interval | train | validation | **holdout** |
|---|---|---|---|
| 1h / 1800d | +0.035 | +0.000 | **+0.206** |
| 4h / 1800d | **−0.029** | +0.158 | **+0.659** |

On **both** intervals the holdout ratio is several times better than train and
validation, and at 4h the train ratio is **negative**.

Round 217, Round 218 and the summary entries built on them quote the holdout
figure. That was defensible as an out-of-sample choice, but reporting only the
best of three splits without showing the other two made a favourable regime look
like a property of the interval. The honest statement of the 4h ratio is:

> **between −0.03 and +0.66 depending on split, median across splits ≈ 0.16.**

Which turns the "~1.5x gap" into roughly **3-6x**, depending on which split one
believes. Better than 5m's ~18x, and not the near-reachable number Round 218
presented.

The pattern is not subtle and it is consistent across both intervals: the last
20% of the 1,800-day window is simply a friendlier regime for these mechanisms.
That is exactly what Round 211 measured from the other direction — a per-split
figure is a property of the strategy **and** the window **and** the partition —
and I did not apply it to my own headline.

## Result 3 — a third confirmation of window sensitivity

1h's holdout ratio was **0.331 on 365 days** and is **0.206 on 1,800 days** — the
same interval, same source, same engine, same metric, 38% lower on the longer
window. Rounds 211 and 212 measured this effect; this is a third independent
instance of it, now on the edge/friction metric rather than on PF.

Also worth recording: 1h/1800d has **pass@cost = 0** against 4h's 2, so the
interval with more cells and more trades per cell passes nothing at all.

## What the next round should do instead

The single-split reading is the problem, and both remaining fixes are concrete:

1. **Walk-forward rather than one 60/20/20 cut.** The tool exposes
   `--train-ratio` and `--validation-ratio`; running several staggered partitions
   over the same 1,800 days and taking the distribution of the ratio would
   replace one draw with several. Round 212's four-window profile did this for
   the PF bar; nobody has done it for edge/friction.
2. **Report the ratio as a range across splits, never as a single number.** This
   round is the evidence for why.

## What is proven, and what is not

Proven:

- Matched 1,800-day window, holdout: 1h ratio +0.206 (61 cells), 4h +0.659
  (40 cells). Friction per trade 0.00701 and 0.00713 — flat, as before.
- Per-split ratios: 1h +0.035 / +0.000 / +0.206; 4h −0.029 / +0.158 / +0.659.
- 1h's holdout ratio falls from 0.331 (365d) to 0.206 (1800d).
- 1h/1800d passes 0 of 77 candidates at production cost; 4h/1800d passes 2.

Not proven, and deliberately not claimed:

- That 4h's advantage is regime-independent. Its train ratio is negative; only
  a walk-forward can say whether the holdout result repeats.
- That the median-across-splits figure (~0.16 at 4h) is the right summary either.
  It is one more single number over three unstable draws; the range is the honest
  object until a walk-forward exists.
- Anything about 5m on the 1,800-day window. It was not run this round — two
  containers, deliberately, after last round's four.
- Anything about real friction. Round 215's limitation is unchanged.
