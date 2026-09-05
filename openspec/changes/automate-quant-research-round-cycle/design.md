## Context

See `proposal.md` - Why. This replaces `add-quant-research-exec-command`'s
design for the same command (that change is `complete`, not yet archived);
this design supersedes its decisions rather than extending them.

Existing surface this builds on:

- `orchestrator.providers.codex.CodexProvider` and
  `orchestrator.providers.claude.ClaudeProvider`: both expose the same
  `BaseProvider.run_turn(prompt, *, cwd, timeout_seconds, on_event) ->
  ProviderResult(success, text, error)` shape, with their own account
  failover already handled internally. Both gain a small addition here
  (Decision 2): capturing and resuming the underlying SDK session/thread
  id, so a later stage doesn't have to re-explain everything to a fresh,
  memoryless turn.
- The underlying SDKs already support this: `openai_codex`'s
  `AsyncCodex.thread_resume(thread_id, ...)` continues an existing thread
  (confirmed present in the installed SDK); `claude_agent_sdk`'s
  `ClaudeAgentOptions.resume: str | None` loads a prior session by the
  `session_id` a `ResultMessage` already carries (also confirmed present
  and already read by `ClaudeProvider.stream()` today).
- `orchestrator.cli._shared`: `resolve_log_path`, `emit_event`/`emit_result`/
  `emit_error` (redacted stdout + JSONL), unchanged.
- `.agents/domain/quant-research-domain.md`: the non-negotiable invariants
  and classification/promotion rules that PLAN, IMPLEMENT, and VERIFY must
  all read.
- Round 453 (this session) ran under the prior single-stage, operator-
  supplied-plan design and will finish under it; this design applies to
  rounds started after this change merges.

## Goals / Non-Goals

**Goals:**
- One bare `quant-research-exec` invocation — no required flags — runs an
  entire round: Claude PLANs (reads the backlog, picks a hypothesis,
  designs the test), Codex IMPLEMENTs, Claude VERIFIES, Codex FIXes within
  a bounded, escalating retry budget if VERIFY finds a defect, Codex
  FINALIZEs. This must be safe to run as `while true; do quant-research-exec;
  sleep <n>; done` with zero parameters inserted.
- Verify stays genuinely independent: it runs through `ClaudeProvider` (a
  different provider than the one that implemented), reading the same
  domain invariants, and judges evidence/classification trustworthiness —
  never whether the hypothesis succeeded. Never Codex grading its own work.
- Every retry (fix, and the verify-question round-trip) is bounded — no
  path in this design can loop indefinitely, even though the outer
  "run another round" loop is the operator's own choice and has no bound
  imposed by this tool.

**Non-Goals:**
- Automating the `PROMOTE` → `/opsx:propose` step. Creating OpenSpec
  planning artifacts is Claude's job and a scripted turn has no
  slash-command/skill discovery to invoke it — a `PROMOTE` classification
  still stops at FINALIZE (commit the round's evidence) and reports the
  stable change name for the operator's own interactive Claude session to
  act on next.
- A generic multi-agent messaging framework. The Codex↔Claude round-trip
  added here (Decision 5) is one narrow, single-purpose, bounded exchange
  for this cycle only — not a reusable inter-agent protocol.
- Retrofitting round 453 or any round already running under the prior
  design.
- Bounding how many rounds an operator chooses to run back-to-back. That is
  explicitly the operator's own call (per `CLAUDE.md`'s "no automatic
  resolver/coordinator" and "operator runs each round manually" — manually
  choosing to loop this command is the operator manually running each
  round, just without re-typing a command each time); this tool only
  bounds what happens *inside* one round.

## Decisions

**1. Stage sequence and state machine.**

```
PLAN (Claude)
   │  reads research/quant/index.md, reports CSV, recent round files, and
   │  .agents/domain/quant-research-domain.md; picks one open hypothesis
   │  (XAU before BTC); designs the test; writes a brief for Codex
   ▼
IMPLEMENT (Codex)
   │  runs the backtest against PLAN's brief; drafts round file + CSV/
   │  index updates; does not commit
   ▼
VERIFY (Claude, resumes PLAN's session)  ──QUESTION──▶ ASK (Codex, one turn)
   │                                          └──▶ VERIFY continues (same pass)
   ├─ PASS ──▶ FINALIZE (Codex: commit)
   │
   └─ DEFECT ──▶ FIX (Codex) ──▶ VERIFY again ─┬─ PASS ──▶ FINALIZE
                     ▲                          │
                     └──────── DEFECT ──────────┘
                (attempts 1-5; attempt 3+ escalates model/effort —
                 see Decision 6; attempt 5 still DEFECT is a hard error,
                 nothing committed)
```

