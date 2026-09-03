## Why

**Sequencing**: land after `phase-agent-orchestrator-submodules`, so this
change edits `accounts/registry.py` directly instead of the flat
`common.py` it would otherwise need to move out from under.

`phase-agent-multi-account-routing` (merged) resolves each named account
through an environment variable per account
(`PHASE_AGENT_<PROVIDER>_ACCOUNT_<NAME>_DIR`). The operator finds exporting
one env var per account awkward to manage and review at a glance — the
registry is scattered across shell profile lines with no single place that
enumerates every configured account. This change replaces the env-var
registry with one declarative YAML file, with no change to any external
behavior (candidate schema, lock semantics, or resolution/failover rules
are untouched).

## What Changes

- Replace `PHASE_AGENT_<PROVIDER>_ACCOUNT_<NAME>_DIR` env vars with one YAML
  file (path TBD in design.md) declaring every account per provider.
- `phase_agent_orchestrator.common.resolve_account_dir`/
  `account_environment_name` read this file instead of `os.environ`; every
  caller of `resolve_account_dir` (the account lock, `account-dir`,
  candidate validation) is unaffected since they only call that function,
  never read the env vars directly.
- Add `pyyaml` as a dependency of `tools/phase-agent-orchestrator` (`uv add pyyaml`).
- No bash script changes: `run-claude-phase.sh`/`run-codex-phase.sh`/
  `run-phase-agent-command.sh` already resolve an account's directory by
  calling out to the Python CLI (`phase-agent-state.sh account-dir ...`)
  rather than reading `PHASE_AGENT_*_DIR` themselves, so they need no edits.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
(none — `ops-backend-routing`'s "Account eligibility and identity are
explicit and registry-bound" requirement only specifies that an account
resolves through a *fixed, named registry entry*; it does not mandate an
environment variable as the storage mechanism, so this is a pure
implementation change and `skip_specs: true` is set on this change)

## Impact

- **Affected repository**: `finance-workspace` only.
- **Affected files**: `tools/phase-agent-orchestrator/src/phase_agent_orchestrator/common.py`
  (registry resolution), `tools/phase-agent-orchestrator/pyproject.toml`/`uv.lock`
  (new dependency), the existing account-related pytest tests (must be
  updated from `monkeypatch.setenv` to writing/pointing at a temp YAML
  file), and `.agents/scripts/tests/test_multi_account_routing.sh` (its
  `PHASE_AGENT_CLAUDE_ACCOUNT_*_DIR` exports become a generated YAML fixture
  instead).
- **Migration**: existing operator shell profiles exporting
  `PHASE_AGENT_*_ACCOUNT_*_DIR` stop being read; this is a breaking change
  for anyone who configured an account via the old env vars, so design.md
  must define the exact new file's location and a clear error message when
  it is missing.
- **Trading safety**: none (orchestration tooling only).
