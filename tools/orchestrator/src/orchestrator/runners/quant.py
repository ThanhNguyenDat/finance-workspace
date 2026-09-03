"""SDK-backed terminal launcher for the quant-research command."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from openai_codex import ApprovalMode, CodexConfig, Sandbox

from ..coordinator import (
    CoordinatorDB,
    CoordinatorError,
    acquire_account_scope,
    admit_session,
    append_event,
    complete_session,
    create_quant_session,
    get_session,
    record_attempt,
    release_admission,
    release_resource,
    seed_quant_iteration_floor,
    update_attempt,
    update_checkpoint,
)
from ..core.fingerprint import fingerprint
from ..core.io import CLIError, atomic_write_json
from ..core.redaction import redact_text
from ..providers.availability import probe
from ..providers.results import classify_sdk_result
from ..providers.sdk import (
    append_jsonl,
    child_environment,
    executable,
    jsonable,
    start_codex,
)
from ..state import candidates, quant_research
from ..subprocess_supervision import (
    hard_kill_claude_client,
    supervise_claude_turn,
    supervise_codex_turn,
)

PREFIX = "run-phase-agent-command"


async def _claude(
    prompt: str,
    model: str,
    effort: str,
    cwd: Path,
    account_dir: Path | None,
    stdout: Path,
    timeout_seconds: int,
    on_message: Callable[[object], None] | None = None,
) -> tuple[int, str, object]:
    env = child_environment()
    if account_dir:
        env["CLAUDE_CONFIG_DIR"] = str(account_dir)
    client = ClaudeSDKClient(
        ClaudeAgentOptions(
            cli_path=executable("claude", PREFIX),
            cwd=cwd,
            env=env,
            model=model,
            effort=effort,
            permission_mode="bypassPermissions",
        )
    )

    def record_message(value: object) -> None:
        append_jsonl(stdout, value)
        if on_message is not None:
            on_message(value)

    try:
        try:
            await asyncio.wait_for(client.connect(), timeout=max(1, timeout_seconds))
        except TimeoutError:
            hard_kill_claude_client(client)
            return 1, "timeout", None
        outcome = await supervise_claude_turn(
            client,
            prompt,
            timeout_seconds=timeout_seconds,
            kill_after_seconds=30,
            on_message=record_message,
        )
        result = outcome.result
        result_class = classify_sdk_result(
            result,
            provider="claude",
            timed_out=outcome.timed_out,
            hard_killed=outcome.hard_killed,
        )
        return (0 if result_class == "success" else 1), result_class, result
    except BaseException as error:
        return 1, classify_sdk_result(provider="claude", error=error), error
    finally:
        try:
            await asyncio.wait_for(client.disconnect(), timeout=2)
        except TimeoutError, asyncio.CancelledError:
            hard_kill_claude_client(client)


def _codex(
    prompt: str,
    model: str,
    effort: str,
    cwd: Path,
    account_dir: Path | None,
    stdout: Path,
    timeout_seconds: int,
) -> tuple[int, str, object]:
    env = child_environment()
    if account_dir:
        env["CODEX_HOME"] = str(account_dir)
    codex = None
    try:
        codex = start_codex(
            CodexConfig(codex_bin=executable("codex", PREFIX), cwd=str(cwd), env=env),
            max(1, timeout_seconds),
        )
        thread = codex.thread_start(
            approval_mode=ApprovalMode.deny_all,
            cwd=str(cwd),
            ephemeral=True,
            model=model,
            sandbox=Sandbox.full_access,
        )
        outcome = supervise_codex_turn(
            thread.turn(
                prompt, effort=effort, model=model, sandbox=Sandbox.full_access
            ),
            timeout_seconds=timeout_seconds,
            kill_after_seconds=30,
        )
        result = outcome.result
        append_jsonl(stdout, result)
        result_class = classify_sdk_result(
            result,
            provider="codex",
            timed_out=outcome.timed_out,
            hard_killed=outcome.hard_killed,
        )
        return (0 if result_class == "success" else 1), result_class, result
    except BaseException as error:
        return 1, classify_sdk_result(provider="codex", error=error), error
    finally:
        if codex is not None:
            codex.close()


def _last_message(result: object) -> str:
    return redact_text(
        str(
            getattr(result, "result", None)
            or getattr(result, "final_response", None)
            or getattr(getattr(result, "error", None), "message", None)
            or ""
        )
    )


def _sdk_event_payload(value: object) -> dict[str, object]:
    """Keep streaming events structured while making scalar SDK values valid payloads."""

    safe_value = jsonable(value)
    if isinstance(safe_value, dict):
        return safe_value
    return {"value": safe_value}


def _worktree_fingerprint(root: Path) -> str | None:
    try:
        return fingerprint(root)
    except OSError, subprocess.CalledProcessError:
        return None


def run(argv: list[str]) -> int:
    if argv != ["quant-research"]:
        raise CLIError(f"{PREFIX}: usage: run-phase-agent-command quant-research")
    timeout_text = os.environ.get("PHASE_AGENT_QUANT_TIMEOUT_SECONDS", "3600")
    if not timeout_text.isdigit() or int(timeout_text) < 1:
        raise CLIError(f"{PREFIX}: invalid timeout")
    root = Path(
        os.environ.get("QUANT_RESEARCH_ROOT", quant_research.root_dir())
    ).resolve()
    prompt_file = root / ".claude/commands/quant-research.md"
    if not prompt_file.is_file() or not prompt_file.stat().st_size:
        raise CLIError(f"{PREFIX}: canonical quant prompt missing")
    coordinator = CoordinatorDB(root=root)
    compatibility_lock, compatibility_state = quant_research.with_state()
    try:
        compatibility_iteration = compatibility_state["iteration"]
    finally:
        compatibility_lock.release()
    seed_quant_iteration_floor(compatibility_iteration, db=coordinator)
    session = create_quant_session(
        {
            "request": "quant-research",
            "prompt_file": str(prompt_file),
            "repository": str(root),
        },
        db=coordinator,
        run_root=root / ".ops/runtime/phase-agents/quant-runs",
    )
    session_id = session["id"]
    append_event(
        session_id,
        phase="PLAN",
        event_type="session.created",
        safe_payload={
            "iteration": session["quant_iteration"],
            "namespace": session["worktree"],
        },
        db=coordinator,
    )
    try:
        admission = admit_session(session_id, db=coordinator, owner_pid=os.getpid())
    except CoordinatorError as exc:
        raise CLIError(f"{PREFIX}: {exc}") from exc
    if not admission["admitted"]:
        append_event(
            session_id,
            phase="PLAN",
            event_type="session.queued",
            safe_payload={"reason": admission["reason"]},
            db=coordinator,
        )
        print(
            f"{PREFIX}: session {session_id} queued: {admission['reason']}",
            file=sys.stderr,
        )
        return 2
    admission_token = admission["fencing_token"]
    append_event(
        session_id,
        phase="PLAN",
        event_type="session.admitted",
        safe_payload={"slot_id": admission["slot_id"]},
        db=coordinator,
    )
    account_provider = account_name = ""
    account_lease = None
    try:
        current_lock, quant_state = quant_research.with_state()
        try:
            override_provider = os.environ.get(
                "PHASE_AGENT_QUANT_RESEARCH_PROVIDER", ""
            )
            override_model = os.environ.get("PHASE_AGENT_QUANT_RESEARCH_MODEL", "")
            override_effort = os.environ.get("PHASE_AGENT_QUANT_RESEARCH_EFFORT", "")
            override_account = os.environ.get("PHASE_AGENT_QUANT_RESEARCH_ACCOUNT", "")
            if any(
                (override_provider, override_model, override_effort, override_account)
            ):
                if not all((override_provider, override_model, override_effort)):
                    raise CLIError(
                        f"{PREFIX}: quant provider/model/effort overrides must be supplied together"
                    )
                candidates.validate_candidate(
                    override_provider,
                    override_model,
                    override_effort,
                    override_account or None,
                )
                options = [
                    {
                        "provider": override_provider,
                        "model": override_model,
                        "effort": override_effort,
                        **(
                            {"account": override_account.lower()}
                            if override_account
                            else {}
                        ),
                    }
                ]
            else:
                agent_lock, agent_state = candidates.with_state()
                try:
                    options = list(
                        agent_state["phases"]["quant_research"]["candidates"]
                    )
                finally:
                    agent_lock.release()
            iteration = int(session["quant_iteration"])
        finally:
            current_lock.release()
        quant_research.begin_iteration()
        base_prompt = f"Quant iteration {iteration} was already recorded mechanically by the terminal launcher. Do not call begin-iteration and do not increment it again. Execute exactly this iteration.\n\n{prompt_file.read_text(encoding='utf-8')}"
        run_dir = Path(session["worktree"])
        run_dir.mkdir(parents=True, exist_ok=True)
        continuation = False
        last_status = 1
        for index, item in enumerate(options, start=1):
            provider, model, effort = item["provider"], item["model"], item["effort"]
            account = item.get("account", "")
            current_lock, current_state = candidates.with_state()
            try:
                if not _quant_candidate_allowed(
                    current_state, item, bool(override_provider)
                ):
                    continue
            finally:
                current_lock.release()
            if not account and not _provider_available(current_state, provider):
                _probe_quant(provider, current_state)
                current_lock, current_state = candidates.with_state()
                try:
                    if not _provider_available(current_state, provider):
                        continue
                finally:
                    current_lock.release()
            attempt_base = run_dir / f"attempt-{index}-{provider}"
            stdout = attempt_base.with_suffix(".stdout.jsonl")
            stderr = attempt_base.with_suffix(".stderr.log")
            last = attempt_base.with_suffix(".last-message.md")
            stdout.write_text("", encoding="utf-8")
            stderr.write_text("", encoding="utf-8")
            fingerprint_before = _worktree_fingerprint(root)
            account_dir = None
            if account:
                normalized, account_dir = candidates.resolve_account_dir(
                    provider, account, PREFIX
                )
                account_provider, account_name = provider, normalized
                try:
                    account_lease = acquire_account_scope(
                        session_id,
                        provider,
                        normalized,
                        db=coordinator,
                        owner_pid=os.getpid(),
                    )
                except CoordinatorError as exc:
                    raise CLIError(f"{PREFIX}: {exc}") from exc
            attempt_id = f"{session_id}-plan-a{index}"
            record_attempt(
                session_id,
                phase="PLAN",
                round=session["round"],
                attempt_no=index,
                attempt_id=attempt_id,
                provider=provider,
                model=model,
                effort=effort,
                account=account or None,
                continuation=continuation,
                status="RUNNING",
                db=coordinator,
            )
            append_event(
                session_id,
                phase="PLAN",
                event_type="provider.attempt.started",
                safe_payload={
                    "provider": provider,
                    "model": model,
                    "effort": effort,
                    "account": account or None,
                    "attempt": index,
                    "continuation": continuation,
                },
                attempt_id=attempt_id,
                db=coordinator,
            )
            try:
                prompt = (
                    base_prompt
                    if not continuation
                    else f"Continue quant iteration {iteration} after provider quota interruption. Preserve existing research artifacts and do not restart, reschedule, or increment the iteration.\n\n{base_prompt}"
                )

                def record_stream(value: object, attempt_id: str = attempt_id) -> None:
                    append_event(
                        session_id,
                        phase="PLAN",
                        event_type="provider.stream",
                        safe_payload=_sdk_event_payload(value),
                        attempt_id=attempt_id,
                        db=coordinator,
                    )

                if provider == "claude":
                    status, result_class, result = asyncio.run(
                        _claude(
                            prompt,
                            model,
                            effort,
                            root,
                            account_dir,
                            stdout,
                            int(timeout_text),
                            on_message=record_stream,
                        )
                    )
                else:
                    status, result_class, result = _codex(
                        prompt,
                        model,
                        effort,
                        root,
                        account_dir,
                        stdout,
                        int(timeout_text),
                    )
                append_event(
                    session_id,
                    phase="PLAN",
                    event_type="provider.result",
                    safe_payload=_sdk_event_payload(result),
                    attempt_id=attempt_id,
                    db=coordinator,
                )
                last.write_text(_last_message(result), encoding="utf-8")
            finally:
                if account_lease:
                    release_resource(
                        "account",
                        f"account:{account_provider}/{account_name}",
                        account_lease["fencing_token"],
                        db=coordinator,
                    )
                    account_lease = None
                    account_provider = account_name = ""
            stderr.write_text("", encoding="utf-8") if not stderr.exists() else None
            stdout.with_suffix(".result-class").write_text(
                f"{result_class}\n", encoding="utf-8"
            )
            stdout.with_suffix(".exit").write_text(f"{status}\n", encoding="utf-8")
            fingerprint_after = _worktree_fingerprint(root)
            attempt_status = (
                "COMPLETED"
                if status == 0
                else ("INTERRUPTED" if result_class == "timeout" else "FAILED")
            )
            update_attempt(
                session_id,
                attempt_id,
                status=attempt_status,
                result_class=result_class,
                evidence_path=str(stdout.with_suffix(".meta.json")),
                db=coordinator,
            )
            append_event(
                session_id,
                phase="PLAN",
                event_type="provider.attempt.completed",
                safe_payload={
                    "provider": provider,
                    "model": model,
                    "effort": effort,
                    "account": account or None,
                    "attempt": index,
                    "continuation": continuation,
                    "status": status,
                    "result_class": result_class,
                },
                attempt_id=attempt_id,
                db=coordinator,
            )
            current_session = get_session(session_id, db=coordinator)
            if current_session is None:
                raise CLIError(f"{PREFIX}: coordinator session disappeared")
            update_checkpoint(
                session_id,
                {
                    "iteration": iteration,
                    "attempt": index,
                    "provider": provider,
                    "account": account or None,
                    "result_class": result_class,
                    "continuation": continuation,
                    "worktree_fingerprint_before": fingerprint_before,
                    "worktree_fingerprint_after": fingerprint_after,
                },
                expected_version=current_session["version"],
                fencing_token=admission_token,
                db=coordinator,
            )
            atomic_write_json(
                stdout.with_suffix(".meta.json"),
                {
                    "iteration": iteration,
                    "attempt": index,
                    "provider": provider,
                    "model": model,
                    "effort": effort,
                    **({"account": account} if account else {}),
                    "continuation": continuation,
                    "result_class": result_class,
                    "worktree_fingerprint_before": fingerprint_before,
                    "worktree_fingerprint_after": fingerprint_after,
                },
            )
            last_status = status
            if status == 0:
                if account:
                    candidates.mutate(
                        "provider-result",
                        ["provider-result", provider, "success", account],
                    )
                else:
                    candidates.mutate(
                        "provider-result", ["provider-result", provider, "success"]
                    )
                append_event(
                    session_id,
                    phase="PLAN",
                    event_type="session.completed",
                    safe_payload={"iteration": iteration, "provider": provider},
                    db=coordinator,
                )
                current_session = get_session(session_id, db=coordinator)
                if current_session is None:
                    raise CLIError(f"{PREFIX}: coordinator session disappeared")
                complete_session(
                    session_id,
                    expected_version=current_session["version"],
                    fencing_token=admission_token,
                    db=coordinator,
                )
                print(f"Quant iteration {iteration} completed with {provider}")
                return 0
            if result_class in {"global-quota-exhausted", "auth-error"}:
                args = ["provider-result", provider, result_class] + (
                    [account] if account else []
                )
                candidates.mutate("provider-result", args)
                continuation = True
            elif result_class in {
                "model-unavailable",
                "model-specific-limit",
                "transient-rate-limit",
            }:
                continuation = True
            else:
                return status
        raise CLIError(
            f"{PREFIX}: no eligible candidate completed quant iteration {iteration} (last status {last_status})"
        )
    finally:
        if account_lease:
            release_resource(
                "account",
                f"account:{account_provider}/{account_name}",
                account_lease["fencing_token"],
                db=coordinator,
            )
        release_admission(session_id, admission_token, db=coordinator)


def _quant_candidate_allowed(state: dict, item: dict, override: bool) -> bool:
    phase = state["phases"]["quant_research"]
    if (
        not override
        and phase["mode"] == "manual"
        and phase.get("pinned_provider") != item["provider"]
    ):
        return False
    return _provider_available(state, item["provider"], item.get("account"))


def _provider_available(state: dict, provider: str, account: str | None = None) -> bool:
    if account:
        return (
            state["providers"][provider]
            .get("accounts", {})
            .get(account, {})
            .get("available", True)
        )
    return state["providers"][provider].get("available", False)


def _probe_quant(provider: str, state: dict) -> None:
    option = next(
        item
        for item in state["phases"]["quant_research"]["candidates"]
        if item["provider"] == provider
    )
    result = probe(
        provider,
        option["model"],
        option["effort"],
        int(os.environ.get("PHASE_AGENT_PROBE_TIMEOUT_SECONDS", "30")),
    )
    if result in {"success", "global-quota-exhausted", "auth-error"}:
        candidates.mutate("provider-result", ["provider-result", provider, result])


def main(argv: list[str] | None = None) -> int:
    return run(list(argv if argv is not None else sys.argv[1:]))
