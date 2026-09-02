All tasks are in the `finance-workspace` repository only (see proposal.md
Impact). Before starting, capture the current bash behavior as the ground
truth: `.agents/scripts/ops-runtime.sh`, `phase-agent-state.sh`, and
`quant-research-state.sh` at the commit this change branches from are the
spec for every task below that says "matches the current bash behavior."

## 1. Bootstrap the `uv` project

- [x] 1.1 Run `uv init --package` at `.agents/orchestrator/` to scaffold
  `pyproject.toml` and `src/phase_agent_orchestrator/`, and verify
  `uv run --project .agents/orchestrator python -c "import phase_agent_orchestrator"`
  succeeds.
- [x] 1.2 Add `pytest` as a dev dependency via `uv add --dev pytest`, and
  verify `uv run --project .agents/orchestrator pytest --collect-only` exits 0
  with zero tests collected yet.
- [x] 1.3 Add a `command -v uv` preflight check with a clear error message to
  `run-phase-agent-command.sh`'s existing
  `for command in jq timeout git; do ... done` loop (design.md Risk:
  bootstrap bar), and verify running the script with `uv` temporarily
  removed from `PATH` fails fast with that message instead of a raw
  `command not found` from deep inside a shim.

## 2. Shared JSON/state helpers

- [x] 2.1 Implement an atomic JSON writer
  (`tempfile.NamedTemporaryFile(dir=..., delete=False)` + `os.replace()`,
  design.md Decision 4) and verify a unit test that a concurrent reader
  never observes a partially written file (simulate by writing a large
  payload and asserting the temp file is renamed only after the write
  completes).
- [x] 2.2 Implement the anchor-pid liveness check
  (`lock_anchor_pid`/`lock_owner_is_live` equivalent, design.md Decisions 5-6):
  reads `$CLAUDE_PID` then `$CODEX_PID`, and a `pid_is_alive(pid, hostname)`
  helper using `os.kill(pid, 0)` that treats both `ProcessLookupError` and
  `PermissionError` as "not confirmed alive," gated on `hostname` matching
  `socket.gethostname()` exactly as the bash version gates on `hostname`.
  Verify with unit tests mocking `os.kill` to raise each of
  `ProcessLookupError`, `PermissionError`, and no exception.
- [x] 2.3 Implement the phase-attempt-lease dead-check
  (`phase_attempt_lease_is_dead` equivalent): reads
  `<change_dir>/runtime/.phase-attempt-lock/pid` and applies the same
  liveness helper from 2.2. Verify with a unit test asserting an absent
  lease directory returns "not dead" (must not be treated as staleness
  evidence — design.md Context) while an existing lease with a confirmed-dead
  pid returns "dead."

## 3. Port `phase-agent-state.sh`

- [x] 3.1 Implement `phase_agent_orchestrator/phase_agent_state.py` with every
  subcommand `phase-agent-state.sh` currently exposes, matching its exact
  argument order and stdout JSON shape.
- [x] 3.2 Wire the `.agents/scripts/phase-agent-state.sh` shim per design.md
  Decision 2, keeping the file executable at its current path.
- [x] 3.3 Verify: `.agents/scripts/tests/test_phase_agent_state.sh` and
  `.agents/scripts/tests/test_phase_agent_routing.sh` pass unmodified against
  the shim.

## 4. Port `quant-research-state.sh`

