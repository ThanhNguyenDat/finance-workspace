"""Shared phase-agent adapter implementation for Claude and Codex SDKs."""

from __future__ import annotations

import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox

from .accounts.registry import resolve_account_dir
from .classify_result import classify_sdk_result
from .fingerprint import fingerprint
from .io import CLIError
from .locks import account_lock, change_lock
from .provider_sdk import append_jsonl, child_environment, executable, jsonable
from .state import candidates, ops_transaction
from .subprocess_supervision import supervise_claude_turn, supervise_codex_turn

PREFIXES = {"claude": "run-claude-phase", "codex": "run-codex-phase"}
PHASES = {"PLAN", "IMPLEMENT", "VERIFY", "FIX", "FINAL_VERIFY"}
SAFE_CHANGE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9._:-]+$")


def _git_root(path: str | Path, prefix: str) -> Path:
    try:
        root = change_lock.canonical_repo(str(path))
    except CLIError:
        raise
    return Path(root)


def _workspace_root() -> Path:
    return _git_root(os.environ.get("OPS_WORKSPACE_ROOT", ops_transaction.root_dir()), "phase-agent")


def _runtime_root() -> Path:
    return Path(os.environ.get("OPS_ROOT", _workspace_root()))


def _read_state(change: str) -> tuple[dict[str, Any], Path, str, int, Path, Path]:
    state_file = _runtime_root() / ".ops/changes" / change / "runtime/state.json"
    if not state_file.is_file():
        raise CLIError(f"phase-agent: runtime state missing: {state_file}")
    state = ops_transaction.read_state(change)
    session_id = state.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise CLIError("phase-agent: missing session id")
    round_value = state.get("round", 0)
    if not isinstance(round_value, int) or round_value < 0:
        raise CLIError("phase-agent: invalid round")
    workspace = _workspace_root()
    return state, state_file, session_id, round_value, workspace, state_file.parent


def build_prompt(change: str, repository: Path, phase: str, continuation: bool, findings: str = "") -> str:
    prompt = (
        f"Execute OPS phase {phase} for OpenSpec change {change} in {repository}.\n"
        "Read AGENTS.md, applicable rules/skills, the active change, OPS state and repository-local instructions. Preserve locks, scope, tests, safety and secrets. Do not push or launch another model process."
    )
    if phase == "PLAN":
        prompt += "\nPlan/reconcile OpenSpec only; do not implement runtime code."
    elif phase == "IMPLEMENT":
        prompt += "\nImplement the approved scope, add tests and run bounded local checks."
    elif phase in {"VERIFY", "FINAL_VERIFY"}:
        prompt += "\nRead-only verification: do not edit, format, stage or commit. Report severity with exact evidence."
    elif phase == "FIX":
        prompt += f"\nFix only the current-round findings and add regression coverage.\n--- FINDINGS ---\n{findings}"
    if phase == "FINAL_VERIFY":
        prompt += (
            "\nYou are the currently running FINAL_VERIFY attempt. This is the pre-push gate: do not report an unpushed local commit, unavailable GitHub Actions run, or the active change task that explicitly covers push/CI as a P0/P1 finding; these are evaluated only after this gate passes and the commit is pushed. The worktree may contain unrelated dirty files: do not include them in findings, do not run unscoped `git diff --check HEAD`, and do not treat their whitespace or status as a change defect. Check only committed files and the active change scope; use an explicit path list for diff checks. Do not dump full task files, runtime state, logs, or research reports; inspect only targeted fields/sections. The resolver appends this attempt and derives verification evidence only after your process exits, so do not fail solely because your own record is not yet present in runtime state. Evaluate the committed code, findings, and applicable local objective checks. Run only the smallest relevant bounded checks, sequentially; do not launch exploratory scans, duplicate checks, parallel shell calls, or retry loops. Do not issue shell commands containing rm, rm -f, git reset, or git checkout; do not create temporary artifacts that need cleanup. If a check fails, record the exact finding and continue to the final assessment. After the objective checks finish, stop using tools and immediately end the response with exactly these machine-readable lines, using PASS only after all applicable objective checks pass and no P0/P1 remains:\nFINAL_VERIFY_GATE: PASS|FAIL\nP0_FINDINGS: <count>\nP1_FINDINGS: <count>\nOBJECTIVE_GATES: PASS|FAIL"
        )
    if continuation:
        prompt += "\nThis is a continuation after provider interruption. Inspect and preserve the current diff/commits and complete remaining work; do not restart or roll back."
    return prompt


