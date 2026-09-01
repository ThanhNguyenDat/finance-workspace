# Round 385 — REJECTED: gold's positive long side is **drift, not edge**. The strategy has **zero directional timing** — and it is positioned against the drift **75% of the time**.

Classification: **REJECTED** — the hypothesis that round 384's positive long
component represents edge is refuted. **Zero containers**: the emitted audit
records plus one narrow read-only price query.

## The test round 384 named

If the strategy has directional timing, the market should rise faster while it
is long than while it is short. If it has none, the drift it experiences is the
same in both directions and the long side's profit is simply alignment with a
rising market.

`exness.cfd.XAU.USD`, pinned window, 174,253 bars = 14,521 hours (605.0 days of
bars; the trading calendar, r370):

| | exposure (h) | sum raw move | **move per hour** |
|---|---|---|---|
| while **long** | 5,389.8 | +0.27767 | **5.152e−05** |
| while **short** | 10,950.7 | +0.57752 | **5.274e−05** |
| whole window (passive) | 14,521.1 | +1.04993 | 4.943e−05 |

Gold went **2174.827 → 4458.240, +105.0%**, over the window.

**Drift while short ÷ drift while long = 1.024.** The market rose at essentially
the same rate in both directions — and marginally *faster* while the strategy
was short. Both figures sit within 7% of the passive drift.

**That is zero directional timing.** The long side is profitable because it was
aligned with a market that doubled; the short side loses because it opposed the
same drift.

## The number that actually matters

**The strategy is short 75.4% of the traded span and long 37.1%** (they overlap
because exposure is measured per trade). It spends **2.0× more time positioned
against the dominant drift than with it**, on a route where that drift was
+105%.

Long: 147 trades, **+0.65265**. Short: 255 trades, **−3.81407**.

So round 384's "first positive component in the arc" is not a discovery about
the long side. It is the visible half of a strategy that is **systematically
wrong-sided on this route**.

## What this means for a long-only rule

A long-only rule on `exness XAU` over this window would very likely make money —
and it would be **beta, not alpha**: a directional position in an asset that
doubled, carrying that position's full drawdown, with no evidence of timing.
Calling that a Portfolio-layer improvement would be exactly the tautology rounds
255 and 257 already caught this program in.

That is not an argument against implementing a side restriction. It is an
argument that **if it is implemented, its acceptance criterion must be
"beats passive exposure over the same bars", not "positive PnL"** — otherwise
any long-only rule on a rising asset passes trivially.

## The question worth taking forward instead

Why is the Portfolio short 75% of the time on a route that rose 105%? That is
not a beta question and it is not answered by restricting a side. Candidate
explanations that this round does **not** test: the Alpha ensemble's
composition on that route (only three production candidates — r375), the
mean-reversion tilt of `rsi_mean_reversion` and `candle_reversion` in a trending
market, or the entry threshold's symmetry.

## What is proven, and what is not

Proven:

- Gold's window move (+105.0%) and bar count, from a narrow read-only query.
- Per-hour drift 5.152e−05 while long against 5.274e−05 while short, ratio
  1.024; passive 4.943e−05.
- Exposure 5,389.8 h long against 10,950.7 h short; net +0.65265 and −3.81407.

Not proven, and deliberately not claimed:

- **That a long-only rule would lose money.** It would probably make money on
  this window. The claim is that doing so would demonstrate nothing.
- That the strategy is wrong-sided on other routes. **One route, one window.**
  The BTC routes' short-better asymmetry (r384) points the other way, and BTC
  also rose over its window — so the same drift logic does **not** obviously
  transfer, and I have not run it.
- Any cause for the short bias. Three candidates named, none tested.
- That drift is constant within the window. Measured as an average; a
  concentrated run would change the per-hour comparison and I have not checked
  for one.

## Named next step

Run the same drift decomposition on the two BTC routes from the records already
held — **zero containers**. If BTC's short-better asymmetry also collapses to
drift, the whole side direction closes; if it does not, BTC is where a side rule
would actually be testable.
