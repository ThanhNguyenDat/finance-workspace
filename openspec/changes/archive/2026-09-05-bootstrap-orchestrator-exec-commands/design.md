## Context

`tools/orchestrator/` does not currently exist — it was deleted in full
(commits `9b8d218`, `73a3a71`) along with its SQLite coordinator, lease
store, account-rotation registry, and operator-approval-question flow. Only
an untracked, source-less stub remains at repo-root `orchestrator/pyproject.toml`
declaring the `codex-exec` / `claude-exec` entry points this change
implements. See `proposal.md` for why these commands are needed now.

## Goals / Non-Goals

**Goals:**
- A working `tools/orchestrator/` package installable via `uv`, at the path
  every existing rule (`CLAUDE.md`, `.agents/rules/coding-and-verification.md`,
  `.agents/rules/phase-agent-coordinator.md`) already assumes.
- `codex-exec` and `claude-exec` as small, independent, stateless CLI
  entry points satisfying `specs/orchestrator-exec-cli/spec.md`.

**Non-Goals:**
- No coordinator, lease/fencing, cross-invocation account-rotation registry
  (persisted "who ran last" state), or operator-approval flow — deleted on
  purpose, not part of this change. (`claude-exec`'s in-invocation account
  failover, added below at the user's request, is deliberately narrower than
  this and does not reintroduce any of it.)
- No re-creation of the old phase-agent lifecycle, quant-run state, or MCP
  transcript server that used to live under `tools/orchestrator/`.
- No changes to how `quant/research.md` or other commands invoke providers
  today (it currently documents manual, launcher-free operation); wiring it
  to these new commands is a future, separate decision.

## Decisions

**Package layout**: `tools/orchestrator/src/orchestrator/cli/<command>.py`
holds each entry point's thin `cli()`/`main()` wrapper (argument parsing and
exit-code mapping only — matches `.agents/rules/phase-agent-coordinator.md`'s
package-boundary convention: "the package root should contain only package
metadata; do not add implementation modules there"). Two more subpackages
hold everything else:
- `orchestrator/providers/` — the SDK-invocation logic (see Provider
  abstraction below).
- `orchestrator/utils/` — small, dependency-free helpers with no SDK
  knowledge (`redaction.py`, `jsonable.py`, `timeout.py`), mirroring the
  `cli/` convention instead of living loose at the package root.
Alternative considered: two fully standalone scripts with no shared modules —
rejected because the timeout/redaction/output-formatting logic would
otherwise duplicate identically in both files.

**Provider abstraction**: `orchestrator.providers.base.BaseProvider` is an
ABC with `start_turn` / `stream` / `interrupt` / `collect_result` as the
per-provider hooks a subclass implements, plus a concrete `run_turn` that
every subclass gets for free — it starts the turn, forwards each raw event
to an `on_event` callback, enforces `--timeout-seconds` by calling
`interrupt()` on expiry, always releases resources via `aclose()`, and
returns a `ProviderResult(success, text, error)`. `CodexProvider`
(`providers/codex.py`) and `ClaudeProvider` (`providers/claude.py`) are the
only two files that import `openai_codex` / `claude_agent_sdk` directly;
`codex_exec.py` and `claude_exec.py` each construct their provider and call
`run_turn`, with no SDK-specific code in the CLI layer. Adding a third
provider later means adding one `providers/<name>.py` subclass and one thin
`cli/<name>_exec.py` — the shared timeout/streaming/error-mapping logic in
`BaseProvider` does not change. Alternative considered: keep each CLI module
calling its SDK directly (as first implemented) — rejected on user request
specifically to keep the two commands extensible to future providers without
duplicating the timeout-and-streaming orchestration a third command would
otherwise have to copy a third time.

**Redaction**: reuse the same regex-based approach the deleted
`core/redaction.py` used (`SECRET_KEY` field-name pattern +
`SECRET_VALUE` bearer/api-key/token/password value pattern), applied to any
string printed to stdout/stderr including streamed SDK turn/tool events.
Alternative considered: no redaction, relying on operators to avoid pasting
secrets into prompts — rejected because streamed tool-call events (e.g. a
`Bash` tool echoing an env var) can surface a secret the operator never
typed directly, and `CLAUDE.md`'s "Secrets and Sensitive Values" section
applies to all tool output, not just direct input.

