# CORRECTION (Round 248)

The **"3 of 4 families peak at 150-300"** count below is **partly an aggregate
artifact**. Checking per candidate (medians and improvement counts rather than
summed aggregates): **breakout survives** — median +0.00056 -> +0.00278, 9/15
candidates improving across seven structurally distinct mechanisms — and
**reversion is robustly worse** (median -0.00034 -> -0.00241, 6/18). But
**trend/momentum does NOT survive**: its median moves the *other* way
(+0.00030 -> +0.00028) with 15/24 improving, near a coin flip; **other** is 6/11
on near-zero magnitudes.

Corrected count: **one family clearly up, one clearly down, two indistinguishable
from noise.** This file's core argument — breakout, a family the policy barely
uses, shows the effect most strongly — is **unaffected and better supported**.
See `round248-per-candidate-check-breakout-survives-momentum-does-not.md`.

---

# Round 247 — The separating test: three mechanically unrelated families also peak at 150-300, but reversion moves the *opposite* way. The window was directional, not uniformly easy

Classification: **NEEDS-MORE-RESEARCH**. Two bounded Docker sweeps.

## The confound Round 246 could not separate

Round 246 found all three instruments strongest in the 150-300 day band but noted
they all run **the same Portfolio policy**, leaving two readings equivalent:
market regime, or the shared policy suiting that period. The separating test it
named: **a mechanically unrelated strategy family over the same bands.**

The Alpha sweep provides exactly that — 68 candidates across families the deployed
policy barely uses. exness XAU 5m, zero cost, candidates with >= 30 trades in both
bands, aggregated per family:

| family | candidates | 0-150 per trade | 150-300 per trade | stronger |
|---|---|---|---|---|
| **breakout** | 15 | +0.00082 | **+0.00294** | 150-300 |
| trend / momentum | 24 | +0.00020 | +0.00031 | 150-300 |
| other | 11 | +0.00008 | +0.00013 | 150-300 |
| **reversion** | 18 | **−0.00048** | **−0.00124** | **0-150** |

## Result — the confound is partly separated, and the answer is more specific than "regime"

**Three of four families peak at 150-300**, including **breakout** — a family the
deployed policy barely uses (production `strategy_weights` are dominated by
`candle_momentum` and `rsi_mean_reversion`, per the Round 206/233 checkpoints).
Breakout shows the largest lift of all: **+0.00294 against its own +0.00082**, a
3.6x increase.

That is evidence **against** the pure shared-policy explanation: a family the
policy does not lean on shows the effect more strongly than the policy's own
families.

**But reversion moves the other way** — negative in both bands and *worse* in
150-300. So the window was not uniformly favourable. The correct characterisation
is directional:

> **The 150-300 day window favoured directional mechanisms (breakout, momentum)
> and punished mean-reversion.**

That is not a new hypothesis invented to fit this table — it is what **Round 228
independently measured** across the same transition: Kaufman efficiency roughly
doubled (0.0366 → 0.0753) and drift roughly doubled (+13.9% → +26.9%) while
volatility fell. Directionality up, reversion punished. Two independent routes,
same conclusion.

## Where this leaves Round 246's question

| explanation | status |
|---|---|
| pure shared-policy artifact | **weakened** — breakout, barely used by the policy, shows the strongest effect |
| uniform market regime | **weakened** — reversion moves the opposite way |
| **directional regime** | **consistent with both this round and Round 228** |

Not settled, but no longer two equally-supported readings. The remaining gap is
that "directional regime" is a description, not a cause — Round 228 already found
no single price statistic tracks *all* the transitions, and this round does not
change that.

## What is proven, and what is not

Proven:

- exness XAU 5m Alpha sweep, zero cost, aggregated per family over candidates with
  >= 30 trades in both bands: breakout +0.00082 → +0.00294; trend/momentum
  +0.00020 → +0.00031; other +0.00008 → +0.00013; reversion −0.00048 → −0.00124.
- 3 of 4 families are stronger in 150-300; reversion is the exception and is
  negative in both.

Not proven, and deliberately not claimed:

- That the family split is authoritative. It is my own string-matching heuristic
  (the same one used in Round 217), not a taxonomy read from the code.
- That per-family aggregates are not dominated by a few high-trade candidates.
  Trades were summed within each family without weighting checks.
- That this is the Portfolio layer. It is the **Alpha** sweep; the Portfolio
  policy's own band profile came from `one_target` in Rounds 242-246.
- Causation. "Directional regime" describes what the bands and Round 228's
  statistics both show; it does not explain why that period was directional.
