## 1. Provider session continuity

- [ ] 1.1 Add `resume_id: str | None = None` to `BaseProvider.start_turn`'s
      signature (and thread it through `run_turn`/`_run_one_attempt`), and
      a `last_session_id: str | None` attribute set by each provider after
      a turn completes. Default `None` everywhere; verify `codex-exec`/
      `claude-exec`/existing `test_providers.py` tests are unaffected
      (never pass a resume id, behavior identical to before).
- [ ] 1.2 `CodexProvider.start_turn`: call `codex.thread_resume(resume_id,
      ...)` instead of `codex.thread_start(...)` when `resume_id` is
      given; capture the thread id into `last_session_id` in both branches.
      Verify with a fake Codex client asserting `thread_resume` is called
      with the given id, and `thread_start` is called when it's `None`.
- [ ] 1.3 `ClaudeProvider.start_turn`: pass `ClaudeAgentOptions(resume=
      resume_id, ...)` when given; set `last_session_id` from
      `self._result_message.session_id` after a turn. Verify with a fake
      query_fn asserting the options object carries the given `resume`
      value, and that `last_session_id` reads the result message's session
      id after a turn.
- [ ] 1.4 Confirm what tool access (bash, web search) a headless
      `ClaudeProvider`/`claude_agent_sdk` turn has available by default,
      and whether it needs explicit `ClaudeAgentOptions` configuration to
      match the domain rules' backlog-exhaustion fallback (Module 1's
      multi-source search when the internal backlog is exhausted). Record
      the finding in this task (edit this line with what was found) rather
      than assuming; adjust PLAN's turn configuration (task 2.2) if needed.

## 2. Cycle orchestration

- [ ] 2.1 Rewrite `quant_research_exec.py`'s CLI surface: drop `--role`;
      make the positional `PROMPT`/`--prompt-file` optional PLAN guidance
      (not a required brief); keep `--round` (auto-detect, resolved before
      PLAN runs); replace `--model`/`--effort` with `--codex-model`/
      `--codex-effort`/`--codex-escalated-model`/`--claude-model`/
      `--claude-effort`/`--claude-escalated-model`; raise the default
      `--timeout-seconds` to 3600. Verify `--help` shows no `--role`, no
      generic `--model`/`--effort`, all six new flags, and that
      `quant-research-exec` with zero arguments parses successfully
      (no "required" error).
- [ ] 2.2 Implement the PLAN stage: one `ClaudeProvider.run_turn` with the
      domain rules, the round-selection backlog files (index.md, metrics
      CSV, recent round files), any optional operator guidance, and the
      `PLAN_BRIEF:` format instruction (informed by task 1.4's findings for
      tool access); parse the brief; capture `claude_session_id` from
      `last_session_id`. Verify with a fake Claude client that a missing
      `PLAN_BRIEF:` line raises the documented hard error before Codex is
      ever invoked.
- [ ] 2.3 Implement the IMPLEMENT stage: one `CodexProvider.run_turn` with
      the domain rules + PLAN's brief, `resume_id=None` (fresh thread),
      capturing `codex_session_id` from `last_session_id` after.
- [ ] 2.4 Implement the VERIFY stage as a reusable function taking an
      effort/model override: one `ClaudeProvider.run_turn` (resuming
      `claude_session_id`) given a description of what IMPLEMENT/FIX
      produced (round file path, CSV path, log path) and the
      `VERIFY_RESULT:` format instruction; parse the last matching
      `VERIFY_RESULT:` line, requiring VERIFY to judge evidence/
      classification trustworthiness only (an honest negative outcome is
      `PASS`, never `DEFECT`). Verify: PASS/DEFECT/QUESTION are each
      parsed correctly from a fake Claude result string; a result with no
      matching line raises the documented hard error before any further
      stage runs.
