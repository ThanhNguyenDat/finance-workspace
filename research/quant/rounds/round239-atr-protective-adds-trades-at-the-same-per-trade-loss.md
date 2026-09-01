# Round 239 — ATR-scaled protective levels: 73% more trades at an unchanged per-trade loss, and the marginal trade costs the same as the average one

Classification: **NO-CHANGE**. Two completed Docker sweeps plus one rejected on a
bad flag value — see the budget note.

## Why this lever, now

Round 238 showed widening a **fractional** stop worsens per-trade economics 65%,
because a fixed wider stop lets every loser run further. An **ATR-scaled** stop is
the mechanism that should avoid exactly that: it widens only when volatility
justifies it. The SUMMARY also lists `--portfolio-atr-periods` as the one
genuinely unexplored item left in the Rule 1 family, and Round 82 closed ATR on
**BTC** cross-broker — never on XAU.

So this is a principled test derived from this session's model, not a parameter
sweep.

exness XAU/USD 5m, 1,800 days, `one_target`, hold 36:

| protective | trades | trades / week | PnL | **PnL per trade** |
|---|---|---|---|---|
| fractional 0.010 / 0.020 (production) | 830 | 3.23 | −5.262 | **−0.00634** |
| fractional 0.020 / 0.040 (Round 238) | 275 | 1.07 | −2.876 | −0.01046 |
| **atr_multiple 2.0 / 4.0, periods 14** | **1,433** | **5.57** | **−9.459** | **−0.00660** |

## Result — ATR changes the count, not the constant

ATR-scaled protection produces **73% more trades** (830 → 1,433) and **80% more
loss** (−5.26 → −9.46), while **loss per trade moves only 4%** (−0.00634 →
−0.00660) — well inside the 14% band Round 237 measured for the constant.

So ATR behaves like the **hold** lever, not like fractional widening:

| lever | trade count | loss per trade |
|---|---|---|
| hold (r236-237) | large reduction | unchanged |
| fractional widening (r238) | large reduction | **65% worse** |
| **atr_multiple (this round)** | **73% increase** | **unchanged** |

It is the first lever measured that moves the count **upward**, and it does so at
the same per-trade cost.

## The sharpest form of the model so far

Because ATR adds trades rather than removing them, the marginal economics become
directly computable:

- extra trades: **603**
- extra loss: **−4.197**
- **marginal loss per trade: −0.00696**
- average loss per trade at production: −0.00634

**The marginal trade costs within 10% of the average trade.** There is no subset
of trades that is better — adding 603 more of them adds loss at essentially the
same rate the existing 830 lose at.

That is the strongest statement this session can make about the system's
economics: **average and marginal are the same, so no selection or throttling of
trades changes the outcome per unit of trading.** It closes the loop on Rounds
236-238 — trading less loses less, trading more loses more, and nothing available
alters the rate.

Note also that ATR moves frequency to **5.57/week**, materially closer to the
Target 3 floor of 7.0 than production's 3.23 — and it costs 80% more loss to get
there. That is the Round 234/237 trade-off measured on a third lever, at the same
constant rate.

## What is proven, and what is not

Proven:

- exness XAU 5m, hold 36: `atr_multiple` 2.0/4.0 at 14 periods gives 1,433 trades
  and −9.459, against production `fractional` 0.010/0.020 at 830 and −5.262.
- Loss per trade −0.00660 vs −0.00634, a 4% difference.
- Marginal loss per added trade is −0.00696, within 10% of the production average.

Not proven, and deliberately not claimed:

- That other ATR multiples or periods behave the same. Only 2.0/4.0 at periods 14
  was run; the SUMMARY's open item — varying `--portfolio-atr-periods` itself —
  remains open.
- That ATR is worse on BTC too. Round 82 closed ATR there on cross-broker
  grounds; this round did not re-run BTC.
- That ATR is a way to reach Target 3. It gets to 5.57/week, still short of 7.0,
  at 80% more loss — and Round 237's projection says the remainder costs at the
  same rate.

## Budget note

Three container starts, two completed. The first was rejected within 45 seconds
by argument validation: I passed `--portfolio-protective-kind atr`, and the
accepted value is `atr_multiple` (`finance-research/src/execution_rules.rs:157`).
No backtest work was done in that run, but it was a container start against a
two-per-round limit and is recorded rather than omitted.
