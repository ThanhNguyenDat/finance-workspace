# MECHANISM IDENTIFIED IN CODE (Round 343)

The decorrelation this file measured has a **code-level explanation**, and it is deliberate
production design rather than a defect. `finance-research/src/strategies.rs:24-78` gives
`exness XAU/USD` a third strategy (`mtf_stochastic_5m_4h_sma5`) that `bybit XAUT` does not get;
`bybit XAUT`, `bybit BTC` and `binance XAU` run **only** the two base strategies. Production's
`finance-api/src/deployment_rules.rs:616-642` gates the live ensemble with the same three
predicates, so **research mirrors production** — the excluded routes are excluded on purpose
and documented in place. Identical prices fed to different ensembles produce different trades.

**But the ensemble does not order the whole matrix**: the base-2 `bybit XAUT`/`binance XAU` pair
correlates at +0.423, *below* the cross-ensemble `exness XAU`/`binance XAU` pair at +0.589. It
is a sufficient mechanism for the gold pair, not the only driver. See `round343-NO-CHANGE-exness-xau-gross-is-positive-across-four-windows-and-the-gold-decorrelation-is-a-deliberate-ensemble-difference.md`.

---

# Round 342 — NEEDS-MORE-RESEARCH: the two gold routes' **prices** correlate at **+0.996** and their Portfolio **PnL** at **+0.287**. The divergence Round 341 found is created by the Portfolio layer, not by the instruments. The fleet is now complete at six of six, and **`exness XAU` is the only route with positive gross at the deployed band.**

Classification: **NEEDS-MORE-RESEARCH** — a large, reproducible, unexplained property of the
Portfolio layer. Two bounded Docker sweeps (exactly the 2-container budget), one narrow
read-only production query, and **zero-container** analysis of six saved gate runs. **XAU-first.**

## The question Round 341 left open

Round 341 found `2026-06-10` was the **worst** day on `bybit XAUT` and the **best** day on
`exness XAU`, and closed with: *"divergence between tokenized XAUT and the XAU/USD CFD,
opposite Portfolio positioning, and different session coverage are all consistent with the
observation. **I queried no market data and inspected no positions.**"*

**Pre-registered as a partition:** let ρ_gold and ρ_BTC be the mean within-group daily-PnL
correlations.
- **ρ_gold < ρ_BTC − 0.20** → the gold routes do not co-move the way the BTC routes do;
- **ρ_gold ≥ ρ_BTC − 0.20** → they co-move comparably and 2026-06-10 was a one-day anomaly.

## Result — the prediction holds, and its natural reading is wrong

Completing the fleet gives all six routes' daily arrays. Within-group daily-PnL correlations:

| group | pairs | mean r |
|---|---|---|
| **BTC** | binance/exness +0.856, binance/bybit +0.715, exness/bybit +0.631 | **+0.734** |
| **gold** | exness XAU/bybit XAUT **+0.287**, exness XAU/binance XAU +0.589, bybit XAUT/binance XAU +0.423 | **+0.433** |

ρ_gold − ρ_BTC = **−0.301**, past the −0.20 line. **The prediction is confirmed.**

The obvious explanation would be that the gold routes track different things. **A narrow
read-only query of daily 5m closes refutes that.** Daily log-return correlations over
2026-05-20 → 2026-08-30:

| pair | price r | n |
|---|---|---|
| **`bybit XAUT` vs `exness XAU`** | **+0.996** | 86 |
| `binance BTC` vs `bybit XAUT` | +0.609 | 102 |
| `binance BTC` vs `exness XAU` | +0.595 | 86 |

**The two gold instruments are the same instrument for practical purposes — r = +0.996.** And
on the day in question both fell together: `XAUT` **−4.00%**, `XAU` **−4.23%**.

So on a −4% gold session, with prices moving as one, the Portfolio made **+0.2197** on the CFD
route and lost **−0.1694** on the spot route. **The inversion is produced by the Portfolio
layer's own per-route decisions, not by any difference in the underlying.**

That is the finding: **price correlation +0.996, PnL correlation +0.287.** The decision layer
discards roughly 70% of the co-movement that exists in the data it is fed.

