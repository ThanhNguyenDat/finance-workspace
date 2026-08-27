# Historical Portfolio Replay: Shared-Driver Refactor

Spec for implementing the fix documented in `finance-mw/raw/todo.md` ("finance-live-action: Portfolio multi-rule replay (Phase 2)"). Written to be implemented directly — exact struct shapes, function signatures, and call-site diffs below, all against `/home/lap17204/Desktop/finance/finance-live-action`.

## Context

Portfolio can run several concurrently-configured execution rules (Phase 1, already shipped — `deployment_rules.rs` → `Vec<PortfolioExecutionConfig>`, each its own scope/ledger). We now want to run several *sizing modes* concurrently too (e.g. `fixed_notional`, `equity_fraction`, and a new ATR/risk-based mode), which makes N>1 configured rules the normal case, not a rare one.

That's currently blocked: `config.rs`'s `multi_rule_replay_conflict()` panics at startup if N>1 rules are configured while historical replay is enabled, because of a real correctness bug (not just a restriction) found during Phase 1's investigation. This fix must land *before* multi-mode is enabled in production.

## The bug

`crates/finance-api/src/trading_api.rs`:

- **Realtime** (lines ~1421-1558, esp. 1485-1554) computes target ONCE per tick from ONE shared `inner.portfolio_construction` (`target = inner.portfolio_construction.construct(decision)`, line 1485), loops every configured rule's own risk layer/ledger against that one target (line 1488, `layer.execution_target(&mut inner.portfolio_construction, ...)` — same shared object every iteration), collects every rule's execution outcome, and only after the full per-rule loop finishes folds ALL of them into the shared construction (`for outcome in execution_outcomes { inner.portfolio_construction.observe_execution(outcome); }`, lines 1552-1554).
- **Historical replay** does not mirror this. `new_historical_portfolio_replays()` (1843-1869) builds N fully independent `HistoricalPortfolioReplay` structs (182-197: `scope_id, ledger, evidence, construction, risk_state, primary_interval, pending_primary_kline, processed_primary_klines`) — one per configured rule, each owning its OWN `evidence` and OWN `construction`. Each replay's `apply_historical_portfolio_kline_with_no_lookahead` (1939-2009) independently does evidence-ingest → decide → construct → risk-evaluate → execute → `replay.construction.observe_execution(outcome)` (2003), using only that ONE rule's own outcome — never other rules'. So each rule's final `construction` end-state is NOT what the correct shared-fold realtime design would have produced for the same tick sequence.
- `commit_historical_portfolio_replay` (2047-2091) compounds this: when a replayed scope is a forward-continuation source (`continue_forward_from_replay`, 1809-1834), it does `inner.portfolio_construction = replay.construction.clone()` (line 2064) — **unconditionally overwriting the ONE shared `inner.portfolio_construction`** with whichever rule's independently-computed (already-wrong) construction commits last, in the loop at `historical_replay.rs:244-254`. Harmless at N=1 (only one candidate, which saw every outcome there is). A real correctness bug at N>1.

## The fix

Split `HistoricalPortfolioReplay` into a shared driver (evidence + construction, one instance) and per-rule replays (ledger + risk_state only), and restructure the per-kline apply function to mirror the realtime pattern exactly: one shared target, N-way risk/execute fan-out, N-way outcome fold-back into the one shared construction.

### 1. Struct changes — `crates/finance-api/src/trading_api.rs`

Replace lines 182-197:

```rust
pub(crate) struct HistoricalPortfolioReplay {
    scope_id: String,
    ledger: SimulatedLedger,
    evidence: MultiTimeframeEvidenceBook,
    construction: PortfolioConstructionState,
    risk_state: PortfolioRiskState,
    primary_interval: String,
    pending_primary_kline: Option<Kline>,
    processed_primary_klines: usize,
}

impl HistoricalPortfolioReplay {
    pub(crate) fn scope_id(&self) -> &str {
        &self.scope_id
    }
}
```

with:

