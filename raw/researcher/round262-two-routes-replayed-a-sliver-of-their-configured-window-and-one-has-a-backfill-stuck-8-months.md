# SEVERITY DE-ESCALATED (Round 264): P2 -> P3

This file filed the finding as **P2, possibly P1 "if it affects live decisions,
which is not established"**. Round 264 established that it **does not**: all six
routes — the two here included — construct Portfolio decisions at an identical
cadence (`portfolio_decisions_total` = 571 on five routes, 342 on `exness XAU` for
the weekend closure) with `evidence_intervals_complete == required == 8` everywhere.

The two routes are **not dormant in live operation**. Their 8 and 3 *lifetime*
trade counts are a **seed artifact**; live, they close at a rate consistent with the
long-run 7.60 vs 9.14/week of Round 261.

Correct severity is **P3**. This file's measurements all stand — the seed spans, the
stalled backfill cluster, and the coinciding 2025-12-26 boundary. What changes is
that no live impact is demonstrated. It is **de-escalated, not closed**: the seed
feeds the reweighting formula, so a propagation path to live behaviour exists and is
merely unmeasured. See
`round264-all-six-routes-decide-at-identical-cadence-the-dormancy-is-a-seed-artifact.md`.

---

# Round 262 — The "dormant" routes are not dormant: they replayed 14 days and 2 days of a configured 365-day window, and one has a history backfill stuck since 2025-12-25

Classification: **DATA-ISSUE**. Read-only production evidence. **Zero containers.**
Investigation only — nothing applied, per the Claude role note in
`.agents/rules/coding-and-verification.md`.

## The question Round 261 handed over

Round 261 replaced Round 260's ill-posed "XAU/BTC gap" with a better one: **why do
`binance XAU/USDT` (8 lifetime trades) and `bybit XAUT/USDT` (3) barely trade,
while `exness XAU` on the same asset class has 395?**

## It is not the data, and it is not the decision rate

Kline coverage in Timescale, 5m:

| route | 5m bars | first bar | last bar |
|---|---|---|---|
| exness.cfd.XAU.USD | 354 814 | 2021-08-26 | 2026-08-28 |
| binance.perpetual_future.XAU.USDT | **75 232** | **2025-12-11** | 2026-08-29 |
| bybit.spot.XAUT.USDT | **145 481** | **2025-04-11** | 2026-08-29 |

Both "dormant" routes have 8 and 16 months of continuous data. Both are currently
alive: `last_portfolio_primary_close_time` on each is **2026-08-29T13:29:59Z**,
the current bar.

## The cause: the replay covered a sliver of its configured window

Configured replay window, read narrowly from the running containers
(`env | grep -E '^HISTORICAL_[A-Z_]*REPLAY_DAYS='`, single variable, no dump):

```
HISTORICAL_DEMO_REPLAY_DAYS=365      (both workers checked)
```

All three replays completed within 17 hours of each other. What they produced:

| route | replay completed | data available in the 365d window | **seeded trade span** | trades |
|---|---|---|---|---|
| exness XAU | 2026-08-22T13:26Z | 365 d | **361 d** (2025-08-25 → 2026-08-21) | 392 |
| binance XAU | 2026-08-22T13:27Z | ~254 d (data starts 2025-12-11) | **14 d** (2025-12-12 → 2025-12-26) | 7 |
| bybit XAUT | 2026-08-23T06:11Z | 365 d | **2 d** (2026-08-19 → 2026-08-21) | 1 |

**`exness XAU` behaves exactly as configured — 361 days against a 365-day setting.
The other two do not.** `binance XAU` left roughly 240 days of available in-window
data unreplayed; `bybit XAUT` left roughly 363 days unreplayed and seeded only the
final two days of its own window.

So the low lifetime trade counts are **not a low decision rate**. They are the
arithmetic consequence of a seed that covered almost none of the period it was
configured to cover.

## The corroborating signal on `binance XAU`

`runtime_state.pending_history_backfill`:

| route | pending 5m bars | timestamp range | age |
|---|---|---|---|
| binance XAU | **508** | **2025-12-23T11:05Z → 2025-12-25T05:20Z** | **~8 months stale** |
| exness XAU | 1000 | 2026-08-07 → 2026-08-12 | ~17 days |
| bybit XAUT | *(key absent)* | — | — |

`.agents/skills/quant-research-loop/SKILL.md` states this field "should be rotating
near-present timestamps; a stale, non-advancing cluster is a real bug, not normal."

**`binance XAU`'s cluster is stuck at 2025-12-23…25, and its seeded trade span ends
2025-12-26.** Those two boundaries coincide to within a day, and 2025-12-26 is
exactly the date Round 206 recorded that route as having frozen. Three independent
observations landing on the same date is the strongest part of this round.

`bybit XAUT` shows a different shape — no pending cluster at all, and a seed
confined to the last two days of its window — so it is not the same failure, only
the same class.

## One difference that is expected, recorded so it is not mistaken for a cause

`historical_replay_completed_scopes` is **27** on `exness XAU` and **19** on both
others. That follows from strategy count: `exness XAU` carries 3 strategies
(8 intervals × 3 + 3 paper rules = 27), the other two carry 2 (8 × 2 + 3 = 19).
`strategy_weights` confirms it. This is a configuration difference, not a defect,
and it does not explain the seed spans.

## Finding for Codex — not applied, investigation only

**P2 (raise to P1 if it affects live decisions, which is not established):** the
historical replay seeds radically different spans across routes under an identical
`HISTORICAL_DEMO_REPLAY_DAYS=365`, and one route carries a `pending_history_backfill`
cluster stalled for eight months at the exact boundary where its ledger stopped.

- **Observed:** `binance XAU` 14-day seed against ~254 days available; `bybit XAUT`
  2-day seed against 365 available; `binance XAU` backfill queue frozen at
  2025-12-23…25.
- **Expected:** each route's replay seeds the full configured window intersected
  with available data, and the backfill queue advances toward the present.
- **Evidence:** the tables above, all read-only from
  `{finance-live-action:checkpoints}:worker_checkpoint:*` and `public.klines`.
- **Required verification after any fix:** seeded trade span per route matches
  `min(365 d, available history)`; `pending_history_backfill` timestamps advance
  toward the present on every route; lifetime `trade_count` on the two routes rises
  to a rate comparable with `exness XAU`'s 7.60/week.

**Cause not established.** I did not determine from the code why the replay stops
early — that is the Codex-side investigation, and this round deliberately stops at
inspection.

## What is proven, and what is not

Proven:

- Kline coverage, replay completion timestamps, seeded trade spans, pending
  backfill ranges, and scope counts as tabulated.
- `HISTORICAL_DEMO_REPLAY_DAYS=365` on both workers read narrowly.
- `exness XAU` seeds 361 days against that setting; the other two seed 14 and 2.
- All three routes' `last_portfolio_primary_close_time` is current.

Not proven, and deliberately not claimed:

- **A causal link between the stalled backfill and the short seed.** The dates
  coincide on `binance XAU`; `bybit XAUT` has a short seed with *no* stalled
  cluster, so the backfill stall cannot be the general mechanism.
- That this affects live trading rather than only the seed. Both routes are
  currently closing trades, and `binance XAU` produced one on 2026-08-28.
- That the two routes would reach `exness XAU`'s 7.60/week if seeded fully. That is
  the hypothesis a fix would test, not something measured here.
- Any code-level cause. Not investigated; deliberately left to Codex.
- Anything about PnL on these routes. Their samples (8 and 3 lifetime trades)
  cannot support a PnL statement and none is made.
