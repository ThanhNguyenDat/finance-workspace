# Round 402 — NO-CHANGE: the two stale fleet-table rows were **harmless**. Separately, `binance XAU` **cannot produce a qualifying holdout at any window length**.

Classification: **NO-CHANGE** — a data-integrity check that came back clean.
Two containers (the budget), cleaned up.

## Why the check was needed

Round 401 found that a `binance XAU` log I was reading came from before the
measurement change. Auditing the provenance of round 390's fleet table showed
**two of its five rows** came from commit `59e2489`, whose measurement path was
corrected **twice** afterwards (`c07951a`, `f158e04`), and **neither was
window-pinned**. Round 381 showed those fixes moved trade counts and PnL on
`binance BTC`.

So two published fleet-table entries rested on a superseded build.

## The re-run

| route | build | gross | net | cost/gross | trades/wk | holdout days |
|---|---|---|---|---|---|---|
| `binance XAU` | stale | −0.39816 | −0.62329 | 0.5654 | 4.794 | 52.6 |
| `binance XAU` | **final** | **−0.42093** | −0.64607 | 0.5349 | 4.797 | 52.5 |
| `bybit BTC` | stale | −0.89289 | −2.45576 | 1.7503 | 8.517 | 180.0 |
| `bybit BTC` | **final** | **−0.89289** | −2.45576 | 1.7503 | 8.517 | 180.0 |

**Registered answer: neither gross sign changed.** The stale entries were
harmless, and round 390's table stands as already corrected by round 397.

Two details worth keeping:

- **`bybit BTC` is bit-identical across builds.** The two fixes changed nothing
  on this route, while round 381 measured them moving `binance BTC` by a trade
  and 4% of PnL. The fixes' effect is **route-dependent and can be zero**.
- **`binance XAU` moved 5.7%** (−0.39816 → −0.42093), consistent with round
  382's finding that unpinned runs drift.

## The structural fact this surfaced

`binance XAU` at `--days 900` loads **75,672 candles = 262.8 bar-days**, and
holdout is the trailing 20% — **52.5 days**.

The gate's `minimum_holdout_days` is **90**. To reach it the route needs **450
bar-days**; it has **263**. **No `--days` value can produce a qualifying holdout
on this route**, because it is already loading its entire venue history (r208).
The shortfall is **187 bar-days ≈ 6.2 months of forward time**.

So of six production routes:

- `binance XAU` — **cannot be gate-qualified at all** until roughly six more
  months of history exist;
- `bybit XAUT` — qualifies only at the most recent cutoff (101.3 days); every
  earlier cutoff is disqualified by length (r400);
- the other four — qualify at 180 days.

**Two of six routes cannot be evaluated across multiple holdouts at qualifying
length**, which bounds every fleet-level statement this arc can make, including
the pooled interval.

## What is proven, and what is not

Proven:

- The four rows above; both gross signs unchanged; `bybit BTC` bit-identical.
- `binance XAU` loads 262.8 bar-days at `--days 900`, giving a 52.5-day holdout
  against a 90-day minimum.
- The shortfall is 187 bar-days.

Not proven, and deliberately not claimed:

- **That the stale-build issue was harmless everywhere.** Two rows were checked;
  the fleet table had five, and older rounds used that build widely without
  re-checking.
- That `bybit BTC`'s bit-identity means the fixes were no-ops. It means they were
  no-ops **on this route and window**; round 381 showed otherwise elsewhere.
- That six months would make `binance XAU` evaluable. It would clear the length
  threshold; the seven interval-continuity checks and the performance thresholds
  are separate.
- Any change to the pooled estimate. `binance XAU` was never in the nine-holdout
  series, and this round adds no new disjoint point.

## Named next step

Nothing in the fleet table needs further re-running: the two suspect rows are
now confirmed. The binding constraints on any further fleet statement are
**structural, not procedural** — two routes cannot supply qualifying holdouts,
and the other four are already measured. That is the honest end of the
fleet-measurement thread.
