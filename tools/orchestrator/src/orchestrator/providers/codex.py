"""Codex SDK provider: one bounded turn on an ephemeral thread.

Optionally fails over to another configured Codex account, within the same
invocation, when a turn hits an auth/usage-limit/budget error -- see
`configured_accounts()`. Account failover itself is generic; it lives in
`BaseProvider.run_turn`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

from openai_codex import ApprovalMode, AsyncCodex, CodexConfig, Sandbox

from ..utils.config import resolve_account_list
from .base import BaseProvider, ProviderResult

CodexClientFactory = Callable[..., Any]

ACCOUNTS_ENV_VAR = "ORCHESTRATOR_CODEX_ACCOUNTS"


def configured_accounts() -> list[str | None]:
    """Resolve the ordered CODEX_HOME list to try; see `resolve_account_list`."""

    return resolve_account_list(ACCOUNTS_ENV_VAR, "codex")


def _turn_error_code(turn: Any) -> str | None:
    """Extract CodexErrorInfoValue's string code, duck-typed like the rest of this class.

    `codex_error_info.root` is either a bare enum (simple codes like
    `unauthorized`) or one of several wrapper models for codes that carry
    extra structured data (e.g. `http_connection_failed`); only the former
    has a `.value`, so the latter correctly yields None here (not a failover
    trigger).
    """

    error = getattr(turn, "error", None)
    if error is None:
        return None
    error_info = getattr(error, "codex_error_info", None)
    if error_info is None:
        return None
    value = getattr(error_info, "root", error_info)
    return getattr(value, "value", None)


class CodexProvider(BaseProvider):
    name = "codex"
    ACCOUNT_FAILOVER_ERRORS = frozenset(
        {"unauthorized", "usage_limit_exceeded", "session_budget_exceeded"}
    )

    def __init__(
        self,
        *,
        codex_client_factory: CodexClientFactory = AsyncCodex,
        accounts: list[str | None] | None = None,
        model: str | None = None,
        effort: str | None = None,
    ) -> None:
        super().__init__(
            accounts=accounts if accounts is not None else configured_accounts()
        )
        self._codex_client_factory = codex_client_factory
        self._model = model
        self._effort = effort
        self._codex_cm: Any = None
        self._handle: Any = None
        self._completed_turn: Any = None
        self._final_text: str | None = None

    async def start_turn(
        self, prompt: str, *, cwd: str | None, account: str | None
    ) -> None:
        self._completed_turn = None
        self._final_text = None
        env = {"CODEX_HOME": account} if account else {}
        self._codex_cm = self._codex_client_factory(
            config=CodexConfig(cwd=cwd, env=env)
        )
        codex = await self._codex_cm.__aenter__()
        thread = await codex.thread_start(
            cwd=cwd,
            sandbox=Sandbox.workspace_write,
            approval_mode=ApprovalMode.auto_review,
        )
        self._handle = await thread.turn(
            prompt, cwd=cwd, model=self._model, effort=self._effort
        )

    async def stream(self) -> AsyncIterator[Any]:
        async for event in self._handle.stream():
            payload = event.payload
            item = getattr(payload, "item", None)
            if item is not None:
                # ItemCompletedNotification.item is a ThreadItem RootModel
                # wrapper for most item kinds (same shape as
                # codex_error_info in _turn_error_code below) -- unwrap it
                # to reach the concrete AgentMessageThreadItem's `.text`.
                item = getattr(item, "root", item)
            text = getattr(item, "text", None)
            if text:
                self._final_text = text
            if event.method == "turn/completed":
                turn = getattr(payload, "turn", None)
                self._completed_turn = turn
                self._last_error_code = _turn_error_code(turn)
            yield payload

    async def interrupt(self) -> None:
        if self._handle is not None:
            await self._handle.interrupt()

    async def aclose(self) -> None:
        if self._codex_cm is not None:
            await self._codex_cm.__aexit__(None, None, None)

    def collect_result(self) -> ProviderResult:
        if self._completed_turn is None:
            return ProviderResult(
                success=False,
                text=None,
                error="codex turn ended without a completion event",
            )
        status = getattr(self._completed_turn, "status", None)
        status_value = getattr(status, "value", status)
        if status_value != "completed":
            error = getattr(self._completed_turn, "error", None)
            message = getattr(error, "message", None) if error else None
            return ProviderResult(
                success=False,
                text=None,
                error=message or f"codex turn ended with status {status_value}",
            )
        return ProviderResult(success=True, text=self._final_text, error=None)
