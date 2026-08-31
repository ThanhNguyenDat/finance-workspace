# Round 237 — XAU's hold lever barely moves, and loss per trade turns out to be the same constant across both instruments and every hold from 12 to 144

Classification: **NO-CHANGE**. Two bounded Docker sweeps.

## The gap Round 236 named

Round 236 measured BTC's hold lever and explicitly did not run XAU, noting XAU is
already below the Target 3 floor so its hold lever has less room. This runs it,
in the direction that matters for XAU: **shortening** hold, since extending it
would breach the floor further.

exness XAU/USD 5m, 1,800 days, `one_target`:

| hold | trades | trades / week | PnL | PnL per trade | trade_reduction_fraction |
|---|---|---|---|---|---|
| **12** | 907 | 3.53 | −6.121 | −0.00675 | 0.071 |
| **36** (production) | 830 | 3.23 | −5.262 | −0.00634 | 0.150 |

## Result 1 — on XAU the hold lever is nearly inert

Tripling the hold (12 → 36) changes trades by only **−8.5%**. On BTC, quadrupling
it (36 → 144) changed trades by **−53.1%**.

The reason is visible in `trade_reduction_fraction`: **0.07-0.15 on XAU against
0.61-0.82 on BTC**. The hold constraint rarely binds on XAU because the signal
already fires rarely. There is no meaningful frequency lever there in either
direction.

## Result 2 — loss per trade is the same constant everywhere

Collecting all four Portfolio-layer measurements from this round and Round 236:

| instrument | hold | trades | PnL | **PnL per trade** |
|---|---|---|---|---|
| BTC | 36 | 3,825 | −28.183 | **−0.00737** |
| BTC | 144 | 1,793 | −12.204 | **−0.00681** |
| XAU | 12 | 907 | −6.121 | **−0.00675** |
| XAU | 36 | 830 | −5.262 | **−0.00634** |

**Trades vary 4.6x. Total PnL varies 5.4x. Loss per trade varies 14%**, sitting in
a band of −0.00737 to −0.00634 around a mean of **−0.0068**.

Two instruments, two brokers, hold values spanning 12 to 144 — and the per-trade
loss is effectively one number. **Total loss is trade count times a constant, and
nothing else this program has adjusted moves that constant.**

This is the strongest form the fixed-per-trade-toll model has taken. Rounds 217
and 227 measured friction as flat per trade within one instrument; this shows the
*net* per-trade outcome is flat **across** instruments and configurations too.

## Result 3 — the price of satisfying Target 3 on XAU

Measured: shortening hold from 36 to 12 buys **+0.30 trades/week** (3.23 → 3.53)
and costs **−0.859 PnL** (−5.262 → −6.121, 16% worse).

Projected, and labelled as such: reaching the **7.0/week** floor from 3.23 needs
**2.17x** the trades. At the measured constant of −0.0068 per trade that projects
to a PnL near **−11.4**, roughly **double the current loss**.

That is a projection from a constant measured over 4.6x variation in trade count,
not an extrapolation of a fitted curve — but it is still a projection, and no
configuration was found that actually produces 7 trades/week on XAU.

So both instruments now answer the Target 3 question the same way, from opposite
sides: **BTC pays for satisfying the floor with 48x cost/gross, and XAU would pay
for satisfying it with roughly double its loss.** The floor is expensive wherever
it binds.

## Note on a measurement discrepancy

Round 234's `--daily-profit-gate` reported XAU at **4.52 trades/week**; `one_target`
here reports **3.23**. Different paths over different spans — the gate evaluates
the deployed policy on holdout only (~360 days), `one_target` covers the full
1,800-day window. Both sit far below 7.0 and the conclusion is unchanged, but the
two numbers should not be quoted interchangeably.

## What is proven, and what is not

Proven:

- exness XAU 5m: hold 12 gives 907 trades / −6.121; hold 36 gives 830 / −5.262.
- `trade_reduction_fraction` is 0.07-0.15 on XAU against 0.61-0.82 on BTC.
- Across four Portfolio measurements spanning two instruments and hold 12-144,
  PnL per trade lies in [−0.00737, −0.00634], a 14% band, while trades vary 4.6x.

Not proven, and deliberately not claimed:

- That −0.0068 holds outside this range. Four points, one interval (5m), one
  window each; the constancy is an observation over the measured range, not a law.
- The projected −11.4 at 7 trades/week. It is arithmetic on the constant, not a
  measured configuration, and no setting was found that reaches 7/week on XAU.
- That the gate and `one_target` frequencies should reconcile. They measure
  different spans and were not reconciled here.
