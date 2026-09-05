# Quant Research Loop Playbook

Use this as a searchable reference after reading the parent `SKILL.md`. Read
the required core sections there, then only the lessons relevant to this round.

One round of the recurring BTC/XAU trading-strategy research session. Each
round must produce a genuine improvement: a new validated candidate, a closed
(honestly falsified) candidate, a real bug found, a metric improvement, or a
shipped fix — never a no-op round.

## Read first

- `research/quant/index.md` — navigation doc, read before
  anything else each round. Lists closed directions (don't re-test), open
  leads, and infra gaps. Update it, don't recreate it, when a direction opens
  or closes.
- `openspec/changes/` and `.ops/changes/` — inspect active promoted engineering
  work and its execution evidence. `docs/archive/legacy-handoff-agent.md` is legacy history/
  index only and never owns task or lifecycle status.
- Load `repository-delivery` and `quant-pipeline-development` (finance-live-action)
  for the underlying commit/CI/Coolify mechanics this skill's dev-mode step 5
  drives — this skill adds the research/backtest/production-verification layer
  on top, it does not replace them.

## Round structure

1. **Determine the round number.** There is no launcher or background
   orchestrator tracking iterations — the round-file sequence under
   `research/quant/rounds/` is the sole source of truth. Find the highest
   existing `round<N>-*.md` file (or the latest `docs(research): round <N>`
   commit in `git log`) and use `N+1`.
2. **Research.** Read the backlog doc, decide the round's focus: extend an
   open lead, close a stale one with fresh data, or search for a genuinely
   new mechanism (Rule 2/3 of the standing `/loop` prompt: web search,
   ctx7, cross-timeframe/cross-broker combinations). Prefer mechanisms not
   yet in the closed-directions table.
3. **Backtest honestly** — see "Backtest tooling" below. Train/validation/
   holdout, every claim needs a number from this pipeline, not a guess.
4. **Verify production state** when the question is about live behavior
   (decision frequency, current weights, checkpoint health) rather than
   backtest performance — see "Production verification" below.
5. **Classify** the result as REJECTED, NO-CHANGE, DATA-ISSUE,
   NEEDS-MORE-RESEARCH, or PROMOTE. Only PROMOTE may enter OpenSpec.
6. **Promote, if actionable** — require defensible evidence, clear scope,
   acceptance criteria, risk/trading safety, and rollback; see "Promotion and
   Codex-down mode" below.
7. **Document** research evidence (see "Research evidence and promotion").
8. **Clean up**: remove temp files under `/tmp`, close the SSH tunnel, confirm
   `git status --short` is clean in both repos before ending the round. A
   clean local working tree is not sufficient proof of a synced evidence
   trail: round422/424/425 each caught a different local-vs-committed-vs-pushed
   drift mode (uncommitted rounds, a commit that vanished from the working
   tree, a commit that never reached the remote) on three consecutive rounds,
   each missed by a `git status --short`-only check. Before ending the round,
   `git fetch origin main -q && git rev-parse HEAD origin/main` and confirm
   both SHAs match; if they diverge, diagnose which side is stale (do not
   assume local is authoritative) before pushing or resetting.

## Backtest tooling

`finance-research` (finance-live-action) runs honest train/validation/holdout
splits against real production data through a read-only SSH tunnel — it is
the only source of truth for backtest numbers in this loop; never estimate or
fabricate one.

- Open the tunnel: `ssh -f -N -L 18086:localhost:8086 my` (background,
  read-only gRPC to Finance MW). Close it at the end of the round:
  `pkill -f "ssh -f -N -L 18086"` (a bash tool wrapper may report a nonzero
  exit code here even on success — verify with
  `ss -tlnp | grep 18086` instead of trusting the exit code).
- **Run it inside Docker, capped at 2-3 CPU cores** (standing user directive —
  never invoke the bare binary on the host):
  ```
  docker build -f docker/Dockerfile-research -t finance-research-local:latest .
  docker run --rm --cpus=2 --network host finance-research-local:latest \
    --endpoint http://127.0.0.1:18086 --broker <binance|exness> \
    --market-type <perpetual_future|cfd> --base-asset <BTC|XAU> \
    --quote-asset <USDT|USD> --interval 5m --days <N> --json
  ```
  `--network host` is required so the container can reach the tunnel on
  `127.0.0.1:18086`. Rebuild the image after any source change in
  `crates/finance-research` or its dependencies before trusting new results.
- **If a run needs to be bounded/killable, start it detached and stop it by
  name — never wrap a foreground `docker run` in `timeout`/`timeout --kill-after`.**
  `timeout ... docker run ...` (without `-d`) only kills the CLI/attach
  process; the container itself keeps running in the background and its gRPC
  connection to MW stays open. Round 124-125 (2026-08-24) confirmed this
  leaks `kline.KlineService/Stream`'s 1-slot concurrency gate (visible via
  `finance_mw_grpc_requests_in_flight` on `finance-mw-1:8002/metrics`) —
  each leaked container held the single slot or queued behind it, so repeated
  bounded attempts across rounds silently exhausted the gate and were
  misdiagnosed as production route contention before the real cause (leaked
  local containers) was found. Use
  `docker run -d --name finance-research-<label> --rm --cpus=2 --network host ...`
  then explicitly `docker logs -f <name>` to watch it and
  `docker kill <name> && docker rm -f <name>` to stop it — confirm with
  `docker ps -a --filter "ancestor=finance-research-local:latest"` that
  nothing is left running before ending the round.
- **`docker run -d ... > file.json` captures the printed container ID, not the
  command's output** (round 443) — `-d` makes `docker run` exit immediately
  after printing the new container's ID, so redirecting *that* invocation's
  stdout writes one 64-character hex string, not the `--json` payload. Always
  capture output with a separate `docker logs -f <name> > file.json
  2>file.err` after the container starts (works even after the container has
  already finished and self-removed via `--rm`, as long as `logs -f` is
  issued before that happens — for a fast research run, launch it immediately
  after the `docker run -d`). Bonus finding from doing this correctly:
  `finance-research`'s own ECS application logs (the "backtest candle count"
  etc. lines) go to **stderr**, and stdout carries **only** the pretty-printed
  `--json` result — so `file.json` needs no jsonl-log-stripping before
  `json.load()`, and `file.err` is where to look for the candle-count/window
  log lines if `--json`'s own fields don't cover something.
- **ML dependency spikes need an API smoke compile, not an empty crate build**
  (round 449). Use a disposable crate in the same Rust builder base as
  `Dockerfile-research`, cap it at the research CPU/RAM/swap limits, and compile
  a minimal `Dataset::new` → model `.fit(...)` path. Invoke the image with
  `bash -c`, not `bash -lc`: a login shell can omit the Rust image's Cargo path.
  Treat a successful dependency build as buildability evidence only; it is not
  market or train/validation/holdout evidence. Root-owned target artifacts from
  the disposable container must be removed through a narrowly scoped cleanup.
- **`--daily-profit-gate` does NOT model the deployed Portfolio construction** (round 356).
  `daily_profit_gate.rs:376-412` replays each decision through `ledger.on_kline` and nothing
  else: **no `PortfolioConstructionState::construct`, no `minimum_hold_decisions`, and no
  `PortfolioRiskLayer`** — so no 10 bps execution-cost gate either. By round 82's definition that
  is the **`legacy_selected_rule`** construction, not `one_target`. `main.rs:255-263` documents
  it, which is why `--portfolio-minimum-hold-decisions` **conflicts with** the gate flag — read
  that conflict as a statement about what the gate measures, not a CLI quirk.
  **Magnitude — `exness XAU` only**: guarded versus guard-free realized PnL differs by
  **0.44% / 3.83% / 1.94%** at @300 / @1500 / @1800 there. **It does not generalise** (round 358):
  at `--days 500` the same ratio is **41.2%** on `binance BTC` (−8.07260 → −4.74869, 30% fewer
  trades) and **19.8%** on `bybit XAUT`. **The gate therefore overstates losses on routes where
  the guard bites** — its BTC verdicts are pessimistic — and is nearly right on `exness XAU` only
  because there the guard changes trade count without changing PnL. Check the guard's bite on the
  route in hand before trusting a gate number.
  **And the guard is a tunable lever, not just an omission** (round 359).
  `--portfolio-minimum-hold-decisions` is a deployed production parameter (36) that had never been
  moved. At `--days 500`, **36 → 72** improves `one_target` PnL by **+42.1%** on `binance BTC`
  (−4.74869 → −2.74744) and **+20.9%** on `bybit XAUT` (−1.57738 → −1.24701), monotone across
  guard-free → 36 → 72 on both, and `binance BTC` **still clears Target 3 at 7.24/week** (from
  9.65) — the first lever in this arc to improve PnL materially without breaking frequency.
  Both routes still **lose**, `bybit XAUT` misses Target 3 at every hold, and `binance BTC`'s
  gross is negative (round 342), so a smaller loss there is not a route to profit.
  **It cannot be promoted, and the reason is structural**: the flag conflicts with
  `--daily-profit-gate` (because the gate does not model the guard), so **no holdout score exists
  for this parameter** and promotion condition 1 cannot be met. Do not weaken the gate to fit it —
  the unblocking step is a code change (gate accepts a hold value, or a holdout-restricted
  `one_target`). **The ladder saturates at 72** (round 360, verified same window at 143,998 candles
  for all three points): `binance BTC` 36 → 72 → 144 gives −4.74869 → −2.74744 → **−2.65041**, so
  the second doubling buys **3.5%** where the first bought 42.1%, and it drops the rate to
  **5.15/week — failing Target 3** that hold 72 cleared at 7.24. **Hold 72 is the joint-objective
  point among tested values.** `execution_cost` rejections fall 189 → 111 → 46 as the hold blocks
  reversals before the risk gate sees them.
- **Two runs from different rounds are NOT necessarily the same window — check `candle_count`**
  (round 360). Every run emits it in the first ECS line
  (`event.dataset: research.backtest_candle_count`); **comparison is valid only when it matches.**
  Measured: `exness XAU` @300 runs 3.5 hours apart gave **57,965** vs **57,925** candles, while
  same-day `binance BTC` and `bybit XAUT` @500 runs all gave **143,998** — session instruments
  drift, 24/7 crypto windows quantise, so **the drift is route-specific and must be checked, not
  assumed**.
  **`legacy_selected_rule` is a free drift control** whenever only Portfolio-construction
  parameters vary: it bypasses the construction guard, so it must be invariant to
  `--portfolio-minimum-hold-decisions` — any movement in it is drift. In the voided `exness XAU`
  transfer test it moved **0.306** against a treatment "effect" of **0.315**, which is what killed
  the comparison. **Run both arms of a comparison in the same round.**
  Done properly (round 361), the gate passes cleanly: two `exness XAU` @300 arms launched together
  reported **57,929 candles each** and a **byte-identical** `legacy` (345 trades, −1.633800). Make
  that gate explicit and **check it before reading the treatment**.
  Measured drift for scale: two `exness XAU` @300 hold-36 runs four hours apart differ by
  **36 candles and 0.25040 of PnL — 18.9% of the scale**; 24/7 routes drifted **zero** over
  similar gaps.
- **The hold lever works on every route tested, and only one keeps Target 3** (round 361, all
  pairs same-window verified): `exness XAU` @300 **+36.0%** (6.30 → 5.34/week, fail → fail),
  `bybit XAUT` @500 +20.9% (3.46 → 3.01, fail → fail), `binance BTC` @500 **+42.1%**
  (9.65 → **7.24**, pass → pass). **On two of three it buys PnL with frequency the route could not
  spare**, and `binance BTC`'s gross is negative — so a smaller loss there is not a route to
  profit.
  **A missing level effect does not mean a parameter has no leverage**: round 358 measured
  guard-at-36 versus guard-free on `exness XAU` at **0.44%** and that was wrongly read as
  insensitivity — the *next* 36 decisions of hold are worth **36%** there. Test the parameter, not
  its presence.
  **Saturation is route-specific** (round 362): the 72 → 144 step buys only **3.5%** on
  `binance BTC` but **+30.3%** on `exness XAU` (−1.00705 → **−0.70183**, 164 trades), for
  **+55.4%** cumulatively from hold 36. Do not generalise a ladder's shape across routes — and do
  not extrapolate past the last tested point, since `binance BTC` looked monotone at 72 and was
  nearly flat by 144.
  The cost is always frequency: `exness XAU` goes 6.30 → 5.34 → **3.83 per week** (−39%) on a
  route already failing Target 3 at every hold. **Whether the gain is added edge or removed cost
  is not decomposable** — the plain path reports net only, and zeroing costs to expose gross
  crosses the 10 bps reversal gate and changes the action space (round 348), the same block as
  round 354's gross-by-weekday question.
  **Drift is not proportional to the window shift** (round 362): a **4-candle** shift reproduced
  `exness XAU` hold-72 *exactly* (−1.00705, 229 trades) while round 361's **36-candle** shift moved
  PnL 18.9%. That is an argument for checking `candle_count`, **not** a licence to compare across
  rounds.
- **The hold direction is CLOSED as a candidate — its endpoint is no activity, not profit**
  (round 363). Full `exness XAU` @300 ladder: hold **36 / 72 / 144 / 288** → **−1.57256 /
  −1.00705 / −0.70183 / −0.32723** at **270 / 229 / 164 / 108** trades, i.e. **6.30 → 2.52 per
  week**. Cumulatively the loss shrinks **79.2%** while trades fall **60.0%**, per-trade loss is
  still **−0.003030** at the deepest point, and Target 3 goes from a near miss to a **2.8x** miss.
  `binance BTC`, the one route that kept the bar at 72, **saturates**. Extending a hold
  indefinitely drives PnL to zero from below — arithmetic, not a strategy.
- **But the mechanism is real and worth keeping: the guard improves trade *quality*, not only
  count.** Net PnL **per trade** goes −0.005824 → −0.004398 → −0.004279 → **−0.003030** (+48%
  overall), while **funding cost per trade rises** with hold (−0.000354 at 36 → −0.000409 at 144).
  Cost moving *against* the improvement means per-trade **gross** improved by more than net shows
  — the first mechanism in this arc that touches edge rather than cost. **Use net-per-trade plus
  `funding_paid` to separate "fewer trades" from "better trades"** when the gross/cost split is
  otherwise unobtainable.
  The per-trade series is **lumpy** (+24.5%, +2.7%, +29.2%): a flat step is not evidence the
  quality effect has stopped.
- **"Loss ≈ trade count × a near-constant" is NOT a general rule** (round 364). It came from round
  274's **ATR** band A/B (per-trade ratio 0.93x) and fails on the **fractional** band: on a
  same-window test (`candle_count` 57,934 both), `exness XAU` @300 hold 36 going 0.01/0.02 →
  0.02/0.04 gives per-trade **−0.005824 → −0.002181 (0.37x, +62.5% better)** while **funding per
  trade rises 47%**. The 74.2% PnL gain decomposes as −31.1% trades and **+62.5% per trade** —
  **quality, not count**.
  **Two levers that cut trades equally can do opposite things to what remains**: at nearly the same
  −30% trade reduction, the hold step moved per-trade **+2.7%** and the band step **+62.6%**.
  Always decompose before calling something a frequency lever.
  Caveat on controls: `legacy_selected_rule` is a free drift control **only** for
  Portfolio-construction parameters. **The band changes the ungated ledger too** (345 → 214
  trades), so band comparisons rely on `candle_count` alone.
  This does **not** reopen the band on its own: still a loss at hold 36, Target 3 gets worse
  (6.30 → 4.34/week), and it is full-window `one_target` while rounds 330-341 closed the band on
  **holdout** gate runs — whose direction it agrees with anyway.
