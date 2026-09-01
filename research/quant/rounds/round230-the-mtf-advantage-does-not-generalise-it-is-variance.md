# Round 230 — The MTF "advantage" does not generalise to BTC and is negative on two of three XAU splits: it is variance, not edge

Classification: **REJECTED**. No containers — the test was answerable from saved
runs, and it rejects the direction I opened last round.

## What Round 229 claimed, and the check it did not run

Round 229 reported the MTF family on XAU holdout at ratio **+4.571**, called it
"the highest edge-to-friction ratio this program has measured anywhere", and
noted it stays above break-even (~2.3) even after Round 221's volatility
adjustment.

It quoted **one split**. The obvious check — do the other two splits agree, and
does the effect appear on BTC — was not run. It is run here, from saved data.

## Result — it fails both checks

| instrument | group | ratio train / validation / holdout | spread | median trades t/v/h |
|---|---|---|---|---|
| XAU | **MTF** | +0.371 / **−1.954** / +4.571 | **6.525** | 85 / 39 / 40 |
| XAU | single-timeframe | −0.031 / +0.158 / +0.659 | 0.690 | 182 / 88 / 110 |
| BTC | **MTF** | +1.458 / **−1.086** / **−1.563** | **3.021** | 99 / 50 / 51 |
| BTC | single-timeframe | +0.125 / −0.540 / +0.165 | 0.705 | 278 / 152 / 134 |

**On XAU the MTF family's validation ratio is −1.954** — the same population,
the adjacent split, deeply negative. **On BTC it is negative on both
out-of-sample splits** (−1.086, −1.563) and positive only on train.

The +4.571 was the best of three cells from the noisiest population in the run.

## The mechanism is arithmetic, not market structure

| instrument | MTF split-spread vs single-timeframe | trades per cell |
|---|---|---|
| XAU | **9.5x** larger | 2.3x fewer |
| BTC | **4.3x** larger | 2.8x fewer |

MTF candidates trade roughly a third as often, and their ratio swings across
splits are four to nine times wider. That is what a smaller sample does to a
per-trade statistic. Round 229's own table showed the trade counts (40 median on
holdout against 110) and I read the ratio without reading the variance that
comes with it.

## ⚠️ Correcting Round 229

The claim that trend filtering produces a real edge advantage on XAU is
**withdrawn**. What Round 229 measured was a higher-variance population, sampled
at its favourable split, on the instrument and segment that flatters every
population (Round 227's S5).

What survives from Round 229 is narrower and still true:

- No MTF candidate clears the PF bar on XAU; the funnel is empty. That stands.
- The trade-floor incompatibility with low-frequency mechanisms stands — but it
  is now the *whole* story rather than half of it. There is no suppressed edge
  behind the floor; the floor is screening out a population whose apparent edge
  does not survive looking at the other two splits.

The two-problem framing of Round 229 — "measurement limitation" versus "real
historical weakness" — was too generous to the first. Both splits that could have
confirmed an edge instead contradict it.

## The recurring error, stated plainly

This is the third time in this session I have quoted a favourable split as if it
were a property:

- Round 218: quoted the 4h holdout ratio 0.659 as "a ~1.5x gap" — corrected in
  Round 219 when train read −0.029.
- Round 225: built a path-dependence mechanism on a boundary arithmetic error —
  corrected in Round 226.
- Round 229: quoted the MTF holdout ratio 4.571 as the best ever measured —
  corrected here when validation reads −1.954.

The pattern is consistent: **a single split from a small-sample population, read
without its spread.** Rounds 210, 211 and 219 all measured why this is wrong. The
operational fix is mechanical rather than attitudinal: **report all three splits
and the spread, or report nothing.** Applied from here.

## What is proven, and what is not

Proven:

- XAU MTF ratios by split: +0.371 / −1.954 / +4.571; BTC MTF: +1.458 / −1.086 /
  −1.563.
- Single-timeframe spreads are 0.690 (XAU) and 0.705 (BTC); MTF spreads are 6.525
  and 3.021, i.e. 9.5x and 4.3x wider.
- MTF median trades per cell are 2.3x (XAU) and 2.8x (BTC) lower.

Not proven, and deliberately not claimed:

- That trend filtering is useless. It reduces trade count as designed, and Round
  229's funnel still shows zero survivors either way; what is rejected is the
  claim of a measured *edge* advantage.
- That the wide spreads are purely sampling. Regime differences between splits
  (Round 227) contribute; no decomposition was attempted.
