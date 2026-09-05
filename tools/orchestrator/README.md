# orchestrator

Minimal, stateless CLI tooling for running a single bounded provider turn.

The previous `tools/orchestrator/` (SQLite coordinator, lease/fencing,
account rotation, operator-approval-question flow, full phase-agent
lifecycle) was removed intentionally. This package starts over with exactly
three commands and no persistent coordination state.

## Commands

- `codex-exec "<prompt>"` — sends the prompt to the Codex SDK for exactly
  one bounded turn, streams turn/tool events to stdout, prints the final
  result, and exits non-zero on failure or timeout.
- `claude-exec "<prompt>"` — sends the prompt to the Claude Agent SDK for
  exactly one bounded turn, streams turn/tool events to stdout, prints the
  final result, and exits non-zero on failure or timeout.
- `quant-research-exec [PROMPT]` — runs one full PLAN/IMPLEMENT/VERIFY/FIX/FINALIZE
  quant-research round; the optional prompt is PLAN guidance.

The provider commands (`codex-exec` and `claude-exec`) accept `--prompt-file <path>`
instead of a positional prompt, `--cwd <dir>`, `--timeout-seconds <n>` (default 300), `--model <name>`, and `--effort <level>` (both passed straight through to the SDK, which validates
them — this tool does not duplicate that validation). Neither provider command reads
or writes any state shared with another invocation — two concurrent runs
never interact. The `quant-research-exec` command is stateless too.

### quant-research-exec

`quant-research-exec` runs one complete quant-research round in a single
bounded invocation:

```text
PLAN (Claude) -> IMPLEMENT (Codex) -> VERIFY (Claude)
  -> QUESTION answer (Codex, at most one exchange)
  -> FIX (Codex) / re-VERIFY (Claude), at most 5 attempts
  -> FINALIZE (Codex)
```

PLAN reads the domain rules and current XAU-first backlog. An optional
positional prompt or `--prompt-file` supplies PLAN guidance; neither is
required. A bare invocation is valid:

```bash
uv run --project tools/orchestrator quant-research-exec
```

All arguments are optional. `--round` overrides the next-round auto-detection.
`--timeout-seconds` applies independently to each stage and defaults to 3600.
Provider settings are independent:

- `--codex-model`, `--codex-effort`, `--codex-escalated-model`
- `--claude-model`, `--claude-effort`, `--claude-escalated-model`

From FIX attempt 3, the highest SDK effort is used and an escalated model is
used when configured. A fifth failed re-VERIFY exits non-zero without
FINALIZE. VERIFY markers are strict: `PASS` means the evidence and
classification are trustworthy, including an honest negative result; it does
not mean the hypothesis succeeded.

When `--cwd` is omitted, the command synchronizes the default branch, runs
PLAN there, then creates `.agents/worktrees/quant-research-round-<N>` for
IMPLEMENT onward. A successful FINALIZE fast-forward-merges that branch and
removes the worktree. A hard error leaves the worktree and branch in place for
inspection. Supplying `--cwd` skips SYNC, worktree creation, merge, and cleanup
and runs every stage directly in that directory.

Logs remain under
`tools/orchestrator/logs/quant-research-round-<N>/quant-research-exec.log`.
Every JSONL line includes a `stage` such as `sync`, `plan`,
`setup_worktree`, `implement`, `verify`, `ask`, `fix`, `finalize`, or `merge`.

### Logging

All commands append one JSON line per streamed event, per result, and per
error (each with a UTC timestamp) to a log file, in addition to printing to
stdout/stderr — a running history on top of the same per-invocation output.

The log file is organized by `--change <name>`:

```bash
uv run --project tools/orchestrator codex-exec --change my-feature "..."
# -> tools/orchestrator/logs/my-feature/codex-exec.log
uv run --project tools/orchestrator claude-exec --change my-feature "..."
# -> tools/orchestrator/logs/my-feature/claude-exec.log
```

`<name>` is validated as kebab-case (matching an OpenSpec change name's
shape) but is **not** checked against `openspec/changes/<name>/` existing on
disk — it's just a label. Omitting `--change` falls back to
`logs/adhoc-<YYYY-MM-DD>/<command>.log`, using the Asia/Ho_Chi_Minh (UTC+7)
calendar date — the per-line `timestamp` field inside each log entry stays
UTC regardless. `tools/orchestrator/logs/` is gitignored.

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

### Role/scope advisory warning

The provider commands accept `--role {plan,implement,verify,fix,final_verify}`
and, when the invoked provider's `config.yaml` entry has a non-empty `scope`
list, print an advisory warning to stderr (and log a `{"type": "warning",
...}` line) if `--role` isn't in that list:

```yaml
claude:
  scope: [plan, verify, final_verify]
codex:
  scope: [implement, fix]
```

```bash
uv run --project tools/orchestrator claude-exec --role implement "..."
# warning: implement is outside the configured scope (plan, verify, final_verify)
# ...then runs the turn normally anyway
```

**This never blocks anything and never changes the exit code** — the exit
code always reflects only the turn's own success or failure. A mismatch is
often a deliberate, valid fallback (e.g. Codex is out of quota for
`implement`, so Claude covers it per `CLAUDE.md`'s role boundary); this is
a heads-up, not enforcement. Omitting `--role`, or leaving `scope` unset,
skips the check entirely.

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
