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
      than assuming; adjust PLAN's turn configuration (task 3.2) if needed.

## 2. Worktree lifecycle (SYNC / SETUP-WORKTREE / MERGE+CLEANUP)

- [ ] 2.1 Add a `sync_and_resolve_round(cwd) -> int` helper (git subprocess
      calls, no LLM turn): `git fetch origin`, `git merge --ff-only
      origin/<default-branch>` in `cwd`, then resolve and return the round
      number by scanning `research/quant/rounds/` in that now-synced tree
      (reuse the existing `highest_round_number` logic). Only called when
      `--cwd` was not given; PLAN then runs directly in this same `cwd`
      (no worktree yet). Verify with a real throwaway git repo fixture
      (not a fake): after calling this, `cwd`'s `<default-branch>` matches
      `origin/<default-branch>`, and the returned number is one past the
      highest existing round file.
- [ ] 2.2 Add a `create_round_worktree(cwd, round_number) -> Path` helper:
      `git worktree add .agents/worktrees/quant-research-round-<round_number>
      -b quant-research-round-<round_number> <default-branch>` in `cwd`;
      return the new worktree's path. Called once, after PLAN produces a
      brief, using the round number `sync_and_resolve_round` already
      returned (no re-scan). Verify with a real throwaway git repo
      fixture: the worktree exists afterward, is on the expected branch,
      and contains the synced tree's content.
- [ ] 2.3 Add a `merge_and_cleanup_worktree(worktree_path, branch, cwd)`
      helper: from the *original* `cwd` (not the worktree), fetch and
      fast-forward `<default-branch>` to `origin/<default-branch>` again,
      then `git merge --ff-only <branch>`; on failure, rebase `<branch>`
      onto the freshly-synced `<default-branch>` and retry the ff-only
      merge; on success, `git worktree remove <worktree_path>` and
      `git branch -d <branch>`. Verify with a real throwaway git repo
      fixture: a clean ff case merges and removes the worktree; a case
      where `<default-branch>` advanced first still merges via
      rebase-then-ff and removes the worktree; the worktree and branch are
      *not* removed if the merge step itself raises.
- [ ] 2.4 Wire these into `quant_research_exec.py`'s `main()`: call
      `sync_and_resolve_round` before PLAN when `--cwd` is omitted (PLAN
      runs in that same `cwd`, logging under the now-known
      `quant-research-round-<N>`); call `create_round_worktree` right after
      PLAN produces its brief, and use its returned path as every stage
      from IMPLEMENT onward's `cwd`; call `merge_and_cleanup_worktree`
      after a successful FINALIZE; on any hard error (unparseable marker,
      exhausted fix budget, a stage's own turn failure) at any point after
      a worktree exists, skip cleanup and let the error propagate with the
      worktree left in place. When `--cwd` is given explicitly, skip all
      three helpers and resolve the round number directly against the
      given `cwd` for every stage including PLAN, unchanged from
      `add-quant-research-exec-command`'s prior behavior. Verify with
      fakes: a full successful fake cycle with no `--cwd` calls all three
      helpers in order (sync → plan → create-worktree → implement...); a
      fake cycle that ends in the exhausted-fix-budget error never calls
      `merge_and_cleanup_worktree`; a fake cycle with an explicit `--cwd`
      calls none of the three helpers.

## 3. Cycle orchestration

- [ ] 3.1 Rewrite `quant_research_exec.py`'s CLI surface: drop `--role`;
      make the positional `PROMPT`/`--prompt-file` optional PLAN guidance
      (not a required brief); keep `--round` (auto-detect, resolved during
      SYNC per task 2.1, or directly against `--cwd` when one is given);
      replace `--model`/`--effort` with `--codex-model`/`--codex-effort`/
      `--codex-escalated-model`/`--claude-model`/`--claude-effort`/
      `--claude-escalated-model`; raise the default `--timeout-seconds` to
      3600. Verify `--help` shows no `--role`, no generic `--model`/
      `--effort`, all six new flags, and that `quant-research-exec` with
      zero arguments parses successfully (no "required" error).
- [ ] 3.2 Implement the PLAN stage: one `ClaudeProvider.run_turn` with the
      domain rules, the round-selection backlog files (index.md, metrics
      CSV, recent round files), any optional operator guidance, and the
      `PLAN_BRIEF:` format instruction (informed by task 1.4's findings for
      tool access); parse the brief; capture `claude_session_id` from
      `last_session_id`. Verify with a fake Claude client that a missing
      `PLAN_BRIEF:` line raises the documented hard error before Codex is
      ever invoked.
- [ ] 3.3 Implement the IMPLEMENT stage: one `CodexProvider.run_turn` with
      the domain rules + PLAN's brief, `resume_id=None` (fresh thread),
      capturing `codex_session_id` from `last_session_id` after.
- [ ] 3.4 Implement the VERIFY stage as a reusable function taking an
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
- [ ] 3.5 Implement the ASK round-trip: on `QUESTION <text>`, one Codex
      turn (resuming `codex_session_id`) answering `<text>`, then one
      Claude turn (resuming `claude_session_id`) with that answer,
      accepting only `PASS`/`DEFECT` from the continuation (a second
      `QUESTION` here is a hard error, not another round-trip). Verify
      with fakes asserting exactly one Codex turn and one Claude turn run
      for a `QUESTION` verdict, and that a second `QUESTION` in the
      continuation raises the documented error.
- [ ] 3.6 Implement the bounded FIX loop: on `DEFECT`, up to 5 attempts of
      (one Codex FIX turn resuming `codex_session_id` with the `DEFECT`
      issue text, then task 3.4's VERIFY logic again resuming
      `claude_session_id`). Attempts 1-2 use the given/default
      `--codex-*`/`--claude-*` model/effort; attempt 3 onward escalates to
      each provider's highest effort (and its `--*-escalated-model` if
      given). If the 5th re-VERIFY still returns `DEFECT`, exit non-zero
      with an error and do not run FINALIZE. Verify with fakes: exactly 5
      FIX turns run when every re-VERIFY keeps returning `DEFECT` (never a
      6th), attempts 1-2 use the base model/effort and attempt 3+ use the
      escalated values, and a `PASS` on any attempt stops the loop
      immediately and proceeds to FINALIZE.
