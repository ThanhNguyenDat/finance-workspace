# Task: Finalize and Archive Completed Quant Promotion + Worker Routing Changes

## Repository

ThanhNguyenDat/finance-workspace

## Current reviewed main

65478ed3e11aa4607c0a2b37203821d04ef9b5d3
mark quant promotion delivery verified

## Review verdict before this task

P0: 0
P1: 1
P2: 1

Core architecture is accepted.

Do NOT redesign:

quant research
→ promotion gate
→ OpenSpec
→ OPS
→ Codex/Claude
→ CI/deploy
→ archive

Do not modify model routing, quota classification, backend immutability, promotion semantics, or FIX behavior unless strictly required to complete archival.

This task is lifecycle finalization only.

---

# Accepted Core Behavior — Preserve

Preserve all existing behavior:

* `docs/archive/legacy-handoff-agent.md` = legacy/non-authoritative only.
* `REJECTED / NO-CHANGE / DATA-ISSUE / NEEDS-MORE-RESEARCH` = research-only.
* `PROMOTE` = OpenSpec first → canonical OPS lifecycle.
* Same `<change>` identity across OpenSpec and OPS.
* `trace-origin` is PLAN-only, immutable, and stores research references only.
* IMPLEMENT = `gpt-5.6-luna`, reasoning `high`.
* FIX = `gpt-5.6-terra`, reasoning `high`.
* FIX model fallback = `gpt-5.6-sol`, reasoning `high`.
* Global Codex quota exhaustion → automatic `codex-off`.
* Generic HTTP 429 → no automatic `codex-off`.
* Active transaction backend is immutable.
* Atomic FIX behavior and max fix rounds remain unchanged.

---

# Problem 1 — Completed Promotion Change Still Looks Active

Current change:

`route-quant-promotions-through-ops`

has all tasks completed and latest CI green.

However it still exists under:

`openspec/changes/route-quant-promotions-through-ops/`

and:

`.ops/changes/route-quant-promotions-through-ops/`

The OPS handoff still contains stale wording equivalent to:

* Codex: implementing...
* Verification required...
* CI still pending...

even though delivery is already verified.

This violates the new traceability contract.

---

# Required Final State — Promotion OpenSpec

Archive:

`openspec/changes/route-quant-promotions-through-ops/`

to:

`openspec/changes/archive/2026-08-29-route-quant-promotions-through-ops/`

Use the native OpenSpec archive workflow where applicable.

Do not manually fake archive state if the native workflow can perform it correctly.

---

# Required OPS Finalization

Finalize the corresponding OPS transaction using the canonical OPS lifecycle.

Preferred lifecycle:

ARCHIVE
→ `ops-runtime.sh complete`
→ DONE

The final result should be:

`.ops/archive/2026-08-29-route-quant-promotions-through-ops/`

and it must no longer exist under:

`.ops/changes/`

Do not simply move files manually if the canonical `complete` operation can safely perform the transition.

Use the existing owner/session/lock-safe lifecycle where possible.

---

# Archived OPS Handoff

Update the archived handoff so it reflects reality.

It should contain concise final evidence equivalent to:

Change:
`route-quant-promotions-through-ops`

Status:
`DONE`

Delivery:
main contains implementation.

Verified HEAD:
`65478ed3e11aa4607c0a2b37203821d04ef9b5d3`

CI:

* workflow: Agent contracts
* run id: `33203126878`
* status: completed
* conclusion: success

Production deployment:
not applicable / not performed.

Use exact factual wording.

Do not claim production deployment if none occurred.

Remove stale wording equivalent to:

* implementing
* verification required
* pending CI

---

# Problem 2 — Stale Worker Routing OpenSpec Change

Current:

`openspec/changes/codex-worker-model-routing/`

has all tasks completed, including:

* implementation completed
* tests completed
* commit completed
* pushed to main
* exact SHA verified
* GitHub Actions green

but it still remains under the active OpenSpec namespace.

Archive it.

Preferred final path:

`openspec/changes/archive/2026-08-29-codex-worker-model-routing/`

Use native OpenSpec archive behavior.

Do not alter the accepted runtime implementation.

---

# Check Whether Matching OPS Transaction Exists

Inspect whether either of these exists:

`.ops/changes/codex-worker-model-routing/`

or a corresponding archived OPS transaction.

If an active terminal/complete OPS transaction exists:

* finalize/archive it correctly.

If no OPS transaction ever existed for that change:

* do NOT fabricate one.
* archive only the OpenSpec change.

Evidence before mutation.

---

# Active Namespace Invariant

After cleanup:

`openspec/changes/`

should contain only:

* `archive/`
* genuinely active changes

Completed changes must not remain active.

Likewise:

`.ops/changes/`

must contain only genuinely active/nonterminal execution records.

Terminal completed records belong under:

`.ops/archive/`

---

# Do Not Modify Research History

Do not rewrite or delete historical research under:

`raw/`

Do not migrate historical `docs/archive/legacy-handoff-agent.md` entries.

Its current banner:

`LEGACY / NON-AUTHORITATIVE`

must remain.

---

# Do Not Change Promotion Semantics

Do not change the classifications:

* REJECTED
* NO-CHANGE
* DATA-ISSUE
* NEEDS-MORE-RESEARCH
* PROMOTE

Do not change the promotion gate.

Do not change `trace-origin`.

Do not change approved research artifact roots.

