## Why

`CLAUDE.md`/`AGENTS.md` declare a role boundary (`PLAN/VERIFY/FINAL_VERIFY =
Claude first, Codex fallback`; `IMPLEMENT/FIX = Codex first, Claude
fallback`), but neither `codex-exec` nor `claude-exec` know which
lifecycle step (role) a given invocation is for, or whether that role is
the one the operator's `config.yaml` says that provider usually handles.
The operator wants a lightweight, informational check: declare the role
per invocation, get a heads-up when it doesn't match the provider's usual
scope, without that check ever stopping the operator from actually doing
the fallback the role boundary itself explicitly allows.

## What Changes

- Add `--role <role>` to both `codex-exec` and `claude-exec`
  (`plan|implement|verify|fix|final_verify`, matching `CLAUDE.md`'s Working
  Model phases). Optional — omitting it disables this check entirely, no
  behavior change from today.
- Add an optional `scope: [<role>, ...]` list under each provider's key in
  `tools/orchestrator/config.yaml` (alongside the existing `accounts` list).
- When `--role` is given and that provider's `config.yaml` has a non-empty
  `scope` list that does not contain the given role, print one warning
  line to stderr before starting the turn (e.g. `implement is outside
  claude's configured scope (plan, verify, final_verify)`). **This is
  advisory only**: the command still runs the turn normally, and the
  process exit code still reflects only the turn's own success/failure —
  never the scope mismatch. A mismatch is expected and valid during a
  genuine fallback (the provider whose quota is exhausted routes to the
  other one for that role), so this must never block or fail the command.
- When `--role` is omitted, or the provider's `scope` is unset/empty, no
  check happens at all — fully backward compatible.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `orchestrator-exec-cli`: adds `--role` and the advisory scope-mismatch
  warning to both `codex-exec` and `claude-exec` (new requirement; no
  existing requirement's behavior changes).

## Impact

- Affected paths: `tools/orchestrator/src/orchestrator/cli/_shared.py`
  (`--role` argument, warning emission),
  `tools/orchestrator/src/orchestrator/utils/config.py` (read `scope` per
  provider), `tools/orchestrator/src/orchestrator/cli/codex_exec.py`,
  `tools/orchestrator/src/orchestrator/cli/claude_exec.py`, their tests,
  `tools/orchestrator/config.yaml` (add `scope` under `claude:`/`codex:`),
  `tools/orchestrator/README.md`.
- Builds on `scope-orchestrator-logs-by-change` (change-scoped logging) if
  that lands first — a role-scope warning is a natural line to also write
  into a change's log — but does not require it; this change stands alone
  if applied independently.
- No changes to `finance-mw`, `finance-web`, `finance-live-action`,
  `finance-broker`, `mt5`, or any runtime code — workspace-local tooling
  only.
