# Round 206 — Mark-price gap liquidations overshoot the isolated-margin threshold by up to 17.1%, and they landed on the one strategy the program has validated

Read-only production evidence only. No backtest container was run this round;
the finding came out of the four route checkpoints in Redis and the code paths
they implicate. Codex is available (`codex_available=true`), so nothing here
was implemented.

## Production identity at measurement time

`2026-08-28T15:35Z` (22:35 UTC+7). All six `live-action-*` containers healthy on
`finance-live-action_sha-7a15b76ab5b8…` (`7a15b76`), up 25 hours; `finance-mw-1`
healthy.

`finance_live_action_portfolio_decisions_total` reads `300` on five routes and
`277` on exness XAU. `300` is not a plateau: the metric is documented as
"Realtime Portfolio decisions constructed **since process start**", and 25 h ×
12 five-minute cycles = 300 exactly. Exness XAU's 277 is consistent with CFD
session breaks. Nothing is stuck.

## Part 1 — Two open handoff items, verified independently

**BTC Portfolio zero-decision (`[trading][high][2026-08-25]`) — recovered.**
`paper-fixed-pct` (the rule actually selected live) now shows **478 trades /
−3.3561** on binance BTC and **484 trades / −5.0230** on exness BTC. Both routes
are constructing and executing decisions. Verified from the checkpoints, not
from Codex's report.

**XAU/binance freeze (`[trading][high][2026-08-25]`, Round 203/205) — still
frozen, exactly as designed.** `paper-fixed-pct` is **7 trades / −0.0478**,
unchanged from Round 203's measurement. `strategy_weights` are
`rsi_mean_reversion 0.6267 / candle_momentum 0.3733`, matching Round 203's
diagnosed 62.2% / 37.8% split to within rounding. `interval_weights` show
`5m = 0.0479`, i.e. Round 167's `INTERVAL_QUALITY_FLOOR = 0.05` still holding
the floor. No re-entry, and per Round 203 the unfrozen behavior backtests to
−1.54, so this remains a choice rather than an oversight.

## Part 2 — The real finding: liquidation is only evaluated on the live mark feed

`SimulatedLedger` liquidates a position in exactly one place —
`on_mark_price_with_closed_trade` (`crates/finance-core/src/trading_modes.rs:1835-1872`),
whose own doc comment states the contract:

> Applies an authoritative venue mark. A candle close, last trade, or an
> observation older than the position is deliberately rejected as a
> liquidation input by the caller contract.

So during historical replay — which has no authoritative mark-price stream —
an open position is **never liquidation-checked**. The first mark that arrives
after the gap closes it, and `close_position`
(`trading_modes.rs:2168-2205`) books PnL at that observed exit price with **no
cap at the posted margin**. The threshold it should have closed at is
`isolated_liquidation_price` (`trading_modes.rs:2288-2321`), for a short
`entry × (1 + 1/L) / (1 + mmr)`.

### binance BTC/USDT — five gap liquidations, all shorts, all past threshold

| strategy | iv | entry | booked exit | threshold | beyond | realized | loss / margin | exit_at |
|---|---|---|---|---|---|---|---|---|
| `rsi_mean_reversion` | 12h | 69,296.14 | 77,259.55 | 74,366.59 | +3.9% | −0.5799 | 1.16x | 2026-08-22T13:26:55Z |
| `rsi_mean_reversion` | 1d | 65,001.70 | 77,259.55 | 69,757.92 | +10.8% | −0.9484 | 1.90x | 2026-08-22T13:26:55Z |
| `rsi_mean_reversion` | 2h | 63,030.89 | 77,259.55 | 67,642.91 | +14.2% | −1.1343 | 2.27x | 2026-08-22T13:26:55Z |
| `rsi_mean_reversion` | 4h | 64,157.07 | 77,259.55 | 68,851.49 | +12.2% | −1.0266 | 2.05x | 2026-08-22T13:26:55Z |
| `mtf_stochastic_4h_1d_sma50` | 4h | 63,101.18 | 79,307.09 | 67,718.34 | **+17.1%** | **−1.2898** | **2.58x** | 2026-08-25T10:43:29Z |

Every ledger runs `fixed_notional = 5.0` at leverage 10, so posted margin is
$0.50 per position. An isolated-margin liquidation should lose approximately
that margin. These lost 1.16x–2.58x of it.

The two exit timestamps are not trade timestamps — they are wall-clock instants
(`13:26:55Z` on 08-22, `10:43:29Z` on 08-25, the latter being this route's
recorded `historical_replay_completed_at`). Four positions closed at the same
second at the same price: the first mark after a gap flushing everything that
was open.

### binance XAU/USDT — the control that proves the mark path itself is fine

