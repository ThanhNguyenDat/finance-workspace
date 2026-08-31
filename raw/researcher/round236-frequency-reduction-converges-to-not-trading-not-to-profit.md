# Round 236 — Testing Round 234's untested assertion: quadrupling the hold cuts the loss 57%, and loss per trade barely moves. Frequency is a mitigation lever with a floor at zero

Classification: **NO-CHANGE**. Two bounded Docker sweeps.

## The assertion being tested

Round 234 measured the deployed Portfolio policy and found BTC at cost/gross
48.20, then asserted — without testing — that "48x is not closable by frequency
alone". That is exactly the kind of claim this session has repeatedly had to
retract, so it gets measured.

`one_target` is the only Portfolio measurement the skill trusts for anything
involving the hold configuration (Round 82). binance BTC/USDT 5m, 1,800 days,
varying only `--portfolio-minimum-hold-decisions`:

| hold | trades | trades / week | realized PnL | **PnL per trade** | trade_reduction_fraction |
|---|---|---|---|---|---|
| **36** (production default) | 3,825 | 14.87 | **−28.183** | **−0.00737** | 0.608 |
| **144** | 1,793 | **6.97** | **−12.204** | **−0.00681** | 0.816 |

## The shape is the answer

Quadrupling the hold period:

- trades fall **53.1%**
- loss falls **56.7%**
- **loss per trade improves only 7.6%**

The loss reduction comes almost entirely from **trading less**, not from
**trading better**. Loss is approximately trades x a constant, which is the
fixed-per-trade-toll model of Rounds 217, 227 and 234 now confirmed at the
Portfolio layer on the deployed policy rather than inferred from Alpha sweeps.

**Round 234's assertion holds, and can now be stated more strongly than it was
asserted:** frequency reduction is a **loss-mitigation lever whose limit is
zero**, not a path to profit. Extrapolating a per-trade loss that stays near
−0.007 regardless of hold, the frequency that minimises loss is the one that
minimises trading. It converges to *don't trade*, never to *trade profitably*.

That is consistent with, and independent of, Rounds 213-215 (cost levers worth
approximately nothing) and Rounds 231-232 (the population carries only ~1.5x
chance-level persistence). Three different measurement paths, same conclusion.

## The frequency floor and the loss-minimising direction meet at hold ≈ 144

At hold=144 the route produces **6.97 trades/week** against the Target 3 floor of
**>= 7.0**. The two constraints touch almost exactly there.

That is the quantitative answer to the question Round 92 closed on judgement:
"how far can hold be extended before Target 3 breaks?" — for BTC on this window,
**hold ≈ 144 (12 hours), and the loss at that point is still −12.2**.

So the product decision Round 234 surfaced now has both of its numbers:

- keep Target 3 as a floor → hold capped near 144 → loss ~−12.2 instead of −28.2;
- treat Target 3 as negotiable → loss keeps falling toward zero as trading stops.

Neither branch reaches profit. Research cannot choose between them; it can say
that the choice is between *losing less* and *losing least*, not between losing
and winning.

## What is proven, and what is not

Proven:

- binance BTC 5m, 1,800 days, `one_target`: hold 36 gives 3,825 trades and
  −28.183; hold 144 gives 1,793 trades and −12.204.
- Loss per trade is −0.00737 and −0.00681 respectively — a 7.6% improvement
  against a 53.1% reduction in trades.
- hold=144 corresponds to 6.97 trades/week, essentially exactly the >= 7.0 floor.

Not proven, and deliberately not claimed:

- The shape between and beyond these points. **Two measurements do not define a
  curve**, and after Round 230's lesson I am not fitting one. What is claimed is
  the ratio between the two effects at these two settings.
- That the same holds for XAU. Round 234 measured XAU at 4.52 trades/week
  already, so its hold lever has far less room; not run here.
- That hold=144 is a recommendation. It is where two constraints intersect on one
  instrument and one window, not a validated configuration — and Round 87
  measured hold x stop/take as sub-additive, so it cannot be combined with other
  levers by assumption.
