# Phase-agent orchestrator

The Python package is the source of truth for OPS state, candidate routing,
provider SDK adapters, availability detection, result classification, and log
monitoring. Operator commands use `uv` so the project environment and locked
dependencies are selected consistently:

```bash
uv run --project tools/phase-agent-orchestrator ops-runtime state <change>
uv run --project tools/phase-agent-orchestrator phase-agent-state state
uv run --project tools/phase-agent-orchestrator run-phase-agent <change> <repo> IMPLEMENT
uv run --project tools/phase-agent-orchestrator run-phase-agent-command quant-research
```

The source is split by responsibility:

- `phase_agent_orchestrator/cli/` contains process-facing argument parsing and
  command dispatch only.
- `phase_agent_orchestrator/providers/` contains reusable SDK, availability,
  and result-classification adapters.
- `phase_agent_orchestrator/runners/` contains reusable lifecycle and quant
  orchestration runners; it does not own argument parsing.
- `state/`, `coordinator/`, `accounts/`, `locks/`, and
  `subprocess_supervision/` contain reusable domain services.

The old top-level module paths remain small compatibility facades for existing
imports; new code should use the grouped modules above.

The optional `bin/*.sh` files are compatibility wrappers for integrations that
need an executable path; they contain no orchestration logic and only dispatch
to the same `uv` project. Contract tests remain under `.agents/scripts/tests/`
because they exercise the shell boundary.

Provider accounts are configured in `accounts.yaml`, next to this package.
Copy [`accounts.yaml.example`](accounts.yaml.example) and replace its example
paths with the local Claude and Codex account directories. Set
`PHASE_AGENT_ACCOUNTS_FILE` when a different registry path is needed, such as
for tests. The real `accounts.yaml` is local-only and ignored by Git.
