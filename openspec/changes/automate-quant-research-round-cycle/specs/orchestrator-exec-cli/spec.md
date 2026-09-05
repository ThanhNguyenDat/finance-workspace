## ADDED Requirements

### Requirement: quant-research-exec runs one full round cycle per invocation
The system SHALL provide a `quant-research-exec` command that, given a
stage brief (positional argument or `--prompt-file`) and an optional
`--round`, runs an entire round cycle in one invocation: Codex IMPLEMENT,
Claude VERIFY, Codex FIX (only if VERIFY fails), one bounded re-VERIFY, and
Codex FINALIZE (or an honest CLOSE if VERIFY still fails after one fix).
The command SHALL NOT accept a `--role` flag; there is exactly one entry
point.

#### Scenario: A clean round completes without a fix
- **WHEN** an operator runs `quant-research-exec "<plan>"` and Claude's
  VERIFY pass returns `PASS`
- **THEN** the command runs IMPLEMENT then VERIFY then FINALIZE, and exits
  with status 0 without ever running a FIX turn

#### Scenario: A round needs exactly one fix
- **WHEN** VERIFY returns `FAIL <issue>` after IMPLEMENT
- **THEN** the command runs one Codex FIX turn addressing `<issue>`, then
  one more VERIFY pass, and proceeds to FINALIZE if that pass returns
  `PASS`

#### Scenario: A round still fails after its one fix
- **WHEN** the re-VERIFY pass after FIX also returns `FAIL`
- **THEN** the command does not run a second FIX; it runs a CLOSE-HONEST
  Codex turn instructing an honest `NEEDS-MORE-RESEARCH` or `DATA-ISSUE`
  reclassification and commit instead

### Requirement: Verify runs through a different provider than implement
The system SHALL run the VERIFY stage through `ClaudeProvider`, never
through the same `CodexProvider` turn or thread that ran IMPLEMENT or FIX,
so that no stage can grade its own work.

#### Scenario: Verify uses Claude
- **WHEN** the command reaches the VERIFY stage
- **THEN** the turn is sent via `ClaudeProvider`, not `CodexProvider`

### Requirement: Verify verdict is a structured marker, parsed strictly
Claude's VERIFY turn SHALL end its result text with exactly one line
matching `VERIFY_RESULT: PASS`, `VERIFY_RESULT: FAIL <issue>`, or
`VERIFY_RESULT: QUESTION <question>`. The command SHALL treat the absence
of a matching line as a hard error and SHALL NOT infer a verdict from any
other text in the result.

#### Scenario: Unparseable verify result is a hard error
- **WHEN** Claude's VERIFY turn result text contains no line matching
  `VERIFY_RESULT: (PASS|FAIL|QUESTION)`
- **THEN** the command exits non-zero with an error and does not proceed to
  FIX or FINALIZE

### Requirement: A verify question is answered by Codex, bounded to one round-trip
When a VERIFY pass returns `QUESTION <text>`, the system SHALL send that
question to Codex as one turn, then send Claude one continuation turn with
Codex's answer, instructing that no further question is accepted this
pass. The system SHALL treat a second `QUESTION` within the same verify
pass as an error, not as another round-trip.

#### Scenario: A verify question is resolved in one round-trip
- **WHEN** VERIFY returns `QUESTION <text>`
- **THEN** the command sends Codex one turn to answer `<text>`, then sends
  Claude one more turn with that answer, and accepts only `PASS` or `FAIL`
  from that continuation

### Requirement: Each actor's session is resumed across its own stages
`CodexProvider` and `ClaudeProvider` SHALL accept an optional session/
thread id to resume a prior turn's session, and SHALL expose the resulting
session/thread id after a turn completes. `quant-research-exec` SHALL
resume Codex's session across IMPLEMENT→ASK→FIX→CLOSE-HONEST→FINALIZE, and
resume Claude's session across VERIFY→its own question-continuation→the
post-fix re-VERIFY, so a later stage is not re-told context its own prior
turn already has. `codex-exec`/`claude-exec` SHALL be unaffected: neither
passes a resume id, and both continue to start a fresh session per
invocation exactly as before.

#### Scenario: Codex's fix turn resumes its implement session
- **WHEN** the command runs a FIX turn after VERIFY returns `FAIL`
- **THEN** that turn resumes the same Codex thread IMPLEMENT used, rather
  than starting a new thread

#### Scenario: codex-exec is unaffected
- **WHEN** an operator runs `codex-exec` directly (not through
  `quant-research-exec`)
- **THEN** it starts a fresh Codex thread exactly as before, never passing
  a resume id

### Requirement: --round resolution and derived --change are unchanged
`quant-research-exec` SHALL keep resolving `--round` (auto-detect for a new
round by scanning `research/quant/rounds/round<N>-*.md`) and deriving
`--change quant-research-round-<N>` for JSONL log scoping exactly as
specified by `add-quant-research-exec-command`, with `--role` removed from
that prior behavior's surface. Every JSONL log line SHALL additionally
carry a `stage` field identifying which part of the cycle produced it.

#### Scenario: Round-scoped log carries a stage field
- **WHEN** any stage of the cycle emits a log line
- **THEN** that line's JSON object includes a `stage` field naming the
  stage (e.g. `"implement"`, `"verify"`, `"ask"`, `"fix"`, `"close_honest"`,
  `"finalize"`)