- **NEVER test one lever with the other pinned at its deployed value** (round 365). The band and
  hold levers are **distinct and compose super-additively**, and the interaction **crosses zero**:
  on `exness XAU` @300 (all cells at `candle_count` 57,934), the band's per-trade effect is
  **+62.5%** at hold 36 but **+566.8%** at hold 288, and `band 0.02/0.04 + hold 288` gives
  `one_target` **+1.17395** on 83 trades (**+0.014144 per trade**) — the **first positive
  full-window PnL at deployed costs** in this arc, with funding per trade *worse*, so not cost
  removal. Round 363 closed the hold direction after testing it only at the deployed band; that
  closure's reasoning held for that band and was the wrong experiment.
  **Treat it as a searched corner, not a candidate.** It trades **1.94/week against a 7.0 bar (a
  3.6x miss, 83 trades where Target 3 needs ~300)**, has **no holdout score and cannot have one**
  (the hold flag conflicts with the gate, so promotion condition 1 is unmeetable), and sits in a
  **~16-cell search on one window** — which is exactly what overfitting produces. What would move
  it: a holdout score for the combined configuration (needs a code change) and the same corner
  surviving on a route or window it was **not** selected from.
  **The transfer test was run** (round 366, all runs at `candle_count` 143,998): applied unchanged
  to routes it was never selected from, the corner turns `binance BTC` @500 **+0.37527** (200
  trades) and improves `bybit XAUT` @500 **+81.9%** to −0.28493. It improves **all three** routes
  (+174.7% / +81.9% / +107.9%) and turns **two** positive — meaningful evidence against a pure
  `exness XAU` artefact, though still **not a holdout**. Note what it cost: `binance BTC` was the
  **only** route in the arc clearing the frequency bar and the corner took it from **9.65 to 2.80
  trades/week**.
- **EVERY profitable configuration this loop has ever measured fails Target 3** (round 366) —
  `exness XAU` corner **1.94/wk** (+1.17395), `protective: none` **1.44** (+0.40691),
  `binance BTC` corner **2.80** (+0.37527), `exness XAU` @1500 gate holdout **2.81** (+0.22720),
  `--fee-bps 3.0` **4.57** (+0.14423), `--slippage-bps 0` **4.57** (+0.13146). **Six for six, best
  at 4.57 against a 7.0 bar, the two most profitable under 2/week.**
  Across four levers and three routes, **every** PnL improvement comes from trading less and the
  profitable region always sits below the bar. Read that as a statement about the **decision
  stream** — the decisions are not good enough to survive being taken often — which points at the
  **Alpha layer**, not Portfolio construction. **Before spending another round on a
  Portfolio-layer knob, check whether it can plausibly raise PnL *without* cutting frequency; none
  tested in 60+ rounds has.**
  **The boundary is now quantified on the best-placed route** (round 367). `binance BTC` @500,
  six (band, hold) cells at `candle_count` 143,998: the **two** cells clearing 7.0/week lose
  **−4.74869** (0.01/0.02, hold 36) and **−2.74744** (0.01/0.02, hold 72); the **one** profitable
  cell trades **2.80/week**. Best negative is **−1.95771 at 5.24/week**, so **break-even lies in
  (2.80, 5.24) per week — at most 25% below the bar**. On the only route that ever cleared the
  bar, **the break-even frequency itself sits under it**.
  Two further cautions from that grid: **"wider is better per trade" does not generalise** — the
  same widening that gained `exness XAU` **+62.5%** per trade costs `binance BTC` **−19.0%**
  (−0.006892 → −0.008199), so the band's per-trade effect is not universal in sign; and the
  frontier is **not monotone in frequency** (6.73/week is worse than 7.24; 5.15 worse than 5.24),
  so frequency alone does not order PnL.
  **Trade count does not**: the guard removes **21.1%** of trades at @300 (~3% at the deep
  windows), so every gate `trades_per_week` is an **upper bound** on the deployed rate — against
  a 7.0 threshold, the deployed stream is *further* from passing than the gate suggests.
  **Consequence for attribution**: a `--daily-profit-gate` run cannot exhibit the reversal gate,
  so the round-348 threshold explanation applies **only** to plain `--json` (`one_target`) runs —
  rounds 349/350 — and **not** to the gate runs of rounds 344/345, whose fee response is the
  cost-feedback path alone.
