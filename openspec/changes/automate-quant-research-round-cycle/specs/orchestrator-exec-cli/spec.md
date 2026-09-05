## ADDED Requirements

### Requirement: quant-research-exec runs one full round cycle with zero required arguments
The system SHALL provide a `quant-research-exec` command that, with no
required arguments, runs an entire round cycle in one invocation: Claude
PLAN (choose a hypothesis and design a test from the current backlog),
Codex IMPLEMENT, Claude VERIFY, and — only if VERIFY finds a defect — up
to 5 Codex FIX attempts each followed by a re-VERIFY, then Codex FINALIZE.
The command SHALL NOT accept a `--role` flag; there is exactly one entry
point. An optional positional prompt or `--prompt-file` SHALL be accepted
as additional PLAN guidance, never as a required brief.

#### Scenario: A bare invocation runs a complete round
- **WHEN** an operator runs `quant-research-exec` with no arguments
- **THEN** the command runs PLAN, then IMPLEMENT, then VERIFY, and (absent
  a defect) FINALIZE, without requiring the operator to have supplied a
  hypothesis or plan

#### Scenario: A round needs a fix within the attempt budget
- **WHEN** VERIFY returns `DEFECT <issue>` after IMPLEMENT, and the
  following re-VERIFY (after at most 5 FIX attempts) returns `PASS`
- **THEN** the command proceeds to FINALIZE

#### Scenario: A round exhausts its fix budget
- **WHEN** the re-VERIFY pass after the 5th FIX attempt still returns
  `DEFECT`
- **THEN** the command exits non-zero with an error, runs no 6th FIX
  attempt, and does not run FINALIZE

### Requirement: Plan and verify both run through a different provider than implement
The system SHALL run the PLAN and VERIFY stages through `ClaudeProvider`,
never through the `CodexProvider` turn or thread used for IMPLEMENT or
FIX, so that Codex neither chooses its own hypothesis unchecked nor grades
its own work. VERIFY SHALL judge only whether the round's evidence and
stated classification are trustworthy (honestly measured, not fabricated
or cherry-picked, holdout genuinely disjoint, classification matching the
numbers) — a negative research outcome
(`REJECTED`/`NO-CHANGE`/`NEEDS-MORE-RESEARCH`/`DATA-ISSUE`) that is
honestly and correctly evidenced SHALL be treated as `PASS`, not `DEFECT`.

#### Scenario: Plan and verify use Claude
- **WHEN** the command reaches the PLAN or VERIFY stage
- **THEN** that turn is sent via `ClaudeProvider`, not `CodexProvider`

#### Scenario: An honest negative result passes verify
- **WHEN** IMPLEMENT's evidence is complete, honestly measured, and
  correctly classified as `REJECTED`
- **THEN** VERIFY returns `PASS`, not `DEFECT`

### Requirement: Plan and verify verdicts are structured markers, parsed strictly
Claude's PLAN turn SHALL end its result text with a `PLAN_BRIEF:` marker
line followed by the brief IMPLEMENT receives. Claude's VERIFY turn SHALL
end its result text with exactly one line matching `VERIFY_RESULT: PASS`,
`VERIFY_RESULT: DEFECT <issue>`, or `VERIFY_RESULT: QUESTION <question>`.
The command SHALL treat the absence of a matching marker as a hard error
in either case and SHALL NOT infer a brief or verdict from any other text
in the result.

#### Scenario: Unparseable verify result is a hard error
- **WHEN** Claude's VERIFY turn result text contains no line matching
  `VERIFY_RESULT: (PASS|DEFECT|QUESTION)`
- **THEN** the command exits non-zero with an error and does not proceed to
  FIX or FINALIZE

#### Scenario: Unparseable plan result is a hard error
- **WHEN** Claude's PLAN turn result text contains no `PLAN_BRIEF:` line
- **THEN** the command exits non-zero with an error and does not invoke
  Codex

### Requirement: A verify question is answered by Codex, bounded to one round-trip
When a VERIFY pass returns `QUESTION <text>`, the system SHALL send that
question to Codex as one turn, then send Claude one continuation turn with
Codex's answer, instructing that no further question is accepted this
pass. The system SHALL treat a second `QUESTION` within the same verify
pass as an error, not as another round-trip.

#### Scenario: A verify question is resolved in one round-trip
- **WHEN** VERIFY returns `QUESTION <text>`
- **THEN** the command sends Codex one turn to answer `<text>`, then sends
  Claude one more turn with that answer, and accepts only `PASS` or
  `DEFECT` from that continuation

### Requirement: Fix is bounded to 5 attempts, escalating effort from attempt 3
Each `DEFECT` verdict SHALL trigger one Codex FIX turn and one re-VERIFY
pass, up to 5 such attempts for one implement/fix chain. Attempts 1-2
SHALL use the configured (or default) model/effort for each provider. From
attempt 3 onward, the system SHALL raise both the Codex FIX turn's and the
Claude re-VERIFY turn's effort to the highest level each SDK exposes, and
SHALL switch to that provider's configured escalated model when one was
given. If the 5th re-VERIFY still returns `DEFECT`, the system SHALL stop
(no 6th attempt) and exit non-zero without finalizing.

