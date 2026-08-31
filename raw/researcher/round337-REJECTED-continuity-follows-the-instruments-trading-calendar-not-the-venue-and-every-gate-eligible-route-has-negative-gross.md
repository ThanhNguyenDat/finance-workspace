# PRECISE VERSION NOW MEASURED (Round 342)

This file's "`exness XAU` is the only route with a positive gross edge" was withdrawn by round
338 because it sampled one band per route. With the fleet complete at **six of six** routes at
the **deployed band**, the precise version holds: `exness XAU` **+0.7820** is the only positive
gross; `bybit XAUT` −0.0135, `binance XAU` −0.3442, `bybit BTC` −1.3153, `binance BTC` −1.7909,
`exness BTC` −2.1476. The withdrawal of the word "only" stands for *arbitrary* bands; at the
deployed band the statement is measured. See `round342-NEEDS-MORE-RESEARCH-the-two-gold-routes-track-each-other-at-0-996-in-price-and-0-287-in-portfolio-pnl.md`.

---

# TWO CORRECTIONS (Round 338)

**1. "The only route with a positive gross edge" is withdrawn.** That was measured at **one
band per route**. On `bybit XAUT` two of three bands give gross **+0.2662** (10.36/week) and
**+0.2590** (1.96/week); only the deployed band gives close to 0. The structural point
survives in weakened form — every gate-eligible route still fails the gate, and the largest
gross found anywhere is still `exness XAU`'s +0.78 — but "only" was an artifact of
single-band sampling.

**2. The cross-route frequency-versus-gross lead is refuted.** Run as a within-route ladder on
this gate-eligible route, gross differs by **2.8 percent across a 5.3x frequency range**. No
within-route support; round 328's flat-gross reading is reconfirmed. See `round338-REJECTED-the-cross-route-frequency-gross-pattern-does-not-survive-a-within-route-ladder-and-bybit-xaut-does-have-gross-edge.md`.

---

# Round 337 — REJECTED (my hypothesis): the continuity failure follows the **instrument's trading calendar**, not the venue — `exness BTC` is a CFD and is nearly clean. And across four routes now gate-measured, **the only route with a positive gross edge is the one whose gate verdict cannot be established.**

Classification: **REJECTED** — my pre-registered venue hypothesis failed, and the search for a
gate-eligible route with an edge came back empty on both routes tested. Two bounded Docker
sweeps (exactly the 2-container budget), **XAU-first**.

## Two pre-registered predictions

Round 336 established that `exness XAU` fails `input_continuity` on all seven non-5m
intervals at every window, while `binance BTC` is completely clean. Two candidate
explanations, both testable with one container each:

- **(A)** the failure is a **venue** property of the Exness CFD surface → `exness BTC`, a
  CFD on the same venue, fails the same seven intervals. **Refuted if it is clean.**
- **(B)** `bybit XAUT` — gold exposure on a 24/7 crypto venue — is gap-free on all eight
  intervals and therefore gate-eligible. **Refuted if it fails continuity.**

## (A) is refuted — the calendar, not the venue

`exness BTC/USD`, `--days 500`, holdout 2026-05-22 → 2026-08-30 (28,788 candles, 101
observed days):

| interval | verified gaps | unverified gaps |
|---|---|---|
| 5m | 1 / 1 candle | **15 / 54 candles** |
| 15m | 0 | 3 / 9 |
| 30m | 0 | 2 / 4 |
| 1h | 0 | 1 / 1 |
| 2h, 4h, 12h, 1d | 0 | **0** |

Four intervals fail, not seven, and the counts are **three orders of magnitude smaller** than
`exness XAU`'s (15 gaps / 54 candles against 628 gaps / 27,659 candles at 15m). Half the
surface is perfectly clean.

**So the Exness CFD venue does not itself produce the failure.** `exness BTC/USD` trades
essentially around the clock; `exness XAU/USD` follows the gold market's weekly session
schedule and closes every weekend. The hundreds of unverified gaps track **the instrument's
trading calendar**, and the venue is incidental. My hypothesis named the wrong variable.

One thing this route shows that no previous run did: `input_continuity_failed:5m` — the 5m
surface itself fails here, and a distinct check, **`holdout_interval_continuity`**, appears
in the failure list. `exness XAU`'s 5m has always been fully marked (645 verified / 0
unverified). So marker coverage is not simply "5m done, the rest not"; it varies by route.

## (B) is confirmed — and it buys nothing

