# Round 282 — CORRECTION: `target_flat` is **not** `force_flat`. The pairwise test Round 279 never ran refutes Round 281's mechanism.

Classification: **REJECTED** — Round 281's causal claim fails its own prediction.
Read-only production evidence plus code inspection. **Zero containers.**

## The contradiction between two of my own rounds

Round 281 concluded that every `target_flat` close is a **risk-gate emergency close**
via `force_flat()`. But `force_flat` sets `waiting_after_protective_exit = true`
(`trading_modes.rs:285`), which by Round 279's own mechanism means re-entry must wait
the **3h guard**.

Round 279 concluded the opposite — that flat exits are followed by **immediate**
re-entry. And Round 279 reached that by matching **aggregate fractions** (≤0.2h gaps
vs flat-exit share), **never pairwise**. So either the code reading or the aggregate
inference was wrong.

The pairwise test settles it: for each close, what is the gap that follows *it*?

| route | after `stop_loss` | after `take_profit` | after **`target_flat`** |
|---|---|---|---|
| binance BTC | n=279, median **3.00h**, ≤0.2h **0.0%** | n=127, median 10.42h, ≤0.2h **0.0%** | n=66, median **0.08h**, ≤0.2h **100.0%** |
| bybit BTC | n=198, median 3.67h, ≤0.2h **0.0%** | n=94, median 12.50h, ≤0.2h **0.0%** | n=18, median **0.08h**, ≤0.2h **100.0%** |
| exness XAU | n=126, median 4.00h, ≤0.2h **0.0%** | n=79, median 3.42h, ≤0.2h **0.0%** | n=186, median **0.08h**, ≤0.2h **100.0%** |

**After `target_flat`, re-entry is immediate 100% of the time on all three routes**
(median 0.08h ≈ one 5m decision). After a protective close it is **never** immediate.

## Two consequences, in opposite directions

**Round 279 is confirmed and strengthened.** Its aggregate-fraction inference was
right, and the pairwise test it never ran now validates it directly, at 100%/0% on
370 target_flat gaps and 903 protective gaps.

**Round 281's mechanism is refuted.** If `target_flat` came from `force_flat`, the
flag would be set and re-entry would need 3h. It is immediate, always. So
`target_flat` is produced by the **`decision.exit == true`** branch of `construct()`
— the branch that explicitly sets `waiting_after_protective_exit = false` — and
**not** by the risk layer's `force_flat`.

Round 281's *correlation* survives: `execution_cost` rejections 98 vs 11 against
`target_flat` shares 47.6% vs 5.8% (8.9x vs 8.2x) is still an observed fact. **The
causal path I asserted from it is wrong.** I read one caller of `force_flat`, saw a
matching ratio, and concluded a mechanism without checking the prediction it makes.

## Where this leaves Round 280's question

**Reopened.** Round 280 asked where `decision.exit == true` originates; Round 281
answered "nowhere — it's `force_flat`", and that answer is now dead. The data say
`decision.exit` **is** true for these closes, so my reading that both `decide()`
branches set `exit: false` must be incomplete — there is a Portfolio decision
constructor I have not found.

## One incidental observation

After `take_profit` the median gap is **10.42h / 12.50h** on the BTC routes, against
**3.00h / 3.67h** after `stop_loss` — takes are followed by much longer waits than
stops, though both clear the guard. Not investigated.

## What is proven, and what is not

Proven:

- The pairwise table above: 100.0% immediate re-entry after `target_flat` and 0.0%
  after either protective close, on all three routes.
- `force_flat` sets `waiting_after_protective_exit = true` (`trading_modes.rs:285`),
  so it cannot be the source of an immediately-followed close.
- Round 279's aggregate inference is correct.

Not proven, and deliberately not claimed:

- **Where `decision.exit == true` comes from.** Still unlocated, and my previous
  answer was wrong. The next step is to find every constructor of `PortfolioDecision`
  reaching `construct()` on the paper-ledger path, not to guess again.
- That the `execution_cost` correlation is spurious. It is **unexplained**, which is
  different — 8.9x against 8.2x across two routes is not nothing, and the gate does
  fire. What is refuted is the path, not the association.
- Anything about why takes are followed by longer waits than stops.
- That Round 281's other findings fail. Its counter measurements and the policy
  comment (`max_total_cost_bps: 10.0`, reversals priced at 14bps) stand as read; only
  the link to `target_flat` is withdrawn.
