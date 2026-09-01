# PATH IDENTIFIED (Round 323)

The "rest of the path" this file could not identify **does not exist**. Cost enters the
simulation only through the PnL arithmetic (which cannot change a trade count) and the
**cost gate**; with `decision_count` identical between arms at all three windows and
`execution_cost` the only non-zero risk bucket, the cost gate is by elimination the only
mechanism for `one_target` and `legacy_selected_rule`.

What actually varies is **trades lost per rejection — 0.055 / 0.636 / 3.242 at
360 / 700 / 900 days, a 59x swing** — while the rejection count itself is not monotone.
See `round323-NEEDS-MORE-RESEARCH-the-missing-path-is-the-cost-gate-what-varies-is-59x-in-trades-lost-per-rejection.md`.

---

# Round 322 — DATA-ISSUE: `edge ÷ cost` is **not a per-trade cost ratio**. Its denominator is contaminated by a trade-selection change that grows from **4% to 43%** with window depth.

Classification: **DATA-ISSUE** — my pre-registered check on the 900-day point held, but
measuring the arm I had been estimating exposed a defect in how the ratio itself is
computed. Two bounded Docker sweeps (exactly the 2-container budget), **XAU-first**.

## The limit Round 321 named

Round 321 closed with: *"That the 26-59% range is measured. Only the 360-day point has
its own cost-per-trade; the other four reuse it, so those four ratios are estimates."*

That is cheap to fix at the end that matters: the **deep** windows produce the most
pessimistic ratios, and 26.0% at 900 days is the number driving "a 74% cost cut is
needed". This round runs the **deployed-cost arm** at 700 and 900 days so those points
are measured rather than inferred.

**Registered before running:** the measured edge-to-cost at 900 days lands within ±25%
of the 26.0% estimate — i.e. between **19.5% and 32.5%**. Refuted outside that, which
would mean cost-per-trade varies by window and the whole estimated range is unreliable.

## The result: the check holds at 900d, and fails badly at 700d

`exness XAU/USD`, same day, zero cost against deployed 5/2 bps:

| `--days` | 0-cost trades | 0-cost pnl | deployed trades | deployed pnl | gross/tr | net/tr | **cost/tr** | **edge ÷ cost** | cut needed |
|---|---|---|---|---|---|---|---|---|---|
| 360 | 391 | +1.0997 | 374 | −2.4441 | +0.00281 | −0.00654 | **0.00935** | **30.1%** | 70% |
| **700** | 645 | +1.7832 | **509** | −1.8103 | +0.00276 | −0.00356 | **0.00632** | **43.7%** | 56% |
| **900** | 715 | +1.7386 | **404** | −3.0651 | +0.00243 | −0.00759 | **0.01002** | **24.3%** | 76% |

**900 days measures 24.3% against the 26.0% estimate — the pre-registration holds**
(7.0% error).

**700 days measures 43.7% against the 29.6% estimate — a 32% error.** The constant-cost
assumption behind Rounds 319 and 321 is materially wrong at that window, even though
both rounds flagged those figures as estimates.

## Why the denominator moves — and why the metric is misnamed

Under `fixed_notional` sizing the per-fill cost should be constant, so `cost/trade`
ought not to move. It moves **1.58x** (0.00632 to 0.01002). The reason is that
`cost/trade` as computed here is `gross/trade − net/trade` — a difference of **two
averages over different trade populations**:

| `--days` | trades at 0 cost | trades deployed | **reduction** |
|---|---|---|---|
| 360 | 391 | 374 | **−4.3%** |
| 700 | 645 | 509 | **−21.1%** |
| 900 | 715 | 404 | **−43.5%** |

**The deployed arm loses progressively more trades as the window deepens**, and by 900
days it trades **43.5% less** than the zero-cost arm. So the quantity I have been
calling "cost per trade" absorbs a **selection change**, not only a cost.

That makes `edge ÷ cost` **not** the thing its name implies. It is the ratio of a
zero-cost per-trade average to the gap between two per-trade averages computed over
different trade sets — and that gap is increasingly dominated by *which trades survive*
rather than *what each trade costs*.

Note the `execution_cost` rejection counts do **not** explain the pattern on their own —
181, 236 and **120** at 360/700/900 days, which is not monotone while the trade
reduction is. So the trades are being lost through more than the cost gate's explicit
rejections, and I have not identified the rest of the path.

## What this does to the published range

Rounds 319 and 321 quoted **26-59%** (a 41-74% cut) from one measured point and four
estimates. The three **measured** points are **30.1%, 43.7% and 24.3%** — needing a
**56-76%** cost cut. The 59.1% figure at 500 days is still an estimate and, given the
700-day error ran in the optimistic direction, should be treated as unverified rather
than as the top of a range.

**The direction is unchanged**: the edge covers cost at no window measured. What changes
is that the optimistic end of the published range rests on estimates that have now been
shown capable of a 32% error.

## What is proven, and what is not

Proven:

- `exness XAU` deployed-cost arms, same day: 700d → 509 trades / −1.8103;
  900d → 404 trades / −3.0651. With the zero-cost arms already measured, this gives
  cost/trade 0.00935 / 0.00632 / 0.01002 and edge-to-cost 30.1% / 43.7% / 24.3% at
  360 / 700 / 900 days.
- The deployed arm trades 4.3%, 21.1% and 43.5% less than the zero-cost arm at 360,
  700 and 900 days.
- `execution_cost` rejections 181 / 236 / 120 — not monotone in depth, unlike the trade
  reduction.
- The 900-day pre-registration holds (24.3% inside 19.5-32.5%); the 700-day estimate
  was wrong by 32%.

Not proven, and deliberately not claimed:

- **Any mechanism for the growing trade loss.** The cost-gate rejection counts do not
  track it, so something else is dropping trades at depth and I have not found it. I am
  not proposing a candidate — Rounds 279-284 remain the standing reason, and Round 312
  already showed one of my mechanisms making a wrong prediction.
- That the correct ratio is 24-44%. Three measured points on one route, and Rounds
  300-312 mean none of them is a window-independent property.
- That 500 days is 59.1%. That point remains an estimate and is now the least trusted
  of the five.
- Any change to the profitability conclusion, or any PF, win rate, Sharpe, Sortino,
  drawdown, streak or SQN. Unchanged since Round 313.
- That the `exness XAU` sign result is affected. Round 321's ten-of-ten positive
  zero-cost values are untouched by this — the defect is in the **ratio**, not in the
  zero-cost measurements.
