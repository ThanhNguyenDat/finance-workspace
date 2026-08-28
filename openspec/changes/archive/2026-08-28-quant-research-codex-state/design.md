## Context

See `proposal.md` and the `quant-research-control` delta spec. The workspace already owns `.claude/commands/ops/run.md`, the transient `.ops` runtime contract, shared rules, and the Agent Contracts workflow. Claude Code 2.1.250 supports Markdown custom commands and file references, but its CLI help does not expose a supported API for recursively invoking one custom command from another.

## Goals / Non-Goals

**Goals:**

- Make Codex availability a mechanically readable state for each research iteration.
- Keep state mutations safe under concurrent loop/toggle activity.
- Give Claude one bounded quant iteration that can hand off normally or enter an explicit fallback lifecycle.
- Reuse the existing `/ops:run` contract by reference and preserve its default Codex backend.
- Verify the contract with deterministic, bounded local and CI tests.

**Non-Goals:**

- Running a real research loop or backtest in CI.
- Adding a second orchestration state machine, recursive Claude session, scheduler, or production deployment path.
- Changing trading runtime code, strategy algorithms, APIs, schemas, or production state.

## Decisions

1. **Use a small Bash state helper.** `quant-research-state.sh` owns initialization, schema validation, toggles, and iteration recording. Bash plus `jq` matches the existing repository tooling and keeps the command API inspectable.
   - Alternative rejected: prose-only mutation in command prompts, because it cannot guarantee atomic updates or malformed-state protection.

2. **Use an atomic JSON replacement with a short-lived mkdir lock.** Mutations validate the current file, write validated JSON to a temporary file in the same directory, then rename it. A lock directory records the owner PID, rejects a live competing mutation, and removes stale ownership after verifying the PID is gone.
   - Alternative rejected: direct in-place `jq` writes, which can leave a truncated state file after interruption.

3. **Keep the runtime file transient.** `.ops/**/runtime/` already ignores `.ops/runtime/quant-research/state.json`; tests use an override state directory so CI never mutates the checkout.
   - Alternative rejected: committed state, because quota availability and iteration counters are operational state, not durable requirements.

4. **Reference `/ops:run` instead of copying it.** `/quant-research` uses a Claude file reference to the existing command contract when fallback implementation is needed and supplies only the explicit backend condition. `/ops:run` is amended only to document that the default remains Codex and that fallback is explicit.
   - Alternative rejected: literal nested custom-command invocation, because installed CLI help does not establish that recursive composition is supported.

5. **Keep fallback self-review honest.** When the current Claude session implements fallback code, the command requires `claude-fallback-self-review` in the evidence and stronger diff/test/CI/deployment checks; it must not call another Claude CLI.

## Risks / Trade-offs

- [A stale lock directory could block a toggle] → store the PID, reject only a live owner, and remove a stale exact lock directory; tests cover both paths.
- [A loop iteration could race with a toggle] → all mutations use the same state lock and atomic replacement; the next iteration re-reads state after recording its own timestamp.
- [A prompt reference could be misunderstood as command recursion] → document that it is a reusable instruction reference, not a nested CLI invocation, and test for forbidden `claude -p`/nested invocation text.
- [Quant command scope is broad] → keep it as one bounded iteration with fixed instrument priority, resource cap, OOS evidence, triad outputs, and no automatic implementation in normal mode.

## Migration Plan

1. Install the helper and command files; no existing runtime state is migrated.
2. The first `init` creates default enabled state atomically. Existing valid state is preserved; malformed state is reported and not replaced.
3. Run local contract tests and Agent Contracts CI.
4. Rollback is deleting the new command/helper/test/docs files from a follow-up commit; no production rollback or data migration is required.

## Open Questions

None. The installed CLI composition limitation is resolved by the file-reference decision above.
