"""SDK-backed terminal launcher for the quant-research command."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from openai_codex import ApprovalMode, CodexConfig, Sandbox

from .classify_result import classify_sdk_result
from .detect_provider_availability import probe
from .io import CLIError, atomic_write_json, run_cli
from .locks import account_lock
from .locks.directory_lock import PidDirectoryLock
from .provider_sdk import append_jsonl, child_environment, executable, start_codex
from .state import candidates, quant_research
from .subprocess_supervision import hard_kill_claude_client, supervise_claude_turn, supervise_codex_turn

PREFIX = "run-phase-agent-command"


async def _claude(prompt: str, model: str, effort: str, cwd: Path, account_dir: Path | None, stdout: Path, timeout_seconds: int) -> tuple[int, str, object]:
    env = child_environment()
    if account_dir:
        env["CLAUDE_CONFIG_DIR"] = str(account_dir)
    client = ClaudeSDKClient(ClaudeAgentOptions(cli_path=executable("claude", PREFIX), cwd=cwd, env=env, model=model, effort=effort, permission_mode="bypassPermissions"))
    try:
        try:
            await asyncio.wait_for(client.connect(), timeout=max(1, timeout_seconds))
        except TimeoutError:
            hard_kill_claude_client(client)
            return 1, "timeout", None
        outcome = await supervise_claude_turn(client, prompt, timeout_seconds=timeout_seconds, kill_after_seconds=30, on_message=lambda value: append_jsonl(stdout, value))
        result = outcome.result
        result_class = classify_sdk_result(result, provider="claude", timed_out=outcome.timed_out, hard_killed=outcome.hard_killed)
        return (0 if result_class == "success" else 1), result_class, result
    except BaseException as error:
        return 1, classify_sdk_result(provider="claude", error=error), error
    finally:
        try:
            await asyncio.wait_for(client.disconnect(), timeout=2)
        except (TimeoutError, asyncio.CancelledError):
            hard_kill_claude_client(client)


def _codex(prompt: str, model: str, effort: str, cwd: Path, account_dir: Path | None, stdout: Path, timeout_seconds: int) -> tuple[int, str, object]:
    env = child_environment()
    if account_dir:
        env["CODEX_HOME"] = str(account_dir)
    codex = None
    try:
        codex = start_codex(CodexConfig(codex_bin=executable("codex", PREFIX), cwd=str(cwd), env=env), max(1, timeout_seconds))
        thread = codex.thread_start(approval_mode=ApprovalMode.deny_all, cwd=str(cwd), ephemeral=True, model=model, sandbox=Sandbox.full_access)
        outcome = supervise_codex_turn(thread.turn(prompt, effort=effort, model=model, sandbox=Sandbox.full_access), timeout_seconds=timeout_seconds, kill_after_seconds=30)
        result = outcome.result
        append_jsonl(stdout, result)
        result_class = classify_sdk_result(result, provider="codex", timed_out=outcome.timed_out, hard_killed=outcome.hard_killed)
        return (0 if result_class == "success" else 1), result_class, result
    except BaseException as error:
        return 1, classify_sdk_result(provider="codex", error=error), error
    finally:
        if codex is not None:
            codex.close()


def _last_message(result: object) -> str:
    return str(getattr(result, "result", None) or getattr(result, "final_response", None) or getattr(getattr(result, "error", None), "message", None) or "")


def run(argv: list[str]) -> int:
    if argv != ["quant-research"]:
        raise CLIError(f"{PREFIX}: usage: run-phase-agent-command.sh quant-research")
    timeout_text = os.environ.get("PHASE_AGENT_QUANT_TIMEOUT_SECONDS", "3600")
    if not timeout_text.isdigit() or int(timeout_text) < 1:
        raise CLIError(f"{PREFIX}: invalid timeout")
    lease_dir = Path(os.environ.get("PHASE_AGENT_QUANT_LEASE_DIR", quant_research.root_dir() / ".ops/runtime/phase-agents/.quant-research-lock"))
    lease = PidDirectoryLock(lease_dir, PREFIX)
    lease.acquire()
    account_provider = account_name = ""
    try:
        current_lock, quant_state = quant_research.with_state()
        try:
            override_provider = os.environ.get("PHASE_AGENT_QUANT_RESEARCH_PROVIDER", "")
            override_model = os.environ.get("PHASE_AGENT_QUANT_RESEARCH_MODEL", "")
            override_effort = os.environ.get("PHASE_AGENT_QUANT_RESEARCH_EFFORT", "")
            override_account = os.environ.get("PHASE_AGENT_QUANT_RESEARCH_ACCOUNT", "")
            if any((override_provider, override_model, override_effort, override_account)):
                if not all((override_provider, override_model, override_effort)):
                    raise CLIError(f"{PREFIX}: quant provider/model/effort overrides must be supplied together")
                candidates.validate_candidate(override_provider, override_model, override_effort, override_account or None)
                options = [{"provider": override_provider, "model": override_model, "effort": override_effort, **({"account": override_account.lower()} if override_account else {})}]
            else:
                agent_lock, agent_state = candidates.with_state()
                try:
                    options = list(agent_state["phases"]["quant_research"]["candidates"])
                finally:
                    agent_lock.release()
            iteration = quant_state["iteration"] + 1
        finally:
            current_lock.release()
        quant_research.begin_iteration()
        root = Path(os.environ.get("QUANT_RESEARCH_ROOT", quant_research.root_dir())).resolve()
        prompt_file = root / ".claude/commands/quant-research.md"
        if not prompt_file.is_file() or not prompt_file.stat().st_size:
            raise CLIError(f"{PREFIX}: canonical quant prompt missing")
        base_prompt = f"Quant iteration {iteration} was already recorded mechanically by the terminal launcher. Do not call begin-iteration and do not increment it again. Execute exactly this iteration.\n\n{prompt_file.read_text(encoding='utf-8')}"
        run_dir = root / ".ops/runtime/phase-agents/quant-runs" / f"iteration-{iteration}"
        run_dir.mkdir(parents=True, exist_ok=True)
        continuation = False
        last_status = 1
        for index, item in enumerate(options, start=1):
            provider, model, effort = item["provider"], item["model"], item["effort"]
            account = item.get("account", "")
            current_lock, current_state = candidates.with_state()
            try:
                if not _quant_candidate_allowed(current_state, item, bool(override_provider)):
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
            account_dir = None
            if account:
                normalized, account_dir = candidates.resolve_account_dir(provider, account, PREFIX)
                account_provider, account_name = provider, normalized
                account_lock.lock_account(provider, normalized, str(os.getpid()), "quant-research", str(iteration))
            try:
                prompt = base_prompt if not continuation else f"Continue quant iteration {iteration} after provider quota interruption. Preserve existing research artifacts and do not restart, reschedule, or increment the iteration.\n\n{base_prompt}"
                if provider == "claude":
                    status, result_class, result = asyncio.run(_claude(prompt, model, effort, root, account_dir, stdout, int(timeout_text)))
                else:
                    status, result_class, result = _codex(prompt, model, effort, root, account_dir, stdout, int(timeout_text))
                last.write_text(_last_message(result), encoding="utf-8")
            finally:
                if account_provider:
                    account_lock.unlock_account(account_provider, account_name, str(os.getpid()), "quant-research", str(iteration))
                    account_provider = account_name = ""
            stderr.write_text("", encoding="utf-8") if not stderr.exists() else None
            stdout.with_suffix(".result-class").write_text(f"{result_class}\n", encoding="utf-8")
            stdout.with_suffix(".exit").write_text(f"{status}\n", encoding="utf-8")
            atomic_write_json(stdout.with_suffix(".meta.json"), {"iteration": iteration, "attempt": index, "provider": provider, "model": model, "effort": effort, **({"account": account} if account else {}), "continuation": continuation, "result_class": result_class})
            last_status = status
            if status == 0:
                if account:
                    candidates.mutate("provider-result", ["provider-result", provider, "success", account])
                else:
                    candidates.mutate("provider-result", ["provider-result", provider, "success"])
                print(f"Quant iteration {iteration} completed with {provider}")
                return 0
            if result_class in {"global-quota-exhausted", "auth-error"}:
                args = ["provider-result", provider, result_class] + ([account] if account else [])
                candidates.mutate("provider-result", args)
                continuation = True
            elif result_class in {"model-unavailable", "model-specific-limit", "transient-rate-limit"}:
                continuation = True
            else:
                return status
        raise CLIError(f"{PREFIX}: no eligible candidate completed quant iteration {iteration} (last status {last_status})")
    finally:
        if account_provider:
            account_lock.unlock_account(account_provider, account_name, str(os.getpid()), "quant-research", str(iteration) if "iteration" in locals() else "")
        lease.release()


def _quant_candidate_allowed(state: dict, item: dict, override: bool) -> bool:
    phase = state["phases"]["quant_research"]
    if not override and phase["mode"] == "manual" and phase.get("pinned_provider") != item["provider"]:
        return False
    return _provider_available(state, item["provider"], item.get("account"))


def _provider_available(state: dict, provider: str, account: str | None = None) -> bool:
    if account:
        return state["providers"][provider].get("accounts", {}).get(account, {}).get("available", True)
    return state["providers"][provider].get("available", False)


def _probe_quant(provider: str, state: dict) -> None:
    option = next(item for item in state["phases"]["quant_research"]["candidates"] if item["provider"] == provider)
    result = probe(provider, option["model"], option["effort"], int(os.environ.get("PHASE_AGENT_PROBE_TIMEOUT_SECONDS", "30")))
    if result in {"success", "global-quota-exhausted", "auth-error"}:
        candidates.mutate("provider-result", ["provider-result", provider, result])


def main(argv: list[str] | None = None) -> int:
    return run(list(argv if argv is not None else sys.argv[1:]))


if __name__ == "__main__":
    run_cli(lambda: main(), PREFIX)