def _validate_common(change: str, repository: str, phase: str, provider: str) -> tuple[dict[str, Any], Path, str, int, Path, Path]:
    if not SAFE_CHANGE.fullmatch(change):
        raise CLIError(f"{PREFIXES[provider]}: invalid change: {change}")
    if phase not in PHASES:
        raise CLIError(f"{PREFIXES[provider]}: unsupported phase: {phase}")
    state, state_file, session_id, round_value, workspace, runtime_dir = _read_state(change)
    if state.get("phase") != phase:
        raise CLIError(f"{PREFIXES[provider]}: runtime phase mismatch")
    if state.get("routing_policy_version") != 1:
        backend = state.get("implementation_backend", "codex")
        valid = (provider == "claude" and (phase in {"PLAN", "VERIFY", "FINAL_VERIFY"} or (phase in {"IMPLEMENT", "FIX"} and backend == "claude-fallback"))) or (provider == "codex" and phase in {"IMPLEMENT", "FIX"} and backend == "codex")
        if not valid:
            raise CLIError(f"{PREFIXES[provider]}: legacy runtime does not select {provider.title()} for this phase")
    repository_root = _git_root(repository, PREFIXES[provider])
    change_lock.assert_repo_lock(change, session_id, repository_root)
    return state, state_file, session_id, round_value, workspace, runtime_dir


def _candidate(provider: str, phase: str, model: str, effort: str, account: str) -> tuple[str, str, str]:
    if not model or not effort:
        current_lock, state = candidates.with_state()
        try:
            phase_state = state["phases"][candidates.normalize_phase(phase)]
            for option in phase_state["candidates"]:
                option_account = option.get("account", "")
                available = state["providers"][option["provider"]].get("available", True)
                if option_account:
                    available = state["providers"][option["provider"]].get("accounts", {}).get(option_account, {}).get("available", True)
                if option["provider"] == provider and available:
                    return option["model"], option["effort"], option_account
            raise CLIError(f"{PREFIXES[provider]}: resolved candidate is not {provider.title()}")
        finally:
            current_lock.release()
    return model, effort, account


def _lock_account(provider: str, account: str, change: str, session_id: str) -> Path | None:
    if not account:
        return None
    normalized, directory = resolve_account_dir(provider, account, PREFIXES[provider])
    account_lock.lock_account(provider, normalized, str(os.getpid()), change, session_id)
    return directory


