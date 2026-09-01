## Context

See `proposal.md` for motivation. The current `raw/` root contains 340 tracked
files and one untracked user file across research rounds, reports, reviews,
archives, prompts, proposals, and a legacy global handoff. Ten shared
`.agents`/`.claude` files depend directly on those paths. One active promoted
change also holds immutable origin references into the old root and must not be
mutated while another OPS session owns its lock.

The installed OpenSpec 1.11.0 integration already owns native `/opsx:*`
commands. Those command and `openspec*` skill implementations are platform
artifacts, not shared Finance content.

## Goals / Non-Goals

**Goals:**

- End with no top-level `raw/` directory and no active workflow that recreates
  it.
- Give each durable artifact one clear owner and preserve research history.
- Keep promoted research traceable after path relocation.
- Make future non-trivial requests use OpenSpec/OPS rather than ad-hoc files.

**Non-Goals:**

- Reclassifying or rewriting historical research conclusions.
- Retrospectively creating OpenSpec changes for old proposals or handoff rows.
- Regenerating, standardizing, or hand-editing platform-native OpenSpec
  commands and skills.
- Changing any runtime Finance service or trading behavior.

## Decisions

### 1. Separate research, maintained documentation, and legacy archive

Use this deterministic destination map:

| Source | Destination |
| --- | --- |
| `raw/researcher/round*.md` | `research/quant/rounds/` |
| research index | `research/quant/index.md` |
| research audits and long-form studies | `research/quant/audits/` or `research/quant/studies/` |
| research sample CSVs | `research/quant/samples/` |
| `raw/reports/` | `research/quant/reports/` |
| `raw/explain/` | `docs/reviews/` |
| legacy handoff | `docs/archive/legacy-handoff-agent.md` |
| old prompts/proposals/closed backlog | `docs/archive/legacy-raw/` by source category |
| untracked ad-hoc request | `docs/archive/legacy-requests/`, preserving bytes |

This keeps research as a first-class artifact domain instead of forcing large
evidence into OpenSpec. The alternative of putting all research inside each
OpenSpec change was rejected because non-promoted rounds intentionally have no
engineering transaction and duplicated evidence would obscure ownership.

### 2. Native opsx owns engineering artifacts, not evidence storage

New or revised engineering work uses `/opsx:propose` or `/opsx:update`, then
`/opsx:apply`, verification through the available native/project lifecycle,
`/opsx:sync`, and `/opsx:archive`. `/ops:run` remains the project-level
orchestrator and delegates OpenSpec operations to native integration.

The migration does not run `openspec update`, change the global OpenSpec
profile, or edit `.claude/commands/opsx/*`, `.claude/skills/openspec*`, or
`.agents/skills/openspec*`. Enabling optional expanded-profile commands is a
separate CLI-owned operation.

### 3. Origin validation moves to explicit quant evidence roots

`trace-origin` accepts only files in the five `research/quant/` evidence
categories named by the spec. Tests cover valid paths, traversal, missing
files, symlink escape, old-root rejection, wrong session, and wrong phase.

An existing origin record is normally immutable. This migration may relocate
its paths only after its owner lock is released and only after proving that
all non-location fields and referenced file hashes are unchanged. The migration
records before/after path mapping in the change evidence. Mutating an origin
owned by another active session is forbidden; apply pauses instead.

### 4. Move content before rewriting references

Tracked files move with Git-aware operations so history follows them. Reference
updates happen after destinations exist, covering current docs/specs, archived
docs/specs where links must remain usable, shared rules/skills, quant commands,
OPS contracts, and internal research links. Semantic uses such as “raw symbol”
or “raw JSON” are not renamed.

The untracked `raw/rafactor.md` is preserved at the explicit legacy-request
destination. No cleanup command recursively deletes `raw/`; the directory is
considered retired only after inventory and reference checks prove it empty.

### 5. Compatibility is validation-driven, not symlink-driven

No `raw -> research` compatibility symlink is created because it would keep the
retired namespace alive and allow new writes to regress. Agent Contract tests
and repository searches enforce the new roots. Historical path strings that
are intentionally quoted as migration history must be clearly marked and must
not be interpreted as writable locations.

## Risks / Trade-offs

- **Active OPS origin is lock-owned** → Stop migration until that owner releases
  the lock; never rewrite live transaction state concurrently.
- **Hundreds of links can become stale** → Move first, mechanically update
  path references, and run targeted broken-reference/inventory checks.
- **Historical documents mention old paths as facts** → Preserve narrative
  wording when relevant but update actionable links and add explicit migration
  context.
- **Large move obscures unrelated skill edits already in the worktree** →
  preserve those edits, review rename detection, and validate skill entrypoints
  independently.
- **Rollback restores the old root** → Use a normal Git revert; no production
  or external state is changed.

## Migration Plan

1. Require no foreign active OPS lock whose origin references the old root;
   capture path and content-hash inventory.
2. Move tracked and untracked artifacts according to the destination map.
3. Update current contracts, commands, rules, non-platform skills, docs,
   OpenSpec references, OPS origin locations, and tests.
4. Verify no active writer or direct dependency targets `raw/`, no top-level
   `raw/` remains, all moved content hashes match, and platform OpenSpec files
   are unchanged.
5. Run bounded Agent Contracts, strict OpenSpec validation, skill validation,
   symlink synchronization, and diff checks.

Rollback is a Git revert before any subsequent research iteration writes to
the new location. If a validation gate fails, retain the moved files and fix
references forward rather than recreating a compatibility symlink.
