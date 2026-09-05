## Why

`CLAUDE.md` and `.agents/rules/coding-and-verification.md` require running
`uv run --project tools/orchestrator sync-agent-links` at the start and end
of every task (the Task Start Gate), and depend on it to keep `.agents/rules/`
and `.agents/skills/` mirrored into `.claude/rules/`/`.claude/skills/` as
symlinks. That command did not exist for this entire session — it lived in
the old `tools/orchestrator/` deleted in commits `9b8d218`/`73a3a71`, and was
not part of the from-scratch rebuild in `bootstrap-orchestrator-exec-commands`
(whose proposal explicitly scoped out "no other CLI commands"). Running the
restored tool's `--check` mode surfaced two real drifts that had accumulated
while it was missing: `.agents/skills/quant-research-loop` had no
`.claude/skills/` symlink, and `.claude/rules/phase-agent-coordinator.md` had
become a real file (content-identical to the canonical `.agents/` copy)
instead of a symlink.

## What Changes

- Add `sync-agent-links` back to `tools/orchestrator` as a `[project.scripts]`
  entry point (`orchestrator.cli.sync_agent_links:cli`) plus a
  `tools/orchestrator/bin/sync-agent-links.sh` bootstrap wrapper, matching
  the shape `CLAUDE.md`/`.agents/rules/coding-and-verification.md` already
  assume.
- Port the tool's logic essentially unchanged from the deleted version
  (mirror `.agents/skills/*` and `.agents/rules/*` into a target tool's
  `skills/`/`rules/` as relative symlinks; `--check` reports drift without
  changing anything; skip `.openspec-target` and any `openspec*`-prefixed
  entry, which are Codex-native OpenSpec skills per `CLAUDE.md`), except
  `TOOLS` now lists only `.claude` — the original also targeted
  `.kimi-code`/`.opencode`, neither of which exists in this workspace
  anymore (`.kimi-code` was deleted in the same cleanup; `.opencode` never
  existed here), so restoring those targets would recreate directories for
  tooling this workspace does not use.
- Ran the restored tool (not `--check`) to actually fix the two drifts found:
  created the missing `quant-research-loop` symlink, and left
  `phase-agent-coordinator.md` flagged (the tool does not overwrite a real
  file that blocks a shared link — that one is reported, not silently
  resolved, pending operator confirmation given its content is identical but
  its recent appearance is unexplained).

## Capabilities

### New Capabilities

- `orchestrator-sync-agent-links`: a read-only-by-default (`--check`) or
  write (`sync-agent-links`) CLI that mirrors `.agents/skills/` and
  `.agents/rules/` into `.claude/skills/`/`.claude/rules/` as relative
  symlinks, and reports (in both modes) any real file blocking a shared
  link without overwriting it.

### Modified Capabilities

(none — `orchestrator-exec-cli` from `bootstrap-orchestrator-exec-commands`
is a separate capability; this does not change its requirements)

## Impact

- Affected paths: `tools/orchestrator/pyproject.toml` (new script entry),
  `tools/orchestrator/bin/sync-agent-links.sh` (new),
  `tools/orchestrator/src/orchestrator/cli/sync_agent_links.py` (new),
  `tools/orchestrator/tests/test_sync_agent_links.py` (new); `.claude/skills/`
  and `.claude/rules/` (symlinks added/left-flagged by running the tool, not
  by hand-editing).
- No changes to `finance-mw`, `finance-web`, `finance-live-action`,
  `finance-broker`, or `mt5` — this is workspace-local tooling only.
