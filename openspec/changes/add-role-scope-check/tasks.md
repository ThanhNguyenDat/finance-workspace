## 1. Config and shared plumbing

- [x] 1.1 Add `utils/config.py::configured_scope(config_section: str) -> list[str]` reading `<config_section>.scope` from `load_config()` (empty list when absent/not a list); unit tests cover present, absent, and non-list-value cases
- [x] 1.2 Add `--role` to `cli/_shared.py::build_arg_parser` with `choices=["plan", "implement", "verify", "fix", "final_verify"]`, default `None`
- [x] 1.3 Add `cli/_shared.py::emit_warning(message, *, log_path=None)` (prints to stderr; writes `{"type": "warning", ...}` to the JSONL log when `log_path` is given, mirroring `emit_error`'s shape)
- [x] 1.4 Add `cli/_shared.py::check_role_scope(role: str | None, scope: list[str]) -> str | None` returning a warning message (or `None` if no mismatch/no role/no scope) — pure function, no I/O, so it's trivially unit-testable

## 2. Wire into codex-exec and claude-exec

- [x] 2.1 In `codex_exec.py::run_turn`/`main`: read `configured_scope("codex")`, call `check_role_scope(args.role, scope)`, and `emit_warning(...)` before starting the turn when it returns a message; the turn still runs and the final exit code still comes only from `result.success`
- [x] 2.2 Same wiring in `claude_exec.py::run_turn`/`main` for `configured_scope("claude")`
- [x] 2.3 Unit tests per command: role in scope → no warning printed, turn runs and returns its own exit code; role not in scope → warning printed to stderr, turn still runs and returns its own exit code (including when the turn itself fails, to confirm the exit code is the turn's, not forced by the mismatch); no `--role` → no warning regardless of configured scope; `scope` unset/empty → no warning regardless of `--role`

## 3. Docs and final verification

- [x] 3.1 Add `scope: [...]` under `claude:`/`codex:` in `tools/orchestrator/config.yaml`, matching `CLAUDE.md`'s role boundary (`claude: [plan, verify, final_verify]`, `codex: [implement, fix]`)
- [x] 3.2 Update `tools/orchestrator/README.md`: document `--role`, the `scope` config key, and state plainly that a mismatch only warns and never blocks or changes the exit code
- [x] 3.3 Run `uv run --project tools/orchestrator pytest`, `ruff check .`, `ruff format --check .`, and `ty check .`; all pass (88 tests)
- [x] 3.4 Manually run one in-scope and one out-of-scope `--role` call for each command against the real SDKs; confirmed: `codex-exec --role implement` (in scope) silent, `codex-exec --role plan` (out of scope) printed `warning: plan is outside the configured scope (implement, fix)`, `claude-exec --role implement` (out of scope) printed the matching warning, all before the turn started and independent of the turn's own outcome. **This run also surfaced a separate, more serious bug** (out of this change's scope, tracked separately): when the real Claude SDK raises an exception (`ResultError`) on quota exhaustion instead of returning a graceful failed result, `BaseProvider.run_turn`'s account-failover loop never sees it and does not try the next configured account — confirmed via the log showing only one account attempted despite two being configured. Reported to the user, who asked for a dedicated OpenSpec change to design the fix rather than a quick patch here.
