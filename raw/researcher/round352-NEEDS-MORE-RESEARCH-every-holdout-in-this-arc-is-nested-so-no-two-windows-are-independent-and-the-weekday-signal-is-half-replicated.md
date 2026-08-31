# GATE METRICS SCORE A GUARD-FREE STREAM (Round 356)

Every `--daily-profit-gate` figure in this file — including the @1500 net **+0.22720** — comes
from a replay with **no minimum-hold guard and no risk layer**
(`daily_profit_gate.rs:376-412`; documented at `main.rs:255-263`, which is why
`--portfolio-minimum-hold-decisions` conflicts with the gate flag). It scores the
`legacy_selected_rule`-style stream, not the deployed `one_target` one.

Magnitude impact on PnL is small — guarded versus guard-free differs by **0.44% / 3.83% / 1.94%**
at @300 / @1500 / @1800 — so sign-level conclusions hold. **Trade count is the exception**: the
guard removes **21.1%** of trades at @300 (≈3% at the deep windows), so every `trades_per_week`
quoted from a gate run is an **upper bound** on the deployed rate, against a 7.0 threshold.
See `round356-DATA-ISSUE-the-daily-profit-gate-omits-the-construction-guard-and-the-risk-layer-so-it-scores-a-different-configuration.md`.

---

# WEEKDAY DIRECTION CLOSED (Round 355)

The concentration idea opened here is closed. Round 354 showed the pattern **inverts** on both BTC
routes, and round 355's permutation test shows the structural evidence is worth **p = 0.6013**
while the magnitude gives **p = 0.0532**, failing its registered α. This file's nesting finding —
that every holdout is nested and no two `--days` values give independent evidence — is unaffected
and remains the durable result of this round. See `round355-REJECTED-the-weekday-lead-closes-a-permutation-test-puts-negative-in-all-three-thirds-at-p-0-60.md`.

---

# DISJOINT PERIODS ARE AVAILABLE *WITHIN* ONE RUN (Round 353)

This file's conclusion — no two `--days` values give disjoint out-of-sample periods — is right
**across runs**. It does not hold **within** one run: a single replay's `daily_results` array can
be split into disjoint sub-periods, and being one replay they are internally consistent, which
round 343 showed they are *not* across runs. `exness XAU` @1800 yields three disjoint 102-day
thirds.

Re-running this file's weekday question that way, with strict single-hypothesis criteria (no
aggregation, which masked Monday's sign flip here): **Friday is positive in all three thirds and
Wednesday negative in all three**, at −0.01895 / −0.01486 / −0.01428 per day — **20.3x** the
overall daily mean. Monday and Thursday flip.

The ceiling is that **neither hypothesis was fresh**: thirds 2 and 3 are inside the very tables
in this file that suggested them. See `round353-NEEDS-MORE-RESEARCH-wednesday-is-negative-in-three-disjoint-periods-but-the-hypothesis-was-not-fresh.md`.

---

# Round 352 — NEEDS-MORE-RESEARCH: **every holdout in this arc is nested** — all six end on the same day and each larger one strictly contains the smaller. So "replicates across windows" has never meant independent evidence. The weekday split replicates on the registered criterion, but only **half** of it does.

Classification: **NEEDS-MORE-RESEARCH** — a real signal that survives its registered test, sitting
on a sample structure that cannot deliver independence. Two bounded Docker sweeps (exactly the
2-container budget), **XAU-first**.

## The question

The binding constraint on `exness XAU` is that gross edge is 60-88% of cost. If the edge were
**concentrated** in particular sessions, a time filter would cut trades — and cost — while keeping
most of the gross. That is the one shape of lever this arc has not tested, and it is the shape
that could close a 13% gap.

Choosing a weekday from the same data it is measured on is exactly the p-hacking the standing
prompt forbids, so the design was fixed first.

**Pre-registered as a partition**, on `exness XAU` @1200 (deployed band, 202-day holdout):
discover on the **first half** which weekdays have positive mean PnL; then, on the **second
half**, the discovered set's mean PnL is
- **> 0** → the concentration replicates; worth further study;
- **≤ 0** → it does not; weekday concentration is noise.

## Result — passes, and only half of it does

| weekday | n (A) | sum A | mean A | n (B) | **sum B** | mean B |
|---|---|---|---|---|---|---|
| Mon | 17 | +0.15138 | **+0.00890** | 17 | **−0.20063** | −0.01180 |
| Tue | 17 | −0.09391 | −0.00552 | 17 | +0.03464 | +0.00204 |
| Wed | 17 | −0.34699 | −0.02041 | 17 | −0.14885 | −0.00876 |
| Thu | 17 | −0.04285 | −0.00252 | 17 | −0.03404 | −0.00200 |
| Fri | 17 | +0.07437 | **+0.00437** | 17 | **+0.26986** | +0.01587 |
| Sat* | 16 | −0.06658 | −0.00416 | 16 | −0.05640 | −0.00353 |

\* the UTC+7 tail of the Friday session (correctness audit L3), not a trading day.

Discovery half A selected **{Mon, Fri}**. On half B that set gives n = 34, sum **+0.06924**, mean
**+0.002036 > 0** — **the registered criterion passes.**

