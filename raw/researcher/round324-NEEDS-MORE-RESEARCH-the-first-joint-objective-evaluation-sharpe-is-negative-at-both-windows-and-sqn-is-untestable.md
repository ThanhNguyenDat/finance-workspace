# Round 324 — NEEDS-MORE-RESEARCH: the **first joint-objective evaluation** in this session. Sharpe is **−2.33 and −0.86**, positive-day ratio **0.40-0.42**, and the gate fails **six checks at both windows** — while independently confirming **positive gross PnL before costs**.

Classification: **NEEDS-MORE-RESEARCH** — the joint objective is now measured on one
route at two windows; five routes remain unmeasured and one required metric is
untestable. Two bounded Docker sweeps (exactly the 2-container budget), **XAU-first**.

## Closing an eleven-round gap

Every round since 313 has ended with the same caveat: *"`one_target` reports PnL only
(Round 84), so this remains a PnL-only result and **not** the joint-objective evaluation
the loop asks for."* The standing brief is explicit — optimise **jointly** on
profitability, decision rate and trade frequency, considering PnL, PF, win rate,
Sharpe/Sortino, drawdown, streak, SQN and decision rate, **never a single metric**.

`--daily-profit-gate` is exactly that instrument: it evaluates the **currently-deployed**
Portfolio decision policy on **holdout only** and emits a versioned scorecard. It
conflicts with `--portfolio-minimum-hold-decisions`, so that flag was omitted.

Run on `exness XAU/USD` at 360 and 900 days, deployed costs.

## The scorecard

| metric | threshold | 360d | | 900d | |
|---|---|---|---|---|---|
| holdout days | ≥ 90 | 60.0 | **FAIL** | 151.0 | PASS |
| trades/week | ≥ 7.0 | 8.51 | PASS | **6.85** | **FAIL** |
| positive-day ratio | ≥ 0.55 | **0.417** | **FAIL** | **0.404** | **FAIL** |
| median daily PnL | ≥ 0.0 | −0.0021 | **FAIL** | 0.0000 | PASS |
| max negative-day streak | ≤ 5 | 4 | PASS | 5 | PASS |
| max total drawdown | ≤ 0.1 | 0.0001 | PASS | 0.0001 | PASS |
| **Sortino** | ≥ 1.0 | **−3.104** | **FAIL** | **−1.179** | **FAIL** |
| **Sharpe** | ≥ 1.0 | **−2.329** | **FAIL** | **−0.861** | **FAIL** |
| **cost ÷ gross PnL** | ≤ 0.5 | **9.886** | **FAIL** | **1.527** | **FAIL** |

Six failures at each window. Holdouts are 2026-06-19→2026-08-28 (86 closed trades) and
2026-03-04→2026-08-28 (174 closed trades).

## What is new here

**1. Risk-adjusted performance is decisively negative, at both windows.** Sharpe −2.33
and −0.86, Sortino −3.10 and −1.18, against a required +1.0. This is the first time in
this session that the deployed policy has been judged on anything other than raw PnL,
and the answer is unambiguous. Its **sign is stable across the two windows**, unlike so
much else in this arc.

**2. The gate independently confirms positive gross edge.** `gross_pnl_before_costs` is
**+0.0535** at 360 days and **+0.7812** at 900 — positive at both, computed on the
holdout only, through a **different code path and a different aggregation** (daily
returns) from the `one_target` cost ablation of Rounds 313-321. Two independent
instruments now agree that `exness XAU`'s raw edge is positive and its net result is not.

The gate's own `cost ÷ gross` figures invert to **10.1%** and **65.5%**. Those are
**not** comparable to Round 322's per-trade 24.3-43.7% — different aggregation and a
different span — and I am not reconciling them.

**3. Drawdown passes trivially and tells us nothing.** Maximum total drawdown is
**0.0001** (0.01%) because `fixed_notional` sizing deploys ~5 units against 10,000
starting equity. The drawdown and streak checks are structurally easy here; only the
ratio, day-quality and cost checks discriminate.

**4. Target 3 flips once more.** 8.51 trades/week on the 360-day holdout, **6.85** on
the 900-day holdout — pass and fail. Entirely consistent with Rounds 304-321.

**5. SQN cannot be computed with this tool.** `unavailable_metrics` names three:
`system_quality_number` (*"requires a per-trade R-multiple distribution"*),
`information_ratio` (needs a benchmark series) and `maximum_consecutive_losing_trades`
(*"requires retained ordered per-trade net PnL outcomes"*). The standing brief lists SQN;
it is **not measurable today**. Recorded as a tooling limitation — **investigation only,
not applied**.

## A data-quality observation, not a finding

The gate reports `input_continuity_failed` on **7 of 8 intervals**, with large
*unverified* gap counts on the higher timeframes (`15m`: 245 gaps / 10,767 candles;
`30m`: 243 / 5,381; `1h`: 243 / 2,688) while **`5m` has `unverified_gap_count: 0`** and
only verified session gaps.

The most likely reading is Round 235's: these are **missing markers, not missing data** —
a weekend closure that is labelled as a verified session gap at 5m may not be labelled
on an aggregated interval. Note `interval_continuity_violations` is **0** in the metrics
block, which is consistent with that. I am recording the observation and **not** treating
it as a defect; distinguishing the two would need the gap-metadata producer inspected,
which was not done.

## What is proven, and what is not

Proven:

- `exness XAU` daily-profit-gate, deployed costs, both windows: `passed=false`, six
  non-continuity checks failing at each.
- Metrics as tabulated, including Sharpe −2.3289 / −0.8614, Sortino −3.1043 / −1.1786,
  positive-day ratio 0.4167 / 0.4040, trades/week 8.5055 / 6.8518.
- `gross_pnl_before_costs` **+0.053459** and **+0.781175**; `total_cost_drag` 0.528501
  and 1.192949; `net_realized_pnl` −0.475042 and −0.411774.
- `unavailable_metrics` lists `system_quality_number`, `information_ratio` and
  `maximum_consecutive_losing_trades` with the stated reasons.
- `5m` shows `unverified_gap_count: 0`; the seven higher intervals do not.

Not proven, and deliberately not claimed:

- **Anything about the other five routes.** One route. The gate was not run on
  `binance BTC`, `exness BTC`, `bybit BTC`, `bybit XAUT` or `binance XAU`.
- That the gate's `cost ÷ gross` and Round 322's `edge ÷ cost` measure the same thing.
  They do not, and no reconciliation is offered.
- That the higher-interval continuity failures indicate missing data. Round 235's
  "missing markers" reading fits and `interval_continuity_violations` is 0, but the
  gap-metadata producer was not inspected.
- That these metrics are window-independent. Sharpe's **sign** is stable across the two
  windows; its **magnitude** differs 2.7x, and Rounds 300-322 apply here as everywhere.
- Any candidate improvement. This round measures the deployed policy; it proposes
  nothing, and no promotion is warranted — the gate's own verdict is a fail, which is
  evidence of a problem, not a validated change.
