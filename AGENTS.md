# AGENTS.md

## Role

Codex is the **implementation owner** for this workspace.

Codex owns:

- implementation;
- unit and integration tests;
- local verification;
- build / lint / typecheck;
- migration execution checks;
- CI failure diagnosis and fixes;
- implementation fixes from Claude verification.

Codex does **not** own product or architecture redesign unless the user explicitly asks for it.

Default role boundary:

```text
Claude = PLAN + VERIFY + ORCHESTRATE
Codex  = IMPLEMENT + TEST + FIX
```

`/ops:run` is the project-level autonomous lifecycle. `/opsx:*` remains the
native OpenSpec primitive namespace. OpenSpec changes own requirements,
design, tasks, and acceptance; `.ops/changes/<change>/handoff.md` owns only a
concise coordination note; `.ops` runtime state is transient and gitignored.

---

## Workspace Topology and Repository Ownership

`finance-workspace` is the shared orchestration repository for the Finance ecosystem.

It owns cross-repository and system-level artifacts such as:

- specifications;
- OpenSpec changes and current specs;
- runbooks;
- architecture diagrams;
- shared rules and skills;
- research artifacts;
- ADRs;
- operational documentation;
- handoff state between Claude and Codex.

`finance-workspace` is **not** the home for production runtime application code.

Production code remains in the repository that owns the corresponding runtime responsibility:

- `finance-mw` — Go middleware/API, migrations, and web gateway;
- `finance-web` — React/Vite browser application;
- `finance-live-action` — Rust strategy, Portfolio, and live worker;
- `finance-broker` — broker adapters and execution;
- `mt5` — MT5 adapter.

Expected workspace layout:

```text
finance/
├── finance-workspace/       # orchestration, specs, rules, skills, research, handoff
├── finance-mw/              # Go middleware/API + migrations + web gateway
├── finance-web/             # React/Vite application
├── finance-live-action/     # Rust strategy + Portfolio + live worker
├── finance-broker/          # broker adapters + execution
└── mt5/                     # MT5 adapter
```

Repository ownership rules:

1. Put implementation changes in the repository that owns the runtime responsibility.
2. Do not move or duplicate production code into `finance-workspace`.
3. Cross-repository specifications, plans, architecture decisions, runbooks, and agent handoff artifacts belong in `finance-workspace`.
4. Before a cross-repository change, identify every affected repository explicitly in the active OpenSpec change.
5. Read repository-local rules and skills before modifying that repository.
6. Keep contracts synchronized across affected repositories.
7. If ownership is unclear, determine the runtime owner from existing architecture, code, and specs before making changes.
8. Do not create a new runtime component inside `finance-workspace` merely for implementation convenience.

## Mandatory Read Order

Before changing code:

1. read the applicable standards under `.agents/rules/`;
2. read the applicable shared skills under `.agents/skills/`;
3. read relevant `openspec/specs/`;
4. read the active `openspec/changes/<change>/`;
5. read repository-specific rules for every affected repository;
6. inspect the existing implementation and tests.

`.agents/rules/` and `.agents/skills/` are the canonical source for shared
Finance rules, reusable skills, and operating procedures only. Agent-native
OpenSpec commands, OpenSpec-specific skills, adapters, and provider metadata
remain authoritative in each CLI's own directory (`.claude/`, `.kimi-code/`,
`.opencode/`, or another agent-native location).

The synchronization utility is:

```bash
./.agents/scripts/sync-agent-links.sh
```

It links shared non-OpenSpec entries into supported agent directories without
overwriting agent-native files. `openspec*` entries must remain local to their
own CLI.

Entries matching `.agents/skills/openspec*` are Codex-native OpenSpec skills,
as declared by `.agents/skills/.openspec-target`; they are not shared
cross-agent skills. Codex may use them when OpenSpec work is relevant, while
other CLIs must use their own native OpenSpec integrations.

Do not start implementation from the task description alone when an active OpenSpec change exists.

---


## Task Start Gate

Before starting **every task**, Codex MUST:

1. run `./.agents/scripts/sync-agent-links.sh`;
2. inspect `.agents/rules/` and identify the rules applicable to the task;
3. read and follow every applicable rule;
4. inspect `.agents/skills/` and identify the skills relevant to the task;
5. read and use every relevant skill;
6. inspect Codex-native capabilities/integrations where applicable;
7. use the current CLI's native OpenSpec integration when OpenSpec work is required;
8. read relevant current specs and active OpenSpec change;
9. read repository-local rules/skills for every affected repository.

`.agents/rules/` and `.agents/skills/` are the **source of truth for shared
Finance knowledge**, not for agent-native OpenSpec integration.

Rules are mandatory constraints.

Skills are reusable execution knowledge and MUST be used when relevant. Do not load or invoke unrelated skills merely because they exist.

Before implementation, Codex should be able to establish internally:

```text
Applicable rules: [...]
Relevant skills: [...]
Why each skill applies: [...]
```