#### Scenario: Escalation applies from the third attempt
- **WHEN** attempts 1 and 2 both end with `DEFECT`
- **THEN** attempt 3's FIX and re-VERIFY turns run at the highest available
  effort level (and the configured escalated model, if any), not the
  default effort/model used for attempts 1-2

### Requirement: Each actor's session is resumed across its own stages
`CodexProvider` and `ClaudeProvider` SHALL accept an optional session/
thread id to resume a prior turn's session, and SHALL expose the resulting
session/thread id after a turn completes. `quant-research-exec` SHALL
resume Claude's session across PLAN→VERIFY→its own question-continuation→
every re-VERIFY, and resume Codex's session across
IMPLEMENT→ASK→every FIX attempt→FINALIZE, so a later stage is not re-told
context its own prior turn already has. `codex-exec`/`claude-exec` SHALL be
unaffected: neither passes a resume id, and both continue to start a fresh
session per invocation exactly as before.

#### Scenario: Verify resumes plan's session
- **WHEN** the command runs the VERIFY turn
- **THEN** that turn resumes the same Claude session PLAN used, rather
  than starting a new session

#### Scenario: Codex's fix turn resumes its implement session
- **WHEN** the command runs a FIX turn after VERIFY returns `DEFECT`
- **THEN** that turn resumes the same Codex thread IMPLEMENT used, rather
  than starting a new thread

#### Scenario: codex-exec and claude-exec are unaffected
- **WHEN** an operator runs `codex-exec` or `claude-exec` directly (not
  through `quant-research-exec`)
- **THEN** each starts a fresh session exactly as before, never passing a
  resume id

### Requirement: Per-provider model/effort flags, plus an escalated-model override
`quant-research-exec` SHALL accept `--codex-model`, `--codex-effort`,
`--codex-escalated-model`, `--claude-model`, `--claude-effort`, and
`--claude-escalated-model`, each independent and each optional. The
`--codex-*`/`--claude-*` (non-escalated) values SHALL apply to PLAN/VERIFY
and to attempts 1-2 of the fix loop; the escalated-model values SHALL
apply to the fix loop from attempt 3 onward per the fix-bound requirement.
The command SHALL NOT accept a single generic `--model`/`--effort` flag,
since two unrelated provider model namespaces are involved in one
invocation.

#### Scenario: Per-provider flags are independent
- **WHEN** an operator supplies `--codex-model` but not `--claude-model`
- **THEN** Codex turns use the given model and Claude turns use
  `ClaudeProvider`'s own default

### Requirement: --round resolution and derived --change are unchanged
`quant-research-exec` SHALL keep resolving `--round` (auto-detect for a new
round by scanning `research/quant/rounds/round<N>-*.md`) before PLAN runs
(during SYNC when `--cwd` is omitted; directly against the given `--cwd`
otherwise), and deriving `--change quant-research-round-<N>` for JSONL log
scoping, with `--role` removed from `add-quant-research-exec-command`'s
prior surface. Every JSONL log line SHALL additionally carry a `stage`
field identifying which part of the cycle produced it.

#### Scenario: Round-scoped log carries a stage field
- **WHEN** any stage of the cycle emits a log line
- **THEN** that line's JSON object includes a `stage` field naming the
  stage (e.g. `"sync"`, `"plan"`, `"setup_worktree"`, `"implement"`,
  `"verify"`, `"ask"`, `"fix"`, `"finalize"`, `"merge"`)

### Requirement: The command manages its own git worktree unless --cwd is given
When `--cwd` is omitted, `quant-research-exec` SHALL, before PLAN runs,
fast-forward local `<default-branch>` to `origin/<default-branch>` and
resolve the round number against that synced tree (SYNC); PLAN SHALL then
run directly in that synced tree, with no worktree yet. Only after PLAN
produces a brief SHALL the system create a dedicated git worktree and
branch (`.agents/worktrees/quant-research-round-<N>`, reusing SYNC's
already-resolved `<N>`) for the rest of the cycle; every stage from
IMPLEMENT onward SHALL use that worktree as its `cwd`. On a successful
FINALIZE, the system SHALL fast-forward-merge (or
rebase-then-fast-forward-merge if `<default-branch>` advanced during the
cycle) that branch into local `<default-branch>`, then remove the worktree
and delete the branch. On any hard error, the system SHALL leave the
worktree and branch in place rather than removing them. When `--cwd` is
given explicitly, the system SHALL skip all of this (including for PLAN)
and operate directly in the given directory for every stage, exactly as
`add-quant-research-exec-command` specified.

#### Scenario: A bare invocation creates and later removes its own worktree
- **WHEN** an operator runs `quant-research-exec` with no `--cwd`, and the
  cycle reaches FINALIZE successfully
- **THEN** PLAN ran before any worktree existed, a worktree was created
  after PLAN produced a brief, every stage from IMPLEMENT onward operated
  inside it, and after FINALIZE the worktree no longer exists and its
  branch has been merged into local `<default-branch>`

#### Scenario: A failed cycle leaves its worktree for inspection
- **WHEN** the cycle exits with a hard error (e.g. the fix budget is
  exhausted)
- **THEN** the round's worktree and branch still exist on disk afterward

#### Scenario: An explicit --cwd disables worktree management
- **WHEN** an operator runs `quant-research-exec --cwd <dir>`
- **THEN** the command neither creates nor merges nor removes any
  worktree, and operates directly in `<dir>`