I registered the right partition and would have drawn the wrong conclusion from it without the
price data. Recording that: a confirmed prediction is not a confirmed explanation.

## The fleet is complete — six of six

Both remaining routes, `--days 500`, deployed band:

| route | gate-eligible | trades/wk | **gross** | cost | net | Sharpe | streak |
|---|---|---|---|---|---|---|---|
| `exness XAU` @900 | no (7 intervals) | 6.85 | **+0.7820** | 1.1929 | −0.4110 | −0.860 | 5 |
| `bybit XAUT` @500 | yes | 4.48 | −0.0135 | 0.4069 | −0.4204 | −1.397 | 13 |
| **`binance XAU` @500** | **no** (53 observed days) | 5.07 | **−0.3442** | 0.2452 | −0.5893 | −4.280 | 6 |
| **`bybit BTC` @500** | **yes** | 12.11 | **−1.3153** | 1.4265 | −2.7417 | −5.057 | 8 |
| `binance BTC` @500 | yes | 21.84 | −1.7909 | 2.1498 | −3.9407 | −6.753 | 7 |
| `exness BTC` @500 | no (4 intervals) | 24.58 | −2.1476 | 2.4149 | −4.5624 | −7.510 | 6 |

**All six fail. At the deployed band, `exness XAU` is the only route with positive gross** —
the precise version of the claim Round 337 overstated and Round 338 corrected using *other*
bands on `bybit XAUT`.

Two notes on the new routes. `bybit BTC` is fully **gate-eligible** (no unverified gaps on any
interval, 101 observed days) and fails on performance, `gross_pnl_positive` included — a third
gate-eligible route, a third negative gross. `binance XAU` has clean continuity but its
`--days 500` request silently returned a **partial window**: holdout 2026-07-09 → 2026-08-30,
15,111 candles, **53 observed days** against the 90 threshold. Its data reaches 2026-08-30, so
the route is current; it is simply shallow. That is the documented `--days`-beyond-depth trap
behaving exactly as documented.

## What is proven, and what is not

Proven:

- Within-group mean daily-PnL correlation: BTC +0.734 (3 pairs), gold +0.433 (3 pairs); the
  `exness XAU`/`bybit XAUT` pair specifically is **+0.287** over 84 shared days.
- Daily close-to-close log-return correlation `bybit XAUT` vs `exness XAU` = **+0.996** (n=86);
  vs `binance BTC` +0.609 and +0.595.
- On 2026-06-10: XAUT −4.00%, XAU −4.23% in price; Portfolio PnL −0.1694 and +0.2197.
- `bybit BTC` @500: 173 trades, 12.110/week, gross −1.31526, cost 1.42647, net −2.74173,
  Sharpe −5.0571, Sortino −5.5505, streak 8, no unverified gaps, 101 observed days.
- `binance XAU` @500: partial window, 53 observed days, 38 trades, 5.070/week, gross −0.34416,
  cost 0.24518, net −0.58934, Sharpe −4.2804, no unverified gaps.
- At the deployed band, five of six routes have negative gross.

Not proven, and deliberately not claimed:

- **That BTC-route prices are less correlated than gold-route prices.** I queried only
  `binance BTC` among the BTC venues, so the within-BTC *price* correlation is **unmeasured**.
  The contrast that is established is within the gold pair alone: price +0.996 against PnL
  +0.287.
- **Why the Portfolio diverges on identical inputs.** Different interval weights from
  route-local Alpha performance, different entry timing, and different position direction are
  all consistent. **I inspected no positions and no per-route weights**, and the replay's
  weights refit per kline (Round 300), which is a known source of route-local state.
- That the PnL correlation is stable. **One window per route**, and Round 341 established that
  most quantities here move with the window.
- That low PnL correlation is a defect. Uncorrelated per-route PnL on a shared underlying is
  what a *diversifying* system would also look like — but here every route loses, so the
  decorrelation is spreading losses, not risk. Which of the two it is on a profitable route is
  untested.
- Any promotion. Six of six routes fail the gate; five of six lose money before costs.
