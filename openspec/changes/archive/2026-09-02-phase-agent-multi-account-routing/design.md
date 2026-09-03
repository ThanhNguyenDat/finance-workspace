## Context

See `proposal.md - Why` for motivation. Relevant current-state facts:

- Candidate resolution and quota-exhaustion continuation already exist
  (`phase-agent-state.sh resolve`, the candidate-iteration loops in
  `run-phase-agent.sh` and `run-phase-agent-command.sh`); this change adds a
  new eligibility dimension to that existing mechanism, it does not invent
  continuation from scratch.
- `phase-agent-python-orchestrator` (a separate, in-flight change) is
  porting `phase-agent-state.sh`/`quant-research-state.sh`/`ops-runtime.sh`
  to Python with byte-identical behavior. This change touches exactly the
  candidate schema and resolution logic that port owns. **This change must
  land after `phase-agent-python-orchestrator` reaches FINAL_VERIFY and is
  merged**, so it is built once, on the Python implementation, instead of
  twice (once in bash, once ported again).
- Multiple OPS transactions can be active concurrently
  (`ops-runtime.sh active` already enumerates more than one running
  change), so an account is a resource shared **across changes**, not just
  within one change's existing per-change/per-repository locks.
- The operator's environment already carries the account-selecting variable
  names this design reuses: `CLAUDE_CONFIG_DIR` (Claude) and `CODEX_HOME`
  (Codex) — confirmed via `codex --help` and the running session's own
  environment during this change's exploration.

## Goals / Non-Goals

**Goals:**
- A candidate may name an account; an unnamed account behaves exactly as
  today (Goal: zero behavior change for any operator with one account).
- Quota exhaustion on one account of a provider does not block a sibling
  account of the same provider from being selected.
- Two different phase attempts (in the same or different OPS transactions)
  can never run concurrently under the same resolved account.

**Non-Goals:**
- No UI or interactive account-setup flow. Registering an account is
  setting one environment variable in the operator's shell profile.
- No secret/credential management. This design only selects *which config
  directory* a CLI reads; it does not create, rotate, or store credentials.
- No change to how `phase-agent-python-orchestrator` itself is verified;
  this change starts only once that one is done (see Context).
- No cross-provider load balancing policy (e.g. "prefer the account with
  more remaining quota"). Selection order is still the existing ordered
  candidate list; only the failover *eligibility* rule is extended.

## Decisions

**1. Account registry is environment-driven and dynamic, not a fixed name
list in source.**
An account is any name `<NAME>` for which
`PHASE_AGENT_<PROVIDER>_ACCOUNT_<NAME>_DIR` is set in the environment
(`PROVIDER` is `CLAUDE` or `CODEX`, `NAME` is upper-cased,
e.g. `PHASE_AGENT_CLAUDE_ACCOUNT_WORK_DIR=/home/.../.claude-work`). A
candidate's `account` field is lower-case and matched case-insensitively
against these. This keeps every host-specific path out of committed source
(this repo already avoids hardcoding secrets/paths in code where it can);
adding a third account is exporting one more environment variable, not
editing Python/bash source.
*Alternative considered*: hardcode a fixed account name list in
`phase_agent_state.py` with env-var-sourced values only — rejected because
the operator would need a source edit (plus this change's own review cycle)
just to add or rename an account, which the environment-driven approach
avoids entirely.

**2. Availability is tracked per `(provider, account)`, keyed by account
name, only for accounts actually referenced by a candidate.**
`phase-agent-state.sh`'s `providers.<provider>` gains an optional
`accounts` map: `providers.codex.accounts.work = {available, reason,
observed_at, next_probe_at}`, structurally identical to today's per-provider
record. `providers.<provider>.available` (no account) keeps meaning
"account-less resolution," unchanged. `provider-result` gains an optional
account argument; omitting it updates the existing account-less record
exactly as today.
*Alternative considered*: flatten to a single map keyed by
`"provider:account"` — rejected; nesting under the existing
`providers.<provider>` keeps `provider-result`/`resolve`'s existing
account-less call sites correct with zero change, and the account map is
simply absent for an operator who never names one.

**3. A new cross-change account lock serializes concurrent use of the same
`(provider, account)`, mirroring the existing repository lock exactly.**
Two different OPS transactions (or a transaction and the quant-research
launcher) can be active at once (Context), so account exclusivity cannot
ride on the existing per-change lock. Add
`.ops/runtime/account-locks/<provider>-<account>/owner.json` acquired by
whichever script is about to spawn a subprocess with a named account
(`run-claude-phase.sh`, `run-codex-phase.sh`,
`run-phase-agent-command.sh`), using the *exact* mkdir + anchor-pid +
phase-attempt-lease staleness logic already built and verified for
`ops-runtime.sh`'s change/repo locks this session (`lock_owner_is_live`,
`lock_anchor_pid`) — reused, not reimplemented, via a shared helper. The
lock is released when the spawning script's subprocess exits (success,
failure, or timeout), via the same `trap ... EXIT` pattern
`run-phase-agent.sh`'s `.phase-attempt-lock` already uses. An account-less
candidate takes no account lock (Non-Goal: no behavior change for a single
account).
*Alternative considered*: rely on the CLI's own session state to reject a
second concurrent invocation under the same config dir — rejected as
unverified and provider-specific; an explicit lock this codebase already
knows how to build correctly is a known-safe mechanism, and it fails closed
(blocks) rather than failing open (races) if that assumption turns out to
be wrong for either CLI.

**4. Continuation eligibility change is one predicate, not a new failover
mode.**
The existing "next candidate in the ordered list is eligible" check
(already skips candidates whose *provider* is unavailable) is extended to
also check per-account availability when a candidate names one, and to
still treat a same-provider/different-account candidate as an ordinary next
candidate — no new state machine, no new attempt `result_class`, no new
`verification_evidence` field. `record-attempt`'s existing schema is
untouched; an attempt already carries `provider`+`model`; account is
additive metadata on top, not a routing-policy version bump.

## Risks / Trade-offs

- **[Risk]** Two concurrent phase attempts under the same account is a
  genuinely untested assumption about CLI behavior (Decision 3's
  alternative). → **Mitigation**: the account lock (Decision 3) makes this
  moot for this codebase's own orchestration; it does not need to be tested
  against the CLI directly.
- **[Risk]** An operator sets `PHASE_AGENT_CLAUDE_ACCOUNT_WORK_DIR` to a
  typo'd or nonexistent path. → **Mitigation**: resolution validates the
  directory exists before use and fails the attempt with a clear message
  (same posture as this session's `CLAUDE_CONFIG_DIR`/`CODEX_HOME`
  defaulting work), rather than silently falling back to the ambient
  default and masking the mistake.
- **[Trade-off]** Dynamic, environment-driven account discovery (Decision
  1) cannot be validated by `openspec validate` or a static test alone
  independent of the operator's actual environment; tests must set the
  relevant env vars explicitly rather than asserting against a fixed
  constant list.
- **[Trade-off]** Sequencing behind `phase-agent-python-orchestrator`
  (Context) means this change cannot start implementation until that one
  merges. Accepted deliberately to avoid building the same schema/resolver
  change twice.
