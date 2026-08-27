# Round 203 — XAU/binance's 8-month freeze: mechanism fully diagnosed, proposed fix REJECTED by its own backtest

## Trigger

User: "binance.perpetual_future.XAU.USDT tôi thấy last trade là 2025 ta? các
khác đều là 2026." Correct. `decisions_since_target_change = 69,710` × 5m
≈ 242 days, landing on 2025-12-26 — matching the "Sell · 26/12/2025" the
user had spotted earlier. It is the only one of six routes frozen.

## Mechanism — precise, and different from the Round 183 hypothesis

`decide` needs `|entry_score| >= 0.10` AND `|trend_score| >= 0.10` AND both
the same sign. Live values:

```
entry_score = +0.14348   clears
trend_score = -0.03899   too small AND opposite sign
```

`trend_score` broken down (interval weight × strategy weight × signed
strength):

| interval | weight | candle_momentum | rsi_mean_reversion | subtotal |
|---|---|---|---|---|
| **1d**  | **0.430** | long  (+0.163) | **hold (0)** | +0.163 |
| **12h** | **0.190** | short (−0.072) | **hold (0)** | −0.072 |
| 4h  | 0.140 | long (+0.053) | short (−0.087) | −0.034 |
| 1h  | 0.048 | short | short | −0.048 |
| 2h  | 0.048 | short | short | −0.048 |
| | | | **total** | **−0.039** |

`rsi_mean_reversion` holds **62.2% of the strategy weight** while reporting
`Hold` at both `1d` and `12h` — together **62% of all trend weight** —
because RSI(14) rarely reaches 30/70 on daily gold bars. Only
`candle_momentum` (37.8%) speaks there, and it contradicts itself across the
two, so the two heaviest intervals nearly cancel.

Contrast with Exness XAU/USD, which trades normally: there `candle_momentum`
carries the **full 1.0** weight (the other two strategies reweighted to 0.0),
so it speaks alone and decisively and clears the gate easily.

**Design observation:** `strategy_weights` is one global number per strategy
applied at every interval, but a strategy's usefulness is interval-dependent.
RSI mean reversion earns its weight on the fast intervals where it signals
often, then carries that same share into intervals where it is structurally
almost always silent — where its share is simply lost rather than deferring
to the strategy that does have an opinion.

## Proposed fix, implemented and A/B tested

Renormalize per interval across only the strategies with a non-`Hold`
opinion: silence abstains instead of voting zero. Purely a re-weighting of
evidence already gathered at the same instant — no time semantics, ordering,
or freshness changes (no-lookahead untouched), and computed rather than
stored (no checkpoint schema change).

Built two `finance-research` images from identical source except this change
and ran both against Binance XAU/USDT, `--days 1825`, minutes apart:

| metric | baseline | variant |
|---|---|---|
| candles | 74,099 | 74,100 |
| decision_count | 73,909 | 73,910 |
| `one_target` trades | 219 | 220 |
| **`one_target` realized_pnl** | **−1.5353** | **−1.5694** |
| execution_cost rejections | 25 | 24 |

**Verdict: rejected.** No measurable improvement, and the PnL delta is
marginally negative. The windows also differ by one candle, so the delta is
within noise either way — which is itself the finding: the change does not
move the outcome. Per the standing rule that an improvement only counts once
validated out-of-sample, this does not qualify. Reverted; not shipped.

## The more important result: unfreezing this route is not obviously desirable

The backtest never freezes — it replays from a full evidence book, so its 219
trades ARE the "unfrozen" behavior of this route. That run returns
**−1.54 realized PnL**. So the honest reading is:

- Frozen, live: **7 trades, −0.049** (fixed-pct)
- Unfrozen, backtested over the same instrument: **219 trades, −1.54**

The freeze has been *protecting* this route from a negative-expectancy
policy, not costing it profit. "Fix the freeze" and "make this route
profitable" are different problems, and only the second one is worth doing
first — unfreezing a PF<1 route just makes it lose faster.

This does not mean leaving a structurally frozen route is acceptable
long-term; a route that cannot decide is a broken system regardless of edge.
But it does mean the freeze is not the urgent problem it looked like, and the
real work is the edge, not the gate.

## Also confirmed this round

The `finance-research` CLI completed a full 5-year multi-interval backtest
**for the first time today after 8 consecutive failures**, and the gate read
`finance_mw_grpc_requests_in_flight{method="Stream"} = 0` — completely free,
versus permanently pinned at 4 all day. Independent confirmation that the
Round 200/201 replay-deadlock fix (finance-live-action `81dfcc1`) is correct.
