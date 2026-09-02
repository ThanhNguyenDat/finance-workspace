# Phase-agent orchestrator

Provider accounts are configured in `accounts.yaml`, next to this package.
Copy [`accounts.yaml.example`](accounts.yaml.example) and replace its example
paths with the local Claude and Codex account directories. Set
`PHASE_AGENT_ACCOUNTS_FILE` when a different registry path is needed, such as
for tests. The real `accounts.yaml` is local-only and ignored by Git.
