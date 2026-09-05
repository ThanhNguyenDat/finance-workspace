## Why

`codex-exec`'s JSONL log (`tools/orchestrator/logs/codex-exec.log`) is a
single flat, ever-growing file shared by every invocation regardless of
task, and `claude-exec` has no log file at all. A real turn against "hi"
already produced ~19 JSON lines (thread/turn lifecycle, plugin hook events,
one line per streamed text delta); a real coding task will produce far
more. There is no way to tell, from the log alone, which invocation
belonged to which piece of work. The operator wants logs organized per
OpenSpec change (so a change's own work is easy to find and, later, stream
to a simple web viewer), and wants `claude-exec` to log symmetrically with
`codex-exec`.

## What Changes

- Add `--change <name>` to both `codex-exec` and `claude-exec`. `<name>` is
  validated as kebab-case (same shape as an OpenSpec change name) but is
  **not** checked against `openspec/changes/<name>/` existing on disk — the
  flag is just a label the caller supplies, keeping the CLI decoupled from
  the OpenSpec tooling.
- Change the log path structure from a single flat file per provider to one
  directory per `--change` value, holding that provider's log:
  `tools/orchestrator/logs/<change>/codex-exec.log` and
  `tools/orchestrator/logs/<change>/claude-exec.log`. **This replaces the
  current flat `tools/orchestrator/logs/codex-exec.log` path** — any
  existing content there is not migrated automatically.
- When `--change` is omitted, default to `adhoc-<YYYY-MM-DD>` using
  Asia/Ho_Chi_Minh (UTC+7) local date, so untagged invocations still bucket
  by day instead of collecting in one unbounded file forever. The
  per-line `timestamp` field already written to each JSON line stays UTC,
  unchanged — only the directory-naming date uses the operator's local day
  boundary.
- Add logging to `claude-exec` (event/result/error JSONL, same shape
  `codex-exec` already writes), which currently has none.
- Log line format itself is unchanged (plain JSONL, one already-redacted
  event/result/error object per line) — no new "digest" or filtered layer.
  Rendering that nicely (collapsing streamed deltas, hiding plugin/hook
  noise, terminal-style display) is explicitly deferred to a future web
  viewer, not this change.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `orchestrator-exec-cli`: adds `--change` and the per-change log directory
  structure to `codex-exec`; adds `--change` and JSONL logging (previously
  absent) to `claude-exec`.

## Impact

- Affected paths: `tools/orchestrator/src/orchestrator/cli/_shared.py`
  (log-path resolution, `--change` argument),
  `tools/orchestrator/src/orchestrator/cli/codex_exec.py`,
  `tools/orchestrator/src/orchestrator/cli/claude_exec.py`, their tests.
- `tools/orchestrator/.gitignore` entry (`tools/orchestrator/logs/`) already
  covers the new nested layout; no change needed there.
- No changes to `finance-mw`, `finance-web`, `finance-live-action`,
  `finance-broker`, `mt5`, or any runtime code — workspace-local tooling
  only. A future web viewer for these logs is out of scope for this change.
