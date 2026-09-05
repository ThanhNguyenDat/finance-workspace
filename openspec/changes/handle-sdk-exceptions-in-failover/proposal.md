## Why

Account failover (`BaseProvider.run_turn`, from `bootstrap-orchestrator-exec-commands`)
only advances to the next configured account when a provider's `stream()`
finishes and `collect_result()` reports a recognized account-exhaustion
error code. In a real run against a genuinely rate-limited Claude account
(`ORCHESTRATOR_CLAUDE_ACCOUNTS`/`config.yaml` had two accounts configured),
`claude_agent_sdk`'s `query()` raised a `ResultError` exception mid-stream
instead of yielding a graceful final result. That exception propagated
straight out of `BaseProvider._run_one_attempt` (which has no `try/except`
around stream consumption beyond `ProviderTimeoutError`), so `run_turn`'s
account-failover loop never ran a second time — confirmed via the JSONL log
showing exactly one account attempted despite two being configured, and the
process exiting via `run_cli_main`'s generic top-level exception handler
instead of a normal failed-turn result. Account failover's entire purpose
is to survive exactly this kind of quota exhaustion; today it silently
doesn't, for the one provider (Claude) whose SDK can raise instead of
return.

## What Changes

- `BaseProvider._run_one_attempt` gains a broad `except Exception` around
  stream consumption (in addition to the existing `except
  ProviderTimeoutError`), converting an uncaught SDK exception into a
  normal `ProviderResult(success=False, error=...)` instead of letting it
  escape the whole provider/CLI. This alone stops the previously uncaught
  crash (`ResultError: ...` from `run_cli_main`'s catch-all) becoming a
  clean, expected non-zero exit either way; the fallback question is
  whether that failure is also classified as account-exhaustion-shaped.
- `_last_error_code` set from a stream event *before* the exception (e.g.
  an `AssistantMessage.error` seen just before `ResultError` is raised)
  continues to work as today — the failover loop already checks
  `_last_error_code`, this change just stops an exception from preventing
  that check from ever running.
- `ClaudeProvider` additionally classifies a caught `ResultError` itself
  (for the case where no classifying event preceded it) using its own
  `api_error_status`/`subtype` attributes, mapped to the same
  `authentication_failed`/`billing_error`/`rate_limit` codes
  `AssistantMessage.error` already uses, so `_last_error_code` is set even
  when the SDK never emitted a classifying message first.
- `CodexProvider` gets the same generic exception-to-`ProviderResult`
  safety net (no more uncaught crash on `CodexRpcError`/
  `TransportClosedError`/etc.), but **no new exception classification** —
  Codex's account-exhaustion signal already arrives gracefully via
  `TurnCompletedNotification`, and its exception types
  (`ServerBusyError`, `TransportClosedError`, generic `CodexRpcError`) are
  transient/connection-shaped, not account-shaped, so they correctly do
  not trigger failover, matching the existing "generic 429/timeout/network
  failures do not count as quota exhaustion" rule.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `orchestrator-exec-cli`: strengthens the existing "Each command fails
  over to a configured fallback account" and "No persistent coordination
  state" requirements' actual guarantee — an SDK exception no longer
  silently defeats failover or crashes the process ungracefully. No
  externally observable CLI flag or config shape changes; this is a
  correctness fix to an existing requirement's implementation.

## Impact

- Affected paths: `tools/orchestrator/src/orchestrator/providers/base.py`
  (`_run_one_attempt`), `tools/orchestrator/src/orchestrator/providers/claude.py`
  (exception classification), tests for both.
- No changes to `codex_exec.py`/`claude_exec.py`/`_shared.py` CLI surface —
  this is entirely inside the provider layer.
- No changes to `finance-mw`, `finance-web`, `finance-live-action`,
  `finance-broker`, `mt5`, or any runtime code — workspace-local tooling
  only.