**Timeout enforcement**: wrap each provider turn with a wall-clock deadline
(`--timeout-seconds`, default 300s) that cancels the SDK call and exits
non-zero on expiry, rather than relying on the SDK's own internal timeouts.
Alternative considered: trust the SDK's default timeout behavior — rejected
because a hung subprocess or network call under the SDK would otherwise
block indefinitely, which `.agents/skills/test-timeouts` and this project's
broader "every bounded execution has a hard timeout" convention rule out for
any long-running process this project owns.

**Statelessness**: no file, database, or lock is written between
invocations. Each command reads only its CLI arguments and the ambient
environment (for provider credentials the SDKs already expect), and writes
only to stdout/stderr plus its own process exit code. This directly
satisfies the "No persistent coordination state" requirement in the spec
and is what makes two concurrent invocations safe without any locking code.

**Account failover (both commands, generalized in `BaseProvider`)**: the
operator runs two personal Claude accounts and one Codex account today (the
Codex side is provisioned for a second account later even though there is
only one now). `orchestrator/utils/config.py::resolve_account_list(env_var,
config_section)` resolves one provider's ordered account list with this
precedence: that provider's env var (`ORCHESTRATOR_CLAUDE_ACCOUNTS` /
`ORCHESTRATOR_CODEX_ACCOUNTS`, comma-separated, quick one-off override)
first, then an `accounts` list under that provider's key in the YAML config
file (`load_config()`, default path `tools/orchestrator/config.yaml`,
overridable via `ORCHESTRATOR_CONFIG_FILE`) for a persistent per-machine
setting, then a single ambient attempt if neither is set — unchanged from
before either source existed. The config file is gitignored (like the old,
deleted `accounts.yaml` before it) because it names local filesystem paths
specific to one operator's machine, not something to check into a shared
repo; its shape is documented in the package README rather than shipped as a
checked-in `.example` file, matching this project's own prior decision to
drop `accounts.yaml.example` in favor of README documentation.

The failover loop itself moved into `BaseProvider.run_turn` (it was first
written once, in `ClaudeProvider`, then duplicated verbatim while adding
Codex support — a real, not speculative, second occurrence, so it was
factored up): `BaseProvider.__init__` takes an `accounts: list[str | None]`
list, `start_turn(prompt, *, cwd, account)` gains an explicit `account`
parameter instead of each subclass stashing a "pending account" instance
attribute before calling `super().run_turn()`, and a subclass sets
`self._last_error_code` inside `stream()` plus a class-level
`ACCOUNT_FAILOVER_ERRORS` frozenset. `run_turn` tries each account in order,
stopping at the first success, and advancing only when the failed attempt's
`_last_error_code` is in `ACCOUNT_FAILOVER_ERRORS` and a further account
remains. `ClaudeProvider.start_turn` sets
`ClaudeAgentOptions(env={"CLAUDE_CONFIG_DIR": account})` and reads
`AssistantMessage.error` (`authentication_failed`/`billing_error`/
`rate_limit`); `CodexProvider.start_turn` sets
`CodexConfig(env={"CODEX_HOME": account})` and reads the completed turn's
`error.codex_error_info` code (`unauthorized`/`usage_limit_exceeded`/
`session_budget_exceeded`) via the same `getattr`-based duck typing the rest
of `CodexProvider` already uses, since `codex_error_info.root` is a bare
enum only for these simple codes and one of several wrapper models (with no
`.value`) for codes needing extra structured data — both SDKs already merge
`options.env`/`config.env` on top of the full inherited environment, so only
the one overridden key needs to be passed per attempt. No file or database
records which account was used last — the list is (re-)resolved from the
environment/config file on every invocation, so this does not reintroduce
the deleted account-rotation registry's cross-invocation state.
Alternative considered (asked of and rejected by the user): round-robin
across invocations, which would need a persisted "last account used" pointer
and a change to the "No persistent coordination state" spec requirement;
the user chose in-invocation failover specifically to avoid that.
Alternative considered: a `--account` flag with no automatic failover —
rejected because it would not help when an account is unexpectedly rate
limited mid-session, which is the actual problem the operator has today.

