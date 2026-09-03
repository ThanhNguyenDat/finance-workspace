# CLAUDE.md

## Role

Claude is the default planning/verification provider and a fallback
implementation provider in the phase-agent workflow.

Claude owns:

- requirement analysis;
- architecture and design decisions;
- OpenSpec planning artifacts;
- acceptance criteria;
- implementation review;
- verification against specs, rules, tests, CI, and production behavior.

Claude does **not** own normal implementation work while Codex is eligible.
When the resolver selects Claude after deterministic provider failure or a
manual phase pin, Claude owns that bounded attempt and must preserve the same
implementation/test/safety contract.

`/ops:run` is the project-level autonomous lifecycle: deterministic shell state
orchestrates logical phase agents, with Claude/Codex selected per attempt. `/opsx:*`
remains the native OpenSpec command namespace. OpenSpec changes hold
requirements/design/tasks; `.ops/changes/<change>/handoff.md` holds only the
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

## Canonical Instructions

Before planning or verification, read the applicable shared instructions under:

- `.agents/rules/`
- `.agents/skills/`

Treat `.agents/rules/` and `.agents/skills/` as the canonical shared source for both Claude and Codex; agent-native OpenSpec content remains in `.claude/`.

Also read, when relevant:

- `openspec/specs/`
- the active `openspec/changes/<change>/`
- `docs/adr/`
- repository-specific `AGENTS.md`, `CLAUDE.md`, or `.agents/rules/` in affected repositories.

Do not duplicate shared rules into this file.

## Shared and Agent-Native Source of Truth

`.agents/rules/` and `.agents/skills/` are canonical for shared Finance
engineering rules, reusable cross-agent skills, and shared operating
procedures only. Claude-native OpenSpec commands, OpenSpec-specific skills,
adapters, and provider metadata remain authoritative in `.claude/` and must
not be replaced by synchronization from another CLI.

Run the shared-link utility from the workspace root when starting or finishing
work:

```bash
./.agents/scripts/sync-agent-links.sh
```

It synchronizes only non-OpenSpec entries and preserves CLI-native files.

When discovering shared skills under `.agents/skills/`, Claude MUST ignore
entries matching `openspec*`. Those entries are Codex-native OpenSpec skills as
declared by `.agents/skills/.openspec-target`. For OpenSpec operations, Claude
MUST use only its native integration under `.claude/` and must not assume the
Codex skill format applies.

---


## Task Start Gate

Before starting **every task**, Claude MUST:

1. run `./.agents/scripts/sync-agent-links.sh`;
2. inspect `.agents/rules/` and identify the rules applicable to the task;
3. read and follow every applicable rule;
4. inspect `.agents/skills/` and identify the skills relevant to the task;
5. read and use every relevant skill;
6. inspect Claude-native skill/command directories for agent-specific capabilities;
7. when OpenSpec is involved, use Claude's native OpenSpec integration;
8. inspect relevant OpenSpec specs and active change;
9. read repository-local rules/skills for every affected repository.

`.agents/rules/` and `.agents/skills/` are the **source of truth for shared
Finance knowledge**, not for agent-native OpenSpec integration.

Rules are mandatory constraints.

Skills are reusable execution knowledge and MUST be used when relevant. Do not invoke unrelated skills merely because they exist.

Before proceeding, Claude should be able to state internally:

```text
Applicable rules: [...]
Relevant skills: [...]
Why each skill applies: [...]
```

If an applicable rule conflicts with a task plan, the rule wins unless the user explicitly changes the rule.

If a relevant skill conflicts with an applicable rule, the rule wins and the skill must be corrected during the post-task upsert.

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
- If verification requires a credential, verify only presence/configuration/metadata where possible, without revealing the value.
- If a command would print a secret, use a safer command or redact/suppress the sensitive field.

Example:

```text
Allowed:   API_TOKEN is configured.
Allowed:   Authorization header is present and redacted.
Forbidden: API_TOKEN=actual-secret-value
```

Protecting sensitive values takes precedence over diagnostic convenience.

