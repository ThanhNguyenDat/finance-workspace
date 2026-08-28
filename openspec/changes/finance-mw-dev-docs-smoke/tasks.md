# Task: First Real Dev-Only Smoke Test for `/ops:run`

Run this as the first real end-to-end validation of the autonomous Finance orchestration workflow.

Use:

```text
/ops:run
```

Do not manually bypass the orchestration helpers.

## Goal

Validate the real workflow behavior end-to-end using a deliberately small, low-risk, development-only change.

The purpose is to verify the orchestration system itself:

```text
Claude PLAN
→ OpenSpec
→ Codex IMPLEMENT
→ Claude VERIFY
→ optional Codex FIX
→ FINAL_VERIFY
→ dev-only ARCHIVE
→ DONE
```

This is **not** a production deployment test.

---

# Change Request

Implement a small developer-only documentation improvement in:

```text
finance-mw
```

Add a new section to its developer documentation explaining how to run the service locally and verify that the service is healthy.

Use existing repository conventions and actual commands/configuration found in the repository.

Do not invent commands.

The documentation should cover, when applicable:

```text
how to start the service locally
required local dependencies
where configuration/environment values come from
how to run the relevant tests
how to verify the service starts successfully
how to check the local health/readiness endpoint if one exists
```

Keep the change concise.

Do not modify runtime application behavior.

Do not change APIs, schemas, migrations, dependencies, Docker topology, deployment configuration, CI/CD behavior, or production settings.

---

# Scope

Expected runtime repository:

```text
finance-mw
```

Expected orchestration repository:

```text
finance-workspace
```

Allowed changes:

```text
finance-workspace/
  openspec/changes/<change>/
  .ops/changes/<change>/
  required orchestration state/evidence

finance-mw/
  existing developer documentation only
```

Do not modify unrelated repositories.

---

# Mandatory `/ops:run` Flow

Use the existing orchestration contract mechanically.

## 1. PLAN

Derive one stable kebab-case OpenSpec change name.

Acquire:

```text
change lock
runtime state
finance-mw repo lock
```

before any planning or repository write according to the existing contract.

Perform read-only discovery first where allowed.

Inspect:

```text
finance-workspace/AGENTS.md
finance-workspace/CLAUDE.md
applicable shared rules and skills
finance-mw repository-local instructions
existing finance-mw docs
actual Makefile/scripts/docker-compose/configuration
```

Determine the real local-development commands from repository evidence.

Do not guess them.

Create the OpenSpec planning artifacts using the native OpenSpec integration.

The change must explicitly state:

```text
documentation-only
dev-only
no production deployment
no runtime behavior change
```

Validate the OpenSpec change.

---

## 2. IMPLEMENT

Transition to:

```text
IMPLEMENT
```

Invoke the real Codex worker through:

```text
.agents/scripts/run-codex-phase.sh
```

Do not manually edit the target documentation as Claude.

Codex owns the implementation.

Codex must:

```text
read the OpenSpec change
read applicable instructions
inspect actual repository commands
modify only the relevant finance-mw developer documentation
run appropriate lightweight verification
not push
```

---

## 3. VERIFY

After Codex completes:

```text
phase → VERIFY
```

Claude must independently inspect:

```text
actual git diff
actual documentation content
repository commands referenced by the documentation
scope
unexpected files
local verification evidence
```

Do not rely on the Codex summary.

Specifically verify that every documented command actually exists in the repository or is otherwise supported by repository evidence.

Check that the change did not modify runtime code.

---

## 4. FIX LOOP

If Claude finds a P0/P1 issue:

```text
fix <change> <session-id>
```

must be used.

Do not enter FIX through generic `phase`.

Then:

```text
Codex FIX
→ VERIFY
```

Respect:

```text
OPS_MAX_FIX_ROUNDS=3
```

Do not artificially trigger a fix if the implementation is already correct.

The smoke test is valid whether zero or more legitimate fix rounds are needed.

---

## 5. FINAL_VERIFY

When no P0/P1 findings remain:

```text
phase → FINAL_VERIFY
```

Repeat the critical checks.

Required final evidence:

```text
documentation matches repository reality
no runtime application behavior changed
no unrelated repository modified
OpenSpec acceptance criteria satisfied
git diff is clean from whitespace/errors
```

---

