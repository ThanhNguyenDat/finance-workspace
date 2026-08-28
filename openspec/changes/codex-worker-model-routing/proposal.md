## Why

Codex orchestration currently depends on the operator's local model defaults and treats all worker failures alike. This makes IMPLEMENT/FIX behavior non-deterministic, loses Claude verification context between rounds, and cannot safely distinguish global quota exhaustion from model-local or transient failures.

## What Changes

- Route IMPLEMENT to Luna/high, FIX to Terra/high, and a same-round FIX fallback to Sol/high using explicit CLI arguments.
- Pass the supported non-interactive equivalent of Codex `--yolo` to every Codex worker and `--dangerously-skip-permissions` to any Claude CLI worker invocation in this orchestration scope.
- Add a deterministic, evidence-based Codex result classifier and attempt metadata while preserving stdout JSONL, stderr, last-message, and exit-code evidence.
- Disable Codex availability for future quant transactions only on explicit global quota exhaustion; preserve the active transaction's immutable backend and never disable on generic HTTP 429 responses.
- Require round-specific Claude verification findings before every FIX worker invocation and keep Terra-to-Sol fallback in the same FIX round.
- Add bounded fake-CLI regression coverage, CI integration, and operator documentation.

## Capabilities

### New Capabilities

- `codex-worker-policy`: Deterministic worker model/effort selection, permission flags, result classification, fallback, evidence, and round-specific FIX handoff.

### Modified Capabilities

- `ops-backend-routing`: Preserve backend immutability and terminal cleanup when a Codex worker reports global quota exhaustion or model-local exhaustion.
- `quant-research-control`: Automatically disable Codex for future transactions only after explicit global quota exhaustion while retaining manual re-enable behavior.

## Impact

- Affected repository: `finance-workspace` only.
- Affected components: `.agents/scripts` worker/runtime helpers and tests, `.claude/commands/ops/run.md`, Agent Contracts CI, README/operator contracts, and OpenSpec.
- No runtime trading code, API, database, market-data, order, deployment, or production behavior changes.
- Rollback is a normal Git revert; no persistent production state is migrated. Transient quant availability can be restored manually with `/quant:codex-on`.
