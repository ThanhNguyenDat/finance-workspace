## ADDED Requirements

### Requirement: quant-research-exec runs one quant-research round's Codex stage
The system SHALL provide a `quant-research-exec` command that accepts a
prompt (positional argument or `--prompt-file`) as the stage-specific brief
and a `--role` of `implement` or `fix`, sends an assembled prompt to the
Codex SDK for exactly one bounded turn through the same provider machinery
`codex-exec` uses, and terminates without persisting any cross-invocation
state.

#### Scenario: Implement stage runs
- **WHEN** an operator runs `quant-research-exec --role implement "<plan>"`
- **THEN** the command sends the assembled prompt to the Codex SDK for one
  turn, prints the final result to stdout, and exits with status 0 on
  success

#### Scenario: Fix stage runs
- **WHEN** an operator runs `quant-research-exec --role fix --round <N>
  "<issue>"`
- **THEN** the command sends the assembled prompt to the Codex SDK for one
  turn addressing that issue, prints the final result to stdout, and exits
  with status 0 on success

#### Scenario: Provider turn fails
- **WHEN** the Codex SDK turn errors, times out, or the process cannot start
- **THEN** the command prints the error to stderr and exits with a non-zero
  status, matching `codex-exec`'s existing failure behavior

### Requirement: Round number resolution differs by role
`quant-research-exec` SHALL accept an optional `--round` integer. For
`--role implement`, when `--round` is omitted, the command SHALL determine
the next round number by finding the highest existing
`research/quant/rounds/round<N>-*.md` file under `--cwd` and using `N+1`.
For `--role fix`, `--round` SHALL be required; the command SHALL reject a
`--role fix` invocation that omits `--round` with a non-zero exit before
starting any provider turn.

#### Scenario: Implement without --round auto-detects the next round
- **WHEN** an operator runs `quant-research-exec --role implement "<plan>"`
  without `--round`, and the highest existing round file is `round452-*.md`
- **THEN** the command resolves the round number to `453`

#### Scenario: Implement with an explicit --round uses that value
- **WHEN** an operator runs `quant-research-exec --role implement --round 453
  "<plan>"`
- **THEN** the command uses `453` and does not scan for existing round files

#### Scenario: Fix without --round is rejected
- **WHEN** an operator runs `quant-research-exec --role fix "<issue>"`
  without `--round`
- **THEN** the command exits non-zero with an error before invoking the
  Codex SDK

### Requirement: --change is derived from --round, not a separate flag
`quant-research-exec` SHALL NOT accept a `--change` flag. It SHALL derive
the log-scoping change name as `quant-research-round-<N>`, where `<N>` is
the resolved round number, and use that value with the same
`--change`-scoped JSONL logging behavior (log file path, redaction, UTC
timestamps, `adhoc-<date>` fallback semantics do not apply here since a
round number is always resolved) that `codex-exec`/`claude-exec` already
provide.

#### Scenario: Log file is scoped by the resolved round number
- **WHEN** `quant-research-exec` resolves round number `453` (whether from
  `--round` or auto-detection)
- **THEN** the command's JSONL log is written under
  `tools/orchestrator/logs/quant-research-round-453/quant-research-exec.log`

### Requirement: Prompt is assembled from the round's domain-rules skill
`quant-research-exec` SHALL read
`.agents/skills/quant-research-domain/SKILL.md` relative to `--cwd`, remove
its leading YAML frontmatter block, and use the remaining body as the base
instructions for the Codex turn, followed by the operator-supplied prompt as
that turn's specific brief. The command SHALL NOT duplicate or hard-code
round-domain-rule text of its own. If the file is missing or its frontmatter
block is malformed (no closing delimiter found), the command SHALL exit
non-zero with an error before invoking the Codex SDK.

#### Scenario: Successful prompt assembly
- **WHEN** an operator runs `quant-research-exec --role implement "<plan>"`
  and `.agents/skills/quant-research-domain/SKILL.md` exists with a
  well-formed frontmatter block
- **THEN** the Codex turn receives a prompt consisting of that file's body
  (frontmatter removed) followed by `<plan>`

#### Scenario: Missing instructions file
- **WHEN** `.agents/skills/quant-research-domain/SKILL.md` does not exist
  under `--cwd`
- **THEN** the command exits non-zero with an error and does not invoke the
  Codex SDK

### Requirement: Inherits existing Codex provider guarantees unchanged
`quant-research-exec` SHALL use the same `CodexProvider` account-failover,
secret-redaction, `--model`/`--effort` passthrough, `--timeout-seconds`
bounding, and `--role`/scope advisory-warning behavior already specified for
`codex-exec`, without introducing a separate implementation of any of them.

#### Scenario: Account failover applies
- **WHEN** more than one Codex account is configured and the first fails
  with an account-exhaustion-shaped error during a `quant-research-exec`
  turn
- **THEN** the command retries against the next configured account, exactly
  as `codex-exec` does

#### Scenario: Role/scope advisory warning applies
- **WHEN** `quant-research-exec`'s resolved `--role` falls outside the
  Codex `config.yaml` entry's configured `scope` list
- **THEN** the command prints and logs the same advisory warning
  `codex-exec` would, without blocking the turn or changing the exit code