- [ ] 2.5 Implement the ASK round-trip: on `QUESTION <text>`, one Codex
      turn (resuming `codex_session_id`) answering `<text>`, then one
      Claude turn (resuming `claude_session_id`) with that answer,
      accepting only `PASS`/`DEFECT` from the continuation (a second
      `QUESTION` here is a hard error, not another round-trip). Verify
      with fakes asserting exactly one Codex turn and one Claude turn run
      for a `QUESTION` verdict, and that a second `QUESTION` in the
      continuation raises the documented error.
- [ ] 2.6 Implement the bounded FIX loop: on `DEFECT`, up to 5 attempts of
      (one Codex FIX turn resuming `codex_session_id` with the `DEFECT`
      issue text, then task 2.4's VERIFY logic again resuming
      `claude_session_id`). Attempts 1-2 use the given/default
      `--codex-*`/`--claude-*` model/effort; attempt 3 onward escalates to
      each provider's highest effort (and its `--*-escalated-model` if
      given). If the 5th re-VERIFY still returns `DEFECT`, exit non-zero
      with an error and do not run FINALIZE. Verify with fakes: exactly 5
      FIX turns run when every re-VERIFY keeps returning `DEFECT` (never a
      6th), attempts 1-2 use the base model/effort and attempt 3+ use the
      escalated values, and a `PASS` on any attempt stops the loop
      immediately and proceeds to FINALIZE.
- [ ] 2.7 Implement FINALIZE: on `PASS` (from the first VERIFY pass or any
      re-VERIFY within the fix loop), one Codex turn (resuming
      `codex_session_id`) instructing commit and cleanup. Verify this is
      the only path that reaches FINALIZE, and that exhausting the fix
      loop (task 2.6) never reaches it.
- [ ] 2.8 Add a `stage` field to every JSONL log line (`plan`, `implement`,
      `verify`, `ask`, `fix`, `finalize`), reusing the existing
      `--change quant-research-round-<N>`-derived log path unchanged.
      Verify log lines from a full fake cycle each carry the correct
      `stage` value.

## 3. Documentation

- [ ] 3.1 Rewrite `tools/orchestrator/README.md`'s `quant-research-exec`
      section for the zero-required-argument full cycle (drop `--role`/
      generic `--model`/`--effort` mentions, document the new per-provider
      model/effort/escalated-model flags, the plan/verify/fix(5-attempt,
      escalating)/finalize shape, and the `stage` log field). Verify by
      reading it against the implemented CLI and log output.
- [ ] 3.2 Rewrite `.claude/commands/quant/research.md`: Claude's
      interactive session (or the operator directly) now runs one
      `quant-research-exec` invocation per round instead of driving
      PLAN/IMPLEMENT/VERIFY/FIX step by step; the command's remaining job
      is reading back the finished round's result and, for `PROMOTE`,
      running `/opsx:propose`. Verify by reading the updated file for
      internal consistency with the new command behavior.
- [ ] 3.3 Reconcile `add-quant-research-exec-command`'s still-unarchived
      spec delta (`--role implement/fix`, operator-supplied brief required,
      no session continuity) with this change's superseding delta before
      either is archived — archiving both as-is would leave two deltas
      describing contradictory requirements for the same command. Verify
      `openspec validate` on both changes (or the combined result if
      archived together) does not report a conflict.

## 4. Verification

- [ ] 4.1 Run `uv run --project tools/orchestrator pytest`, `ruff check .`,
      `ruff format --check .`, and `ty check .` from `tools/orchestrator/`
      and verify all pass.
- [ ] 4.2 Run `uv run --project tools/orchestrator sync-agent-links --check`
      and verify it reports synchronized.
- [ ] 4.3 Exercise one real round end-to-end (real Codex + Claude SDK
      calls, not fakes) in a dedicated round worktree, per
      `.agents/rules/coding-and-verification.md`'s per-change worktree
      workflow, running `quant-research-exec` with zero arguments. Verify:
      PLAN genuinely picks a hypothesis from the real backlog (confirm via
      the JSONL log that a real `ClaudeProvider` PLAN turn ran, not a
      stub), IMPLEMENT drafts a round file, VERIFY independently reviews
      it, and the cycle reaches either FINALIZE or the 5-attempt
      fix-budget error — not left hanging.
