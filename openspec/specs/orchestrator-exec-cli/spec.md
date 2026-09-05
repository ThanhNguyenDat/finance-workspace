# orchestrator-exec-cli Specification

## Purpose
Provide a minimal, stateless way to run exactly one bounded Codex or Claude
provider turn from the command line, with no persistent coordination, lease,
or approval state.

## Requirements

### Requirement: codex-exec runs one bounded Codex turn
The system SHALL provide a `codex-exec` command that accepts a prompt
(positional argument or `--prompt-file`), sends it to the Codex SDK for
exactly one turn, and terminates without persisting any cross-invocation
state.

#### Scenario: Successful one-shot run
- **WHEN** an operator runs `codex-exec "<prompt>"`
- **THEN** the command sends the prompt to the Codex SDK for one turn, prints
  the final result to stdout, and exits with status 0

#### Scenario: Prompt supplied from a file
- **WHEN** an operator runs `codex-exec --prompt-file <path>`
- **THEN** the command reads the prompt from the file and behaves identically
  to a positional prompt argument

#### Scenario: Provider turn fails
- **WHEN** the Codex SDK turn errors or the process cannot start
- **THEN** the command prints the error to stderr and exits with a non-zero
  status

### Requirement: claude-exec runs one bounded Claude turn
The system SHALL provide a `claude-exec` command that accepts a prompt
(positional argument or `--prompt-file`), sends it to the Claude Agent SDK
for exactly one turn, and terminates without persisting any cross-invocation
state.

#### Scenario: Successful one-shot run
- **WHEN** an operator runs `claude-exec "<prompt>"`
- **THEN** the command sends the prompt to the Claude Agent SDK for one turn,
  prints the final result to stdout, and exits with status 0

#### Scenario: Prompt supplied from a file
- **WHEN** an operator runs `claude-exec --prompt-file <path>`
- **THEN** the command reads the prompt from the file and behaves identically
  to a positional prompt argument

#### Scenario: Provider turn fails
- **WHEN** the Claude Agent SDK turn errors or the process cannot start
- **THEN** the command prints the error to stderr and exits with a non-zero
  status

### Requirement: Bounded execution
Both `codex-exec` and `claude-exec` SHALL accept a `--timeout-seconds` option
with a default value, and SHALL terminate the provider turn and exit
non-zero when the timeout elapses before the turn completes.

#### Scenario: Turn exceeds the timeout
- **WHEN** a provider turn does not complete before `--timeout-seconds`
  elapses
- **THEN** the command terminates the turn, prints a timeout error, and exits
  with a non-zero status

#### Scenario: Default timeout applies when not specified
- **WHEN** an operator runs either command without `--timeout-seconds`
- **THEN** the command applies its documented default bound instead of
  running unbounded

### Requirement: No persistent coordination state
Neither command SHALL read from or write to any coordinator database, lease
store, account-rotation registry, or operator-approval-question queue.
Each invocation SHALL be independent of every other invocation.

#### Scenario: Two concurrent invocations do not interact
- **WHEN** an operator runs `codex-exec` and `claude-exec` at the same time
- **THEN** neither invocation blocks on, queues behind, or reads state
  written by the other

### Requirement: Each command fails over to a configured fallback account
Both `codex-exec` and `claude-exec` SHALL support an ordered list of more
than one account config directory for their respective provider (Claude:
`CLAUDE_CONFIG_DIR`; Codex: `CODEX_HOME`). When more than one account is
configured, the command SHALL retry the same prompt against the next listed
account, within the same invocation, when a turn fails with an
account-exhaustion-shaped error for that provider (Claude: authentication,
billing, or rate-limit; Codex: unauthorized, usage-limit, or session-budget),
up to one retry per additional configured account. When only one account is
configured (or none), the command SHALL make exactly one attempt, matching
behavior before account configuration existed.

An account-exhaustion-shaped error SHALL be detected the same way whether
the provider's SDK reports it by returning a graceful failed result (e.g.
Codex's `TurnCompletedNotification`) or by raising an exception mid-turn
(e.g. Claude's SDK can raise `ResultError` instead of yielding a final
result). Either way, the failing attempt SHALL NOT crash the command with
an unhandled exception; it SHALL always produce a normal failed-turn
outcome that the failover logic evaluates the same way.