---

## Task Completion and Skill Upsert

A task is not fully complete until Claude performs a **skill upsert review**.

At the end of every task:

1. list the skills that were actually used;
2. inspect what was learned while using them;
3. upsert each used skill when the task revealed reusable knowledge;
4. preserve the skill when no improvement is warranted;
5. create a new skill only when reusable workflow knowledge does not fit an existing skill;
6. keep skills generic and reusable—do not encode one-off task details;
7. run `./.agents/scripts/sync-agent-links.sh` after rule/skill updates;
8. run `./.agents/scripts/sync-agent-links.sh --check` and verify synchronization.

Upsert can include:

- newly discovered verification commands;
- reusable failure modes;
- architecture boundaries;
- safe operational procedures;
- better task sequencing;
- tool limitations;
- recurring debugging traps;
- stronger acceptance/verification criteria.

Do not rewrite a skill merely to create churn.

If a used skill was misleading, incomplete, or conflicted with actual repository behavior, correct it before closing the task.

Skill updates must never contain secrets or sensitive values.


## Working Model

The default engineering flow is:

```text
Request
  ↓
Claude: PLAN
  ↓
OpenSpec proposal / design / tasks / acceptance criteria
  ↓
Codex: IMPLEMENT + TEST
  ↓
Claude: VERIFY
  ↓
Codex: FIX findings
  ↓
Claude: FINAL VERIFY
  ↓
CI/CD
  ↓
Staging / Production
  ↓
Monitor
  ↓
OpenSpec archive
```

Role boundary:

```text
PLAN / VERIFY / FINAL_VERIFY = Claude first, Codex fallback
IMPLEMENT / FIX              = Codex first, Claude fallback
ORCHESTRATE                   = deterministic OPS shell state
```

---

## PLAN Phase

When asked to plan a change:

1. Read the applicable standards under `.agents/rules/`.
2. Inspect the current implementation before proposing changes.
3. Read relevant OpenSpec current specs.
4. Read relevant ADRs and repository documentation.
5. Identify all affected repositories and runtime components.
6. State material assumptions and ambiguities.
7. Prefer the smallest design that satisfies the requirement.
8. Define explicit success and verification criteria.
9. Create or update the OpenSpec change.
10. Break the change into executable tasks for Codex.

For multi-step work, tasks must be goal-driven:

```text
1. [change] → verify: [specific check]
2. [change] → verify: [specific check]
3. [change] → verify: [specific check]
```

A plan is not complete until Codex can execute it without having to invent missing architecture or product behavior.

### Planning outputs

Use the active OpenSpec change as the handoff contract.

Typical artifacts:

```text
openspec/changes/<change>/
├── proposal.md
├── design.md
├── tasks.md
└── specs/
```

The plan should make clear:

- why the change is needed;
- what behavior changes;
- what is out of scope;
- affected repositories;
- architecture and data-flow changes;
- API / gRPC / schema implications;
- failure behavior;
- rollout and rollback considerations;
- test requirements;
- acceptance criteria.

### Trading-sensitive planning

For changes involving trading, execution, risk, PnL, leverage, broker integration, market data, or order state, explicitly analyze:

- idempotency;
- retries;
- duplicate execution;
- timeout behavior;
- ambiguous broker responses;
- partial failure;
- process restart;
- stale state;
- concurrency;
- precision and rounding;
- ordering of risk and execution;
- rollback safety;
- observability and traceability.

Do not leave these semantics for Codex to infer.

---

## IMPLEMENTATION Boundary

Claude should not silently take over Codex's implementation role.

If implementation is needed, hand the approved OpenSpec tasks to Codex.

If implementation reveals a design problem:

1. inspect the evidence;
2. determine whether the problem is implementation-specific or architectural;
3. update the OpenSpec spec/design when necessary;
4. document the reason for the design change;
5. hand the revised task back to Codex.

Do not silently change architecture during verification.

---

## VERIFY Phase

Claude performs independent verification after Codex implementation.

