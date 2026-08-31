# Round 272 — Occupancy is not the problem: `binance XAU` sits in the market *more* than the healthiest route. The entire difference is hold duration.

Classification: **NEEDS-MORE-RESEARCH**. Read-only production evidence.
**Zero containers.**

## Round 271's gap, and an identity that closes it

Round 271 ended on: *"position duration per route was not measured."* That is the
quantity that decides whether a low close rate means the system is **idle** or merely
**holding**. It decomposes exactly:

```
closes/week  =  occupancy × 168h / mean_hold_hours
```

Computed from each route's retained `paper-backtest-fixed-pct` trade history, the
identity reproduces the observed rate **to two decimals on all four routes**, which
validates the decomposition rather than assuming it.

| route | n | span | **occupancy** | **mean hold** | median hold | closes/week |
|---|---|---|---|---|---|---|
| binance BTC | 473 | 362 d | **59.6%** | **10.96h** | 6.17h | 9.14 |
| **binance XAU** | **7** | **14 d** | **63.5%** | **29.98h** | 29.92h | **3.56** |
| bybit XAUT | **1** | **1 d** | 100.0% | 32.92h | 32.92h | 5.10 |
| exness XAU | 392 | 361 d | 86.7% | 19.17h | 8.46h | 7.60 |

## Occupancy is ruled out

**`binance XAU` holds a position 63.5% of the time — *more* than `binance BTC`'s
59.6%, the healthiest route in the fleet.** It is not idle, it is not sitting out of
the market, and its low lifetime trade count is not an exposure problem.

Combined with Round 271's snapshot (4 of 5 routes holding open positions right now,
`binance XAU` among them), the "dormant route" reading is now contradicted from two
independent directions.

## The entire difference is hold duration

`binance XAU`'s mean hold is **29.98h against `binance BTC`'s 10.96h — 2.74x
longer**, on the same broker with the same protective band. Exits are stop (1%),
take (2%) or flat, so a longer hold means the price takes longer to travel the same
*fractional* distance.

That is Round 261's P1 mechanism, which was only "partially confirmed, weaker than
predicted" there (1.37x hold ratio against a 2.39x volatility prediction). **Here it
fits far better**: gold against BTC is roughly a 2.4x volatility contrast (Round 258
band volatilities ≈ 0.43% vs ≈ 1.0% per 4h), against the 2.74x hold ratio observed.
Round 261's comparison was muddied by `exness XAU`'s weekend closure; this one is
within a single broker.

So the effect is located: **downstream of the gate, in exit timing** — where Round
270 suspected it but could not confirm.

## The sample warning, which is not a footnote here

**`binance XAU`'s figures come from 7 trades over 14 days, and `bybit XAUT`'s from a
single trade over one day.** Those are the two routes the whole question is about,
and they carry essentially no statistical weight. The occupancy and hold numbers
above are arithmetic facts about those 7 and 1 trades, not estimates of the routes'
behaviour.

The only well-sampled comparison is `binance BTC` (473 trades) against `exness XAU`
(392): occupancy 59.6% vs 86.7%, hold 10.96h vs 19.17h — **both levers move, and they
partly offset**, netting 9.14 against 7.60 closes/week.

## What is proven, and what is not

Proven:

- The identity `closes/week = occupancy × 168 / mean_hold` reproduces each route's
  observed rate exactly, on all four.
- The occupancy, mean-hold and median-hold figures tabulated, as arithmetic over each
  route's retained trade history.
- `binance XAU`'s occupancy (63.5%) exceeds `binance BTC`'s (59.6%).

Not proven, and deliberately not claimed:

- **That `binance XAU` typically holds 63.5% of the time or 29.98h per trade.**
  Seven trades over fourteen days. This rules occupancy out as an *explanation of
  those seven trades*; it is not a characterisation of the route.
- Anything at all about `bybit XAUT`. One trade.
- That volatility explains the hold ratio. 2.74x observed against a ~2.4x volatility
  contrast is suggestive and was **not** tested — Round 261 made exactly this kind of
  comparison and found it weaker than predicted.
- That long holds are a defect. A less volatile instrument reaching a fixed
  fractional band more slowly is expected behaviour, not a fault; whether the band
  *should* be volatility-scaled is a separate question Rounds 81-82 closed on
  cross-broker grounds for PnL, never for frequency.
- Anything about PnL or Target 3.
