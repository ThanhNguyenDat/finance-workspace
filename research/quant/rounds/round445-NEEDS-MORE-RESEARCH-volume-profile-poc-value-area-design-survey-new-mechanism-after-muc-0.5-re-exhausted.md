# Round 445 — NEEDS-MORE-RESEARCH: Volume Profile (POC / Value Area) design survey, genuinely new mechanism found via multi-source search after mục 0.5 re-exhausted at round444

Date: 2026-09-04. Coordinator session `529d401a-77d9-4d8f-8dde-789ffef0b431`,
research-state iteration 247 (recorded once by the launcher before this
prompt — `begin-iteration` not called). Round-file/commit sequence (the
authoritative counter per the loop's own instructions) is 445, the number
immediately after round444.

## Why this round searched instead of backtesting directly

Round444 closed item 6/6 of `index.md` mục 0.5 (Hurst regime filter), leaving
**both** the internal backlog (mục 3, ~93 closed directions) and mục 0.5 (all
6 user-proposed post-round432 directions) with zero open leads. This is the
**first** round since that closure — not a second or later consecutive
search-failure round — so per the command's own escalation order the correct
action is a fresh multi-source search for a new mechanism/technique, not yet
a provider pin (`agent-role-state pin quant_research codex`). No pin applied
this round.

## Search

Two `WebSearch` queries, plus a third narrowed to XAU/community sources per
the command's instrument-specific guidance:

1. `volume profile point of control value area trading strategy backtest crypto forex`
2. `simple machine learning gradient boosting logistic regression intraday trading signal OHLCV features backtest`
3. `r/algotrading volume profile gold XAUUSD strategy reddit`

Two candidate mechanisms surfaced, screened against the full mục 3 closed-list
(93 rows) and mục 0.5 (6 rows, all now closed) read in this round before any
design work:

### Item 7 (new) — Volume Profile / Market Profile: POC + Value Area breakout-or-reversion

Sources:
- [Volume Point of Control and Value Area Analysis for Trading](https://medium.com/@pyquantlab/volume-point-of-control-and-value-area-analysis-for-trading-cd545c2e081b) (Medium, pyquantlab)
- [Volume profile indicators: basic concepts](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/) (TradingView docs — describes the standard retail approximation of distributing each bar's volume across its own high-low range when tick-level data isn't available, which is exactly the data shape this repository has: `Kline.volume` is a single per-candle total, no intra-candle tick distribution)
- [VAH Entry / VAL Exit Xauusd by TheMarketVengeance](https://www.tradingview.com/script/sylmBxzG-VAH-Entry-VAL-Exit-Xauusd-by-TheMarketVengeance) (TradingView community script, XAUUSD-specific — matches this program's XAU-first priority)
- [Volume Profile Trading Strategy](https://www.tradezella.com/strategies/volume-profile-strategy) (Tradezella)

**Mechanism**: over a rolling N-closed-bar window, build a volume-by-price
histogram (each closed bar's `volume` distributed across evenly-spaced price
bins spanning its own `[low, high]` — the same simplification the TradingView
source describes as standard when only OHLCV is available, not a shortcut
invented for this survey). From the histogram derive:
- **POC** (point of control): the bin with the largest accumulated volume.
- **Value Area** (VAH/VAL): the contiguous bin range around the POC that
  contains a configurable fraction (canonically 70%) of total windowed
  volume.

Two opposite entry hypotheses, mirroring the `converge`/`diverge` pairing
round443 used for stat-arb and the `Trending`/`MeanReverting` pairing
round444 used for Hurst-gating — test both, do not assume the "textbook"
side wins:
- **breakout**: close crossing above VAH → `EnterLong`; below VAL →
  `EnterShort` (price accepted outside the prior balance area, trend
  continuation).
- **reversion**: close touching/exceeding VAH → `EnterShort`; VAL →
  `EnterLong` (fade back toward POC, price rejected outside balance).

**Why this is a genuinely new mechanism, not a variant of anything in mục
3/0.5**: every closed direction that touches volume is either (a) a pure
oscillator on total volume with no price-bin structure — On-Balance Volume
(round113), Money Flow Index (round114), taker buy/sell imbalance
(round72-75) — or (b) volume used only as a filter/confirmation threshold on
top of a price-only entry (`VolumeFilterStrategy`, `--min-volume`-style
gates). None of those build a **distribution of volume across price
levels** and read structural anchors (POC/VAH/VAL) off it. VWAP-based
`SessionVwapReversionStrategy` (round18/21, closed) is the closest existing
code — it is also volume-weighted — but it collapses volume into a single
mean+stddev band, not a full histogram with a mode (POC) and an asymmetric
70%-mass region, so it cannot express "price accepted outside the value
area" the way this mechanism does.

**Buildability — HIGH, evidence-based, not asserted:**
- `Kline` already carries every field needed
  (`crates/finance-core/src/kline.rs:9-23`: `high`, `low`, `close`, `volume`)
  — no schema change, no second data source, no new CLI plumbing beyond a
  new `Strategy` registration (unlike round434/437's cross-instrument work,
  which needed a second `MarketSubscription`/leader-broker CLI surface).
- The causal-accumulation pattern this needs already exists twice in
  `crates/finance-research/src/strategies.rs`: `SessionVwapReversionStrategy`
  (`:2965-3109`) accumulates `weighted_price`/`volume` per closed bar into a
  per-key `Mutex<HashMap<..>>` state and reads it back the same call —
  reusable almost verbatim for a rolling histogram keyed the same way
  (`kline.instrument.key():kline.timeframe`), with a `VecDeque` eviction of
  the oldest bar's bin contributions when the window exceeds N bars (same
  `while ... pop_front()` idiom `SessionVwapReversionStrategy` already uses
  for its `closes` buffer, and that `RealizedVolatilityRegimeFilterStrategy`
  (`:3859`) / `HurstRegimeFilterStrategy` (`:3990`) use for their own rolling
  windows).
- **No lookahead risk beyond the standard causal-window pattern already
  audited and shipped repeatedly in this program**: the histogram at
  evaluation time for bar *t* includes bar *t*'s own volume contribution —
  identical in kind to `SessionVwapReversionStrategy` including the current
  bar's typical price in its own running VWAP before comparing `kline.close`
  to the band. That is not a new risk class; it is the same "read what is
  knowable at this bar's own close" contract every strategy in this codebase
  already follows. This is a materially lower-risk shape than round434's
  cross-instrument as-of alignment (different trading calendars, genuinely
  new join logic) or round435's shared-risk-gate blast radius (four
  no-ledger-context call sites) — both of those correctly stopped at design
  survey for reasons that do not apply here.
- Registration point is a one-line addition to `strategies::candidates()`
  (`:5173`), same as every strategy added since round88.

**Open design parameters requiring a sweep, not a guess** (why this round
stops at design survey rather than implementing):
- **Bin count / bin width**: too coarse loses POC precision, too fine makes
  the 70%-mass Value Area noisy on thin windows — no principled default
  exists yet in this codebase (unlike ATR periods or RSI(14), which had
  literature precedent already used elsewhere in the program). Needs a small
  grid (e.g. 12/24/48 bins) rather than one arbitrary pick.
- **Lookback window N**: this determines whether POC represents "today's
  balance" (shift session-anchored, mirroring `SessionVwapReversionStrategy`)
  or a longer structural level (e.g. N=200-500 bars at 5m ≈ 16-42 hours).
  These are different trading claims and should not be conflated in one
  sweep cell without labeling which one is being tested.
- **breakout vs. reversion, and confirmation (volume-above-average at the
  crossing bar, per the TradingView source) vs. bare crossing** — at least a
  2×2 grid before trusting either hypothesis, same discipline round443/444
  applied to their own hypothesis pairs.

Writing the bin/window/hypothesis choices under this round's remaining
budget risked exactly the failure mode round434/435 named for their own
mechanisms: producing one plausible-looking number from an unswept,
arbitrarily-chosen configuration and mistaking it for evidence. Per the
command's own instruction ("ưu tiên ghi ý tưởng lại cho round sau nếu không
chắc"), this round records the design and defers implementation.

**Concrete next step**: a dedicated round adds `VolumeProfileStrategy` (new
`Strategy`, not a wrapper — no existing candidate needs gating) with the
`SessionVwapReversionStrategy` state-accumulation pattern reused for a
histogram instead of a single weighted mean, a rolling-window eviction unit
test (confirms an evicted bar's volume actually leaves the bins, the same
correctness class `HurstRegimeFilterStrategy`'s synthetic-fixture tests
cover for its own rolling estimator), a POC/VAH/VAL-on-known-distribution
unit test (uniform histogram → POC/VA boundary at a computable location,
skewed histogram → boundary shifts predictably), then a plain-sweep backtest
over {bin_count}×{window}×{breakout,reversion} on `exness XAU` first (this
program's stated priority) before `binance BTC`.

### Item 8 (new, lower priority — infra gap, not yet a backtest candidate) — simple ML classifier (gradient boosting / logistic regression) on standard OHLCV-derived features

Sources:
- [Forecasting Markets using eXtreme Gradient Boosting](https://blog.quantinsti.com/forecasting-markets-using-extreme-gradient-boosting-xgboost/) (QuantInsti)
- [My Quant Journey into Machine Learning: A Gradient Boosting Strategy](https://medium.com/@fyang1989/gradient-boosting-for-stock-market-prediction-a-tsla-case-study-backtest-f4dd2fb680fc) (Medium)
- [Cascading logistic regression onto gradient boosted decision trees](https://www.sciencedirect.com/science/article/abs/pii/S1568494619305289) (Elsevier — cascaded LR→GBDT feature pipeline)

**Why this is genuinely new**: every one of the ~93 closed mục 3 directions
and all 6 mục 0.5 directions is a hand-specified rule (indicator threshold,
crossover, pattern, regime gate, sizing formula). None fits a statistical
model to historical features to produce a direction/probability — this
would be the first learned (as opposed to hand-specified) signal in the
program's full 445-round history. This is explicitly one of the mechanism
classes the command names as a valid search target ("machine-learning
signal đơn giản").

**Why this stays lower priority instead of a design survey with a concrete
next step (unlike item 7)**: checked the actual buildability constraint
before writing anything hopeful —

```
$ grep -rn "linfa\|smartcore\|ndarray\|xgboost\|lightgbm\|candle" \
    --include="Cargo.toml" finance-live-action/
# (no output — no ML/numerical-array crate anywhere in the workspace)
```

`finance-research`/`finance-core`/`finance-strategy` are pure Rust with no
existing linear-algebra or ML dependency. Any simple-ML approach here is not
"wrap existing causal state in a new `Strategy`" (item 7's shape) but
"introduce a new compiled dependency to a workspace that already runs its
backtests inside a CPU/RAM-capped Docker container (2 CPU / 4 GB RAM / 2 GB
swap ceiling, per this skill's own resource contract)". That changes the
risk profile: build-time and binary-size impact of a crate like `linfa` or
`smartcore` inside that container cap is an unmeasured unknown, and picking
one without checking compiles-clean-under-cap first would itself be the kind
of ungrounded number this program's discipline exists to prevent. A future
round should first spike whether a minimal dependency (e.g. `linfa` logistic
regression, no GPU/BLAS pulled in) builds inside the existing
`docker/Dockerfile-research` image under the CPU/RAM cap before any feature
engineering or backtest work — that spike is the concrete next step, kept
separate from item 7's already-buildable design.

## Classification

**NEEDS-MORE-RESEARCH.** Zero containers, zero SSH tunnel, zero backtest
compute this round (same discipline as round434/435/442 for their own
design-survey rounds) — this round's evidence is the search, the mục 3/0.5
closed-list screen against 93+6 existing entries, and the concrete
file:line buildability check above, not a train/validation/holdout number.
No promotion, no OpenSpec/OPS transaction, no production change.

## Files updated

- `research/quant/index.md` — mục 0.5 reopened with item 7 (Volume Profile,
  concrete next step) and item 8 (simple ML, infra-spike next step) appended
  after the "6/6 mục đã đóng" round444 summary; header count updated to
  reflect the new open items.
- `research/quant/reports/optimize_loop_update_v2.csv` — one row, `round_seq`
  445, all backtest metric columns empty (no evidence produced), matching
  the round434/435/441 precedent for design-survey/status rounds.
- `research/quant/rounds/round445-*.md` — this file.