Every box is one `CodexProvider.run_turn` or `ClaudeProvider.run_turn`
call. Codex's session is resumed across IMPLEMENT→ASK→every FIX
attempt→FINALIZE; Claude's session is resumed across PLAN→VERIFY→its own
question-continuation→every re-VERIFY (Decision 2) — VERIFY resuming
PLAN's own session means Claude's review already has full context of *why*
it chose this hypothesis and what it decided would count as evidence,
without the orchestrator re-deriving that context in the VERIFY prompt.
The Python orchestrator in `quant_research_exec.py` drives this sequence
directly (plain `if`/`while` control flow over `await
provider.run_turn(...)` calls) — no new concurrency primitive, no
background task.

There is no separate "close honest" stage. A round whose research outcome
is negative (`REJECTED`/`NO-CHANGE`/`NEEDS-MORE-RESEARCH`/`DATA-ISSUE`) but
whose execution was sound reaches `PASS` and FINALIZE exactly like a
`PROMOTE` outcome would — VERIFY judges whether the *evidence and
classification are trustworthy*, never whether the hypothesis succeeded
(Decision 4). If a DEFECT turns out to be something FIX cannot literally
patch (e.g. the test design itself needs to change, not the code), the
honest response is for that FIX turn to rewrite the round's own
classification to `NEEDS-MORE-RESEARCH`/`DATA-ISSUE` with a clear
explanation — at which point the evidence is sound again and the next
VERIFY pass correctly returns `PASS`. There is still a hard stop: the
fix→re-verify loop is capped at 5 attempts (Decision 6); if the 5th
re-verify still returns `DEFECT`, the command exits with an error and
commits nothing.

**2. Capture and resume each actor's session/thread id across the cycle.**

`BaseProvider` gains an optional `resume_id: str | None` parameter threaded
through `start_turn(prompt, *, cwd, account, resume_id)` (default `None` —
`codex-exec`/`claude-exec`/existing tests are unaffected when they never
pass one), and a `last_session_id` property read after `collect_result()`:

- `CodexProvider.start_turn` calls `codex.thread_resume(resume_id, ...)`
  instead of `codex.thread_start(...)` when `resume_id` is given, and
  records the thread's id (from the `ThreadStartResponse`/`ThreadResumeResponse`)
  as `last_session_id`.
- `ClaudeProvider.start_turn` sets `ClaudeAgentOptions(resume=resume_id,
  ...)` when given, and `last_session_id` reads
  `self._result_message.session_id` after a turn (that field already
  exists and is already read for other purposes in `fakes.py`).

`quant_research_exec.py` keeps two local variables for the cycle's
lifetime, `claude_session_id` (set after PLAN, reused for VERIFY and every
re-VERIFY/question-continuation) and `codex_session_id` (set after
IMPLEMENT, reused for ASK/FIX/FINALIZE). This is the *only* reason
`BaseProvider` changes — account failover within one `run_turn` call is
untouched; this adds continuity *across* separate `run_turn` calls, a
different axis.

Alternative considered: keep every stage a fresh, independent turn and have
the orchestrator re-paste full context into each prompt. Rejected once
session resumption was confirmed available in both SDKs — re-deriving
context an actor already has is strictly worse: slower, more expensive,
and a fresh turn re-reading prior work from disk cannot recover *why* a
judgment call was made the way a resumed session's own memory can.

**3. PLAN runs through Claude, automatically, with no operator-supplied
brief required.**

The bare, zero-argument invocation must work (this is the whole point of
the redesign), so PLAN cannot depend on the operator having already chosen
a hypothesis interactively. `quant_research_exec.py` starts every cycle
with one `ClaudeProvider.run_turn` whose prompt is
`.agents/domain/quant-research-domain.md`'s content plus an instruction to:
read the round-number-resolution logic's target files
(`research/quant/index.md`, `research/quant/reports/optimize_loop_update_v2.csv`,
recent files under `research/quant/rounds/`), pick one open hypothesis
(XAU before BTC per the domain rules), design the test, and end with a
`PLAN_BRIEF:` marker line (parsed the same strict way as `VERIFY_RESULT:`,
Decision 4) followed by the brief text IMPLEMENT will receive verbatim.

