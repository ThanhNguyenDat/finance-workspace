## 1. Shared path resolution and --change flag

- [x] 1.1 Add `--change <name>` to `cli/_shared.py::build_arg_parser` (shared by both commands); validate kebab-case (`^[a-z0-9][a-z0-9-]*$`) at parse time via `parser.error(...)` on mismatch, with no existence check against `openspec/changes/`
- [x] 1.2 Implement `cli/_shared.py::resolve_log_path(command: str, change: str | None) -> Path` returning `tools/orchestrator/logs/<change or adhoc-<date>>/<command>.log`; the `adhoc-<date>` fallback uses `zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")` for the current local calendar date (stdlib, no new dependency)
- [x] 1.3 Unit tests for `resolve_log_path`: explicit change name produces the expected nested path; omitted change falls back to `adhoc-<date>`; date fallback uses Asia/Ho_Chi_Minh (freeze/inject a fixed instant near a UTC day boundary and confirm the VN-local date is used, not the UTC date)
- [x] 1.4 Unit test: an invalid `--change` value (not kebab-case) causes argument parsing to fail before any provider call, with no log directory created for that value

## 2. codex-exec: switch to the shared resolver

- [x] 2.1 Replace `codex_exec.py`'s standalone `DEFAULT_LOG_PATH` constant and inline `log_path is not None else DEFAULT_LOG_PATH` logic with a call to `resolve_log_path("codex-exec", args.change)` (still resolved fresh inside `run_turn`/`main`, not bound as a parameter default, so tests can override); keep the existing `log_path` override parameter for direct test injection
- [x] 2.2 Update existing `codex_exec` tests that relied on `DEFAULT_LOG_PATH`/monkeypatching it directly to work with the new resolver (adjust `tests/conftest.py`'s autouse isolation fixture accordingly)
- [x] 2.3 New test: running with `--change some-change` writes to `tools/orchestrator/logs/some-change/codex-exec.log`

## 3. claude-exec: add logging

- [x] 3.1 Add `--change`-driven `log_path` threading to `claude_exec.py::run_turn`/`main`, mirroring `codex_exec.py`'s pattern exactly (`functools.partial(emit_event, log_path=...)` for `on_event`, `log_path=` on `emit_result`/`emit_error`)
- [x] 3.2 New tests mirroring `codex_exec`'s logging tests: a successful run writes the expected JSONL lines (event(s) + result) with timestamps; a failed run writes an error line matching stderr; omitting `--change` writes under the resolved `adhoc-<date>` directory
- [x] 3.3 Verify no existing `claude_exec` test regresses (none of them previously exercised `log_path`, so none should need behavior changes, only possibly the isolation fixture)

## 4. Docs and final verification

- [x] 4.1 Update `tools/orchestrator/README.md`: document `--change`, the new `logs/<change>/<command>.log` path shape, and the `adhoc-<YYYY-MM-DD>` (Asia/Ho_Chi_Minh) fallback for both commands (currently only describes `codex-exec`'s flat-file logging)
- [x] 4.2 Grep `tools/orchestrator/src` for any remaining reference to a flat `codex-exec.log` path assumption and confirm none remain outside historical OpenSpec change text
- [x] 4.3 Run `uv run --project tools/orchestrator pytest`, `ruff check .`, `ruff format --check .`, and `ty check .`; all pass (71 tests)
- [x] 4.4 Manually run both `codex-exec --change <name> "..."` and `claude-exec --change <name> "..."` against the real SDKs and confirm the resulting directory/file layout matches `tools/orchestrator/logs/<name>/{codex,claude}-exec.log` — **this real run surfaced and fixed an out-of-scope bug**: `CodexProvider.stream()` read `item.text` directly instead of unwrapping the `ThreadItem` RootModel's `.root` first (same wrapper shape `_turn_error_code` already unwraps for `codex_error_info`), so `--change`'s own test coverage never caught it (fakes don't model the `.root` wrapper) but a real Codex turn's final result was silently always empty. Fixed in `providers/codex.py`; existing fake-based tests were unaffected (fakes have no `.root` attribute, so the added `getattr(item, "root", item)` is a no-op for them).
