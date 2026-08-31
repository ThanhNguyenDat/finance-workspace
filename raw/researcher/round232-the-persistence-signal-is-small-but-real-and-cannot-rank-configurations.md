# Round 232 — Applying Round 230's rule to Round 231's own statistic: the pooled lift is real (z=3.22) and no single configuration can be ranked

Classification: **NO-CHANGE**. No containers — twelve saved sweeps re-read.

## Why this check

Round 230 ended with a mechanical rule: **report all three splits and the spread,
or report nothing.** Round 231 then reported a single obs/exp value per run and
singled out one — "exness BTC 4h+1d at 2.10x, the highest legitimate value and
where the little signal lives" — without a spread.

That is the same error one round later, applied to a new statistic. This round
runs the check Round 230's rule demands.

## The spread of the statistic itself

**Same configuration (BTC 4h+1d), varying only broker, window and partition:**

| variant | expected | observed | obs/exp | z |
|---|---|---|---|---|
| exness 1800d 60/20/20 | 3.33 | 7 | 2.10 | 2.01 |
| binance 1800d 60/20/20 | 4.01 | 5 | 1.25 | 0.49 |
| bybit 1800d 60/20/20 | 3.04 | 5 | 1.64 | 1.12 |
| binance 1800d 40/20/40 | 4.01 | 9 | 2.24 | 2.49 |
| binance 1200d 50/20/30 | 5.99 | 10 | 1.67 | 1.64 |
| binance 900d 40/20/40 | 4.03 | 11 | **2.73** | **3.47** |
| binance 900d 60/20/20 | 2.67 | 1 | **0.37** | −1.02 |

**Range 0.37 to 2.73 — a 7.3x spread for what is essentially one
configuration.** XAU 4h variants span 0.00 to 1.54 (median 0.86), including two
configurations with **zero** observed against ~1 expected.

Round 231's 2.10 is an unremarkable draw from that distribution. Its z is 2.01,
and the highest z in the whole table (3.47) belongs to **binance 900d 40/20/40** —
the very window where Round 225 measured the best candidate collapsing. High
population persistence in a window implies nothing about any candidate in it.

## But pooling strengthens Round 231's actual finding

Treating the counts as Poisson:

| | value |
|---|---|
| individual configurations with \|z\| > 2 | 3 of 12 |
| \|z\| > 3 | 1 of 12 |
| **pooled expected** | **34.19** |
| **pooled observed** | **53** |
| **pooled ratio** | **1.55** |
| **pooled z** | **3.22** |

So both halves of Round 231 need adjusting, in opposite directions:

- **Its aggregate claim is confirmed and sharpened.** The lift is not "barely
  above chance" in the sense of being indistinguishable from it — pooled z=3.22
  means the population does carry a small, real persistence signal. 1.55x, not
  nothing.
- **Its ranking claim is withdrawn.** No configuration can be singled out; the
  0.37-2.73 range is what Poisson noise on counts of 0-11 produces, and the
  three configurations exceeding |z|=2 are spread across brokers and windows with
  no pattern.

## The resulting position, stated once

> **The candidate population carries a real but small persistence signal —
> roughly 1.5x the chance rate, pooled over ~700 candidate-evaluations. It is far
> too small to make any individual configuration, window, broker or candidate
> identifiable, which is exactly why every candidate that cleared the bar in
> Rounds 222-230 failed the next independent test.**

That is a coherent explanation of the whole session rather than a tally of
disappointments, and it is compatible with both a genuinely weak edge existing
somewhere and with none of the tested mechanisms being the one carrying it.

## Note on my own error rate

This is the fourth self-correction in this session (Rounds 219, 226, 230, and
now 232 correcting 231). Three of the four were the same failure: quoting one
favourable number without its spread. Round 230 wrote the rule; Round 231 broke
it immediately; this round applied it.

The rule is not the problem — remembering to apply it to *new* statistics, not
just the ones it was written for, is. Recorded so it generalises: **the spread
requirement applies to any statistic this program reports, including statistics
invented to evaluate other statistics.**

## What is proven, and what is not

Proven:

- obs/exp for twelve configurations ranges 0.37-2.73 (BTC 4h+1d) and 0.00-1.54
  (XAU 4h).
- Pooled expected 34.19 against observed 53: ratio 1.55, z = 3.22.
- 3 of 12 configurations exceed |z| = 2; the maximum (3.47) is binance BTC 900d
  40/20/40.

Not proven, and deliberately not claimed:

- That the pooled z is a clean significance test. The twelve runs overlap heavily
  in candidates and data, so they are not independent samples and the pooled z is
  optimistic.
- That any configuration is better than another. That is precisely what this
  round rejects.
- That a real edge exists in the registry. A 1.55x population lift is compatible
  with a small number of weakly-persistent mechanisms and with none of the ones
  tested being promotable.
