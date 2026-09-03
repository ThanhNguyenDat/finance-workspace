## Context

Implementation status: the canonical Python implementation is under
`tools/orchestrator/`; operational wrappers live beside it under
`tools/orchestrator/bin/` and only dispatch through `uv run`.
Shell tests and the native Claude stop hook also remain shell.

See `proposal.md - Why`. Relevant current-state facts:

- `phase-agent-python-orchestrator` already ported the state/lock layer and
  left three thin bash shims (`ops-runtime.sh`, `phase-agent-state.sh`,
  `quant-research-state.sh`) that each `exec uv run --project
  tools/orchestrator python -m orchestrator.<module> "$@"`.
  Every remaining bash script calls these *as subprocesses* (by path), not
  as Python imports, so today a single phase attempt pays for several
  separate `uv run` startups (one per state/lock call).
- `run-phase-agent.sh` resolves a candidate, then shells out to
  `run-$provider-phase.sh` (`run-claude-phase.sh` or `run-codex-phase.sh`)
  as *another* separate process, which itself shells out a third time to
  `timeout ... claude|codex ...`.
- The operator, at a terminal, invokes several of these scripts directly
  today (this session did so repeatedly: `ops-runtime.sh lock/state`,
  `run-phase-agent-command.sh quant-research`), so every script's CLI
  entry point must keep working standalone, not only as an internal call
  from another script.
- GNU `timeout --signal=TERM --kill-after=30s N cmd...` sends `SIGTERM` to
  `cmd` (its direct child, not a process group) after `N` seconds, waits,
  and sends `SIGKILL` after another `30s` if it has not exited. None of the
  current adapters use `setsid`/process groups, so a subprocess that itself
  forks children not sharing its exact PID is *not* guaranteed cleaned up
  today either — this is existing behavior to preserve exactly, not a gap
  to silently "fix" while porting.
- **SDK findings (fetched via `ctx7`, 2026-09-02)**: `claude-agent-sdk`
  (Python) and `openai_codex` (Python) are both official, first-party
  packages. Both operate on a subprocess model — "each call to `query()`
  spawns a separate claude CLI process" (Claude Agent SDK hosting docs);
  the analogous Codex TypeScript SDK source spawns `codex exec
  --experimental-json` and streams JSONL over stdio, and the Python
  `openai_codex` package documents the same JSON-RPC-over-stdio transport
  (`thread/shellCommand`, `turn/interrupt`, etc.). Neither SDK is a raw
  HTTP API client and neither introduces a persistent daemon. Both
  document cancellation: Claude's `ClaudeSDKClient.interrupt()` ("only
  works in streaming mode" — the one-shot `query()` function has no
  documented interrupt path, so the streaming client is required) and
  Codex's `TurnHandle.interrupt()` (sends `turn/interrupt`, which the
  Codex app-server acknowledges with `turn/completed` /
  `status: "interrupted"`). Codex's auth precedence is documented to read
  `$CODEX_HOME/auth.json` (env var `CODEX_HOME`), matching the
  already-shipped per-account resolution from
  `phase-agent-account-registry-config`; the equivalent guarantee for
  Claude's `CLAUDE_CONFIG_DIR` was not independently confirmed in the
  fetched SDK docs and needs a targeted implementation-time check (Task
  3.0). Neither the fetched Claude SDK docs nor the fetched Codex SDK docs
  document a public accessor for the underlying spawned process's PID/
  handle for a hard-kill fallback if `interrupt()` does not resolve the
  turn within a grace period — this is the central open risk this design
  carries forward (Risks below).

## Goals / Non-Goals

**Goals:**
- Every script listed in `proposal.md` becomes a Python CLI module with an
  unchanged external invocation (same path or an equivalent thin shim, same
  arguments, same stdout/stderr/exit-code contract).
- Timeout/cancellation semantics preserve GNU `timeout`'s two guarantees —
  a grace period before forcible termination, and forcible termination
  eventually happening regardless of whether the child cooperates — using
  each SDK's native cancellation call as the "polite" first step and an
  explicit hard-kill fallback as the guaranteed second step (Decision 2).
- Same-process calls between the ported modules (e.g. `run-phase-agent`
  resolving state, or the ported `run-claude-phase`/`run-codex-phase`
  acquiring a lock) become direct Python function calls instead of spawning
  a new `uv run` subprocess per call, removing repeated interpreter-startup
  overhead — *while* every module remains independently invocable as its
  own CLI for manual/terminal use (Context).
