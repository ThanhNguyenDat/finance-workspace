# Round 277 — Measured: `bybit BTC` occupancy is 43.3%, the lowest in the fleet. Target 3 failures have two distinct causes, not one.

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence.
**Zero containers.**

## Round 276's first job, done

Round 276 qualified the σ² law and named the next round's first job: *"occupancy was
**not measured** on that route. That is the next round's first job."* Round 272's
occupancy table covered four routes; the two it never measured are exactly the ones
needed.

| route | n | span | **occupancy** | mean hold | ledger /week |
|---|---|---|---|---|---|
| bybit XAUT | **1** | 1 d | 100.0% | 32.92h | — |
| exness XAU | 392 | 361 d | 86.7% | 19.17h | 7.60 |
| binance XAU | **7** | 14 d | 63.5% | 29.98h | 3.56 |
| exness BTC | 481 | 362 d | **60.3%** | 10.89h | 9.30 |
| binance BTC | 473 | 362 d | **59.6%** | 10.96h | 9.14 |
| **bybit BTC** | 311 | 363 d | **43.3%** | 12.14h | 5.99 |

## The reconciliation is confirmed

The three BTC routes have near-identical volatility, and — exactly as σ² requires —
**near-identical hold durations: 10.89h, 10.96h, 12.14h.** The σ² law is doing its
job on the quantity it actually governs.

**What differs is occupancy: 60.3%, 59.6%, and 43.3%.** `bybit BTC` sits flat far
more of the time than the other two.

Testing Round 276's argument against the identity `frequency = occupancy × 168 /
hold`:

```
predicted bybit/binance frequency ratio = (43.3/59.6) × (10.96/12.14) = 0.656
observed  one_target ratio              = 5.55 / 9.42                 = 0.589
```

Within 10%. Round 276 reasoned this out from the identity and flagged it as
**unmeasured**; it is now measured and it holds.

The ledger and `one_target` methods also agree independently: bybit BTC 5.99 vs 5.55,
exness BTC 9.30 vs 9.80, binance BTC 9.14 vs 9.42 — all within ~8%, from different
windows and different measurement paths.

## Target 3 has two distinct causes

| failing route | /week | cause | mechanism |
|---|---|---|---|
| binance XAU | 3.63 | **long holds** | lowest volatility in the fleet; σ² (Round 273) |
| **bybit BTC** | **5.55** | **low occupancy** | 43.3% against ~60% on sibling BTC routes |

**These are different failures.** Rounds 273-275 read the Target 3 shortfall as a
single volatility story; it is not. `bybit BTC` holds for a perfectly normal duration
and simply is not in the market often enough.

That also means the Round 274/275 conclusion — that frequency can only be bought with
proportional loss — was demonstrated **only for the hold-duration lever** (the
protective band). Whether raising *occupancy* carries the same proportional cost is
**untested**, and it is a different lever.

## What is proven, and what is not

Proven:

- Occupancy and mean hold for all six routes, from the same ledger histories.
- The three BTC routes hold 10.89h / 10.96h / 12.14h at near-identical volatility.
- `bybit BTC` occupancy 43.3% against 59.6% and 60.3%.
- The identity predicts the bybit/binance frequency ratio at 0.656 against an observed
  0.589.
- Ledger and `one_target` frequencies agree within ~8% on all three BTC routes.

Not proven, and deliberately not claimed:

- **What drives occupancy.** It varies 43.3%-86.7% across routes and is not explained
  by volatility. No cause is investigated here and none is guessed at.
- That raising occupancy would improve Target 3 without a proportional PnL cost.
  **Untested** — Rounds 274/275 tested only the band. Given per-trade cost is
  unchanged by every lever tried so far, the prior should be pessimistic.
- Anything from the two weak rows. `bybit XAUT` (n=1) and `binance XAU` (n=7) are in
  the table for completeness; their occupancy figures carry no weight.
- That `bybit BTC` fails Target 3 in production. Backtest and seed-ledger evidence
  only.
