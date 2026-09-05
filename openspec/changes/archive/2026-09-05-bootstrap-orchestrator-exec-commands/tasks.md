## 1. Package relocation

- [x] 1.1 Move `orchestrator/pyproject.toml` to `tools/orchestrator/pyproject.toml` (git mv or recreate identically) and delete the now-empty repo-root `orchestrator/` directory; verify `git status` shows no leftover `orchestrator/` path
- [x] 1.2 Add `tools/orchestrator/README.md` describing the package (what `codex-exec`/`claude-exec` do, `uv sync --project tools/orchestrator` setup); verify the file exists and `pyproject.toml`'s `readme = "README.md"` resolves
- [x] 1.3 Add `tools/orchestrator/.python-version` matching `requires-python = ">=3.12"` and run `uv sync --project tools/orchestrator` to verify the environment builds

## 2. Shared utils and provider abstraction

- [x] 2.1 Create `tools/orchestrator/src/orchestrator/__init__.py` and `src/orchestrator/cli/__init__.py`; verify `uv run --project tools/orchestrator python -c "import orchestrator"` succeeds
- [x] 2.2 Implement a shared redaction helper under `orchestrator/utils/redaction.py` (field-name and value regex patterns per design.md) with a unit test covering a secret-shaped key and a secret-shaped bearer/token value each getting replaced with a redaction placeholder
- [x] 2.3 Implement a shared timeout-enforcement helper under `orchestrator/utils/timeout.py` that cancels a provider call after `--timeout-seconds` and raises a distinguishable `ProviderTimeoutError`, with a unit test using a fake slow call that confirms it is cancelled and reported as a timeout
- [x] 2.4 Implement `orchestrator.providers.base.BaseProvider` (start_turn/stream/interrupt/collect_result + shared `run_turn` timeout orchestration) so a future provider is a new `providers/<name>.py` subclass, not a change to the CLI layer; unit test the shared `run_turn` orchestration (event forwarding, timeout -> interrupt -> `ProviderResult`) against a minimal fake subclass, independent of Codex/Claude specifics

## 3. codex-exec command

- [x] 3.1 Implement `orchestrator/providers/codex.py::CodexProvider` (SDK-specific turn/stream/interrupt/result logic) and a thin `cli/codex_exec.py` that parses prompt (positional or `--prompt-file`), `--cwd`, `--timeout-seconds` (default 300), builds a `CodexProvider`, streams turn/tool events through the redaction helper to stdout, prints the final result, and returns exit code 0 on success
- [x] 3.2 Wire `codex-exec` to exit non-zero with a stderr error message on SDK turn failure, and non-zero with a timeout message when `--timeout-seconds` elapses; verified with a fake Codex SDK client in a test for each path (success, failure, missing-completion, timeout)
- [x] 3.3 Verify `codex-exec` reading a prompt from `--prompt-file` behaves identically to the same prompt passed positionally, via a test comparing both invocations against a fake SDK client

## 4. claude-exec command

