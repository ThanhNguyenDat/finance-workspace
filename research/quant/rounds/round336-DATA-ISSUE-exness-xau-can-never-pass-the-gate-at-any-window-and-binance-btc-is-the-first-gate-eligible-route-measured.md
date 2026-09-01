# CAUSE NARROWED (Round 337)

This file left the cause of the missing markers open. One candidate is now **eliminated**:
it is **not a venue property**. `exness BTC/USD` — a CFD on the *same* Exness surface —
fails only **four** intervals with 15 unverified gaps over 54 candles at 5m, against
`exness XAU`'s 628 gaps over 27,659 candles at 15m, and its 2h/4h/12h/1d are perfectly
clean. The difference between the two is the **instrument's trading calendar**: `exness BTC`
trades around the clock, `exness XAU` closes every weekend. The calendar is the obvious
remaining difference and is **not itself verified**.

Also new there: `input_continuity_failed:5m` and a distinct `holdout_interval_continuity`
check both fire on `exness BTC`, so marker coverage is not simply "5m done, the rest not" —
it varies by route. See `round337-REJECTED-continuity-follows-the-instruments-trading-calendar-not-the-venue-and-every-gate-eligible-route-has-negative-gross.md`.

---

# Round 336 — DATA-ISSUE: `exness XAU` fails input continuity at **900 days too**, so **no** gate verdict on that route at **any** window is pass-eligible. `binance BTC` is clean on all eight intervals — the first genuinely gate-eligible measurement in this arc, and it fails on **negative gross**.

Classification: **DATA-ISSUE** — a data-coverage shortfall, not a performance result, decides
the gate outcome on one of the two routes. Two bounded Docker sweeps (exactly the
2-container budget), **XAU-first**, plus read-only local code inspection (no containers).

## The question Round 335 left open

Round 335 named it precisely: *"Whether the seven interval-continuity checks also fail at
900 days is **untested** — if they do, no gate verdict on this route means what it appears
to."*

**Pre-registered before running:** `binance BTC` — a 24/7 perpetual with no session
closures — passes **both** `minimum_holdout_days` and all eight `input_continuity` checks
at 500 days, making the continuity failure route-specific to the CFD rather than universal.
**Refuted** if it fails either.

## Result 1 — the caveat resolves against the exness arc

`exness XAU`, `--days 900`, deployed band, holdout 2026-03-04 → 2026-08-28 (34,867 candles,
**151 observed days**):

```
FAILED: minimum_trades_per_week, positive_day_ratio, median_daily_pnl,
        sortino_ratio, sharpe_ratio, cost_to_gross_pnl_ratio,
        input_continuity_failed: 12h, 15m, 1d, 1h, 2h, 30m, 4h
```

`minimum_holdout_days` **passes** here (151 ≥ 90), exactly as Round 331 said. But **all
seven interval-continuity checks still fail**, and they fail harder than at 500 days —
15m carries 628 unverified gaps over 27,659 candles, 30m 626 / 13,821, 1h 625 / 6,901.
5m again reports **645 verified session gaps and 0 unverified**.

**So the 900-day window is no more gate-eligible than the 500-day one.** Every gate verdict
in the `exness XAU` arc — Rounds 328, 330, 331, 332, 334, 335 — is a **relative ranking on
a common window**, never a pass-eligible verdict. Round 335 established this for 500 days;
it now holds at every window measured.

The performance numbers reproduce: 174 trades, 6.85/week, gross **+0.7820**, cost drag
1.1929, net −0.41099 against Round 331's −0.4118 — a 0.2% drift consistent with the window
ending at a later "now".

## Result 2 — `binance BTC` is clean, and the prediction holds

`binance BTC`, `--days 500`, deployed band, holdout 2026-05-22 → 2026-08-30 (28,799
candles, **101 observed days**):

| interval | verified gaps | unverified gaps |
|---|---|---|
| 5m, 15m, 30m, 1h, 2h, 4h, 12h, 1d | **0** | **0** |

**Zero gaps of any kind on all eight intervals.** `minimum_holdout_days` passes (101 ≥ 90).
No `input_continuity_failed` entry appears in the failure list. **The pre-registered
prediction is confirmed: the continuity failure is route-specific to the CFD's session
structure, not a universal property of the gate.** Crypto-route gate verdicts are real
performance verdicts.

## Result 3 — and the first gate-eligible route fails decisively, in a different way

