## 1. Restore the tool

- [x] 1.1 Port `orchestrator.cli.sync_agent_links` (mirror `.agents/skills/`, `.agents/rules/` into a tool's `skills/`/`rules/` as relative symlinks; `--check` is read-only; skip `.openspec-target` and `openspec*`-prefixed entries; never overwrite a real file at a link's expected path) into `tools/orchestrator/src/orchestrator/cli/sync_agent_links.py`, with `TOOLS = (".claude",)` reflecting that `.kimi-code`/`.opencode` no longer exist in this workspace
- [x] 1.2 Add `tools/orchestrator/bin/sync-agent-links.sh` (uv-dispatch bootstrap wrapper) matching the shape `.agents/rules/coding-and-verification.md` assumes, and register `sync-agent-links = "orchestrator.cli.sync_agent_links:cli"` in `[project.scripts]`; verify `uv run --project tools/orchestrator sync-agent-links --check` runs without a spawn error

## 2. Test coverage

- [x] 2.1 Unit test: missing link is reported (not created) by `--check`, and created by a normal run, for both a skill and a rule
- [x] 2.2 Unit test: `openspec`-prefixed skill entries are never linked
- [x] 2.3 Unit test: a real file at a link's expected path is reported as an error and left untouched, in both modes
- [x] 2.4 Unit test: a stale symlink (target deleted from `.agents/`) is reported by `--check` and removed by a normal run
- [x] 2.5 Unit test: running twice in a row (`main([])` then `main(["--check"])`) ends clean (exit 0), confirming the tool converges

## 3. Apply to this workspace and verify

- [x] 3.1 Run `sync-agent-links --check` against the real `.agents/`/`.claude/` and record what it finds
- [x] 3.2 Run `sync-agent-links` (write mode) to fix what it safely can; confirm via `git status`/`ls -la .claude/skills` that only the expected new symlink appeared
- [x] 3.3 Leave the real-file collision at `.claude/rules/phase-agent-coordinator.md` reported, not fixed (see design.md) — flag it to the operator instead of resolving it silently
- [x] 3.4 Run `uv run --project tools/orchestrator pytest`, `ruff check .`, `ruff format --check .`, and `ty check .`; all pass
