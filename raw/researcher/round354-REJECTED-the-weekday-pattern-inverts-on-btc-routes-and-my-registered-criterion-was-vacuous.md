# Round 354 — REJECTED: the `exness XAU` weekday pattern **inverts** on both BTC routes — Wednesday goes from **worst** to **best**, Friday from **best** to **worst**. My registered criterion fired "systematic", and it was **vacuous**. Separately, Wednesday's loss looks like **edge**, not cost.

Classification: **REJECTED** — the transfer hypothesis is refuted by the discriminating comparison,
and my own pre-registration is the fourth defective one in this loop. Two bounded Docker sweeps
(exactly the 2-container budget), **XAU-first** in origin.

## Part 1 — the question Round 353 said decides everything

Round 353 closed on: *"`daily_results` carries `realized_pnl`, which is **net**. Whether
Wednesday's edge is negative or merely more expensive is not determinable — and that distinction
decides whether a filter would help at all."*

Zeroing costs would give gross per day, but Round 348 established that
`(fee + slippage) × 2 > 10` is what blocks reversals, so **any cost setting low enough to isolate
gross also changes the action space**. Gross-by-weekday with the deployed decision stream is
**unobtainable**. That block is real and I am recording it rather than working around it badly.

What *is* available is an activity proxy: a day with `realized_pnl == 0` closed no trade.

**Pre-registered as a partition:** A_wed = share of Wednesday rows that are non-zero; A_other =
the same for Mon/Tue/Thu/Fri.
- **A_wed ≥ A_other × 1.15** → Wednesday trades materially more, so cost stays a live explanation;
- **A_wed < A_other × 1.15** → it does not, and negative edge is the favoured reading.

`exness XAU` @1800, 306 holdout days:

| weekday | n | active | activity rate | mean \|PnL\| on active days | wins | losses |
|---|---|---|---|---|---|---|
| Mon | 51 | 44 | 0.863 | 0.04243 | 22 | 22 |
| Tue | 51 | 42 | 0.824 | 0.03979 | 21 | 21 |
| **Wed** | 51 | 42 | **0.824** | **0.04699** | **18** | **24** |
| Thu | 52 | 44 | 0.846 | 0.02397 | 27 | 17 |
| Fri | 52 | 44 | 0.846 | 0.05074 | 24 | 20 |

**A_wed = 0.8235 against A_other × 1.15 = 0.9714 — the negative-edge branch fires.** Wednesday is
if anything **less** active than average. Its day-level win rate is **0.429 (18/42) against 0.540**
elsewhere, and its moves are **1.20x larger** in magnitude. Fewer wins, bigger swings, same
activity — that is a directional story, not a cost story.

## Part 2 — the fresh cross-route test, and why my criterion was worthless

The Wednesday hypothesis was derived from `exness XAU` alone, so applying it to routes it was
never formed on **is** a fresh test — the thing Round 353 said it lacked.

**Pre-registered:** Wednesday's mean PnL is negative on **both** `exness BTC` @1800 and
`binance BTC` @1800 → systematic across routes; non-negative on either → specific to `exness XAU`.

| route | Mon | Tue | Wed | Thu | Fri | best | worst |
|---|---|---|---|---|---|---|---|
| `exness XAU` | −0.00062 | −0.00473 | **−0.01603** | +0.00474 | **+0.01043** | **Fri** | **Wed** |
| `exness BTC` | −0.02337 | −0.01260 | **−0.01196** | −0.02867 | **−0.04116** | **Wed** | **Fri** |
| `binance BTC` | −0.01653 | −0.01026 | **−0.01148** | −0.03125 | **−0.04547** | Tue | **Fri** |

Wednesday is negative on both BTC routes, so **the registered criterion fires "systematic".**

**It is vacuous.** *Every* weekday is negative on both BTC routes — they lose overall (net
−6.6188 and −6.4102, on **negative gross** of −2.2161 and −1.9930). A criterion that any
all-negative route passes cannot discriminate anything. **I registered a test that could not fail
where it was applied**, and that is the fourth pre-registration defect in this loop — after Round
327's uncomputed p-value, Round 330's bound on the wrong variable, and Round 340's unassigned
interval.

**The discriminating comparison refutes transfer.** Ranked within each route, Wednesday is the
**worst** day on `exness XAU` and the **best** (or second best) on both BTC routes; Friday is the
**best** on `exness XAU` and the **worst** on both BTC routes. The pattern does not transfer — it
**inverts**. So the `exness XAU` weekday structure is **not** a systematic Portfolio artifact; it
is route-specific, or it is noise.

## Part 3 — audit L3 quantified

The correctness audit flagged that UTC+7 bucketing splits a CFD's Friday session and dilutes the
per-day gate metrics. On `exness XAU` @1800: **49 Saturday buckets, 47 of them (95.9%) exactly
zero** — the Friday-evening tail almost never closes a trade. Overall **88 of 306 rows (28.8%)
are exactly zero**.

`positive_day_ratio` measures **0.37255** (114/306). Excluding the Saturday buckets it is
**0.43580** (112/257). **The Sat bucket alone depresses the metric by 0.06325**, about 17% of its
reported value, against a 0.55 threshold. The threshold is written for an instrument that trades
every day; on a session-based one it is applied to a denominator padded with structurally empty
buckets.

## What is proven, and what is not

Proven:

- The activity table above; A_wed 0.8235 versus A_other 0.8447; Wednesday day-level win rate
  0.429 (18/42) against 0.540 elsewhere; mean |PnL| on active days 0.04699 against 0.03923.
- The three-route weekday means and their within-route ranks; Wednesday worst on `exness XAU`,
  best/second-best on the BTC routes; Friday best on `exness XAU`, worst on both BTC routes.
- `exness BTC` @1800: 361 observed days, gross −2.2161, cost 4.4027, net −6.6188.
  `binance BTC` @1800: 361 days, gross −1.9930, cost 4.4171, net −6.4102.
- `exness XAU` @1800: 49 Sat buckets, 47 zero; 88/306 rows zero; `positive_day_ratio` 0.37255,
  0.43580 excluding Sat buckets.

Not proven, and deliberately not claimed:

- **That Wednesday's loss is negative edge.** The activity proxy points that way, but the proxy is
  coarse — a non-zero day may hold one trade or five — and the win rate is **day-level, not
  trade-level**. Gross by weekday remains unobtainable, so the question Round 353 called decisive
  is still open.
- **That the BTC routes disprove a weekday effect on `exness XAU`.** They show it does not
  transfer. A route-specific effect and noise both predict that, and this round does not separate
  them.
- That the inversion is meaningful. Friday worst on both BTC routes is itself only two nested-ish
  observations on routes that lose on every day of the week.
- Any correction to Round 353's within-route replication. That result stands on its own evidence;
  what this round removes is the "systematic across routes" reading, which Round 353 never claimed.
- Any promotion. Nothing is testable end-to-end (no weekday filter in the CLI), the route is
  gate-ineligible, and the decisive gross/cost split cannot be measured.
