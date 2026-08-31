# PARTIALLY UN-SCOPED (Round 319)

The blanket scoping above is **too broad for the strongest cell**. `exness XAU` was
re-run at zero cost across **250, 360 and 500 days** and is positive on **both measures
at all three** (+1.4354 / +1.0997 / +3.0359 on `one_target`), so its positive raw edge is
**window-robust across that range** — not a 360-day artifact.

Across all nine zero-cost cells, **0 of 3 with `|one_target| ≥ 1.0` disagree between
measures, against 2 of 6 below 1.0**: the instability this file identified lives in the
**near-zero** cells (`exness BTC`, `bybit XAUT`), where the caution still fully applies.
Note the *magnitude* remains window-dependent — per-trade edge swings 1.97x. See
`round319-NEEDS-MORE-RESEARCH-the-sign-is-window-robust-on-the-strongest-cell-but-the-magnitude-swings-2x.md`.

---

# Round 318 — DATA-ISSUE: the control **fails**. A route's raw-edge sign agreement does not survive a 110-day window change, so cost-ablation conclusions do **not** transfer between windows.

Classification: **DATA-ISSUE** — my pre-registered decision rule returned
**INCONCLUSIVE** on the primary question, and the reason is a method limitation I had
been assuming away. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**.

## The design, and why it was chosen

Round 317 identified the cell that would settle market-type versus instrument —
**`binance XAU`, XAU on a perpetual future** — and its blocker: only 262 days of 5m
history, so it cannot be run at `--days 360`.

Rather than work around that, this round moved the **whole comparison** to a window
`binance XAU` can support, and spent the second container on a **control**:
`bybit XAUT`, whose 360-day sign is known positive on both measures. Both runs at
`--days 250`, zero execution cost, same day.

**Pre-registered, before running:**

| condition | conclusion |
|---|---|
| control (`bybit XAUT`) sign flips at 250d | the window is not comparable — **inconclusive** |
| control holds, `binance XAU` negative & measures agree | **market type wins** |
| control holds, `binance XAU` positive & measures agree | **instrument wins** |
| `binance XAU` measures disagree | ambiguous |

## The result: the control failed

| window | route | market | asset | `one_target` | guard-free | trades | measures agree |
|---|---|---|---|---|---|---|---|
| 360d | `exness XAU/USD` | cfd | XAU | +1.0997 | +1.5993 | 391 | yes |
| 360d | `exness BTC/USD` | cfd | BTC | +0.5634 | −0.4548 | 508 | **NO** |
| 360d | `bybit XAUT/USDT` | spot | XAU | **+0.3427** | **+0.0936** | 278 | **yes** |
| 360d | `bybit BTC/USDT` | perp | BTC | −0.3654 | −1.0816 | 320 | yes |
| 360d | `binance BTC/USDT` | perp | BTC | −0.4432 | −2.0053 | 479 | yes |
| **250d** | **`binance XAU/USDT`** | **perp** | **XAU** | **−0.4474** | **−0.4543** | 174 | **yes** |
| **250d** | **`bybit XAUT/USDT`** | **spot** | **XAU** | **+0.6346** | **−0.1791** | 192 | **NO** |

**`bybit XAUT` agreed positive at 360 days and disagrees at 250.** The control fails,
and by my own rule the primary question is **inconclusive**.

## The methodological finding, which is the real result

Round 308 established that a **fixed-`--days` A/B is the one comparison the Round 300
confound leaves clean**, and Rounds 313-317 leaned on that. It is still true — *within*
a window.

What this round shows is the part I had been assuming without testing: **conclusions do
not transfer between windows.** A route's raw-edge sign, and even whether its two
measures agree on that sign, is **not a window-independent property**. I designed this
round on the unstated assumption that it was.

So the five-cell table from Rounds 313-317 describes **the 360-day window**, not "the
fleet". Every statement in it — market type splitting cleanly, asset not, Exness-
specificity ruled out — is scoped to that window and was never shown to hold at another.

## What can still be said

**`binance XAU` at 250 days is negative on both measures** (−0.4474 and −0.4543,
**−0.00257/trade**) — a solid cell, and squarely in the range the other two perpetual
routes occupy at 360 days. It *points* toward market type.

But the contrast it was meant to feed — XAU-on-perpetual against XAU-on-spot **at the
same window** — rests on `bybit XAUT` at 250 days, which is ambiguous. That is the
identical defect that stopped `exness BTC` from settling the question at 360 days: the
deciding comparison keeps landing on a cell whose sign is not solid.

A small observation, offered as a hypothesis and not a finding: both
measure-disagreement cells (`exness BTC` at 360d, `bybit XAUT` at 250d) have small
`|PnL|` on both measures, consistent with an edge indistinguishable from zero. But
`binance XAU` at 250d has similarly small values (−0.45 on both) and **agrees**, so
magnitude alone does not explain it, and trade count does not either (508 is the
highest measured, 192 the lowest).

## What is proven, and what is not

Proven:

- At `--days 250`, zero cost, same day: `binance XAU/USDT` 174 trades, `one_target`
  **−0.4474**, guard-free −0.4543, measures agreeing; `bybit XAUT/USDT` 192 trades,
  `one_target` **+0.6346**, guard-free **−0.1791**, measures disagreeing.
- `bybit XAUT`'s two measures agreed positive at 360 days (+0.3427 / +0.0936) and
  disagree at 250 days — sign agreement is not stable across a 110-day window change.
- `binance XAU`'s 250-day gross edge is −0.00257/trade.

Not proven, and deliberately not claimed:

- **Any answer to market type versus instrument.** The pre-registered rule returned
  inconclusive and I am honouring it rather than reading the `binance XAU` cell on its
  own.
- That the 360-day five-cell picture is wrong. It is **scoped**: it describes that
  window, and nothing in this round contradicts it there.
- That `binance XAU` is negative in general. One window, on a route whose live
  checkpoint market data ends 2025-12-25 (Rounds 207, 306) even though Timescale holds
  complete klines to 2026-08-30 — a pairing Round 306 recorded and did not explain, and
  which I have not resolved either.
- Any explanation for why measures disagree on some cells. The magnitude hypothesis
  above is contradicted by `binance XAU` itself.
- Any magnitude, PF, win rate, Sharpe, Sortino, drawdown or streak. Unchanged since
  Round 313.
