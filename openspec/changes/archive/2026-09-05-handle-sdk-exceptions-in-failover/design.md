## Context

See `proposal.md` for the reproduction. Confirmed via a real run: Claude's
SDK emitted an `AssistantMessage` with `.error = "rate_limit"` (which
`ClaudeProvider.stream()` already captures into `self._last_error_code`),
then raised `ResultError` (subclass of `ClaudeSDKError`) instead of
yielding a final `ResultMessage`. `ResultError` carries `.api_error_status`
(HTTP status, `429` in the observed case), `.subtype`, `.terminal_reason`,
`.errors`, and `.result`. `BaseProvider._run_one_attempt`
(`providers/base.py`) currently only catches `ProviderTimeoutError` around
stream consumption; any other exception propagates out of `run_turn`
entirely, skipping the account-failover loop and reaching
`run_cli_main`'s generic top-level handler instead.

## Goals / Non-Goals

**Goals:**
- No SDK exception, from either provider, should ever crash the process
  with a raw traceback or bypass `run_cli_main`'s intended failure path —
  it should always become a normal `ProviderResult(success=False, ...)`.
- When a raised exception is genuinely account-exhaustion-shaped (or an
  earlier event in the same turn already showed one), failover proceeds
  exactly as it already does for a gracefully-returned failure.

**Non-Goals:**
- Not building a general-purpose exception taxonomy across arbitrary future
  SDK versions — only the exception types these two SDKs are documented to
  raise for this purpose today (`ResultError` for Claude; Codex's
  `CodexRpcError` family, none of which are account-exhaustion-shaped).
- Not changing the account-exhaustion code sets themselves
  (`ACCOUNT_FAILOVER_ERRORS` on each provider) — only how a code gets into
  `_last_error_code` in the exception case.

## Decisions

**Catch broadly (`except Exception`) at the `_run_one_attempt` boundary,
not narrowly per-SDK-exception-type**: this boundary already wraps
provider-controlled, external-SDK-driven stream consumption; anything that
escapes it today is by definition something the external SDK raised
(`asyncio.CancelledError` is a `BaseException` in 3.8+, not `Exception`, so
task cancellation from the timeout path is unaffected; `KeyboardInterrupt`
is likewise a `BaseException` and still reaches `run_cli_main`'s explicit
handler). Alternative considered: catch only `ClaudeSDKError`/`CodexError`
specifically — rejected because it would leave the exact same crash-instead-
of-clean-failure gap for any exception type outside those hierarchies
(a bug in this project's own event-forwarding code, for instance, should
still surface as a normal non-zero exit with a message, not a raw
traceback, at this specific boundary).

**Preserve a `_last_error_code` already set by a preceding event; only
fall back to classifying the exception itself when nothing was set yet**:
this is the minimal-invasiveness fix for the reproduced case (the
AssistantMessage's `.error` had already fired before the raise) and keeps
today's proven event-based classification as the primary source of truth.
`_run_one_attempt`'s `except Exception` handler does not overwrite
`self._last_error_code` when it is already non-`None`.

**`ClaudeProvider` gains `_classify_exception(exc: Exception) -> str |
None`, called only when `_last_error_code` is still `None` after the
catch**: for a `ResultError`, map `api_error_status` using standard HTTP
semantics: `401`/`403` → `authentication_failed`, `402` → `billing_error`,
`429` → `rate_limit`; any other status (or a non-`ResultError` exception)
→ `None` (no classification, no failover). Alternative considered: string-
match `exc.result`/`exc.errors` text (e.g. `"rate limit"` substring) —
rejected as far more fragile than the SDK's own structured HTTP status
attribute, which is already documented and stable.

**`CodexProvider` gets the same generic `except Exception` safety net but
no `_classify_exception` override** (the base class's default returns
`None` unconditionally): Codex's account-exhaustion signal is already
delivered gracefully via `TurnCompletedNotification.turn.error.codex_error_info`
(handled by the existing `_turn_error_code`), and its own exception types
(`ServerBusyError`, `TransportClosedError`, generic `CodexRpcError`) are
transient/connection-shaped, matching the deliberate exclusion of
`server_overloaded`/similar codes from `ACCOUNT_FAILOVER_ERRORS` already
established in `bootstrap-orchestrator-exec-commands`'s design.

## Risks / Trade-offs

- **[Risk]** The HTTP-status-to-code mapping is a best-effort heuristic
  layered on top of an SDK exception not originally designed as a
  structured account-exhaustion signal. A future SDK version could reuse
  `429` for a non-account-related rate limit (e.g. a per-IP limit). →
  **Mitigation**: this fallback path only activates when no earlier event
  already classified the failure (the common case, per the reproduction,
  already works without it); it is a secondary safety net, not the primary
  mechanism, and mis-classifying toward "try the fallback account" is a
  low-cost mistake (one extra bounded attempt), not a correctness hazard.
- **[Risk]** Broadening `_run_one_attempt`'s catch to `Exception` could mask
  a genuine bug in this project's own `stream()`/`on_event` code as if it
  were an SDK failure. → **Mitigation**: the caught exception's
  `type(exc).__name__: {exc}` is preserved in the returned
  `ProviderResult.error` (matching `run_cli_main`'s existing convention),
  so it remains visible in stdout/stderr and the JSONL log, not swallowed
  silently.