# Dev-Only Release Behavior

This smoke test must **not deploy production**.

Do not:

```text
deploy
restart production services
modify production config
call production mutation endpoints
change production infrastructure
```

This is explicitly a dev-only workflow.

After successful FINAL_VERIFY, record release/deployment as:

```text
not applicable / intentionally skipped
```

according to the existing `/ops:run` state-machine contract.

Use the valid dev-only transition path.

Do not fake:

```text
RELEASE PASS
DEPLOY_VERIFY PASS
```

if those phases are not applicable.

---

# Archive

After successful final verification:

```text
phase → ARCHIVE
```

Use native OpenSpec sync/archive behavior as required.

Then:

```bash
./.agents/scripts/ops-runtime.sh complete <change> <session-id>
```

Expected final state:

```text
DONE
```

---

# Mandatory Post-Run Evidence

Before reporting success, verify all of the following.

## Runtime state

```text
archived state = DONE
```

## Locks

```text
change lock = absent
finance-mw repo lock owned by this workflow = absent
```

## OpenSpec

Verify the change was archived correctly.

## Repository scope

Show:

```bash
git -C finance-workspace status --short
git -C finance-mw status --short
```

and confirm no unexpected repository was modified.

## Git evidence

Show the relevant:

```bash
git -C finance-mw diff --check
git -C finance-mw log --oneline -5
```

If Codex created a local commit as required by repository rules, report its SHA.

Do not push the runtime repository unless the existing approved dev-only workflow explicitly requires it.

For this first smoke test, prefer:

```text
no production push/deploy
```

unless repository policy mechanically requires a harmless documentation push.

---

# Orchestration Evidence

Report evidence that the orchestration itself actually worked.

Include:

```text
change name
session id
affected repo
initial phase
Codex IMPLEMENT invocation result
number of FIX rounds
Claude VERIFY result
FINAL_VERIFY result
final archived state
lock cleanup result
```

Do not expose secrets or raw environment dumps.

---

# Important Failure Behavior

If any orchestration mechanism fails, do not work around it manually.

Examples:

```text
change lock failure
repo lock failure
Codex invocation failure
wrong cwd
Codex cannot access OpenSpec
Codex cannot write finance-mw
invalid state transition
Stop hook failure
OpenSpec validation failure
lock cleanup failure
```

Treat that as a smoke-test finding.

Record the evidence and stop with:

```text
BLOCKED
```

or:

```text
FAILED
```

as appropriate.

Do not manually finish the documentation change just to make the task appear successful.

The purpose is to test `/ops:run`, not merely produce documentation.

---

# Success Criteria

The smoke test passes only if:

1. `/ops:run` creates and owns the change correctly;
2. OpenSpec planning is created successfully;
3. only `finance-mw` is selected as the runtime implementation repo;
4. Codex is invoked for IMPLEMENT;
5. Codex can read the central OpenSpec change;
6. Codex can modify the sibling `finance-mw` repo;
7. Claude independently verifies the actual diff;
8. any FIX uses atomic `fix()`;
9. FINAL_VERIFY passes;
10. no production deployment occurs;
11. OpenSpec is archived;
12. `.ops` workflow is completed;
13. final state is `DONE`;
14. change lock is released;
15. finance-mw repo lock is released;
16. no unrelated files/repos are modified;
17. the final report contains concrete evidence rather than claims.

---

# Final Report Format

Return:

## Smoke Test

```text
PASS / BLOCKED / FAILED
```

## Change

```text
change name:
runtime repo:
scope:
```

## Workflow

```text
PLAN             PASS/FAIL
IMPLEMENT        PASS/FAIL
VERIFY           PASS/FAIL
FIX rounds       N
FINAL_VERIFY     PASS/FAIL
ARCHIVE          PASS/FAIL
DONE             YES/NO
```

## Codex

Show:

```text
worker invoked: yes/no
target repository:
exit result:
evidence path:
```

Do not print sensitive log contents.

## Verification

Summarize the actual diff and checks performed by Claude.

## Locks

```text
change lock remaining: yes/no
repo lock remaining: yes/no
```

## Git

Show relevant local commit SHA if one exists.

## Deployment

Must state:

```text
production deployment: NOT PERFORMED
```

## Findings

List only real orchestration or implementation findings.

Do not add new orchestration features during this smoke test.