- [x] 4.1 Implement `phase_agent_orchestrator/quant_research_state.py` with
  every subcommand `quant-research-state.sh` currently exposes (including
  `begin-iteration`'s exactly-once-increment semantics), matching its exact
  argument order and stdout JSON shape.
- [x] 4.2 Wire the `.agents/scripts/quant-research-state.sh` shim.
- [x] 4.3 Verify: `.agents/scripts/tests/test_quant_research_state.sh` and
  `.agents/scripts/tests/test_quant_backend_routing.sh` pass unmodified
  against the shim.

## 5. Port `ops-runtime.sh` state/routing subcommands

- [x] 5.1 Implement `init`, `phase`, `fix`, `route`, `record-attempt`,
  `trace-origin`, `state`, `active`, and `complete`/`archive` in
  `phase_agent_orchestrator/ops_runtime.py`, matching current validation
  rules (`valid_phase`, `valid_transition`, `valid_backend`,
  `routing_policy_version`, the `trace-origin` path-traversal and
  approved-evidence-root checks) exactly.
- [x] 5.2 Verify: a unit test asserts every currently-rejected transition in
  `valid_transition` (e.g. `RELEASE -> FIX`) is still rejected, and every
  currently-accepted transition still succeeds.
- [x] 5.3 Verify: a unit test asserts `trace-origin` still rejects a
  traversal path (`research/quant/rounds/../candidate.md`) and an
  out-of-evidence-root path (`README.md`), matching
  `test_quant_promotion_trace.sh`'s existing cases.

## 6. Port `ops-runtime.sh` lock/unlock subcommands (highest-risk section)

- [x] 6.1 Implement `lock`, `unlock`, `lock-repos`, `unlock-repos`, and
  `assert-repo-lock`, reusing the helpers from Task 2, and matching
  `owner.json`'s exact current field set (`change`/`session_id`/`pid`/
  `hostname`/`started_at`, plus `repository` for repo locks).
- [x] 6.2 Implement the repository-lock-candidate staleness check using a
  `ThreadPoolExecutor` (design.md Decision 6) for the read-only liveness
  evaluation only; keep the actual acquisition (`mkdir`-equivalent,
  `release_repo_locks` on any failure) sequential and unchanged.
- [x] 6.3 Verify: unit tests reproduce the four scenarios validated by hand
  for the bash version this session — (a) parent alive, no phase-attempt
  lease → stays locked; (b) parent alive, live phase-attempt lease → stays
  locked; (c) parent alive, dead phase-attempt lease → auto-released; (d)
  unverifiable owner (different recorded hostname) → stays locked
  (manual-release-only) — for both the change-lock and the repo-lock path.
- [x] 6.4 Wire the `.agents/scripts/ops-runtime.sh` shim.
- [x] 6.5 Verify: `.agents/scripts/tests/test_ops_orchestration.sh` passes
  unmodified against the shim.

## 7. Full-system verification and cutover

- [x] 7.1 Verify: every bash test under `.agents/scripts/tests/` passes
  against the fully shimmed state (`test_ops_orchestration.sh`,
  `test_phase_agent_state.sh`, `test_quant_research_state.sh`,
  `test_phase_agent_routing.sh`, `test_quant_backend_routing.sh`,
  `test_quant_promotion_trace.sh`, `test_hermetic_agent_contracts.sh`,
  `test_claude_quant_launcher.sh`, `test_phase_agent_quant_launcher.sh`,
  `test_codex_availability_detection.sh`, `test_codex_worker_policy.sh`,
  `test_claude_worker_policy.sh`, `test_provider_availability.sh`).
- [x] 7.2 Verify: `uv run --project .agents/orchestrator pytest` passes with
  the full suite from Tasks 2, 5, and 6.
- [x] 7.3 Run one live end-to-end smoke check:
  `./.agents/scripts/run-phase-agent-command.sh quant-research` against the
  real Python-backed `quant-research-state.sh`, and verify it completes with
  the same `Quant iteration <n> completed with <provider>` success line the
  bash implementation produces today (or the same lease-contention message
  when a prior run is still held). Verified by Claude (VERIFY):
  `Quant iteration 212 completed with claude`, round416 NO-CHANGE recorded.