The positional `PROMPT`/`--prompt-file` argument becomes optional operator
*guidance* folded into the PLAN prompt (e.g. "consider X" or a specific
instrument to prioritize this round) rather than the whole brief — when
omitted, PLAN works from the backlog alone, exactly as `while true; do
quant-research-exec; sleep <n>; done` requires.

Alternative considered: keep PLAN as the operator's own interactive-session
job and require a brief as input (the prior design). Rejected per explicit
operator direction — a bare, parameter-free invocation is the actual
requirement, and the interactive session already has `ClaudeProvider`
available to it for every other stage, so there is no technical reason
PLAN alone must stay outside the tool.

**4. Verify's verdict is a structured marker line, not inferred prose;
`PASS` judges evidence quality, not the research outcome's sign.**

The VERIFY prompt instructs Claude to end its final message with exactly
one of:

```
VERIFY_RESULT: PASS
VERIFY_RESULT: DEFECT <one-line issue summary>
VERIFY_RESULT: QUESTION <one question>
```

`PASS` means the round's evidence is honestly measured, not fabricated or
cherry-picked, with a genuinely disjoint holdout, and its classification
matches its own numbers — regardless of whether that classification is
`PROMOTE` or `REJECTED`. `DEFECT` is reserved for an actual problem with
*how* the round was executed or measured, never for "the hypothesis
didn't work." The orchestrator finds the last line matching
`^VERIFY_RESULT: (PASS|DEFECT|QUESTION)\b` in the turn's result text; no
match is a hard error (`emit_error`, exit non-zero) — the orchestrator
never guesses a verdict from unstructured prose. A second `QUESTION`
within the same verify pass (Decision 5) is a parse error, not another
round-trip.

Alternative considered: parse free-form prose for approval/rejection
language. Rejected — exactly the kind of ambiguity this feature exists to
avoid.

**5. The verify→question→answer round-trip asks Codex, bounded to one
exchange.**

When a VERIFY pass returns `QUESTION <text>`, the orchestrator sends Codex
one turn (resuming `codex_session_id`) asking it to answer `<text>` about
the round it just worked on, then sends Claude one continuation turn
(resuming `claude_session_id`) with that answer, instructing that no
further question is accepted this pass — it must end with `PASS` or
`DEFECT`. Codex is the party with full context of what it just did, the
natural one to answer a clarifying question about its own work, the same
way a code author answers a reviewer's question. Rejected alternative:
spawn a fresh Claude sub-agent review turn instead — it would need the
full round context re-supplied from scratch to answer what is usually a
question about *why Codex did something*, which Codex already knows and a
fresh reviewer would not.

**6. Fix is bounded to 5 attempts, with model/effort escalation from
attempt 3 onward.**

Each `DEFECT` verdict triggers one Codex FIX turn (resuming
`codex_session_id`, given the issue text as its brief) and one more VERIFY
pass (resuming `claude_session_id`), up to 5 fix attempts total. Attempts
1-2 use the operator-given (or default) `--codex-model`/`--codex-effort`/
`--claude-model`/`--claude-effort`. From attempt 3 onward, both the FIX
turn and the re-VERIFY turn escalate to the highest effort level each SDK
exposes, and to `--codex-escalated-model`/`--claude-escalated-model` when
the operator supplied one (optional, `None` by default — escalation then
just raises effort, same model). If the 5th re-verify still returns
`DEFECT`, the command exits non-zero with an error and commits nothing —
intentionally *not* auto-classified as `DATA-ISSUE` on the round's behalf;
a defect five escalating attempts couldn't resolve needs an operator to
look at it.

Alternative considered (raised and revised twice during design): no
attempt cap at all, loop until `PASS`. Rejected in favor of a bound —
consistent with this project's "no unbounded quota burn" principle; a
defect that isn't fixable by re-prompting would otherwise consume Codex
turns indefinitely with no one in the loop to notice.

**7. `--role` and the operator-required brief are both gone; `--round`
keeps auto-detecting; per-provider model/effort flags replace the generic
ones.**

