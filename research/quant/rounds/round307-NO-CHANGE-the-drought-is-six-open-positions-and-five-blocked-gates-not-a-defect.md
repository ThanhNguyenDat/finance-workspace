# Round 307 — NO-CHANGE: the fleet-wide drought is **six open positions and five blocked gates**. Every gate reason reproduces from the code. No defect.

Classification: **NO-CHANGE** — investigated, fully explained, nothing to fix.
**Zero containers**; narrow read-only production evidence only. Answers the one
question Round 306 left open.

## The question Round 306 left

Round 306 found the fleet had gone 27-38 hours without a close while five of six
workers checkpointed within 40 seconds of the read, and closed with: *"whether
positions are open, whether targets simply have not changed, or whether a gate is
firing was **not inspected** this round."*

**Registered before reading:** the drought is **positions being held**, not entries
being blocked — so the routes show **non-flat** positions. I predicted this because
closes come from target changes and a gate blocking all six routes across three brokers
simultaneously would be a different kind of event.

## The state, read from the live checkpoints

| route | position | `decisions_since_target_change` | held | h since last close | **flat gap** | gate |
|---|---|---|---|---|---|---|
| `binance BTC/USDT` | **long** | 342 | 28.5 h | 36.1 | 7.6 h | BLOCK `trend_score_below_threshold` |
| `exness BTC/USD` | **short** | 330 | 27.5 h | 36.1 | 8.6 h | **PASS** `multi_timeframe_gate_passed` |
| `bybit BTC/USDT` | **short** | 330 | 27.5 h | 27.2 | ~0 | BLOCK `entry_trend_conflict` |
| `binance XAU/USDT` | **short** | 156 | 13.0 h | 35.8 | 22.8 h | BLOCK `entry_trend_conflict` |
| `exness XAU/USD` | **short** | 39 | 3.2 h | 38.0 | — | BLOCK `stale_timeframe_evidence:15m` |
| `bybit XAUT/USDT` | **short** | 102 | 8.5 h | 38.0 | 29.5 h | BLOCK `entry_score_below_threshold` |

**All six routes hold an open position** — one long, five short, every one opened via
`multi_timeframe_gate_passed`. The prediction holds: **the fleet is not idle, it is
fully invested.**

Three things follow.

**1. The hold guard is not involved.** `minimum_holding_decisions` is 36 on every route
and the smallest counter is **39**; the largest is 342. Every route is past the guard
and free to change target. `waiting_after_protective_exit` is `false` everywhere, so no
route is in a post-protective cooldown either.

**2. Five of six gates are blocking right now, each for a different reason** — and
every reason reproduces exactly from `trading_modes.rs:842-857` with
`minimum_role_score = 0.1`:

| route | \|entry_score\| | \|trend_score\| | signs | reported reason | reproduces? |
|---|---|---|---|---|---|
| `binance BTC` | 0.12782 ✓ | **0.01048 ✗** | opposite | `trend_score_below_threshold` | **yes** |
| `exness BTC` | 0.12863 ✓ | 0.13263 ✓ | same | `multi_timeframe_gate_passed` | **yes** |
| `bybit BTC` | 0.11464 ✓ | 0.27510 ✓ | **opposite** | `entry_trend_conflict` | **yes** |
| `binance XAU` | 0.10674 ✓ | 0.28236 ✓ | **opposite** | `entry_trend_conflict` | **yes** |
| `exness XAU` | **0.01611 ✗** | 0.74762 ✓ | same | `stale_timeframe_evidence:15m` | staleness wins |
| `bybit XAUT` | **0.00899 ✗** | 0.42172 ✓ | same | `entry_score_below_threshold` | **yes** |

Five reproduce from the two scores and the 0.1 threshold. The sixth is the weekend
staleness guard on the gold CFD — the same benign signature Round 306 traced to a
`.1d` Kafka offset at market close. **The live gate logic matches the code exactly.**

**3. So the drought has a complete, boring explanation.** A close requires a new
target; a new target requires the gate to pass; five gates are refusing. The positions
stay open, and no trade closes. Nothing is broken.

## One live observation that qualifies an earlier round

Round 284 recorded that flat exits are followed by **immediate re-entry, 100% of the
time**. The live flat gaps here are **7.6 h** (`binance BTC`), **8.6 h**
(`exness BTC`) and **29.5 h** (`bybit XAUT`) — only `bybit BTC` re-entered at the close.

That is not immediate. Round 284's finding came from replay, and Round 300 established
that replay comparisons across windows are unsound; this is live evidence pointing the
other way for the within-run flat/re-entry pattern too. I am recording it as an
observation on **three routes**, not as a refutation: the gaps are derived from
`decisions_since_target_change × 5 min`, which assumes uninterrupted 5-minute decisions.

That assumption is **invalid** for `exness XAU` (weekend closure, worker 28 h stale) and
for `binance XAU` (its checkpoint market data ends 2025-12-25), so those two rows are
excluded from the claim.

## What is proven, and what is not

Proven:

- All six routes hold a non-flat `current_target` at 2026-08-30T04:32Z: `binance BTC`
  long, the other five short, every `reason` = `multi_timeframe_gate_passed`.
- `decisions_since_target_change` = 342 / 330 / 330 / 156 / 39 / 102 against
  `minimum_holding_decisions` = 36; `waiting_after_protective_exit` = false on all six.
- `gate_passed` = false on five routes, true on `exness BTC`; reasons as tabulated.
- The `entry_score`/`trend_score` pairs reproduce five of the six reported gate reasons
  under the 0.1 role-score threshold.
- Samples appended to `research/quant/samples/position-state-samples.csv` (12 rows) and
  `research/quant/samples/signal-state-samples.csv` (27 rows).

Not proven, and deliberately not claimed:

- **That the drought is normal or abnormal.** It is *explained* — six open positions,
  five blocked gates — which is not the same as being expected. No null model was run,
  as in Round 306.
- Any cause for the five closes clustering in a two-hour band on 2026-08-28. A common
  market move across gold and BTC is plausible and untested; I am not asserting it.
- That the flat gaps refute Round 284. Three routes, one snapshot, and gaps computed
  from a decision counter rather than from timestamps.
- Any Target 3 verdict. Unchanged from Round 306: 13 closes is a baseline.
- That the gates are correctly *calibrated*. What is verified is that they behave as
  written. Whether `minimum_role_score = 0.1` is the right threshold is a different
  question and was not examined.
