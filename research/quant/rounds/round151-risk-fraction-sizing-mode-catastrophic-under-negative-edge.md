# Round 151 — `risk_fraction`/`equity_fraction` Portfolio sizing modes: dangerous under the current negative-edge Alpha layer

> ⚠️ **CORRECTION (Round 163, 2026-08-25): this finding is NOT new.**
> `round89-risk-fraction-effective-leverage-catastrophic-loss.md` and
> `round90-equity-compounding-sizing-geometric-decay-confirmed.md`
> (2026-08-22) already found and closed this exact question, with the same
> root-cause mechanism (`notional = equity × risk_fraction / stop`, hidden
> effective leverage) and cross-broker/cross-instrument coverage this file
> lacks. This round's numbers are a legitimate independent reconfirmation
> (different tool — `--daily-profit-gate`'s holdout-only scope vs Round 89's
> full-5-year `one_target` scope — and fresher data), and this round did
> catch two genuinely new things (the vestigial-env-var methodology bug
> below, and a tooling gotcha — see `SUMMARY-priority-backlog.md`'s Rule 1
> section), but the headline conclusion should be attributed to Round 89/90,
> not this round. Read `SUMMARY-priority-backlog.md`'s Rule 1 section for
> the corrected, consolidated picture before citing this file alone.

## Context

Round 83 (2026-08-21) flagged `--portfolio-sizing-mode`/`--portfolio-sizing-value`
as an untested Rule-1 (Portfolio-construction) lever — the internal priority
ranking decided that round rates Rule 1 tuning far above Rule 2/3 new-signal
search (2/3 successful levers vs 0/15+ new mechanisms; see
`SUMMARY-priority-backlog.md` §"Thứ tự ưu tiên"). With Awesome Oscillator
(Round 150) now the 8th consecutive Alpha-search failure this session, this
round tested that flagged lever instead of another oscillator.

## Method

