## Context

See `proposal.md - Why`. `resolve_account_dir(provider, account, prefix)` in
`common.py` is the single chokepoint every caller already goes through
(design.md of `phase-agent-multi-account-routing`, Decision 1) — this
change only needs to change what is inside that one function's lookup, not
any of its callers.

## Goals / Non-Goals

**Goals:**
- One YAML file lists every account for both providers in one place.
- Same fail-fast behavior as today: an unknown account, or an account whose
  directory does not exist, dies with a clear message before any lock is
  taken or subprocess spawned.
- Zero change to the candidate schema, lock semantics, or CLI argument
  shapes established by `phase-agent-multi-account-routing`.

**Non-Goals:**
- No UI or CLI command to edit the file; it is hand-edited, like
  `tools/phase-agent-orchestrator/pyproject.toml` already is.
- No secret storage in this file — it holds directory *paths* only, the
  same thing the env vars held.

## Decisions

**1. File location: `tools/phase-agent-orchestrator/accounts.yaml`, overridable via
`PHASE_AGENT_ACCOUNTS_FILE`.**
Kept beside the Python package that reads it, matching where
`pyproject.toml`/`uv.lock` already live. The env-var override exists for
the same reason `OPS_ROOT` and similar overrides exist elsewhere in this
codebase: tests point it at a temp file instead of monkeypatching a dozen
individual variables.
*Alternative considered*: a top-level `.agents/accounts.yaml` next to
`.agents/rules`/`.agents/skills` — rejected; those directories are shared
Finance-ecosystem source of truth per `CLAUDE.md`, while this file is
purely local operator configuration for one Python package.

**2. Shape:**
```yaml
claude:
  personal: /home/operator/.claude-personal
  work: /home/operator/.claude-work
codex:
  personal: /home/operator/.codex
```
Top-level keys are `claude`/`codex` (matches `PROVIDERS` in the existing
code); each maps account name (already validated by
`normalize_account`/`ACCOUNT_NAME`) to an absolute or `~`-relative
directory path (expanded exactly like the env var value is today).
*Alternative considered*: a flat `provider/account` key
(`claude/work: ...`) — rejected as a less natural YAML shape than nesting.

**3. Missing file, missing provider key, or missing account key all die
through the same `resolve_account_dir` path with distinct messages** (file
not found; provider has no accounts configured; account not found under
that provider) rather than a generic KeyError, matching the existing
env-var version's behavior of a specific, actionable message per failure
mode (design.md Risk in `phase-agent-multi-account-routing`).

## Risks / Trade-offs

- **[Risk]** Any operator who set the old `PHASE_AGENT_*_ACCOUNT_*_DIR`
  vars gets a silent behavior change (accounts vanish) unless they migrate.
  → **Mitigation**: this is a single-operator repository (per this
  session's account setup); the operator doing this migration is the same
  person maintaining the file, so there is no other consumer to silently
  break. Still, fail with "no accounts configured" rather than treating a
  missing file as zero accounts silently succeeding for the account-less
  path (account-less resolution is unaffected either way).
- **[Trade-off]** Adds a real dependency (`pyyaml`) where before there were
  none beyond the standard library — accepted, since a config file this
  shape is exactly what YAML is for, and the alternative (hand-rolling a
  parser for a strict subset, or overloading JSON where nested comments and
  operator-editability matter less) is worse.
