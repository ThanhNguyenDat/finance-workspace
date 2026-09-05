## MODIFIED Requirements

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