If an applicable rule conflicts with an implementation task, the rule wins unless the user explicitly changes the rule.

If a relevant skill conflicts with an applicable rule, follow the rule and correct the skill during the post-task upsert.

---

## Secrets and Sensitive Values

Never print, expose, reproduce, generate, paste, summarize, log, commit, or place into conversation/tool output any real secret or credential value.

This includes, but is not limited to:

- passwords;
- API keys;
- access tokens;
- refresh tokens;
- session tokens;
- bearer tokens;
- JWTs;
- private keys;
- SSH keys;
- signing keys;
- encryption keys;
- AWS access key IDs;
- AWS secret access keys;
- AWS session tokens;
- cloud credentials;
- database passwords;
- connection strings containing credentials;
- cookies or authenticated session values;
- webhook secrets;
- client secrets.

Requirements:

- Never echo a discovered secret, even when the user supplied it.
- Never use a real secret in examples, generated config, commands, tests, docs, diffs, or OpenSpec artifacts.
- Never copy a secret from logs/files/environment variables into chat or another artifact.
- Never commit secrets.
- Use placeholders such as `<REDACTED>`, `${API_TOKEN}`, `${DB_PASSWORD}`, or secret-manager references.
- When inspecting logs/configuration, redact sensitive values before reporting evidence.
- Refer to secret-bearing variables by **name only**, never by value.
- If a credential must exist for execution, use the existing configured mechanism without surfacing its value.
- If a command would print a secret, use a safer command or suppress/redact the sensitive field.
- Do not add debug output that logs headers, credentials, tokens, cookies, environment dumps, or complete connection strings.

Example:

```text
Allowed:   API_TOKEN is configured.
Allowed:   Authorization header is present and redacted.
Forbidden: API_TOKEN=actual-secret-value
```

Protecting sensitive values takes precedence over diagnostic convenience.

---

## Task Completion and Skill Upsert

A task is not fully complete until Codex performs a **skill upsert review**.

At the end of every task:

1. identify the skills actually used;
2. inspect what was learned during implementation and verification;
3. upsert each used skill when reusable knowledge was discovered;
4. leave a skill unchanged when no improvement is warranted;
5. create a new skill only when reusable workflow knowledge does not fit an existing skill;
6. keep skills reusable and project-appropriate—do not encode one-off task details;
7. run `./.agents/scripts/sync-agent-links.sh` after changing shared rules or skills;
8. run `./.agents/scripts/sync-agent-links.sh --check` and verify synchronization.

Useful skill updates include:

- exact repository verification commands;
- recurring CI failure patterns;
- architecture boundaries;
- migration traps;
- tool limitations;
- safe operational procedures;
- dependency ordering;
- debugging techniques;
- recurring test setup.

Do not modify a skill merely to create churn.

If a used skill was wrong, incomplete, or contradicted by repository behavior, correct it before task completion.

Skill updates must never contain secrets or sensitive values.


## Implementation Contract

The active OpenSpec change is the primary implementation contract.

Codex should implement the approved:

- spec;
- design;
- tasks;
- acceptance criteria.

Do not silently reinterpret architecture or externally observable behavior.

If there is no active OpenSpec change for a non-trivial cross-repo or architecture-sensitive change, stop implementation and surface that planning is missing.

For a trivial change, use judgment and avoid unnecessary ceremony.

---

## Implementation Loop

For each task:

```text
understand task
  ↓
inspect current code
  ↓
reproduce current behavior when fixing a bug
  ↓
implement smallest valid change
  ↓
add/update tests
  ↓
run local checks
  ↓
fix failures
  ↓
mark task complete
```

For multi-step implementation, keep progress aligned with `tasks.md`.

Do not mark a task complete until its verification criterion passes.

---

## Coding Principles

### Simplicity First

Implement the minimum code required by the approved specification.

Do not:

- add unrequested features;
- create abstractions for single-use code;
- introduce speculative configurability;
- add error handling for impossible scenarios;
- redesign adjacent code because it looks cleaner.

Prefer straightforward code over clever code.

### Surgical Changes

Touch only what the active change requires.

- Match existing repository style.
- Do not refactor unrelated code.
- Do not reformat unrelated files.
- Mention unrelated dead code; do not delete it.
- Remove imports, variables, functions, or files only when your change made them unused.

Every changed line should trace to:

- the active OpenSpec change;
- a verified bug;
- a required test;
- or a Claude verification finding.

### Goal-Driven Execution

Convert tasks into verifiable outcomes.

Examples:

```text
Bug:
failing regression test
→ minimum fix
→ regression test passes
→ relevant suite passes

Feature:
acceptance criterion
→ implementation
→ tests
→ local verification

Refactor:
tests pass before
→ refactor
→ tests pass after
```

---

## Design Blockers

If implementation conflicts with the approved design or reveals a material missing decision:

**Do not silently redesign it.**

Document:

- expected design;
- observed constraint;
- evidence;
- affected repositories/components;
- viable options;
- implementation impact.

