---
description: "Run one fast, bounded implementation turn for a quick or recurring request"
---

Run one bounded, stateless implementation turn for:

$ARGUMENTS

For quick, small tasks, or the same kind of task run repeatedly — not a
multi-phase lifecycle. There is no coordinator, lease, worktree allocation,
or shell-state orchestration: `tools/orchestrator/`'s old coordinator-based
`/ops:e2e` (SQLite state, `run-phase-agent`, `configure-agent-roles`,
per-attempt worktrees) was deleted (commit `73a3a71`) and this command does
not reintroduce it. Each invocation is independent; nothing is remembered
between runs, so this is safe to call again for the next task in a batch or
on a `/loop` interval.

## Steps

1. **Implement.** Run the request through one bounded provider turn using
   this workspace's own `tools/orchestrator` CLIs:

   ```bash
   uv run --project tools/orchestrator codex-exec "<request>"
   ```

   Codex is the default implementer (`CLAUDE.md`/`AGENTS.md` role boundary:
   `IMPLEMENT / FIX = Codex first, Claude fallback`). Fall back to
   `claude-exec` only when Codex is confirmed out of quota for this attempt
   — a generic 429, timeout, or network blip is not quota exhaustion, and
   there is no automatic resolver to detect the difference; that judgment
   is manual.

   ```bash
   uv run --project tools/orchestrator claude-exec "<request>"
   ```

   Both run one full bounded agentic turn end-to-end (file edits, test
   runs, etc. within that turn, not just a text completion), streaming
   output and — for `codex-exec` — appending a JSONL log; see
   `tools/orchestrator/README.md` for `--model`/`--effort`/`--timeout-seconds`
   and account-failover configuration (`ORCHESTRATOR_CODEX_ACCOUNTS` /
   `ORCHESTRATOR_CLAUDE_ACCOUNTS`).

2. **Verify.** Run the checks relevant to whatever changed (tests, lint,
   build) scoped to that change — not a full separate-process VERIFY pass.
   For anything non-trivial per `.agents/rules/coding-and-verification.md`,
   that fuller independent VERIFY/FINAL_VERIFY gate still applies before
   pushing; this command covers the fast implement step, not that gate.

3. **Report.** Summarize what changed and the verification result. Do not
   commit or push unless the request explicitly asked for that.

## When this isn't the right tool

A change touching multiple repositories, requiring formal OpenSpec
planning, or needing independent (different-provider) VERIFY/FINAL_VERIFY
evidence before release should go through `/opsx:propose` first and follow
`.agents/rules/coding-and-verification.md`'s full required order — this
command is deliberately the fast path for everything else.
