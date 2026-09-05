## RENAMED Requirements

- FROM: `### Requirement: codex-exec writes a JSONL log file`
- TO: `### Requirement: Both commands write a JSONL log file, organized per change`

## MODIFIED Requirements

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
