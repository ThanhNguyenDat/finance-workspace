# "IMMATERIAL" IS `exness XAU`-SPECIFIC (Round 358)

This file's *"the guard's omission is immaterial in magnitude"* was measured on **one route**
across three windows. Tested on two more at `--days 500`, it **fails**: on **`binance BTC`** the
guard removes 30% of trades and cuts the loss by **41%** (−8.07260 → −4.74869); on `bybit XAUT`
it removes 20% and cuts 19.8%. Against `exness XAU`'s 0.44%.

**So the gate, which scores the guard-free stream, systematically overstates losses on routes
where the guard bites** — its BTC verdicts are pessimistic by a large margin. This file's
structural finding about *what* the gate omits is unaffected; only the claim that the omission
does not matter is withdrawn, and kept as an `exness XAU` observation. See `round358-REJECTED-the-guard-is-immaterial-only-on-exness-xau-it-moves-binance-btc-by-41-percent.md`.

---

# Round 356 — DATA-ISSUE: the `--daily-profit-gate` scorecard **does not model the deployed Portfolio construction**. It replays decisions straight into a ledger — no minimum-hold guard, **no risk layer, and therefore no 10 bps execution-cost gate**. PnL impact is small (≤3.8%), trade-count impact is not (**21.1%** at @300).

Classification: **DATA-ISSUE** — the joint-objective scorecard used from Round 328 onward scores a
different configuration than the one every conclusion was attributed to. Two bounded Docker
sweeps (exactly the 2-container budget), **XAU-first**.

## What the gate actually does

`finance-research/src/daily_profit_gate.rs:376-412` builds one `SimulatedLedger` and calls
**`ledger.on_kline(&timed.kline, &timed.decision)`** for every decision. That is all.

It never calls `PortfolioConstructionState::construct`, never applies
`minimum_hold_decisions`, and never runs `PortfolioRiskLayer` — no `evaluate_historical`, no
`execution_target`. The `one_target` path in `portfolio_measurement.rs:184-208` does all three.

Per Round 82's definition, a ledger fed by `on_kline` directly **is** the
`legacy_selected_rule` construction. **So the gate scores the guard-free stream, not the
Portfolio-faithful one.**

The code says so plainly at `main.rs:255-263`: *"The daily-profit gate **does not model this
construction comparison**, so reject an explicit value there instead of silently ignoring it"* —
which is why `--portfolio-minimum-hold-decisions` **conflicts with** `--daily-profit-gate`. The
tool has been honest; I read the conflict as a CLI quirk and never as a statement about what the
gate measures.

## How much it matters

**Pre-registered as a partition:** `|one_target − legacy| / |legacy|` on realized PnL —
**≥ 0.20** → the guard materially changes the outcome and gate metrics are unreliable for the
deployed configuration; **< 0.20** → the omission is immaterial in magnitude.

`exness XAU`, deployed band, `minimum_hold_decisions 36`, plain `--json`:

| window | `one_target` trades | `legacy` trades | trade reduction | `one_target` PnL | `legacy` PnL | **rel. diff** | `execution_cost` rejections |
|---|---|---|---|---|---|---|---|
| @300 | 280 | 355 | **0.2113** | −1.32216 | −1.32799 | **0.0044** | 102 |
| @1500 | 398 | 410 | 0.0293 | −3.82660 | −3.68554 | **0.0383** | 55 |
| @1800 | 488 | 504 | 0.0317 | −4.34249 | −4.25993 | **0.0194** | 73 |

**All three are ≤ 0.038 — the "immaterial in magnitude" branch fires.** The guard changes
realized PnL by **0.4% to 3.8%**, so the gate's net, Sharpe and cost÷gross figures are not badly
wrong in size.

**But the trade count is a different story.** The guard removes **21.1%** of trades at @300 and
~3% at the deep windows — and `trades_per_week` is a **gate threshold** (Target 3, 7.0/week). The
gate therefore reports a frequency for a stream that trades **more** than the deployed one; the
true guarded rate is **lower**, which makes Target 3 harder to pass, not easier. Every
trades/week figure quoted from a gate run since Round 328 is an **upper bound** on the deployed
rate.

The `execution_cost` column also shows the contrast directly: the plain path records **102 / 55 /
73** rejections; the gate path, having no risk layer, records none because it has no gate to
record.

## The correction this forces on Round 348

Round 348 explained Round 344's and Round 345's fee-ladder jumps by the **10 bps reversal gate** —
`(fee + slippage) × 2 > 10`. But **Rounds 344 and 345 were `--daily-profit-gate` runs**, and the
gate path has **no risk layer**, so that gate could not have fired in them.

- **Rounds 349 and 350 stand**: both used plain `--json`, where the risk layer *is* active, and
  Round 349 measured the rejections directly (102 → 3).
- **Round 348's attribution of the r344/r345 ladder to the reversal gate is withdrawn.** Those
  runs are guard-free and risk-layer-free, so their fee response is the **cost-feedback path
  alone**.

This actually makes the arc more coherent rather than less: Round 350 concluded the cost slope
explains the movement (Δ = −0.13, inside its registered band), and Round 349 isolated a gate-free
feedback path on the ungated `legacy_selected_rule` ledger whose PnL runs −1.32799 / −0.75172 /
−0.72084 / −0.83321 across the same cost ladder. The gate path *is* that ungated ledger.

## What is proven, and what is not

Proven:

- `daily_profit_gate.rs:376-412` replays via `ledger.on_kline` with no construction state and no
  risk layer; `portfolio_measurement.rs:184-208` uses `construct` → `evaluate_historical` →
  `execution_target` → `execute_target`; `main.rs:255-263` documents the omission and is why the
  flags conflict.
- The three-window table above, from plain `--json` runs at the deployed band with hold 36.
- Relative PnL difference between guarded and guard-free streams: 0.44%, 3.83%, 1.94%.
- Trade reduction from the guard: 21.13%, 2.93%, 3.17%.
- Rounds 344 and 345 were `--daily-profit-gate` runs; Rounds 349 and 350 were plain `--json`.

Not proven, and deliberately not claimed:

- **That gate conclusions are wrong.** The PnL-magnitude effect is ≤3.8% on three windows, so
  sign-level and large-magnitude conclusions are unaffected. What changes is **what
  configuration they describe** — guard-free, risk-layer-free — and that `trades_per_week` from a
  gate run overstates the deployed rate.
- That the 21.1% trade reduction at @300 transfers. It is 3% at both deep windows; the guard's
  bite clearly varies with the window and I have three points.
- **That the deployed configuration would score better or worse on the gate.** It cannot be
  scored on the gate at all — the flags conflict by design — so this is not a comparison I can
  run without a code change.
- Any restatement of Rounds 349/350. They used the path where the risk layer is active and are
  untouched.
- Any promotion. Nothing changed and every window still loses at deployed costs.