```rust
/// The ONE shared evidence book, net-target construction state, and
/// primary-kline bookkeeping that every configured Portfolio execution rule
/// replays against — the historical counterpart of the realtime path's single
/// `inner.portfolio_evidence` / `inner.portfolio_construction`
/// (~trading_api.rs:1421-1558). Exactly one `HistoricalPortfolioDriver` exists
/// per replay run, regardless of how many Portfolio execution rules are
/// configured.
pub(crate) struct HistoricalPortfolioDriver {
    evidence: MultiTimeframeEvidenceBook,
    construction: PortfolioConstructionState,
    primary_interval: String,
    pending_primary_kline: Option<Kline>,
    processed_primary_klines: usize,
}

/// One configured Portfolio execution rule's own ledger and risk state,
/// replayed against the shared `HistoricalPortfolioDriver`'s net target — the
/// historical counterpart of realtime's per-rule `SimulatedLedger` +
/// `PortfolioRiskState` pair keyed by `portfolio_scope_id` in the realtime
/// execution loop.
pub(crate) struct HistoricalPortfolioRuleReplay {
    scope_id: String,
    ledger: SimulatedLedger,
    risk_state: PortfolioRiskState,
}

impl HistoricalPortfolioRuleReplay {
    pub(crate) fn scope_id(&self) -> &str {
        &self.scope_id
    }
}
```

### 2. Function changes — `crates/finance-api/src/trading_api.rs`

**`install_historical_funding_schedule`** (1708-1728): only the parameter type changes, body unchanged (still only touches `.ledger`):

```rust
pub(crate) fn install_historical_funding_schedule(
    &self,
    alpha_replays: &mut BTreeMap<String, SimulatedLedger>,
    portfolio_replays: &mut [HistoricalPortfolioRuleReplay],
    schedule: &[FundingSettlement],
) -> Result<(), FundingScheduleError> {
```

**`new_historical_portfolio_replays`** (1842-1869) → split into two:

```rust
/// Builds the ONE shared evidence/construction driver for a historical
/// Portfolio replay run. Evidence policy and minimum holding decisions are
/// account-wide already — every configured rule's `PortfolioReplaySemantics`
/// carries an identical `decision_policy` and `minimum_holding_decisions`
/// (trading_api.rs:686-727, sourced from the one shared
/// `AppConfig::portfolio_minimum_holding_decisions`) — so it is safe to
/// source both from whichever configured rule is encountered first. Returns
/// `None` only when no Portfolio execution rule is configured.
pub(crate) fn new_historical_portfolio_driver(&self) -> Option<HistoricalPortfolioDriver> {
    let context = self.historical_portfolio_contexts().next()?;
    let semantics = self.portfolio_replay_semantics.get(&context.scope_id)?;
    Some(HistoricalPortfolioDriver {
        evidence: MultiTimeframeEvidenceBook::new(
            self.symbol.clone(),
            semantics.decision_policy.clone(),
        ),
        construction: PortfolioConstructionState::with_minimum_holding_decisions(
            self.symbol.clone(),
            semantics.minimum_holding_decisions,
        ),
        primary_interval: self.interval.clone(),
        pending_primary_kline: None,
        processed_primary_klines: 0,
    })
}

/// One replay per configured Portfolio execution rule, each owning only its
/// own ledger and risk state. The net target and Portfolio Construction state
/// they replay against live on the ONE shared `HistoricalPortfolioDriver`
/// returned by `new_historical_portfolio_driver`, not here.
pub(crate) fn new_historical_portfolio_rule_replays(&self) -> Vec<HistoricalPortfolioRuleReplay> {
    self.historical_portfolio_contexts()
        .map(|context| HistoricalPortfolioRuleReplay {
            scope_id: context.scope_id.clone(),
            ledger: SimulatedLedger::new(
                context.strategy_id.clone(),
                self.interval.clone(),
                self.simulation_for(&context.scope_id),
            ),
            risk_state: PortfolioRiskState::default(),
        })
        .collect()
}
```

(`simulation_for`, `rule_for`, `sizing_for` untouched.)

**`apply_historical_portfolio_kline` / `apply_historical_portfolio_kline_with_no_lookahead`** (1930-2009) → replace both with:

