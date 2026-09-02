**Sequencing precondition**: `phase-agent-multi-account-routing` (merged)
and `phase-agent-account-registry-config` should both land first, since
this change's `run-claude-phase`/`run-codex-phase`/`run-phase-agent-command`
ports must carry over their already-shipped account-lock/account-dir logic
rather than porting an older pre-account version of these scripts.

All tasks are in the `finance-workspace` repository only.

## 1. Classifiers and detectors

- [x] 1.1 Port `classify-claude-result.sh` and `classify-codex-result.sh`
  to `phase_agent_orchestrator.classify_claude_result`/
  `classify_codex_result`, reading their current bash logic line by line
  (design.md Decision 5) and building an explicit mapping table from each
  existing `result_class` string to the `claude-agent-sdk`/`openai_codex`
  structured result field(s) that now produce it, captured from real SDK
  result objects for each scenario (success, timeout, quota/budget
  exhaustion, auth failure, crash) rather than inferred from docstrings.
  Verify: a unit test feeds every fixture already used by the bash
  version's own tests (or, if none exist standalone, every scenario
  exercised by the phase-agent bash test suite, now expressed as a
  captured SDK result object) and asserts an identical `result_class`
  string to what the bash classifier produces for the equivalent scenario.
- [x] 1.2 Port `detect-provider-availability.sh` and
  `detect-codex-availability.sh` the same way, probing via each SDK and
  reading its structured success/auth-error/quota-error result. Verify: a
  unit test with a fake `claude`/`codex` SDK-facing fixture reproduces
  every result class the bash version's own test coverage
  (`test_provider_availability.sh`, `test_codex_availability_detection.sh`)
  currently exercises.
- [x] 1.3 Wire the four corresponding `.agents/scripts/*.sh` shims. Verify:
  `test_provider_availability.sh` and `test_codex_availability_detection.sh`
  pass unmodified against the shims.

## 2. Operator CLI

- [x] 2.1 Port `configure-phase-agents.sh` to a Python module, preserving
  its exact `show`/`set`/`candidate-set`/`reset`/`reset-all`/`pin`/`auto`/
  `provider-on`/`provider-off`/`provider-manual`/`provider-auto` subcommands
  and table-formatted `show` output byte-for-byte (including the `ACCOUNT`
  column added by `phase-agent-multi-account-routing`). Unaffected by the
  SDK pivot. Verify: a unit test diffs the formatted `show` output against
  a fixed fixture state.
- [x] 2.2 Wire the shim. Verify: a manual invocation of every subcommand
  against a temp state produces output identical to the current bash
  version run against the same starting state.

## 3. SDK spike and cancellation core (highest-risk section)