**Model/effort passthrough**: `--model`/`--effort` on both commands map
directly onto parameters each SDK's turn call already accepts (Codex:
`Thread.turn(model=..., effort=...)`; Claude: `ClaudeAgentOptions(model=...,
effort=...)`), stored on the provider instance and applied in `start_turn`
alongside the account override. No validation is duplicated on this tool's
side — an invalid value surfaces as a normal turn failure from the SDK,
consistent with how an invalid prompt or `--cwd` is already handled. Claude's
`effort` field is a closed `Literal[...]`; since a CLI flag is an untrusted
`str` until the SDK validates it, `providers/claude.py` passes it through
via an explicit `cast(Any, ...)` at that one call site, documented inline,
rather than hand-rolling a mirror of the SDK's own allowed-values list.

**codex-exec JSONL log file**: `_shared.py::emit_event`/`emit_result`/
`emit_error` accept an optional `log_path`; when given, each already-redacted
line that goes to stdout/stderr is also appended to that file via a
`logging.FileHandler` (chosen over hand-rolled `open(...).write(...)` per
review feedback — it centralizes file lifecycle/encoding and is the
idiomatic stdlib tool for "append structured lines to a file"), formatted as
`%(message)s` so the file stays pure JSONL. A small path-keyed cache
(`_file_loggers`) avoids attaching a duplicate handler on every one of the
many `emit_event` calls within a single turn, which would otherwise multiply
every line written. `codex_exec.py` defines `DEFAULT_LOG_PATH =
tools/orchestrator/logs/codex-exec.log` and resolves `log_path=None` to that
constant *inside* `run_turn`/`main`'s body (not as the parameter's own bound
default), specifically so tests can `monkeypatch.setattr(codex_exec,
"DEFAULT_LOG_PATH", ...)` and have it take effect — a bound default would
have captured the original path once at import time and ignored the patch.
This is `codex-exec`-only per the request; `claude-exec` does not call
`emit_*` with a `log_path`, so its behavior is unchanged. The log file is an
append-only, write-only side channel: no command reads it back, so it does
not reintroduce cross-invocation coordination state despite persisting
across runs (unlike the deleted coordinator database, which was read back to
make decisions).

## Risks / Trade-offs

- **[Risk]** No shared coordination means two invocations could redundantly
  consume the same account's rate limit at the same time. → **Mitigation**:
  out of scope for this change (account rotation was deleted on purpose);
  operators are responsible for not over-invoking the same account
  concurrently until any future account-management tooling is proposed.
- **[Risk]** Regex-based redaction can miss a secret shape it doesn't
  recognize. → **Mitigation**: reuse the exact patterns already reviewed and
  used in the deleted `core/redaction.py`, rather than inventing new ones;
  extending the pattern set is a fast follow-up if a gap is found, not a
  blocker for this change.
- **[Risk]** Failing over on a broad error-code match could retry a request
  that will predictably fail on every account (e.g. a genuinely invalid
  prompt misclassified as `invalid_request` would correctly NOT fail over,
  but a bug in error-code detection could waste a second account's quota on
  a doomed retry). → **Mitigation**: match only the SDK-native codes that
  specifically indicate account/billing exhaustion for each provider
  (Claude: `authentication_failed`, `billing_error`, `rate_limit`; Codex:
  `unauthorized`, `usage_limit_exceeded`, `session_budget_exceeded`), not
  the broader transient/unrelated codes each SDK also defines (e.g. Codex's
  `server_overloaded`, `bad_request`).
- **[Risk]** Relocating `orchestrator/` to `tools/orchestrator/` could
  collide with an in-progress edit to the untracked stub. → **Mitigation**:
  the stub is untracked and contains only `pyproject.toml` with no source;
  the move is a straightforward `git mv`-equivalent relocation with no
  history to preserve.

## Migration Plan

1. Move `orchestrator/pyproject.toml` to `tools/orchestrator/pyproject.toml`
   (or recreate it there with identical contents) and add the missing
   `tools/orchestrator/README.md`.
2. Add `tools/orchestrator/src/orchestrator/__init__.py`,
   `cli/__init__.py`, `cli/codex_exec.py`, `cli/claude_exec.py`,
   `providers/{__init__,base,codex,claude}.py`, and
   `utils/{__init__,redaction,jsonable,timeout}.py`.
3. Remove the now-empty repo-root `orchestrator/` directory.
4. `uv sync --project tools/orchestrator` and run the new tests locally.
5. No production deployment is involved — this is local workspace tooling
   only; no rollback beyond reverting the commit is needed.