```rust
pub(crate) fn apply_historical_portfolio_kline(
    &self,
    kline: &Kline,
    alpha_ledgers: &BTreeMap<String, SimulatedLedger>,
    driver: &mut HistoricalPortfolioDriver,
    replays: &mut [HistoricalPortfolioRuleReplay],
) {
    drop(self.apply_historical_portfolio_kline_with_no_lookahead(
        kline,
        alpha_ledgers,
        driver,
        replays,
    ));
}

pub(crate) fn apply_historical_portfolio_kline_with_no_lookahead(
    &self,
    kline: &Kline,
    alpha_ledgers: &BTreeMap<String, SimulatedLedger>,
    driver: &mut HistoricalPortfolioDriver,
    replays: &mut [HistoricalPortfolioRuleReplay],
) -> Vec<NoLookaheadObservation> {
    let mut no_lookahead = BTreeMap::new();
    for item in self.alpha_position_evidence(WorkflowKind::Backtest, kline, alpha_ledgers) {
        if let Err(error) = driver.evidence.ingest(item) {
            tracing::warn!(%error, "Discarding invalid historical portfolio evidence");
        }
    }
    if kline.timeframe == driver.primary_interval {
        driver.pending_primary_kline = Some(kline.clone());
    }
    if let Some(primary) = driver.pending_primary_kline.as_ref() {
        for observation in driver.evidence.no_lookahead_observations(primary.close_time) {
            no_lookahead.insert(observation.interval.clone(), observation);
        }
    }
    let synchronized_primary = driver
        .pending_primary_kline
        .as_ref()
        .filter(|primary| driver.evidence.is_synchronized(primary.close_time))
        .cloned();
    if let Some(primary) = synchronized_primary {
        // Computed ONCE per synchronized primary close and executed by every
        // configured rule against its own risk layer/ledger — mirrors the
        // realtime block at trading_api.rs:1485-1554 exactly, including
        // folding every rule's execution outcome back into this ONE shared
        // `driver.construction` only after the full per-rule loop finishes.
        let decision = driver.evidence.decide(primary.close_time);
        let target = driver.construction.construct(decision);
        let risk_sequence = driver.processed_primary_klines.saturating_add(1) as u64;
        let mut execution_outcomes = Vec::new();
        for replay in replays.iter_mut() {
            let Some(layer) = self.portfolio_risk_layers.get(&replay.scope_id) else {
                tracing::error!(
                    scope_id = %replay.scope_id,
                    "Historical Portfolio context is missing its risk layer"
                );
                continue;
            };
            let current_position = replay.ledger.position().cloned();
            let risk_outcome = layer.evaluate_historical(
                &mut replay.risk_state,
                PortfolioRiskEvaluation {
                    target: &target,
                    current_position: current_position.as_ref(),
                    performance: replay.ledger.performance(),
                    equity: replay.ledger.equity(),
                    simulation: replay.ledger.simulation_config(),
                    mark_price: primary.close,
                    evaluated_at: primary.close_time,
                    sequence: risk_sequence,
                },
            );
            if let PortfolioRiskOutcome::Rejected { rejection, .. } = &risk_outcome
                && should_log_historical_portfolio_rejection(rejection.rejected_count)
            {
                tracing::warn!(
                    scope_id = %replay.scope_id,
                    gate = rejection.gate.as_str(),
                    reason = %rejection.reason,
                    rejected_count = rejection.rejected_count,
                    "Historical Portfolio target rejected by risk management"
                );
            }
            let execution_target =
                layer.execution_target(&mut driver.construction, &target, &risk_outcome);
            if let Some(execution_target) = execution_target {
                execution_outcomes.push(replay.ledger.execute_target(&primary, &execution_target));
            }
        }
        for outcome in execution_outcomes {
            driver.construction.observe_execution(outcome);
        }
        driver.pending_primary_kline = None;
        driver.processed_primary_klines += 1;
    }
    no_lookahead.into_values().collect()
}
```

`alpha_position_evidence` (2011-2045) unchanged.

**`commit_historical_portfolio_replay`** (2047-2091) → replace entirely with:

```rust
/// Commits every configured Portfolio execution rule's replayed ledger and
/// risk state, plus the ONE shared driver's Portfolio Construction state that
/// every rule's execution outcome was folded into during replay.
///
/// A rule ledger with a live forward counterpart that has not yet closed a
/// trade continues into that forward ledger exactly as before, per rule. The
/// ONE shared `inner.portfolio_construction` is assigned from the ONE shared
/// `driver.construction` at most once per call — never once per rule — and
/// only when at least one rule actually continued forward, so a multi-rule
/// replay can no longer have one rule's commit silently clobber another
/// rule's contribution to the account-wide target state.
pub(crate) async fn commit_historical_portfolio_replay(
    &self,
    driver: HistoricalPortfolioDriver,
    replays: Vec<HistoricalPortfolioRuleReplay>,
) -> bool {
    if driver.processed_primary_klines == 0 || replays.is_empty() {
        return false;
    }
    let mut inner = self.inner.write().await;
    let mut any_forward_continuation = false;
    for replay in replays {
        let replay_scope_id = replay.scope_id.clone();
        let replay_risk_state = replay.risk_state.clone();
        let forward_scope_id = self
            .forward_counterpart_scope(&replay_scope_id)
            .map(str::to_owned);
        if self.continue_forward_from_replay(&mut inner, &replay.scope_id, &replay.ledger) {
            any_forward_continuation = true;
            if let Some(forward_scope_id) = forward_scope_id {
                let forward_risk_state = self
                    .portfolio_risk_layers
                    .get(&forward_scope_id)
                    .expect("forward Portfolio context must have a risk layer")
                    .continue_state(&replay_risk_state)
                    .expect("valid replayed Portfolio risk state must rebind to forward scope");
                inner
                    .portfolio_risk_states
                    .insert(forward_scope_id, forward_risk_state);
            }
        }
        inner
            .simulated_ledgers
            .insert(replay.scope_id.clone(), replay.ledger);
        inner
            .portfolio_risk_states
            .insert(replay_scope_id, replay_risk_state);
        inner
            .historical_replay_completed_scopes
            .insert(replay.scope_id.clone(), driver.processed_primary_klines);
        inner
            .historical_replay_completed_at
            .insert(replay.scope_id, Utc::now());
    }
    if any_forward_continuation {
        // The forward ledger and target are one state transition. Carrying
        // only the open position(s) would make the next `Hold` target `Flat`
        // and immediately undo the replay continuation.
        inner.portfolio_construction = driver.construction;
    }
    let _ = self.updates.send(());
    true
}
```

