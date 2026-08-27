# Round 168 — Funding rate as an Alpha signal: preliminary correlation found, real backtest blocked on architecture

## Context

Rule 2/3's own guidance (Round 93) says the technical-indicator space at 5m
is largely exhausted; the productive direction is a genuinely different
information source. Order-flow (taker imbalance) was tried and closed
Round 72-75. Funding rate — freely available in this codebase's cost
model but never tested as a *signal* — had not been tried. The classic
crypto-specific hypothesis: extreme positive funding (longs paying shorts
heavily) indicates crowded long positioning, often followed by a
mean-reversion pullback; extreme negative funding is the mirror case.

## What was tried

1. Added `--dump-funding-schedule` to `finance-research` (opt-in JSON
   diagnostic export of resolved `FundingSettlement` records — timestamp,
   signed rate, mark price — alongside the existing settlement *count*
   field). Safe, additive, off by default; does not change any existing
   field's meaning or any production behavior. Committed separately from
   the analysis below (see commit list).
2. Attempted to fetch real settlements via `--actual-funding-broker
   binance` through `finance-mw` — blocked: `FINANCE_MW_GRPC_BEARER_TOKEN
   is required for authoritative funding`. This is an internal/protected
   endpoint; did not attempt to acquire or extract that credential (out of
   scope for read-only research access, and not something to go digging
   for per this program's credential-handling rules).
3. Pivoted to Binance's public REST API directly (`fapi.binance.com`,
   fully public market data, no credentials) for a **preliminary**
   correlation check: 1,095 real `BTCUSDT` funding settlements + 8,752
   hourly klines, both for the trailing 365 days.

## Preliminary finding (NOT a validated strategy — see caveats)

For each funding settlement, paired the signed rate with BTC's realized
return over the following 8 hours (until the next settlement):

- Overall Pearson correlation (funding rate vs next-8h return): **-0.0186**
  — negligible in aggregate.
- Quintile split shows a directionally consistent but weak and non-
  monotonic pattern (Q5, most positive funding: -0.060% mean fwd return;
  Q1, most negative: +0.005%).
- **Extreme decile (top/bottom 10% by funding rate) shows a real
  asymmetry:** most-positive-funding decile → mean forward 8h return
  **-0.131%**; most-negative-funding decile → **+0.004%** (near zero). The
  contrarian effect is real-looking only at the extremes, not in the
  general population — consistent with the standard "funding extremes
  matter, mild funding doesn't" framing from crypto market-structure
  literature.

## Why this is not a validated candidate yet — three real caveats

1. **Not an honest train/validation/holdout split.** This is a single
   correlation pass over the combined sample — exactly the p-hacking risk
   Rule 7 warns against. A real test needs this program's actual 3-way
   split methodology.
2. **Public-API data, not the production candle/funding source.** Cross-
   checking against `finance-mw`'s own authoritative funding history
   (blocked this round on the bearer-token requirement) is necessary
   before trusting this for anything beyond a go/no-go signal on whether
   to invest further.
3. **Magnitude is close to this program's known cost ceiling.** ~13bps at
   the extreme decile is not far above the ~7bps/trade structural cost
   ceiling this program has repeatedly found (Round 93/96 cost-ablation
   findings) — after realistic fee+slippage+spread, a real strategy built
   on this would likely need a materially larger raw edge than what this
   quick check found to survive costs and still clear Target 3's frequency
   floor (extreme-decile-only entries are inherently low-frequency).

## Why not implemented as a `Strategy` this round

`Kline` (the only input `Strategy::evaluate()` receives) does not carry
funding data — funding is joined only at the Portfolio/cost-simulation
layer, never passed into the Alpha-strategy layer. Building a real
`FundingRateContrarianStrategy` needs either (a) extending the `Strategy`
trait's input (touches every existing strategy's call site) or (b) a
side-channel that feeds funding data into a stateful strategy out-of-band
of `evaluate()`. Both are real architecture decisions bigger than a single
round should rush, especially before the correlation itself is confirmed
through the real backtest pipeline (caveat 1-2 above) — no point building
the harder plumbing before knowing if the honest 3-way-split number still
looks promising.

## Recommendation for a future round

1. Get `finance-mw`'s authoritative funding source accessible for research
   (own action item, not this round's to solve — likely needs the token
   provisioned for the research CLI's use case, an infra/ops decision).
2. Until then, cross-validate the public-API finding on Exness/XAU's proxy
   if any funding-like carry data is available there, or accept the public
   Binance BTC data as the only source and be explicit about that
   limitation in any future writeup.
3. Design the minimal `Strategy` trait extension (or side-channel) needed
   to feed funding rate into an Alpha strategy, sized to the actual
   validated signal (extreme-decile threshold only, not the whole
   distribution — the general-population correlation is noise).
4. Re-run the correlation through this program's actual train/validation/
   holdout split before writing any "promising" strategy code.

Logged as a real Rule-7 contribution (new information source explored,
preliminary signal found and honestly caveated) — not a promotion, not a
closed direction either. `--dump-funding-schedule` stays in the tool for
whichever future round picks this up.

## Round 171 update — CLOSED, falsified via honest chronological split

Ran the honest train/validation/holdout methodology this program requires,
using the same public dataset (chronological 60/20/20 split, no shuffling —
`train=656, validation=219, holdout=219` paired observations). Threshold
(90th percentile of `|funding_rate|`) chosen from **train only**, applied
unchanged to validation and holdout. Contrarian rule: funding above
threshold → short next 8h; below negative threshold → long next 8h.

| split | trades | PF (no cost) | PF (14bps round-trip cost) | win rate |
|---|---|---|---|---|
| train | 65 | 1.79 | 1.30 | 46.2% |
| validation | 10 | 15.08 | 8.17 | 70.0% |
| holdout | 31 | 0.48 | **0.35** | 32.3% |

This is the textbook "weak/promising train+validation, reverses on
holdout" false-positive shape this program's methodology exists to catch
— validation's PF 15 is a thin-sample artifact (only 10 trades at that
threshold in that window), not a real edge; holdout clearly falsifies the
strategy even before costs (PF 0.48), and costs make it worse (0.35).

**Verdict: CLOSED.** The Round 168 preliminary correlation (extreme-decile
asymmetry, -0.131% mean forward return) does not survive honest
out-of-sample validation on a proper chronological split. Does not rule
out funding rate as a signal *combined* with something else (e.g. as a
regime filter layered on an existing entry, matching this program's
established successful filter pattern), but a standalone contrarian
threshold strategy on funding rate alone is falsified. No further
investigation of this exact mechanism planned; the `Strategy`-trait
plumbing question from the original writeup is now moot for this specific
approach — would need a fundamentally different combination (filter, not
standalone signal) to be worth revisiting.
