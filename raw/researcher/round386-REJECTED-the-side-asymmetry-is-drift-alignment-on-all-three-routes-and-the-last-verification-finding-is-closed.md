# Round 386 — REJECTED: the side asymmetry is **drift alignment on all three routes**. The direction closes. P2-3 is resolved and the transaction reaches FINAL_VERIFY.

Classification: **REJECTED** — the side-asymmetry direction is closed as an edge
claim. Two containers (the budget), cleaned up.

## The synthesis I did not expect

Round 384 found the asymmetry inverts by instrument: short better on both BTC
routes, long better on gold. Round 385 showed gold's long advantage is drift.
This round completes it on matched pinned windows.

| route | long move/h | short move/h | short/long | net long | net short | better side |
|---|---|---|---|---|---|---|
| `exness XAU` | +5.152e−05 | +5.274e−05 | 1.024 | **+0.65265** | −3.81407 | **long** |
| `binance BTC` | −5.525e−05 | −6.697e−06 | 0.121 | −3.63186 | **−1.84068** | **short** |
| `bybit BTC` | −8.798e−06 | −1.688e−05 | 1.918 | −2.67790 | **−1.40548** | **short** |

**Gold's drift is positive in both exposure states; both BTC routes' drift is
negative in both.** Gold rose over the window; BTC fell.

**The better side is, on every route, simply the side aligned with the
instrument's drift.** Long wins on a rising asset, short wins on a falling one.
That is the same explanation round 385 established for gold, and it now covers
all three routes — including the two where the asymmetry pointed the *other*
way, which is what made them look like a separate phenomenon.

**There is no directional timing anywhere in this table.** The direction the
user proposed is closed as an edge claim.

## The residual, which is route-local and does not generalise

Around that drift baseline the routes disagree. On `binance BTC` the market fell
**8.3× faster while long** than while short — genuinely anti-timed. On
`bybit BTC` it fell **1.9× faster while short** — mildly well-timed. Same
instrument, same pinned window, same configuration, **opposite timing signs**.

That means the two Portfolios hold at sufficiently different times for the sign
to invert, on markets whose volatility r276 measured identical to three
decimals. Consistent with r345 (the replay is chaotic in its inputs) and r382's
window sensitivity. It is one more route-local effect, and I am not building on
it.

## The acceptance criterion this leaves behind

If a side-restricted rule is ever implemented, round 385's requirement now has
three routes behind it rather than one: **the criterion must be "beats passive
exposure over the same bars", never "positive PnL"** — because on every route
tested, the profitable side is the one the market handed to it.

## Verification: the last finding is closed

**P2-3 resolved.** Codex `gpt-5.6-terra` / high, round 3, attempt 1, exit 0,
commit `ae6a1fd`. Verified by running it:

| report | `data_as_of` | `candle_count` |
|---|---|---|
| gate | **2026-08-31T00:00:00Z** | 174,254 |
| non-gate | 2026-08-31T00:00:00Z | 259,201 |

The gate report now carries the cutoff, so a gate verdict is reproducible from
its own output.

**All findings are closed**: P1 (via the achievable determinism criterion),
P2-1, P2-2, P2-3. Task 4.2 reconciles to 1.8e-15. 702 tests pass in my own run.
`finance-core` untouched, `finance-strategy` additive only. The transaction is
in **FINAL_VERIFY**.

## What is proven, and what is not

Proven:

- The three-route drift table above, all on `--as-of 2026-08-31T00:00:00Z`
  except `bybit BTC`'s earlier rolling-window export, which this round replaced
  with a pinned one (491 long / 360 short).
- Gold's drift positive in both states, both BTC routes' negative in both.
- The gate report now emits `data_as_of`.

Not proven, and deliberately not claimed:

- **That drift alignment is the whole story.** It explains which side wins on
  three routes; the residual timing sign still differs between two near-identical
  markets, and that is unexplained.
- That a long-only rule would fail. On gold it would likely profit — as beta.
  On BTC over this window it would have lost, since BTC fell. Neither outcome
  would demonstrate skill.
- That BTC fell by any particular amount. Inferred from all four exposure-state
  drifts being negative, not from a price query.
- That the change is released. FINAL_VERIFY is entered; nothing is pushed, and
  the push is an outward action I will not take unprompted.

## Named next step

The transaction is ready for the release decision. Separately, the open research
question from round 385 stands and is **not** a side question: why is the
Portfolio short 51% of the span on a route that rose 105%, and long into the
fastest declines on `binance BTC`? Both point at the Alpha ensemble's
composition (three production candidates on gold, r375) rather than at any
Portfolio-layer knob.