- [x] 7.4 Update `.agents/rules/coding-and-verification.md` or the relevant
  skill (per `CLAUDE.md`'s Task Completion and Skill Upsert) to record `uv`
  as a required tool and note the new `.agents/orchestrator/` bootstrap step,
  and verify `./.agents/scripts/sync-agent-links.sh --check` still passes
  after the edit.

## 8. FIX round — Claude VERIFY findings

- [x] 8.1 **P1 (correctness).** In `lock_repositories`
  (`.agents/orchestrator/src/phase_agent_orchestrator/ops_runtime.py:311-353`),
  the `ThreadPoolExecutor` snapshot taken before the sequential acquisition
  loop is reused as the liveness verdict when a repo lock is contended
  (`live = statuses.get(canonical); if live is None: live = owner_is_live(...)`),
  so a "dead" verdict from the snapshot is trusted even after other
  repositories in the same call have been processed in between — widening the
  window in which this process can steal a lock a different session has since
  legitimately re-acquired, unlike the bash original which always re-checked
  `kill -0` immediately before stealing. Fix: use the thread pool only to
  speed up the existence pre-check (`lock.exists()`), and always call
  `owner_is_live()` fresh — never from the cached `statuses` snapshot — at the
  point inside `except FileExistsError` where the steal decision is made, for
  every repository, matching the change-lock path's behavior in `lock_change`
  (which already re-checks fresh, single-lock, no caching). Verify: a unit
  test with two repositories where repo A's lock is legitimately re-acquired
  (fresh live pid written) by a simulated concurrent actor *after* the
  `lock_repositories` snapshot phase but *before* its sequential loop reaches
  repo A asserts the call refuses to steal repo A's lock (raises the
  "repository lock exists" path, exit 1) instead of destroying the concurrent
  owner's lock. Re-run the full suite from Tasks 2, 5, 6, 7 (bash and pytest)
  to confirm no regression.
- [x] 8.2 **P2 (simplification).** Remove the `/proc/$parent_pid/cwd`
  ancestor-walking fallback from the three shims
  (`.agents/scripts/ops-runtime.sh`, `phase-agent-state.sh`,
  `quant-research-state.sh`): `PROJECT_DIR="$SCRIPT_DIR/../orchestrator"` is
  derived from `BASH_SOURCE` and is therefore always the shim's actual
  sibling directory regardless of the caller's cwd or process ancestry, so
  the fallback branch is unreachable dead code that also hard-depends on
  Linux `/proc` (breaks the branch, silently, on any non-Linux host). Keep
  only the `PHASE_AGENT_ORCHESTRATOR_PROJECT` env-var override and the
  `$SCRIPT_DIR/../orchestrator` default. Verify: `shellcheck` (or a manual
  read) shows no remaining `/proc` reference in any of the three shims, and
  Task 7.1's bash suite still passes unmodified.
- [x] 8.3 Verify: re-run the full bash test suite (Task 7.1's list) and
  `uv run --project .agents/orchestrator pytest` after 8.1 and 8.2, and
  re-run the live smoke check from 7.3 once more as the FINAL_VERIFY gate for
  this FIX round. Verified by Claude (VERIFY): 13/13 bash suites pass, 15/15
  pytest pass (new test `test_repo_lock_rechecks_owner_after_existence_snapshot`
  reproduces the 8.1 race and confirms the fix), smoke check
  `Quant iteration 214 completed with claude`.
- [x] 8.4 **CI gap found during VERIFY**: `.github/workflows/agent-contracts.yml`
  runs the bash test suites (which now invoke the Python-backed shims via
  `uv run --project`) but never installs `uv`, so a fresh CI runner has
  neither `uv` nor a pre-bootstrapped `.venv` and every shim invocation would
  fail with `uv is required`. Add a `uv` setup step (the official
  `astral-sh/setup-uv` action, pinned to a specific version, matching this
  repo's convention of pinning third-party actions) before the "Validate
  shell and JSON" step, and verify: a workflow run (or a local `act`/manual
  dry run reproducing the same steps in a clean checkout with no
  pre-existing `.agents/orchestrator/.venv`) completes the "Run bounded
  orchestration tests" step successfully.
- [x] 8.5 Commit every file this change touches (`.agents/orchestrator/`,
  the three shims, `.agents/rules/coding-and-verification.md`,
  `.agents/skills/quant-research-loop/SKILL.md`, and the CI workflow from
  8.4) in one reviewable commit or small stack, push to `origin/main`, and
  verify the `Agent contracts` workflow run for that exact commit SHA
  succeeds on GitHub Actions before this change is archived.
