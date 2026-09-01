# FLEET COMPLETE (Round 375)

This file measured the guard advantage on four routes and reported **3 of 4 positive**.
The remaining two are now measured: `bybit BTC` **+56.9%** and `exness BTC` **+28.7%**,
both positive.

Settled record, deployed configuration, one window per route:

| route | advantage | % of loss |
|---|---|---|
| `exness XAU` | +1.55149 | +68.7% |
| `bybit BTC` | +4.97718 | +56.9% |
| `binance BTC` | +5.08599 | +51.3% |
| `exness BTC` | +1.95096 | +28.7% |
| `bybit XAUT` | +0.46533 | +18.6% |
| `binance XAU` | -0.34870 | **-31.9%** |

**Five of six production routes positive, one negative** - this file's conclusion holds
on the full fleet, and its refutation of *generality* stands: one route is still negative.

Round 375 also refuted a second candidate explanation. `production_candidates` gives the
Portfolio a route-dependent 2, 3 or 5 Alpha inputs, and the only negative route is a
2-input route - but `bybit BTC`, also 2-input and never used to form the hypothesis,
lands at +56.9%, above two of the three 3-and-5-input routes. **Input count joins trade
frequency (this file, rho = +0.143) as an eliminated explanation.** See
`round375-REJECTED-alpha-input-count-does-not-explain-the-guard-advantage-and-the-fleet-complete-record-is-five-of-six-routes-positive.md`.

---

# Round 372 — REJECTED: the guard advantage is **not general either**. On `binance XAU` the construction guard plus risk layer is **31.9% worse** than the unguarded stream.

Classification: **REJECTED** — my pre-registered criterion fired against the
hypothesis. Two bounded Docker runs (exactly the 2-container budget), the two
remaining XAU routes at the deployed configuration @900. Qualifies Round 371.

## The pre-registration

Round 371 found the construction-guard-plus-risk-layer advantage over the
`legacy_selected_rule` control positive in 4/4 measurements across two routes
and two window depths — the only quantity in 60+ rounds to survive both the
cross-route and cross-window tests. It was measured on `exness XAU` and
`binance BTC` only.

Registered before running, on the two remaining XAU routes at deployed
parameters (band 0.01/0.02, hold 36) @900:

- **both advantages positive** → the effect is 6/6 across four routes and is the
  arc's first general Portfolio-layer finding;
- **either ≤ 0** → the effect joins every other route-local result and nothing
  at this layer is general.

**Observed: `bybit XAUT` +0.46533, `binance XAU` −0.34870. The criterion fired.**

A note on validity that makes this test cheap: the advantage is computed
**within each run** (`one_target` against `legacy_selected_rule` on the same
decision stream), so unlike every cross-configuration comparison in this arc,
the routes' windows do **not** need to match.

## The complete six-measurement table

| measurement | trades/week | `legacy` | advantage | as % of loss |
|---|---|---|---|---|
| **`binance XAU` @900 deployed** | 1.04 | −1.09279 | **−0.34870** | **−31.9%** |
| `exness XAU` @900 corner | 1.27 | −2.25984 | +1.55149 | +68.7% |
| `exness XAU` @500 corner | 1.93 | −1.44608 | +2.24338 | +155.1% |
| `bybit XAUT` @900 deployed | 2.05 | −2.49876 | +0.46533 | +18.6% |
| `binance BTC` @900 corner | 2.45 | −4.81544 | +1.86003 | +38.6% |
| `binance BTC` @900 deployed | 6.80 | −9.90557 | +5.08599 | +51.3% |

**Five of six positive, three of four routes positive, one route negative.**
That is the best replication record anything in this arc has achieved — and it
is still not what was registered, so the "first general effect" claim from Round
371 is **withdrawn**.

Normalised, the advantage spans **−31.9% to +155.1%**. Round 371 already cautioned
that "the sign is what replicates, not the size". Now the sign does not fully
replicate either.

## The failing route cannot be given more data

`binance XAU` @900 returns **75,672 candles — 262.8 bar-days**, not 900. That is
the venue horizon (r208: this is a venue horizon, not a backfill gap), so the
route is at its **full available history** and the negative result **cannot be
resolved by running a deeper window**. It is also the thinnest evidence in the
table (134 trades, 1.04/week, the least active route in the fleet).

I am recording that as a limitation, **not** as a reason to discount the result.
The criterion was registered before the run and it fired; explaining away a
failed pre-registration by pointing at the sample is the exact move this arc has
been disciplined against.

## A mechanism I proposed and my own data refutes

The obvious story: the guard suppresses whipsaw re-entries, so on a route that
barely trades it can only remove trades that might have been winners — predicting
the advantage should rise with trade frequency.

Ranked by frequency the normalised advantages run
**−31.9 / +68.7 / +155.1 / +18.6 / +38.6 / +51.3**. Spearman ρ = **+0.143**.
The lowest-frequency measurement is indeed the only negative one and the highest
is large, but the middle is scrambled and the correlation is negligible. **The
mechanism I proposed is not supported by the six points I have**, and I am
recording it as refuted rather than leaving it as a plausible-sounding
explanation.

(ρ here is **descriptive only** — six points, and they are not independent: two
configurations share `binance BTC` @900 and two share `exness XAU`.)

## What is proven, and what is not

Proven:

- `binance XAU` @900: 75,672 candles, 134 trades, `one_target` −1.44149,
  `legacy` −1.09279, advantage **−0.34870**.
- `bybit XAUT` @900: 145,921 candles, 263 trades, `one_target` −2.03343,
  `legacy` −2.49876, advantage **+0.46533**.
- The six-measurement table above; normalised range −31.9% to +155.1%;
  ρ(frequency, normalised advantage) = +0.143.

Not proven, and deliberately not claimed:

- **That the guard hurts `binance XAU` generally.** One window — which is that
  route's entire history — one configuration, 134 trades. What is shown is that
  the *general* claim fails, not that the guard is harmful there.
- **That the guard is useless.** It is positive on three of four routes and on
  the two routes carrying the most trades. What is refuted is generality, which
  was the specific thing Round 371 claimed and the specific thing registered.
- Any mechanism, including the one above, which my own data refutes.
- That the two remaining routes (`bybit BTC`, `exness BTC`) would behave either
  way. Untested; nothing here predicts them.
- Anything about the older period on any route: windows are nested (r352) and
  r300 forbids differencing Portfolio counters across window lengths.

## Where this leaves the arc

Every effect measured at the Portfolio layer is now route-local, including the
one that briefly looked general. The two structural blockers are unchanged —
hold-bearing configurations have no gate score (r356), and every holdout is
nested (r352) — and the decomposition Round 371 named (guard versus risk layer)
still requires a code change and is not runnable.
