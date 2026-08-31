# Round 233 — Production's first durable trades read against the session's own rules, and the frozen XAU/binance route has un-frozen

Classification: **NO-CHANGE**. No containers — read-only production inspection.

## Why look at production now

Rounds 231-232 concluded the candidate population carries a real but small
persistence signal (~1.55x, z=3.22), too small to identify anything. Production
is the only genuinely unseen data the program has. Round 207 built the durable
trade log as the measurement path and said to re-read it later.

## What production has done

Durable Portfolio closes, all six routes, since the log went live:

| route | closes | wins | PF | close reasons |
|---|---|---|---|---|
| binance BTC | 4 | 2 | 1.74 | 3 target_flat, 1 take_profit |
| exness BTC | 3 | 1 | 0.84 | 2 stop_loss, 1 take_profit |
| bybit BTC | 2 | 1 | 1.68 | 1 take_profit, 1 stop_loss |
| binance XAU | 1 | 1 | — | 1 take_profit |
| exness XAU | 1 | 1 | — | 1 take_profit |
| bybit XAUT | 1 | 1 | — | 1 take_profit |

Twelve closes, nine wins. Aggregate PnL is positive on every rule.

## And it says nothing, by this session's own rules

Two reasons, both measured earlier in this session rather than asserted now:

1. **Sample.** Round 210 established that a PF from fewer than ~30 trades carries
   no usable information. These are **1 to 4 trades per route**. Quoting "binance
   BTC PF 1.74" would be precisely the error corrected in Rounds 219, 229/230 and
   231/232 — three of my four self-corrections this session were exactly that.

2. **Independence.** The three gold routes each closed **exactly one winning
   take_profit**. Round 209 measured gold sources correlating **0.9915** on 4h
   returns; three venues capturing the same gold move is one observation, not
   three. The same applies to the BTC routes. Effective independent events are
   roughly **4-5, not 12**.

Nine wins from twelve correlated trades over two days is what a coin looks like
at this sample size. **No performance claim is made here, in either direction.**

## The one substantive finding: XAU/binance has un-frozen

| measurement | Round 206 (2026-08-28) | now (2026-08-29T00:30Z) |
|---|---|---|
| `paper-fixed-pct` trades | 7 | **8** |
| `paper-fixed-pct` PnL | −0.0478 | **+0.0466** |
| `strategy_weights` | rsi 0.6267 / candle 0.3733 | **unchanged** |

The route frozen since 2025-12-26 — diagnosed in Round 203, re-confirmed frozen
in Rounds 205 and 206 — has executed its eighth trade, a take_profit win, and its
selected-rule PnL has flipped positive.

Read carefully:

- **The freeze broke on market conditions, not on a weight change.**
  `strategy_weights` are identical to Round 206, so `reweight_from_alpha_performance`
  did not move. Round 203's gate needs `|entry| >= 0.10` and `|trend| >= 0.10`
  with matching signs; the trend score evidently crossed.
- **One winning trade validates nothing.** Round 203's backtest put this route's
  unfrozen behaviour at −1.54, and eight trades total is far below any floor. The
  PnL flip from −0.048 to +0.047 is a single trade moving a number that was
  always near zero.
- It does mean Round 205's framing — "stays frozen by choice" — is now out of
  date as a description of the live route, whatever it was as a decision.

## A process note worth keeping

The checkpoint query initially returned `(nil)`, which looks exactly like
checkpoint loss on a production route. It was a wrong key on my side — the route
suffix `.5m` was missing. Scanning `*worker_checkpoint*` showed all six keys
present and healthy.

Recorded because the failure mode is asymmetric: reporting "production checkpoint
missing" would have triggered an incident response over a typo. Scan before
concluding absence.

## What is proven, and what is not

Proven:

- Twelve durable Portfolio closes across six routes; per-route counts 4/3/2/1/1/1;
  nine wins, three losses; close reasons as tabulated.
- binance XAU: 7 → 8 trades, `paper-fixed-pct` PnL −0.0478 → +0.0466,
  `strategy_weights` unchanged, `evaluation_count` 3836.
- All six worker checkpoints exist.

Not proven, and deliberately not claimed:

- Anything about production profitability. The sample is 1-4 trades per route
  across correlated venues over two days.
- That the XAU/binance route is now healthy or that its edge changed. One trade.
- That the un-freeze persists. It may re-freeze on the next evaluation; the gate
  is a live condition, not a state that was released.
