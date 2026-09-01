# Round 183 — XAU/binance's 8-month "flat since Dec 2025" stall: root cause identified as the exact mechanism Round 167 fixed; resolution not yet confirmed

## Trigger

User directly observed in the frontend: XAU's last trade shows "Sell ·
26/12/2025" — asked me to verify. This was not something this session's
research had surfaced on its own; investigated on the user's prompt.

## Verification (read-only Redis checkpoint reads, all 4 production routes)

```
                    decisions_since_target_change   last exit ≈
XAU/binance         69,610                          ~2025-12-11 (~241 days)
BTC/binance         206                              ~17 hours ago
Exness/BTC          44                               ~3.7 hours ago
Exness/XAU          46                               ~3.8 hours ago
```

All 4 routes currently show `current_target.position: "flat"`,
`reason: "protective_exit_waiting_for_fresh_insight"`. XAU/binance is not
uniquely broken — all 4 routes are in the *identical* state mechanically;
they differ only in *when* their most recent protective exit happened.
XAU/binance's is far older because (per Round 167-166's own findings) it
has been **impossible**, not just rare, for XAU/binance to re-enter since
that exit — every other route has simply had a more recent exit because
they've continued trading in the meantime.

## Root cause, read directly from `crates/finance-core/src/trading_modes.rs`

`PortfolioConstructionState::construct()` only allows flat→long/short when
`decision.gate_passed` is true, which requires `entry_score.abs() >=
minimum_role_score` (`0.10` — see `trading_api.rs:781`). `entry_score` sums
`interval_weight × strategy_weight × per-strategy score` across
entry-role intervals (5m/15m/30m).