```
FAILED: positive_day_ratio, median_daily_pnl, negative_day_streak,
        sortino_ratio, sharpe_ratio, gross_pnl_positive, cost_to_gross_pnl_ratio
```

| | `exness XAU` @900 | `binance BTC` @500 |
|---|---|---|
| trades / per week | 174 / 6.85 | 312 / **21.84** |
| **gross before costs** | **+0.7820** | **−1.7909** |
| cost drag | 1.1929 | 2.1498 |
| net | −0.41099 | **−3.9407** |
| Sharpe / Sortino | −0.860 / −1.177 | **−6.753 / −6.817** |
| positive-day ratio | 0.404 | 0.406 |
| negative-day streak | 5 | 7 |
| Target 3 | fail (6.85) | **pass (21.84)** |
| gate-eligible | **no** | **yes** |

**The two routes fail for structurally different reasons.** `exness XAU` earns a **positive
gross edge** and loses it to execution cost (cost÷gross 1.53) — a cost problem. `binance
BTC` has **negative gross**: it loses *before* any cost is charged, and `gross_pnl_positive`
is in its failure list. No cost reduction can rescue a negative gross.

This is the first time the distinction has been measured on the gate's own holdout with a
route whose eligibility is not in question. It confirms from a clean angle what the
Rounds 313-320 cost arc found on `exness XAU`, and it says the frequency lever is not the
binding issue on `binance BTC` — that route trades **3.2x** the bar and still loses.

## Where the missing markers come from (read-only inspection, not applied)

A gap is counted "verified" only when the kline carries `gap_before_reason` /
`gap_before_candles` — `finance-live-action/crates/finance-research/src/klines.rs:314-329`
(no reason and no count → `unverified_gap_count += 1`).

Both ends of that contract support **all eight intervals** in code:

- `finance-mw/cmd/ops/kline-gap-marker-backfill/main.go:334-354` — `activeIntervalDuration`
  accepts `5m, 15m, 30m, 1h, 2h, 4h, 12h, 1d`; the tool takes `instrument` and `interval`
  as arguments, so it is run **per route per interval**.
- `finance-mw/internal/interfaces/worker/kline_flusher.go:331-337` — the live repair path
  sets `GapBeforeReason` / `GapBeforeCandles` from a `step` derived from the route's own
  interval; it is interval-agnostic.

So the shortfall is in the **coverage of the stored data**, not in a code path unable to
express it. **Investigation only — nothing applied, no fix proposed here.**

## What is proven, and what is not

Proven:

- `exness XAU` @900: 151 observed days, `minimum_holdout_days` passes,
  `input_continuity_failed` on all seven non-5m intervals; 15m 628 unverified gaps /
  27,659 candles, 30m 626 / 13,821, 1h 625 / 6,901, 5m 645 verified / 0 unverified.
- `exness XAU` @900 deployed band: 174 trades, 6.853/week, gross +0.78196, cost 1.19295,
  net −0.41099, Sharpe −0.8599, Sortino −1.1766, cost÷gross 1.5256.
- `binance BTC` @500: 0 verified and 0 unverified gaps on **all eight** intervals, 101
  observed days, no continuity or holdout-length failure.
- `binance BTC` @500 deployed band: 312 trades, 21.841/week, gross **−1.79087**, cost
  2.14981, net −3.94069, Sharpe −6.7534, Sortino −6.8170, streak 7, `gross_pnl_positive`
  failed.
- The code citations above, read directly.

Not proven, and deliberately not claimed:

- **Why the markers are absent on seven intervals.** The tool and the live path both
  support every interval, so un-run backfill and a live-path coverage gap are both
  consistent with the data. **I inspected no backfill records and no production state**, and
  I am not asserting which it is.
- That the higher-timeframe gaps are wrong data. `unverified` still means "not confirmed as
  a session gap", not "missing" — unchanged from Round 335.
- **That the `exness XAU` rankings are invalid.** They are not; a structural check failing
  identically across every configuration cannot reorder them. What is invalid is reading any
  of those runs as a **gate verdict**.
- That `binance BTC`'s negative gross is a window property or a route property. **One
  window, one route, one band.** Rounds 331-334 already showed window-fragility on the
  other route, and nothing here tests it on this one.
- Any promotion. Both routes lose money, and the one that is gate-eligible loses before
  costs.
