## ADDED Requirements

### Requirement: The research tool measures the configuration it names

Every Portfolio report SHALL be produced by a replay that applies the
`PortfolioConstructionState` construction guard and the `PortfolioRiskLayer`.
The daily-profit gate SHALL use that same replay. A minimum-hold value SHALL be
accepted together with the gate. Any stream that bypasses the guard or the risk
layer SHALL be reported only as an explicitly labelled control, never as the
configuration's own score.

#### Scenario: Gate and Portfolio path agree exactly

- **WHEN** the gate and the Portfolio-faithful report are run over the same
  window at the deployed default minimum-hold value
- **THEN** both report identical trade counts and identical realized PnL

#### Scenario: A hold-bearing configuration can be gate-scored

- **WHEN** a run specifies both `--daily-profit-gate` and a minimum-hold value
- **THEN** the run is accepted and produces a gate verdict for that
  configuration

#### Scenario: The unguarded stream remains visible as a control

- **WHEN** a gate report is produced
- **THEN** the output contains both the guarded figures and the unguarded
  `legacy_selected_rule` control under distinct names

### Requirement: Out-of-sample segments are disjoint

The tool SHALL provide an anchored walk-forward mode producing contiguous,
non-overlapping out-of-sample segments that cover the window exactly once. Each
segment SHALL be evaluated using only bars strictly earlier than that segment.
Segment results SHALL be reported individually and SHALL NOT be pooled into a
single figure. The existing trailing-holdout mode SHALL remain available and
SHALL remain the default.

#### Scenario: Segments do not overlap

- **WHEN** walk-forward evaluation runs with N segments
- **THEN** the segment boundaries are contiguous and disjoint and together cover
  the window exactly once

#### Scenario: No segment observes its own future

- **WHEN** a segment is evaluated
- **THEN** no bar at or after that segment's end has been observed by the fit
  that produced its decisions

#### Scenario: Default behaviour is unchanged

- **WHEN** a run does not request walk-forward
- **THEN** its output is unchanged from the trailing-holdout behaviour

### Requirement: The joint objective is measurable on the Portfolio path

The Portfolio-faithful report SHALL expose profit factor, win rate, Sharpe
ratio, Sortino ratio, maximum drawdown, longest negative-day streak, SQN,
decision rate and cost-to-gross ratio. Daily bucketing SHALL use the operational
timezone. A metric whose inputs are insufficient SHALL be reported as absent and
SHALL NOT be reported as zero. Each metric SHALL have exactly one implementation
shared by every report that emits it.

#### Scenario: Metrics accompany the Portfolio figures

- **WHEN** a Portfolio report is produced
- **THEN** it contains the joint-objective metrics alongside trades and realized
  PnL

#### Scenario: An unsupported metric is absent, not zero

- **WHEN** a report covers a period with no losing trades
- **THEN** profit factor is reported as absent rather than as zero

### Requirement: Execution is auditable at the trade level

The tool SHALL be able to emit one record per closed trade, containing entry and
exit time, price, side, quantity, fees, slippage, funding and exit reason.
Emission SHALL be opt-in and SHALL NOT alter the default output contract. The
emitted records SHALL reconcile with the reported aggregate.

#### Scenario: Emitted trades reconcile with the aggregate

- **WHEN** per-trade emission is enabled for a run
- **THEN** the summed PnL of the emitted records equals the reported realized
  PnL within floating-point tolerance

### Requirement: The tool refuses to publish a score it cannot support

A strategy whose required input is unavailable for a route SHALL be reported as
excluded with a reason and SHALL NOT be scored. A defaulted or absent input
SHALL NOT be substituted so that the strategy runs anyway. A result row with
zero trades SHALL report zero realized PnL, with any holding-cost accrual in a
separate explicitly named field. Wrapper variants whose threshold cannot bind,
because the inner strategy's entry condition saturates the filtered metric,
SHALL be reported as a single entry.

#### Scenario: A missing input excludes rather than degrades

- **WHEN** a strategy requires a data column that is unavailable for the route
- **THEN** it is reported as excluded with a reason and carries no score

#### Scenario: A row that never traded reports no profit

- **WHEN** a strategy closes no trades in a period
- **THEN** its realized PnL is reported as zero and any funding accrual appears
  in its own field

#### Scenario: An inert wrapper threshold is reported once

- **WHEN** several wrapper variants cannot differ because the inner strategy's
  entry condition saturates the filtered metric
- **THEN** they are reported as one entry rather than as several identical ones

### Requirement: Live trading behaviour is unchanged

This capability SHALL NOT alter live trading semantics. The construction guard,
the risk layer, and the execution ledger's behaviour SHALL be reused, not
modified. Changes to shared crates SHALL be additive only.

#### Scenario: Shared execution semantics are untouched

- **WHEN** the change is reviewed
- **THEN** the diff to shared execution code contains no behavioural change, and
  the existing shared-crate test suite passes unchanged
