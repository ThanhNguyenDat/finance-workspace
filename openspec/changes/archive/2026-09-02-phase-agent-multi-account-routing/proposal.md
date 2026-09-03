## Why

The operator has more than one Claude/Codex account (separate config
directories with independent auth and quota — for example
`CLAUDE_CONFIG_DIR=~/.claude-personal` and `~/.claude-work`). Today, when a
running phase attempt reports confirmed quota exhaustion, candidate
resolution can only fail over to a *different provider or model*
(`openspec/specs/ops-backend-routing/spec.md`, "Backend remains immutable
during a transaction": "a confirmed quota-interrupted phase MAY create a
continuation attempt through another eligible provider"). It has no notion
of a same-provider, same-model, different-account continuation, so a
transaction degrades to a weaker fallback model (or blocks entirely) even
when the *preferred* provider/model still has capacity left on a second
account.

## What Changes

- Extend a phase-agent candidate (`phase_agent_state.py`'s `candidate()` /
  the equivalent bash structure it replaces) with an optional `account`
  field alongside `provider`/`model`/`effort`, naming one entry in a fixed
  account registry rather than an arbitrary path.
- Add a small account registry per provider (`personal`, `work`, ... —
  named, not free-form paths) that resolves an account name to the
  environment variable the corresponding CLI reads for its config location
  (`CLAUDE_CONFIG_DIR` for Claude, `CODEX_HOME` for Codex).
- Track provider availability per `(provider, account)` pair instead of only
  per `provider`, so one account's confirmed quota exhaustion does not mark
  a different account on the same provider unavailable.
- Extend the existing quota-exhaustion continuation path (candidate list
  iteration in `run-phase-agent.sh`/`run-phase-agent-command.sh`) to treat a
  same-provider, different-account candidate as an eligible continuation
  target, using the exact same confirmed-exit/checkpoint/continuation-mode
  contract the current provider-to-provider failover already uses — no new
  failover semantics, only a wider set of eligible next candidates.
- Candidates without an explicit `account` keep resolving through the
  provider's ambient environment exactly as today (backward compatible; no
  behavior change for any existing single-account configuration).

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `ops-backend-routing`: the candidate-resolution and quota-continuation
  requirements extend to cover per-account eligibility and availability,
  in addition to the existing per-provider behavior.

## Impact

- **Affected repository**: `finance-workspace` only (phase-agent
  orchestration tooling under `.agents/scripts/` and
  `.agents/orchestrator/`; see `phase-agent-python-orchestrator`, which this
  change should land after — see design.md).
- **Affected components**: `phase_agent_state.py`/`phase-agent-state.sh`
  (candidate schema, availability schema), `run-claude-phase.sh`,
  `run-codex-phase.sh`, `run-phase-agent-command.sh` (must resolve and
  export the selected candidate's account before spawning `claude`/`codex`),
  and their existing bash/pytest test suites.
- **Trading safety**: none directly — this is orchestration tooling, not
  trading code. It is safety-relevant to the OPS workflow the same way the
  existing routing/lock system is: incorrect account resolution could run a
  phase attempt under the wrong account's auth/quota, or (worse) silently
  reuse an account still mid-attempt from another concurrent process, so
  design.md must define account-level exclusivity explicitly.
- **Rollback**: candidates without an `account` field are unaffected;
  rollback is reverting the schema/resolution change, since no persisted
  state format becomes unreadable by the prior version if `account` is
  additive and optional throughout.