#### Scenario: First account is exhausted, second account succeeds
- **WHEN** more than one account is configured and the turn on the first
  fails with an account-exhaustion-shaped error for that provider
- **THEN** the command retries the same prompt against the second account in
  the same invocation and reports that account's result

#### Scenario: All configured accounts fail
- **WHEN** every configured account's turn fails with an
  account-exhaustion-shaped error
- **THEN** the command reports the final account's error and exits non-zero
  without retrying further

#### Scenario: A non-account-shaped failure does not trigger failover
- **WHEN** a turn fails for a reason that is not account-exhaustion-shaped
  for that provider (e.g. an invalid request or a timeout)
- **THEN** the command does not retry with another configured account and
  reports that failure directly

#### Scenario: No account rotation configured
- **WHEN** neither provider's env var nor its `accounts` list in the YAML
  config file names more than one account
- **THEN** the command makes exactly one attempt using the ambient
  environment's account, unchanged from prior behavior

#### Scenario: The SDK raises an exception instead of returning a failed result
- **WHEN** a provider's SDK raises an exception mid-turn instead of
  yielding a final result (e.g. Claude's SDK raising `ResultError` on
  quota exhaustion)
- **THEN** the command does not crash with an unhandled exception; the
  attempt is treated as a normal failed turn, and failover proceeds to the
  next configured account when that exception is classified as
  account-exhaustion-shaped (directly, or via an account-exhaustion-shaped
  signal already observed from an earlier event in the same turn)

#### Scenario: An unclassifiable raised exception does not trigger failover
- **WHEN** a provider's SDK raises an exception mid-turn that is not
  classified as account-exhaustion-shaped (for either provider) and no
  earlier event in the same turn was
- **THEN** the command reports that failure directly and does not retry
  with another configured account, matching how a non-account-shaped
  graceful failure is already handled

### Requirement: Account list may come from a YAML config file
The system SHALL support configuring each provider's ordered account list
via an `accounts` list under that provider's key (`claude.accounts` /
`codex.accounts`) in a YAML config file, as an alternative to that
provider's environment variable (`ORCHESTRATOR_CLAUDE_ACCOUNTS` /
`ORCHESTRATOR_CODEX_ACCOUNTS`), resolved from `ORCHESTRATOR_CONFIG_FILE`
when set or a default path otherwise. When both the environment variable and
the config file are present for a provider, the environment variable SHALL
take precedence for that provider.

#### Scenario: Config file supplies the account list
- **WHEN** a provider's env var is unset and the YAML config file has a
  non-empty `accounts` list under that provider's key
- **THEN** that provider's command uses that list for account failover, in
  order

#### Scenario: Environment variable overrides the config file
- **WHEN** both a provider's env var and the config file's `accounts` list
  for that provider are set
- **THEN** that provider's command uses the environment variable's list and
  ignores the config file's list for that invocation

#### Scenario: Missing or unreadable config file is not an error
- **WHEN** no config file exists at the resolved path
- **THEN** each command proceeds as if no config file were configured,
  without raising an error

### Requirement: Secret redaction in output
Both commands SHALL redact credential-shaped values (API keys, tokens,
passwords, connection strings) from anything printed to stdout or stderr,
including streamed provider turn/tool events.

#### Scenario: Provider event contains a secret-shaped value
- **WHEN** a streamed turn or tool event contains a value that matches a
  known credential pattern
- **THEN** the command replaces that value with a redaction placeholder
  before printing it

### Requirement: Model and reasoning effort are configurable per turn
Both `codex-exec` and `claude-exec` SHALL accept `--model` and `--effort`
options and pass the given values through to the respective SDK call for
that turn, without validating them beyond what the SDK itself enforces. When
omitted, the command SHALL use the SDK's own default for that setting.

#### Scenario: Model and effort are passed through
- **WHEN** an operator runs either command with `--model <name>` and/or
  `--effort <level>`
- **THEN** the command passes that value to the SDK for the turn

#### Scenario: Omitted flags use the SDK default
- **WHEN** an operator runs either command without `--model` or `--effort`
- **THEN** the command does not override that setting, leaving the SDK's own
  default in effect