`continue_forward_from_replay` (1809-1834) and `forward_counterpart_scope` (1836-1840) unchanged.

### 3. Call-site changes — `crates/finance-api/src/historical_replay.rs` (`bootstrap_pending_intervals`)

Replace lines 154-160:

```rust
    let portfolio_pending = runtime.historical_portfolio_replay_pending().await;
    // One shared driver plus one ledger/risk-state replay per configured
    // Portfolio execution rule.
    let mut portfolio_driver = if portfolio_pending {
        runtime.new_historical_portfolio_driver()
    } else {
        None
    };
    let mut portfolio_replays = if portfolio_pending {
        runtime.new_historical_portfolio_rule_replays()
    } else {
        Vec::new()
    };
```

Lines 165-169 (`install_historical_funding_schedule` call): unchanged text — only the flowed-through type of `portfolio_replays` changes.

Replace lines 189-205 (inner per-kline loop):

```rust
        if let Some(replay_ledgers) = alpha_ledgers.get_mut(&kline.timeframe) {
            runtime.apply_historical_replay_kline_to_ledgers(
                &kline.timeframe,
                &kline,
                &signals,
                replay_ledgers,
            );
            if let Some(driver) = portfolio_driver.as_mut() {
                for observation in runtime.apply_historical_portfolio_kline_with_no_lookahead(
                    &kline,
                    replay_ledgers,
                    driver,
                    &mut portfolio_replays,
                ) {
                    no_lookahead.insert(observation.interval.clone(), observation);
                }
            }
        }
```

Replace lines 244-254 (final commit block):

```rust
    if portfolio_inputs_complete
        && let Some(driver) = portfolio_driver
        && !portfolio_replays.is_empty()
    {
        let scope_ids = portfolio_replays
            .iter()
            .map(|replay| replay.scope_id().to_string())
            .collect::<Vec<_>>();
        if runtime
            .commit_historical_portfolio_replay(driver, portfolio_replays)
            .await
        {
            tracing::info!(
                symbol = %subscription.legacy_symbol(),
                scope_ids = ?scope_ids,
                "Historical portfolio replay applied"
            );
        }
    } else if portfolio_pending && !portfolio_inputs_complete {
```

(rest of the `else if` arm unchanged; let-chains already used elsewhere, e.g. `trading_api.rs:1988-1989`.)

### 4. Guard removal — `config.rs` / `main.rs` / docs

Once the shared driver lands, N>1 configured rules with replay enabled is correct by construction:

- `crates/finance-api/src/config.rs`: delete `multi_rule_replay_conflict` (lines 207-225, incl. doc comment) and its test `multi_rule_replay_conflict_only_rejects_more_than_one_rule_with_replay_enabled` (~1590-1596).
- `crates/finance-api/src/main.rs`: delete the `if let Some(error) = config::multi_rule_replay_conflict(...) { panic!("{error}"); }` block (~lines 65-69).
- `finance-mw/.agents/skills/trading-mode-synchronization/SKILL.md` (~lines 166-174): rewrite to state replay is now safe with any number of configured rules — no per-rule clobbering possible by construction. Delete/mark-done the corresponding `finance-mw/raw/todo.md` entry.

### 5. Contract version bump (18 → 19)