**But it passes on aggregate while half its members fail.** Friday goes +0.07437 → **+0.26986**;
Monday goes +0.15138 → **−0.20063**, a sign flip. The set replicates because Friday outweighs
Monday, not because the pattern held.

And the discovery step itself carries no significance: with six weekday cells and n = 17,
**about three positive cells are expected under the null**. Selecting two of six and verifying is
one honest test of one hypothesis, not evidence of structure.

## What survives, and what kills it

Across every deployed-band window measured:

| window | Mon | Wed | **Fri** | Thu |
|---|---|---|---|---|
| @1200 half A | +0.151 | −0.347 | **+0.074** | −0.043 |
| @1200 half B | −0.201 | −0.149 | **+0.270** | −0.034 |
| @1500 | +0.243 | −0.656 | **+0.403** | +0.351 |
| @1800 | −0.032 | −0.818 | **+0.542** | +0.246 |

**Friday is positive in all four; Wednesday is negative in all four** — and Wednesday is the more
consistent of the two, being the single worst weekday everywhere.

**But these are not four samples.** This is the finding that matters:

| window | holdout |
|---|---|
| @300 | 2026-07-01 → 2026-08-28 |
| @900 | 2026-03-04 → 2026-08-28 |
| @1200 | 2026-01-02 → 2026-08-28 |
| @1500 | 2025-11-03 → 2026-08-28 |
| @1800 | 2025-09-03 → 2026-08-28 |

**Every holdout ends on the same day, and each larger window's holdout strictly contains all the
smaller ones.** They are perfectly nested. Two `--days` values can never give disjoint
out-of-sample periods, because the holdout is always the tail of a window ending at "now".

**Consequence for the whole arc.** Every cross-window claim made in Rounds 331-351 — "the optimum
moves with the window", "gross is positive at 300/500/900/1200", "the trough does not replicate" —
rests on nested samples. Window-*fragility* findings survive this (a superset behaving differently
is genuinely informative). **Window-*replication* findings do not mean what they sound like**: the
recent data is inside every sample, so agreement is partly guaranteed. My own Round 343 headline —
*"the first quantity in this arc to survive window variation"* — needs reading in that light.

**There is no way to fix this with the current CLI.** Disjoint holdouts would need an as-of or
end-date flag, and there is none (a standing limitation since the earliest rounds).

## An incidental result that must not be over-read

`exness XAU` @1500 is **net positive at deployed costs**: gross +0.95498, cost 0.72778, **net
+0.22720**, cost÷gross **0.7621**, Sharpe +0.3424, Sortino +0.5401 — the first profitable
deployed-cost gate run in this arc.

It is **one window of six**, its holdout contains all the smaller ones, and it still fails six
gate checks: `minimum_trades_per_week` (**2.814** against 7.0 — a 2.5x miss), `positive_day_ratio`
0.373, `median_daily_pnl` 0.0, `sortino_ratio` 0.540, `sharpe_ratio` 0.342, `cost_to_gross_pnl_ratio`
0.762 against 0.5 — plus the seven continuity checks that make the route gate-ineligible anyway.
The immediately adjacent deeper window, @1800, is **net −0.24159** with cost÷gross 1.4353.

Gross remains positive at all six windows (+0.3391 / +0.6000 / +0.7820 / +0.7300 / **+0.9550** /
+0.5550), which is the durable statement.

## What is proven, and what is not

Proven:

- The weekday tables above, read from saved `daily_results` arrays.
- The registered criterion: discovered set {Mon, Fri} gives mean **+0.002036** on half B.
- Monday's mean flips sign between halves; Friday's does not.
- The holdout list above: all five end 2026-08-28 and are strictly nested.
- `exness XAU` @1500: 255 observed days, 120 trades, 2.814/week, gross +0.95498, cost 0.72778,
  net +0.22720, Sharpe +0.3424, Sortino +0.5401, streak 5, six non-continuity gate failures.
- `exness XAU` @1800: 306 observed days, 140 trades, 2.731/week, gross +0.55498, net −0.24159,
  cost÷gross 1.4353, Sharpe −0.3122.

Not proven, and deliberately not claimed:

- **That a Friday filter or a Wednesday exclusion would help.** Friday's consistency is measured
  on nested samples with no correction for having chosen it from six cells; Wednesday was never
  pre-registered at all and is reported as an observation, not a result.
- **That the four windows corroborate each other.** They are nested by construction, so they are
  closer to one sample measured at four resolutions than to four samples.
- **That @1500's profitability means anything beyond that window.** One of six, nested, failing
  six gate checks including a 2.5x frequency miss, and its deeper neighbour is negative.
- That the weekday buckets are trading days. UTC+7 splits the Friday session into the Fri and
  Sat buckets (audit L3), so "Friday" here is a partial session and "Saturday" is its tail.
- Any correction of Rounds 331-351's window findings. Their **fragility** results stand; only the
  strength of their **replication** language needs discounting, which is what this round records.
- Any promotion. Nothing is actionable, and the one profitable window fails the joint objective.
