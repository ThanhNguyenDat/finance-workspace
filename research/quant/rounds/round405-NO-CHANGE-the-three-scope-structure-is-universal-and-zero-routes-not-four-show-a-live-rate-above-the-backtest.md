# Round 405 — NO-CHANGE: the three-scope structure is **universal across all six routes**, and **zero** routes — not four — show a live rate above the backtest.

Classification: **NO-CHANGE** — completes round 404's correction fleet-wide; no
new defect. **Zero containers**; narrow read-only production reads.

## Completing the correction

Round 404 established the three-scope pooling defect on **two** routes. Round
403's retracted claim covered **all six**, so the correction had to be checked
everywhere.

| route | raw | scopes | **distinct** | live /wk (95% CI) | backtest | |
|---|---|---|---|---|---|---|
| `exness XAU` | 9 | 3 | **3** | 1.1 – 15.7 | 6.232 | overlaps |
| `binance XAU` | 3 | 3 | **1** | 0.0 – 10.0 | 4.797 | overlaps |
| `bybit XAUT` | 3 | 3 | **1** | 0.0 – 10.0 | 3.454 | overlaps |
| `binance BTC` | 18 | 3 | **6** | 3.9 – 23.4 | 7.661 | overlaps |
| `bybit BTC` | 12 | 3 | **4** | 1.9 – 18.3 | 8.517 | overlaps |
| `exness BTC` | 15 | 3 | **5** | 2.9 – 20.9 | 5.794 | overlaps |

**Every route has exactly three scopes** — `paper-fixed-pct`,
`paper-compounding-10pct`, `paper-risk-2pct` — and on every route
**raw = 3 × distinct**, with all three scopes agreeing on the distinct count.
The pooling factor is exactly 3 everywhere, not approximately.

**Zero routes show a live rate above the backtest holdout rate.** Round 403
reported four. The correct answer across all six is **none**.

## What the live sample actually is

**20 distinct trades across the whole fleet in 3.91 days**, not 60. Two routes
have **one** trade each.

So the honest position on the live-versus-backtest question is not "they agree"
— it is that **the live log currently supports no conclusion in either
direction**. Every interval overlaps because every interval is wide; two of them
start at zero.

## What is proven, and what is not

Proven:

- All six routes carry exactly the same three `scope_id` prefixes.
- On every route the raw key size is exactly 3× the distinct trade count, and
  all three scopes agree on that count.
- Distinct trades: 3, 1, 1, 6, 4, 5 — twenty in total over 3.91 days.
- No route's live 95% interval lies above its backtest holdout rate.

Not proven, and deliberately not claimed:

- **That live and backtest rates agree.** Overlapping wide intervals are the
  absence of evidence, not evidence of agreement — and this round makes that
  weaker than round 404 suggested, since four of six routes have fewer than five
  distinct trades.
- That the three scopes always share one decision stream. Verified tuple-by-tuple
  on two routes (round 404); on the other four only the counts are shown to
  match, which is consistent with but does not prove a shared stream.
- Anything about live PnL, still. Sizes differ by three orders of magnitude
  across scopes and no scope has been matched to the backtest's parameters.

## Named next step

Unchanged and now quantified precisely: the live log yields **~5 distinct trades
per route per 3.9 days at best, and 1 at worst**. A month of forward time gives
roughly **8–46 distinct closes per route**. Until then there is nothing further
to read from it, and this thread should not be re-opened each round for the sake
of having something to run.