`bybit XAUT/USDT` spot, `--days 500`, holdout 2026-05-22 → 2026-08-30 (28,799 candles, 101
observed days): **zero verified and zero unverified gaps on all eight intervals**, no
continuity entry in the failure list, `minimum_holdout_days` passes. It is **gate-eligible**.

And it fails on performance, badly:

```
FAILED: minimum_trades_per_week, positive_day_ratio, median_daily_pnl,
        negative_day_streak, sortino_ratio, sharpe_ratio,
        gross_pnl_positive, cost_to_gross_pnl_ratio
```

64 trades, **4.48 per week**, gross **−0.01346**, cost drag 0.4069, net −0.4204,
Sharpe −1.397, Sortino −1.965, **negative-day streak 13** — the worst streak measured on any
route in this arc.

## The picture across four gate-measured routes

| route | gate-eligible | trades/week | **gross before costs** | net | Sharpe |
|---|---|---|---|---|---|
| `exness XAU` @900 | **no** (7 intervals) | 6.85 | **+0.7820** | −0.4110 | −0.860 |
| `bybit XAUT` @500 | **yes** | 4.48 | −0.0135 | −0.4204 | −1.397 |
| `binance BTC` @500 | **yes** | 21.84 | −1.7909 | −3.9407 | −6.753 |
| `exness BTC` @500 | no (4 intervals) | 24.58 | −2.1476 | −4.5624 | −7.510 |

**`exness XAU` is the only route with a positive gross edge, and it is precisely the route
whose gate verdict cannot be established.** Every gate-eligible route measured has gross at or
below zero — which means no cost reduction and no frequency lever can reach profitability on
them, because there is nothing there to keep.

That is an uncomfortable but honest reading of where the last twenty rounds of cost and band
work sit: the cost arc (Rounds 313-335) is entirely about `exness XAU`, the one route where
the effort makes sense **and** the one route whose gate verdict is structurally unreachable.

## An observation, explicitly not a claim

Ordered by frequency, the four gross figures run +0.7820 (6.85/week), −0.0135 (4.48),
−1.7909 (21.84), −2.1476 (24.58). The two low-frequency routes sit at or above zero and the
two high-frequency routes are deeply negative.

If that held up it would say the Portfolio's extra decisions are **systematically worse**, not
merely more expensive — a different and more serious statement than Round 328's "frequency
multiplies cost without creating edge". **But four routes with different instruments, venues,
data depths and windows is not a controlled test**, the ordering is not monotone in frequency
(4.48/week sits below 6.85/week on gross), and Round 328's own within-route ladders held gross
roughly flat across a 5-7x frequency change. I am recording it as a lead, not a finding.

## What is proven, and what is not

Proven:

- `exness BTC` @500: 4 intervals fail continuity (5m 15 unverified gaps / 54 candles, 15m 3/9,
  30m 2/4, 1h 1/1); 2h, 4h, 12h, 1d completely clean; `holdout_interval_continuity` also
  fails. 351 trades, 24.575/week, gross −2.14756, cost 2.41489, net −4.56244, Sharpe −7.510,
  Sortino −7.470, streak 6.
- `bybit XAUT` @500: 0 gaps of any kind on all eight intervals, 101 observed days,
  gate-eligible. 64 trades, 4.480/week, gross −0.01346, cost 0.40693, net −0.42039,
  Sharpe −1.397, Sortino −1.965, streak 13, positive-day ratio 0.366.
- Of the four routes gate-measured so far, exactly one has positive gross, and it is the one
  that is not gate-eligible.

Not proven, and deliberately not claimed:

- **That the trading calendar is the confirmed cause.** What is shown is that the *venue*
  hypothesis fails: one Exness CFD is nearly clean while another is not. The calendar is the
  obvious remaining difference between them, and I have **not** verified it against session
  schedules or the marker-writing path per route.
- That gold has no edge. `bybit XAUT` is a different instrument, venue, depth and liquidity
  profile from `exness XAU` — this is **not** a controlled comparison of the underlying, and
  the two disagree on gross sign.
- That negative gross is a permanent property of any of these routes. **One window each.**
  Rounds 331-334 showed window-fragility on `exness XAU`; nothing here tests it elsewhere.
- The frequency-versus-gross pattern above. Four uncontrolled points, non-monotone, and
  contradicted by the within-route evidence already on file.
- Anything about the two routes still unmeasured by the gate — `bybit BTC` and `binance XAU`.
- Any promotion. Four routes, four failures, and the only positive gross belongs to a route
  that cannot produce a gate verdict.
