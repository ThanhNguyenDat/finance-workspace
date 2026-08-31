# Round 253 — The long/short asymmetry hypothesis fails: BTC's up-trending band was its *worse* band

Classification: **REJECTED** — the hypothesis Round 252 named is refuted on the
independent instrument. Re-analysis of retained Round 250/251 data; two container
starts produced nothing (see "Budget" below).

## The test Round 252 named

Round 252 closed with one explicitly-untested observation: the two strong bands
are directional in **opposite** directions — XAU's drift +16.89% (uptrend), BTC's
−48.18% (downtrend) — and *"a strategy population that handles uptrends better
than downtrends would produce exactly the observed pattern."* It named the test:
**measure candidate performance in up-trending versus down-trending segments.**

That test does not need new backtests. Rounds 250 and 251 retained per-mechanism
edges for **both bands on both instruments** under an identical, pre-committed
dedup rule, and Round 252 measured the drift of each band. The four cells are
already on record; what was never done is **grouping them by trend direction
instead of by calendar band.**

## The four cells

| instrument | band (days ago) | drift | trend | median edge (7 directional mechanisms) |
|---|---|---|---|---|
| exness XAU | 0-150 | −6.43% | DOWN | +0.00099 |
| exness XAU | 150-300 | +16.89% | **UP** | **+0.00874** |
| binance BTC | 0-150 | +12.21% | **UP** | **−0.00294** |
| binance BTC | 150-300 | −48.18% | DOWN | +0.00268 |

**BTC's up-trending band is the only negative cell of the four.** On the
independent instrument, the up-trending window was not better than the
down-trending one — it was worse, and it was the single worst band measured.

## The same 14 numbers, two labelings

The 14 mechanism-band measurements are identical in both groupings. Only the
label changes.

| grouping | XAU | BTC | instruments agreeing | pooled | nominal p |
|---|---|---|---|---|---|
| **A — by calendar band** (150-300 > 0-150) | 7/7 | 5/7 | **2/2** | 12/14 | 0.0129 |
| **B — by trend direction** (up-band > down-band) | 7/7 | **2/7** | **1/2** | 9/14 | 0.4240 |

Under the calendar-band label both instruments point the same way. Under the
trend-direction label they point in opposite directions, because BTC's assignment
flips. **Trend direction explains nothing that calendar band did not already
explain, and it destroys the cross-instrument consistency that band has.**

## Why this is the only evidence available, and how weak it is

Within a single instrument, calendar band and trend direction are **perfectly
confounded** in this dataset: each instrument has exactly two bands, one up and
one down, so every within-instrument comparison is simultaneously a band
comparison and a direction comparison. XAU's 7/7 supports both stories equally
well and cannot discriminate between them.

**The only discriminating evidence is cross-instrument consistency** — and that is
**n = 2**. One instrument agrees with the direction story, one contradicts it.
The honest summary is not "direction is disproven"; it is that the one
independent draw available went against it, and band survives that same draw
while direction does not.

The nominal p-values above carry the Round 251 deflation unchanged: seven
mechanisms on one instrument over one 150-day window are seven views of one price
path, not seven independent trials. **p = 0.0129 is overstated**, and it is
reported here only because grouping B must be scored the same way to be
comparable — the comparison between the two rows is the result, not either row's
absolute value.

## Where this leaves the thread

Rounds 242-248's shared favourable calendar window stands, and now stands a
little more firmly: the third candidate explanation for it has failed, and it
failed on the instrument that matters.

- Round 252 refuted **directionality magnitude** as the explanation of the
  instrument gap (it pointed backwards).
- This round refutes **long/short asymmetry** as the explanation (it disagrees
  across instruments).
- What remains: the effect tracks **calendar time**, shared across instruments,
  and the cross-instrument *magnitude* difference is still unexplained.

Nothing here changes the standing result that loss ≈ trade count × a near-constant
and that no Portfolio-construction lever improves per-trade economics.

## Budget — two container starts, zero yield

Two sweeps were launched to add a **300-450 day** third band per instrument
(`--days 450 --train-ratio 0.3333 --validation-ratio 0.3333`, 4h, zero cost),
which is what would break the band/direction confound properly. Both were started
with `docker run -d --rm` and **exited in ~24s before their stdout was captured**;
`--rm` then destroyed them, so the output is gone. Both cleaned up, nothing leaked,
tunnel closed and verified with `ss` (0 listeners).

That is my invocation error, not a tool failure. **The round's 2-container budget
was spent for no evidence, so no further containers were run.** The fix for next
round: redirect to a file at launch —
`docker run -d --name <n> ... > /dev/null` is not enough; either drop `--rm` and
read `docker logs` after exit, or run attached and pipe stdout to a file.

## What is proven, and what is not

Proven:

- Regrouping the retained Round 250/251 tables by trend direction gives XAU 7/7
  and BTC 2/7 — instruments disagree (1/2). Regrouping the same 14 numbers by
  calendar band gives 7/7 and 5/7 — instruments agree (2/2).
- BTC's up-trending band (0-150, drift +12.21%) has median edge −0.00294, the
  only negative cell of the four and lower than its own down-trending band
  (+0.00268).

Not proven, and deliberately not claimed:

- That long/short asymmetry does not exist anywhere in the candidate population.
  One independent instrument contradicted it; that is n = 2, not a disproof.
- Any statistical weight for either grouping's p-value. Both are inflated by the
  shared-price-path problem; only their *comparison* is used here.
- That the 300-450 band would behave as predicted. It was not measured.
- Any explanation for the cross-instrument magnitude gap. Still open after two
  refuted candidates.
