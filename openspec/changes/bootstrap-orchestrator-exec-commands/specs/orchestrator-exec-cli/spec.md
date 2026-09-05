## Purpose

Provide a minimal, stateless way to run exactly one bounded Codex or Claude
provider turn from the command line, with no persistent coordination, lease,
or approval state.

## ADDED Requirements

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

### Requirement: codex-exec writes a JSONL log file
In addition to printing to stdout/stderr, `codex-exec` SHALL append one
JSON line per streamed event, per result, and per error to a log file at a
fixed path, each line including a UTC timestamp. This is additive,
append-only output for after-the-fact inspection; it is not read back by any
command and does not influence any invocation's behavior.

#### Scenario: A successful run is logged
- **WHEN** `codex-exec` completes a turn
- **THEN** the log file contains one JSON line per streamed event plus one
  final JSON line for the result, each with a timestamp

#### Scenario: A failed run is logged
- **WHEN** a `codex-exec` turn fails
- **THEN** the log file contains a JSON error line with a timestamp,
  matching what was printed to stderr

#### Scenario: The log file does not affect statelessness
- **WHEN** two `codex-exec` invocations run concurrently
- **THEN** both append their own lines to the log file without blocking on,
  reading, or otherwise depending on each other's lines
