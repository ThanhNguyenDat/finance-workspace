## 1. Prompt assembly and round-number resolution

- [x] 1.1 Add a helper that reads
      `.agents/skills/quant-research-domain/SKILL.md` relative to `--cwd`,
      strips the leading `---\n...\n---\n` frontmatter block, and returns
      the remaining body; raise a clear error (caught at the CLI boundary,
      `emit_error` + exit 1) when the file is missing or no closing
      frontmatter delimiter is found. Verify with unit tests covering:
      well-formed frontmatter, missing file, missing closing delimiter.
- [x] 1.2 Add a helper that scans `research/quant/rounds/round<N>-*.md`
      under `--cwd` and returns the highest `N` found (or `0` when the
      directory is empty/missing, so the first round resolves to `1`).
      Verify with unit tests covering: several round files present, empty
      directory, missing directory.

## 2. `quant-research-exec` CLI

- [x] 2.1 Add `src/orchestrator/cli/quant_research_exec.py` with
      `PROG = "quant-research-exec"`, an argument parser accepting the
      positional prompt / `--prompt-file`, `--round` (optional int),
      `--role` (required, `implement` or `fix`), `--cwd`,
      `--timeout-seconds`, `--model`, `--effort` — no `--change` flag.
      Verify `--help` lists exactly these flags and omits `--change`.
- [x] 2.2 Wire round-number resolution per role: `--role implement` uses
      `--round` if given, else the auto-detected next round (task 1.2);
      `--role fix` requires `--round` and exits non-zero before any provider
      call when it is missing. Verify with a test asserting the non-zero
      exit and no Codex call for `--role fix` without `--round`.
- [x] 2.3 Derive `change = f"quant-research-round-{round}"` and pass it into
      the existing `resolve_log_path`/`emit_event`/`emit_result`/
      `emit_error` helpers from `cli/_shared.py`, unchanged. Verify the
      resulting log path matches
      `logs/quant-research-round-<N>/quant-research-exec.log` in a test
      using a monkeypatched `LOGS_ROOT` (same pattern as
      `test_shared_log_path.py`).
- [x] 2.4 Assemble the final prompt (task 1.1's body + `\n\n## This round's
      brief\n\n` + the operator prompt) and run it through `CodexProvider`
      exactly as `codex_exec.run_turn` does (reuse that function's
      structure/imports; do not fork `CodexProvider` itself). Verify with a
      fake Codex client asserting the assembled prompt text reaches the
      turn.
- [x] 2.5 Register the `quant-research-exec = "orchestrator.cli.
      quant_research_exec:cli"` entry point in `pyproject.toml`
      `[project.scripts]`. Verify `uv run --project tools/orchestrator
      quant-research-exec --help` succeeds after `uv sync`.

## 3. Documentation

- [x] 3.1 Add a `### quant-research-exec` section to
      `tools/orchestrator/README.md` documenting: what it wraps, the
      `--round`/`--role` semantics from task 2.2, the derived `--change`
      naming, and the fix-loop bound guidance (call `--role fix` at most
      once per round; if Claude's re-check still finds a problem, close the
      round as `NEEDS-MORE-RESEARCH`/`DATA-ISSUE` instead of fixing again).
      Verify by reading the rendered section for accuracy against the
      implemented CLI flags.
- [x] 3.2 Update `.claude/commands/quant/research.md`'s Bước 3 and Bước 7
      example commands from `codex-exec --role implement/fix --change
      quant-research-round-<N>` to `quant-research-exec --role
      implement/fix --round <N>` now that the command exists. Verify by
      reading the updated file: both example blocks use the new command and
      no longer pass a raw `--change` flag.

## 4. Verification

- [x] 4.1 Run `uv run --project tools/orchestrator pytest`, `ruff check .`,
      `ruff format --check .`, and `ty check .` from `tools/orchestrator/`
      and verify all pass.
- [x] 4.2 Run `uv run --project tools/orchestrator sync-agent-links --check`
      and verify it reports synchronized (this change does not touch
      `.agents/`, so this should already pass — confirms nothing else drifted).
