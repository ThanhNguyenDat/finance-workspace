# GATE VERDICT QUALIFIED (Round 335)

This file reports that the best configuration "still fails the gate" and attributes it to
performance checks. That attribution is **incomplete**. At `--days 500` on `exness XAU` the
gate **also** fails `minimum_holdout_days` (84 observed days against a threshold of 90 — a
CFD's closed weekends make 90 unreachable in this window) and `input_continuity_failed` on
**all seven** non-5m intervals. **No configuration of any kind can pass the gate on this
route at 500 days**, so this file's gate verdicts are not performance verdicts.

The **relative rankings** across bands on this common window are unaffected and stand. See
`round335-DATA-ISSUE-no-500-day-exness-xau-run-can-pass-the-gate-and-the-band-optimum-is-a-plateau-not-a-point.md`.

---

# COARSE-GRID ARTIFACT (Round 334)

The "interior optimum at 0.02/0.04" reported here is a **grid artifact**. Refining the
500-day grid between 0.01 and 0.02 — the interval this file never sampled — finds the best
net at **0.0125/0.025 (−0.0121)**, **2.5x better** than 0.02/0.04's −0.0301, at
**7.67 trades/week**. See
`round334-REJECTED-the-6-8-per-week-coincidence-dissolves-on-a-refined-grid-and-the-volatility-prediction-locates-the-band.md`.

---

# 500-DAY SPECIFIC (Round 331)

The interior optimum found here **does not survive a change of window**. Re-run at
`--days 900` (holdout 151 days, clearing the gate's own minimum), the ordering changes:
**the deployed 0.01/0.02 band has the best net (−0.4118)**, ahead of 0.02/0.04 (−0.4695)
and 0.04/0.08 (−0.7931). So "interior optimum at 0.02/0.04" is a **500-day** result, and
the lever's *shape* differs too — interior optimum at 500 days, monotone across the same
three points at 900.

What does replicate: **no configuration is profitable at either window** (6 of 6), the
widest band is worst at both, and widening destroys gross more sharply at depth
(+0.4460 → **−0.0207** for 0.04/0.08). Saturation was **not** re-tested at 900 days. See
`round331-REJECTED-the-band-optimum-moves-with-the-window-so-parameter-tuning-on-one-window-does-not-transfer.md`.

---

# Round 330 — REJECTED: widening the protective band **further makes it worse**. There is an **interior optimum at 0.02/0.04**, the lever **saturates** below 0.04, and **nothing across an 8.2x frequency range reaches break-even**.

Classification: **REJECTED** — my pre-registered expectation fails, and the protective-band
lever is closed as a route to profitability. Two bounded Docker sweeps (exactly the
2-container budget), **XAU-first**.

## The question Rounds 328-329 opened

Rounds 328-329 showed that raising frequency multiplies cost without creating edge, on
two routes. The obvious follow-up runs the lever the **other** way: `exness XAU`'s wide
band (0.02/0.04) reached net **−0.0301** and Sharpe **−0.096** — very close to
break-even. How far does that go?

**Pre-registered:** if cost is the only thing frequency multiplies, widening further
keeps improving net toward — and possibly past — zero, with gross roughly flat.
**Bounded or refuted** if gross falls more than 30% below the +0.60 level as the band
widens.

## The full lever

`exness XAU/USD`, `--days 500`, deployed costs, identical holdout:

| band | trades | tr/wk | pos-day | streak | Sortino | Sharpe | cost÷gross | gross | **net** |
|---|---|---|---|---|---|---|---|---|---|
| **0.08 / 0.16** | 86 | **6.11** | 0.429 | 5 | −0.725 | −0.445 | 1.31 | **+0.4460** | −0.1396 |
| **0.04 / 0.08** | 86 | **6.11** | 0.429 | 5 | −0.725 | −0.445 | 1.31 | **+0.4460** | −0.1396 |
| **0.02 / 0.04** | 96 | 6.82 | 0.417 | 5 | −0.155 | **−0.096** | **1.05** | +0.6067 | **−0.0301** |
| 0.01 / 0.02 (deployed) | 126 | 8.95 | 0.429 | 4 | −1.152 | −0.814 | 1.38 | +0.6000 | −0.2283 |
| ATR 1.5 / 3.0 | 703 | 49.94 | 0.095 | 16 | −14.802 | −23.225 | 7.25 | +0.6839 | −4.2751 |

### 1. The lever saturates

**`0.04/0.08` and `0.08/0.16` are identical in every field** — same 86 trades, same
6.11/week, same gross, net, Sharpe, streak and ratio, to the last decimal. At or below a
0.04 stop the protective band **stops binding altogether**; every close then comes from a
target change. So the lever has a **floor at 6.11 trades/week** and widening beyond 0.04
does literally nothing.

### 2. There is an interior optimum, and it is 0.02/0.04

Past it, widening **hurts**: gross falls **+0.6067 → +0.4460 (−26.5%)** while frequency
falls only 6.82 → 6.11 (**−10.4%**), so net worsens **4.6x** (−0.0301 → −0.1396).

That is the pre-registered expectation failing. Below the optimum the band is no longer
just removing cost — it is **giving up more gross than it saves**. A plausible reading is
that the take-profit at 0.04 was still capturing winners and at 0.08 it never triggers, so
winning trades ride until the target flips; I have no per-trade close-reason data and am
**not** asserting it.

### 3. Nothing reaches break-even

Across the **entire** lever — an **8.2x** frequency range from 6.11 to 49.94 trades per
week — the best net is **−0.0301**. **No configuration is profitable.** The
protective-band lever, taken to both of its limits, cannot make this route make money.

### 4. And the optimum still fails everything

At 0.02/0.04 the route trades **6.82/week — below the 7/week Target 3 bar** — and still
fails the gate on Sharpe (−0.096 against +1.0), positive-day ratio (0.417 against 0.55)
and cost÷gross (1.05 against 0.5). The best point on the lever meets **neither** Target 1
nor Target 3.

## A correction to my own criterion

I registered "bounded if gross falls more than 30% below +0.60". Gross fell **25.7%** —
just under it — so by the letter of my own rule the run was not "bounded", yet net clearly
worsened and the direction was clearly refuted.

**The criterion was mis-aimed.** I set the threshold on **gross** when the decisive
quantity was **net**, which is what the whole lever question is about. Recording that
rather than quietly reading the result off a different number than the one I registered.

## What is proven, and what is not

Proven:

- `exness XAU` at `--days 500`, identical holdout: 0.08/0.16 and 0.04/0.08 both give 86
  trades / 6.11 per week / gross +0.4460 / net −0.1396 / Sharpe −0.445 — identical in
  every reported field.
- 0.02/0.04 gives the best net (−0.0301), Sharpe (−0.096) and cost÷gross (1.05) of the
  five configurations.
- Gross falls 26.5% between 0.02/0.04 and the saturated bands while frequency falls
  10.4%; net worsens 4.6x.
- Across all five configurations, spanning 8.2x in trade rate, **no net is positive**.

Not proven, and deliberately not claimed:

- **Why gross falls at the wider bands.** The take-profit explanation fits but needs
  per-trade close reasons, which `one_target` and the gate do not report. Untested.
- That 0.02/0.04 is *the* optimum. It is the best of five points on a coarse grid;
  nothing between 0.01 and 0.04 was tested, and the true optimum could sit elsewhere in
  that range.
- That this holds on other routes or windows. One route, `--days 500` only. Round 329's
  `binance BTC` ladder was not extended downward, and Rounds 318-322 apply.
- That the optimum is promotable. It fails Target 3 **and** three gate checks; it loses
  less, which the promotion gate does not accept as an improvement. **No promotion.**
- Any change to the fleet conclusion. Every route still fails the gate, and the
  protective band is now shown to be unable to fix that on the one route where it was
  taken to both limits.