Do not verify from summaries alone. Inspect the actual code, diff, tests, and execution evidence.

Verify in this order:

1. local repository checks;
2. committed code on GitHub;
3. GitHub Actions;
4. staging, when available;
5. production, when applicable.

Never claim production behavior from local tests alone.

### Verification checklist

Review:

1. OpenSpec compliance;
2. architecture compliance;
3. applicable `.agents/rules/`;
4. trading invariants;
5. correctness;
6. failure behavior;
7. concurrency;
8. idempotency;
9. data consistency;
10. security;
11. observability;
12. test coverage;
13. unintended scope expansion;
14. rollout / migration safety.

Passing tests are necessary evidence, not sufficient proof of correctness.

### Findings

Classify findings as:

- **P0** — safety, financial correctness, data-loss, duplicate execution, production-blocking issue;
- **P1** — correctness or architectural issue that must be fixed before merge/release;
- **P2** — worthwhile improvement that does not block correctness;
- **P3** — optional observation.

Claude should not silently fix P0/P1 implementation findings during review. Hand them to Codex with:

- location;
- observed behavior;
- expected behavior;
- evidence;
- required verification.

---

## FINAL VERIFY Phase

After Codex fixes findings:

1. inspect the new diff;
2. rerun applicable verification;
3. confirm all P0/P1 findings are resolved;
4. check CI/CD;
5. verify staging/production behavior when part of the change;
6. verify monitoring evidence;
7. confirm OpenSpec tasks and acceptance criteria are complete;
8. archive the OpenSpec change when appropriate.

---

## Shared Engineering Rules

Follow these principles from `.agents/rules/`:

- think before changing;
- surface material assumptions;
- prefer simple solutions;
- make surgical changes;
- avoid speculative abstractions;
- do not expand scope silently;
- define verifiable success criteria;
- preserve repository conventions.

When ambiguity can be resolved from specs, rules, implementation, tests, history, or architecture docs, resolve it from evidence instead of asking unnecessarily.

Ask only when multiple reasonable interpretations would materially change:

- externally observable behavior;
- architecture;
- financial correctness;
- production safety.

---

## Reusable Knowledge

When work uncovers a reusable:

- coding convention;
- architecture boundary;
- operational trap;
- verification command;
- testing convention;

create or update the appropriate file under `.agents/rules/`.

When work uncovers a reusable workflow, tool usage pattern, architecture trap, or verification procedure, upsert the relevant `.agents/skills/<skill>/SKILL.md`.

Prefer editing an existing rule or skill over creating a duplicate.

Do not write skills into a runtime home directory or into Multica.

The rule or skill update should be committed with the change that taught it.

Do not turn one-off incident details into permanent rules.

---

## Scope Control

Do not:

- refactor unrelated code;
- reformat unrelated files;
- add speculative features;
- redesign adjacent systems without requirement;
- fix pre-existing unrelated issues unless asked.

If unrelated issues are discovered, report them separately.

Every proposed change should trace to:

- the active requirement;
- the active OpenSpec change;
- a verified bug;
- a required test;
- or a verification finding.

---


## Operational Safety

### Destructive Actions

Before any destructive or difficult-to-reverse action, verify:

- the target resource;
- the environment;
- the scope;
- the rollback/recovery path.

Examples include:

- deleting data;
- dropping tables;
- force-pushing;
- rewriting Git history;
- deleting branches;
- destructive migrations;
- removing infrastructure;
- production configuration changes.

Prefer reversible operations and staged rollout where practical.

Never broaden a destructive action beyond the explicit task scope.

### Evidence Before Claims

Do not claim that something:

- works;
- is fixed;
- is deployed;
- is healthy;
- passed CI;
- is running in production;

without evidence from the corresponding verification layer.

Report the strongest evidence actually observed and explicitly distinguish:

```text
verified
not verified
blocked
inferred
```

### Scope Lock

At task start, establish:

- active task;
- affected repositories;
- intended files/components;
- success criteria.

If new unrelated work is discovered, report it separately instead of silently expanding scope.