### Requirement: Both commands write a JSONL log file, organized per change
In addition to printing to stdout/stderr, both `codex-exec` and
`claude-exec` SHALL append one JSON line per streamed event, per result,
and per error to a log file, each line including a UTC timestamp. This is
additive, append-only output for after-the-fact inspection; it is not read
back by any command and does not influence any invocation's behavior.

Both commands SHALL accept a `--change <name>` option. `<name>` SHALL be
validated as kebab-case (matching an OpenSpec change name's shape) but
SHALL NOT be checked against any `openspec/changes/<name>/` directory
existing on disk — the flag is a caller-supplied label only. The log file
for a given invocation SHALL live at
`tools/orchestrator/logs/<name>/<command>.log` (e.g.
`tools/orchestrator/logs/<name>/codex-exec.log`). When `--change` is
omitted, `<name>` SHALL default to `adhoc-<YYYY-MM-DD>` using the
Asia/Ho_Chi_Minh (UTC+7) local date; the per-line `timestamp` field
remains UTC regardless of this default's timezone.

#### Scenario: A successful run is logged
- **WHEN** an operator runs either command with `--change <name>` and the
  turn completes
- **THEN** `tools/orchestrator/logs/<name>/<command>.log` contains one JSON
  line per streamed event plus one final JSON line for the result, each
  with a timestamp

#### Scenario: A failed run is logged
- **WHEN** a turn fails
- **THEN** the log file contains a JSON error line with a timestamp,
  matching what was printed to stderr

#### Scenario: No --change given falls back to a date-bucketed adhoc directory
- **WHEN** an operator runs either command without `--change`
- **THEN** the command logs to `tools/orchestrator/logs/adhoc-<YYYY-MM-DD>/<command>.log`,
  where the date is the current Asia/Ho_Chi_Minh calendar day

#### Scenario: An invalid --change value is rejected
- **WHEN** `--change` is given a value that is not kebab-case (matching an
  OpenSpec change name's shape)
- **THEN** the command reports an error and exits non-zero before starting
  the turn, without creating a log directory for that value

#### Scenario: --change is not checked against openspec/changes/
- **WHEN** `--change <name>` is given and no `openspec/changes/<name>/`
  directory exists
- **THEN** the command proceeds normally and logs under that name anyway

#### Scenario: The log file does not affect statelessness
- **WHEN** two invocations (same or different `--change` values) run
  concurrently
- **THEN** each appends only to its own resolved log file without blocking
  on, reading, or otherwise depending on another invocation's log file

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

### Requirement: Optional advisory role/scope mismatch warning
Both `codex-exec` and `claude-exec` SHALL accept an optional `--role`
option with values `plan`, `implement`, `verify`, `fix`, or `final_verify`.
When `--role` is given and the invoked provider's `config.yaml` entry
defines a non-empty `scope` list that does not include the given role, the
command SHALL print one warning line to stderr before starting the turn.
This check SHALL NOT alter the command's exit code, SHALL NOT prevent the
turn from running, and SHALL be skipped entirely when `--role` is omitted
or the provider's `scope` is unset or empty.

#### Scenario: Role matches configured scope
- **WHEN** an operator runs a command with `--role <role>` and that role is
  in the invoked provider's configured `scope` list
- **THEN** no warning is printed and the turn runs normally

#### Scenario: Role does not match configured scope
- **WHEN** an operator runs a command with `--role <role>` and that role is
  NOT in the invoked provider's configured `scope` list
- **THEN** the command prints one warning line to stderr naming the role
  and the provider's configured scope, then runs the turn normally and
  exits based on the turn's own outcome

#### Scenario: A scope mismatch never blocks a fallback
- **WHEN** a scope mismatch is detected (e.g. `claude-exec --role
  implement` while `claude`'s configured scope is `[plan, verify,
  final_verify]`)
- **THEN** the command completes the turn and its exit code reflects only
  whether the turn itself succeeded, never the mismatch

#### Scenario: No --role given skips the check
- **WHEN** an operator runs either command without `--role`
- **THEN** no scope check happens and no warning is printed, regardless of
  the provider's configured `scope`

#### Scenario: No configured scope skips the check
- **WHEN** `--role` is given but the invoked provider's `config.yaml` entry
  has no `scope` key or an empty `scope` list
- **THEN** no warning is printed and the turn runs normally