---

# Do Not Change Worker Policy

Preserve exactly:

IMPLEMENT:

* model = `gpt-5.6-luna`
* reasoning effort = `high`

FIX:

* model = `gpt-5.6-terra`
* reasoning effort = `high`

FIX model fallback:

* model = `gpt-5.6-sol`
* reasoning effort = `high`

Do not change quota classifier behavior.

Do not change backend routing.

---

# Required Verification

Run:

```bash
bash -n .agents/scripts/ops-runtime.sh
bash -n .agents/scripts/quant-research-state.sh
bash -n .agents/scripts/classify-codex-result.sh
bash -n .agents/scripts/run-codex-phase.sh
bash -n .claude/hooks/ops-stop-hook.sh
```

Run all bounded suites:

```bash
./.agents/scripts/tests/test_ops_orchestration.sh
./.agents/scripts/tests/test_quant_research_state.sh
./.agents/scripts/tests/test_quant_research_contract.sh
./.agents/scripts/tests/test_quant_backend_routing.sh
./.agents/scripts/tests/test_codex_worker_policy.sh
./.agents/scripts/tests/test_quant_promotion_trace.sh
```

Then:

```bash
./.agents/scripts/sync-agent-links.sh
./.agents/scripts/sync-agent-links.sh --check

jq -e . .claude/settings.json

git diff --check
```

---

# OpenSpec Validation

Run strict validation using the installed valid command.

Example:

```bash
openspec validate --all --strict --no-interactive
```

or the exact installed equivalent.

After archive, verify there are no invalid active references.

---

# Archive Verification

Run:

```bash
find openspec/changes -maxdepth 2 -type d | sort
find .ops/changes -maxdepth 2 -type d | sort
find .ops/archive -maxdepth 2 -type d | sort
```

Expected:

`route-quant-promotions-through-ops`

must NOT remain active.

Expected archived OPS path:

`.ops/archive/2026-08-29-route-quant-promotions-through-ops/`

Expected archived OpenSpec path:

`openspec/changes/archive/2026-08-29-route-quant-promotions-through-ops/`

Expected:

`codex-worker-model-routing`

must NOT remain as an active completed OpenSpec change.

Expected archived OpenSpec path:

`openspec/changes/archive/2026-08-29-codex-worker-model-routing/`

---

# Regression Test Recommendation

Add a small bounded contract test only if the current suite does not catch this lifecycle mistake.

Useful invariant:

If a change has all delivery tasks completed and delivery evidence says verified, it must not remain in the active namespace.

Do not create a large generic lifecycle framework for this task.

A targeted assertion is sufficient.

---

# Git Delivery

After all checks pass:

```bash
git status
git diff --check
git log --oneline -10
```

Commit only lifecycle cleanup/finalization changes.

Suggested commit message:

```text
chore(ops): archive completed orchestration changes
```

Push:

```bash
git push origin main
```

No force push.

---

# Remote Verification

Verify:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main
```

They must match exactly.

---

# GitHub Actions

Verify the exact final pushed SHA.

Required:

* workflow: Agent contracts
* status = completed
* conclusion = success

Do NOT rely on previous run `33203126878` for the final cleanup commit.

A new exact-SHA green run is required.

---

# Acceptance Criteria

Complete only when all are true:

1. `route-quant-promotions-through-ops` is no longer under active OpenSpec.
2. It is archived under dated OpenSpec archive.
3. Its OPS transaction is no longer under `.ops/changes`.
4. Its OPS transaction is archived under dated `.ops/archive`.
5. Archived OPS state is `DONE`.
6. Archived handoff reflects final verified state.
7. Archived handoff no longer says implementation/verification is pending.
8. Exact verified SHA is recorded correctly.
9. Previous CI evidence is recorded correctly where useful.
10. No false production deployment claim is made.
11. `codex-worker-model-routing` is no longer an active completed OpenSpec change.
12. Matching OPS transaction for worker-routing is finalized only if one actually exists.
13. No fake OPS transaction is created.
14. `docs/archive/legacy-handoff-agent.md` remains legacy/non-authoritative.
15. Promotion gate remains unchanged.
16. `trace-origin` remains unchanged.
17. Luna/Terra/Sol worker routing remains unchanged.
18. Quota classifier remains unchanged.
19. Backend immutability remains unchanged.
20. Atomic FIX remains unchanged.
21. Existing orchestration tests pass.
22. Existing quant tests pass.
23. Worker policy tests pass.
24. Promotion trace tests pass.
25. Strict OpenSpec validation passes.
26. Agent Contracts CI passes on exact final SHA.
27. Local HEAD equals remote main.

---

# Final Report

Return:

## Verdict

PASS / BLOCKED / FAILED

## Active OpenSpec

Show all remaining active changes.

## Archived OpenSpec

Show whether these exist:

* `2026-08-29-route-quant-promotions-through-ops`
* `2026-08-29-codex-worker-model-routing`

## Active OPS

Show all remaining active OPS changes.

## Archived OPS

Show:

`2026-08-29-route-quant-promotions-through-ops`

and its final status.

## Handoff

Show concise final status and evidence.

## Tests

List exact commands and results.

## CI

Show:

* run id
* head SHA
* status
* conclusion

for the final pushed SHA.

## Git

Show:

* local HEAD
* remote main

## Remaining Limitations

Only real limitations.

Do not add unrelated architecture changes.
