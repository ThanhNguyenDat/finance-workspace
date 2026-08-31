# CORRECTION (Round 368)

This file's premise that `binance BTC` was **"the route best placed to break"** the
profit/frequency incompatibility — because it was *"the only route that ever cleared
7 trades/week"* — was a statement about the **settings tested**, not about the route.
`exness XAU` had simply never been run below the deployed 0.01/0.02 band. At band
0.005/0.01, hold 36, it reaches **10.43 trades/week**, and at 0.0075/0.015 it reaches
**8.17** — both above the bar.

This file's **conclusion is unaffected and is now corroborated on a second route**:
both cells that clear the bar lose money, and `exness XAU`'s break-even frequency is
bounded at **3.83/week, 45% below the bar** — a wider shortfall than the 5.24/week
bound recorded here.

The "wider is better per trade" refutation in this file also stands, but understates
the problem: on `exness XAU` per-trade PnL is **non-monotone** in band
(-0.006080 / -0.004554 / -0.005824 / -0.002181 across 0.005 / 0.0075 / 0.01 / 0.02),
so the +62.5% widening improvement cited here is one step of a curve that turns twice.
See `round368-NEEDS-MORE-RESEARCH-exness-xau-does-reach-target-3-once-the-band-is-tightened-but-only-at-a-loss-and-the-band-curve-is-sharply-asymmetric-around-the-deployed-point.md`.

---

# Round 367 — REJECTED: on the route best placed to break it, **no (band, hold) setting is both profitable and at Target 3**. The two cells that clear 7.0/week lose **−4.75** and **−2.75**; the only profitable cell trades **2.80/week**. The break-even frequency is **at most 5.24/week — 25% below the bar.**

Classification: **REJECTED** — the hypothesis that some Portfolio-parameter setting satisfies both
Target 1 and Target 3 is refuted on the best-placed route within the tested grid. Two bounded
Docker sweeps (exactly the 2-container budget).

## The question Round 366 forced

Round 366 found six profitable configurations and six Target 3 failures, and the skill's rule
became: *before spending another round on a Portfolio-layer knob, check whether it can plausibly
raise PnL without cutting frequency.*

`binance BTC` is the route best placed to break that: it is the **only** route in the arc that
ever cleared 7.0/week (9.65 at deployed), and Round 366 showed the corner turns it positive at
2.80/week. So the frontier between those two points is where an answer lives.

**Pre-registered as a partition:** is there a tested configuration on `binance BTC` @500 that is
**both** PnL-positive **and** ≥ 7.0 trades/week?
- **Yes** → the profit/frequency incompatibility is broken and a real candidate exists;
- **No** → it holds on the route best placed to break it.

## Result — no

All six cells at `candle_count` **143,998**, one window:

| band | hold | trades | **trades/week** | `one_target` PnL | PnL/trade |
|---|---|---|---|---|---|
| 0.01/0.02 | 36 (deployed) | 689 | **9.65** ✓ | −4.74869 | −0.006892 |
| 0.01/0.02 | 72 | 517 | **7.24** ✓ | −2.74744 | −0.005314 |
| **0.02/0.04** | **36** | **481** | 6.73 | **−3.94375** | **−0.008199** |
| **0.02/0.04** | **72** | **374** | 5.24 | **−1.95771** | −0.005235 |
| 0.01/0.02 | 144 | 368 | 5.15 | −2.65041 | −0.007202 |
| 0.02/0.04 | 288 | 200 | 2.80 | **+0.37527** | +0.001876 |

**Two cells clear the bar; both lose heavily. One cell is profitable; it trades 2.80/week. The
registered answer is NO.**

## The sharper form: where break-even actually sits

The best negative cell is **−1.95771 at 5.24/week**; the only positive one is **+0.37527 at
2.80/week**. So the zero crossing lies in **(2.80, 5.24) trades per week** — **at most 5.24, which
is 25% below the 7.0 bar.**

That is stronger than Round 366's tally. It is not merely that the profitable configurations found
so far happen to be slow: **on this route the break-even frequency itself lies below the target**,
so no setting on this frontier can satisfy both objectives. Round 366's pattern now has a
quantitative boundary on the one route that had the most room.

## A route-specific inversion worth recording

Widening the band at hold 36 makes `binance BTC` **worse per trade** — −0.006892 → **−0.008199**,
a 19.0% degradation — while the identical widening on `exness XAU` (Round 364) **improved**
per-trade economics by **+62.5%**.

So the band's per-trade effect is **not universal in sign**. Round 364 refuted the "constant
per-trade" rule; this refutes the tempting replacement ("wider is better per trade"). Neither
generalisation survives, which is consistent with everything the arc has found about route
specificity.

The frontier is also **not monotone in frequency**: 6.73/week (−3.944) is worse than 7.24
(−2.747), and 5.15 (−2.650) is worse than 5.24 (−1.958). Frequency alone does not order PnL.

## What is proven, and what is not

Proven:

- The six-cell grid above, all at `candle_count` 143,998 on `binance BTC` @500.
- Two cells at or above 7.0/week, with PnL −4.74869 and −2.74744; one cell positive, at 2.80/week.
- Break-even lies in (2.80, 5.24) trades/week — at most 25% below the bar.
- Band widening at hold 36: `binance BTC` per-trade −0.006892 → −0.008199 (−19.0%), against
  `exness XAU`'s +62.5% for the same change.

Not proven, and deliberately not claimed:

- **That no setting anywhere satisfies both objectives.** Six cells, one route, one window,
  full-window `one_target`. Unsampled regions exist — holds between 72 and 288, bands between 0.02
  and 0.04, and every combination on the other five routes.
- That the break-even frequency is a route constant. It is bounded on this window only, and Rounds
  331/334/341 all showed such boundaries moving with the window.
- That the frontier's non-monotonicity is structural. The replay is deterministic (Round 351), so
  this is input sensitivity rather than noise, but no mechanism is offered.
- Anything about holdout behaviour. Unchanged and structural: hold-bearing configurations have no
  gate score, so promotion condition 1 stays unmeetable.
- Any promotion. The registered question answered **no**, which is the opposite of a candidate.
