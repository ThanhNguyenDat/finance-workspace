# THE DENOMINATOR WAS BIASED (Round 358)

This file computed live rates as *closes ÷ (last entry − first entry)*. **That conditions on the
events** and inflates the rate; the correct denominator is the observation window. Two facts this
file listed as unread are now verified: the writer is **append-only** (`trade_log.rs` has `ZADD`
only — no trim, expiry or delete, so "wait and re-read" is valid), and **three entries really are
one trade** written under three paper scopes, so this file's counts were right.

Redis started **2026-08-22 05:26 UTC**. Over that 8.67-day window, **five of six routes have their
backtest rate outside the live 95% Poisson interval**, all with the backtest predicting **4.5x to
7.6x** more trading than happens. Over the 3.4-day worker window, only `exness BTC` is outside.
**The retained data does not settle which window applies**, so no discrepancy is claimed — but
this file's "no inconsistency detected" was reached with the wrong denominator.
See `round358-REJECTED-the-guard-is-immaterial-only-on-exness-xau-it-moves-binance-btc-by-41-percent.md`.

---

# Round 357 — DATA-ISSUE: the production trade log holds **1 to 6 closed trades per route** over a 3-day span that matches worker uptime. The live-versus-backtest check this arc has never run **still cannot be run** — and I am recording why, with the numbers.

Classification: **DATA-ISSUE** — the evidence needed to calibrate the replay against production
does not exist in retained form. **Zero containers**; narrow read-only production inspection.

## The test this was meant to be

Round 356 established that the gate scores the **guard-free** stream while `one_target` is the
guarded one, and that at @300 they differ by **26.8%** in trade count (280 against 355, i.e.
6.53 against 8.28 per week over the full window). That difference is exactly the kind of thing a
**live trade rate** could arbitrate: production either behaves like the guarded stream or like the
guard-free one.

**Pre-registered as a partition:** the live closed-trade rate on `exness.cfd.XAU.USD` is closer to
the guarded rate (6.53/week) → the deployed system is guarded and `one_target` is the right
reference; closer to the guard-free rate (8.28/week) → the gate's construction is the faithful
one.

## Why it cannot be run

Production Redis, all six durable trade logs (`trades:<route>`, zset, three entries per closed
trade, **no TTL** — `TTL` returns −1):

| route | entries | **closes** | span | live closes/week |
|---|---|---|---|---|
| `exness XAU` | 3 | **1** | single timestamp | **n/a** |
| `bybit XAUT` | 3 | **1** | single timestamp | n/a |
| `binance XAU` | 3 | **1** | single timestamp | n/a |
| `binance BTC` | 18 | 6 | 2.74 d | 15.33 |
| `bybit BTC` | 12 | 4 | 2.45 d | 11.43 |
| `exness BTC` | 12 | 4 | 2.90 d | 9.66 |

The earliest entry on any route is **2026-08-27 14:39 UTC** and every live-action worker reports
**"Up 3 days"**. The log therefore begins at worker start, not at a retention boundary — the keys
carry no TTL, so this is **restart truncation, not expiry**.

**`exness XAU` — the one route the whole arc is about — has exactly one closed trade, and all
three of its entries share a single timestamp.** No rate can be computed, so the registered
partition has no input. With one observation the exact Poisson 95% interval spans roughly
**0.03x to 5.6x** the point estimate; discriminating a **26.8%** rate difference is not remotely
possible.

## What the BTC routes do say, and how little

The three routes with more than one close can be compared to their gate-run rates, with exact
Poisson intervals:

| route | closes | live/week | **95% CI** | backtest/week | consistent? |
|---|---|---|---|---|---|
| `binance BTC` | 6 | 15.33 | **[5.63, 33.36]** | 21.84 | yes |
| `bybit BTC` | 4 | 11.43 | **[3.11, 29.26]** | 12.11 | yes |
| `exness BTC` | 4 | 9.66 | **[2.63, 24.72]** | 24.58 | yes |

**No inconsistency is detected on any route** — and the intervals are so wide that this is
**agreement by lack of power**, not evidence of calibration. `exness BTC`'s backtest rate sits
near the top of its interval (24.58 against an upper bound of 24.72), which is the closest thing
to a signal here and is not one.

This is the first live-versus-backtest rate comparison in the arc. Its honest summary is: **the
replay has never been checked against production behaviour, and with the evidence production
retains it still has not been.**

## Where this sits among the known gaps

It is the same shape as audit item **L4** — the backtest serialises no per-trade record — seen
from the other end: **production serialises too few**. Between them, there is no path today from
a backtest number to a live observation of the same quantity:

- backtest side: aggregates only, no trade rows (`portfolio_measurement.rs:23-28`);
- live side: 1-6 closes retained, reset on restart.

The arc's numbers are internally consistent and **externally unvalidated**, and that is a
property of the evidence chain rather than of any one round.

## What is proven, and what is not

Proven:

- The six-route trade-log table above, read from production Redis; three entries per closed trade;
  `TTL` = −1 on the inspected key; earliest entry 2026-08-27 14:39 UTC; all six workers "Up 3
  days".
- `exness XAU` retains exactly one closed trade, all entries at one timestamp.
- Exact Poisson 95% intervals for the three BTC routes as tabulated; all three contain their
  backtest rate.

Not proven, and deliberately not claimed:

- **That the live and backtest rates agree.** Three intervals spanning 3-33 per week contain
  almost any plausible value. This is **failure to detect**, not agreement.
- **That production is guarded or guard-free.** The registered partition could not be evaluated;
  no conclusion either way.
- That the log is capped by design. It has no TTL and starts at worker uptime, which is
  consistent with restart truncation — but **I did not read the writer** and cannot rule out a
  size cap elsewhere.
- That three days is the normal retention. Workers restarted 3 days ago; a longer-running worker
  might retain more, and that is testable simply by looking again later.
- Any promotion. Nothing measured, nothing changed.

## The one cheap follow-up this creates

The log grows while the workers stay up. **Re-reading these six keys after a longer uninterrupted
run is free** and eventually reaches a sample that can discriminate: `exness XAU` needs roughly
**30-40 closes** — about **6-8 weeks** at its backtest rate — before a 27% difference is
separable at 95%.
