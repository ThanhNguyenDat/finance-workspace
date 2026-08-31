# Round 329 — NEEDS-MORE-RESEARCH: the frequency-as-cost-multiplier result **replicates on `binance BTC`** — both orderings hold, gross stays roughly flat across a **5.4x** frequency range. The **magnitude** differs enormously: net loss worsens **2.7x** here against **142x** on XAU.

Classification: **NEEDS-MORE-RESEARCH** — my pre-registered replication holds on both
axes; magnitudes differ and one metric turns out uninterpretable on this route. Two
bounded Docker sweeps (exactly the 2-container budget).

## The limit Round 328 named

Round 328's within-route ladder was the strongest result of this arc, and it named its
own gap first: *"That this generalises to other routes. **One route.** The five other
routes were not laddered."*

This round repeats the identical ladder on **`binance BTC`** — the flagship, and the
route with an existing 500-day gate baseline. It is BTC rather than XAU by design: the
XAU route was laddered last round, and a replication has to be on a *different* route.

**Pre-registered:** Sharpe orders inversely with trades/week (wide > deployed > ATR),
and `gross_pnl_before_costs` stays roughly flat while cost÷gross rises. Refuted if the
Sharpe ordering is violated or gross moves proportionally with frequency.

## The replication

`binance BTC/USDT`, `--days 500`, deployed costs, identical holdout (101 observed days):

| band | trades | tr/wk | pos-day | streak | Sortino | **Sharpe** | cost÷gross | gross | net |
|---|---|---|---|---|---|---|---|---|---|
| wide fractional 0.02/0.04 | 218 | **15.26** | **0.475** | 10 | −5.984 | **−5.730** | 0.76 | −1.9515 | −3.4406 |
| deployed fractional 0.01/0.02 | 312 | 21.84 | 0.416 | 7 | −6.817 | −6.753 | 1.20 | −1.7909 | −3.9406 |
| ATR 1.5/3.0 | 1,176 | **82.32** | **0.139** | **27** | −13.481 | **−18.871** | 6.46 | −1.2520 | **−9.3378** |

**Both orderings hold.** Frequency 15.26 < 21.84 < 82.32; Sharpe −5.730 > −6.753 >
−18.871. The prediction is confirmed on a second route.

## Direction replicates, magnitude does not

| | `exness XAU` (r328) | `binance BTC` (this round) |
|---|---|---|
| frequency range wide → ATR | **7.32x** | **5.39x** |
| gross change | **+12.7%** | **+35.8%** |
| cost ÷ gross | 1.05 → 7.25 | 0.76 → 6.46 |
| **net loss change** | **142x** | **2.7x** |
| Sharpe wide → ATR | −0.096 → −23.225 | −5.730 → −18.871 |

**The mechanism is the same on both: gross barely moves while cost scales with trade
count.** A 5-7x frequency increase produces a 13-36% change in gross — far from
proportional — so the extra trades carry cost without carrying edge.

**The net-loss multiplier differs by ~50x between the routes**, and the reason is where
each starts: `exness XAU`'s wide band is nearly break-even (−0.0301), so any added cost
is a huge relative worsening; `binance BTC` is already deep in loss (−3.4406), so the
same mechanism moves it proportionally much less. The **ratio** is misleading; the
**direction and the flat-gross mechanism** are what replicate.

## Two honest caveats from this run

**`cost ÷ gross` is not interpretable on `binance BTC`.** All three bands have
**negative** gross, so "cost is X times the gross profit" has no meaning there. Only the
ratio's *direction* (0.76 → 1.20 → 6.46, rising with frequency) is used, and its
**levels are not comparable** to `exness XAU`'s, where gross is positive. The check that
matters on this route is `gross_pnl_positive`, which all three bands fail.

**The negative-day streak does not follow frequency on either route.** `exness XAU` runs
5 / 4 / 16 and `binance BTC` 10 / 7 / 27 — in both cases the *deployed* band has the
shortest streak, not the widest. Streak is not part of the pattern, and I am not folding
it in.

Also worth noting: `binance BTC`'s wide band has **positive-day ratio 0.475** — the
highest of any configuration measured on either route — and still fails the 0.55
threshold.

## What is proven, and what is not

Proven:

- `binance BTC` at `--days 500`, identical holdout, three bands: wide 218 trades /
  15.26 per week / Sharpe −5.730 / gross −1.9515 / net −3.4406; deployed 312 / 21.84 /
  −6.753 / −1.7909 / −3.9406; ATR 1,176 / 82.32 / −18.871 / −1.2520 / −9.3378.
- Both pre-registered orderings hold on this route, as they did on `exness XAU`.
- Gross moves +35.8% across a 5.39x frequency range; cost÷gross rises 0.76 → 6.46; net
  loss worsens 2.7x.
- All three bands fail the gate, including `gross_pnl_positive`.

Not proven, and deliberately not claimed:

- **That the mechanism holds on the other four routes.** Two of six laddered.
  `exness BTC`, `bybit BTC`, `bybit XAUT` and `binance XAU` were not.
- That the net-loss multiplier means anything comparable across routes. 142x against
  2.7x reflects each route's starting distance from break-even, not a difference in
  mechanism.
- That `cost ÷ gross` levels on `binance BTC` are meaningful. Negative gross makes the
  ratio uninterpretable; only its direction is used.
- That gross is *unaffected* by frequency. It moved 12.7% and 35.8% — small against
  5-7x, not zero, and I have not tested whether either is meaningful.
- That the wide band is preferable on `binance BTC`. It has the better Sharpe and
  positive-day ratio but a **worse** gross (−1.9515 against −1.7909) and still fails
  every gate check. **No promotion is proposed.**
- Any window-independence. Both ladders are `--days 500` only; Rounds 318-322 apply.
