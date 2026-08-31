# GENERALITY WITHDRAWN (Round 372)

This file's central claim - that the guard-plus-risk-layer advantage is the arc's **first
effect stable across routes and windows** - **does not survive the two remaining XAU
routes.** On `binance XAU` @900 the advantage is **-0.34870**, i.e. the guarded stream is
**31.9% worse** than the unguarded one.

Full record, six measurements: **+2.24338 / +1.55149 / +1.86003 / +5.08599 / +0.46533 /
-0.34870** - five of six positive, **three of four routes** positive, one negative.
Normalised, the spread is **-31.9% to +155.1%**. This file cautioned that the sign
replicates and the magnitude does not; the sign does **not** fully replicate either.

That is still the best replication record anything in this arc has achieved, and the
advantage remains positive on the two routes carrying the most trades. What is withdrawn
is **generality**, which is what this file claimed. Its measurements, its quantification
of the gate's ~2x understatement, and its Target 3 finding are unaffected. See
`round372-REJECTED-the-guard-advantage-is-not-general-either-binance-xau-is-31-9-percent-worse-with-the-guard-than-without-it.md`.

---

# Round 371 — NEEDS-MORE-RESEARCH: the **construction guard plus risk layer** is the arc's **first effect that is positive on both routes at both window depths**. Separately, `binance BTC`'s Target 3 pass **fails at 900 days**.

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker runs (exactly the
2-container budget), `binance.perpetual_future.BTC.USDT` @900, both
`candle_count` **259,198** — same window, so the two arms are directly
comparable. Closes the corner question; opens a better one.

## Two pre-registrations, answered in opposite directions

Round 370 killed the profitable corner on `exness XAU` (sign flip at 900 days)
and explicitly refused to predict `binance BTC`. Registered before running, on
`binance BTC` at band 0.02/0.04, hold 288, @900:

1. **Corner sign** — positive → the corner survives deeper on BTC where it
   failed on XAU; negative → its positivity is a recent-window property on
   **both** routes.
2. **Corner advantage over the `legacy_selected_rule` control** — positive →
   the first Portfolio-layer effect stable across both routes *and* both window
   depths; ≤ 0 → even the advantage is route-local, and nothing at this layer
   survives.

**Part 1: −2.95541. Negative.** The corner is a recent-window artifact on both
routes; the question is closed.

**Part 2: +1.86003. Positive.** And it is the more interesting half.

## The measurements

| route | window | config | `one_target` | `legacy` control | advantage | loss cut |
|---|---|---|---|---|---|---|
| `exness XAU` | 500 | corner | +0.79730 | −1.44608 | **+2.24338** | sign flip |
| `exness XAU` | 900 | corner | −0.70835 | −2.25984 | **+1.55149** | **68.7%** |
| **`binance BTC`** | **900** | corner | −2.95541 | −4.81544 | **+1.86003** | **38.6%** |
| **`binance BTC`** | **900** | **deployed** | −4.81958 | −9.90557 | **+5.08599** | **51.3%** |

**Four measurements, two routes, two window depths, all positive.** Nothing else
in this arc has done that — every band gradient, per-trade rule, weekday pattern,
trough and profitable corner has failed one of these two tests.

## What the effect actually is — and it is not the corner

The largest advantage in the table belongs to the **deployed** configuration
(+5.08599, a 51.3% loss reduction), not the corner. So this is **not** a property
of the searched parameter corner. It is a property of the machinery itself: the
`PortfolioConstructionState::construct` minimum-hold whipsaw guard plus the
`PortfolioRiskLayer`, measured against the same decision stream fed straight to
the ledger.

That machinery is **exactly what `--daily-profit-gate` bypasses** (r356). The
consequence is now quantified rather than argued: on this route and window the
gate scores a stream that loses **−9.90557** while what actually runs loses
**−4.81958**. **Gate verdicts understate the deployed configuration by roughly
2x**, in the pessimistic direction.

This does not make anything promotable — the effect is "loses half as much", not
"makes money" — but it is the first thing at this layer with a stable sign, and
it is measured on the deployed configuration rather than on a searched corner.

## `binance BTC`'s Target 3 pass is window-dependent

Same deployed parameters (band 0.01/0.02, hold 36), two windows I ran myself:

| window | trades | trades/week | verdict |
|---|---|---|---|
| 500 (r367) | 689 | **9.65** | pass |
| **900** *(new)* | 874 | **6.80** | **fail** |

A **−29.5% shift that crosses the bar.** This route is a 24/7 perpetual —
259,198 candles is exactly 900.0 days, so calendar and bar denominators coincide
and the r370 coverage caveat does not apply here. The number is unambiguous.

Round 286 tested 260d → 360d (9.42 → 8.92), called both passes **window-robust**
at a +27.4% margin, and wrote its own stopping condition: *"Either falling below
7 would mean no single-window verdict is trustworthy."* At 900 days it falls
below 7. The condition Round 286 named has now occurred.

## What is proven, and what is not

Proven:

- `binance BTC` @900, corner: 259,198 candles, 315 trades, `one_target`
  −2.95541, `legacy` −4.81544.
- `binance BTC` @900, deployed: 874 trades, 6.80/week, `one_target` −4.81958,
  `legacy` −9.90557.
- Both arms report identical `candle_count`, so the comparison is within one
  window.
- The guard-plus-risk-layer advantage is positive in 4/4 measurements spanning
  two routes and two window depths, cutting the loss 38.6%–68.7%.

Not proven, and deliberately not claimed:

- **That the advantage is stable in magnitude.** It ranges 38.6% to 68.7% across
  four measurements — the *sign* is what replicates, not the size, and four
  points across two routes is not a distribution.
- **That the guard is why the deployed system should keep its current shape.**
  `legacy_selected_rule` is a control, not a deployable alternative; "better
  than a stream with no guard and no risk layer" is a low bar that happens to be
  the only one anything has cleared.
- **That gate verdicts are wrong by 2x generally.** One route, one window. r356
  established the mechanism; this round measures it **once**.
- That `binance BTC` fails Target 3. It fails **at 900 days** on the deployed
  parameters. r286 (260d, 360d) and r367 (500d) all pass. What is shown is that
  the verdict moves with the window and no single-window verdict settles it —
  which was r286's own stated criterion, not a new standard imported here.
- Any mechanism for the 900-day drop, and any claim about what happened in the
  older period: the windows are nested (r352) and r300 forbids differencing
  Portfolio counters across window lengths.

## Named next step

The advantage is the only surviving effect, and it is currently measured only
against an unguarded control. The useful decomposition is **guard versus risk
layer** — which of the two carries the 38.6%–68.7%. That is not reachable with
the present flags (no way to disable one and keep the other), so it is a
**code-change question**, filed with the gate-scoring gap (r356) and the
per-trade audit trail (audit L4) rather than as a runnable next round.
