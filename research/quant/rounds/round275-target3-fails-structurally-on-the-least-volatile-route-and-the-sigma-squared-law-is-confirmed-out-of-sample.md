# QUALIFICATION (Round 276)

This file's pre-registered prediction hit to 2.8% — but Round 276 shows that success
was **partly luck**. σ² predicts *hold duration*, and frequency also carries an
**occupancy** term (Round 272's identity). `binance XAU` (63.5%) and `binance BTC`
(59.6%) happen to have similar occupancy, so that term nearly cancelled in this
file's pair.

Round 276's demanding test — three BTC routes with a 1.3% volatility spread — found
frequencies from **5.55 to 9.80/week (1.77x)**, firing its pre-registered refutation
criterion. **`bybit BTC` fails Target 3 at 5.55/week despite volatility identical to
the two passing routes**, so this file's reading that the failure is confined to
low-volatility instruments is wrong.

This file's measurements stand; the generalisation does not. See
`round276-QUALIFICATION-sigma-squared-governs-hold-not-frequency-and-bybit-btc-also-fails-target3.md`.

---

# Round 275 — Target 3 fails structurally on `binance XAU` (3.63/week), and Round 273's σ² law is confirmed by a pre-registered prediction to within 2.8%

Classification: **NEEDS-MORE-RESEARCH** — a specification conflict is established;
what to do about it is not a research question. Two bounded Docker sweeps (exactly
the 2-container budget).

## A prediction registered before the runs

Round 273's σ² law rested on four points and I said so. This round tests it the
right way: **the prediction was written to disk before either container was
launched** (`precommit_r275.md`, iteration 70).

> frequency ∝ σ². Measured 5m volatilities: binance BTC 0.14371%, binance XAU
> 0.09058%. So `one_target` frequency on binance XAU should be about
> **(0.09058/0.14371)² = 0.397x** binance BTC's. Refuted if the ratio falls outside
> 0.25-0.60.

Matched 260-day window (bounded by `binance XAU`'s history), deployed parameters
(fractional 0.01/0.02, `minimum_hold_decisions` 36), read from `one_target`.

| route | trades | **/week** | realized_pnl | pnl/trade | **Target 3** |
|---|---|---|---|---|---|
| **binance XAU/USDT** | 135 | **3.63** | −1.4331 | −0.01062 | **FAIL** |
| binance BTC/USDT | 350 | **9.42** | −3.3986 | −0.00971 | PASS |

**Predicted ratio 0.397; observed 0.386 — an error of 2.8%.**

That is an out-of-sample confirmation of the σ² law on an independent measurement
(Portfolio-level `one_target` frequency, not the ledger hold durations the law was
fitted to). Round 273's main weakness — "a law from four points" — is substantially
answered.

## The operational finding: the two targets are in mechanical conflict

Authoritative `one_target` frequencies under deployed parameters:

| route | /week | Target 3 (≥7) |
|---|---|---|
| binance BTC | 9.42 | passes comfortably |
| exness XAU | 7.06 (Round 274, 360d) | passes by **0.9%** |
| **binance XAU** | **3.63** | **fails by 48%** |

And the escape route is closed. Round 274 showed that narrowing the band raises
frequency **2.43x** while multiplying the loss **2.27x**, because the per-trade cost
is unchanged. So on `binance XAU`, reaching 7/week means roughly doubling the trade
count — and roughly doubling the loss.

**Target 1 (profitability / no prolonged loss) and Target 3 (≥7 trades/week) are
directly opposed on low-volatility instruments**, and the opposition is mechanical:
frequency scales as σ², per-trade cost does not scale at all, so frequency can only
be bought with proportional loss. On `binance XAU` the target set as specified is
not simultaneously satisfiable.

This is not a defect to fix. It is a **specification conflict**, now grounded in
measurement rather than argued.

## A correction to the "near-constant"

Per-trade cost across the four `one_target` measurements now available:
−0.00663, −0.00712 (exness XAU, Round 274), −0.00971 (binance BTC), −0.01062
(binance XAU). That is a **1.6x spread**, wider than the "±14%" earlier rounds
reported. Those earlier figures were **within one instrument across configurations**;
**across instruments the constant is noticeably less constant**, and I have been
quoting the tighter number in contexts that spanned instruments.

The qualitative result is untouched — cost per trade does not fall when frequency
rises — but "a near-constant −0.0068" should read "−0.0066 to −0.0106 depending on
route".

## What is proven, and what is not

Proven:

- The prediction and its refutation criteria were written to disk before launch.
- `one_target` under deployed parameters, matched 260-day window: binance XAU 135
  trades (3.63/week, −1.4331); binance BTC 350 (9.42/week, −3.3986).
- Observed frequency ratio 0.386 against a pre-registered 0.397.
- Per-trade cost spans −0.00663 to −0.01062 across four route/config measurements.

Not proven, and deliberately not claimed:

- **That `binance XAU` fails Target 3 in production.** This is a 260-day backtest.
  Round 259's live window gives [0.09, 20.30]/week and settles nothing.
- That the σ² law holds generally. One pre-registered prediction on one pair, plus
  Round 273's four fitted points. Two instruments of similar volatility would be a
  much weaker test than this pair, which was deliberately far apart.
- That no other lever could raise frequency without proportional loss. Only the
  protective band was tested (Round 274) and only on one instrument.
- That the target set should change. That is the user's call, not a research output,
  and no recommendation is made here.
- Anything about `bybit XAUT`, `exness BTC` or `bybit BTC` under `one_target`. Not
  measured.