```
quant-research-exec [PROMPT] [--prompt-file FILE] [--round N]
                     [--cwd DIR] [--timeout-seconds N]
                     [--codex-model NAME] [--codex-effort LEVEL]
                     [--codex-escalated-model NAME]
                     [--claude-model NAME] [--claude-effort LEVEL]
                     [--claude-escalated-model NAME]
```

Every argument is optional — `quant-research-exec` with zero flags runs a
complete round end to end, resolving its own next round number and
choosing its own hypothesis (Decisions 3 and the existing round-file
auto-detect logic). `PROMPT`/`--prompt-file` becomes optional PLAN
guidance (Decision 3), not a required brief. `--model`/`--effort` split
into per-provider flags (`--codex-*` for IMPLEMENT/ASK/FIX/FINALIZE,
`--claude-*` for PLAN/VERIFY) since the two providers have unrelated model
namespaces — a single generic `--model` would be ambiguous with two
providers in one invocation.

**8. One `--timeout-seconds` value applies per stage, with a much larger
default than `codex-exec`'s.**

Each stage (plan, implement, verify, ask, fix, finalize) gets its own
independent `timeout_seconds` budget. Default changes from the generic
`DEFAULT_TIMEOUT_SECONDS` (300s, sized for a quick one-off turn) to a
quant-research-specific default of 3600s (round 452's real implement turn
took ~20 minutes) — still overridable via `--timeout-seconds`.

**9. Logging: one log file per round, a `stage` field on every line.**

Still `tools/orchestrator/logs/quant-research-round-<N>/quant-research-exec.log`
(unchanged path convention — `<N>` is now resolved before PLAN even runs,
same auto-detect logic as before), but every emitted JSONL line now
includes `"stage": "plan" | "implement" | "verify" | "ask" | "fix" |
"finalize"` so a reader (or a future log-streaming UI) can reconstruct
which part of the cycle produced which event.

## Risks / Trade-offs

- [Automating PLAN removes the interactive session's broader judgment
  (e.g. web search across multiple external sources when the backlog is
  exhausted, per the domain rules' Module 1 fallback) — a scripted Claude
  turn needs the same tool access to do this well] → PLAN's `ClaudeProvider`
  turn must be configured with the same tool access (bash, and web search
  if the SDK route supports it in headless/non-interactive mode) that the
  domain rules' backlog-exhaustion fallback requires; verify this
  concretely during implementation (task 1.4) rather than assuming it.
- [A resumed thread/session accumulates a long conversation across
  plan/implement/verify/ask/fix/finalize, risking context-window bloat] →
  Bounded by Decision 6 already keeping the *number* of resumed turns
  small (at most implement + ask + 5×fix + finalize = 8 for Codex, at most
  plan + verify + ask-continuation + 5×re-verify = 8 for Claude); each
  individual prompt stays focused on its own instruction, not re-pasting
  history.
- [`thread_resume`/`resume=` fails (stale id, backend error) mid-cycle] →
  Surfaces as that stage's own `ProviderResult(success=False, ...)`; the
  orchestrator aborts the cycle with an error rather than silently
  starting a fresh, memory-less turn in its place.
- [Asking Codex to answer its own question could get a self-serving
  answer] → Not fully solvable without a second independent party
  (rejected in Decision 5 as disproportionate); mitigated by the
  one-question cap and by Claude's re-verify still being free to return
  `DEFECT` even after getting an answer.
- [Running this in a `while true` loop with no operator judgment between
  rounds, as explicitly requested, removes the human checkpoint that
  historically caught bad rounds early] → Accepted per explicit operator
  direction; every round still independently goes through Claude PLAN and
  Claude VERIFY (not skipped), so the tool retains its internal checks —
  what's removed is only the *interactive* pause between rounds, not the
  PLAN/VERIFY roles themselves.
- [`.claude/commands/quant/research.md`'s Bước 1-8 describe the old
  hand-driven flow] → Tracked as its own task (see tasks.md) so it isn't
  forgotten.

## Migration Plan

`quant-research-exec`'s CLI surface changes (removes `--role`; the
positional brief becomes optional guidance instead of required; replaces
`--model`/`--effort` with six per-provider flags; changes default
timeout) — a breaking change to that one command's flags, not to
`codex-exec`/`claude-exec`/anything else. No round is currently relying on
the old flags outside this session's own manual testing. Update
`.claude/commands/quant/research.md` in the same change so documented
usage never drifts from implemented behavior.
