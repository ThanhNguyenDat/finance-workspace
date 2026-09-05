## ADDED Requirements

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