Append to the doc comment ending at `trading_api.rs:66` (match existing "Version N ..." style), then bump the constant on line 67:

```
/// Version 19 replays one shared evidence/construction driver across every
/// configured Portfolio execution rule instead of each rule building and
/// folding only its own execution outcome into an independent copy, so a
/// checkpoint's Portfolio construction state produced under the old per-rule
/// replay semantics must not be resumed as if every rule's outcome was
/// already folded into it.
pub(crate) const HISTORICAL_REPLAY_CONTRACT_VERSION: u32 = 19;
```

No `WorkerRuntimeState`/serialization changes needed — `restore_checkpoint_state` (2161-2176) already forces a fresh replay on any version mismatch, by design; no code change there.

### 6. Test changes (6 tests touch these symbols in `trading_api.rs`)

1. `authoritative_funding_is_installed_in_forward_and_replay_ledgers` (~3392): mechanical — `new_historical_portfolio_replays()` → `new_historical_portfolio_rule_replays()`; `.ledger` access unchanged.
2. `multiple_portfolio_rules_each_get_an_independent_scope_and_ledger` (~4460): no change (uses `sizing_for`/context helpers only).
3. `alpha_sizes_every_position_the_same_and_portfolio_uses_selected_rule` (~4709): no change (`sizing_for`/`rule_for` only).
4. `strategy_owned_protective_levels_apply_without_adding_alpha_contexts` (~4739): no change (`rule_for` only).
5. `historical_portfolio_replay_stays_within_the_weighted_lane` (~5908-6016): **rewrite in place** to the driver/replays split (swap `new_historical_portfolio_replays()` for `new_historical_portfolio_driver()` + `new_historical_portfolio_rule_replays()`, move `processed_primary_klines` assertions from per-replay to the shared driver, update `apply_historical_portfolio_kline`/`commit_historical_portfolio_replay` call shapes per the new signatures above). Same assertions, same N=1 output — this is the regression-free proof for today's only production shape.
6. **New test** `historical_portfolio_replay_folds_every_rules_outcome_into_the_shared_construction`: configure **two** rules with divergent protective stops (one tight enough to trip on the existing stop-kline fixture, one wide enough not to), replay both through the same kline sequence, commit, and assert the shared `portfolio_construction.current_target()` reflects the **tight** rule's protective exit (`Flat` / `protective_exit_waiting_for_fresh_insight`) even though the wide rule is configured *last* (and would incorrectly win under the pre-fix "last commit wins" code). This is the concrete regression test proving the bug is fixed, not just refactored around.
7. `historical_portfolio_replay_exposes_no_lookahead_for_every_input` (~6018-6062): mechanical rewrite to driver/replays split; assertions unchanged (N=1, identical output).

### 7. Verification checklist

1. `cargo build -p finance-api` — clean; `grep -rn "HistoricalPortfolioReplay\b" crates/finance-api/src/` returns zero hits (old name fully gone).
2. `cargo fmt --all -- --check`.
3. `cargo test -p finance-api` (or targeted `historical_portfolio`/`multi_rule_replay` — the latter should report "no tests", not a failure, since the guard test was deleted).
4. `cargo clippy -p finance-api --all-targets` (match whatever flags the repo's CI already uses).
5. **N=1 identical-output check**: rewritten test 5 above must assert the exact same trade count / `Flat` end state / reason string as before the refactor — concrete evidence single-rule production behavior is unchanged. Checkpoints will *not* resume across the deploy that lands this (18→19 forces one fresh replay on first restart) — expected, not a regression, and should be called out in the commit message.
6. New test 6 above must fail if run against the pre-refactor code (mentally trace, or diff-check) — that's the actual proof the bug is fixed.
7. Re-grep `trading_api.rs` for `new_historical_portfolio_replays\|HistoricalPortfolioReplay\|commit_historical_portfolio_replay\|apply_historical_portfolio_kline` after the edit — expected surviving symbols only: `new_historical_portfolio_driver`, `new_historical_portfolio_rule_replays`, `HistoricalPortfolioDriver`, `HistoricalPortfolioRuleReplay`, `commit_historical_portfolio_replay`, `apply_historical_portfolio_kline`, `apply_historical_portfolio_kline_with_no_lookahead`.

## After this lands

Once verified, the follow-up (separate task, not part of this refactor) is enabling multiple concurrent Portfolio sizing modes in `deployment_rules.rs` — `fixed_notional`, `equity_fraction`, and a new ATR/risk-based `PositionSizing` variant (risk % per trade still needs to be chosen before that mode is added). That work depends on this fix landing first.
