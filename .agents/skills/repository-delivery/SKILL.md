---
name: repository-delivery
description: Commit, push, monitor, deploy, and verify Finance repository changes through bounded local checks, exact-SHA GitHub Actions, immutable images, Coolify, and final production evidence. Use for repository delivery or authorized infrastructure reconciliation.
---

# Repository Delivery

Deliver the exact reviewed revision through the lane that owns the target
state, while preserving OpenSpec/OPS traceability and unrelated local changes.

## Inputs and output

Input is an approved change, affected repositories, required checks, delivery
authorization, and rollback boundary. Output is scoped commits plus exact-SHA
local, CI, deployment, and production evidence—or one explicit blocker.

## Choose the lane

- Repository-owned code/configuration: validate, commit, push, CI-build an
  immutable image, let Coolify deploy, then verify production.
- Host-only infrastructure state: inventory and back up, apply a guarded
  live-first mutation, verify it, then reconcile durable repository source.
- Respect an owner-held push gate; local success never implies push approval.

## Delivery workflow

1. Read repository rules, inspect status, fetch current `main`, and preserve
   unrelated changes.
2. Run narrow checks first, then required bounded suites and build checks.
3. Review and commit explicit paths; fetch again and require fast-forward push.
4. Locate CI by exact SHA and monitor each long run with one detached watcher.
5. Deploy only when applicable, then verify immutable identity, behavior,
   data/progress, observability, host safety, and rollback readiness.
6. Record concise evidence in OpenSpec/OPS; legacy handoff is non-authoritative.

## Detailed guidance

Read [references/playbook.md](references/playbook.md) for lane-specific safety,
the owner-held gate, watcher commands, Coolify and production checks,
infrastructure/Grafana handling, database/contracts, and the completion report.
Read only the sections required by the chosen lane.
