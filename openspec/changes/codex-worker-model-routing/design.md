## Context

The current generic Codex launcher performs one unclassified attempt and inherits user model configuration. The runtime already owns immutable backend state, FIX round increments, repository locks, terminal cleanup, and quant availability toggles. This change extends those contracts without moving lifecycle ownership into the worker.

Official OpenAI model documentation and the installed `codex-cli 0.150.1` establish the full model IDs, `high` reasoning support, explicit `--model`/`--config` arguments, and `--dangerously-bypass-approvals-and-sandbox` as the supported non-interactive equivalent of the requested `--yolo`. Local no-tool probes confirmed Luna, Terra, and Sol are available.

## Goals / Non-Goals

**Goals:**

- Make phase-to-model routing independent of user config.
- Keep fallback classification deterministic and testable without external model calls.
- Preserve enough per-attempt evidence for Claude verification while keeping metadata secret-safe.
- Carry exact current-round Claude findings into FIX.
- Disable only future Codex selection after explicit account-wide quota exhaustion.

**Non-Goals:**

- Changing Claude/Codex phase ownership, runtime repository ownership, release gates, or production deployment.
- Automatically re-enabling Codex, weakening the quant fallback gate, or interpreting ordinary coding failures as capacity failures.
- Adding an unbounded retry loop or changing the existing maximum FIX rounds.

## Decisions

### Use full official model IDs and explicit effort

The launcher defaults to `gpt-5.6-luna`, `gpt-5.6-terra`, and `gpt-5.6-sol`, passing `model_reasoning_effort="high"` on each invocation. Environment variables retain controlled operator overrides. Full IDs avoid relying on undocumented local aliases; inheriting `~/.codex/config` was rejected because it makes CI/operator behavior non-deterministic.

### Treat requested `--yolo` as the installed CLI's canonical flag

`codex-cli 0.150.1` does not expose a literal `--yolo`. Worker argv therefore uses `--dangerously-bypass-approvals-and-sandbox`, whose documented behavior matches the request. Any Claude CLI launcher in scope uses the literal supported `--dangerously-skip-permissions`. These flags are asserted by fake-CLI tests.

### Classify evidence before deciding fallback

A separate classifier accepts exit status plus captured JSONL/stderr evidence. It checks structured code/type/category fields first, then stable normalized patterns, with explicit global quota patterns preceding generic 429/rate-limit patterns. Exit status 124 maps to timeout. This keeps policy auditable and lets tests inject exact evidence without real API calls.

### Keep attempt policy in the generic launcher

The launcher owns model selection, attempt numbering, evidence naming, metadata, FIX-only Sol fallback, and automatic `codex-off`. The runtime helper remains the authority for rounds, immutable backends, and cleanup. This avoids a second lifecycle state machine inside the worker.

### Require findings at the launcher boundary

The Claude orchestration command writes `verification-findings-round-<round>.md` after entering each FIX round. The launcher fails before invocation when that exact artifact is missing and injects only that file into the FIX prompt. A Sol retry reuses it because attempt fallback does not call the runtime `fix` operation.

### Keep metadata allowlisted and evidence files attempt-scoped

Each attempt uses a common basename and four evidence files plus atomic JSON metadata. Metadata is constructed from an explicit allowlist rather than serializing process state. Prompts and environment values never enter metadata.

## Risks / Trade-offs

- [Permission-bypass flags grant broad worker authority] → Limit them to explicit worker launchers, preserve repository/change locks, and test their exact placement.
- [Provider wording changes could evade pattern classification] → Prefer structured fields, keep patterns narrow, classify uncertainty as `unknown-error`, and retain raw bounded evidence for diagnosis.
- [A true quota event could be missed rather than auto-disable] → Fail safely without switching backend; operators can still use manual `/quant:codex-off` after review.
- [Environment overrides can select an unavailable model] → Apply the same classifier/fallback rules and record the actual model in metadata.

## Migration Plan

1. Add classifier and update the generic launcher with attempt-scoped evidence.
2. Update orchestration handoff and bounded fake-CLI tests.
3. Run shell syntax, contract suites, strict OpenSpec validation, and Agent Contracts CI.
4. Commit and push the orchestration-only change; do not deploy production.

Rollback is a normal Git revert. If automatic quota detection disabled Codex availability during testing, restore it manually with `/quant:codex-on` after confirming quota is available.
