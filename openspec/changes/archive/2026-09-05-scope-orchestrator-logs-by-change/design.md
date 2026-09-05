## Context

See `proposal.md` for motivation. `_shared.py::emit_event`/`emit_result`/
`emit_error` already accept an optional `log_path: Path`; `codex_exec.py`
resolves a `DEFAULT_LOG_PATH` when none is passed, read fresh inside
`run_turn`/`main` (not bound as the parameter's own default) specifically
so tests can monkeypatch it. `claude_exec.py` has no logging at all today.

## Goals / Non-Goals

**Goals:**
- One shared path-resolution function, used by both CLIs, so `--change`
  and the `adhoc-<date>` fallback behave identically for both.
- Keep the existing `log_path: Path | None` parameter contract in
  `_shared.py` unchanged (it already supports "pass an explicit path" for
  tests) — only change how `codex_exec.py`/`claude_exec.py` compute the
  path they pass in.

**Non-Goals:**
- Not building the web viewer — explicitly deferred.
- Not migrating or deleting the existing flat `tools/orchestrator/logs/codex-exec.log`
  file from before this change; it simply stops being written to.
- Not adding log rotation, retention, or size limits — out of scope, no
  such requirement was raised.

## Decisions

**`--change` validation regex**: reuse the shape OpenSpec's own change
names already use — `^[a-z0-9][a-z0-9-]*$` (lowercase alphanumeric,
hyphen-separated, starting with alphanumeric). This is the same pattern the
old, deleted coordinator used for its own `SAFE_CHANGE` check, so it is a
proven-adequate shape for this exact purpose. Validation happens in
argument parsing (`_shared.py`), before any provider is touched, so an
invalid value fails fast with no log directory created and no turn
attempted.

**Timezone for the `adhoc-<date>` default**: Asia/Ho_Chi_Minh (UTC+7),
per explicit user instruction, computed via Python's standard library
(`zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")`, stdlib since 3.9, no new
dependency) rather than a naive UTC+7 offset constant — correct even
across any future DST-like calendar quirks, though Vietnam has none today,
this is still the more honest primitive to reach for. The per-line
`timestamp` field inside each JSON line is unaffected and stays UTC (it
already uses `datetime.now(timezone.utc)`), so only the directory name's
date computation changes.

**Path resolution as one shared function**: add
`_shared.py::resolve_log_path(command: str, change: str | None) -> Path`
that returns `tools/orchestrator/logs/<change-or-adhoc-date>/<command>.log`.
Both `codex_exec.py` and `claude_exec.py` call it with their own command
name (`"codex-exec"` / `"claude-exec"`) instead of each hardcoding a
`DEFAULT_LOG_PATH` constant. Alternative considered: keep two separate
`DEFAULT_LOG_PATH`-style constants and duplicate the change/adhoc logic in
each CLI module — rejected as the exact kind of duplication this project
already factored out once before (`BaseProvider`) when it appeared twice.

**`claude-exec` logging reuses the existing `_shared.py` primitives
as-is**: `claude_exec.py`'s `run_turn`/`main` gain the same
`log_path`-threading pattern `codex_exec.py` already has (a
`functools.partial(emit_event, log_path=...)` for the `on_event`
callback, plus `log_path=` on `emit_result`/`emit_error`). No changes to
`emit_event`/`emit_result`/`emit_error`/`_file_logger` themselves — they
were already generic, just never invoked with a path from `claude_exec.py`.

## Risks / Trade-offs

- **[Risk]** A large number of distinct `--change` values (or `adhoc-<date>`
  buckets accumulating daily) creates a growing number of log
  directories/files with no cleanup. → **Mitigation**: explicitly
  out-of-scope per Non-Goals; `tools/orchestrator/logs/` is fully
  gitignored so this is local disk usage only, not a repository-size
  concern. A retention policy is a fast follow-up if it becomes a real
  problem, not a blocker here.
- **[Risk]** Existing content in the old flat `tools/orchestrator/logs/codex-exec.log`
  becomes orphaned (not read by anything after this change). →
  **Mitigation**: acceptable per proposal.md — that file predates this
  change's scoping model and its content isn't tied to any tracked change
  anyway (it was written before `--change` existed).