- `--daily-profit-gate` evaluates the deployed *decision policy* on holdout only
  (Sharpe/Sortino/streak/frequency) — it does not let you pick an arbitrary
  **Alpha strategy** candidate (`--gate-strategy` was removed at round 55).
  **It does, however, respect every `--portfolio-*` flag** (sizing mode/value,
  protective kind/stop/take/atr-periods, minimum-hold-decisions) exactly like
  `one_target` does, because both read the same `selected_portfolio_rule`
  built from those flags (`main.rs`'s gate branch calls
  `evaluate_real_portfolio_with_funding_and_continuity_and_hold` with
  `selected_portfolio_rule.simulation` directly) — this is how round
  80/83/356-367/427-431/439 all got real holdout Sharpe/Sortino for a
  non-deployed Portfolio-layer configuration (a different hold/band/sizing
  value or mode than what's live). Do not read "can't pick a candidate" as
  "can't change the Portfolio config" — they are different axes. The plain
  sweep table (no gate flag, optionally with `--higher-timeframe-interval
  <interval>` to include MTF trend-filtered candidates) scores arbitrary
  **Alpha strategy** candidates on PF/win-rate only. There is no tool to get
  extended metrics (Sharpe/Sortino/streak) for an arbitrary Alpha candidate —
  don't invent one; report PF/win-rate honestly and say so if extended
  metrics are unavailable.
- **Diagnostic for "is a sizing-mode difference real or just a scale
  effect": check `cost_to_gross_pnl_ratio` invariance** (round 439). Fees,
  slippage, and funding all scale with notional the same way PnL does, so a
  pure uniform rescaling (e.g. `fixed_notional 5.0` vs `equity_fraction
  0.10`, ~200x different notional at $10k starting equity) leaves
  `cost_to_gross_pnl_ratio` essentially unchanged even though every raw PnL
  number moves ~200x — confirmed empirically (1.702 vs 1.710). A sizing mode
  whose *per-trade* size varies independently of a uniform scale (e.g.
  `VolatilityScaled`, which sizes each trade by its own realized-volatility
  reading) breaking that invariance — round 439 saw `cost_to_gross_pnl_ratio`
  jump 4.6x (1.710 → 7.811) at the *same* base `target_fraction` as the
  `equity_fraction` control — is evidence the mechanism is reallocating size
  per-trade in a way correlated (positively or negatively) with each trade's
  own edge/cost profile, not merely a calibration/scale question. Run the
  uniform-rescaling pair as a control in the same round before concluding a
  new sizing mode's cost-ratio shift means anything mechanistic.
- The `portfolio_execution` block in `--json` output carries several parallel
  Portfolio-level measurements with different fidelity — verified by reading
  `portfolio_measurement.rs::compare_real_portfolio_with_funding` directly
  (round 82): only **`one_target`** actually applies
  `--portfolio-minimum-hold-decisions` (via `PortfolioConstructionState::construct`).
  `legacy_grid`, `legacy_selected_rule`, and every entry in `capital_reports`
  (including the `fixed-atr`/`compounding-atr` protective-stop comparison)
  feed the raw decision stream directly, bypassing that guard entirely —
  confirmed empirically (identical output whether `--portfolio-minimum-hold-decisions`
  is 12 or 100). Only trust `one_target` for any conclusion involving the
  current hold-period configuration; treat `legacy_*`/`capital_reports` as a
  separate, hold-period-agnostic comparison that can silently mislead if
  read as if it reflected current production Portfolio-construction settings.
  `--portfolio-protective-kind`/`--portfolio-stop-value`/`--portfolio-take-value`/
  `--portfolio-atr-periods` correctly flow into `one_target` too, so use
  those flags (not `capital_reports`) to compare protective-stop mechanisms
  under the real current configuration.
- `one_target` measures the **whole `--days` window**, not a split
  (`main.rs` loads the full `portfolio_series` and
  `portfolio_measurement.rs` replays it end to end). Nested `--days N` runs
  therefore all end at the same "now", which makes **differencing consecutive
  cumulative trade counts** a legitimate way to get per-period rates without
  extra runs. Two caveats that have bitten: runs from *different rounds* end
  at different "now"s, so a slice differenced across rounds carries that
  drift — and **differencing amplifies it**: a 3% shift in a cumulative count
  produced a 37% shift in a 19-trade slice (round 298), so always measure the
  two windows bounding a slice **in the same round** before trusting a small
  slice's magnitude. Cross-check a slice's candle count against Timescale;
  the two agree exactly when the window is sound. Before spending a container
  on a deep window, **check the instrument's actual 5m history depth** — a
  `--days` value beyond available data silently yields a partial window
  rather than an error.
- **Only `one_target` and `legacy_selected_rule` may be differenced across
  windows.** Both carry `ledgers: 1` under `fixed_notional` sizing, are
  equity-path-independent, and are monotone in `--days`. `legacy_grid`
  (`ledgers: 4`, including `compounding-pct`/`compounding-atr`) and
  `risk_rejected_counts` are **not** — their cumulative counts *decrease* at
  some window lengths, because a longer window starts earlier and the
  compounded equity path differs. A decrease is the tell; check monotonicity
  before differencing any counter.
- `legacy_selected_rule` is the **guard-free twin** of `one_target`: same rule,
  same decision stream, `minimum_hold_decisions` bypassed. Verify with
  `trade_reduction_fraction == 1 - one_target/legacy_selected_rule` (it holds
  exactly), then use the pair to test whether any effect is caused by the hold
  guard or lies upstream of Portfolio construction. Note the guard is
  **stateful** (`decisions_since_target_change` carries forward), so
  differencing `one_target` alone carries a state-carryover confound that the
  guard-free measure does not.
- **Nested differencing is INVALID for Portfolio-layer counters.** The
  candidate *set* is static (`strategies::production_candidates(&instrument)`
  takes only the instrument identity), but the **weights over it are not**:
  `portfolio_decision_replay.rs:317` calls
  `evidence.reweight_from_alpha_performance(&alpha_performance(&ledgers))`
  **on every kline**, from ledger performance accumulated since the window
  start. Two runs of different `--days` therefore hold different weights at
  every bar they share, so a 540d−360d difference is **not** "what happened in
  `[360,540]`". The tell was already in the data: `legacy_grid.trades` and
  `risk_rejected_counts.execution_cost` both *decrease* from 360d to 540d,
  which nesting forbids. There is no way around this with the current CLI —
  equal-length windows at different end dates would work, but there is **no
  as-of/end-date flag**. Treat within-route Portfolio time comparison as **not
  currently measurable**, and never build a claim on differenced Portfolio
  slice rates. **Measure the noise before believing any window comparison**:
  re-run the same route at `--days N` and `--days N+1`. One extra day is worth
  a fraction of a trade, so whatever the count actually moves by is the
  method's noise floor. On `exness XAU` (round 301) that was **−7 trades for
  one day** and a 25-trade spread across N=360/361/365 — 6.7% of the
  cumulative count — which swallowed a 19-trade "anomaly" that three rounds
  had been spent explaining. A *negative* move is the unambiguous tell.
  **The magnitude is route-dependent**: the same test on `binance BTC` moved the
  rate only **+1.04%** (round 302), and that route's recorded ladder reproduced
  exactly (350 measured against 350.1 implied). So run the perturbation on the
  route you are about to make a claim about — do not assume one route's floor
  transfers to another.
- **A fixed-`--days` A/B is the one comparison the round-300 confound leaves clean** —
  use it for any parameter question, and prefer it over anything that varies the window.
  **But its conclusions do not transfer to another window.** `bybit XAUT`'s two measures
  agree positive at 360 days and *disagree* at 250 (round 318), so a route's raw-edge
  sign — and whether the measures agree on it — is **not window-independent**. Scope
  every cost-ablation statement to the window it was measured at, and when a comparison
  needs a route that cannot reach your window, **run a matched-window control first**:
  re-measure a route whose sign you already know, and treat a control failure as
  inconclusive rather than reading the target cell on its own.
  **The instability is concentrated in the near-zero cells.** `exness XAU` is positive
  on both measures at 250, 360 *and* 500 days (round 319), and across all nine
  zero-cost cells measured, **0 of 3 with `|one_target| ≥ 1.0` disagree between measures
  against 2 of 6 below 1.0** — large magnitude has always come with agreement, small
  magnitude is a coin flip. So a strong cell's *sign* can be trusted across that range;
  a marginal one's cannot. **The magnitude is never window-robust**: `exness XAU`'s
  per-trade edge swings 1.97x (0.00281-0.00553) across those same windows, which moves
  the edge-to-cost ratio from 30% to 59% — so quote a **range** (30-60%, needing a
  41-70% cost cut), never the single-window figure.
  **Measure-agreement does NOT imply window-stability — they are independent.**
  `binance BTC` agrees between measures at both 360 and 500 days and still **flips
  sign** (−0.4432 → +1.7176, −0.00093 → +0.00334 per trade), which makes the
  "perpetuals are negative" rule of rounds 316-317 a **360-day artifact** (round 320).
  Of three routes tested across windows only **`exness XAU`** is usable (sign and
  measures stable 3/3); `bybit XAUT` disagrees at 2 of 3; `binance BTC` flips. **Before
  building anything on a cost-ablation cell, re-measure it at two more windows** — and
  treat a single-window route-level claim as unverified until you have.
  **`exness XAU` is the one cell that has passed that bar**: positive on both measures at
  **250, 360, 500, 700 and 900 days** — ten of ten values, agreeing throughout (round
  321). Its per-trade edge still spans **2.27x** across those windows, so the
  edge-to-cost ratio runs **26-59%** (a **41-74%** cost cut to break even) with the two
  **deepest** windows giving the two lowest ratios. Quote that range, not a point, and
  do not extend the stability to any other route.
  **Never reuse one window's cost-per-trade at another, and read `edge ÷ cost` as a
  contaminated ratio.** Measuring the deployed arm at 700 and 900 days (round 322) gave
  30.1% / 43.7% / 24.3% at 360/700/900 against estimates of 30.1% / 29.6% / 26.0% — a
  **32% error** at 700d. The reason is that `cost/trade = gross/tr − net/tr` differences
  **two averages over different trade populations**: the deployed arm trades **4.3% /
  21.1% / 43.5%** less than the zero-cost arm as the window deepens, so the denominator
  absorbs a *selection* change, not just a cost. The `execution_cost` rejection counts
  (181 / 236 / 120) do **not** track that reduction, so the rest of the path is
  unidentified. Always run both cost arms at the same window before quoting a ratio.
  **Round 323 closed that gap by differencing every counter, with no new runs:**
  `decision_count` is *identical* between arms at every window, `execution_cost` is the
  only non-zero risk bucket in either arm, and the guard-free measure loses *more*
  trades than `one_target` — so the loss is upstream of the hold guard and, by
  elimination (cost enters only the PnL arithmetic and the cost gate; `fixed_notional`
  sizing and an entry-price protective band are both cost-insensitive), **the cost gate
  is the only path**. What varies is **trades lost per rejection: 0.055 / 0.636 /
  3.242** at 360/700/900 days — a 59x swing — while the rejection count is not monotone.
  Before hunting a "missing mechanism", difference the counters you already have.
- **`--daily-profit-gate` is the joint-objective instrument** — the only way to get
  Sharpe, Sortino, positive-day ratio, streak, drawdown and cost-to-gross for the
  deployed policy. It scores **holdout only**, cannot take an arbitrary candidate, and
  **conflicts with `--portfolio-minimum-hold-decisions`** (omit that flag). Exit code 2
  means the gate failed, not that the run failed — capture stdout either way. On
  `exness XAU` it fails six checks at both 360 and 900 days: Sharpe **−2.33 / −0.86**,
  Sortino −3.10 / −1.18, positive-day ratio 0.42 / 0.40, cost÷gross 9.89 / 1.53 (round
  324). Two things to know when reading it: `gross_pnl_before_costs` is **positive** at
  both windows, independently confirming the cost-ablation result through a different
  code path; and the **drawdown and streak checks pass trivially** because
  `fixed_notional` deploys ~5 units against 10,000 equity, so only the ratio,
  day-quality and cost checks discriminate.
- **SQN is not measurable with this tool.** The gate's `unavailable_metrics` names
  `system_quality_number` (needs per-trade R-multiples), `information_ratio` (needs a
  benchmark) and `maximum_consecutive_losing_trades` (needs retained per-trade
  outcomes). Report them as unavailable rather than substituting a proxy.
- **The gate is the arc's one window-proof instrument** — each scorecard is computed on
  its own holdout, so cross-route statements from it involve no differencing. Run it at
  a `--days` that gives a **≥90-day holdout** (the gate's own `minimum_holdout_days`;
  360d gives only 60) and use the **same `--days` across routes** so holdouts match.
  Across four route-windows (round 325) **Sharpe and Sortino are negative on 4/4**,
  positive-day ratio is below 0.55 on 4/4, and cost÷gross exceeds 0.5 on 4/4.
  `maximum_negative_day_streak` is the "no prolonged loss" objective: 4 / 5 on
  `exness XAU`, **14** on `bybit XAUT`, **7** on `binance BTC` against a limit of 5.
- **`gross_pnl_before_costs` is holdout-only** — do not read it against a whole-window
  `one_target` zero-cost figure. `bybit XAUT` and `binance BTC` are **positive over the
  full 500-day window and negative on its last ~101 days**; both are correct, and the
  difference is **period**, not measurement. `exness XAU` is the only route positive
  before costs on every measurement taken — including on a **matched holdout** (all four
  routes gated at `--days 500`, holdout starting 2026-05-22): `exness XAU` **+0.6000**
  against `bybit XAUT` −0.0135, `binance BTC` −1.7909 and `exness BTC` −2.1633
  (round 326). Note gold CFD does not trade weekends, so its holdout is 84 days against
  101 for the others even at the same `--days` — start dates match, lengths cannot.
- **A frequency-versus-risk tension worth watching, not yet a finding**: on that matched
  holdout the two routes above 20 trades/week have Sharpe near **−7** and the two below
  9 near **−1** — Spearman(trades/week, Sharpe) = **−0.80**, exact two-sided **p = 0.33**
  on n=4, so **not significant**. It points the opposite way to Target 3, and round 274's
  ATR-band lever (2.43x trades for 2.27x loss) agrees in direction by an independent
  method. Do not treat raising trade frequency as free. With the fleet complete
  (five matched routes, round 327) it strengthens to **ρ = −0.900, exact two-sided
  p = 0.0833** — one adjacent swap from a perfect ordering, still **not significant**.
  **Round 328 settled the direction within a single route.** Same route, window and
  holdout, only the protective band changed: wide fractional 0.02/0.04 → 6.82 trades/wk,
  Sharpe **−0.096**, net **−0.0301**; deployed 0.01/0.02 → 8.95, −0.814, −0.2283; ATR
  1.5/3.0 → 49.94, **−23.225**, **−4.2751**. Across that **7.32x** frequency range
  `gross_pnl_before_costs` moves only **12.7%** (+0.6067 / +0.6000 / +0.6839) while
  cost÷gross rises **6.9x** and net loss **142x**. **The frequency lever does not create
  edge; it multiplies cost** — cost scales with trade count, gross does not. Treat any
  proposal to raise trade frequency as a cost multiplier until shown otherwise.
  Note the conflict this exposes: on that route the configuration **nearest break-even
  misses Target 3** (6.82 against the 7/week bar) and meeting the bar costs **7.6x the
  net loss**. A lower-frequency band that merely *loses less* while still failing Sharpe,
  positive-day ratio and cost÷gross is **not** a promotable improvement.
  **It replicates.** The identical ladder on `binance BTC` (round 329) gives 15.26 /
  21.84 / 82.32 trades per week with Sharpe **−5.730 / −6.753 / −18.871** — both
  orderings hold again, and gross moves only **+35.8%** across a 5.39x frequency range.
  Direction and mechanism replicate; **magnitude does not** — net loss worsens 142x on
  `exness XAU` against 2.7x here, because each route starts a different distance from
  break-even. Quote the mechanism, never the multiplier.
- **`cost ÷ gross` is meaningless when gross is negative.** On `binance BTC` all three
  bands have negative gross, so its 0.76 / 1.20 / 6.46 cannot be read as "cost is X times
  gross profit" and is not comparable to a positive-gross route's. Use
  `gross_pnl_positive` there instead, and only the ratio's direction.
  Likewise **`maximum_negative_day_streak` does not track frequency** — 5/4/16 on
  `exness XAU` and 10/7/27 on `binance BTC`, with the *deployed* band shortest in both.
  Do not fold it into the frequency story.
- **The protective-band lever is closed, and it saturates.** Running it the *other* way
  on `exness XAU` @500 (round 330): 0.04/0.08 and 0.08/0.16 are **identical in every
  field** — at a stop of 0.04 or wider the band stops binding at all, so the lever has a
  **floor at 6.11 trades/week**. There is an **interior optimum at 0.02/0.04** (net
  −0.0301, Sharpe −0.096, cost÷gross 1.05); widening past it costs **26.5% of gross** for
  only 10.4% less frequency and makes net **4.6x worse**. Across the whole lever — an
  **8.2x** frequency range — **no configuration reaches break-even**, and the optimum
  still misses Target 3 (6.82/week) and fails three gate checks. Do not re-run this lever
  expecting a different answer.
  **But that optimum is 500-day specific.** At `--days 900` (holdout 151 days, clearing
  the gate's minimum) the ordering flips: **the deployed 0.01/0.02 band has the best net**
  (−0.4118) ahead of 0.02/0.04 (−0.4695) and 0.04/0.08 (−0.7931), and the shape is
  monotone rather than an interior optimum (round 331). **The optimal parameter setting is
  itself window-fragile — a tuning result on one window does not transfer, even on the
  same route.** What replicates across both windows: no configuration is profitable
  (6 of 6), the widest band is worst, and widening destroys gross more sharply at depth
  (+0.4460 → **−0.0207** for 0.04/0.08).
  **Completing the 900-day ladder settles it (round 332):** tightening past the deployed
  band is clearly worse (−0.4118 → −1.1279 → −1.6051 at 6.85 / 9.45 / 13.78 per week), so
  the curve is **unimodal with its peak at the deployed setting** — on this lever, at this
  window, **production is not misconfigured**. And the two optima line up on *frequency*
  even though the bands differ: **6.82/week at 500 days, 6.85/week at 900** — within 0.4%.
  Read the lever in trades/week, not in band values; the band-to-frequency mapping moves
  with the window. Both optima sit **just below** the 7/week Target 3 bar.
  Note net and Sharpe can disagree by one ladder step (at 900 days net peaks at 6.85/week,
  Sharpe at 5.04) — on a joint objective, say which metric you optimised.
  **Why the mapping moves is measured, not guessed** (round 333): `exness XAU`'s 500-900
  day segment is **42% less volatile** than the recent 500 (0.05590 vs 0.09597 %/5m), so
  the 900-day blend is 16% calmer — and the *same* deployed band's trade-rate ratio
  between the windows (**1.307x**) matches their volatility ratio (**1.190x**) to **9.8%**.
  A fixed fractional barrier is hit less often when moves are smaller. Measure segment
  volatility from Timescale before attributing a rate change to anything else.
  **Refine the grid before declaring an optimum, and the volatility argument then
  predicts the band** (round 334). The 2.0x optimal-band ratio *was* a grid artifact:
  filling in the untested 0.01-0.02 interval at 500 days moves the best net from
  0.02/0.04 (−0.0301) to **0.0125/0.025 (−0.0121, 2.5x better, Sharpe −0.041,
  cost÷gross 1.02, 7.67/week)**. Scaling the 900-day optimum by the volatility ratio
  predicted **0.0119**, within **5%** of the best tested point — the argument located the
  *region*, not a point, since only two intermediate bands were run and the lower one won.
  Two consequences for method: an "interior optimum" on a grid whose adjacent points are a
  factor of 2 apart is a **grid-resolution statement**, not a measured optimum; and the
  round-332 frequency coincidence ("~6.8/week at both windows") **dissolved** on the finer
  grid (500-day optimum is 7.67/week, not 6.82) — a coincidence between two coarse-grid
  points is not a property of the route. Also note the refined net curve is **non-monotone**
  (0.015/0.03 at −0.0724 is worse than both neighbours), so with magnitudes of 0.01-0.07
  claim only the bracket ("the optimum lies between 0.01 and 0.02"), never the ranking of
  adjacent points. The best refined configuration **passes Target 3 (7.67/week)** while
  still failing the gate on Sharpe, positive-day ratio and cost÷gross, so the round-328
  Target 1 / Target 3 conflict is **window-scoped to 900 days**.
- **Read the gate's *whole* `failed_checks` list before calling a failure a performance
  failure** (round 335). On `exness XAU` at `--days 500` every run also fails
  `minimum_holdout_days` — the holdout spans 98.5 calendar days but only **84 observed
  days** against a threshold of 90, and a CFD's closed weekends make 90 structurally
  unreachable in that window — plus `input_continuity_failed` on **all seven** non-5m
  intervals (5m has 356 verified session gaps and 0 unverified; 15m carries 344
  *unverified* gaps over 15,154 candles, 1h 342/3,782, 30m 342/7,572). **No configuration
  can pass the gate on that route at 500 days**, so 500-day gate runs yield valid
  *relative rankings* and invalid *gate verdicts*. At `--days 900` the holdout reaches 151
  observed days and that check passes; whether the continuity checks also pass there is
  untested. `unverified` means "not confirmed as a session gap", **not** "data missing" —
  do not report it as a data defect without inspecting the classifier.
  **The continuity failure is route-specific and window-independent** (round 336): it also
  fails at `--days 900` on `exness XAU` — where `minimum_holdout_days` *does* pass at 151
  observed days — and fails harder there (15m: 628 unverified gaps over 27,659 candles). So
  **no `exness XAU` gate verdict at any window is pass-eligible**, and the whole band arc on
  that route (rounds 328, 330-335) yields relative rankings only. `binance BTC` at 500 days
  reports **zero gaps of any kind on all eight intervals** and passes both structural checks
  — crypto routes give real gate verdicts. **Run a 24/7 route as the control** before
  attributing a gate failure to performance.
  Where the markers come from, read-only (round 336, investigation only): a gap counts as
  verified only when the kline carries `gap_before_reason`/`gap_before_candles`
  (`finance-research/src/klines.rs:314-329`), and **both ends support all eight intervals** —
  `finance-mw/cmd/ops/kline-gap-marker-backfill/main.go:334-354` runs per route *per
  interval*, and `finance-mw/internal/interfaces/worker/kline_flusher.go:331-337` derives its
  step from the route's own interval. The shortfall is in **stored-data coverage**, not in a
  code path unable to express it; un-run backfill and a live-path gap are both consistent
  with the evidence.
- **Separate a cost failure from a no-edge failure before proposing any lever** (round 336).
  On the gate's own holdout the two routes fail differently: `exness XAU` @900 earns
  **positive gross** (+0.7820) and loses it to cost (cost÷gross 1.53), while `binance BTC`
  @500 has **negative gross** (−1.7909) and trips `gross_pnl_positive` — it loses *before*
  any cost is charged, so no cost or frequency lever can rescue it (it already trades
  21.84/week, 3.2x the Target 3 bar, and still loses). Check `gross_pnl_before_costs` first;
  its sign decides which levers are even applicable.
  **Across four gate-measured routes only one has positive gross, and it is the one that is
  not gate-eligible** (round 337): `exness XAU` @900 **+0.7820** (not eligible), `bybit XAUT`
  @500 −0.0135 (eligible), `binance BTC` @500 −1.7909 (eligible), `exness BTC` @500 −2.1476
  (4 intervals fail). So the entire cost/band arc (rounds 313-335) targets the only route
  where cost work is meaningful *and* the only route whose gate verdict is structurally
  unreachable. State that trade-off explicitly rather than reporting a cost improvement as
  progress toward a gate pass.
  A cross-route pattern worth *only* a lead: gross ordered by frequency is +0.7820 (6.85/wk),
  −0.0135 (4.48), −1.7909 (21.84), −2.1476 (24.58). Four uncontrolled points, non-monotone,
  and **contradicted** by round 328's within-route ladders (gross flat across 5-7x frequency).
  **That lead is now refuted** (round 338): the within-route ladder on `bybit XAUT` — the
  gate-eligible route — gives gross **+0.2662 at 10.36/week and +0.2590 at 1.96/week**, a
  2.8 percent difference across a **5.3x** frequency range. Round 328's flat-gross reading
  holds on a second route. It also **corrects** the round-337 claim that `exness XAU` is the
  only route with positive gross: that was one band per route, and two of three bands on
  `bybit XAUT` are at +0.26. **Never characterise a route's edge from a single band.**
- **Read the joint objective across bands before calling any band better** (round 338). On
  `bybit XAUT` the three gate dimensions point in opposite directions: net is best at
  0.02/0.04 (−0.0595, cost÷gross 1.23) and that *same* band is worst on frequency (1.96/week
  against a 7.0 bar) and worst on streak (**21** consecutive negative days against a
  threshold of 5) — and streak degrades monotonically as frequency falls (5 → 13 → 21 at
  10.36 → 4.48 → 1.96 per week). A band that halves the loss while tripling the losing streak
  and missing the frequency bar by 3.6x is **not** an improvement; report all three or the
  result is cherry-picked.
- **Before calling an odd single point noise, measure its neighbours** (round 339). The
  deployed band's near-zero gross on `bybit XAUT` looked like configuration noise of order
  ±0.28 against neighbours at +0.26. It is not: 0.008 returns **+0.2518** but 0.0125 returns
  **−0.0682**, so **two adjacent bands** sit at roughly zero between three at +0.25 to +0.27.
  Noise does not produce two adjacent low readings between three high ones. The route has a
  narrow **0.01-0.0125 gross hole and the deployed band is inside it** — cause unknown, edges
  only known to grid resolution, one route and one window.
  **It is still not actionable, and the reason generalises**: leaving the hole restores
  +0.265 of gross and adds **+0.298** of cost (frequency 4.48 → 5.88/week), leaving net
  0.032 *worse*. Recovering gross through the band lever always buys frequency at the same
  time, and cost scales with trade count (round 274 onward) — so a gross-only improvement is
  not an improvement. Check the cost delta before reporting a recovered edge.
  **Filling in the shoulders settles it** (round 340): with 0.009 (**+0.1561**) and 0.015
  (**+0.1414**) added, the seven-band gross sequence is perfectly unimodal — 0.2662 > 0.2518 >
  0.1561 > −0.0135 > −0.0682 < +0.1414 < +0.2590 — a **smooth trough with monotone shoulders**,
  not a sharp hole. Noise does not produce a monotone descent across three points followed by a
  monotone ascent across three more, so the feature is structural. Cause still unknown; shape
  is not mechanism.
  **But "structural" here means "not noise within this window", not "a property of the
  route"** (round 341): at `--days 300` the 0.0125-versus-0.02 gross gap collapses from
  **0.3272 to 0.0476** and both bands turn negative. The gross *sign* on `bybit XAUT` is
  window-dependent too, so round 337's "only `exness XAU` has positive gross" and round 338's
  correction of it are both window-scoped statements. **Round 331's lesson, now re-learned
  three times** (optimal band r331, optimal frequency r334, trough r341): a shape measured on
  one window is a statement about that window — replicate on a second window before naming a
  feature. And note the trap in the replication design itself: a shorter `--days` shifts the
  holdout *start*, so it changes the period **and** drops specific days at once — it can test
  persistence but cannot attribute a change to any one excluded day.
- **Single-day dominance is general, and the daily arrays show cross-route structure**
  (round 341, zero containers). Every route has a band-independent worst day; on `exness XAU`
  it is **2026-08-12** at both the 500- and 900-day windows (window-independent too). The two
  BTC venues agree exactly (2026-06-05 worst, 2026-06-15 best on both `binance` and `exness`),
  while **the two gold routes invert**: 2026-06-10 is the *worst* day on `bybit XAUT` and the
  *best* day on `exness XAU`. Top-five days carry a strikingly uniform **14.4-19.7 percent** of
  total absolute daily PnL across five runs, three instruments and two window lengths. Mine
  these arrays across saved runs before spending a container — the cross-route comparison costs
  nothing and the saved logs accumulate.
  **The cross-route divergence is made by the Portfolio, not by the instruments** (round 342).
  `bybit XAUT` and `exness XAU` daily *price* returns correlate at **+0.996** (n=86, narrow
  read-only Timescale query) while their Portfolio *PnL* correlates at **+0.287**; on
  2026-06-10 both fell together (−4.00 and −4.23 percent) yet the Portfolio made +0.2197 on one
  and lost −0.1694 on the other. Within-group mean PnL correlation is +0.734 for BTC and +0.433
  for gold. **Check the price correlation before attributing a PnL divergence to the
  instruments** — a confirmed prediction is not a confirmed explanation. Cause of the
  divergence is unknown (route-local Alpha weights, entry timing and position direction are all
  consistent; none inspected).
- **The fleet is complete at six of six, all failing** (round 342), deployed band:
  `exness XAU` @900 **+0.7820** gross (not gate-eligible, 7 intervals), `bybit XAUT` −0.0135
  (eligible), `binance XAU` −0.3442 (not eligible, 53 observed days), `bybit BTC` −1.3153
  (eligible), `binance BTC` −1.7909 (eligible), `exness BTC` −2.1476 (not eligible, 4
  intervals). **At the deployed band `exness XAU` is the only positive gross** — the precise
  form of the claim round 337 overstated. Three routes are gate-eligible; all three have
  negative gross.
  `binance XAU` is **shallow, not frozen**: its data reaches the present but `--days 500`
  silently returns a partial window (holdout 2026-07-09 → 2026-08-30, 53 observed days). Check
  `observed_days` and `holdout_start` on every run — a partial window is not an error.
  Also: `cost_to_gross_pnl_ratio` is computed against a **negative** gross on those routes and
  must not be read as a cost improvement.
- **`exness XAU`'s positive gross is the one window-robust quantity found so far** (round 343):
  **+0.3391 / +0.6000 / +0.7820 / +0.7300** at `--days` 300 / 500 / 900 / 1200, holdouts
  starting January through July. Set that against every quantity that *moved* with the window —
  optimal band (r331), optimal frequency (r334), the gross trough (r341), `bybit XAUT`'s gross
  sign (r341). The premise the whole cost arc rests on is sound; net is still −0.045 to −0.460
  and the route is gate-ineligible at all four windows. `--days 300` is its closest to
  break-even ever measured on the deployed band (net −0.0454, streak 3) — one window.
- **Routes do not run the same Alpha ensemble, by design** (round 343, investigation only).
  `finance-research/src/strategies.rs:24-78`: every route starts with `candle_momentum` +
  `rsi_mean_reversion`, and only **three** get extras — `binance BTC/USDT` perp, `exness XAU/USD`
  cfd (`mtf_stochastic_5m_4h_sma5`) and `exness BTC/USD` cfd. `bybit XAUT`, `bybit BTC` and
  `binance XAU` run the base two only. Production gates identically
  (`finance-api/src/deployment_rules.rs:616-642`, test at `:747-780`), with the exclusions
  documented in place — so research mirrors production and this is **not** a measurement defect.
  It is a sufficient mechanism for the gold pair's PnL decorrelation, though it does not order
  the whole correlation matrix. **Check the ensemble before comparing two routes' PnL.**
- **A calendar day's PnL is not a fixed quantity — never difference daily arrays across
  windows** (round 343). At the deployed band on `exness XAU`, 2026-08-12 measures
  **−0.0545 / −0.1796 / −0.1796 / +0.0015** at 300 / 500 / 900 / 1200 days, and 2026-08-21 goes
  −0.1666 / +0.0924 / 0.0000 / 0.0000 — all four holdouts contain both dates. This is the
  round-300 per-kline weight refit reaching the daily array. Cross-route day comparisons made
  *within* one window are fine; anything across windows is not.
- **`--fee-bps` and `--slippage-bps` are not exogenous — cost-component attribution is not
  identified** (round 344). On `exness XAU` @300, `--fee-bps 0` left the trade count at exactly
  42 and dropped `gross_pnl_before_costs` — measured *before* costs — from **+0.33907 to
  +0.07177 (−79%)**; `--slippage-bps 0` moved the count 42 → 38. A cost parameter cannot change
  pre-cost gross on a fixed trade set, so the trades differ. Same round-300 mechanism: cheaper
  execution makes more strategies profitable → different `alpha_performance_quality` → different
  weights → different trades. **Any `total_cost_drag` delta across cost settings is a joint
  cost-and-decision effect**; quote it as such and never as "slippage is worth X". This is the
  mechanism behind round 215's super-additivity, and it applies to rounds 213-215 too.
  Numbers, quoted jointly: slippage removal −46.6% of cost drag (against a 28.6% share of the
  bps), fee removal −71.9% (against 71.4%).
- **The only positive net ever measured in this arc is a counterfactual — do not let it
  escape its caveats** (round 344). `exness XAU` @300 with `--slippage-bps 0`: net **+0.1315**,
  Sharpe +0.913, Sortino **+1.592**, cost÷gross 0.610. Zero slippage is unachievable, the run is
  confounded (38 trades vs 42), it still fails Sharpe / cost÷gross / positive-day ratio, and the
  route is gate-ineligible at every window. What it establishes is only that at this window the
  deficit is the same order as the slippage line — an execution-quality question for
  `finance-broker`/`mt5`, not a Portfolio-layer result.
  **And that reading got weaker still** (round 345): net across the fee ladder is
  **non-monotone** — −0.04538 / −0.05056 / **+0.14423** / −0.03635 at 5.0 / 4.9 / 3.0 / 0.0 bps
  — so a *larger* cost cut (fee 0.0) is **not** profitable. A profitable point on a cost ladder
  is not evidence that reducing cost helps.
- **The replay is chaotically sensitive: a 1.4% cost perturbation moves gross 14.8%**
  (round 345). `--fee-bps 4.9` against the deployed 5.0 — 0.1 bps, 1.4% of the round trip —
  adds a trade, moves gross **+0.050 (+14.8%)**, *raises* total cost 14.4% at a lower rate, and
  leaves net 11.4% worse. This also **refutes** the natural mechanism hypothesis: the
  `realized_pnl > 0` gate in `alpha_performance_quality` (`trading_modes.rs:597-612`) is a step,
  so a sub-sign-flip nudge should have changed nothing. What actually drives it is **not
  established**.
  **Practical consequence — treat small between-configuration differences as uninterpretable.**
  Round 334's best two bands differ by 0.018 in net and round 340's trough shoulders by similar
  amounts, both inside what a 1.4% nudge produces here. Sign-level and large-magnitude
  conclusions are unaffected; fine rankings are not measurable with this tool. Caveat: this was
  measured on the **cost axis** only — it is grounds for suspicion on the band and `--days` axes,
  not a proven bound there (round 300's `N` vs `N+1` probe is the equivalent on `--days`).
  The one statement that survives every perturbation tried: **`exness XAU`'s gross is positive at
  every cost setting and every window** — magnitude unstable to 15%, sign never moved.

## Backtest correctness — audited, with citations

A full look-ahead / fill / accounting audit is in
`research/quant/audits/backtest-correctness-audit-look-ahead-and-fill-invariants.md`. **No look-ahead
was found.** Do not re-derive these; cite them.

- **Causal ordering is sound**: only `is_kline_closed` bars enter (`klines.rs:246`);
  `replay_order` sorts by **`close_time`** tie-broken by ascending interval
  (`portfolio_decision_replay.rs:59-67`), so a higher-timeframe bar never reaches a base bar
  that closed at the same instant; the MTF filter writes its trend sign only on closed
  higher-interval bars and suppresses during warm-up
  (`multi_timeframe_trend_filter.rs:77-116`); the Portfolio decides at `primary.close_time`
  behind `is_synchronized` (`portfolio_decision_replay.rs:340-347`); weight refitting is online
  from cumulative *past* performance — path dependence, not leakage (`:317`).
- **Fills are adverse and pessimistic**: entry = `kline.close` moved against the position
  (`trading_modes.rs:1919-1923`); the per-bar order `record_true_range → settle_funding →
  try_close_at_protective_level → apply_target` (`:1745-1760`) makes a same-bar entry-and-exit
  round trip structurally impossible; a bar containing both stop and take takes the **stop**
  (`:2153-2161`).
- **Accounting integrity holds empirically** across 8 gate runs and all six routes:
  `ending_equity == starting_equity + cumsum(realized_pnl)` to ≤1.3e-11 on 1e4, and
  `Σ daily == net_realized_pnl` exactly. Re-run this check whenever the replay changes.
- **Saturday PnL on a gold CFD is not a bug.** `daily_profit_gate.rs:340,402` bucket days by
  `close_time.with_timezone("Asia/Ho_Chi_Minh")` (UTC+7), so bars closing after 17:00 UTC fall
  on the next local day and a Friday session splits across two buckets. Verified against
  Timescale: `exness XAU` has **zero** 5m bars on every flagged Saturday, and Friday runs
  00:00–20:55 UTC. Consequence to remember: the gate applies per-day thresholds to those
  **partial** buckets, diluting `positive_day_ratio`, `median_daily_pnl` and streak.
- **Known limitations, none of them look-ahead**: protective fills execute at *exactly* the
  stop/take price with **no gap modelling** (`trading_modes.rs:2143-2161`) — tail loss is
  understated, and it bites hardest on the weekend-closing `exness XAU`; the holdout's day 0 can
  carry a position opened in training; and **there is no per-trade audit trail** —
  `ExecutionFootprint` (`portfolio_measurement.rs:23-28`) exposes aggregates only and
  `SimulatedTrade` (`trading_modes.rs:1548-1562`) is never serialized, so fills **cannot** be
  reconciled against market data without a code change. Treat every ordering invariant above as
  code-verified, not trade-verified.
- **Production retains too few trades to validate anything** (round 357) — the mirror image of
  L4. The durable logs `trades:<route>` are **zsets with three entries per closed trade** and
  **no TTL**; they start at worker uptime, so a restart truncates them. Measured with all six
  workers "Up 3 days": `exness XAU` **1 close**, `bybit XAUT` 1, `binance XAU` 1, `binance BTC` 6,
  `bybit BTC` 4, `exness BTC` 4. **`exness XAU` — the route the arc is about — has one closed
  trade at a single timestamp.**
  The three countable routes' live rates are consistent with their gate rates (15.33 vs 21.84,
  11.43 vs 12.11, 9.66 vs 24.58) but the exact Poisson 95% intervals are
  **[5.63, 33.36] / [3.11, 29.26] / [2.63, 24.72]** per week — **agreement by lack of power**,
  never quote it as calibration. Discriminating the guarded-vs-guard-free 26.8% rate difference
  needs ~**30-40 closes**, roughly **6-8 weeks** of uninterrupted uptime on `exness XAU`.
  **Re-reading these six keys later is free** and is the one cheap way this ever becomes testable —
  and it is **valid**, because the writer is append-only: `finance-redis/src/trade_log.rs` has
  `ZADD` only, with no trim, expiry or delete (round 358). Three entries really are **one trade**
  under three paper scopes (`paper-risk-2pct`, `paper-compounding-10pct`, `paper-fixed-pct`), so
  closes = entries ÷ 3.
  **Compute live rates over the observation window, never over first-event-to-last-event**
  (round 358) — the latter conditions on the events and inflates the rate. Redis started
  2026-08-22 05:26 UTC; over that 8.67-day window **five of six routes have their backtest rate
  outside the live 95% Poisson interval**, all with the backtest predicting **4.5-7.6x** more
  trading than happens, while over the 3.4-day worker window only `exness BTC` is outside.
  **Which window applies is not resolvable from retained data**, so claim no discrepancy — but do
  not repeat the biased denominator.
  Free confirmation from a live payload: `contributing_strategies` on the one `exness XAU` close
  reads `candle_momentum −0.6296, mtf_stochastic_5m_4h_sma5 0.0, rsi_mean_reversion 0.0` —
  **two of three deployed strategies at weight exactly 0.0 on a real trade**, the first direct
  evidence of the weight collapse outside the replay. One trade; not shown to be typical.
- **Production ECS logs and OTel spans are the observability channel — use them, they are
  free.** Each route worker writes ECS JSONL to `/data/log/finance-live-action-<route>/`
  (`application`/`info`/`warn`/`error`/`access`, rotated daily). Application events carry a
  `span` with `market.event.id`, `market.interval`, Kafka topic/offset/partition and W3C
  `trace.id`/`span.id`. VictoriaMetrics' API is **authenticated** — do not try to obtain
  credentials; metric-series checks are out of reach from this loop.
  Verified from those logs (`research/quant/audits/observability-trace-audit-*.md`): on `exness XAU`
  2026-08-28, **0 of 620** signals were emitted before their bar closed (min lag **+1.015 s**,
  median +2.133 s, all eight intervals); Kafka offsets strictly increase on all eight topics;
  **245 distinct `market.event.id`, none processed under two traces** — no duplicate execution;
  `trace.id`/`span.id` are 32/16 chars on 620/620; and the gold worker emitted **0** events on
  the closed Saturday. Also, across 24 saved backtest runs the emitted
  `research.backtest_candle_count` event shows `train + validation + holdout == candle_count`
  **exactly every time** (60/20/20, no overlap).
- **`market.event.id` semantics differ per broker — establish the convention before differencing
  timestamps.** Exness encodes the **bar open**, exactly aligned (ms offset 0). Binance encodes a
  close-side event timestamp with **0-1444 ms jitter**. Applying the Exness convention to Binance
  produces a spurious "518 of 528 signals before bar close, median −299.93 s"; under its own
  convention the worst case is −0.43 s. **A false look-ahead alarm came from exactly this.**
- **Two backtest-vs-live divergences the code cannot show.** (1) **Binance revises closed
  klines** — 347/day on BTC, 154/day on XAU, **zero on Bybit and Exness**; live replaces the
  history entry but *blocks strategy evaluation for the revision*, while the replay reads the
  post-revision Timescale values, so **the backtest evaluates candles live refused to
  re-evaluate**. Magnitude unmeasured (the warn event carries no before/after prices).
  `exness XAU`, the only route with positive gross, has **zero** revisions. (2) **Production
  enforces an `execution_cost` risk gate at 10 bps** (`"projected execution cost is 14bps;
  maximum is 10bps"`, cumulative `rejected_count`), and **the replay models no such gate** — so
  production trades a strictly smaller, cheaper target set than the backtest, biasing the
  backtest permissively on the exact axis (cost) this arc has been optimising.
  **Divergence 1 is now quantified and P3** (round 347). Join the live `Signal evaluated`
  `price` to Timescale's stored `close_price` on the bar named by the event's `market.event.id`
  — that difference *is* the pre-versus-post revision delta, and it needs no Kafka access (the
  broker's console consumer is refused without credentials; **do not go hunting for them**).
  125 `binance BTC` 5m bars: **51.2% identical**, **median 0.0000 bps**, mean 0.1806, p95 1.4211,
  **max 2.8955 bps**, 6.4% ≥1 bps, 3.2% ≥2 bps, **0% ≥7 bps** (the round trip). Revision *rate*
  is high — **74.0%** of 5m bars, 68.8-83.3% on the other intervals, each bar revised exactly
  once — but the price impact is bounded well under cost. The tail is the same order as the
  deployed **2 bps slippage**, so treat it as bounded, not harmless.
  **Crucially, `exness XAU` has zero revisions**, as do both Bybit routes and `exness BTC`;
  only the two Binance routes are affected and both already fail on negative gross. **Divergence
  2 remains open and does bear on `exness XAU`.**
  Method note worth reusing: if a bar-alignment assumption is wrong, deltas land in the tens of
  bps (a full 5m move); hundredths-of-a-bp deltas are themselves the proof the alignment is
  right.
  **Divergence 2 is WITHDRAWN — the replay does apply the gate** (round 348).
  `portfolio_measurement.rs:170-181` builds the `PortfolioRiskLayer`, and
  `PortfolioRiskPolicy::widened_for_simulation` (`portfolio_risk.rs:272-307`) widens **only**
  notional/leverage, leaving `max_total_cost_bps = 10.0` intact.
- **THE COST FLAGS CHANGE THE ACTION SPACE, NOT JUST THE COST — a 10 bps gate blocks reversals**
  (round 348). Projected cost = `(fee_bps + slippage_bps) × leg_multiplier` with
  **`leg_multiplier = 2` for a reversal** (`portfolio_risk.rs:624, 643-648`; defaults
  spread/impact/latency = 0 at `:248-250`), rejected on a **strict** `>` against 10.0
  (`execution_cost.rs:243`, policy at `:210`). So at deployed 5+2 bps a single leg (7) passes and
  **a reversal (14) is always rejected**. Production confirms it is the gate's only behaviour:
  **369 rejections across all six routes, every one at 14 bps**, none at any other value —
  `bybit BTC` 213, `binance BTC` 87, `exness BTC` 66, **`exness XAU` 3**, others 0.
  **This is the threshold that explains rounds 344-345**: `--fee-bps 3.0` and `--slippage-bps 0`
  both put the reversal at **exactly 10.0** — which passes, since the test is strict — and both
  produce **38 trades** with nets **+0.1442** and **+0.1315**; `--fee-bps 4.9` (13.8) and the
  deployed 5.0 (14.0) stay blocked and give 43/42 trades at −0.051/−0.045. **The fee ladder is a
  step function, not chaos** — round 345's "chaotically sensitive" is corrected, though its
  residual (4.9 vs 5.0 differing by a trade and 14.8% of gross, both above the ceiling) is real
  and unexplained.
  **Practical rule: before attributing anything to a cost change, compute `(fee+slippage)×2` and
  check which side of 10 bps it lands on.** Every profitable number this arc produced from a cost
  flag came from crossing that line, i.e. from buying an action space production does not have.
  (Round 346's `protective: none` +0.4069 is the exception — it ran at deployed costs.)
  **`risk_rejected_counts` in the plain `--json` output measures this directly** — per-gate
  tallies from the replay's risk layer (`portfolio_measurement.rs:255`), no per-trade trail
  needed. On `exness XAU` @300 (55,045 decisions, deployed band, hold 36): **102**
  `execution_cost` rejections at deployed costs versus **3** with `--slippage-bps 0`, and
  **every other gate at 0** in both. Read it against **trades, not decisions**: 102/280 is
  **one blocked reversal per ~3 executed trades**. Check this counter before theorising about a
  cost flag's effect.
- **The execution-cost gate is an action-quality lever, not a frequency lever** (round 349).
  Unlocking reversals moved the trade count **−1.1%** (280 → 277) while realized PnL improved
  **31%** (−1.3222 → −0.9166): a blocked reversal does not remove a trade, the Portfolio just
  does not act on that decision. Every band/frequency conclusion in this arc was read as if
  trade count were the lever — here it barely moves and the outcome moves a third.
  **And the gate-free feedback path is now isolated**: `legacy_selected_rule` executes *outside*
  the risk layer and still moved 355 → 338 trades between the same two runs, so that residual
  (round 345's unexplained sensitivity) lives somewhere the gate never touches — use that ledger
  to study it.
  **What cannot be concluded**: the unlocked arm changes cost *and* action space together, so the
  31% cannot be attributed between them. The clean run needs `max_total_cost_bps` held while
  costs stay deployed, and **the CLI has no flag for it**. Never state that production's gate
  costs PnL on the strength of this pair.
  **The missing flag can be worked around** (round 350): hold `--fee-bps 5` and walk slippage
  **2.0 / 1.0 / 0.5**, all of which keep the reversal above 10 bps (14.0 / 12.0 / 11.0, rejections
  102 / 96 / 97) — three points that measure the **pure cost slope with the action space fixed**.
  Extrapolate to 5.0 bps and compare against the unlocked run. Result: blocked-arm slope
  **−0.27222 PnL per bps**, prediction **−0.78532**, actual **−0.91662**, **Δ = −0.13130**. So
  round 349's 31% gain is the **cost slope**, and the unlock's own contribution is **negative** —
  the "production's gate costs PnL" reading is refuted in sign; if anything the gate is mildly
  protective.
  **But do not quote a point estimate.** A nearest-pair extrapolation gives Δ = −0.18446, on the
  other side of the registered 0.15 threshold; the blocked arm's pairwise slopes differ by
  **44%**; and the **ungated** `legacy_selected_rule` ledger moves **−0.11237** across the same
  step while being non-monotone. An effect of ~0.13 is not separable from a ~0.11 wobble on a
  ledger with no gate. **The defensible statement is a range of −0.13 to −0.18, small against the
  0.4056 total move.**
- **`--interval` does NOT change the Portfolio decision interval — it is hardcoded to `"5m"`**
  (round 351). `main.rs` passes the literal `"5m"` at `:577` (replay), `:599`/`:612` (gate) and
  `:634` (measurement), never `args.interval`, and `portfolio_decision_replay.rs:246-250`
  hard-errors on anything else. The flag reaches only the **Alpha sweep table**. An
  `--interval 30m` run reproduced the 5m baseline in **20/20 metric fields and all 51 daily
  rows**; `--interval 15m` merely shifts the holdout by 3 candles (window-alignment side effect,
  uninvestigated) and perturbs the same 5m replay. **Never report an `--interval` value as a
  decision-horizon result**; testing a longer horizon needs a code change.
- **The replay is bit-for-bit deterministic** (round 351): two runs in different rounds at
  different wall-clock times with the same data window agreed to **seventeen digits** on every
  field and every daily row. Consequences: there is **no run-to-run jitter**, so every difference
  between configurations in this arc is a real response to a real input change; "configuration
  noise" (round 339) and "chaotic sensitivity" (round 345) both mean **sensitivity to inputs**,
  not randomness; and **repeating an identical configuration proves nothing** — probe stability
  by changing an input. Determinism is reproducibility, **not** accuracy: the fidelity limits in
  both audits are untouched, and cross-image determinism is untested.
- **EVERY holdout is nested — no two `--days` values give independent out-of-sample evidence**
  (round 352). The holdout is always the tail of a window ending at "now", so all of them share
  an end date and each larger one strictly contains the smaller: @300 `2026-07-01→08-28` ⊂ @900
  `2026-03-04→08-28` ⊂ @1200 ⊂ @1500 `2025-11-03→08-28` ⊂ @1800 `2025-09-03→08-28`. There is no
  as-of/end-date flag, so disjoint holdouts are **impossible** with this CLI.
  **Read every cross-window statement accordingly**: window-*fragility* results are unaffected (a
  superset behaving differently is real information), but window-*replication* is partly
  guaranteed because the recent data sits inside every sample. Say "measured at N nested
  resolutions", never "replicated across N windows".
- **Gross is positive at all six windows** on `exness XAU` at the deployed band: **+0.3391 /
  +0.6000 / +0.7820 / +0.7300 / +0.9550 / +0.5550** at 300 / 500 / 900 / 1200 / 1500 / 1800 days
  — the durable statement, with the nesting caveat attached. **@1500 is net positive at deployed
  costs** (net +0.22720, cost÷gross 0.7621, Sharpe +0.3424) — the only such run in the arc — and
  it still fails six gate checks, including `minimum_trades_per_week` at **2.814** against 7.0,
  while its deeper neighbour @1800 is net −0.24159. One nested window; do not quote it as a
  result.
- **A weekday filter is not established** (round 352). Registered design: discover on the first
  half of the @1200 holdout, verify on the second. {Mon, Fri} was selected and the set's mean on
  half B is +0.002036 > 0, so the criterion **passes** — but **Monday flips sign** (+0.151 →
  −0.201) and Friday carries the whole result. With six weekday cells and n = 17, ~three positive
  cells are expected under the null, so the discovery step carries no significance. Friday is
  positive and Wednesday negative in all four nested slices; **Wednesday was never
  pre-registered**. Remember the UTC+7 split: the "Sat" bucket is the tail of the Friday session
  (audit L3), so weekday cells are not trading days.
  **Disjoint periods ARE available within one run** (round 353). A single replay's
  `daily_results` array splits into disjoint sub-periods that are internally consistent (unlike
  across runs — round 343); `exness XAU` @1800 gives three disjoint 102-day thirds. Use that, not
  multiple `--days` values, whenever a claim needs out-of-sample structure.
  Re-run that way with **strict single-hypothesis** criteria (never aggregate a set — round 352's
  aggregate passed while Monday flipped sign): **Wednesday is negative in all three thirds**
  (−0.01895 / −0.01486 / −0.01428) and **Friday positive in all three** (+0.00057 / +0.00829 /
  +0.02176); Monday and Thursday flip. Wednesday is 16.7% of days carrying **−0.81767** of a
  −0.24159 holdout — **20.3x** the overall daily mean.
  **Its ceiling is hypothesis freshness, not design.** Thirds 2 and 3 were inside the round-352
  tables that suggested both hypotheses, so the data is not out-of-sample *with respect to the
  hypothesis*. A clean test can only be built **prospectively**, on days that do not yet exist.
  Two further blocks: `daily_results` is **net**, so nothing can be said about gross by weekday —
  and that distinction decides whether a filter helps at all — and **the CLI has no weekday
  filter**, so the candidate cannot be run end-to-end without a code change.
  **And gross-by-weekday is structurally unobtainable** (round 354): zeroing costs would expose
  it, but `(fee + slippage) × 2 > 10` is exactly what blocks reversals, so any cost low enough to
  isolate gross also changes the action space. Use the **activity proxy** instead — a day with
  `realized_pnl == 0` closed no trade. On `exness XAU` @1800, Wednesday is **less** active than
  average (0.824 vs 0.845) with a day-level win rate of **0.429 vs 0.540** and **1.20x** larger
  moves: fewer wins, bigger swings, same activity — **edge, not cost**. The proxy is coarse
  (a non-zero day may hold one trade or five) and its win rate is day-level, not trade-level.
  **The pattern does not transfer — it inverts** (round 354, a genuinely fresh test since the
  hypothesis came from `exness XAU` only). Ranked within each route @1800: Wednesday is **worst**
  on `exness XAU` (−0.01603) and **best/second-best** on `exness BTC` (−0.01196) and
  `binance BTC` (−0.01148); Friday is **best** on `exness XAU` (+0.01043) and **worst** on both
  BTC routes (−0.04116, −0.04547). Route-specific or noise; this does not separate them.
- **Never register a criterion an all-negative route passes by default.** Round 354 registered
  "Wednesday's mean is negative on both BTC routes" as evidence of a systematic effect — but
  **every** weekday is negative there (both routes have negative gross and net ≈ −6.5), so the
  test could not fail. **Fourth pre-registration defect** (327 uncomputed p-value, 330 wrong
  variable, 340 unassigned interval, 354 vacuous criterion). Register a **discriminating**
  statistic — here, the weekday's **rank within its own route**, which refuted transfer at once.
- **Audit L3 quantified** (round 354): on `exness XAU` @1800 there are **49 Saturday buckets, 47
  of them exactly zero** (95.9%), and **88 of 306 rows (28.8%) are zero overall**.
  `positive_day_ratio` reads 0.37255 but is **0.43580** excluding the Saturday buckets — the
  UTC+7 tail alone costs **0.063**, ~17% of the reported value, against a 0.55 threshold written
  for an instrument that trades every day.
- **The weekday direction is CLOSED** (round 355). A permutation test (20,000 shuffles of weekday
  labels, counts fixed, 257 trading-weekday rows) on `exness XAU` @1800:
  **p = 0.6013** for *"some weekday negative in all three disjoint thirds"* — round 353's headline
  structure **happens six times in ten by chance**, because each weekday is negative in a third
  with probability slightly over ½ and there are five of them; **p = 0.0532** for the
  min-weekday-mean statistic, **failing** the registered α = 0.05; **p = 0.1996** for Friday.
  **"Marginal" is not a result** — a registered threshold either passes or it does not.
  **Measure what multiplicity costs**: testing Wednesday *by name* gives **p = 0.0112**, 4.8x
  smaller than the selection-corrected 0.0532, and would have flipped the verdict. Always make
  the statistic the **extremum across the candidate set**, never the chosen member.
  A "structure" argument (agreement across k disjoint sub-periods) is worth almost nothing when
  the base rate is near ½ per period — compute its permutation p before quoting it as evidence.
- **The gap-fill limitation is quantified and now P3** (round 346). `exness XAU` 5m since
  2024-09-01: **session-boundary** gaps n=118, mean 0.2565%, max **2.0030%**, only **6 (5.08%)**
  reach the deployed 1% stop; **intraday** gaps n=140,901 with **1** bar past 1%. So the
  exact-stop fill is essentially exact within a session, the optimism is confined to session
  boundaries, and the worst case is about **2x** the modelled loss on ~6 events in two years.
  The join to actual positions remains blocked by L4 — measure market exposure, never claim a
  specific trade was affected. Crypto routes have no session boundaries at all.
- **`--portfolio-protective-kind none` is the largest lever in the tool, and it is
  window-fragile like all the others** (round 346). `exness XAU` @300 with no band: 12 trades,
  **1.44/week**, net **+0.4069**, Sharpe **+3.05**, Sortino +10.18 — the first *achievable*
  profitable configuration measured. The same change @900: gross turns **negative** (+0.7820 →
  −0.0287) and net is **−0.7675 against the deployed −0.4110, 87% worse**. Refuted in the round
  that raised it. And even at its good window it misses Target 3 by **4.9x** (1.44 vs 7/week),
  worsens the streak (5 vs 3) and fails positive-day ratio — **reading Target 1 alone would have
  called it a large win**. Do not treat a no-band result as a candidate without both windows and
  all three targets.
- **`daily_results` is already in every `--json` run — mine it before spending a container.**
  It is a 101-entry array of `date`, `realized_pnl`, `return_fraction`,
  `maximum_drawdown_fraction`, `ending_equity`, and it sums to `net_realized_pnl` (net, not
  gross). Round 340 answered two open questions from it at **zero container cost**: the
  "identical 37/101 positive-day ratio at three bands" invariance is a **coincidence in the
  count** (0.008 and 0.0125 share only 29 of 37 days, Jaccard 0.644), and **one calendar day
  was the worst day at every band measured** — 2026-06-10 on `bybit XAUT`, worth **358.6
  percent** of the net loss at the best-net band. Report single-day dominance as a
  **concentration** measurement, never as "profitable if you exclude it": the day is in the
  sample and Sharpe/Sortino are punishing exactly that tail.
- **Per-trade cost is not constant across bands** (round 340): 0.00636 to 0.01137, a 1.8x
  spread, non-monotone in band width. "Cost scales with trade count" (rounds 274 onward) is a
  useful approximation that holds at the 2-5x frequency changes those rounds used, **not an
  identity** — do not lean on it for per-trade differences under ~2x.
- **Pre-register the criterion as a partition, not two inequalities.** Round 340 registered
  "confirmed if gross ≥ +0.15, refuted if ≤ +0.1" and the result landed at **+0.1414**, in the
  gap. Third defect of this kind (327: uncomputed p-value; 330: bound on the wrong variable;
  340: unassigned interval) — every branch of the outcome space must map to a verdict before
  the run starts.
- **Continuity failure follows the instrument's trading calendar, not the venue or the
  market type** (round 337). `exness BTC/USD` — a CFD on the same Exness surface as
  `exness XAU` — fails only 4 intervals with 15 unverified gaps over 54 candles at 5m, and
  2h/4h/12h/1d are perfectly clean; `exness XAU` fails 7 with 628 gaps over 27,659 candles at
  15m. The difference is that BTC/USD trades around the clock while XAU/USD closes every
  weekend. Two corollaries: **5m is not automatically the marked interval** (`exness BTC`
  trips `input_continuity_failed:5m`, where `exness XAU`'s 5m is fully marked), and a
  separate **`holdout_interval_continuity`** check exists and can fire on its own. Marker
  coverage varies per route — read each run's own continuity block, never assume.
- **A tuned optimum is usually a plateau; measure its width before naming a point**
  (round 335). Filling the 500-day grid in to seven bands shows 0.0115 (net −0.01225) and
  0.0125 (−0.0121) identical to within 1.2% on net, Sharpe, positive-day ratio, streak and
  cost÷gross — and the volatility-scaled prediction (0.0119) lands **inside** that flat
  region. The same grid resolves whether fine ordering is noise: net climbs
  −0.2283 → −0.0541 → −0.0122 across 0.01 → 0.011 → 0.0115, steps one to two orders of
  magnitude larger than the gaps in doubt, so the **rising side is signal** even though the
  falling side stays non-monotone. Two structural readings hold across all seven points:
  **trades/week is perfectly monotone in band width** (8.95 → 6.11, no exceptions), and
  **gross and net peak at different bands** — gross peaks at 0.011 while cost drag falls
  monotonically with trade count, so the net optimum sits *wider* than the gross optimum,
  set by that crossover rather than by an edge maximum.
- **Pre-register the criterion on the quantity the conclusion turns on, and compute any
  threshold before committing to it.** Two defects in four rounds: round 327 registered
  "|ρ| ≥ 0.9 reaches p = 0.0167 at n=5" without computing it (it is 0.0833, 5x off), and
  round 330 registered a bound on **gross** when the decision turned on **net** (gross
  fell 25.7%, just inside the stated 30% bound, while net worsened 4.6x). Both were
  caught in-round; the fix is to state the criterion on the deciding variable.
- **Compute a permutation p-value before pre-registering a significance threshold.**
  Round 327 registered "|ρ| ≥ 0.9 reaches p = 0.0167 at n=5" without computing it; the
  exact distribution gives p = 0.0833 there, and **only |ρ| = 1.0 reaches 0.0167** at
  n=5 (0.1333 at 0.8, 0.2333 at 0.7). At these sample sizes almost nothing clears 5%.
- **All six routes fail the daily-profit gate**, every one on Sharpe, Sortino,
  positive-day ratio and cost÷gross. On the matched five, `exness XAU` is the only route
  with positive gross before costs; `binance XAU` is also positive (+0.0797) but only on
  a 51-day holdout, **below the gate's own 90-day minimum** — report it separately rather
  than folding it into the matched comparison.
  The cost ablation is the highest-value one: at `--fee-bps 0 --slippage-bps 0` on
  `exness XAU` 360d the Portfolio layer flips to **+1.10** (`one_target`) and **+1.60**
  (guard-free) against −2.44 / −1.98 deployed, so **the loss is cost-driven, not
  signal-driven** — but the gross edge is only **30% of round-trip cost**, needing a
  51-70% cost cut to break even (round 313). Note the cost gate caps total cost at
  **`max_total_cost_bps = 10.0`**, so the deployed 7 bps one-way is at **70% of a hard
  ceiling**: at 14 bps one-way `one_target` returns **zero trades**, not worse trades.
  A cost arm above the cap is degenerate — use `legacy_selected_rule`, which still
  trades there, if you need a third point on the cost curve.
  **The cost-driven diagnosis is route-specific — never generalise it.** The identical
  ablation on `binance BTC` (360d) returns **−0.4432 at zero cost**, gross edge
  **−0.00093/trade**: the raw signal is unprofitable before any friction, so no cost cut
  reaches break-even there (round 314). Cost dominates the loss on both routes (145% of
  it on XAU, 88% on BTC) but only XAU's residual is positive. Run the ablation per route
  before drawing any conclusion about "why we lose".
  **Three** consecutive pre-registrations on this question failed, twice in opposite
  directions (r313 predicted XAU negative → positive; r314 predicted BTC positive →
  negative; r315 predicted `exness BTC` negative → positive). There is no working model
  of where raw edge lives in this fleet — do not offer directional predictions on it.
  Current picture at `--days 360`, gross edge per trade: `exness XAU` **+0.00281**,
  `exness BTC` **+0.00111**, `binance BTC` **−0.00093** — a gradient, not a binary, and
  the best cell still converts only 30% of its round-trip cost. **Check both measures
  before believing a sign**: on `exness BTC`, `one_target` says +0.5634 while the
  guard-free `legacy_selected_rule` says −0.4548. And note **broker is perfectly
  confounded with market type** in everything measured so far (every positive route is
  exness+cfd, the only negative is binance+perpetual_future) — `bybit BTC` or
  `bybit XAUT` would separate them. **Round 316 ran `bybit BTC` and ruled broker out**:
  two different exchanges on perpetual futures land at −0.00093 and −0.00114/trade,
  20% apart, both measures agreeing, while the two Exness CFD routes are 87% apart. So
  **market type is the surviving candidate** — but "cfd" is still perfectly confounded
  with "exness" (every CFD route is Exness), and market type is only a *label* on a
  bundle (pricing, spread, funding, venue microstructure) this design cannot separate.
  Round 317 then ran `bybit XAUT` (spot) and ruled out **Exness-specificity** too: it
  is positive on both measures with the fleet's **highest edge-to-cost ratio (33.8%)**.
  Grouped by market type the five cells split cleanly (cfd + spot positive, perpetual
  negative); grouped by asset they do not. **Market type and instrument remain tied**,
  because the only within-instrument contrast (BTC across cfd/perp) rests on
  `exness BTC` — the one sign-ambiguous cell — and there is no within-market-type
  contrast favouring instrument. The discriminating cell is `binance XAU` (XAU on a
  perpetual), and it **cannot be run at `--days 360`**: only 262 days of 5m history,
  frozen since 2025-12-26. Gross edge per trade, five cells: +0.00281, +0.00123,
  +0.00111, −0.00093, −0.00114.
  **When you have no usable prior, pre-register the *interpretation* rather than the
  outcome** — state in advance what each result will be taken to mean, including an
  explicit "ambiguous" branch for when the two measures disagree. That keeps the round
  rigorous without inventing a directional guess.
- **The durable Redis trade log is the only window-free Target 3 measure** —
  real closed positions, no replay, no adaptive weights, no `--days`. Read
  `trades:<broker>.<market_type>.<base>.<quote>` (ZCARD) against its
  `:payloads` hash (HLEN); they must match, and **closes = entries ÷ 3** (three
  capital rules). Prefer it over any backtest number for a frequency claim, and
  when the fleet looks stalled, check
  `{finance-live-action:checkpoints}:worker_checkpoint:<route>.5m` — a fresh
  `updated_at` means the workers are alive and the stall is in the
  decision-to-target path, not an outage. A gold-CFD worker going stale over a
  weekend, with its last Kafka offset on the `.1d` topic, is the known benign
  signature (rounds 102, 306) — never report it as a fault.
  The same checkpoint carries the live Portfolio state: `current_target.position`,
  `decisions_since_target_change`, `waiting_after_protective_exit`, `gate_passed`,
  `gate_reason`, `entry_score`, `trend_score`. Read those before theorising about a
  quiet fleet — in round 307 all six routes were simply **holding open positions**
  with five gates blocking, every counter far past the 36-decision hold guard. Each
  `gate_reason` reproduces from the two scores and `minimum_role_score = 0.1`
  (`trading_modes.rs:842-857`), so the read doubles as a live check that the gate
  logic matches the code. Append samples to `research/quant/samples/position-state-samples.csv`
  and `research/quant/samples/signal-state-samples.csv`.
- **Never size a gate lever from `gate_reason` labels.** The three conditions are
  evaluated in order, so a magnitude failure fires first and masks a sign conflict
  underneath: in round 308, 6 of 11 `*_below_threshold` blocks *also* had conflicting
  signs, so the labels overstated `minimum_role_score`'s reach by more than 2x
  (50% claimed against 22.7% real). Recompute reach from the raw `entry_score` /
  `trend_score` pairs — a block clears at threshold 0 **iff the two scores share a
  sign** — before running anything. On that basis a 30% cut to the deployed 0.1
  unblocks *nothing* and removing the gate entirely unblocks under a quarter, so the
  threshold is a weak frequency lever; `entry_trend_conflict` dominates and has no
  threshold at all.
- `minimum_role_score` has **no research CLI flag** (`trading_modes.rs:427/459/465`,
  used at `:850`/`:853`; nothing in `finance-research/src/main.rs`), so its joint-
  objective effect cannot be measured today — unlike the protective-band and hold
  parameters, which do mirror runtime. Note an A/B at a **fixed `--days`** stays clean
  even after the round-300 confound, since that only breaks comparisons *across*
  window lengths — so a missing flag, not the confound, is what blocks parameter work.
- **`entry_score` and `trend_score` are not on the same scale.** `role_scores()`
  partitions by *interval* (`trading_modes.rs:1042-1069`): Entry sums `5m`/`15m`/`30m`
  (3 intervals), Trend sums `1h`/`2h`/`4h`/`12h`/`1d` (5), all at weight 1/8
  (`:477-496`), and the single `minimum_role_score = 0.10` (`:501`) is compared against
  both sums unchanged. Observed mean `|entry|` is 0.107 — sitting *on* the threshold —
  against mean `|trend|` 0.277, so the cut lands almost entirely on the entry side.
  Never reason about the gate as if one threshold meant one thing.
  **And do not assume the uniform weights.** The live `interval_weights` in the
  production checkpoint have drifted far from 1/8: `5m` sits **2.1x-7.8x below**
  uniform on all six routes and `1d` above it on all six (up to 0.43 — 43% of the
  total), pushing the live entry:trend ratio to **2.21x-5.96x** (round 310). Read the
  checkpoint's `interval_weights` and `strategy_weights` before any gate reasoning.
  The cause is documented, not new: `alpha_performance_quality` returns **1.0 at
  `trade_count == 0`** (`trading_modes.rs:593-595`), so untraded intervals get maximum
  quality while the actively-trading `5m` is scored on real losing performance and
  falls to `INTERVAL_QUALITY_FLOOR = 0.05` (`:453`) — see the standing note at
  `deployment_rules.rs:218-240`, which also names the fix direction (an explicit
  interval-weight floor) and warns against removing the zombie `mtf_*` entries.
  **Because every strategy is a confirmed loser, `empirical` is exactly 0.0 and the
  quality function reduces to `1 − min(trade_count/20, 1)`** — a pure trade-count
  function with no performance term at all (`PERFORMANCE_CONFIDENCE_TRADES = 20`,
  `:431`). That inverts: from a route's normalised weight vector you can read back each
  interval's implied trade count (round 311 got `1d` = 11-15 trades on three
  two-strategy routes, everything else ≥20). It is also **the mechanism of the
  round-300 window confound**: replay ledgers start empty, a 180-day window gives `1d`
  only 180 bars against `5m`'s 51,840, so **shorter windows leave the long intervals
  immature and therefore more heavily weighted** — the decision stream shifts
  trend-ward with window length, by construction and in a predictable direction. The
  floor itself is a deliberate deadlock guard (`:630-645`): without it an all-mature-
  loser route would weight everything to zero and never decide again.
  **But do not extend that mechanism to predict the confound's size.** Its natural
  corollary — long windows mature everything, weights return to uniform, so deep
  perturbations should be milder — is **false**: on `binance BTC` a one-day probe moved
  `one_target` **+5 at 260 days and +50 at 900 days**, a 10x *larger* response at depth
  and a 52x overshoot against that day's real content (round 312). Sensitivity grows
  with window depth; no mechanism for that is established. Probe at the depth you intend
  to use, every time.
- **Never quote a backtest Target 3 rate without its `--days`.** On
  `exness XAU` the single-window rate is 3.89/week at 180 days and 7.27/week at
  360 — **1.87x** from window length alone, against `binance BTC`'s 0.98x. When a
  route's margin over the 7/week bar is smaller than its window sensitivity
  (XAU: +1.7% margin against a 5.5% spread), record the verdict as
  **undetermined**, not as a pass. **A verdict is trustworthy exactly when the
  margin exceeds the sensitivity** — a large relative defect does not by itself
  invalidate one: `bybit XAUT`'s 8.57% sensitivity cannot bridge its −65.8%
  gap, so its *fail* is as safe as `binance BTC`'s pass (round 303).
  **Never compute that cushion from a one-day perturbation.** On `binance BTC`
  the one-day figure was 1.04%; a ladder out to 280 days gave **15.9%** —
  **15.3x** larger, and equal to that route's smallest margin, erasing what had
  been reported as a 33x cushion (round 305). The growth factor is not
  predictable: 15.3x on `binance BTC` against 1.7x on `exness XAU` over the same
  extension. Measure a 4-point ladder spanning at least 20 days before quoting
  any sensitivity.
- The defect's magnitude is **not** explained by bar density or session
  continuity — `bybit XAUT` is 24/7 at 288 bars/day and has the *largest*
  relative defect (round 303, pre-registered prediction refuted). Across three
  routes the **absolute** one-day movement is nearly constant (+5, −7, +8
  trades) over a 4x range of trade counts, so the damage scales inversely with
  how many trades a route makes: **low-trade routes are the least measurable**.
  Treat this as a description of three routes, not a law — and note the
  one-day figure is only a **lower bound**: extending the `exness XAU` ladder to
  370 and 380 days produced a **−20 trade** violation from a single +10-day step
  (round 304), against the ~7 seen at one day. Measure the ladder over the step
  size you actually intend to compare, and read every published per-route
  sensitivity as a floor.
- **Count nesting violations, not rates**, when you need a rate-free measure of
  the confound: a nested cumulative counter must be non-decreasing in `--days`
  whatever the market did, so any decrease is pure method noise and needs no
  estimate of the true trade rate. On `exness XAU`, 3 of 4 steps in the
  360/361/365/370/380 ladder decreased while Alpha trades and candle counts had
  **zero** violations.
- The **Alpha layer is the weight-free control**. `strategy_scores[*].splits[*].trades`
  is simulated independently of Portfolio weights and *is* cleanly nested (76
  of 77 strategies strictly monotone across 260/360/540/720d in round 300). Use
  it to ask whether a market period was genuinely quiet before attributing
  anything to the market. It counts Alpha-strategy trades across ~77
  strategies and has **no** relationship to Portfolio trade frequency — never
  quote it against Target 3.
- The CLI's `--json` output is a **pretty-printed multi-line JSON document**
  appended after the JSONL log lines, not a single JSONL record. Parse it by
  scanning for the first line that is exactly `{` from which the remainder of
  the file parses; `portfolio_execution` is a **list**, and `one_target`
  lives at `portfolio_execution[0]["one_target"]`.
- For read-only Timescale coverage checks, `public.instruments` joins on
  `i.id = k.instrument_id` and `i.broker_id = b.id` — there is **no**
  `instruments.instrument_id` column. Session-closed markets (gold CFD) report
  their gaps as `verified_session_gap_candles` with
  `authoritative_gap_metadata: true` and `unverified_gap_count: 0`; that is
  recorded market closure, **not** missing data, and a CFD route's lower
  bars/day must not be read as a data defect.
- A "weak train, strong later splits" or "only holdout wins" pattern is a
  known false-positive shape — re-test on an independent window (e.g. a
  shorter/different `--days` range) before trusting it. Cross-validate any
  promising single-broker result against the other broker and, where
  relevant, the other instrument before treating it as a real signal — a
  result that holds on Binance BTC but inverts on Exness BTC or XAU is very
  likely an artifact of that one data source, not a real edge.
- New strategy mechanisms belong in `finance-research/src/strategies.rs` as a
  local (unpromoted) candidate — this file's own header comment states the
  convention: unvalidated candidates live here, never in the shared
  `finance-strategy` crate (that crate is reserved for strategies already
  promoted into `StrategyKind`/`finance-api::deployment_rules.rs`). New
  reusable indicators (e.g. a new channel/oscillator calculation) do belong
  in `finance-strategy/src/indicators/` since indicators are generic
  utilities shared by promoted and unpromoted strategies alike.

## Production verification

Read live state directly from Redis rather than trusting a workflow's own
report or a prior round's summary:

```
ssh my "docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}'" | grep live-action
ssh my "docker exec redis-singleton-<id> sh -c \"REDISCLI_AUTH=\\\$REDIS_PASSWORD redis-cli --no-raw GET '{finance-live-action:checkpoints}:worker_checkpoint:<route>'\""
```

The four routes are `binance.perpetual_future.btc.usdt.5m`,
`binance.perpetual_future.xau.usdt.5m`, `exness.cfd.btc.usd.5m`,
`exness.cfd.xau.usd.5m`. The redis container name changes across restarts;
find it fresh with `docker ps | grep redis-singleton` rather than assuming a
stale name from a previous round.

**Never run a broad environment dump** (`docker exec <container> env`,
unfiltered `printenv`) on any production container while investigating a
config value — it prints every secret in that container, not just the one
being checked (this has caused two separate credential-exposure incidents on
the Kafka container specifically). Grep the exact variable name instead:
`docker exec <container> sh -c 'env | grep SPECIFIC_VAR'`, or read a mounted
config file when one exists. If a broad dump happens anyway, stop, do not
repeat the value anywhere (including in `docs/archive/legacy-handoff-agent.md`), flag it to
the user in the same turn, and log a P0 security item for rotation without
attempting the rotation yourself unless it's a low-risk, well-understood
credential — a live distributed-system credential (Kafka controller/broker
auth, DB passwords) has real outage risk if rotated incorrectly and deserves
a dedicated, careful follow-up rather than a rushed fix mid-round.

`redis-cli --no-raw GET` wraps the JSON value in outer quotes with escaped
inner quotes/backslashes — strip and unescape before parsing:

```python
raw = output.strip()
if raw.startswith('"') and raw.endswith('"'):
    raw = raw[1:-1]
raw = raw.encode().decode('unicode_escape')
d = json.loads(raw)
```

Useful fields inside `runtime_state`: `evaluation_count` (advances every
cycle — never restart-stable, always compare against a same-session
baseline, not a stale one from days ago), `portfolio_evidence.policy` (live
`interval_weights`/`strategy_weights`, `minimum_role_score`), `simulated_ledgers`
(per-strategy-and-interval `demo-*-scope-*` entries feed the reweight
formula; `paper-*-scope-*` entries are the real Portfolio-level ledgers —
`performance.trade_count`/`realized_pnl` there are the actual decision/PnL
counters), `pending_history_backfill` (should be rotating near-present
timestamps; a stale, non-advancing cluster is a real bug, not normal).

## Promotion and provider failover

Only a result classified PROMOTE enters engineering. Derive one stable,
meaningful kebab-case change name, create the OpenSpec change via
`/opsx:propose` with research-origin references, then stop at planning —
there is no automatic lifecycle after that. Never implement runtime code
directly from a research-only result.

Codex implements and fixes by default; Claude covers it when Codex is
confirmed out of quota (`CLAUDE.md`'s Role/Working Model role boundary — and
symmetrically, Codex covers PLAN/VERIFY when Claude is out of quota). Only a
confirmed account/global quota exhaustion justifies falling back to the
other provider; a generic 429, timeout, network blip, or implementation
failure does not. There is no coordinator that detects this automatically —
whoever is operating the round makes that call, and continues the same
diff/commits under the same change if a fallback happens mid-work.

1. Implement directly against the plan, per the role boundary above; do not
   invoke a deleted `/ops:e2e`/`run-phase-agent` lifecycle — neither exists
   anymore. Read a sibling implementation first — e.g. an existing
   `Strategy` impl or `StrategyKind` variant — before writing a new one.
2. Test locally inside Docker with a CPU cap, same as the backtest tooling
   rule above: `docker run --rm --cpus=3 -v "$PWD":/app -w /app
   rust:1.88-slim-bookworm bash -c "apt-get update -qq && apt-get install -y -qq
   protobuf-compiler build-essential ca-certificates >/dev/null 2>&1 &&
   cargo test ..."`. Run the full workspace suite before committing
   (`cargo test --workspace --exclude finance-redis` — finance-redis's tests
   need Docker-in-Docker, unavailable in this environment; note the
   exclusion honestly rather than silently skipping it). `cargo fmt --check`
   must be clean; run `cargo fmt` and re-verify if not.
3. Commit directly to `main` (solo-maintainer exception already in effect
   for this ecosystem — no branch/PR ceremony) with a conventional commit
   message after the configured verification gates pass.
4. Push, then track CI: `gh run list --branch main --limit 2 --repo
   ThanhNguyenDat/finance-live-action`. A transient `curl: Resolving timed
   out` / DNS failure in the deploy step is infrastructure flakiness, not a
   code problem — `gh run rerun <run-id> --failed` is the correct response,
   not a revert. Use `gh run watch <run-id> --exit-status` with
   `run_in_background: true` while continuing other round work, rather than
   polling in a tight loop.
5. finance-live-action's "Detect changed paths" job sets a `research`/`deploy`
   output pair — a change touching only `finance-research` (no
   `finance-strategy`/`finance-api`) resolves `deploy=false` and the
   `build-and-push`/`deploy-app` jobs show as skipped (`-`) in `gh run view`,
   not failed. Do not assume every green run deployed; check the job list
   before running the production-verification step below — a research-only
   commit needs no SSH check at all, production is untouched. After a
   successful deploy (`deploy-app` actually ran), verify production
   independently (see "Production verification") — confirm every affected
   container reports the exact deployed commit SHA, is healthy, and (for
   behavior-preserving changes) that state like
   `evaluation_count`/`interval_weights` is unchanged; for behavior-changing
   fixes, confirm the expected new values.
6. A finding that would change core, shared decision-algorithm behavior
   (e.g. `reweight_from_alpha_performance`, anything touching all four
   production routes at once) needs stronger justification than an
   instrument-scoped fix — read any doc comment stating the original design
   intent first (this codebase's comments are unusually detailed and
   sometimes explicitly document a deliberate tradeoff, e.g. "instead of
   diluting the demonstrated signal" is a real design choice, not an
   oversight); simulate the change's effect against real production data
   before deploying it, not just against synthetic test cases.

## Research evidence and promotion

Every round updates the research evidence set, even a purely-negative round:

1. **`research/quant/reports/optimize_loop_update_v2.csv`** — one row per
   instrument/broker/strategy combination touched this round. Columns:
   `round_date,round_seq,layer,instrument,broker,market_type,base_interval,
   strategy_or_rule,data_source,trades,win_rate_pct,rr_ratio,profit_factor,
   sharpe_ratio,sortino_ratio,information_ratio,net_pnl_usd,
   starting_equity_usd,trades_per_week_est,max_drawdown_duration_days,
   max_consecutive_losses,ulcer_index,sqn,skewness,kurtosis,
   target1_profitable,target2_makedecision,target3_freq_ge1day_or_7week,notes`.
   Leave a metric blank rather than fabricating it when the tool didn't
   report it.
2. **`research/quant/rounds/round<N>-<slug>.md`** — full writeup: methodology,
   numbers, honest caveats, comparison to prior rounds when relevant. When a
   round corrects an earlier round's conclusion, add a visible `⚠️
   CORRECTION` banner at the top of the original file pointing at the new
   one — never silently edit history. When a round only extends an existing
   thread with a small addendum, append a `## Cập nhật Round <N>` section to
   the existing file instead of creating a near-duplicate new one.
3. **`research/quant/index.md`**: refresh the relevant
   direction so the next round can navigate open/closed research without
   treating it as engineering task state.

For REJECTED, NO-CHANGE, DATA-ISSUE, or NEEDS-MORE-RESEARCH, stop after research
evidence. For PROMOTE, reference these paths from OpenSpec and OPS origin
metadata; do not copy report contents and do not write an implementation task
to `docs/archive/legacy-handoff-agent.md`.

- **A route's "maximum frequency" is a property of the settings you have run, not
  of the route.** Round 367 called `binance BTC` the only route that ever cleared
  7 trades/week and reasoned from that; Round 368 tightened the band on
  `exness XAU` and got 10.43/week on the first try. Before claiming a route
  cannot reach a bar, check whether the knob that moves frequency has actually
  been pushed in that direction there.
- **The band is asymmetric around the deployed point.** On `exness XAU`,
  tightening bought +29.6% frequency for a 1.36% PnL change while widening cost
  31% frequency for +74% PnL. When testing a knob, sample **both** directions
  from the deployed value — the two sides are not mirror images and a one-sided
  sweep will report a trade-off that does not exist on the other side.
- **Judge a PnL difference against per-trade scale before calling it a change.**
  0.02140 on 350 trades at ~0.0046/trade is under five trades' worth. State that
  as a magnitude argument and say so explicitly; a single deterministic replay
  supports **no significance test**, and calling one difference "noise" and
  another "an effect" without that scale check is where p-hacking starts.

- **Identify a stored log by the parameters it reports, not by the filename a
  previous round gave it.** Round 369's first evaluation read a stored
  `0.02/0.04` run as the deployed cell and produced a plausible-looking cost
  ratio against a correct threshold — the right verdict from the wrong
  arithmetic. Parse `candle_count`, trade count and the run's own parameters out
  of each log and assert they match the cell you think you are comparing.
- **Precompute a threshold from data you already hold on the *same* route.**
  Round 369's criterion came from Round 367's widening step on `binance BTC`,
  so the bar was fixed before the runs and could not be tuned to the answer.
  This is stronger than a round-number threshold and stronger than a bar taken
  from the other route.
- **Direction of a knob's cheapness is a route property, not a knob property.**
  Tightening the band is 52x cheaper than widening on `exness XAU` and 1.9x more
  expensive on `binance BTC`; the per-trade gradient's good end also swaps.
  Three consecutive rounds have refuted a band generalisation. Assume any
  Portfolio-layer effect is route-local until it is measured on a second route
  in the same window.

- **Test a positive result's *sign* on a window it was not selected on, before
  anything else.** The arc's only profitable configuration held its sign from
  300 to 500 days and flipped at 900. A full-window in-sample positive is a
  candidate for a window test, never a candidate for promotion.
- **Report the `legacy_selected_rule` control alongside any PnL claim.** In
  Round 370 it separated two very different statements: the configuration beats
  the control at *every* window (real effect) but crosses zero only on the
  recent ones (not a candidate). Without the control the round would have read
  as a flat refutation.
- **When windows are nested, do not attribute the difference to the older
  period.** r300's finding stands: Portfolio weights refit on every kline, so a
  900-day run and a 500-day run carry different weights over every shared bar.
  State the sign change; never publish a subtraction.
- **Check bar coverage against calendar time before quoting trades/week.**
  `exness` CFD gold runs at ~67% coverage, so calendar-based rates understate
  activity by ~1.49x on that route. Keep the arc's existing convention for
  comparability, but say which denominator a Target 3 verdict depends on.

- **Register two questions on one pair of runs when the same output answers
  both.** Round 371 got a corner sign and a control advantage from the same two
  containers; the two answered in opposite directions, and the negative half
  closed a question while the positive half opened a better one. Budget is two
  containers, not two questions.
- **When a control keeps beating the thing being tested, the control comparison
  *is* the finding.** The guard-plus-risk-layer advantage over
  `legacy_selected_rule` is positive in 4/4 measurements across two routes and
  two window depths - the only quantity in 60+ rounds to survive both the
  cross-route and cross-window tests. Report the advantage alongside every PnL
  number; it costs nothing and it was hiding the arc's one stable effect.
- **A prior round's own stated stopping condition is the strongest bar to test
  against.** Round 286 wrote "falling below 7 would mean no single-window
  verdict is trustworthy"; Round 371 measured 6.80 at 900 days. Quoting the
  earlier round's criterion removes any suspicion the bar was chosen after
  seeing the number.
- **Check whether a route's bar coverage makes the denominator question moot
  before repeating the caveat.** A 24/7 perpetual at 900 days gives exactly
  900.0 days of candles, so calendar and bar rates coincide and the CFD coverage
  caveat does not apply - say so rather than carrying a caveat that cannot bite.

- **A within-run comparison does not need matched windows.** `one_target` against
  `legacy_selected_rule` is computed on the same decision stream inside one run,
  so a fleet-wide sweep of that comparison can use each route's own horizon -
  the validity gate that governs every cross-configuration comparison in this
  arc does not apply. This makes route-generality cheap to test; do it early on
  any effect before calling it general.
- **When a pre-registered criterion fires on the thinnest route, record the
  thinness as a limitation and the refutation as the result.** Round 372's
  failing route had 134 trades and no more history available. Explaining away a
  failed pre-registration by pointing at the sample is the move this loop exists
  to prevent.
- **Test your own proposed mechanism against the data you already have before
  writing it down.** Round 372's whipsaw-frequency story predicted a
  frequency/advantage correlation; the six points gave Spearman rho +0.143 and
  refuted it. A mechanism published without that check becomes a
  plausible-sounding claim later rounds have to dismantle.

- **`strategy_scores` in every run's JSON is the Alpha layer with real
  train/validation/holdout splits at deployed costs**, and it is sha256-identical
  across Portfolio configurations on the same route and window. It is free in
  every log already captured - check it before spending containers, and never
  re-run a route just to read it.
- **Simulate the null for a cross-route criterion *before* registering it.**
  Round 373 registered "positive on >= 2 of six routes" when the chance
  probability was 0.9999. A criterion that cannot fail is not a test; compute
  P(criterion | chance) with a quick permutation and pick a bar the null puts
  well below 0.5.
- **The six production routes are not six independent trials.** Three BTC routes
  share volatility to three decimals (r276) and the gold routes correlate 0.996
  in price (r342). Collapse to instrument level - and collapse parameter
  variants into mechanism families - before quoting any multiplicity p-value.
  Round 373's P < 1e-5 became p = 0.0115 under that collapse.
- **Selecting on the holdout consumes it.** The holdout is the trailing 20% of
  the window, so no `--days` value yields a fresh one (r352's blocker applies to
  the Alpha layer too). Once a scan picks winners by holdout PnL, the only
  unseen data left is forward time - say so instead of implying confirmation.
- **Pre-register a minimum validation trade count for threshold selection.** A
  zero-trade validation cell can tie at zero PnL and win a naive argmax while
  providing no evidence; exclude such cells from selection, report them, and
  keep the holdout untouched.

- **Never count a `strategy_scores` row without checking `trades > 0`.** A
  strategy whose signal side never changes opens one position and never closes
  it: `trade_count` stays 0 while funding accrues, and the row reports a small
  positive `realized_pnl` equal to `-funding_paid` with `win_rate` and
  `profit_factor` null. Round 373 counted twelve such phantom cells and built
  its headline on one.
- **Use `survives_selection()` in `sweep.rs` rather than hand-rolling
  selection.** It already requires `trades > 0 && realized_pnl > 0` on train and
  validation and deliberately excludes holdout - both guards a hand-written scan
  is likely to miss. Before writing analysis code over a JSON array, grep the
  crate for a function that already does it.
- **An absent input degrades a strategy silently instead of disabling it.**
  `taker_base_vol` is 100% populated on Binance and 0% on bybit/exness, so
  `buy_ratio` is identically 0 there and every threshold fires the same side
  forever. When a family's variants return identical numbers, suspect a missing
  input before suspecting an inert parameter - and confirm it against
  `public.klines` with one narrow read-only query.
- **A round can be worth more with zero containers.** Round 374 retracted the
  previous round's headline using only code reading, logs already captured, and
  one query. Check what the held logs and the source can settle before spending
  the container budget.

- **Check which strategy set a code path actually consumes before assuming
  contamination.** `main.rs:573` and `:629-630` feed the Portfolio from
  `production_candidates` and the 77-strategy `strategy_scores` from
  `candidates()` - disjoint. A defect in the sweep does not reach the Portfolio,
  and the call sites settle it in one grep.
- **A wrapper strategy is a no-op whenever the inner strategy's entry condition
  saturates the metric the wrapper filters on.** `keltner_reversion` only fires
  on a band breach, which forces `strength = 1.0`, so `min_strength` at 0.5/0.7/
  0.9 drops nothing and three sweep ids are one behaviour. When variants return
  byte-identical splits *on every route including ones with complete data*,
  suspect this before suspecting missing inputs.
- **Measure effective breadth as distinct split-signatures, not id count.** The
  sweep advertises 77 and delivers 74 on Binance routes and 71 elsewhere. Any
  multiplicity calculation should use the smaller number - or a family collapse
  that is more conservative still.
- **Form a hypothesis on the routes you have measured, then test it on one you
  have not.** Round 375 built the Alpha-input-count story on five routes and
  refuted it on `bybit BTC`, whose advantage had never been computed. Holding
  one route back costs nothing when the comparison is within-run.

- **A measurement blocker is a promotable defect, not a permanent constraint.**
  The user authorised architecture changes to remove blockers, provided the
  rules and the promotion gate still hold and correctness comes first
  (2026-08-31). When a round concludes "this cannot be measured", the next step
  is an OpenSpec change against the measurement tool - not another round that
  re-derives the same wall. See
  `openspec/changes/portfolio-measurement-integrity/`.
- **When unifying two diverged code paths, the acceptance test is exact
  equality, not similarity.** The replay is deterministic, so a unified gate and
  Portfolio path must agree bit-for-bit on trade count and PnL at the same
  configuration. Any difference is a defect. A test that only checks "close
  enough" would have permitted the original divergence.
- **Prefer refusing a score over publishing a degraded one.** A strategy whose
  input is missing, a row that never traded, a wrapper whose threshold cannot
  bind - each produced a false result in this arc. Absent is a valid value;
  zero and a defaulted input are not.

- **Pin a change's acceptance values before the implementation is visible.**
  While a worker is mid-IMPLEMENT, read the expected numbers out of logs
  captured *before* the change existed and store them. This is the same
  discipline as pre-registering a round's criterion, applied to verification -
  and it removes any possibility of adjusting the bar to what the
  implementation happens to produce.
- **Prefer an acceptance check whose two possible answers differ in opposite
  directions across cases.** The gate/`one_target` baselines differ by 2.32x on
  one route and 0.76x on another, so an implementation that kept the old stream
  cannot be wrong in one consistent direction that might be excused as a scaling
  bug. Also assert the control does not collapse into the new value.
- **While a worker holds the repository lock, do not inspect its work in
  progress beyond `git status`.** Reading a partial diff contaminates the
  independence that `verification_mode=independent` exists to protect, and a
  half-finished tree cannot be verified anyway.

- **Pin an acceptance baseline on the same restriction the check will run
  under.** Round 377 pinned full-window `one_target` figures, but the gate is
  holdout-restricted by design, so the comparison could never succeed and tested
  nothing. Before pinning, ask what slice of data the thing under test actually
  reports on.
- **A pinned baseline on a route still accumulating history expires.**
  `binance XAU` returned 24 more candles two hours later because it sits at its
  venue horizon. Re-read the baseline, or pin only routes whose window is
  already capped by `--days`.
- **Structural identity of a call sequence is not behavioural equality.** Two
  paths can both call the shared function and still differ in what they feed it.
  Confirm the code, then still run the numbers - and say plainly which one you
  have done.

- **`candle_count` equality does NOT mean the two runs covered the same bars.**
  The loader takes `Utc::now()` inside `load()`, which runs once per interval
  (eight intervals), so every run has a rolling, per-interval window. Two runs
  hours apart can report an identical count over different bars. Always pass
  `--as-of <RFC3339>` and compare `data_as_of`; treat the old
  same-`candle_count` validity gate as insufficient.
- **Know the jitter before believing a small difference.** On `bybit BTC` @900 a
  three-candle window shift moved PnL 8.3% and the trade count by 4. Any
  cross-run difference smaller than the route's jitter is not established. Pin
  the cutoff, or run both arms in one round and say which.
- **When a fix chases a value, check the value is reproducible at all.** Two FIX
  rounds pursued a baseline whose window had never been recorded and could not
  be recreated. Before demanding a number in a findings file, confirm the
  original run captured enough state to reproduce it.

- **Any directional result must be compared against passive drift over the same
  bars before it counts.** Gold rose 105% over the window, and the strategy's
  drift while long (5.152e-05/h) versus while short (5.274e-05/h) differed by
  2.4% - zero directional timing. A long side that profits on a rising asset is
  beta. Make "beats passive exposure over the same bars" the acceptance
  criterion for any side-restricted rule, never "positive PnL".
- **Decompose exposure time, not just PnL.** The finding that mattered on
  `exness XAU` was not the long side's +0.65 but that the Portfolio is short
  75.4% of the span against a +105% drift. Time-on-the-wrong-side is a
  different and more diagnostic quantity than per-trade PnL.
- **The audit trail pays for itself immediately.** Rounds 383-385 - the side
  split, the cross-route inversion, and the drift refutation - all came from
  `--emit-trades` output at zero containers. Export trades on any run worth
  analysing later.

- **Never register a criterion on the sign of a statistic alone.** Round 387
  registered "positive correlation confirms" and measured rho = +0.006 - noise
  that the criterion as written would have scored as confirmation. This is the
  seventh mis-specified pre-registration in the arc. Always state a magnitude
  the null is unlikely to reach, and simulate it first when the statistic's null
  distribution is not obvious.
- **Exposure-time share is a first-class diagnostic, not a by-product.** The
  gold short bias (67% of exposure-hours on a route that rose 105%) is invisible
  in PnL and trade counts and only appears when time-in-position is
  decomposed by side. Compute it whenever a route's result looks directional.

- **Check the input exists before naming it as the next step.** Round 387
  proposed reading per-strategy side distributions from `strategy_scores`;
  round 388 found that schema has no side field at all. A named next step is a
  commitment - grep the schema before writing it down.
- **Factor a skew into its components before hunting for a cause.** Exposure
  skew = entry count x mean duration, and the identity holds exactly. On gold
  the entry term (1.735x short) carries the bias while the duration term
  (1.17x) matches every other route - which rules out the minimum-hold guard and
  everything downstream of entry in one step, at zero containers.

- **A ratio is uninterpretable when its denominator can be negative.**
  `cost_to_gross_pnl_ratio` reads as "costs are N times the edge" only when
  `gross_pnl_before_costs > 0`. On three routes gross is negative and the ratio
  still produces a plausible number - one of them would even pass the threshold.
  Always read `gross_pnl_positive` first; the gate provides it as a separate
  check for exactly this reason.
- **Separate "edge too small to pay costs" from "no edge at all" before
  drawing any conclusion about costs.** Only one of five routes is in the first
  category. Targeting cost per trade would have been the wrong conclusion for
  four of them.

- **Disjoint holdouts ARE available: shift `--as-of` back by one holdout
  length.** r352's nested-holdout blocker stood for 39 rounds and was dissolved
  by a flag added for an unrelated reason. A 900-day window admits roughly four
  disjoint 180-day holdouts. Use this before believing any positive holdout
  figure - the first time it was run, it reversed the sign of the arc's last
  surviving positive result.
- **A correct measurement whose answer is negative is the point, not a
  disappointment.** The measurement transaction's value was making a defensible
  out-of-sample judgement possible; the judgement came back negative, which is
  worth more than the parameter search it replaced.

- **Simulate a criterion's POWER, not just its null.** Round 393 registered
  "3 or more replicate" against a null expectation of 0.025 - which sounds
  strict but was nearly unreachable, since only four strategies were positive on
  the first holdout at all. Eight pre-registrations in this arc have been
  mis-specified the same way: chosen for how demanding they sound rather than
  for what the test can detect. Before registering, simulate both the null AND a
  plausible effect.
- **Check the base rate before calling something a search space.** 7.6% of
  strategy-holdout cells are positive where coin flips would give ~50%. The
  library does not contain rare winners among neutral candidates; it loses out
  of sample ~92% of the time. That reframes "which strategy" as the wrong
  question.

- **Match production strategies to sweep entries by PARAMETER, not by id.**
  `production_candidates` uses ids like `candle_momentum`; `candidates()` uses
  parameterised labels like `candle_momentum_10bps`. A name lookup finds nothing
  and invites the false conclusion that the two sets are disjoint. Read the
  constructor arguments in `strategies.rs` and match on those.
- **Compare the Alpha inputs' total to the Portfolio's output on the same
  holdout.** On `exness XAU` H1 the two production candidates lose -27.64 over
  4,081 trades and the Portfolio loses -0.38 over 160 - a 98.6% loss reduction
  with a 65% per-trade improvement. This one comparison reframes which layer is
  worth optimising, and it costs nothing once trades are exported.

- **`--higher-timeframe-interval` unlocks a second 105-strategy MTF sweep.**
  Without it, `strategy_scores` contains only the plain `candidates()` library
  and every multi-timeframe strategy - including production's route-specific
  extras - is silently absent. No round in this arc's first 190 iterations
  passed it. Check which library a run actually scored before concluding
  anything is missing from the tool.
- **Before proposing a code change to close a coverage gap, grep for an existing
  function that already covers it.** Round 394 proposed adding production's MTF
  configurations to the sweep; three of the four were already present under
  parameterised labels behind a flag. The real gap was one parameter variant.

- **Decompose a pooled rate by window before comparing it to anything.** The
  MTF library's 16.3% positive-cell rate looked like double the plain library's
  7.6%; excluding one outlier window it is 8.7%. The entire difference was one
  period. Pool only after checking the per-window spread.

- **Subject negative results to the same robustness test as positive ones.**
  Rounds 391-392 put the one positive gross reading through four disjoint
  holdouts; round 390's three negative readings were accepted on one holdout
  each. Retesting one of them showed it is gross-POSITIVE on two of three. Only
  stress-testing the result that stands out is a selection asymmetry whichever
  way it points, and here it produced a published fleet characterisation that
  did not hold.
- **A single holdout does not characterise a route.** Every route measured on
  more than one disjoint holdout alternates in sign around zero. Require at
  least three before writing down a route's gross sign.

- **If the only thresholds available have a weak null, say so instead of
  reporting "criterion met".** At n=7 a Spearman threshold of -0.5 has an exact
  permutation p of 0.133; the observed value landed exactly on it. Reporting
  that as a met criterion would overstate it. Either gather more points first or
  report the direction and the p-value together.
- **Convert repeated qualitative claims into an interval once enough holdouts
  exist.** "Alternates around zero" became mean +0.089 with a 95% interval
  [-0.349, +0.527] - which says both that no edge is demonstrated AND that an
  edge of +/-0.5 is not excluded. The interval carries information the phrase
  did not.

- **Slide the window before believing a short-holdout result.** A 65-day holdout
  on `bybit XAUT` was net-positive at 7.07 trades/week - the arc's only
  joint-objective success - and both neighbouring windows, one overlapping it by
  33 days, were negative. Overlapping windows that disagree are stronger
  evidence against a reading than independent ones, because they share most of
  their data.
- **Do not pool overlapping windows into a holdout series.** Two new readings on
  a route already in the series would have raised n from 9 to 11 with correlated
  data. Keep the pooled estimate honest even when more numbers are available.
- **Check `holdout_calendar_days` against the 90-day minimum before reading any
  gate number.** On short-history routes most cutoffs are disqualified by length
  before their performance matters at all.

- **`decision_rate` is trades / decision_count - trade conversion, not decision
  production.** ~95-99.9% of closed bars already produce a decision record,
  mostly Hold, so the field does not measure the objective's "Make Decision
  rate". It is also absent from the gate report, so no proxy for that target is
  measurable on holdout at all. Record `n/a` for Target 2 WITH that reason, and
  do not invent a definition to report against.
- **Check a held log's build before treating a missing field as a defect.**
  Logs from before the measurement change have a four-field `one_target`; a
  missing key there is staleness, not a null. Assert `key in dict`, not
  `dict.get(key) is None`.

- **Audit the build provenance of every row in a published comparison table.**
  Two of five rows in the fleet table came from a commit whose measurement path
  was corrected twice afterwards. Re-running them showed no sign change here,
  but the check is cheap and the alternative is a table nobody can date.
- **Two of six routes cannot supply a qualifying holdout.** `binance XAU` loads
  its entire venue history at 262.8 bar-days, giving a 52.5-day holdout against
  a 90-day minimum - no `--days` value fixes that, and it needs ~6 months of
  forward time. `bybit XAUT` qualifies only at the newest cutoff. This bounds
  every fleet-level statement, including the pooled interval.

- **The live trade log is append-only and is now usable.** `trade_log.rs` has
  `ZADD` only - no trim, expiry or delete - so `ZCARD`/`ZCOUNT` over
  `trades:<route>` counts every close since the worker started. It held 1-6
  closes at round 357 and 60 at round 403; recount it as forward time accrues.
- **Anchor a live observation window on an event-independent reference and
  report the sensitivity.** Anchoring on the earliest close conditions on the
  data (r357/r358's bias), so the window is a lower bound and the rate an upper
  bound. Re-run the comparison with a longer window and report only what
  survives both.
- **A live-versus-backtest rate gap is not evidence the backtest is wrong when
  the two windows differ in length by 46x on a trending quantity.** Round 392
  measured that trend; it alone can explain a 2-4x gap between a 4-day live
  window and a 180-day holdout.

- **The live trade log pools THREE paper sizing scopes per route.**
  `paper-fixed-pct`, `paper-compounding-10pct` and `paper-risk-2pct` share one
  decision stream - identical `(entry_at, exit_at, side, close_reason)` tuples -
  and differ only in position size, by up to 1,372x. `ZCARD` therefore returns
  3x the distinct trade count. Always de-duplicate by that tuple, or filter on
  one `scope_id`, before computing any live rate.
- **Read what the records ARE before computing statistics on them.** Round 403
  verified the log was append-only, anchored its window carefully, used exact
  Poisson intervals and tested window sensitivity - and still reported a 3x
  artifact, because it never opened a payload. Rigour on the statistics does not
  compensate for not reading the data.

- **Writing a lesson into this file does not prevent repeating it.** Round 394
  recorded "match production strategies by PARAMETER, not by id"; round 395
  matched by name again and reported a coverage gap that round 406 found does
  not exist. When a rule here applies, open the constructor and read the
  arguments - do not rely on having written the rule.
- **The research sweep already covers every production candidate.** All six
  distinct production configs, including `mtf_stochastic_9_3_35_65_sma5` for
  gold, are in `candidates()`/`multi_timeframe_candidates()`. There is no
  coverage gap to close.

- **The sweep's MTF entries take their intervals from CLI arguments.** They
  correspond to production only when the run passes `--interval 5m
  --higher-timeframe-interval 4h`. With any other higher interval the entries
  keep the same names and core parameters but describe strategies production
  does not run - a name that looks right attached to a different thing.
- **Close a gap in the round that names it.** Rounds 394, 395 and 406 each named
  a limitation and moved on; two of them turned out to be the error itself.
  Enumerate every branch and match by constructor arguments in the same round,
  or do not claim the coverage question is settled.

- **`production_candidates` in `finance-research` is a MIRROR, not the live
  configuration.** The live binary is `finance-api`; its strategies come from
  `deployment_rules::configured_alpha_strategies`. The two have drifted: both
  BTC routes run a seventh strategy, `mtf_stochastic_4h_1d_sma50` (4h base / 1d
  higher), that the mirror omits. Read the live definition, and confirm against
  `contributing_strategies` in the live trade payloads.
- **Check the deployed image tag before reasoning about "what production runs".**
  `docker ps` shows `finance-live-action_sha-<commit>`; compare it to
  `origin/main` and check whether any intervening commit touches application
  code rather than CI.
- **A strategy can be unscoreable at the intervals you always run.** The seventh
  strategy's core parameters exist in the sweep, but every MTF run in this arc
  used `5m`/`4h` while it runs at `4h`/`1d`. Matching parameters is not enough -
  match the intervals too.

- **All seven distinct production strategies lose on holdout.** Measured at each
  one's own intervals, best figure anywhere is -0.05; the seventh
  (`mtf_stochastic` 4h/1d sma50) shows train-positive / validation-negative /
  holdout-more-negative on 11 trades, the shape `strategies.rs` itself calls
  disqualifying - on a strategy that is deployed. Do not re-run this scan; it is
  complete and uniform.

## Communication

The standing `/loop` prompt for this project requires Vietnamese-only
responses to the user (Rule 0) — keep that even when this skill's own
documentation and code comments are in English, matching the codebase's
existing convention.