- [x] 3.0 **Spike, before any other Task 3-5 work**: confirm the exact
  PyPI distribution names for the Claude and Codex Python SDKs, add them
  to `tools/phase-agent-orchestrator/pyproject.toml` pinned to exact versions, run
  `uv sync --project tools/phase-agent-orchestrator`, and resolve design.md's open
  hard-kill-fallback risk: build a fake `claude`/`codex` CLI binary that
  speaks enough of each SDK's stdio protocol to be recognized as a live
  session, make it ignore the SDK's `interrupt()`/`turn/interrupt` call,
  and confirm a concrete way exists in this codebase to forcibly terminate
  it anyway (a documented SDK accessor, or locating and killing the
  SDK-spawned process from the owning Python process). Verify: a bounded
  spike script demonstrates the fake process is forcibly terminated within
  a short bounded time after interrupt is ignored, for both providers
  independently. If no reliable hard-kill path is found for a given
  provider, record that finding in this change's `.ops/changes/<change>/
  handoff.md` and fall back to design.md Migration Plan step 8's partial-
  adoption path (that provider keeps the original Popen-based design)
  before proceeding to Task 3.1 for that provider.
- [x] 3.1 Implement the SDK-native-interrupt-then-hard-kill timeout helper
  (design.md Decision 2) per provider as a small reusable function taking
  a constructed SDK client/turn handle, timeout seconds, and kill-after
  seconds, returning the terminal result object (or the hard-kill fallback
  outcome). Verify: the hanging-session integration test from Task 3.0's
  fixture confirms the SDK interrupt call fires at the timeout, the
  fixture is still "running" from the SDK's perspective afterward
  (simulating a session that does not resolve on interrupt), the hard-kill
  fallback fires `kill_after` seconds later, and a fixture that resolves
  cleanly on interrupt is not hard-killed at all.
- [x] 3.2 Verify: a unit test confirms the timer is cancelled (no stray
  interrupt/hard-kill call) when the SDK session completes normally well
  before its timeout.

## 4. Phase adapters

- [x] 4.1 Port `run-claude-phase.sh` to
  `phase_agent_orchestrator.run_claude_phase`, constructing a
  `ClaudeSDKClient` (design.md Decision 2 requires the streaming client,
  not the one-shot `query()` function, since only the streaming client
  documents `interrupt()`), using the Task 3 helper for timeout/
  cancellation, and porting the prompt construction verbatim (design.md
  Decision 3) including the account-lock wiring already shipped in the
  bash version — confirm the constructed client actually resolves
  credentials from the per-account `CLAUDE_CONFIG_DIR` the account-registry
  computes (design.md Context flags this as unconfirmed for Claude,
  unlike Codex's documented `CODEX_HOME` precedence). Verify: a unit test
  asserts the constructed prompt string is byte-identical to the bash
  version's for every phase (`PLAN`, `IMPLEMENT`, `VERIFY`, `FIX`,
  `FINAL_VERIFY`, continuation mode on/off); a separate test confirms a
  distinct `CLAUDE_CONFIG_DIR` value actually changes which account
  identity the SDK client authenticates as.
- [x] 4.2 Port `run-codex-phase.sh` the same way, using `Codex()`/
  `thread.turn(...)` and confirming `CODEX_HOME` resolution per account
  (already documented in design.md Context, still needs an in-repo test,
  not just doc trust).
- [x] 4.3 Port the git-status/diff/untracked-file fingerprint function
  (design.md Decision 4 — unaffected by the SDK pivot) used by both
  adapters' VERIFY/FINAL_VERIFY mutation check. Verify: a unit test asserts
  the Python fingerprint of a fixed fixture repository state matches a
  fingerprint captured from the current bash `fingerprint()` function run
  against the identical fixture.
- [x] 4.4 Wire both shims. Verify:
  `.agents/scripts/tests/test_claude_worker_policy.sh`,
  `test_codex_worker_policy.sh`, and `test_multi_account_routing.sh`
  (its account-lock-exclusivity and real-account-directory-export
  assertions) pass unmodified against the shims.

## 5. Resolver and quant launcher

- [x] 5.1 Port `run-phase-agent.sh` to
  `phase_agent_orchestrator.run_phase_agent`, calling the Task 1/2/4
  modules directly as Python functions rather than as subprocesses
  (design.md Decision 1), while keeping its own standalone shim/CLI entry
  point. Verify: `test_ops_orchestration.sh`, `test_phase_agent_routing.sh`,
  `test_quant_backend_routing.sh`, and `test_hermetic_agent_contracts.sh`
  pass unmodified.
- [x] 5.2 Port `run-phase-agent-command.sh` to
  `phase_agent_orchestrator.run_phase_agent_command`. Verify:
  `test_claude_quant_launcher.sh`, `test_phase_agent_quant_launcher.sh`,
  and `test_multi_account_routing.sh`'s quant-research failover assertions
  pass unmodified.
- [x] 5.3 Wire both shims.

## 6. Full-system verification and cutover

- [x] 6.1 Verify: every bash test under `.agents/scripts/tests/` passes
  against the fully shimmed state.
- [x] 6.2 Verify: `uv run --project tools/phase-agent-orchestrator pytest` passes
  with the full suite from Tasks 1-5, including the new hanging-session
  cancellation coverage from Task 3, and that `uv.lock` pins exact SDK
  versions (no version range).
- [ ] 6.3 Run one live end-to-end smoke check:
  `./.agents/scripts/run-phase-agent-command.sh quant-research` against the
  fully SDK-backed chain, and verify it completes with the same
  `Quant iteration <n> completed with <provider>` success line.
- [ ] 6.4 Update `.github/workflows/agent-contracts.yml` if the CI job's
  `bash -n` syntax-check step needs adjusting for any removed bash file,
  and verify the workflow still succeeds on a pushed commit.
- [x] 6.5 Update `.agents/rules/coding-and-verification.md` and/or the
  relevant skill to reflect that the phase-agent system is now
  Python-first and SDK-backed for provider invocation, and verify
  `./.agents/scripts/sync-agent-links.sh --check` still passes.