- [x] 4.1 Implement `orchestrator/providers/claude.py::ClaudeProvider` (wraps `claude_agent_sdk.query()` — the SDK's stateless one-shot primitive, more accurate here than the stateful `ClaudeSDKClient` named in the original plan) and a thin `cli/claude_exec.py` that parses prompt (positional or `--prompt-file`), `--cwd`, `--timeout-seconds` (default 300), streams turn/tool events through the redaction helper to stdout, prints the final result, and returns exit code 0 on success
- [x] 4.2 Wire `claude-exec` to exit non-zero with a stderr error message on SDK turn failure, and non-zero with a timeout message when `--timeout-seconds` elapses; verified with a fake Claude SDK query function in a test for each path (success, failure, missing-result, timeout)
- [x] 4.3 Verify `claude-exec` reading a prompt from `--prompt-file` behaves identically to the same prompt passed positionally, via a test comparing both invocations against a fake SDK client

## 4a. Account failover, generalized in BaseProvider

- [x] 4a.1 Generalize account failover into `BaseProvider`: `__init__` takes an `accounts: list[str | None]` list and tracks `_last_error_code`; `start_turn(prompt, *, cwd, account)` gains an explicit `account` parameter (replacing a per-subclass "pending account" instance attribute); `run_turn` loops over accounts, stopping at first success and advancing only when `_last_error_code` is in the subclass's `ACCOUNT_FAILOVER_ERRORS` and a further account remains; unit tests exercise this generically against a minimal fake subclass (advance-on-match, stop-on-non-match, exhaust-all-accounts), independent of Codex/Claude specifics — this replaced an initial per-subclass `run_turn` override once the same loop was duplicated verbatim while adding Codex support
- [x] 4a.2 `ClaudeProvider`: set `ACCOUNT_FAILOVER_ERRORS = {authentication_failed, billing_error, rate_limit}`, read `ORCHESTRATOR_CLAUDE_ACCOUNTS` via `configured_accounts()`, set `CLAUDE_CONFIG_DIR` via `ClaudeAgentOptions(env=...)` per attempt, and record `AssistantMessage.error` into `_last_error_code`; verified with a fake `query_fn` returning a rate-limit-shaped failure then a success on the second account
- [x] 4a.3 `CodexProvider`: set `ACCOUNT_FAILOVER_ERRORS = {unauthorized, usage_limit_exceeded, session_budget_exceeded}`, read `ORCHESTRATOR_CODEX_ACCOUNTS` via `configured_accounts()`, set `CODEX_HOME` via `CodexConfig(env=...)` per attempt, and extract the completed turn's `error.codex_error_info` code (duck-typed via `getattr`, since `.root` is a bare enum only for simple codes) into `_last_error_code`; verified with a fake Codex client returning a usage-limit-shaped failure then a success on the second account
- [x] 4a.4 Verify a non-account-shaped failure (e.g. Claude `invalid_request` / Codex plain `error_message` with no `codex_error_info`) does not trigger a retry for either provider, via a test asserting the fake backend is called exactly once
- [x] 4a.5 Verify all-accounts-exhausted returns the final account's error and exits non-zero for either provider, via a test with two consecutive account-exhaustion-shaped failures
- [x] 4a.6 Verify no file or database is written by the failover loop for either provider (extends the existing statelessness regression test)

## 4b. YAML config file for the account list

- [x] 4b.1 Implement `orchestrator/utils/config.py::load_config()` reading an optional YAML file (default `tools/orchestrator/config.yaml`, overridable via `ORCHESTRATOR_CONFIG_FILE`), returning `{}` when the file is missing or not a mapping; unit tests cover missing file, valid mapping, and non-mapping YAML
- [x] 4b.2 Implement `orchestrator/utils/config.py::resolve_account_list(env_var, config_section)` (env var > `<section>.accounts` from `load_config()` > `[None]`), shared by both `providers/claude.py::configured_accounts()` (`ORCHESTRATOR_CLAUDE_ACCOUNTS`, `claude`) and `providers/codex.py::configured_accounts()` (`ORCHESTRATOR_CODEX_ACCOUNTS`, `codex`); unit tests per provider cover config-only, env-var-only, both-set precedence, and neither-set (one ambient attempt)
- [x] 4b.3 Expand `~` in both env-var and config-file account entries via `os.path.expanduser`; unit tests confirm `~/.claude` and `~/.codex` resolve against `HOME` for their respective providers
- [x] 4b.4 Gitignore `tools/orchestrator/config.yaml` (machine-specific, not shared), document its shape (both `claude.accounts` and `codex.accounts`) in the README instead of a checked-in `.example` file (matching this project's prior decision to drop `accounts.yaml.example`), and create the real gitignored file with the operator's actual accounts (`~/.claude`, `~/.claude-personal-02` for Claude; `~/.codex` for Codex)
- [x] 4b.5 Add an autouse `tests/conftest.py` fixture isolating `ORCHESTRATOR_CLAUDE_ACCOUNTS`/`ORCHESTRATOR_CODEX_ACCOUNTS`/`config_module.CONFIG_PATH` for every test, so the real `tools/orchestrator/config.yaml` created in 4b.4 cannot silently change other tests' behavior
- [x] 4b.6 Remove the config-file-location env var (`ORCHESTRATOR_CONFIG_FILE`) at the user's request, hardcoding `utils/config.py::CONFIG_PATH` to the one fixed path; update tests to isolate via `monkeypatch.setattr(config_module, "CONFIG_PATH", ...)` instead of an env var, and update the README accordingly

## 4c. --model / --effort passthrough

- [x] 4c.1 Add `--model` and `--effort` to the shared `cli/_shared.py::build_arg_parser` (both commands take identical flag names; no value validation on this tool's side, matching the "trust the SDK" pattern already used for prompt/cwd)
- [x] 4c.2 Thread `model`/`effort` through `CodexProvider.__init__` into `Thread.turn(model=..., effort=...)`; unit test confirms both values reach the fake thread's `turn()` call
- [x] 4c.3 Thread `model`/`effort` through `ClaudeProvider.__init__` into `ClaudeAgentOptions(model=..., effort=...)` (effort passed via an explicit, commented `cast(Any, ...)` since the SDK types it as a closed `Literal`); unit test confirms both values reach the fake `query_fn`'s `options`

## 4d. codex-exec JSONL log file

- [x] 4d.1 Add `log_path: Path | None` to `cli/_shared.py::emit_event`/`emit_result`/`emit_error`, appending a timestamped JSON line via a cached `logging.FileHandler` per path (avoiding a duplicate handler — and duplicate lines — on every event within one turn) when `log_path` is given; unchanged behavior when `log_path` is `None`
- [x] 4d.2 Wire `cli/codex_exec.py` to a fixed `DEFAULT_LOG_PATH` (`tools/orchestrator/logs/codex-exec.log`), resolved fresh inside `run_turn`/`main` (not bound as the parameter's own default) so tests can monkeypatch `codex_exec.DEFAULT_LOG_PATH`; `claude-exec` is left unchanged (no `log_path` wiring) per the request being codex-exec-specific
- [x] 4d.3 Gitignore `tools/orchestrator/logs/`; unit tests confirm a successful run and a failed run each produce the expected JSONL lines (with timestamps) in an explicit `log_path`, and that omitting `log_path` writes to the (test-isolated) `DEFAULT_LOG_PATH`

## 5. Statelessness and concurrency verification

- [x] 5.1 Verify `codex_exec.py`, `claude_exec.py`, and both `providers/*.py` modules contain no coordinator/lease/account-registry/operator-approval references (regex-bounded grep test, avoiding false positives like "release") and add a regression test asserting no file is created outside `--cwd` during a run for either command
- [x] 5.2 Run `codex-exec` and `claude-exec` concurrently (`asyncio.gather`) against fake SDK backends in a test and verify both complete independently with no shared state or blocking between them

## 6. Registration and final checks

- [x] 6.1 Confirm `[project.scripts]` in `tools/orchestrator/pyproject.toml` still points to `orchestrator.cli.codex_exec:cli` and `orchestrator.cli.claude_exec:cli`, then verify `uv run --project tools/orchestrator codex-exec --help` and `uv run --project tools/orchestrator claude-exec --help` both print usage without error
- [x] 6.2 Run `uv run --project tools/orchestrator pytest`, `uv run --project tools/orchestrator ruff check .`, `uv run --project tools/orchestrator ruff format --check .`, and `uv run --project tools/orchestrator ty check .`; all pass (52 tests, 0 lint errors, 0 format diffs, 0 type errors — `ty` caught 3 real bugs across two rounds: `asyncio.run` given a too-broad `Awaitable[int]` type instead of `Coroutine`, and two separate `list[str]`/`list[str | None]` invariance mismatches, all fixed)
- [x] 6.3 Grep the repo for remaining references to the repo-root `orchestrator/` path (outside this change's own history) and confirm there are none left pointing at the old location