- Result classification and availability detection read the SDK's
  structured result objects instead of parsing subprocess stdout/exit
  codes, while still emitting the exact `result_class` string vocabulary
  `phase_agent_state` already consumes (Decision 5) — the internal
  mechanism changes, the contract with already-shipped code does not.

**Non-Goals:**
- No persistent daemon (same non-goal as `phase-agent-python-orchestrator`
  — each top-level invocation, e.g. one `run-phase-agent-command.sh
  quant-research` call, is still a fresh, short-lived Python process; the
  SDK's own internal subprocess is spawned and torn down within that
  invocation, not kept warm across invocations).
- The agent-link synchronizer is also Python (`sync_agent_links.py`) exposed by
  the `sync-agent-links` console command; the optional `bin/*.sh` surface only
  dispatches to `uv` and has no runtime logic.
- No change to prompt wording, model/effort validation rules, or the
  candidate-resolution/failover logic itself — that behavior is owned by
  `phase-agent-python-orchestrator`/`phase-agent-multi-account-routing` and
  is only *called* from here, never redefined.
- Not a "keep bash's exact mechanism, just in Python" port for the
  spawn/cancel path specifically (Decision 2) — that was the original scope
  before the SDK pivot (proposal.md - Why) and is deliberately superseded;
  every other script keeps the byte-for-byte-port goal unchanged.

## Decisions

**1. One Python module per operational entrypoint, called directly (no
subprocess) when the caller is itself already-ported Python. The canonical
Python code and operational wrappers live under
`tools/orchestrator/`; wrappers in `bin/` are thin `uv run`
entrypoints. Shell tests remain under `.agents/scripts/tests/` because they
are contract tests, not production orchestration logic.** [updated at implementation]
Concretely: `run_phase_agent.py`'s candidate loop imports
`ops_runtime.lock_account`/`phase_agent_state.resolve` and calls them as
Python functions, and imports `run_claude_phase`/`run_codex_phase` and
calls their `main()`-equivalent directly, rather than spawning
`run-claude-phase.sh` as a child process. Each of those modules keeps its
own `if __name__ == "__main__":` entry point and its own
`bin/run-claude-phase.sh` compatibility wrapper, while the preferred operator
command is `uv run --project tools/orchestrator run-claude-phase
<change> <repo> PLAN`.
*Alternative considered*: merge everything into one CLI with subcommands
— rejected for the same reason `phase-agent-python-orchestrator` rejected
it: it would require editing every caller (including this session's own
muscle-memory terminal usage) for no behavioral benefit.

**2. Spawn and supervise `claude`/`codex` through the official SDK client
for each provider, using the SDK's native interrupt as the timeout's first
action and an explicit hard-kill fallback as its second — not
`subprocess.Popen` + a hand-written `SIGTERM`-then-`SIGKILL` timer.**
[supersedes the original Decision 2] Concretely, per provider:
- **Claude**: use `ClaudeSDKClient` (not the one-shot `query()` function,
  because only the streaming client documents `interrupt()`). Start the
  query, arm a timer for `CLAUDE_TIMEOUT_SECONDS` (default 3600,
  unchanged) that calls `await client.interrupt()`. If no terminal
  `ResultMessage` has arrived `kill_after` seconds (30s, unchanged) after
  that, invoke the hard-kill fallback (Task 3.0 must confirm the concrete
  mechanism — e.g. a documented internal transport/process handle, or, if
  none exists, closing the client's underlying transport and killing the
  process group it spawned, verified against a real hanging fake `claude`
  binary rather than assumed from docs).
- **Codex**: use `Codex()`/`thread.turn(...)`, which returns a
  `TurnHandle`. On timeout, call `turn_handle.interrupt()` (`turn/interrupt`
  over the SDK's JSON-RPC transport, confirmed by fetched docs to yield a
  `turn/completed` event with `status: "interrupted"`). If the turn has not
  reached a terminal status `kill_after` seconds after that, invoke the
  same class of hard-kill fallback as Claude's.
- Cancel the timer on normal (pre-timeout) completion in both cases, same
  as the original design's Decision 2.
