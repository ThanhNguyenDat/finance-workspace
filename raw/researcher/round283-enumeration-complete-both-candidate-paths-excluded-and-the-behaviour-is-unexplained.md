# Round 283 — Enumeration complete: both candidate paths for `target_flat` are excluded, and the observed behaviour matches neither

Classification: **NEEDS-MORE-RESEARCH**. Local code inspection. **Zero containers.**

## Round 282's instruction, followed literally

Round 282 said: *"find every constructor of `PortfolioDecision` reaching `construct()`
on the paper-ledger path, **not to guess again**."* Done systematically rather than by
grepping for a symptom.

**Every `PortfolioDecision` constructor feeding the Portfolio/paper path sets
`exit: false`, hard-coded:**

| site | context |
|---|---|
| `trading_modes.rs:862` | `decide()` passing branch |
| `trading_modes.rs:1101` | `decide()` → `hold()` |
| `trading_api.rs:2458` | `record_market_without_decision` |

Both runtime `construct()` callers that feed paper ledgers take their decision from
`…evidence.decide(…)`: `trading_api.rs:1707` (realtime) and `2260` (historical
replay driver). The remaining constructors are in `finance-research` (a separate
binary) and `alpha_decision` (single-strategy `demo-*` ledgers).

**So `decision.exit` is never true on this path — and Round 282's inference that it
must be true is withdrawn.**

## `apply_target` has exactly two call sites

```
trading_modes.rs:1734  apply_target(…, "strategy_exit",  "opposite_decision")   ← single-strategy
trading_modes.rs:1764  apply_target(…, "target_flat",    "target_changed")      ← Portfolio
```

So `target_flat` is unambiguously the **flat branch of the Portfolio path**, and it
requires `target.position == Flat`.

## A new fact: reversals never happen

`target_changed` — the reversal label at the same call site — **does not appear at all**
in any close-reason distribution collected across three routes and 1176 trades
(Rounds 261, 280, 282 all show only `stop_loss`, `take_profit`, `target_flat`).

The reversal branch closes and reopens **within the same call**
(`trading_modes.rs:1997-2008`, "A reversal is one action"), so a reversal would
produce a `target_changed` close with a ~0 gap. None exists. **Direct reversals never
occur**, which is consistent with Round 281's cost-gate reading even though Round 282
refuted that reading's link to `target_flat`.

## Both candidate mechanisms are now excluded

For a `target_flat` close, `current_target` must already be Flat. On the Portfolio
path that is reachable only via:

- `force_flat()` — sets `waiting_after_protective_exit = true` → next entry needs the
  3h guard;
- `observe_execution(ProtectiveExit)` — same flag, same consequence.

Round 282 measured re-entry after `target_flat` at **100% ≤0.2h on all three routes**
(n = 66/18/186, median 0.08h). **Neither path permits that.** And the third
possibility, `decision.exit == true`, is excluded above.

**So the observed behaviour is not explained by the code as I have read it.** I am
stating that rather than proposing a third mechanism, having had two refuted in two
rounds.

## The most likely place I am wrong

These are `paper-**backtest**-*` ledgers — the historical replay seed. I have assumed
they are filled through `trading_api.rs:2260`, on the strength of Round 262's
`historical_replay_completed_scopes` evidence. If instead they are seeded through a
path I have not traced, every inference above about *their* close reasons is built on
the wrong call graph. **Verifying which code path actually writes these ledgers is the
next step** — before any further mechanism claims.

## What is proven, and what is not

Proven:

- The complete list of `PortfolioDecision` constructors and `construct()` /
  `apply_target()` call sites, cited to line.
- `exit: false` is hard-coded on all three constructors feeding the Portfolio path.
- `apply_target` has exactly two call sites with distinct label pairs.
- `target_changed` appears zero times across three routes and 1176 trades.

Not proven, and deliberately not claimed:

- **Any mechanism for `target_flat`.** Three candidates have now been excluded:
  `force_flat` (Round 282), `decision.exit` (this round), and both protective paths.
  I am not offering a fourth.
- That the enumeration is exhaustive beyond the crates searched. It covers
  `finance-core`, `finance-api`, `finance-research` and `finance-strategy`,
  excluding tests.
- That Round 281's cost-gate correlation is explained. It remains an unexplained
  association, now joined by the absence of `target_changed`, which is at least
  consistent with reversals being blocked.
- That the ledgers are written by the path I assumed. That is the specific thing to
  check next, and it may invalidate this round's framing rather than extend it.