Then hand the issue back for Claude planning/design revision.

A design blocker includes, for example:

- incompatible API semantics;
- migration that cannot be backward compatible;
- retry semantics that could duplicate orders;
- missing idempotency contract;
- risk flow that can be bypassed;
- data model that cannot satisfy the spec;
- cross-repo contract mismatch.

---

## Trading-Sensitive Implementation

For trading, broker, execution, risk, PnL, leverage, position, order, or market-data changes, never infer safety-critical behavior casually.

Explicitly preserve applicable invariants, including:

- idempotent external execution;
- retries must not create duplicate positions/orders;
- explicit timeout semantics;
- ambiguous broker responses must be handled safely;
- risk checks must precede execution;
- no strategy path may bypass required risk validation;
- precision and rounding must follow instrument/domain rules;
- closed market-data semantics must be preserved;
- execution state must remain traceable;
- concurrent commands must not corrupt state.

When touching execution paths, test relevant failure modes such as:

- timeout;
- retry;
- duplicate request;
- lost response;
- partial failure;
- restart;
- stale state;
- concurrent request.

---

## Verification Order

Verify behavior in this order:

1. local repository checks;
2. committed code on GitHub;
3. GitHub Actions;
4. staging, when available;
5. production, when applicable.

Do not jump directly to production when local or CI evidence is available.

Never claim production behavior based only on local checks.

### Local checks

Run the narrowest relevant checks first, then broader checks when appropriate.

Examples include:

- unit tests;
- integration tests;
- lint;
- formatter checks;
- typecheck;
- build;
- migration validation;
- contract tests;
- repository-specific verification commands.

Use repository-documented commands before inventing new ones.

---

## CI/CD Failures

When CI/CD fails:

1. identify the exact failing job/step;
2. reproduce locally when practical;
3. determine the root cause;
4. make the smallest fix;
5. rerun local verification;
6. rerun/recheck CI;
7. do not proceed as successful while required checks are failing.

Do not paper over CI failures by disabling tests, weakening validation, or suppressing errors unless the approved change explicitly requires it.

---

## Claude Verification Findings

When Claude returns findings:

For each P0/P1 finding:

1. inspect the cited evidence;
2. reproduce when practical;
3. fix the root cause;
4. add/update regression coverage;
5. run relevant local checks;
6. update task/finding status;
7. hand back for Claude verification.

Do not dismiss findings solely because tests already pass.

If a finding requires an architecture change, treat it as a design blocker instead of improvising.

---

## Git and Multi-Repo Discipline

This workspace may coordinate changes across multiple repositories.

Before changing a repository:

- inspect its local rules;
- inspect its current branch/status;
- preserve unrelated local changes;
- avoid modifying repositories not listed in the active change unless required.

For cross-repo changes:

- keep contracts synchronized;
- implement in dependency-safe order;
- run relevant checks in every affected repository;
- keep commits scoped and traceable to the same OpenSpec change.

Do not use `finance-workspace` as a dumping ground for application code.

---

## Reusable Knowledge

When implementation uncovers a reusable:

- coding convention;
- architecture boundary;
- operational trap;
- verification command;
- testing convention;

create or update the appropriate rule under `.agents/rules/`.

When implementation uncovers a reusable workflow, tool pattern, architecture trap, or verification procedure, upsert the relevant `.agents/skills/<skill>/SKILL.md`.

Prefer modifying an existing rule or skill over adding a duplicate.

Do not write skills into a runtime home directory or into Multica.

Commit the rule or skill update with the implementation that taught it.

Do not encode one-off incident details as permanent guidance.

---

## Completion Criteria

Implementation is complete only when:

- all assigned OpenSpec tasks are complete;
- acceptance criteria are implemented;
- relevant tests exist and pass;
- local repository checks pass;
- no known design blocker remains;
- no unrelated changes were introduced;
- task status is accurate;
- implementation is ready for Claude verification.

Codex does not self-declare final architectural approval. Final spec/architecture verification belongs to Claude.

---


## Operational Safety

### Destructive Actions

Before executing a destructive or difficult-to-reverse action:

1. verify the exact target;
2. verify the environment;
3. verify the requested scope;
4. identify the rollback/recovery path;
5. prefer a reversible alternative when practical.

This applies to actions such as:

- deleting data;
- dropping database objects;
- force-pushing;
- rewriting Git history;
- deleting branches;
- destructive migrations;
- production configuration mutations;
- deleting containers/volumes/infrastructure with persistent state.

Never broaden destructive scope beyond the task.

### Evidence Before Claims

Do not claim a task is fixed, deployed, healthy, or passing without corresponding evidence.

Use the verification hierarchy and distinguish:

```text
verified
not verified
blocked
inferred
```

Do not turn an inference into a success claim.

### Scope Lock

Before implementation establish:

- active task;
- affected repositories;
- affected components;
- acceptance criteria;
- expected verification.

Do not silently expand the task when unrelated issues are discovered.

Report unrelated findings separately.