`finance-research --daily-profit-gate` — this replays the REAL currently-
deployed `production_candidates()` decision stream (not a synthetic
candidate) on BTC/binance holdout, varying only the Portfolio-construction
sizing config via `--portfolio-sizing-mode`/`--portfolio-sizing-value`. This
is the trusted `one_target`-equivalent path (confirmed by reading
`main.rs`: `selected_portfolio_rule` built from these exact CLI flags feeds
directly into `evaluate_real_portfolio_with_funding_and_continuity`, same
construction used by Round 80/83's validated hold/stop-take levers).

**Baseline — CORRECTED in Round 152 (2026-08-25):** the original version of
this section trusted a `docker exec ... env | grep PORTFOLIO_` read showing
`PORTFOLIO_STOP_VALUE=0.005`/`TAKE_VALUE=0.010` and used those as the CLI's
implicit defaults for the baseline run. **That env var is vestigial and not
what production actually consumes.** Reading
`crates/finance-api/src/deployment_rules.rs:58-59` directly shows
`PORTFOLIO_STOP_VALUE`/`PORTFOLIO_TAKE_VALUE` are compiled-in Rust
constants (`0.01`/`0.02`, exactly Round 83's deployed change, commit
`31ed149`) — `configured_portfolio_rules()`, the function
`production_candidates()`'s execution rules actually come from, never reads
any environment variable for these; a workspace-wide grep confirms every
other `"PORTFOLIO_STOP_VALUE"`/`"PORTFOLIO_TAKE_VALUE"` string in the
codebase is only an error-message field label inside `validate_fraction(...)`
calls, never an `env::var(...)` read. Round 83's 0.01/0.02 change is real
and live; the env var was a red herring (likely a stale Compose default from
before that commit, never wired to anything). Corrected sizing sweep runs
using `--portfolio-stop-value 0.01 --portfolio-take-value 0.02` explicitly
(matching real production) were queued this round; results below are
updated once they land — see "Correction status" at the end of this file if
still pending when read.

Docker, 2 parallel containers max, each `--cpus=1 --memory=2g
--memory-swap=3g` (fits the "like production, max 2 containers" rule 9
budget), BTC/binance, 5-year window, 5m.

## Results

| sizing mode | value | net PnL | max total drawdown | Sharpe | Sortino |
|---|---|---|---|---|---|
| `fixed_notional` (production baseline) | 5.0 | -$13.29 | 0.13% | -6.63 | -6.60 |
| `risk_fraction` | 0.02 (2%) | **-$9,999.89** | **99.99%** | -6.77 | -6.80 |
| `risk_fraction` | 0.002 (0.2%, 10x smaller) | **-$6,583.75** | **66.2%** | -6.66 | -6.63 |

(`equity_fraction` 0.02 failed all 4 attempts with `transport error` this
round. Initially looked mode-specific, but a same-window 30-day sanity
check showed `risk_fraction` also failing identically at that point in
time — confirms this is the `KlineService/Stream` gate's known ongoing
flakiness (see `docs/reviews/kline-stream-gate-capacity-saga.md`), not an
`equity_fraction` code bug. Not obtained this round; the two `risk_fraction`
data points already give an unambiguous, reproducible conclusion, and
`equity_fraction` is structurally the same equity-scaling risk without the
stop-distance lever multiplier, so the same caution applies by construction
until actually measured.)

## Why this happens

`risk_fraction` sizes each position as `risk_fraction / stop_distance ×
current_equity` notional — i.e. it *leverages up* relative to how tight the
stop is. At `stop=0.005` and `risk_fraction=0.02`, that's a ~4x
equity-to-notional multiplier per trade; at `risk_fraction=0.002` it's still
~0.4x, non-trivial on top of the underlying 10x instrument leverage. The
production Alpha signals (`candle_momentum`/`rsi_mean_reversion`, both
already known PF<1 — see closed-directions table) have **negative expected
value**. Any sizing mode that scales *up* with account equity under a
negative-EV process accelerates ruin (textbook negative-Kelly territory) —
it doesn't matter how conservative the risk fraction looks in isolation,
because `fixed_notional` at $5 flat is already far smaller in relative terms
once compounding is removed from the equation. `fixed_notional` is
accidentally the *safe* choice specifically because it does not compound —
each trade risks the same dollar amount regardless of current equity or
recent losses, so it cannot spiral even when every signal has negative edge.

## Verdict: this lever is CLOSED as an unconditional risk, not "not yet
promising"

This is a genuine Rule-7 finding (a real bug/risk discovered and validated
on real holdout data), and also a genuine warning: **do not deploy
`risk_fraction` or (untested but structurally identical) `equity_fraction`
sizing to production while the Alpha layer's edge remains negative.**
`fixed_notional` should stay as the production sizing mode until either (a)
a genuinely positive-edge Alpha signal is found, or (b) a much more
conservative `risk_fraction` value than tested here is separately proven
non-destructive — untested territory below 0.002 was not explored this
round given the two results already tested are unambiguous.

No production config change was made — this is a backtest-only finding.
Logging to `docs/archive/legacy-handoff-agent.md` as an `evidence`-tagged **closed-as-risk**
item so a future round session doesn't re-attempt this lever without
re-reading this file first.

## Correction status: RESOLVED (Round 155-161, 2026-08-25)

Corrected runs with real production's `--portfolio-stop-value 0.01
--portfolio-take-value 0.02` needed 7 attempts across several rounds before
succeeding — root cause turned out to be **the local SSH tunnel (`ssh -f -N
-L 18086:localhost:8086 my`) silently dying mid-session**, not the MW gate
at all. `ss -tlnp | grep 18086` came back empty when checked directly,
explaining every `transport error` that round — the client had nothing to
connect to. Re-established the tunnel and the very next attempt succeeded
cleanly. **Process lesson for future rounds:** check `ss -tlnp | grep 18086`
before assuming a `transport error` is the `KlineService/Stream` gate
saga — it can just as easily be a dead local tunnel, which is instant to
fix and easy to rule out first.

**Corrected final numbers** (real production config: `fixed_notional`
sizing $5, stop=0.01/take=0.02, 5-year BTC/binance):

| sizing mode | value | net PnL | max total drawdown | trades | trades/wk |
|---|---|---|---|---|---|
| `fixed_notional` (true production baseline) | 5.0 | -$6.16 | 0.066% | 705 | 13.5 |
| `risk_fraction` | 0.02 | **-$9,346.96** | **94.2%** | 705 | 13.5 |

Trade count matches exactly between the two runs (705, 13.5/week) — as
expected, since sizing mode only changes position notional, never which
candles trigger a decision. The wider stop/take (vs the originally-tested
0.005/0.01) reduces baseline loss substantially (-$13.29 → -$6.16, fewer
premature stop-outs, consistent with Round 83's own documented mechanism)
and drops trade frequency from 36.2/week to 13.5/week — both expected
effects of a wider stop, and both consistent with `deployment_rules.rs`
being the real config source. **The core conclusion is unchanged and now
confirmed against the actual live production configuration:**
`risk_fraction` sizing devastates the account (94.2% drawdown) even at
the correct, wider stop distance — the compounding-under-negative-edge
mechanism dominates regardless of the exact stop value tested (0.005 or
0.01). No further correction needed; this file's numbers above the
"Correction status" heading should be read as superseded by this table for
any conclusion depending on exact magnitude, though the qualitative verdict
was correct throughout.
