## 1. Migration safety and inventory

- [ ] 1.1 Confirm no foreign active OPS lock owns an origin record that
  references `raw/`; if one exists, stop without moving files, otherwise record
  the tracked/untracked path inventory and content hashes for later comparison.
- [ ] 1.2 Record checksums for `.agents/skills/openspec*`,
  `.claude/skills/openspec*`, and `.claude/commands/opsx/*`, and verify the
  working tree's unrelated skill-normalization edits are preserved.

## 2. Relocate durable artifacts

- [ ] 2.1 Move quant rounds, index, studies, audits, samples, and reports into
  the `research/quant/` taxonomy with Git-aware moves; verify every tracked
  source path has exactly one destination.
- [ ] 2.2 Move operational explanations into `docs/reviews/`, move legacy
  handoff/prompts/proposals/closed backlog into explicit `docs/archive/`
  locations, and preserve the untracked `raw/rafactor.md` under
  `docs/archive/legacy-requests/`; verify no source file is overwritten.
- [ ] 2.3 Compare pre/post content hashes and tracked file counts, then verify
  no top-level `raw/` directory remains and no compatibility symlink recreates
  that namespace.

## 3. Update authoritative contracts and writers

- [ ] 3.1 Update `AGENTS.md`, `README.md`, applicable shared rules, and
  non-platform skill guidance to describe the new research/docs ownership and
  native `/opsx:*` engineering workflow; verify semantic uses such as raw
  symbols and raw JSON remain unchanged.
- [ ] 3.2 Update `.claude/commands/quant-research.md` and
  `.claude/commands/ops/run.md` so new evidence and promotion references use
  only approved `research/quant/` roots; verify no project command writes
  `raw/` or uses a global handoff as a queue.
- [ ] 3.3 Update `ops-runtime.sh trace-origin` path and resolved-path allowlists
  for the five approved quant evidence categories, preserving traversal,
  symlink-escape, missing-file, phase, session, and immutability checks.
- [ ] 3.4 Update Agent Contract fixtures and assertions to accept new roots and
  reject old-root, traversal, missing, outside-root, wrong-owner, and
  wrong-phase inputs within explicit test timeouts.

## 4. Repair traceability and references

- [ ] 4.1 Update current specs, active change artifacts, documentation, and
  internal research links to their relocated paths; verify all actionable
  repository-relative links resolve.
- [ ] 4.2 After confirming the owning OPS lock is released, migrate any existing
  origin artifact locations while preserving every non-location field,
  artifact count, and referenced content hash; verify the before/after mapping
  is exact and no concurrent runtime state is touched.
- [ ] 4.3 Update archived narrative references where needed for current-checkout
  discoverability while preserving their historical meaning; verify Git history
  still exposes the original paths and contents.

## 5. Repository verification

- [ ] 5.1 Verify searches find no active `raw/` writer, approved-path contract,
  global handoff dependency, or top-level `raw/` entry, allowing only clearly
  historical prose and unrelated semantic uses of the word `raw`.
- [ ] 5.2 Run all bounded `.agents/scripts/tests/*.sh`, shell syntax checks for
  changed scripts, and the skill validator for every changed non-platform
  skill; verify every command exits successfully.
- [ ] 5.3 Run `openspec validate --all --strict --no-interactive`,
  `./.agents/scripts/sync-agent-links.sh`,
  `./.agents/scripts/sync-agent-links.sh --check`, and `git diff --check`;
  verify strict validation and synchronization pass.
- [ ] 5.4 Compare platform-native checksums from task 1.2 and review the final
  rename-aware diff; verify no `openspec*` skill or `/opsx:*` command
  implementation changed and no unrelated user change was lost.