- No process-group signaling is added beyond whatever each SDK already
  does internally (Context: today's bash does not use one either, and this
  change does not get to choose the SDK's internal process topology).
*Alternative considered (the original Decision 2)*: `subprocess.Popen` +
`threading.Timer`-driven `SIGTERM` then `SIGKILL`, calling `claude
--print ...`/`codex exec --json ...` directly — this remains a fully valid,
lower-risk design (its signal semantics are simple, well-understood, and
independently verifiable without depending on either SDK's internal
behavior). It was rejected by explicit operator direction after reviewing
the SDK documentation (proposal.md - Why), in favor of the structured
results and native cancellation the SDKs provide, accepting the new open
risk below in exchange.

**3. Prompt construction is copied verbatim from each bash script's prompt
string, not rewritten "in the spirit of" the original — only the transport
changes.**
Every `case "$phase" in ...)` branch and every conditional prompt append
(continuation mode, FIX findings, FINAL_VERIFY's machine-readable footer
instructions) must produce the byte-identical prompt text the bash version
produces for the same inputs. The only change from the original design is
*where that string goes*: instead of a `--print` CLI argument, it becomes
the `prompt` passed to `ClaudeSDKClient.query()` / `thread.run()`/
`thread.turn()`. Verify by diffing captured prompts, not by re-reading for
"equivalent meaning."

**4. Fingerprinting (the VERIFY/FINAL_VERIFY mutation-detection hash) is
ported with the exact same inputs in the exact same order, unaffected by
the SDK pivot**: `git status --porcelain=v1 -z`, `git diff --binary HEAD`,
then each untracked file's path and (content hash, or `symlink:<target>`
for a symlink) — piped through the same hash algorithm
(`sha256sum`-equivalent, i.e. Python's `hashlib.sha256` over the identical
byte sequence). A different but "equivalent" hash construction would still
detect mutation correctly in practice, but would break the ability to
compare a historical bash-computed fingerprint against a new
Python-computed one during the transition window, so the byte sequence
must match exactly. This decision is entirely local git-state inspection
and does not involve either SDK.

**5. Result classification reads each SDK's structured result object, not
raw stdout/exit code — but must still emit the exact `result_class` string
vocabulary the existing bash classifiers produce, since
`phase_agent_state` (already shipped) consumes that vocabulary as a
contract this change does not get to redefine.**
[supersedes the original Decision 5's "read bash line by line" framing for
*where the signal comes from*, but keeps its discipline about not
paraphrasing from memory] Concretely:
- Claude: `classify_claude_result` reads `ResultMessage.subtype` (e.g.
  `"success"`, `"error_max_turns"`, `"error_max_budget_usd"`) and
  `.is_error`/`.stop_reason` where available, plus the hard-kill fallback's
  own outcome (timeout vs. clean interrupt vs. crash) when Decision 2's
  fallback path was taken.
- Codex: `classify_codex_result` reads `TurnResult.status` (e.g.
  `"completed"`, `"interrupted"`, `"failed"`) the same way.
- Task 1.1 must build the explicit mapping table {existing bash
  `result_class` string -> which SDK field/value combination now produces
  it} by reading the current bash classifier's logic line by line
  (unchanged discipline from the original design) *and* by capturing real
  SDK result objects for each corresponding scenario (success, timeout,
  quota/budget exhaustion, auth failure, crash) — a table is not
  trustworthy until both sides are captured from real observed behavior,
  not inferred from either the bash script's comments or the SDK's
  docstrings alone.
- `detect-provider-availability.sh`/`detect-codex-availability.sh` are
  ported the same way: probe via the SDK, read its structured
  success/auth-error/quota-error result, map to the existing availability
  result classes.

Account-aware retry note: a provider-reported transient rate limit is also
retryable against the next configured account/candidate. It is not persisted as
an account-off state, because the SDK may be reporting a temporary session
window rather than a permanently exhausted credential. This keeps the
personal-02-first ordering while allowing personal to continue the same
attempt when personal-02 returns HTTP 429/session-limit evidence.

## Risks / Trade-offs

