# Phase-agent orchestrator

The Python package is the source of truth for OPS state, candidate routing,
provider SDK adapters, availability detection, result classification, and log
monitoring. Operator commands use `uv` so the project environment and locked
dependencies are selected consistently:

```bash
uv run --project tools/orchestrator ops-runtime state <change>
uv run --project tools/orchestrator phase-agent-state state
uv run --project tools/orchestrator run-phase-agent <change> <repo> IMPLEMENT
uv run --project tools/orchestrator run-phase-agent-command quant-research
```

The source is split by responsibility:

- `orchestrator/cli/` contains process-facing argument parsing and
  command dispatch only.
- `orchestrator/providers/` contains reusable SDK, availability,
  and result-classification adapters.
- `orchestrator/runners/` contains reusable lifecycle and quant
  orchestration runners; it does not own argument parsing.
- `core/`, `state/`, `coordinator/`, `accounts/`, `locks/`, and
  `subprocess_supervision/` contain reusable domain services.

The package root intentionally contains no implementation modules; new code
must import from one of the responsibility-specific subpackages above.

The optional `bin/*.sh` files are compatibility wrappers for integrations that
need an executable path; they contain no orchestration logic and only dispatch
to the same `uv` project. Contract tests remain under `.agents/scripts/tests/`
because they exercise the shell boundary.

Provider accounts are configured in `accounts.yaml`, next to this package.
Copy [`accounts.yaml.example`](accounts.yaml.example) and replace its example
paths with the local Claude and Codex account directories. Set
`PHASE_AGENT_ACCOUNTS_FILE` when a different registry path is needed, such as
for tests. The real `accounts.yaml` is local-only and ignored by Git.
