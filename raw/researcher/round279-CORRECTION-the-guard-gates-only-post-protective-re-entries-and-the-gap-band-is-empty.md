# Round 279 — CORRECTION: the hold guard gates *only* re-entries after a protective exit. The 0.2-2.9h band is empty on every route.

Classification: **NEEDS-MORE-RESEARCH**. Local code inspection plus read-only
production evidence. **Zero containers.**

## Round 278's untraced assumption, traced

Round 278 found median flat time at exactly the 3h hold guard and said plainly what
was missing: *"no code path was traced to confirm the guard gates re-entry as well as
reversal."* It does not — and the code says something sharper
(`trading_modes.rs:238-264`):

```rust
let starts_initial_position = self.current_target.position == TargetPosition::Flat
    && !self.waiting_after_protective_exit;
let holding_period_elapsed = self.decisions_since_target_change >= self.minimum_holding_decisions;
if !changes_position || starts_initial_position || holding_period_elapsed { … take the position … }
```

`observe_execution(ProtectiveExit)` sets `waiting_after_protective_exit = true`; a
plain `decision.exit` sets it **false**. So:

- after a **flat exit** → `starts_initial_position` is true → the next gate pass opens
  a position **immediately, bypassing the guard**;
- after a **protective exit** (stop/take) → the flag blocks that shortcut → re-entry
  waits for the full **36 decisions = 3h**.

**Prediction: flat gaps should be bimodal — a spike near zero and a spike at exactly
3h — with the fraction near zero equal to the fraction of flat exits.**

## Confirmed, and about as exactly as data allows

| route | gaps | **≤0.2h** | **0.2-2.9h** | **2.9-3.1h** | >3.1h | **flat exits** |
|---|---|---|---|---|---|---|
| binance BTC | 472 | **14.0%** | **0.0%** | 40.5% | 45.6% | **14.0%** |
| bybit BTC | 310 | **5.8%** | **0.0%** | 24.5% | 69.7% | **5.8%** |
| exness XAU | 391 | **47.6%** | **0.0%** | 17.6% | 34.8% | **47.6%** |

**The ≤0.2h fraction equals the flat-exit fraction exactly on all three routes**, and
**the 0.2-2.9h band is empty on all three**. There is literally nothing between
"immediate" and "three hours". Every flat exit is followed by an immediate re-entry;
every protective exit by a wait of at least 2.9h.

## What this corrects in Round 278

Round 278 wrote that "between half and two-thirds of all re-entries happen at the
earliest moment the guard permits" and treated its `≤3.05h` bucket as one population.
**It is two populations**, and the guard touches only one of them:

| route | ≤3.05h (Round 278) | = immediate (guard **not** involved) | + at the 3h guard |
|---|---|---|---|
| exness XAU | 64.7% | 47.6% | 17.6% |
| binance BTC | 52.5% | 14.0% | 40.5% |
| bybit BTC | 26.8% | 5.8% | 24.5% |

So on `exness XAU` the guard is involved in only **17.6%** of re-entries, not 64.7%.
Round 278's statistic conflated a mechanism with its opposite.

## The chain is now complete — and occupancy follows the close-reason mix

Flat-exit fraction 47.6% > 14.0% > 5.8% orders the routes exactly as occupancy does:
86.7% > 59.6% > 43.3%. The causal chain:

```
close-reason mix → fraction of exits that are "flat" → immediate vs 3h re-entry
                 → occupancy → (with hold, governed by σ²) → frequency
```

Round 277 split hold and occupancy into "two distinct causes". They are less distinct
than that: both trace to how a **fixed fractional band** interacts with the
instrument — the band sets hold duration (σ², Round 273) and also determines how often
price reaches it *before* the signal goes flat, which sets the close-reason mix.

**But that is not the whole story either.** `bybit BTC` and `binance BTC` have
near-identical volatility yet 5.8% against 14.0% flat exits — a 2.4x difference the
band cannot explain.

## What is proven, and what is not

Proven:

- The code path above, cited to line, and its two branches.
- On three routes: the ≤0.2h gap fraction equals the flat-exit fraction exactly, and
  the 0.2-2.9h band contains **zero** gaps out of 472, 310 and 391.
- The re-decomposition of Round 278's `≤3.05h` bucket into immediate and at-guard
  populations.
- Flat-exit fraction orders the three routes identically to occupancy.

Not proven, and deliberately not claimed:

- **What sets the close-reason mix on same-volatility routes.** `bybit BTC` vs
  `binance BTC` is 5.8% against 14.0% at equal volatility; the band cannot explain it
  and nothing here does.
- That the unified reading supersedes Round 277. Round 277's *measurements* stand;
  what is revised is calling hold and occupancy fully independent causes, since both
  respond to the same band. The `bybit BTC` residual is exactly the part that is not
  unified.
- That flat exits are always followed by an immediate re-entry **in principle**. What
  is shown is that they were, on every gap in three routes — the gate could in
  principle fail to pass immediately, and evidently almost never does.
- Anything about `binance XAU` or `bybit XAUT` (n = 7 and 1), excluded.
