# Round 235 — Round 234's continuity flag resolved: every unmarked gap starts at the daily session boundary. It is missing metadata, not missing data

Classification: **DATA-ISSUE**. No containers — one read-only query and local
classification of 118,363 bars.

## The flag being resolved

Round 234's XAU Portfolio gate listed 13 failed checks, seven of them
`input_continuity_failed` on every non-5m interval (15m alone: 1,266 unverified
gaps across 55,917 candles), while `holdout_interval_continuity` **passed** and
`interval_continuity_violations` was **0**. Two signals disagreeing, deliberately
left uninterpreted for this pass.

Full exness XAU 15m series, 118,363 bars, 2021-08-26 to 2026-08-28:

| | count |
|---|---|
| discontinuities found | **1,297** |
| total missing 15m slots | 57,209 |
| carrying a `gap_before_reason` | **10** |
| unmarked | **1,287** |
| distinct reasons present | `broker_session_or_no_tick` only |

## Every unmarked gap starts at the daily session boundary

Hour (UTC) at which the 992 small unmarked gaps (<= 2h) begin:

| hour | count |
|---|---|
| **20:00** | **655** |
| **21:00** | **332** |
| 08:00 / 11:00 / 13:00 / 23:00 | 1 / 1 / 1 / 2 |

**987 of 992 — 99.5% — begin at 20:00 or 21:00 UTC.** That is the exness daily
close, not scattered data loss. Median size 4 slots (one hour), one occurrence
per trading day (Thu 258, Fri 255, Mon 255, Tue 260, Wed 258 across ~260 weeks).

The 253 large gaps have the same origin extended over the weekend: **244 of 253
start Friday 20:00 or 21:00 UTC**, sizes 150-292 slots.

So of 1,287 unmarked discontinuities, **1,283 are the daily or weekend session
closure of a weekday CFD** and only **4** fall outside that pattern.

## The verdict

**The data is complete. The markers are missing.**

- `interval_continuity_violations = 0` is correct — there is no data loss.
- `input_continuity_failed:X` fires on `unverified_gap_count > 0` — i.e. on
  discontinuities lacking a marker, whether or not they are real closures.
- The two checks disagree because they ask different questions: *is data
  missing?* versus *is every discontinuity explained by a marker?*

Ten markers exist for 1,297 real session closures — **0.8% coverage**.

## Why this matters, and how much

It does **not** invalidate any backtest in this session or earlier. The kline
series is complete for the instrument's real trading calendar, which is what the
strategies consume.

It does make the Portfolio gate report misleading to read: **13 failed checks of
which 7 are metadata noise and 6 are real** (`minimum_trades_per_week`,
`positive_day_ratio`, `median_daily_pnl`, `sortino_ratio`, `sharpe_ratio`,
`cost_to_gross_pnl_ratio`). Anyone reading that report without this analysis would
either over-count the failures or, worse, start distrusting the data underneath
them — which is the more expensive error, since Round 234's six real failures are
the substantive result.

The fix is marker backfill for session closures, which the repository already has
tooling for (`kline-gap-marker-backfill`, a guarded mutation per
`docs/runbooks/kline-maintenance-tools.md`). Not attempted here: it is a guarded
production mutation, and this round is research.

## What is proven, and what is not

Proven:

- exness XAU 15m has 1,297 discontinuities over five years; 10 carry a marker.
- 987 of 992 small unmarked gaps begin at 20:00 or 21:00 UTC; 244 of 253 large
  ones begin Friday 20:00 or 21:00 UTC.
- 1,283 of 1,287 unmarked discontinuities match the daily or weekend session
  closure pattern; 4 do not.
- Marker coverage is 10/1,297 = 0.8%.

Not proven, and deliberately not claimed:

- What the four anomalous gaps (starting 08:00, 11:00, 13:00, 23:00 UTC) are.
  Four out of 1,287 is small enough not to affect the conclusion and large enough
  to be worth naming rather than rounding away.
- That the other six intervals behave identically. Only 15m was classified; the
  other flagged intervals show the same order-of-magnitude unverified counts and
  the same underlying series, so the same explanation is likely but untested.
- That backfilling markers changes any measured result. It would change the
  report, not the data.
