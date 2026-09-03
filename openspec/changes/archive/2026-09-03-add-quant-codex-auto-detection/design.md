## Context

The quant state helper currently stores one resolved availability boolean and
provides atomic `codex-on` and `codex-off` mutations.
`classify-codex-result.sh` already distinguishes explicit account-wide quota
exhaustion from generic 429, model-local, authentication, network, timeout, and
unknown failures. The state does not say whether its boolean is an explicit
manual override or a value that should be refreshed automatically.

## Goals / Non-Goals

**Goals:**

- Persist whether quant routing uses automatic detection or a manual override.
- Reconcile auto-mode routing at command selection and before every research
  iteration.
- Preserve the exact previous state whenever availability is ambiguous.
- Keep the probe bounded, non-interactive, non-persistent, and independently
  testable without a real model service.
- Preserve role-specific model routing rather than applying one model or effort
  to every Codex phase.

**Non-Goals:**

- Monitor quota outside explicit auto-command and research-iteration starts or
  modify an existing `/loop` schedule.
- Change an active OPS transaction's persisted backend.
- Treat binary presence, authentication, generic 429, or model-local capacity
  as proof of account-wide availability or exhaustion.
- Remove the explicit on/off overrides.
- Move VERIFY or FINAL_VERIFY from independent Claude execution to Codex.

## Decisions

### 1. Separate selection mode from resolved availability

Schema version 2 adds `codex_mode`, constrained to `auto|manual`, and a
`codex_profiles` object while retaining `codex_available` as the last resolved
routing value. The profiles are `probe`, `implement`, `fix`, and
`fix_fallback`; each contains a non-empty model and a supported reasoning
effort. A missing state initializes as manual/available with the current
role-specific defaults: Luna/high for probing and implementation, Terra/high
for primary fixing, and Sol/high for eligible fix fallback. A valid v1 state
migrates atomically to v2/manual with those defaults while retaining all prior
fields and timestamps; malformed or unsupported states remain untouched.

`/quant:codex-auto` selects auto mode and probes immediately.
`/quant:codex-manual` selects manual mode without changing availability.
`/quant:codex-on` and `/quant:codex-off` select manual mode and explicitly set
availability. Using one enum with `auto|on|off` was rejected because it would
conflate selection policy with the most recent detected availability.

`/quant:codex-config` shows the four profiles, updates exactly one profile with
`<role> <model> <effort>`, or resets one role/all roles to defaults. The command
accepts only `probe|implement|fix|fix-fallback`; the stored key for the last role
is `fix_fallback`. It validates model names as non-empty safe CLI values and
effort against `none|minimal|low|medium|high|xhigh`, then uses the same locked,
atomic state mutation path as mode changes. It never prints raw state JSON.

### 2. Use a dedicated detector script

Add a small detector that runs outside the state helper. It invokes one Codex
probe under GNU `timeout`, captures stdout/stderr in a private temporary
directory, classifies the result with the existing classifier, and removes the
temporary evidence on exit. It invokes the atomic state helper only after a
conclusive classification, so no state lock is held across the probe.

Embedding the probe in `quant-research-state.sh` was rejected because that
would mix remote availability checks with deterministic state mutation and
would risk holding the mutation lock while Codex hangs.

### 3. Use a minimal isolated Codex invocation

The detector reads the `probe` profile and uses `codex exec
--dangerously-bypass-approvals-and-sandbox --ignore-user-config --ephemeral
--skip-git-repo-check --json --model <model> --config
model_reasoning_effort=<effort>` from a temporary working directory with a
minimal response-only prompt. The timeout is configurable for tests but
validated as a positive integer. The probe neither reads the Finance
repositories nor grants additional directories.

The older `--yolo` spelling was rejected after checking the installed CLI:
current `codex exec --help` exposes only the explicit bypass flag above. The
selected flag preserves the requested yolo semantics without making every real
probe fail argument parsing.

Checking only `command -v codex` or `codex --version` was rejected because it
proves installation, not service/quota availability.

### 4. Resolve auto mode only on conclusive outcomes

- `success` records detected availability true while preserving auto mode.
- `global-quota-exhausted` records detected availability false while preserving
  auto mode.
- Every other classifier result, a missing dependency, or timeout leaves the
  last resolved availability untouched and returns a concise inconclusive
  classification.

This asymmetry prevents a transient provider or network problem from silently
routing future engineering work to Claude fallback.

### 5. Probe at every auto-mode iteration boundary

`/quant-research` reads state first. In auto mode it invokes the detector, then
re-reads state before recording the iteration and selecting the backend. An
inconclusive probe does not abort research; the iteration continues with the
last resolved availability and reports the limitation. Manual mode skips the
probe entirely.

The detector does not run continuously or reschedule the loop. This gives auto
mode a deterministic retry point without adding a daemon or parallel state
writer.

### 6. Keep command output concise

The custom command runs the detector exactly once and reports the resulting or
inconclusive mode in Vietnamese. It does not print runtime JSON, probe stdout,
stderr, prompts, credentials, or environment values.

### 7. Route Codex profiles by phase and keep review independent

The Codex phase runner resolves `implement` only for IMPLEMENT, `fix` for the
first FIX attempt, and `fix_fallback` only for an eligible fallback. Explicit
phase-runner environment overrides retain precedence for operational
compatibility; otherwise persisted profiles override built-in defaults. Every
attempt records the effective model and effort in existing worker metadata.

VERIFY and FINAL_VERIFY remain independent Claude phases. Adding a Codex
`review` profile was rejected because it would turn implementation
self-review into the release gate and violate the workspace ownership model.

## Risks / Trade-offs

- [Auto mode consumes one small model request per iteration] → Use one minimal
  response and probe only at the deterministic iteration boundary.
- [A selected model can be unavailable while the account has quota] → Classify
  as inconclusive and preserve state rather than guessing.
- [Codex hangs or loses network] → Enforce TERM plus KILL timeout and clean the
  temporary directory with a trap.
- [Probe output could contain provider details] → Keep logs private and
  ephemeral; expose only the safe result class.

## Migration Plan

1. Add schema-v2 migration and atomic auto/manual/detected-result operations.
2. Add role-specific profile operations and `/quant:codex-config`, then route
   the detector and phase runner through their matching profiles.
3. Add the detector plus `/quant:codex-auto` and `/quant:codex-manual` commands,
   then make `/quant-research` invoke detection only in auto mode.
4. Add fake-Codex tests for migration, mode transitions, success, global quota,
   generic 429, timeout, missing executable, and last-value preservation.
5. Run bounded Agent Contracts and strict OpenSpec validation.

Rollback removes the command/detector and converts schema-v2 state back to the
existing boolean fields by dropping `codex_mode`; the last resolved
`codex_available` value remains usable by the old helper.
