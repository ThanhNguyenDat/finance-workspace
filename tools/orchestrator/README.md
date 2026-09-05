# orchestrator

Minimal, stateless CLI tooling for running a single bounded provider turn.

The previous `tools/orchestrator/` (SQLite coordinator, lease/fencing,
account rotation, operator-approval-question flow, full phase-agent
lifecycle) was removed intentionally. This package starts over with exactly
two commands and no persistent coordination state.

## Commands

- `codex-exec "<prompt>"` — sends the prompt to the Codex SDK for exactly
  one bounded turn, streams turn/tool events to stdout, prints the final
  result, and exits non-zero on failure or timeout.
- `claude-exec "<prompt>"` — sends the prompt to the Claude Agent SDK for
  exactly one bounded turn, streams turn/tool events to stdout, prints the
  final result, and exits non-zero on failure or timeout.

Both accept `--prompt-file <path>` instead of a positional prompt, `--cwd
<dir>`, `--timeout-seconds <n>` (default 300), `--model <name>`, and
`--effort <level>` (both passed straight through to the SDK, which validates
them — this tool does not duplicate that validation). Neither command reads
or writes any state shared with another invocation — two concurrent runs
never interact.

`codex-exec` additionally appends a JSONL line (event/result/error, each
with a UTC timestamp) to `tools/orchestrator/logs/codex-exec.log` for every
run, in addition to printing to stdout/stderr — a running history on top of
the same per-invocation output.

### Account failover

Configure more than one account for a provider and its `*-exec` command
retries the same prompt on the next account, in the same invocation, when a
turn fails with an account-exhaustion-shaped error:

- **claude-exec**: `CLAUDE_CONFIG_DIR` values, retried on authentication,
  billing, or rate-limit errors.
- **codex-exec**: `CODEX_HOME` values, retried on unauthorized, usage-limit,
  or session-budget errors.

Two ways to configure either one, checked in this order:

1. **Env var** (quick, one-off) — comma-separated:
   ```bash
   export ORCHESTRATOR_CLAUDE_ACCOUNTS="$HOME/.claude,$HOME/.claude-personal-02"
   export ORCHESTRATOR_CODEX_ACCOUNTS="$HOME/.codex"
   ```
2. **Config file** (persistent, per-machine) — `tools/orchestrator/config.yaml`
   (gitignored — it names local account directories, so it isn't shared):
   ```yaml
   claude:
     accounts:
       - ~/.claude
       - ~/.claude-personal-02

   codex:
     accounts:
       - ~/.codex
   ```
   Always read from `tools/orchestrator/config.yaml` — its location is fixed,
   not configurable.

Neither source is required, and a single-entry list (like `codex.accounts`
above today) simply means there is nothing to fail over to — one attempt,
same as before. With neither source set for a given provider, its command
makes exactly one attempt using whatever the ambient environment already
provides. Whichever source is used, nothing is written to disk to remember
which account ran: both are read fresh on every invocation, never written
back to.

## Setup

```bash
uv sync --project tools/orchestrator
```

## Usage

```bash
uv run --project tools/orchestrator codex-exec "explain this repo's layout"
uv run --project tools/orchestrator claude-exec --prompt-file ./prompt.txt --timeout-seconds 120
```

## sync-agent-links

Mirrors `.agents/skills/` and `.agents/rules/` into `.claude/skills/`/
`.claude/rules/` as relative symlinks, so shared Finance knowledge has one
source of truth. `--check` reports drift without changing anything; it never
overwrites a real file sitting where a link is expected — that's reported as
an error instead.

```bash
uv run --project tools/orchestrator sync-agent-links --check
uv run --project tools/orchestrator sync-agent-links
```

## Tests

```bash
uv run --project tools/orchestrator pytest
uv run --project tools/orchestrator ruff check .
uv run --project tools/orchestrator ty check .
```
