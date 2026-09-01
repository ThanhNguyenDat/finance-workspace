# Round 404 — DATA-ISSUE: round 403's live rate was inflated **exactly 3×** by pooling **three paper sizing configurations** of a **single** decision stream.

Classification: **DATA-ISSUE** — a defect in my own measurement one round old.
**Zero containers**; narrow read-only production reads.

## What round 403 missed

Round 403 counted closes in `trades:<route>` and concluded production trades
2–4× faster than the backtest. It did not read the payloads.

The payloads carry a `scope_id`, and there are **three per route**:

- `paper-fixed-pct-scope`
- `paper-compounding-10pct-scope`
- `paper-risk-2pct-scope`

**Production runs three paper sizing configurations in parallel**, and the trade
log pools all three under one key. Round 403 counted three configurations as one.

## They share one decision stream

Comparing the `(entry_at, exit_at, side, close_reason)` tuples across scopes:

| route | distinct tuples per scope | identical across all three |
|---|---|---|
| `exness XAU` | 3 / 3 / 3 | **3 of 3** |
| `binance BTC` | 6 / 6 / 6 | **6 of 6** |

**Every trade is the same trade**, opened and closed at the same moment on the
same side for the same reason. The scopes differ **only in position size**:

| scope | mean quantity, `exness XAU` |
|---|---|
| `paper-fixed-pct` | 0.001105 |
| `paper-compounding-10pct` | 0.213332 |
| `paper-risk-2pct` | 1.516232 |

A **1,372× spread in size**, and zero difference in decisions.

So the distinct trade counts are **3 and 6**, not 9 and 18.

## The corrected comparison

| route | scope | closes | live /wk (95% CI) | backtest | |
|---|---|---|---|---|---|
| `exness XAU` | each of three | 3 | 1.1 – 15.7 | 6.232 | **overlaps** |
| `exness XAU` | *pooled (r403)* | *9* | *7.4 – 30.6* | *6.232* | *live higher* |
| `binance BTC` | each of three | 6 | 3.9 – 23.4 | 7.661 | **overlaps** |
| `binance BTC` | *pooled (r403)* | *18* | *19.1 – 50.9* | *7.661* | *live higher* |

**Round 403's headline is withdrawn.** Per configuration, production's trade
rate **overlaps** the backtest's holdout rate on both routes tested. The 2–4×
gap was exactly the 3× pooling factor.

Round 403's *alternative* explanation — the rising-frequency trend — is neither
confirmed nor needed: **there is no discrepancy left to explain.**

## What is proven, and what is not

Proven:

- Three `scope_id` prefixes per route in the live trade log.
- All `(entry, exit, side, close_reason)` tuples are identical across the three
  scopes on both routes checked: 3 of 3 and 6 of 6.
- Mean position quantities differ by up to 1,372× between scopes.
- Per-scope live rates overlap the backtest holdout rate on both routes.

Not proven, and deliberately not claimed:

- **That production and the backtest agree on frequency.** "Overlaps" with 3 and
  6 events over 3.9 days is **weak** — the intervals span an order of magnitude
  and would overlap almost any plausible rate. This removes the evidence of
  disagreement; it does not supply evidence of agreement.
- That the three scopes exist on all six routes. Checked on two.
- That `paper-fixed-pct` is exactly the backtest's configuration. Its name and
  its tiny quantity are consistent with the backtest's `fixed-pct` rule and
  `fixed_notional` sizing, but I did not verify the parameters — that would mean
  reading worker configuration, which I am not doing.
- Anything about live PnL. Position sizes differ by three orders of magnitude
  between scopes, so live PnL is not comparable to the backtest's without
  establishing which scope corresponds and on what notional basis.

## The lesson worth keeping

Round 403 checked whether the log was trimmed, anchored the window carefully,
computed exact Poisson intervals, and tested the result's sensitivity to the
window — and still got the wrong answer, because it never looked at **what the
records were**. Rigour on the statistics did not compensate for not reading the
data.

## Named next step

The live comparison needs **distinct trades**, and there are 3–6 per route after
de-duplication. Round 403's "wait for 30+ days" stands, with the correction that
the usable count is **one third** of the raw key size — so a month of forward
time yields roughly 20–45 distinct closes per route, not 60–135.
