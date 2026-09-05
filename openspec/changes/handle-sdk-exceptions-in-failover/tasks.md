## 1. Generic exception safety net in BaseProvider

- [x] 1.1 Add `BaseProvider._classify_exception(exc: Exception) -> str | None` returning `None` by default (base class has no classification knowledge)
- [x] 1.2 In `_run_one_attempt`, add `except Exception as exc:` after the existing `except ProviderTimeoutError`: if `self._last_error_code` is still `None`, set it to `self._classify_exception(exc)`; return `ProviderResult(success=False, text=None, error=f"{type(exc).__name__}: {exc}")` either way (preserving the exception's type/message, matching `run_cli_main`'s existing convention)
- [x] 1.3 Unit test (generic, via a minimal fake `BaseProvider` subclass like `test_providers.py` already has): `stream()` raising a plain `Exception` after already setting `_last_error_code` to a value in `ACCOUNT_FAILOVER_ERRORS` causes `run_turn` to advance to the next configured account, exactly like a graceful failure would
- [x] 1.4 Unit test: `stream()` raising an exception with no preceding `_last_error_code` and a `_classify_exception` override returning `None` does not trigger failover — the command reports the failure and exits non-zero without retrying
- [x] 1.5 Unit test: `KeyboardInterrupt` raised from `stream()` is NOT caught by the new `except Exception` (it's a `BaseException`) and still propagates to `run_cli_main`'s existing handler

## 2. Claude-specific exception classification

- [x] 2.1 Override `ClaudeProvider._classify_exception` for `ResultError` (imported from `claude_agent_sdk`): map `api_error_status` `401`/`403` → `authentication_failed`, `402` → `billing_error`, `429` → `rate_limit`; any other status, or a non-`ResultError` exception, → `None`
- [x] 2.2 Unit tests: a fake `query_fn` that raises `ResultError(api_error_status=429, ...)` with no preceding classifying event still triggers failover to the second configured account; `api_error_status=500` (or another unmapped value) does not trigger failover; a preceding `AssistantMessage.error` already in `ACCOUNT_FAILOVER_ERRORS` takes precedence and is not overwritten by a different classification from the exception

## 3. Codex: safety net only, no new classification

- [x] 3.1 Unit test: a fake Codex client whose `thread.turn()`/`handle.stream()` raises a generic exception (e.g. simulating `CodexRpcError`/`TransportClosedError`) produces a normal non-zero exit with the exception's message, not a crash, and does not trigger failover when no preceding event classified it (matching `CodexProvider`'s unchanged default `_classify_exception`)

## 4. Final verification

- [x] 4.1 Run `uv run --project tools/orchestrator pytest`, `ruff check .`, `ruff format --check .`, and `ty check .`; all pass (97 tests)
- [x] 4.2 Attempted a real reproduction: re-ran `claude-exec` against the account that had genuinely hit its spend limit earlier this session. By the time of this run its rate-limit window had already partially reset (0.76-0.77 utilization, `status: allowed`), so it succeeded on the first account without needing to fail over — the original failure could not be reliably reproduced on demand (rate limits reset over time, as anticipated). Validated instead via the unit tests in sections 1-3, which reproduce the exact `ResultError`-raising behavior observed in the original incident deterministically.
