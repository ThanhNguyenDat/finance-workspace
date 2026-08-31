# SIGN REFUTED ACROSS WINDOWS (Round 370)

The profitable corner recorded here (band 0.02/0.04, `minimum_hold_decisions` 288)
**flips sign at 900 days**. Measured on `exness XAU` at the same band and hold:

| window | `one_target` PnL | `legacy` control |
|---|---|---|
| 300 (this file) | **+1.17395** | - |
| 500 | **+0.79730** | -1.44608 |
| **900** | **-0.70835** | -2.25984 |

The corner beats the `legacy` control at **every** window, including the one where it
loses money - so the configuration does something real. What fails is the only thing
that made it interesting: **crossing zero**. Its positive PnL is a property of the
recent window, consistent with r241/r244 on this layer, not a property of the
configuration.

This file's measurement at 300 days stands, as does its caution that it was
full-window and in-sample. See
`round370-REJECTED-the-arcs-only-profitable-configuration-flips-sign-at-900-days-so-the-corner-is-a-recent-window-property-not-a-configuration-property.md`.

---

# THE PATTERN NOW HAS A QUANTITATIVE BOUNDARY (Round 367)

This file's tally — six profitable configurations, six Target 3 failures — is sharpened on
`binance BTC` @500, the route best placed to break it. Across six (band, hold) cells at
`candle_count` 143,998: the **two** cells clearing 7.0/week lose **−4.74869** and **−2.74744**, and
the **one** profitable cell trades **2.80/week**.

The best negative cell is **−1.95771 at 5.24/week**, so **break-even lies in (2.80, 5.24) trades
per week — at most 25% below the bar**. It is not merely that the profitable settings found so far
are slow: **on this route the break-even frequency itself sits below the target**. See
`round367-REJECTED-no-band-hold-setting-is-both-profitable-and-at-target-3-the-break-even-frequency-is-25-percent-below-the-bar.md`.

---

# Round 366 — NEEDS-MORE-RESEARCH: the profitable corner **transfers** — applied to `binance BTC`, a route it was never selected from, it turns **+0.37527**. And the arc-wide pattern is now unmistakable: **every profitable configuration ever measured fails Target 3**, the best of them at **4.57 trades/week** against a 7.0 bar.

Classification: **NEEDS-MORE-RESEARCH** — the overfitting null takes a real hit, and the joint
objective becomes the whole story. Two bounded Docker sweeps (exactly the 2-container budget),
**XAU-first**.

## The test Round 365 asked for

Round 365 named what would move its result: *"the same corner surviving on a route or window it
was not selected from."* The corner — **band 0.02/0.04 with hold 288** — came from `exness XAU`
alone, so applying it unchanged to two other routes is a genuinely fresh test.

**Pre-registered as a partition:** the corner turns `one_target` PnL **positive on at least one**
of `bybit XAUT` and `binance BTC` @500 → the direction survives a fresh test; **negative on both**
→ it does not transfer, consistent with overfitting to the route it was selected on.

**Validity:** all four runs report `candle_count` **143,998** — one window, and the deployed
baselines from Round 358 are directly comparable.

## Result — it transfers, on one of two

| route | config | trades | trades/week | `one_target` PnL | PnL/trade |
|---|---|---|---|---|---|
| `bybit XAUT` @500 | deployed | 247 | 3.46 | −1.57738 | −0.006386 |
| `bybit XAUT` @500 | **corner** | 108 | 1.51 | **−0.28493** | −0.002638 |
| `binance BTC` @500 | deployed | 689 | 9.65 | −4.74869 | −0.006892 |
| `binance BTC` @500 | **corner** | 200 | **2.80** | **+0.37527** | **+0.001876** |

**`binance BTC` turns positive. The registered branch fires.**

And the corner improves **all three** routes tested, by large margins:

| route | PnL | change | trades/week | Target 3 |
|---|---|---|---|---|
| `exness XAU` @300 | −1.57256 → **+1.17395** | **+174.7%** | 6.30 → 1.94 | fail → fail |
| `bybit XAUT` @500 | −1.57738 → −0.28493 | +81.9% | 3.46 → 1.51 | fail → fail |
| `binance BTC` @500 | −4.74869 → **+0.37527** | **+107.9%** | 9.65 → **2.80** | **PASS → fail** |

This is real evidence against "it is only an `exness XAU` window artefact". A parameter corner
found on one route improving three and turning two positive is not what a pure search artefact
usually does.

**But note what it did to `binance BTC`**: that was the **only** route in the entire arc clearing
the frequency bar (9.65/week), and the corner drops it to **2.80** — it buys profitability by
destroying the one thing that route had.

## The pattern that now decides the arc

Every profitable configuration this loop has ever measured, with its trade rate:

| configuration | trades/week | PnL | Target 3 |
|---|---|---|---|
| `exness XAU` @300 corner (Round 365) | **1.94** | +1.17395 | FAIL |
| `exness XAU` @300 `protective: none` (Round 346) | **1.44** | +0.40691 | FAIL |
| `binance BTC` @500 corner (this round) | **2.80** | +0.37527 | FAIL |
| `exness XAU` @1500 deployed, gate holdout (Round 352) | **2.81** | +0.22720 | FAIL |
| `exness XAU` @300 `--fee-bps 3.0` (Round 345, counterfactual) | 4.57 | +0.14423 | FAIL |
| `exness XAU` @300 `--slippage-bps 0` (Round 344, counterfactual) | 4.57 | +0.13146 | FAIL |

**Six profitable configurations, six Target 3 failures. The highest frequency among them is 4.57
per week against a 7.0 bar, and the two most profitable trade under 2 per week.**

That is no longer a coincidence across levers — it is the shape of the result. **At this
Portfolio's decision quality, profitability and the frequency target are incompatible everywhere
the arc has looked.** Every lever that improves PnL does it by trading less, and the profitable
region always sits below the bar.

That is a statement about the **decision stream**, not about any parameter: the decisions are not
good enough to survive being taken often. Improving them is an Alpha-layer problem, not a
Portfolio-construction one, and no Portfolio-layer knob tested in 60+ rounds has moved it.

## What is proven, and what is not

Proven:

- All four runs at `candle_count` 143,998; the Round 358 baselines are same-window comparable.
- `bybit XAUT` @500 corner: 108 trades, 1.51/week, −0.28493 (+81.9% against deployed).
- `binance BTC` @500 corner: 200 trades, **2.80/week**, **+0.37527** (+107.9% against deployed).
- The three-route improvement table and the six-configuration profitability/frequency table above.

Not proven, and deliberately not claimed:

- **That the corner is not overfitted.** It passed one fresh positivity test of two. Improving
  three routes is meaningful evidence, and it is **not** a holdout, which is what the promotion
  gate requires and what cannot be produced for any hold-bearing configuration.
- **That `binance BTC`'s positive `one_target` contradicts its negative gross** (Round 342). That
  gross figure is a **gate** measurement at the **deployed** band on a guard-free stream; the
  corner is a different configuration and **no gross measurement exists for it**.
- That the profit/frequency incompatibility is a law. It is six configurations across four levers
  on three routes, all full-window or nested-holdout — a strong pattern, not a proof, and no
  mechanism is offered for it.
- That the Alpha layer is the answer. That is where the argument points; nothing here tests it.
- Any promotion. Condition 1 remains structurally unmeetable for hold-bearing configurations, and
  every profitable configuration fails the joint objective by at least 1.5x.
