## Why

The old `tools/orchestrator/` (SQLite coordinator, lease/fencing, account
rotation, operator-approval-question flow, full phase-agent lifecycle) was
deleted intentionally as cleanup. Nothing now exists to invoke Codex or
Claude for a single bounded turn from the command line: only an untracked
stub at repo-root `orchestrator/pyproject.toml` declares two entry points
(`codex-exec`, `claude-exec`) with no implementation behind them. The quant
research loop and manual operator workflows need a minimal way to run one
provider turn without any of the deleted coordination machinery.

## What Changes

- Relocate the orchestrator Python package from repo-root `orchestrator/` to
  `tools/orchestrator/`, matching the path every existing rule already
  references (`CLAUDE.md`, `.agents/rules/coding-and-verification.md`,
  `.agents/rules/phase-agent-coordinator.md` Task Start Gate).
- Add the `tools/orchestrator/README.md` the relocated `pyproject.toml`
  expects (`readme = "README.md"`).
- Implement `codex-exec` as a one-shot CLI: takes a prompt, invokes the
  `openai-codex` SDK for exactly one bounded turn, streams turn/tool events
  to stdout, prints the final result, exits non-zero on failure or timeout.
- Implement `claude-exec` as a one-shot CLI: takes a prompt, invokes the
  `claude-agent-sdk` for exactly one bounded turn, streams turn/tool events
  to stdout, prints the final result, exits non-zero on failure or timeout.
- Both commands support `--cwd` and `--timeout-seconds` (bounded, sane
  default) and redact secret-shaped values from anything they print, per the
  existing secrets rule in `CLAUDE.md`.
- Both `claude-exec` and `codex-exec` fail over to the next configured
  account, within the same invocation, when a turn fails with an
  account-exhaustion-shaped error and more than one account config directory
  is configured for that provider (the operator currently runs two personal
  Claude accounts and one Codex account — Codex is wired up for a second
  account later even though there is only one today). Each provider's
  account list can come from an env var (`ORCHESTRATOR_CLAUDE_ACCOUNTS` /
  `ORCHESTRATOR_CODEX_ACCOUNTS`, quick override) or from an `accounts` list
  under that provider's key in a gitignored `tools/orchestrator/config.yaml`
  (persistent, per-machine; env var wins if both are set). This stays
  stateless: no file or database records which account ran last, only a list
  read fresh and tried in order for that one invocation.
- Both commands accept `--model` and `--effort`, passed straight through to
  the respective SDK's turn call with no extra validation on this tool's
  side.
- `codex-exec` additionally appends a JSONL line (event/result/error, each
  timestamped) to `tools/orchestrator/logs/codex-exec.log` for every run, on
  top of the existing stdout/stderr output; `claude-exec` is unaffected.
- **Out of scope**: no coordinator, lease store, cross-invocation
  account-rotation registry, or operator-approval-question logic (deleted on
  purpose, not reintroduced) — the in-invocation account failover above is
  narrower than that and does not persist anything between runs; no other CLI
  commands; no changes to `quant/research.md` or other unrelated files beyond
  the stale-path fix tied directly to this relocation.

## Capabilities

### New Capabilities

- `orchestrator-exec-cli`: one-shot `codex-exec` / `claude-exec` commands
  that run a single bounded provider turn (Codex or Claude) from a prompt
  and report the result, with no persistent coordination state.

### Modified Capabilities

(none — no existing `openspec/specs/` capabilities to modify)

## Impact

- Affected paths: repo-root `orchestrator/` (removed/relocated),
  `tools/orchestrator/` (new package: `pyproject.toml`, `README.md`,
  `src/orchestrator/cli/codex_exec.py`, `src/orchestrator/cli/claude_exec.py`,
  plus shared SDK-invocation helper code and tests).
- Dependencies: `openai-codex`, `claude-agent-sdk`, `mcp`, `pyyaml` (already
  declared in the existing stub `pyproject.toml`), `uv` for environment
  management per `.agents/rules/coding-and-verification.md`.
- No changes to `finance-mw`, `finance-web`, `finance-live-action`,
  `finance-broker`, or `mt5` — this is workspace-local tooling only.
