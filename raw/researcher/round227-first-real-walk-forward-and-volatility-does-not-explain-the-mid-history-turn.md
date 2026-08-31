# Round 227 — The first real walk-forward on XAU, and the one segment that breaks the volatility explanation

Classification: **NO-CHANGE**. Two bounded Docker sweeps plus one read-only query.

## The walk-forward Rounds 219-220 asked for, now possible

Round 219 asked for a walk-forward. Round 220 concluded it was not expressible:
`--days` only moves the start and the holdout is always the tail, so no interior
holdout can be placed.

Round 226 removed that obstacle without changing any tooling. It proved **each
split is evaluated independently of preceding history** — identical results for a
fixed holdout under 1,800 / 1,200 / 900 days of prior data. That makes the
**train and validation splits themselves valid interior segments**. Setting
`--train-ratio k*0.2 --validation-ratio 0.2` reads segment *k* directly.

Five non-overlapping ~360-day segments of exness XAU 4h, cells with >= 30 trades:

| segment | cells | median trades | friction/trade | edge/trade | **ratio** | % edge > 0 | PF>1 cells |
|---|---|---|---|---|---|---|---|
| S1 1800→1440 ago | 42 | 104 | 0.00703 | −0.00080 | **−0.114** | 45% | 6 |
| S2 1440→1080 ago | 41 | 109 | 0.00701 | −0.00185 | **−0.264** | 41% | 5 |
| S3 1080→720 ago | 41 | 97 | 0.00712 | +0.00108 | **+0.151** | 59% | 11 |
| S4 720→360 ago | 43 | 88 | 0.00722 | +0.00114 | **+0.158** | 56% | 11 |
| S5 360→0 ago | 40 | 110 | 0.00713 | +0.00470 | **+0.659** | 70% | 14 |

Friction is flat to within 3% across five years — a sixth independent
confirmation that it is a fixed per-trade toll.

The trend is a step, not a drift: **two clearly negative segments, then three
positive ones**, with the positive share climbing 41% → 59% → 56% → 70% and the
PF>1 count 5 → 11 → 11 → 14.

This replaces Round 220's gradient — inferred from nested windows — with a direct
segment-by-segment measurement. It confirms the gradient exists and is not an
artifact of nesting.

## The segment that breaks the volatility story

Round 221 attributed roughly half the recent advantage to gold's volatility
doubling. Pairing each segment's ratio against its own realised volatility:

| segment | median \|4h return\| | vs S1 | ratio |
|---|---|---|---|
| S1 | 0.1549% | 1.00x | −0.114 |
| S2 | 0.1520% | 0.98x | −0.264 |
| **S3** | **0.1471%** | **0.95x** | **+0.151** |
| S4 | 0.1820% | 1.17x | +0.158 |
| S5 | 0.3143% | 2.03x | +0.659 |

**S3 has the lowest volatility of all five segments and a clearly positive
ratio, while S1 and S2 at higher volatility are negative.**

If volatility drove the ratio, S3 would be the worst segment. It is the third
best. Concordance across all pairs is 8 of 10, and the two discordant pairs are
exactly S3 against S1 and S2.

So the attribution splits cleanly by era:

- **S4 → S5** (0.158 → 0.659 while volatility goes 1.17x → 2.03x): consistent
  with Round 221 — largely the volatility effect against a fixed toll.
- **S2 → S3** (−0.264 → +0.151 while volatility *falls* to 0.95x): **not
  explicable by volatility.** Something changed in how tradable gold 4h was,
  around 1,080 days ago, at constant-to-falling volatility.

That is a sharper statement than Round 221's "half artifact, half real": the real
half is **located**, in the S2→S3 transition, and the artifact half is located in
S4→S5.

## What is proven, and what is not

Proven:

- Five-segment walk-forward ratios: −0.114, −0.264, +0.151, +0.158, +0.659, with
  friction flat at 0.00701-0.00722 throughout.
- Segment volatility: 0.1549%, 0.1520%, 0.1471%, 0.1820%, 0.3143%.
- S3 combines the lowest volatility with a positive ratio; 8 of 10 pairs are
  concordant, both discordant pairs involving S3.

Not proven, and deliberately not claimed:

- Statistical significance of any of it. Five segments, medians over ~40 cells
  each, no test performed. The concordance count is descriptive.
- What changed around 1,080 days ago. The data says *that* something changed at
  constant volatility, not *what*.
- That any segment is tradable. The best of five is 0.659, and Round 221 showed
  that falls to ~0.32 under volatility-adjusted friction. **No segment in five
  years reaches break-even.**
- Anything about BTC, other intervals, or other sources.
