"""Claude Agent SDK provider: one bounded, stateless turn via `query()`.

Optionally fails over to another configured Claude account, within the same
invocation, when a turn hits an authentication/billing/rate-limit error --
see `configured_accounts()`. Account failover itself is generic; it lives in
`BaseProvider.run_turn`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any, cast

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultError,
    ResultMessage,
)
from claude_agent_sdk import query as default_query

from ..utils.config import resolve_account_list
from .base import BaseProvider, ProviderResult

QueryFn = Callable[..., AsyncIterator[Any]]

ACCOUNTS_ENV_VAR = "ORCHESTRATOR_CLAUDE_ACCOUNTS"

# HTTP status -> AssistantMessage.error-shaped code, for classifying a
# ResultError the SDK raised instead of yielding a graceful result. Any
# other status (or a non-ResultError exception) is left unclassified.
_RESULT_ERROR_STATUS_CODES = {
    401: "authentication_failed",
    403: "authentication_failed",
    402: "billing_error",
    429: "rate_limit",
}


def configured_accounts() -> list[str | None]:
    """Resolve the ordered CLAUDE_CONFIG_DIR list to try; see `resolve_account_list`."""

    return resolve_account_list(ACCOUNTS_ENV_VAR, "claude")


class ClaudeProvider(BaseProvider):
    name = "claude"
    ACCOUNT_FAILOVER_ERRORS = frozenset(
        {"authentication_failed", "billing_error", "rate_limit"}
    )

    def __init__(
        self,
        *,
        query_fn: QueryFn = default_query,
        accounts: list[str | None] | None = None,
        model: str | None = None,
        effort: str | None = None,
    ) -> None:
        super().__init__(
            accounts=accounts if accounts is not None else configured_accounts()
        )
        self._query_fn = query_fn
        self._model = model
        self._effort = effort
        self._stream: Any = None
        self._result_message: ResultMessage | None = None

    async def start_turn(
        self,
        prompt: str,
        *,
        cwd: str | None,
        account: str | None,
        resume_id: str | None = None,
    ) -> None:
        self._result_message = None
        self.last_session_id = None
        env = {"CLAUDE_CONFIG_DIR": account} if account else {}
        options = ClaudeAgentOptions(
            cwd=cwd,
            permission_mode="bypassPermissions",
            env=env,
            model=self._model,
            resume=resume_id,
            # The SDK types this as a closed Literal; a CLI-supplied value is
            # an untrusted str until the SDK itself validates it at the RPC
            # boundary, same as an invalid --model name would be.
            effort=cast(Any, self._effort),
        )
        self._stream = self._query_fn(prompt=prompt, options=options)

    async def stream(self) -> AsyncIterator[Any]:
        async for message in self._stream:
            if isinstance(message, AssistantMessage) and message.error:
                self._last_error_code = message.error
            if isinstance(message, ResultMessage):
                self._result_message = message
            yield message

    async def interrupt(self) -> None:
        if self._stream is not None:
            await self._stream.aclose()

    def _classify_exception(self, exc: Exception) -> str | None:
        if isinstance(exc, ResultError) and exc.api_error_status is not None:
            return _RESULT_ERROR_STATUS_CODES.get(exc.api_error_status)
        return None

    def collect_result(self) -> ProviderResult:
        if self._result_message is not None:
            self.last_session_id = self._result_message.session_id
        if self._result_message is None:
            return ProviderResult(
                success=False,
                text=None,
                error="claude turn ended without a result message",
            )
        if self._result_message.is_error:
            message = self._result_message.result or (
                f"claude turn failed: {self._result_message.subtype}"
            )
            return ProviderResult(success=False, text=None, error=message)
        return ProviderResult(
            success=True, text=self._result_message.result, error=None
        )
