# Round 238 — Stop/take does move the per-trade constant that hold could not, and it moves it the wrong way: 67% fewer trades, each 65% worse

Classification: **NO-CHANGE**. Two bounded Docker sweeps, both run detached and
removed per the skill's leak guidance.

## The question Round 237 set up

Round 237 measured loss per trade as an effective constant (−0.0068 ± 14%) across
two instruments and hold values from 12 to 144. Hold only gates *how many* trades
happen; it does not touch what happens inside one. **Stop/take does.** So the
sharp test is whether any Portfolio-construction lever can move the constant at
all.

exness XAU/USD 5m, 1,800 days, `one_target`, hold at the production default 36,
varying only `--portfolio-stop-value` / `--portfolio-take-value`:

| stop / take | trades | trades / week | PnL | **PnL per trade** |
|---|---|---|---|---|
| 0.005 / 0.010 | 831 | 3.23 | −5.293 | −0.00637 |
| **0.010 / 0.020** (production) | 830 | 3.23 | −5.262 | **−0.00634** |
| 0.020 / 0.040 | **275** | **1.07** | **−2.876** | **−0.01046** |

## Result 1 — halving the production levels changes nothing on XAU

0.005/0.010 against 0.010/0.020: trades 831 vs 830, PnL −5.293 vs −5.262. The two
settings are indistinguishable.

Round 83 measured widening from 0.005/0.010 to 0.010/0.020 as a **32-41% loss
reduction** — but on **BTC**. On XAU over this window that step is a **null**.
Not a contradiction of Round 83, which never claimed XAU; recorded as an
instrument-specific null so the lever is not assumed to transfer.

## Result 2 — doubling again does move the constant, downward

0.010/0.020 → 0.020/0.040:

- trades fall **66.9%** (830 → 275)
- total loss falls **45.3%** (−5.262 → −2.876)
- **loss per trade gets 65% worse** (−0.00634 → −0.01046)

So the answer to Round 237's question is **yes, stop/take moves the constant —
and it worsens it.** A wider stop lets each loser run further before it is cut;
total loss falls only because the trade count falls faster than the per-trade
loss grows.

## The Portfolio-lever picture, now complete

| lever | effect on trade count | effect on loss per trade | net |
|---|---|---|---|
| hold (Rounds 236-237) | large reduction | **unchanged** | loss ∝ count |
| stop/take widening (this round) | larger reduction | **65% worse** | loss falls, each trade worse |

**No Portfolio-construction lever available to this program improves per-trade
economics. They reduce loss only by reducing exposure, and one of them actively
degrades each remaining trade.**

That is consistent with, and independent of, Rounds 213-215 (cost levers worth
approximately nothing), Rounds 231-232 (population persistence ~1.5x chance) and
Round 236 (frequency reduction converges to not trading). Four measurement paths,
one conclusion: the Portfolio layer can shrink the loss but cannot change its
sign.

It also decomposes what Round 83 reported. That round recorded widening as a
~41%/32% loss reduction without separating the two effects. On XAU the same
direction of change is now visible as **67% fewer trades, each 65% worse** — the
headline improvement is an exposure reduction, not an execution improvement.

## What is proven, and what is not

Proven:

- exness XAU 5m, 1,800 days, hold 36: stop/take 0.005/0.010 gives 831 trades and
  −5.293; 0.010/0.020 gives 830 and −5.262; 0.020/0.040 gives 275 and −2.876.
- Loss per trade across that 4x stop/take range spans −0.00634 to −0.01046, a 39%
  spread — against the 14% band Round 237 measured across hold 12-144.
- The 0.005 → 0.010 step is a null on XAU.

Not proven, and deliberately not claimed:

- That 0.020/0.040 is preferable. It drops the route to **1.07 trades/week** on
  275 trades — far below any frequency target and a much thinner sample.
- That the same holds on BTC. Round 83 measured a real effect there for the step
  that is null here; this round did not re-run BTC.
- A curve. Three points on one instrument and one window; after Round 230 I am
  not fitting one, and Round 87 measured hold x stop/take as sub-additive so the
  two levers cannot be combined by assumption.