def _write_last_message(path: Path, result: Any) -> None:
    text = getattr(result, "result", None) or getattr(result, "final_response", None) or ""
    if not text:
        error = getattr(result, "error", None)
        text = getattr(error, "message", None) or (str(error) if error else "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(text), encoding="utf-8")


async def _run_claude_sdk(prompt: str, model: str, effort: str, workspace: Path, repository: Path, account_dir: Path | None, stdout: Path, timeout_seconds: float) -> tuple[int, str, Any]:
    environment = child_environment()
    if account_dir is not None:
        environment["CLAUDE_CONFIG_DIR"] = str(account_dir)
    options = ClaudeAgentOptions(
        cli_path=executable("claude", "run-claude-phase"),
        cwd=workspace,
        add_dirs=[] if repository == workspace else [repository],
        env=environment,
        model=model,
        effort=effort,
        permission_mode="bypassPermissions",
    )
    client = ClaudeSDKClient(options)
    try:
        await client.connect()
        outcome = await supervise_claude_turn(
            client,
            prompt,
            timeout_seconds=timeout_seconds,
            kill_after_seconds=30,
            on_message=lambda message: append_jsonl(stdout, message),
        )
        result = outcome.result
        result_class = classify_sdk_result(result, provider="claude", timed_out=outcome.timed_out, hard_killed=outcome.hard_killed)
        return (0 if result_class == "success" else 1), result_class, result
    except BaseException as error:
        append_text = stdout.with_suffix(".error")
        append_text.write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")
        return 1, classify_sdk_result(provider="claude", error=error), error
    finally:
        await client.disconnect()


def _run_codex_sdk(prompt: str, model: str, effort: str, workspace: Path, stdout: Path, timeout_seconds: float, account_dir: Path | None) -> tuple[int, str, Any]:
    environment = child_environment()
    if account_dir is not None:
        environment["CODEX_HOME"] = str(account_dir)
    config = CodexConfig(codex_bin=executable("codex", "run-codex-phase"), cwd=str(workspace), env=environment)
    codex = None
    try:
        codex = Codex(config)
        thread = codex.thread_start(approval_mode=ApprovalMode.deny_all, cwd=str(workspace), ephemeral=True, model=model, sandbox=Sandbox.full_access)
        handle = thread.turn(prompt, effort=effort, model=model, sandbox=Sandbox.full_access)
        outcome = supervise_codex_turn(handle, timeout_seconds=timeout_seconds, kill_after_seconds=30)
        result = outcome.result
        append_jsonl(stdout, result)
        result_class = classify_sdk_result(result, provider="codex", timed_out=outcome.timed_out, hard_killed=outcome.hard_killed)
        return (0 if result_class == "success" else 1), result_class, result
    except BaseException as error:
        stdout.with_suffix(".error").write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")
        return 1, classify_sdk_result(provider="codex", error=error), error
    finally:
        if codex is not None:
            codex.close()


def run(provider: str, argv: list[str]) -> int:
    prefix = PREFIXES[provider]
    if len(argv) != 3:
        raise CLIError(f"{prefix}: usage: {prefix}.sh <change> <repository> <PLAN|IMPLEMENT|VERIFY|FIX|FINAL_VERIFY>")
    change, repository, phase = argv
    state, state_file, session_id, round_value, workspace, runtime_dir = _validate_common(change, repository, phase, provider)
    model, effort = os.environ.get("PHASE_AGENT_MODEL", ""), os.environ.get("PHASE_AGENT_EFFORT", "")
    account = os.environ.get("PHASE_AGENT_ACCOUNT", "")
    if not model or not effort:
        current_lock, candidates_state = candidates.with_state()
        try:
            phase_state = candidates_state["phases"][candidates.normalize_phase(phase)]
            selected = next((item for item in phase_state["candidates"] if item["provider"] == provider and (candidates_state["providers"][provider].get("accounts", {}).get(item.get("account"), {}).get("available", True) if item.get("account") else candidates_state["providers"][provider].get("available", True))), None)
            if selected is None:
                raise CLIError(f"{prefix}: resolved candidate is not {provider.title()}")
            model, effort, selected_account = selected["model"], selected["effort"], selected.get("account", "")
            account = account or selected_account
        finally:
            current_lock.release()
    if not SAFE_IDENTIFIER.fullmatch(model):
        raise CLIError(f"{prefix}: unsafe model")
    valid_efforts = {"claude": {"low", "medium", "high", "xhigh", "max"}, "codex": {"none", "minimal", "low", "medium", "high", "xhigh"}}[provider]
    if effort not in valid_efforts:
        raise CLIError(f"{prefix}: unsupported {provider.title()} effort")
    if provider == "claude" and re.search(r"(^|[-.:])opus($|[-.:])", model) and effort not in {"medium", "high"}:
        raise CLIError(f"{prefix}: Opus requires medium or high")
    timeout_name = "CLAUDE_TIMEOUT_SECONDS" if provider == "claude" else "CODEX_TIMEOUT_SECONDS"
    timeout_text = os.environ.get(timeout_name, "3600")
    if not timeout_text.isdigit() or int(timeout_text) < 1:
        raise CLIError(f"{prefix}: invalid timeout")
    continuation = os.environ.get("PHASE_AGENT_CONTINUATION", "false")
    if continuation not in {"true", "false"}:
        raise CLIError(f"{prefix}: invalid continuation mode")
    findings = ""
    if phase == "FIX":
        findings_path = runtime_dir / f"verification-findings-round-{round_value}.md"
        if not findings_path.is_file() or not findings_path.stat().st_size:
            raise CLIError(f"{prefix}: FIX findings missing: {findings_path}")
        findings = findings_path.read_text(encoding="utf-8")
    prompt = build_prompt(change, _git_root(repository, prefix), phase, continuation == "true", findings)
    account_dir = _lock_account(provider, account, change, session_id)
    try:
        log_dir = runtime_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        attempt_id = os.environ.get("PHASE_AGENT_ATTEMPT_ID", f"direct-{os.getpid()}")
        if not SAFE_IDENTIFIER.fullmatch(attempt_id):
            raise CLIError(f"{prefix}: unsafe attempt id")
        base = Path(os.environ.get("PHASE_AGENT_EVIDENCE_BASE", str(log_dir / f"{provider}-{phase.lower()}-round-{round_value}-{attempt_id}")))
        stdout, stderr, last, exit_file, result_file = (base.with_suffix(suffix) for suffix in (".stdout.jsonl", ".stderr.log", ".last-message.md", ".exit", ".result-class"))
        stdout.parent.mkdir(parents=True, exist_ok=True)
        stdout.write_text("", encoding="utf-8")
        stderr.write_text("", encoding="utf-8")
        before = (fingerprint(workspace), fingerprint(_git_root(repository, prefix))) if phase in {"VERIFY", "FINAL_VERIFY"} else None
        if provider == "claude":
            status, result_class, result = asyncio.run(_run_claude_sdk(prompt, model, effort, workspace, _git_root(repository, prefix), account_dir, stdout, int(timeout_text)))
        else:
            status, result_class, result = _run_codex_sdk(prompt, model, effort, workspace, stdout, int(timeout_text), account_dir)
        _write_last_message(last, result)
        if before is not None:
            after = (fingerprint(workspace), fingerprint(_git_root(repository, prefix)))
            if before != after:
                stderr.write_text("read-only verifier mutated a Git worktree\n", encoding="utf-8", errors="replace")
                status, result_class = 1, "implementation-error"
        exit_file.write_text(f"{status}\n", encoding="utf-8")
        result_file.write_text(f"{result_class}\n", encoding="utf-8")
        if result_class in {"global-quota-exhausted", "auth-error", "success"}:
            args = ["provider-result", provider, result_class]
            if account:
                args.append(account)
            candidates.mutate("provider-result", args)
        if status:
            print(f"{provider.title()} phase {phase} failed: {result_class}", file=sys.stderr)
            return status
        print(f"{provider.title()} phase {phase} completed: {base}")
        return 0
    finally:
        if account:
            account_lock.unlock_account(provider, account, str(os.getpid()), change, session_id)