**Before Round 167's fix**, XAU/binance's 5m/15m/30m `interval_weight` was
confirmed **exactly 0.0** (Round 163's direct checkpoint read, and Round
166's Python reproduction matching production exactly). With
`interval_weight = 0` for every entry-role interval, `entry_score` is
**exactly zero regardless of signal strength** — not a low-probability
event, a mathematical impossibility. This is the precise mechanism that
trapped XAU/binance the moment it had its (evidently only) protective exit
around 2025-12-11, and it could never have escaped on its own no matter how
long it waited — 69,610 consecutive failed cycles is exactly what "provably
impossible" looks like, not "very unlucky."

Round 167 (this same session, ~5 hours before this check) deployed
`MultiTimeframePortfolioPolicy::INTERVAL_QUALITY_FLOOR = 0.05` specifically
to stop `interval_weight` from ever normalizing to exactly zero. Verified
post-deploy: XAU/binance's `5m` weight moved from `0.0000` to `0.0479`. This
directly targets the exact mechanism responsible for this stall.

## Status: mechanism identified, resolution NOT yet confirmed

As of this check (~5 hours post-deploy, ~50-60 decision cycles elapsed),
XAU/binance is still flat, `decisions_since_target_change` still counting
up from the same 2025-12-11 exit (not reset — no re-entry has happened
yet). This is not proof the fix is insufficient — 50-60 cycles is a small
sample to expect a strong-enough weighted signal alignment, especially
since `0.0479` is still a fairly small weight relative to the trend-role
intervals (~0.15-0.43) that dominate `interval_weight`'s total mass. It is
also not proof the fix is sufficient. **Genuinely unresolved, needs
monitoring.**

## Round 184 update — exact current `entry_score` computed from live evidence, quantifies how close/far the gate actually is

Pulled the live `portfolio_evidence.evidence` block (real per-interval,
per-strategy `side`/`strength` at this exact moment) and computed
`entry_score` by hand using the real formula (`interval_weight ×
strategy_weight × signed_strength`, summed across entry-role intervals):

```
15m  candle_momentum      short  strength=1.00  contrib=-0.01796
15m  rsi_mean_reversion   long   strength=1.00  contrib=+0.02991
30m  candle_momentum      long   strength=1.00  contrib=+0.01796
30m  rsi_mean_reversion   short  strength=1.00  contrib=-0.02991
5m   candle_momentum      long   strength=1.00  contrib=+0.01796
5m   rsi_mean_reversion   short  strength=1.00  contrib=-0.02991

TOTAL entry_score = -0.01195   (needs |entry_score| >= 0.10 to pass)
```

**`candle_momentum` and `rsi_mean_reversion` are on opposite sides at
every single entry interval right now** — a real, structural pattern (RSI
mean-reversion and raw momentum are naturally anti-correlated in choppy
conditions), not a fluke of this one snapshot. Their weights (0.375 vs
0.625) mean they partially cancel rather than fully cancel, but the
residual is tiny relative to the 0.10 threshold.

**Best-case ceiling at the current `0.05` floor:** if both strategies
agreed (same side, full strength) at all 3 entry intervals simultaneously,
`entry_score = 3 × 0.0479 × (0.375+0.625) × 1.0 ≈ 0.144` — **this clears
0.10**, so the fix is not mathematically insufficient, but it requires
genuine directional agreement between the two strategies across
5m/15m/30m at the same time, which the current snapshot shows is not the
strategies' typical relationship. This explains why resolution is likely
to take real time (waiting for a genuine alignment event) rather than
happening on the very next candle, but confirms the fix is not a dead end
— just needs the right market moment. If XAU/binance is still stuck after
several days with no sign of even a partial (2-of-3-interval) agreement
ever occurring, that would be the concrete trigger to reconsider the floor
value.

## Round 191-192 correction — Round 184's `entry_score` calculation was only
## half the gate; `trend_score` is the actual current blocker

Round 191 re-pulled live `portfolio_evidence` for XAU/binance and got
`entry_score = +0.1436` — clearing the `0.10` gate, with `candle_momentum`
and `rsi_mean_reversion` both long across all 3 entry intervals (5m/15m/30m),
persisting across two consecutive checks (Round 191 and Round 192, ~10+
minutes apart, event timestamps advancing normally). This looked like the
long-awaited alignment moment Round 184 said was needed. **It was not
enough**: XAU/binance was still flat after the wait.

Re-reading `MultiTimeframeEvidenceBook::decide()` (`trading_modes.rs:805-840`)
shows Round 184's analysis was incomplete — it only ever computed
`entry_score`, but the real gate requires **both**:
1. `entry_score.abs() >= minimum_role_score` (0.10) — clears, per above.
2. `trend_score.abs() >= minimum_role_score` (0.10) — **does not clear**.
3. `entry_score` and `trend_score` must agree in sign (no `entry_trend_conflict`).

Hand-computed `trend_score` from the same live evidence snapshot the same
way (`interval_weight × strategy_weight × side.score(strength)`, summed
across the 5 trend-role intervals: 1h/2h/4h/12h/1d):

```
12h  candle_momentum   long   contrib=+0.07111
12h  rsi_mean_reversion hold  contrib=+0.00000
1d   candle_momentum   long   contrib=+0.16164
1d   rsi_mean_reversion hold  contrib=+0.00000
1h   candle_momentum   long   contrib=+0.01796
1h   rsi_mean_reversion short contrib=-0.02991
2h   candle_momentum   long   contrib=+0.01796
2h   rsi_mean_reversion short contrib=-0.02991
4h   candle_momentum   short  contrib=-0.05263
4h   rsi_mean_reversion short contrib=-0.08765

TOTAL trend_score = +0.0686   (needs >= 0.10)
```

The longer-term picture (12h/1d, which together carry ~62% of trend-role
interval weight) is strongly long, but 4h is strongly short (both
strategies agree short there) and 1h/2h roughly cancel — net trend_score
lands at 0.0686, close to but short of the 0.10 gate. **This is the real,
current, precise blocker**, not a lack of entry-role agreement (which is
already present and has been for at least 10+ minutes). The swing strategy
deployed in Round 189 (`mtf_stochastic_4h_1d_sma50`) is BTC-only, not
registered for XAU, so it has no bearing on this route's trend_score.

This corrects the honest state of the investigation: XAU/binance is
genuinely closer to escaping the stall than Round 183's original ceiling
estimate suggested (that estimate only modeled entry_score, never checked
whether trend_score could independently clear its own identical gate) —
but "close" here still means the trend-role signal needs its own alignment
moment (either 4h's short view weakening/flipping, or 12h/1d's long view
strengthening further), independent of and in addition to the entry-role
alignment already observed.

## Action items

1. **Re-check XAU/binance's `decisions_since_target_change` in 1-2 days.**
   If it has reset to a small number (meaning a real re-entry happened),
   the fix worked as intended — first real, observable evidence beyond the
   interval_weights match already confirmed. If it's still climbing from
   the same baseline, `INTERVAL_QUALITY_FLOOR = 0.05` is too small to
   practically matter and needs raising (with the same real-production-data
   simulation discipline as Round 165-167, not a guess).
2. **Also check the other 3 routes** — even though they show more recent
   exits (not currently as visibly "stuck"), verify they successfully
   re-enter after their own next protective exit too, not just XAU/binance.
3. This changes the honest answer to "is there improvement" from Round
   167-180's session: **the floor fix's real production effect on Target 2
   is not yet observed, only inferred from the interval_weights match.**
   Say so plainly if asked again before confirmed.