| strategy | iv | entry | booked exit | threshold | beyond | realized | loss / margin | exit_at |
|---|---|---|---|---|---|---|---|---|
| `rsi_mean_reversion` | 12h | 4,193.72 | 4,610.23 | 4,500.58 | +2.4% | −0.5018 | 1.00x | 2026-08-22T13:27:09Z |
| `rsi_mean_reversion` | 1d | 4,353.16 | 4,672.73 | 4,671.68 | **+0.0%** | −0.3722 | 0.74x | 2026-08-24T11:38:13Z |

The 08-24 one did **not** land on a restart instant and closed *exactly* at its
threshold. When the mark feed is continuous, liquidation is priced correctly.
The defect is the gap, not the formula.

### exness is structurally immune, which is a methodology problem of its own

Both exness demo ledgers carry `leverage: 1`, `maintenance_margin_rate: 0.0`.
`isolated_liquidation_price` returns `None` for `leverage <= 1`, so exness
positions can never liquidate — `liquidation_count = 0` on both exness routes,
and it always will be.

This program's central validation rule is "a result must hold cross-broker".
That rule is currently comparing a **10x liquidatable** ledger against a **1x
non-liquidatable** one. Any binance-side result that includes a gap liquidation
is being cross-checked against a broker where the same event cannot occur. This
does not invalidate past cross-broker *falsifications* (a candidate that fails
on both is still failed), but it does mean binance-vs-exness PF gaps carry an
asymmetry nobody has been accounting for.

## Part 3 — Why this specifically matters now

The 08-25 liquidation hit `mtf_stochastic_4h_1d_sma50`: Round 189's deployment,
the swing 4h/1d candidate, and the **only mechanism in 205 rounds that this
program ever validated as carrying real edge**.

| ledger | trades | gross profit | gross loss | net | PF |
|---|---|---|---|---|---|
| `demo-backtest-4h` (replay seed) | 12 | 2.6785 | 0.8168 | +1.9158 | **3.28** |
| `demo-4h` (live) | 13 | 2.6785 | 2.1066 | +0.6260 | **1.27** |

Gross profit is identical; the entire difference is that single −1.2898. One
gap liquidation cut the live-ledger PF of the program's best strategy from 3.28
to 1.27. On exness the same strategy sits at 12 trades / +1.8315 / PF 3.20 with
no live trade at all.

And the ledger it damaged is precisely the one being counted toward maturity.
`mature_alpha_strategy_quality` (`trading_modes.rs:611-622`) returns `0.0`
below `PERFORMANCE_CONFIDENCE_TRADES = 20` (`trading_modes.rs:431`), so
`strategy_weight` is currently **0.0 for this strategy on both BTC routes** —
confirmed live: binance `{candle_momentum 0.5229, rsi_mean_reversion 0.4771,
all four mtf_* 0.0}`, exness `{rsi 0.6450, candle 0.3550, all mtf_* 0.0}`.

### The maturity gate is frequency-blind — quantified

The 12 replay trades span 2025-10-19 → 2026-08-16, about **43.4 weeks**, i.e.
**~0.28 trades/week** — close to Round 189's ~0.35/week estimate, now measured
rather than estimated. From 13 (binance) and 12 (exness) trades, reaching 20
takes roughly **25-28 more weeks**.

So the only validated edge the program has contributes **exactly zero** to every
Portfolio decision until roughly **March 2027**, while `candle_momentum` and
`rsi_mean_reversion` — PF 0.35-0.94 at seven of eight intervals on binance BTC —
hold 100% of the weight. Round 188 listed "a shorter, strategy-specific
`PERFORMANCE_CONFIDENCE_TRADES` override" as an option and Round 189 chose to
deploy without it; this round supplies the number that option was missing.

## What is proven, and what is not

Proven from production data and code:

- Liquidation is evaluated only on authoritative marks, never on replayed candles.
- Five binance BTC positions were closed 3.9-17.1% past threshold at two
  wall-clock instants, losing 1.16-2.58x posted margin.
- A continuous-feed liquidation on the same code closed at +0.0% past threshold.
- Exness ledgers cannot liquidate at all (`leverage = 1`).
- `mtf_stochastic_4h_1d_sma50` live PF fell 3.28 → 1.27 from one such close, and
  its `strategy_weight` is 0.0 on both BTC routes.
- Observed swing frequency is ~0.28 trades/week.

**Not** proven, and deliberately not claimed:

- The exact candle at which each position *would* have liquidated with a
  continuous feed. That needs a replay with mark data, which does not exist today.
- Whether the 1x/0.0-mmr exness ledger config is a deliberate CFD modelling
  choice or a leftover. It should be read from the deployment rules before anyone
  changes it — Round 86 already had one leverage-labelling correction.
- Any claim that fixing this turns a losing system profitable. It will not.
  Every Alpha strategy here still has PF < 1 at the intervals that carry weight.
  This is a measurement-integrity defect, not an edge.

## Handoff

Logged as a new `[trading][high]` Todo for Codex with two separable pieces: the
gap-liquidation pricing defect (the P1) and the frequency-blind maturity gate
(a design question, needs a decision before it is worth implementing).
