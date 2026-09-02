**Sequencing precondition**: `phase-agent-python-orchestrator` must be at
FINAL_VERIFY-passed / merged before starting Task 2 below (design.md
Context). Task 1 can start immediately since it only adds the account
registry/lock helper, which is provider-schema-neutral.

All tasks are in the `finance-workspace` repository only (see proposal.md
Impact).

## 1. Account registry and cross-change account lock

- [x] 1.1 Implement the environment-driven account registry (design.md
  Decision 1): a lookup that, given `provider` and `account`, resolves
  `PHASE_AGENT_<PROVIDER>_ACCOUNT_<NAME>_DIR` (case-insensitive `NAME`) and
  verifies the resolved directory exists, dying with a clear message
  otherwise (design.md Risk). Verify: a unit test asserts an unset variable
  and a variable pointing at a nonexistent directory both fail with a
  distinct, actionable message.
- [x] 1.2 Implement the account lock at
  `.ops/runtime/account-locks/<provider>-<account>/owner.json`, reusing
  `lock_owner_is_live`/`lock_anchor_pid` (design.md Decision 3) rather than
  duplicating the logic — refactor those into a shared helper callable from
  both the change/repo lock path and this new account lock path if they are
  not already generic enough. Verify: a unit test acquires the lock, then
  asserts a second acquisition attempt with a live anchor pid is rejected,
  and a third attempt after the anchor pid is confirmed dead auto-releases
  and succeeds — mirroring the four scenarios already proven for the
  change/repo lock this session.
  **Correctness note (found by Claude VERIFY on an earlier uncommitted
  draft, if `lock_account`/`unlock_account` already exist in the working
  tree): staleness detection must check the phase-attempt-lease of the
  *existing lock owner's* change (`owner.json`'s `.change` field), not the
  *new claimant's* `change` argument. A prior draft called
  `owner_is_live(owner, change_dir(change))` using the caller's own
  `change` parameter — since the caller's own phase-attempt-lease is always
  alive while it is synchronously requesting the lock, this makes the
  lease-staleness check a silent no-op rather than actually detecting a
  dead prior owner. Derive the change to check from `owner.json`'s
  recorded `.change` (when present) instead. Verify: a unit test where the
  *recorded* owner's change has a dead phase-attempt-lease, and the *new
  claimant's* own change (a different change) has a live one, asserts the
  lock is still correctly treated as stale and reclaimed — this would fail
  against the prior draft's logic.
- [x] 1.3 Wire lock acquisition/release into the three spawn sites
  (`run-claude-phase.sh`, `run-codex-phase.sh`,
  `run-phase-agent-command.sh`) via a `trap ... EXIT` release exactly like
  `.phase-attempt-lock`'s existing pattern, taking the lock only when the
  resolved candidate names an account. Verify: an integration test spawning
  two overlapping attempts against the same named account observes the
  second attempt block until the first releases, using a fake/sleep
  subprocess instead of a real `claude`/`codex` call.

## 2. Candidate schema and per-account availability

- [x] 2.1 Extend the candidate structure with an optional `account` field
  and extend `validate_candidate`/`state_valid` (or their Python
  equivalents once Task 2 starts, per the sequencing precondition above) to
  accept it, rejecting an account name with no registry entry (spec
  scenario "Unknown account is rejected") at validation time, not at spawn
  time. Verify: a unit test asserts `set`/`candidate-set`/`pin` all reject
  an unregistered account name with a clear message, and accept a
  registered one.
- [x] 2.2 Add the optional `accounts` map under `providers.<provider>`
  (design.md Decision 2), and extend `provider-result` to accept an
  optional account argument that updates `providers.<provider>.accounts.
  <account>` instead of the top-level record when present. Verify: a unit
  test asserts a `global-quota-exhausted` result for `codex`/`work` leaves
  `providers.codex.available` and `providers.codex.accounts.personal`
  untouched (spec scenario "One account's exhaustion does not disable a
  sibling account").
- [x] 2.3 Extend candidate-resolution eligibility (`resolve`, and the
  candidate-iteration loops in `run-phase-agent.sh` /
  `run-phase-agent-command.sh`) to skip a candidate whose named account is
  currently unavailable, using the same per-provider-availability check
  path each already has. Verify: a unit test with two same-provider,
  same-model candidates differing only by account asserts resolution skips
  the exhausted account and selects the other (spec scenario "Same-provider
  account failover preserves the preferred model").

## 3. Full-system verification

- [x] 3.1 Verify: the full existing bash and pytest suites (the same lists
  as `phase-agent-python-orchestrator` Task 7.1/7.2) still pass unmodified
  for every candidate that omits `account` (Non-Goal: zero behavior change
  for a single-account operator).
- [x] 3.2 Verify: a bounded integration test exercises one full
  account-failover cycle — a fake provider adapter reports
  `global-quota-exhausted` for account `work`, and the next attempt resolves
  and runs under account `personal` of the same provider and model, without
  contacting any real model service (per `ops-backend-routing`'s existing
  "Routing and regression tests are bounded" requirement).
- [ ] 3.3 Run one live end-to-end smoke check with two real
  `PHASE_AGENT_CLAUDE_ACCOUNT_*_DIR` values configured (whatever accounts
  the operator actually has), confirming a candidate naming each resolves
  and spawns under the correct `CLAUDE_CONFIG_DIR`/`CODEX_HOME`, and record
  the accounts exercised in the change's OPS handoff evidence.
