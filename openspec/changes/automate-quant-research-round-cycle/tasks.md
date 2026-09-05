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

## 2. Cycle orchestration

- [ ] 2.1 Rewrite `quant_research_exec.py`'s CLI surface: drop `--role`,
      keep `--round` (same auto-detect-for-implement semantics, now
      unconditional since there's one entry point), drop `--model`/
      `--effort`, raise the default `--timeout-seconds` to 3600. Verify
      `--help` output matches (no `--role`, no `--model`, no `--effort`,
      default shown as 3600).
- [ ] 2.2 Implement the IMPLEMENT stage: one `CodexProvider.run_turn` with
      the domain rules + supplied plan, `resume_id=None` (fresh thread),
      capturing `codex_session_id` from `last_session_id` after. Verify
      with a fake Codex client that the assembled prompt matches the
      existing (already-shipped) domain-rules-plus-brief shape.
- [ ] 2.3 Implement the VERIFY stage: one `ClaudeProvider.run_turn` given
      the domain rules, a description of what IMPLEMENT/FIX produced (the
      round file path, CSV path, log path), and the `VERIFY_RESULT:`
      format instruction; parse the last matching `VERIFY_RESULT:` line
      per design.md Decision 3. Verify: PASS/FAIL/QUESTION are each parsed
      correctly from a fake Claude result string; a result with no
      matching line raises the documented hard error before any further
      stage runs.
- [ ] 2.4 Implement the ASK round-trip: on `QUESTION <text>`, one Codex
      turn (resuming `codex_session_id`) answering `<text>`, then one
      Claude turn (resuming `claude_session_id`) with that answer,
      accepting only `PASS`/`FAIL` from the continuation (a second
      `QUESTION` here is a hard error, not another round-trip). Verify
      with fakes asserting exactly one Codex turn and one Claude turn run
      for a `QUESTION` verdict, and that a second `QUESTION` in the
      continuation raises the documented error.
- [ ] 2.5 Implement the FIX stage: on `FAIL` from the *first* verify pass,
      one Codex turn (resuming `codex_session_id`) with the `FAIL` issue
      text, then one more VERIFY pass (task 2.3's logic, reused). Verify
      with fakes that FIX runs exactly once even if the re-verify also
      fails (task 2.6 covers what happens then).
- [ ] 2.6 Implement CLOSE-HONEST: on `FAIL` from the *second* verify pass
      (i.e., after one FIX already ran), one Codex turn (resuming
      `codex_session_id`) instructing an honest `NEEDS-MORE-RESEARCH`/
      `DATA-ISSUE` reclassification and commit, skipping FINALIZE. Verify
      no second FIX turn ever runs in this path.
- [ ] 2.7 Implement FINALIZE: on `PASS` (first or post-fix verify pass),
      one Codex turn (resuming `codex_session_id`) instructing commit and
      cleanup. Verify this is the only path that reaches FINALIZE.
- [ ] 2.8 Add a `stage` field to every JSONL log line (per design.md
      Decision 8), reusing the existing `--change quant-research-round-<N>`-
      derived log path unchanged. Verify log lines from a full fake cycle
      each carry the correct `stage` value.

## 3. Documentation

- [ ] 3.1 Rewrite `tools/orchestrator/README.md`'s `quant-research-exec`
      section for the new one-invocation cycle (drop `--role`/`--model`/
      `--effort` mentions, document the verify/fix/close-honest/finalize
      shape and the `stage` log field). Verify by reading it against the
      implemented CLI and log output.
- [ ] 3.2 Rewrite `.claude/commands/quant/research.md`'s Bước 3-8 to match:
      Claude PLAN hands the plan to one `quant-research-exec` call; Claude
      reads back the finished round's evidence for a final sanity check
      instead of driving VERIFY/FIX itself turn-by-turn. Verify by reading
      the updated file for internal consistency with the new command
      behavior.
- [ ] 3.3 Add a task to reconcile `add-quant-research-exec-command`'s
      still-unarchived spec delta (`--role implement/fix`,
      `.agents/domain/...` prompt assembly with no session continuity)
      with this change's superseding delta before either is archived —
      archiving both as-is would leave two deltas describing contradictory
      requirements for the same command. Verify `openspec validate` on
      both changes (or the combined result if archived together) does not
      report a conflict.

## 4. Verification

- [ ] 4.1 Run `uv run --project tools/orchestrator pytest`, `ruff check .`,
      `ruff format --check .`, and `ty check .` from `tools/orchestrator/`
      and verify all pass.
- [ ] 4.2 Run `uv run --project tools/orchestrator sync-agent-links --check`
      and verify it reports synchronized.
- [ ] 4.3 Exercise one real round end-to-end (real Codex + Claude SDK
      calls, not fakes) in a dedicated round worktree, per
      `.agents/rules/coding-and-verification.md`'s per-change worktree
      workflow, and verify: IMPLEMENT drafts a round file, VERIFY
      genuinely reads it independently (confirm via the JSONL log that a
      real `ClaudeProvider` turn ran, not a stub), and the cycle reaches
      either FINALIZE or CLOSE-HONEST — not left hanging.
