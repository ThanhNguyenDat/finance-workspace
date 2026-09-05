## Context

See `proposal.md` for why this is needed now. The tool's logic already
existed once, in the deleted `tools/orchestrator/`; this is a restoration
into the freshly rebuilt package from `bootstrap-orchestrator-exec-commands`,
not a new design from scratch.

## Goals / Non-Goals

**Goals:**
- Restore the exact `CLAUDE.md`/`.agents/rules/coding-and-verification.md`
  contract: `uv run --project tools/orchestrator sync-agent-links[--check]`
  works again.
- Never silently overwrite or delete a real (non-symlink) file at a shared
  link's expected path, in either mode.

**Non-Goals:**
- No change to which files live under `.agents/skills/`/`.agents/rules/` —
  this only mirrors what is already there.
- No revival of the deleted coordinator, lease store, or any other part of
  the old `tools/orchestrator/` beyond this one utility.

## Decisions

**`TOOLS` scoped to `.claude` only**: the original tuple was `(".claude",
".kimi-code", ".opencode")`. `.kimi-code` was deleted from this repo in the
same cleanup that deleted the old orchestrator (`git show 9b8d218`), and
`.opencode` has no directory in this repo at all. Restoring links into
directories for tooling this workspace does not use would recreate
already-deleted structure rather than reflect current reality. Alternative
considered: restore the original tuple verbatim for fidelity — rejected
because `sync_entries()` would then unconditionally `mkdir` fresh
`.kimi-code/skills` and `.kimi-code/rules` directories on every run, which is
exactly the kind of drift this tool exists to prevent, just aimed at a tool
no longer in use.

**Leave `phase-agent-coordinator.md`'s real-file collision reported, not
fixed, by this change**: `--check` and a normal run both correctly flagged
`.claude/rules/phase-agent-coordinator.md` as a real file blocking its
shared link (content is byte-identical to `.agents/rules/phase-agent-coordinator.md`,
confirmed with `diff`). The tool's own safety property — never overwrite a
real file — means this needs an explicit `rm` + rerun by the operator, not
something this change does automatically. Its appearance is also
unexplained: unlike the other three `.claude/rules/*` links (all dated one
sync run in the past), this one has today's timestamp with no corresponding
action taken in this session, alongside other unexplained file changes
observed in the same session (an untracked `${env:HOME}/` directory
appearing at the repo root, and two unrelated lines vanishing from
`.gitignore`). Fixing it here without first understanding that pattern risks
masking a symptom of whatever is causing it.

## Risks / Trade-offs

- **[Risk]** A future tool this workspace adopts (e.g. a new agent CLI) will
  not get shared links until `TOOLS` is updated. → **Mitigation**: adding a
  tool to `TOOLS` is a one-line change; `--check` in CI (if ever added) would
  not by itself catch a *missing* entry in `TOOLS`, only drift within tools
  already listed — worth remembering if another tool directory appears here.
- **[Risk]** Restoring this from the deleted version by hand could reproduce
  a bug that existed in the original. → **Mitigation**: the ported logic is
  unchanged aside from `TOOLS`; new tests (`test_sync_agent_links.py`) cover
  missing-link creation, `--check` read-only behavior, stale-link removal,
  the real-file-blocks-a-link safety property, and skipping
  `openspec`-prefixed entries.

## Migration Plan

1. Add `tools/orchestrator/src/orchestrator/cli/sync_agent_links.py` and
   `tools/orchestrator/bin/sync-agent-links.sh`; register the
   `[project.scripts]` entry.
2. `uv sync --project tools/orchestrator` and run the test suite.
3. Run `sync-agent-links --check` to see current drift, then
   `sync-agent-links` to fix what it safely can.
4. No production deployment; no rollback beyond reverting the commit and,
   separately, restoring any symlinks it created back to plain files if ever
   desired (they carry the same content either way).
