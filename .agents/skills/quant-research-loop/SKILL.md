---
name: quant-research-loop
description: Run one round of the recurring "/loop" Quant Researcher session for finance-live-action's trading strategies (BTC/XAU across Binance/Exness) — research with honest holdout backtests, preserve raw evidence, and promote only actionable candidates through one stable OpenSpec + OPS change. Use whenever the user runs a recurring quant-optimization /loop targeting Portfolio-layer profitability and Make Decision rate for finance-live-action.
---

# Quant Research Loop

One round of the recurring BTC/XAU trading-strategy research session. Each
round must produce a genuine improvement: a new validated candidate, a closed
(honestly falsified) candidate, a real bug found, a metric improvement, or a
shipped fix — never a no-op round.

## Read first

- `raw/researcher/SUMMARY-priority-backlog.md` — navigation doc, read before
  anything else each round. Lists closed directions (don't re-test), open
  leads, and infra gaps. Update it, don't recreate it, when a direction opens
  or closes.
- `openspec/changes/` and `.ops/changes/` — inspect active promoted engineering
  work and its execution evidence. `raw/handoff_agent.md` is legacy history/
  index only and never owns task or lifecycle status.
- Load `repository-delivery` and `quant-pipeline-development` (finance-live-action)
  for the underlying commit/CI/Coolify mechanics this skill's dev-mode step 5
  drives — this skill adds the research/backtest/production-verification layer
  on top, it does not replace them.

## Round structure

1. **Check Codex status.** `git -C <repo> log --oneline -3` in both
   `finance-mw` and `finance-live-action`. New commits since last round mean
   Codex is active — review and verify its Verify-section items instead of
   implementing yourself. No new commits for several rounds plus an explicit
   user statement that Codex is out of quota means full ownership: research
   **and** implement **and** review, until the user says otherwise (see
   "Codex-down mode" below).
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
   NEEDS-MORE-RESEARCH, or PROMOTE. Only PROMOTE may enter OpenSpec + OPS.
6. **Promote, if actionable** — require defensible evidence, clear scope,
   acceptance criteria, risk/trading safety, and rollback; see "Promotion and
   Codex-down mode" below.
7. **Document** research evidence (see "Research evidence and promotion").
8. **Clean up**: remove temp files under `/tmp`, close the SSH tunnel, confirm
   `git status --short` is clean in both repos before ending the round.

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
- `--daily-profit-gate` evaluates the *real currently-deployed* Portfolio
  decision policy on holdout only (Sharpe/Sortino/streak/frequency) — it does
  not let you pick an arbitrary candidate. The plain sweep table (no gate
  flag, optionally with `--higher-timeframe-interval <interval>` to include
  MTF trend-filtered candidates) scores arbitrary candidates on PF/win-rate
  only. There is no tool to get extended metrics (Sharpe/Sortino/streak) for
  an arbitrary candidate — don't invent one; report PF/win-rate honestly and
  say so if extended metrics are unavailable.
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
repeat the value anywhere (including in `raw/handoff_agent.md`), flag it to
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

## Promotion and Codex-down mode

Only a result classified PROMOTE enters engineering. Derive one stable,
meaningful kebab-case change name, create/reuse complete native OpenSpec
artifacts that reference the research evidence, then enter the existing
`/ops:run` lifecycle with the same change name. Attach immutable origin
references with `ops-runtime.sh trace-origin` during PLAN. Never implement
runtime code directly from a research-only result and never copy the OPS state
machine into the research command.

Codex-down mode is triggered by an explicit user statement that Codex is out of quota (check
current memory for the standing instruction and its scope/end condition
before assuming it still applies — it toggles back the moment the user says
Codex has resumed). While active:

1. Route an actionable implementation through the existing `/ops:run`
   lifecycle in the current top-level Claude session; do not modify runtime
   code outside that lifecycle. The transaction must be initialized with the
   explicit `claude-fallback quant-fallback` backend only while the current
   quant state reports `codex_available=false`. The runtime persists that
   backend and `claude-fallback-self-review`; a later `codex-on` affects only
   new transactions. Read a sibling implementation first — e.g. an existing
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
   message and `Co-Authored-By: Claude <noreply@anthropic.com>`.
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

1. **`raw/reports/optimize_loop_update_v2.csv`** — one row per
   instrument/broker/strategy combination touched this round. Columns:
   `round_date,round_seq,layer,instrument,broker,market_type,base_interval,
   strategy_or_rule,data_source,trades,win_rate_pct,rr_ratio,profit_factor,
   sharpe_ratio,sortino_ratio,information_ratio,net_pnl_usd,
   starting_equity_usd,trades_per_week_est,max_drawdown_duration_days,
   max_consecutive_losses,ulcer_index,sqn,skewness,kurtosis,
   target1_profitable,target2_makedecision,target3_freq_ge1day_or_7week,notes`.
   Leave a metric blank rather than fabricating it when the tool didn't
   report it.
2. **`raw/researcher/round<N>-<slug>.md`** — full writeup: methodology,
   numbers, honest caveats, comparison to prior rounds when relevant. When a
   round corrects an earlier round's conclusion, add a visible `⚠️
   CORRECTION` banner at the top of the original file pointing at the new
   one — never silently edit history. When a round only extends an existing
   thread with a small addendum, append a `## Cập nhật Round <N>` section to
   the existing file instead of creating a near-duplicate new one.
3. **`raw/researcher/SUMMARY-priority-backlog.md`**: refresh the relevant
   direction so the next round can navigate open/closed research without
   treating it as engineering task state.

For REJECTED, NO-CHANGE, DATA-ISSUE, or NEEDS-MORE-RESEARCH, stop after raw
evidence. For PROMOTE, reference these paths from OpenSpec and OPS origin
metadata; do not copy report contents and do not write an implementation task
to `raw/handoff_agent.md`.

## Communication

The standing `/loop` prompt for this project requires Vietnamese-only
responses to the user (Rule 0) — keep that even when this skill's own
documentation and code comments are in English, matching the codebase's
existing convention.
