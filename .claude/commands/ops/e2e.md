---
description: "Run the bounded Finance phase-agent workflow"
---

Run one stateful OPS lifecycle for:

$ARGUMENTS

Invoke as `/ops:e2e "<request>"`. The parent process orchestrates deterministic
state and never calls a model CLI directly. Every model-owned phase runs only
through `uv run --project tools/orchestrator run-phase-agent`.

## Running a phase attempt without blocking

`run-phase-agent` can run up to its full timeout (default 3600s). Never
invoke it as a plain foreground call and never poll it with an ad-hoc
`sleep`/`ps aux | grep <pid>` loop — the PID changes every attempt and is
easy to get wrong. Always:

1. Launch it with `run_in_background: true`.
2. Immediately arm `uv run --project tools/orchestrator wait-for-phase-attempt <change>`
   in a `Monitor` (or as a second `run_in_background` command) — it blocks
   on the change's `.phase-attempt-lock` lease itself, not a PID, so it
   works unmodified across retries/continuations. Also arm
   `uv run --project tools/orchestrator watch-phase-attempt-log <change>` in a second
   `Monitor` to stream real agent progress (tool calls, file changes,
   messages) instead of manually polling status.
3. Do not manually re-check status between notifications. A stop hook may
   repeatedly report the change is still active while the attempt runs;
   that is expected and is not a signal to poll — wait for the Monitor/
   background-task notification instead.

## Contract

- Logical agents own PLAN, IMPLEMENT, VERIFY, FIX and FINAL_VERIFY; ordered
  Codex/Claude candidates are configured by
  `uv run --project tools/orchestrator configure-agent-roles`.
- Exactly one attempt owns the phase lease and repository lock. A provider/model
  cannot change while that attempt is alive.
- Confirmed global quota/model availability may select another candidate only
  after the old process exits. Partial PLAN/IMPLEMENT/FIX work is continued from
  the actual diff/commits; never roll it back or increment the FIX round.
- Generic 429, timeout, network or implementation failure is not global quota.
- VERIFY and FINAL_VERIFY are fresh read-only processes. Evidence derives
  `provider-independent` or `same-provider-process-separated` from the actual
  mutator/verifier providers.
- Provider adapters never push. Claude passes
  `--dangerously-skip-permissions`; Codex passes
  `--dangerously-bypass-approvals-and-sandbox`.
- Runtime evidence remains transient under `.ops/**/runtime/`; concise handoff
  never copies secrets, environment dumps, full logs or task files.
- `/ops:*` orchestrates; `/opsx:*` remains native OpenSpec integration.

## PLAN

1. Derive one stable kebab-case `<change>`, acquire the change lock, initialize
   the new routing-policy state, then read instructions:

   ```text
   uv run --project tools/orchestrator ops-runtime lock <change> <session-id>
   uv run --project tools/orchestrator ops-runtime init <change> <session-id>
   ```

2. Run `sync-agent-links.sh`; read AGENTS/CLAUDE, applicable rules/skills,
   current specs, active change and every affected repository's instructions.
3. Identify every affected runtime repository. Each phase attempt runs in
   its own detached Git worktree of that repository (allocated
   automatically by `run-phase-agent`); no repository-wide lock is needed
   or acquired — a change's worktree isolates it from any other change
   touching the same repository. A mutating phase (IMPLEMENT/FIX)
   fast-forwards the canonical repository onto its worktree's commits when
   it completes.
4. Run PLAN sequentially for each affected repository:

   ```text
   uv run --project tools/orchestrator run-phase-agent <change> <repository> PLAN
   ```

5. Validate the native OpenSpec change strictly. For a quant promotion, attach
   immutable origin references exactly once:

   ```text
   uv run --project tools/orchestrator ops-runtime trace-origin <change> <session-id> <research-iteration> <instrument> <research-artifact>...
   ```

## IMPLEMENT, VERIFY, FIX

Run each model phase sequentially through the same resolver:

```text
uv run --project tools/orchestrator ops-runtime phase <change> <session-id> IMPLEMENT
uv run --project tools/orchestrator run-phase-agent <change> <repository> IMPLEMENT

uv run --project tools/orchestrator ops-runtime phase <change> <session-id> VERIFY
uv run --project tools/orchestrator run-phase-agent <change> <repository> VERIFY
```

For P0/P1 findings, enter FIX atomically, write only the current round's exact
findings, then invoke the resolver:

```text
uv run --project tools/orchestrator ops-runtime fix <change> <session-id>
.ops/changes/<change>/runtime/verification-findings-round-<round>.md
uv run --project tools/orchestrator run-phase-agent <change> <repository> FIX
```

`OPS_MAX_FIX_ROUNDS` remains bounded at 3 by default. P2/P3 does not silently
become a release blocker. After a fix, return through VERIFY.

When no P0/P1 remains:

```text
uv run --project tools/orchestrator ops-runtime phase <change> <session-id> FINAL_VERIFY
uv run --project tools/orchestrator run-phase-agent <change> <repository> FINAL_VERIFY
```

Release requires successful derived FINAL_VERIFY evidence. Same-provider
process separation must explicitly state that provider independence is not
available; it may proceed only when all objective acceptance/test/security/
trading-safety evidence passes.

## RELEASE, DEPLOY_VERIFY, ARCHIVE

After FINAL_VERIFY gates pass, follow repository-delivery rules through local
commit, push, exact-SHA CI, deployment and production verification when scoped:

```text
uv run --project tools/orchestrator ops-runtime phase <change> <session-id> RELEASE
uv run --project tools/orchestrator ops-runtime phase <change> <session-id> DEPLOY_VERIFY
uv run --project tools/orchestrator ops-runtime phase <change> <session-id> ARCHIVE
uv run --project tools/orchestrator ops-runtime complete <change> <session-id>
```

Implementation defects found during RELEASE/DEPLOY_VERIFY return through the
atomic FIX path and fresh VERIFY/FINAL_VERIFY. External infrastructure blockers
become BLOCKED with evidence. Use centralized cleanup on terminal failure:

```text
uv run --project tools/orchestrator ops-runtime cleanup <change> <session-id> <FAILED|BLOCKED>
```

Legacy active transactions that already persist `implementation_backend` and
`verification_mode` retain their old routes until terminal; do not migrate them
in place.
