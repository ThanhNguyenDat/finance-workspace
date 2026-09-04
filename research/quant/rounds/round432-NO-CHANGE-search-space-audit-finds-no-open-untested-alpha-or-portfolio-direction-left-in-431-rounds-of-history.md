# Round 432 — NO-CHANGE: search-space audit finds no open, untested Alpha or Portfolio direction left after 431 rounds

Classification: **NO-CHANGE**. Zero containers, zero SSH tunnel, zero
backtest compute. This round's task per the prompt is narrowly: (1) find a
new Alpha Layer candidate, or (2) optimize the Portfolio Layer via real
backtest with train/validation/OOS or walk-forward evidence. Before spending
the container/compute budget on either, this round did the prerequisite
work the prompt also requires: read `research/quant/index.md` end to end
(sections 0, 1, 2, 3, 4, 6, and the round-by-round entries from the most
recent — round431 — back through round330) to identify which Alpha/Portfolio
threads are still genuinely open versus already closed, so as not to
re-spend backtest budget re-deriving a conclusion the corpus already has.
None of the status-check items this prompt explicitly excludes (OpenSpec/OPS
lifecycle, CI/deploy, ADRs, externally-blocked threads) were touched.

## What was audited

1. **The most recently active thread — the round365/366 "corner"
   (protective band 0.02/0.04 + minimum-hold 288) — is fully closed as of
   round431.** It was tested against deployed config (band 0.01/0.02, hold
   36) via `--daily-profit-gate` on all three routes that could run it:
   - `binance BTC` (round427): corner loses *before costs*
     (`gross_pnl_before_costs` −1.86562), 3.64 trades/week, fails
     `minimum_trades_per_week`. REJECTED.
   - `bybit XAUT` (round428→431, four disjoint holdout windows): corner beat
     deployed on net PnL/Sharpe/Sortino in windows A-C but reversed in window
     D — 3-of-4, not 3-of-3 as round430 had claimed before round431's
     correction — and never approached Target 3 in any window (1.066 / 1.61
     / 2.815 / 2.878 trades/week vs. the 7.0/week bar). History depth for
     this route/corner pair is exhausted (candle_count shrank
     143998→118185→94549→75640 across the four `--as-of` shifts; a fifth
     window would be shorter still). REJECTED, thread explicitly closed by
     round431 ("Đóng nhánh disjoint-window cho corner này trên `bybit
     XAUT`... Không chạy thêm cửa sổ nào cho corner này trên route này").
   - `exness XAU` (where the corner originated, round365/366): never
     gate-eligible at any window depth (round335-336, `holdout_interval_continuity`
     structurally fails at both 500 and 900 days) — no gate verdict possible
     on this route for this or any corner.

   No route has produced a corner reading that survives an independent
   robustness check. This closes the last thread that had been under active
   test across rounds 365-366 and 426-431.

2. **Rule 1 (Portfolio-construction sizing/band/hold) is closed as a
   space**, per the index's own "Thứ tự ưu tiên" section (index.md line
   ~10195-10266): hold (round80, deployed), stop/take width (round83,
   deployed), hold×stop/take interaction (round87, sub-additive, current
   production is the best of 4 combinations), sizing mode (`risk_fraction`
   vs `equity_fraction` vs `fixed_notional`, round89-90 and re-confirmed
   round151-152 — only the deployed `fixed-pct` mode avoids catastrophic
   geometric-compounding loss). The band-width local-optimum question was
   answered directly by round330-332: at `--days 900` on `exness XAU`, the
   **deployed band is the interior optimum** among five tested configs —
   "trên đòn bẩy này, ở cửa sổ này, cấu hình production KHÔNG BỊ cấu hình
   sai" (round332). The one item the index still marks formally open —
   `--portfolio-atr-periods` — is inapplicable to current production
   (`protective-kind` is `fractional`, not `atr`), and the ATR arm already
   appears as a comparison row in round329/330's sweep tables with
   dramatically worse results than fractional (Sharpe −18.9 to −23.2 vs.
   fractional's −0.1 to −0.9), so sweeping its period parameter without
   first re-opening the fractional-vs-atr `protective-kind` question (itself
   already closed, unfavorably) would not be a defensible use of this
   round's budget.

3. **Rule 2/3 (Alpha signal search) is closed as a space at 5m** per
   section 3 of the index: ~40 distinct mechanisms tested (Donchian,
   Keltner, Heikin-Ashi, Ichimoku, Parabolic SAR, CCI, OBV, Elder Ray,
   Vortex, Awesome Oscillator, Larry Connors RSI(2), session-time filters,
   funding-rate contrarian, day-of-week, realized-vol regime filter,
   engulfing/three-soldiers candle patterns, Fibonacci Golden Zone,
   order-flow imbalance, swing 4h/1d sweeps, MTF ensembles) — 0 mechanisms
   clear PF>1 consistently cross-split, cross-broker, and cross-window. The
   ensemble/regime-switching direction (section 2) was independently closed
   twice: once by hand-backtest vs. the real `PortfolioDecisionPolicy`
   engine (round54, Sharpe 1.8 hand-computed vs. −6.72 through the real
   engine), and again for production's actual live MTF strategies
   (round67/394-396, PF collapse from 19.6-26.6 to 0.58-0.98 once a
   lookahead bug was fixed).

4. **Direction/guard/cost-structure sub-threads are closed**: long/short
   asymmetry is drift, not edge, on all three routes tested (round385-386);
   construction guard + risk layer does not generalize (round371-372,
   `binance XAU` guard makes results 31.9% worse); day-of-week seasonality
   fails a pre-registered permutation test (p=0.60, round354-355); pooled
   gross edge across the fleet's 9 disjoint holdouts is not distinguishable
   from zero (95% CI [−0.170, +0.551], contains 0, round398-400), and
   round400 itself already concluded that adding 2-3 more disjoint points on
   `exness BTC`/`bybit BTC` "sẽ không đổi câu trả lời" (would not change the
   answer) and is only worth doing "như xác nhận, không phải như truy vấn"
   (as confirmation, not as a live question) — i.e. the corpus's own prior
   analysis already flags further pooled-significance runs as low-value.

5. **The three threads still explicitly open in the index (release
   decision, Target 2 metric definition, forward-time-for-more-holdout) are
   all blocked by factors this prompt excludes from this round's scope**
   (product decision, calendar time, infra access) — not re-audited here
   beyond confirming they are the same threads previously identified, per
   the prompt's explicit instruction not to fill a round with checking
   externally-blocked status.

## Conclusion

No new Alpha candidate and no untested, applicable Portfolio-construction
lever was found. Every currently-known, currently-applicable direction in
the corpus has either produced a defensible REJECTED/closed verdict or is
blocked by a factor outside this round's scope. Spending this round's
Docker/backtest budget on a re-run of any closed direction, or on a
parameter variant of a mechanism already shown structurally unfavorable
(ATR periods under a worse `protective-kind`), would not meet the
prompt's bar against manufacturing engineering work or re-testing
closed directions. No promotion, no implementation, no production change.

## Named next step

None from the backtest side this round. The next legitimate new-material
event on either open front would be: (a) a product/human decision on what
Target 2 ("Make Decision rate") should actually measure, since round401
established the tool has no metric for it at all under any name; or (b)
enough forward calendar time to extend any route's disjoint-holdout series
past what round400 already assessed as low-value-incremental. Neither is
actionable from a research round. If a genuinely new Alpha mechanism idea
(not a parameter variant of anything in index.md section 3) or a genuinely
new Portfolio-construction lever (not hold/stop-take/band/sizing-mode, all
closed) is identified in a future round, that is the bar for reopening
compute-spending research here.