- [ ] 3.7 Implement FINALIZE: on `PASS` (from the first VERIFY pass or any
      re-VERIFY within the fix loop), one Codex turn (resuming
      `codex_session_id`) instructing commit and cleanup, followed by task
      2.2's `merge_and_cleanup_worktree` (when applicable). Verify this is
      the only path that reaches FINALIZE, and that exhausting the fix
      loop (task 3.6) never reaches it.
- [ ] 3.8 Add a `stage` field to every JSONL log line (`setup`, `plan`,
      `implement`, `verify`, `ask`, `fix`, `finalize`, `merge`), reusing
      the existing `--change quant-research-round-<N>`-derived log path
      unchanged. Verify log lines from a full fake cycle each carry the
      correct `stage` value.

## 4. Documentation

- [ ] 4.1 Rewrite `tools/orchestrator/README.md`'s `quant-research-exec`
      section for the zero-required-argument full cycle (drop `--role`/
      generic `--model`/`--effort` mentions, document the new per-provider
      model/effort/escalated-model flags, the plan/verify/fix(5-attempt,
      escalating)/finalize shape, the worktree lifecycle (created/entered
      when `--cwd` is omitted, merged and removed on success, left in
      place on error, skipped entirely when `--cwd` is given), and the
      `stage` log field). Verify by reading it against the implemented CLI
      and log output.
- [ ] 4.2 Rewrite `.claude/commands/quant/research.md`: Claude's
      interactive session (or the operator directly) now runs one
      `quant-research-exec` invocation per round instead of driving
      PLAN/IMPLEMENT/VERIFY/FIX step by step, and no longer needs to
      create/enter/merge a worktree by hand (the command does it). The
      command's remaining job is reading back the finished round's result
      and, for `PROMOTE`, running `/opsx:propose`. Verify by reading the
      updated file for internal consistency with the new command behavior.
- [ ] 4.3 Reconcile `add-quant-research-exec-command`'s still-unarchived
      spec delta (`--role implement/fix`, operator-supplied brief required,
      no session continuity, no worktree management) with this change's
      superseding delta before either is archived — archiving both as-is
      would leave two deltas describing contradictory requirements for the
      same command. Verify `openspec validate` on both changes (or the
      combined result if archived together) does not report a conflict.

## 5. Verification

- [ ] 5.1 Run `uv run --project tools/orchestrator pytest`, `ruff check .`,
      `ruff format --check .`, and `ty check .` from `tools/orchestrator/`
      and verify all pass.
- [ ] 5.2 Run `uv run --project tools/orchestrator sync-agent-links --check`
      and verify it reports synchronized.
- [ ] 5.3 Exercise one real round end-to-end (real Codex + Claude SDK
      calls, not fakes), running `quant-research-exec` with zero
      arguments from the real repository (letting it manage its own
      worktree per section 2 — do not pre-create one by hand for this
      task, that would not exercise SYNC/SETUP-WORKTREE/MERGE+CLEANUP).
      Verify: PLAN genuinely picked a hypothesis from the real backlog
      before any worktree existed (confirm via the JSONL log that a real
      `ClaudeProvider` PLAN turn ran, not a stub), a worktree was created
      right after, IMPLEMENT drafted a round file, VERIFY
      independently reviewed it, the cycle reached either FINALIZE or the
      5-attempt fix-budget error, and — if FINALIZE ran — the worktree no
      longer exists afterward and the round's commit landed on local
      `main`.