- **[Risk — new, highest priority]** Decision 2's hard-kill fallback
  mechanism is not confirmed by the SDK documentation fetched during
  planning; if `interrupt()` does not resolve a wedged process and no
  hard-kill path exists, a runaway `claude`/`codex` process could become
  *unstoppable* from this code, which is strictly worse than the original
  Decision 2's Popen-based design (where this code always owns the direct
  child process and can always `SIGKILL` it).
  → **Mitigation**: Task 3.0 is a dedicated spike, before any adapter
  code is written, that (a) confirms the exact PyPI package names and
  pins them, (b) finds or rules out a documented hard-kill path in each
  SDK, and (c) if no such path exists, defines a fallback (e.g. locating
  and killing the SDK-spawned `claude`/`codex` process by inspecting the
  process tree the SDK's Python process owns) verified against a real
  fake CLI binary that ignores the SDK's `interrupt()` message. If no
  reliable hard-kill path can be established for either SDK, this design
  must be revisited before Task 4 (adapters) proceeds — an unstoppable
  subprocess is not an acceptable regression versus the current bash
  behavior, and reverting to the original Popen-based Decision 2 for the
  affected provider only is an explicitly acceptable fallback if the spike
  fails.
- **[Risk]** The signal-escalation reimplementation (Decision 2) is still
  the single highest-risk piece of this change for the same underlying
  reason as the original design — a bug here could either leave a runaway
  model subprocess unbounded (resource/cost risk) or cancel it too early
  (spurious attempt failures) — the SDK pivot changes *which* bug is likely
  (a gap in the fallback path vs. a gap in hand-written signal code), not
  whether this area needs the same rigor.
  → **Mitigation**: the same class of bounded integration test the
  original design required — a deliberately-hanging fake `claude`/`codex`
  CLI binary — must still exist, but now must speak enough of each SDK's
  stdio protocol to be recognized as a live session by the SDK client
  (materially more test-fixture work than faking a plain CLI process that
  ignores signals, since the original design's fake process just had to
  exist and ignore SIGTERM). The test must assert (a) the SDK's
  `interrupt()` call fires at the configured timeout, (b) the fixture is
  still "running" from the SDK's perspective after that (simulating a
  session that does not resolve on interrupt), (c) the hard-kill fallback
  fires after the kill-after grace period, (d) the attempt is recorded
  with the correct terminal state either way.
- **[Risk]** Removing the shim-subprocess indirection between ported
  Python callers (Decision 1) changes *how* errors propagate (a Python
  exception across a function call vs. a subprocess exit code) even though
  external behavior is meant to be unchanged.
  → **Mitigation**: every internal call site must translate an internal
  exception back into the exact same stderr message and exit code the
  subprocess boundary produced today, verified by the same bash integration
  tests run against the new code path.
- **[Risk]** Two new third-party dependencies (`claude-agent-sdk`,
  `openai_codex`) now sit on the critical path for every phase attempt;
  a breaking change in either SDK's minor/patch version could silently
  change cancellation or result-classification behavior underneath this
  code.
  → **Mitigation**: pin exact versions in `uv.lock` (same discipline
  `coding-and-verification.md` already requires for `tools/orchestrator`);
  do not use a version range. A future SDK upgrade is a separate, reviewed
  change, not an incidental side effect of an unrelated commit.
- **[Trade-off]** This is the largest of the three phase-agent Python
  migration changes by line count and by behavioral surface (real
  subprocess/cancellation handling and a new external dependency, not just
  JSON/lock logic) — proposal.md's motivation is maintainability, not a
  safety defect being fixed, so the bar for "prove no regression" before
  cutover is at least as high as `phase-agent-python-orchestrator`'s, and
  is now higher still on the specific point of Decision 2, given the
  unresolved-at-planning-time hard-kill question above.

## Migration Plan

1. **Task 3.0 spike (new, gates everything else)**: confirm exact PyPI
   package names for both SDKs, pin versions, and resolve the Decision 2
   hard-kill-fallback open risk with a real fake-CLI experiment before
   writing any adapter code.
2. Port `classify-claude-result.sh`/`classify-codex-result.sh` and
   `detect-provider-availability.sh`/`detect-codex-availability.sh` next
   (smallest, and the mapping table from Decision 5 can be built and
   verified independent of the cancellation work).
3. Port `configure-phase-agents.sh` (thin CLI wrapper, already
   Python-backed via the `configure-phase-agents` console command, unaffected
   by the SDK pivot).
4. Port `run-claude-phase.sh`/`run-codex-phase.sh` (the cancellation/
   hard-kill risk area — hold until Task 3.0's spike and the hanging-
   session integration test are both proven).
5. Port `run-phase-agent.sh`, wiring it to call the ported adapters
   directly (Decision 1) instead of shelling out to them.
6. Port `run-phase-agent-command.sh` last (the most end-to-end-tested
   script via `test_multi_account_routing.sh`/`test_claude_quant_launcher.sh`
   /`test_phase_agent_quant_launcher.sh`).
7. Run the full existing bash + pytest suites, plus the new hanging-session
   integration test, before replacing any original bash file with its shim.
8. **Rollback**: `git revert` any one script's cutover commit independently
   restores its bash original at the same path with no caller changes,
   exactly like `phase-agent-python-orchestrator`'s rollback story. If
   Task 3.0's spike fails for one provider only, that provider's adapter
   may keep the original Popen-based Decision 2 design while the other
   provider proceeds with the SDK — this is an explicitly acceptable
   partial-adoption outcome, not a blocker for the whole change.
