## 1. Delete the dead coordinator rule

- [x] 1.1 Delete `.agents/rules/phase-agent-coordinator.md` (describes only the deleted SQLite coordinator/lease/fencing/account-rotation system); verify `git status` shows it removed
- [x] 1.2 Run `uv run --project tools/orchestrator sync-agent-links`; since `.claude/rules/phase-agent-coordinator.md` is currently a real file (not the expected symlink — confirmed content-identical via `diff` before this change), the tool will not remove it (it never deletes real files). Manually `rm .claude/rules/phase-agent-coordinator.md` as part of this task, then rerun `sync-agent-links --check` and confirm it reports no error for that path
- [x] 1.3 Grep the repo (excluding `.git/` and this change's own `openspec/changes/retire-phase-agent-coordinator-docs/`) for `phase-agent-coordinator` and confirm no remaining reference to the deleted rule file

## 2. Rewrite CLAUDE.md's Role and Working Model

- [x] 2.1 In CLAUDE.md's `## Role` section, replace the paragraph "`/ops:e2e` is the project-level autonomous lifecycle: deterministic shell state orchestrates logical phase agents, with Claude/Codex selected per attempt..." — `/ops:e2e` was deleted (commit `73a3a71`) along with the shell-state orchestration it names. State plainly that no automatic phase-routing mechanism exists today; `/opsx:*` remains the native OpenSpec command namespace (unchanged, still accurate)
- [x] 2.2 In the same section, replace "When the resolver selects Claude after deterministic provider failure or a manual phase pin, Claude owns that bounded attempt..." — there is no resolver. State that Claude is, in practice, the implementation path today absent that mechanism, while preserving the same implementation/test/safety contract this sentence already requires
- [x] 2.3 Rewrite `## Working Model`'s `Role boundary` block: remove the `ORCHESTRATE = deterministic OPS shell state` line (no such shell state exists) and add a note that fallback is a manual decision on confirmed quota exhaustion, not automatic detection. Keep `Codex: IMPLEMENT + TEST` / `Codex: FIX findings` and `IMPLEMENT / FIX = Codex first, Claude fallback` exactly as originally written — the role boundary itself is unaffected by the coordinator's deletion (corrected mid-apply; see design.md's superseded first draft)
- [x] 2.4 Verify by re-reading the edited sections: no remaining reference to `/ops:e2e`, "resolver", "phase agent" (as automatic routing), or "OPS shell state" anywhere in CLAUDE.md

## 3. Rewrite coding-and-verification.md's non-trivial-change pipeline

- [x] 3.1 Replace the "Required order for a non-trivial change" pipeline (`phase-agent PLAN → phase-agent IMPLEMENT → local checks → local commit → fresh phase-agent VERIFY → phase-agent FIX (if needed) → fresh FINAL_VERIFY → push main → ...`) with the current actual order: plan (via `/opsx:propose`), implement, run local checks, commit, independently verify, fix if needed, final-verify, then push/CI/Coolify/production-verify — without naming a `phase-agent` routing mechanism that no longer exists
- [x] 3.2 Confirm the "Claude role note: bug investigations & system reviews" subsection immediately below still reads coherently against the rewritten pipeline (it already correctly says "A separate Codex agent implements..." as one path — leave that sentence as-is; it describes an operator-initiated Codex invocation, not automatic routing, and needs no change)
- [x] 3.3 Grep `coding-and-verification.md` for `phase-agent` and confirm every remaining hit is either this file's own now-corrected text or an unrelated proper noun (none expected) — no dangling reference to automatic phase routing

## 4. Patch quant-research-loop skill

- [x] 4.1 In `.agents/skills/quant-research-loop/SKILL.md`, "Core workflow" step described by "The terminal launcher records the iteration exactly once before invoking the `quant_research` phase agent. Provider selection comes from atomic phase-agent state...": replace with what `.claude/commands/quant/research.md` already documents — no launcher or state CLI tracks iteration; the round-file sequence under `research/quant/rounds/` is the sole source of truth for the next round number
- [x] 4.2 In the same file, replace "For `PROMOTE` only, create/reuse one stable OpenSpec change and enter the canonical OPS lifecycle with research-origin references" with: create the OpenSpec change via `/opsx:propose` and stop at planning — no automatic lifecycle follows
- [x] 4.3 In `references/playbook.md`'s "Round structure" step 1 ("Confirm the recorded iteration and routing. The terminal launcher has already incremented..."), replace with the round-file-sequence-is-the-only-truth language, matching 4.1
- [x] 4.4 In `references/playbook.md`'s "Promotion and provider failover" section, replace the heading and step 1 ("Route actionable implementation only through `/ops:e2e` and `uv run --project tools/orchestrator run-phase-agent`; do not modify runtime code outside that lifecycle or invoke Codex/Claude directly...") with: create the OpenSpec change, then implementation is a separate manual decision by the operator (matching `.claude/commands/quant/research.md`'s current wording) — keep steps 2-5 immediately below (local Docker test, commit-to-main, push, CI tracking, deploy-path checking) unchanged, they remain accurate
- [x] 4.5 Grep `.agents/skills/quant-research-loop/` for `phase-agent|ops:e2e|run-phase-agent|terminal launcher` and confirm zero remaining hits

## 5. Final verification

- [x] 5.1 Grep the whole repo (excluding `.git/`) for `run-phase-agent|agent-role-state|ops-runtime\.sh|phase-agent-coordinator` and confirm every remaining hit is either historical (git log, `docs/archive/`) or this change's own proposal/design explaining what was removed — none in currently-active `.agents/`, `CLAUDE.md`, or `.claude/commands/`. This grep surfaced three items outside the original plan (see 5.3-5.5, approved mid-apply by the user).
- [x] 5.2 Re-read the four edited/deleted files end-to-end for internal coherence (no leftover sentence assuming the deleted mechanism still exists)

## 5a. Added scope, approved mid-apply

The user reviewed the 5.1 grep findings and approved fixing all three, with
`.claude/commands/orchestrator/e2e.md` **rewritten, not deleted** — they use
it for quick/one-off and recurring tasks. The user also corrected the role
boundary during this apply: it is **Codex first for IMPLEMENT/FIX** (not
"Claude implements directly, Codex when invoked") — restoring the original
`CLAUDE.md`/`AGENTS.md` framing, with quota-based fallback now described as
manual (no coordinator) rather than automatic. `CLAUDE.md`, `AGENTS.md`, and
`.agents/rules/coding-and-verification.md` were corrected to this restored
framing after that message (superseding the "Claude by default" language
tasks 2.2/2.3/3.1 were first drafted with).

- [x] 5.3 Rewrite `.claude/commands/orchestrator/e2e.md` (found resurrected with its original, pre-deletion coordinator content — see design.md's "environment anomaly" risk) to describe a fast, stateless implementation turn via `tools/orchestrator`'s `codex-exec`/`claude-exec` (Codex first, Claude fallback on confirmed quota), explicitly for quick or repeated/recurring requests — not deleted, per the user's explicit request
- [x] 5.4 Patch `AGENTS.md`: remove the `ORCHESTRATE = deterministic OPS shell state` line and the `agent-role-state`/`/ops:e2e` references (role boundary table itself — Claude first for PLAN/VERIFY/FINAL_VERIFY, Codex first for IMPLEMENT/FIX — is unchanged, matching the restored framing)
- [x] 5.5 Patch `README.md`: rewrite the opening summary, the `.claude/`/`.kimi-code/`/`.opencode/` line (only `.claude/` exists), the `tools/` structure line, the entire "Quant research và phase agents" section (launcher, `run-phase-agent-command`, `configure-agent-roles`, per-role state file — all deleted), and "Source of truth cho quant promotion" (drop the `OPS = execution/tracing truth` row and the `enter canonical /ops:e2e` claim)
- [x] 5.6 Re-run the full repo-wide grep from 5.1 after 5.3-5.5; confirm every remaining hit is historical or self-referential ("this was deleted") — none assume the deleted mechanism still exists
- [x] 5.7 Re-run `tools/orchestrator` verification (`pytest`, `ruff check`, `ty check`) and `sync-agent-links --check`; all pass
