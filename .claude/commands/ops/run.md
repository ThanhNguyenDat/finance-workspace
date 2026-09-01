---
description: "Run the bounded Finance phase-agent workflow"
---

Run one stateful OPS lifecycle for:

$ARGUMENTS

Invoke as `/ops:run "<request>"`. The parent process orchestrates deterministic
state and never calls a model CLI directly. Every model-owned phase runs only
through `./.agents/scripts/run-phase-agent.sh`.

## Contract

- Logical agents own PLAN, IMPLEMENT, VERIFY, FIX and FINAL_VERIFY; ordered
  Codex/Claude candidates are configured by
  `./.agents/scripts/configure-phase-agents.sh`.
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
   ./.agents/scripts/ops-runtime.sh lock <change> <session-id>
   ./.agents/scripts/ops-runtime.sh init <change> <session-id>
   ```

2. Run `sync-agent-links.sh`; read AGENTS/CLAUDE, applicable rules/skills,
   current specs, active change and every affected repository's instructions.
3. Identify and lock every affected runtime repository before change-specific
   writes:

   ```text
   ./.agents/scripts/ops-runtime.sh lock-repos <change> <session-id> <repo>...
   ```

4. Run PLAN sequentially for each affected repository:

   ```text
   ./.agents/scripts/run-phase-agent.sh <change> <repository> PLAN
   ```

5. Validate the native OpenSpec change strictly. For a quant promotion, attach
   immutable origin references exactly once:

   ```text
   ./.agents/scripts/ops-runtime.sh trace-origin <change> <session-id> <research-iteration> <instrument> <research-artifact>...
   ```

## IMPLEMENT, VERIFY, FIX

Run each model phase sequentially through the same resolver:

```text
./.agents/scripts/ops-runtime.sh phase <change> <session-id> IMPLEMENT
./.agents/scripts/run-phase-agent.sh <change> <repository> IMPLEMENT

./.agents/scripts/ops-runtime.sh phase <change> <session-id> VERIFY
./.agents/scripts/run-phase-agent.sh <change> <repository> VERIFY
```

For P0/P1 findings, enter FIX atomically, write only the current round's exact
findings, then invoke the resolver:

```text
./.agents/scripts/ops-runtime.sh fix <change> <session-id>
.ops/changes/<change>/runtime/verification-findings-round-<round>.md
./.agents/scripts/run-phase-agent.sh <change> <repository> FIX
```

`OPS_MAX_FIX_ROUNDS` remains bounded at 3 by default. P2/P3 does not silently
become a release blocker. After a fix, return through VERIFY.

When no P0/P1 remains:

```text
./.agents/scripts/ops-runtime.sh phase <change> <session-id> FINAL_VERIFY
./.agents/scripts/run-phase-agent.sh <change> <repository> FINAL_VERIFY
```

Release requires successful derived FINAL_VERIFY evidence. Same-provider
process separation must explicitly state that provider independence is not
available; it may proceed only when all objective acceptance/test/security/
trading-safety evidence passes.

## RELEASE, DEPLOY_VERIFY, ARCHIVE

After FINAL_VERIFY gates pass, follow repository-delivery rules through local
commit, push, exact-SHA CI, deployment and production verification when scoped:

```text
./.agents/scripts/ops-runtime.sh phase <change> <session-id> RELEASE
./.agents/scripts/ops-runtime.sh phase <change> <session-id> DEPLOY_VERIFY
./.agents/scripts/ops-runtime.sh phase <change> <session-id> ARCHIVE
./.agents/scripts/ops-runtime.sh complete <change> <session-id>
```

Implementation defects found during RELEASE/DEPLOY_VERIFY return through the
atomic FIX path and fresh VERIFY/FINAL_VERIFY. External infrastructure blockers
become BLOCKED with evidence. Use centralized cleanup on terminal failure:

```text
./.agents/scripts/ops-runtime.sh cleanup <change> <session-id> <FAILED|BLOCKED>
```

Legacy active transactions that already persist `implementation_backend` and
`verification_mode` retain their old routes until terminal; do not migrate them
in place.
