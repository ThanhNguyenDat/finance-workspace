## 1. OpenSpec and state foundation

- [x] 1.1 Implement `.agents/scripts/quant-research-state.sh` with validated defaults, atomic replacement, stale/live mutation locking, toggles, and iteration recording; verify with `bash -n` and the dedicated state test.
- [x] 1.2 Confirm `.ops/runtime/quant-research/state.json` is transient/ignored without broadening ignore scope; verify with the contract test and `git check-ignore` in a temporary state fixture.

## 2. Claude command integration

- [x] 2.1 Add `/quant-research`, `/quant:codex-off`, and `/quant:codex-on` under `.claude/commands/`; verify frontmatter, intended invocation, state reads, one-iteration behavior, Vietnamese output, and no recursive Claude/loop scheduling through the contract test.
- [x] 2.2 Update `/ops:run` only to document explicit `implementation_backend=claude-fallback` behavior while preserving the Codex default and lifecycle gates; verify existing orchestration tests and static default-backend assertions pass.

## 3. Documentation and tests

- [x] 3.1 Add deterministic state and quant command contract tests with hard timeouts and no real 20-minute loop; verify both scripts pass locally.
- [x] 3.2 Extend Agent Contracts CI with shell syntax checks and bounded quant tests; verify the workflow YAML has a job timeout and all existing orchestration checks remain present.
- [x] 3.3 Document commands, runtime-state semantics, composition limitation, normal/fallback modes, and loop safety in README; verify exact examples and no quota text embedded in the loop invocation.

## 4. Verification and delivery

- [x] 4.1 Run native OpenSpec strict validation, sync-link checks, shell syntax checks, state/quant/orchestration tests, settings JSON validation, and `git diff --check`; verify all acceptance criteria individually.
- [x] 4.2 Review the final diff, archive the completed OpenSpec change, commit the scoped workspace changes to `main`, push without force, verify local/remote SHA equality, and track Agent Contracts to success.
