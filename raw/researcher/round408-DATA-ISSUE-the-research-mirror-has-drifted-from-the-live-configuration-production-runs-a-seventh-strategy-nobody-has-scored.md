# Round 408 — DATA-ISSUE: the research mirror has **drifted** from the live configuration. Production runs a **seventh** strategy that appears nowhere in it, on two routes, confirmed in live payloads.

Classification: **DATA-ISSUE** — a concrete defect that narrows the scope of
several earlier rounds. **Zero containers**; narrow read-only production reads
plus code.

## The check that led here

Round 407 closed with the caveat that it had not verified the deployed binary
matches the source it read. Checking that produced two facts and then a third
that matters more.

**Deployment identity.** All six live-action containers run image tag
`finance-live-action_sha-7a15b76…`, i.e. commit **`7a15b76`**. `origin/main` is
`14afa8e` — one commit ahead, and that commit is *"ci: remove runner bootstrap
from delivery workflow"*, infrastructure-only, so production being one behind is
expected, not stale.

**Source agreement.** `production_candidates` is byte-identical between
`7a15b76` and my working HEAD, and so is
`deployment_rules::configured_extra_strategies`. Nothing here is a deploy-lag
artifact.

## The drift

`production_candidates` (in `crates/finance-research`) is called **only from the
research CLI** — `main.rs:617` and `:678`. **No live code calls it.** The live
binary is `finance-api`, and its strategy set comes from
`deployment_rules::configured_alpha_strategies` / `configured_extra_strategies`.

**Two separate definitions, and they have diverged:**

| route group | live (`finance-api`) | research mirror | |
|---|---|---|---|
| `exness XAU` | 3 | 3 | agree |
| `binance BTC`, `exness BTC` | **6** | **5** | **differ** |

The live-only strategy is **`mtf_stochastic_4h_1d_sma50`** — `k_period 14,
d_period 3, oversold 30, overbought 70, trend_period 50`, on base **4h** and
higher **1d**. It appears **zero times** in the research mirror.

**Confirmed in production data, not just code.** The live trade payloads'
`contributing_strategies` list six names on both BTC routes, including
`mtf_stochastic_4h_1d_sma50`, and three on `exness XAU`.

## What this narrows

- **Round 375's Alpha-input counts are wrong for BTC.** It recorded 5 / 5 / 3 /
  2 / 2 / 2 across the fleet; production is **6 / 6 / 3 / 2 / 2 / 2**. The
  input-count hypothesis that round tested was refuted anyway, so the conclusion
  survives — but on corrected numbers it was never testing what it thought.
- **Rounds 406 and 407's "coverage complete, six of six"** describe the research
  mirror. Production runs **seven** distinct configurations. The seventh is
  **unscored**.
- **Round 394's Alpha-to-Portfolio comparison** used `exness XAU`, where the two
  definitions agree, so it is unaffected.

## The seventh strategy is scoreable but has never been scored

Its core parameters match the sweep entry
`mtf_stochastic_14_3_30_70_sma50_trend_filtered`, which scored **+0.19411** on
`exness XAU` in round 406's family table — **but at the wrong intervals**. Every
MTF run in this arc used `--interval 5m --higher-timeframe-interval 4h`;
production runs this one at **4h/1d**. The name and the core parameters match
while the strategy does not.

**Round 407 predicted this failure mode one round before it appeared**, in the
caveat it wrote about CLI-supplied intervals. It then did not check whether any
deployed strategy actually used different intervals.

## What is proven, and what is not

Proven:

- All six live containers run image `sha-7a15b76`; `origin/main` is one
  infrastructure-only commit ahead.
- `production_candidates` and `configured_extra_strategies` are both identical
  between `7a15b76` and my HEAD.
- `production_candidates` has no caller outside the research CLI.
- `mtf_stochastic_4h_1d_sma50` is in the live configuration for both BTC routes
  and absent from the research mirror; live payloads list six contributing
  strategies on those routes.

Not proven, and deliberately not claimed:

- **That the drift changes any performance conclusion.** The seventh strategy is
  unmeasured at its real intervals; it could be anything. Nothing in rounds
  394–407 is retracted on performance grounds — what is narrowed is **scope**.
- That the mirror is wrong rather than deliberately reduced. There may be a
  reason the research crate omits a 4h/1d strategy from a 5m sweep; I did not
  find one in comments and did not assume one either way.
- That the two definitions agree on everything else. I compared the strategy
  sets; ordering, weights and any other deployment parameter were not compared.
- That six routes' live payloads were checked. Three were; the other three carry
  only the two generic candidates in the mirror and were not re-verified.

## Named next step

Score `mtf_stochastic_4h_1d_sma50` at **its own intervals** —
`--interval 4h --higher-timeframe-interval 1d` — on `binance BTC` and
`exness BTC`. That is the one production strategy never measured, it is
runnable today, and it is the only remaining backtest question that is not
blocked on the release decision, a Target 2 definition, or forward time.
