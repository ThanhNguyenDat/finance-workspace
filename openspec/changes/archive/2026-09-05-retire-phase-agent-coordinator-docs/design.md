## Context

See `proposal.md` for the full inventory of what's stale and why. This
design covers the one real judgment call: what the rewritten
`CLAUDE.md`/`coding-and-verification.md` text should say about *who
implements* now that no automatic Codex-routing coordinator exists.

## Goals / Non-Goals

**Goals:**
- Replace every passage that assumes an automatic phase-routing mechanism
  exists with text describing today's reality: the role boundary itself
  (Claude first for PLAN/VERIFY/FINAL_VERIFY, Codex first for IMPLEMENT/FIX)
  is unchanged, but selecting the fallback provider on quota exhaustion is
  now a manual, operator- or session-level decision, not something a
  coordinator detects and switches automatically.
- Keep the PLAN/VERIFY-first and IMPLEMENT/FIX-first assignments CLAUDE.md
  and AGENTS.md already state — only the *routing mechanism* is what
  changed, not the role boundary's intent.

**Non-Goals:**
- Not deciding whether a new Codex-routing mechanism should be built later
  (`quant/research.md` already says explicitly: implementation "chờ
  orchestrator mới được dựng lại" / waits for a new orchestrator to be
  built — that's a future, separate decision, not this change's job).
- Not touching any of the 3 rules or 12 skills already confirmed clean.

## Decisions

**Keep the original Codex-first-for-implement framing; only remove the
automatic-routing claim** (corrected mid-apply by the user, superseding this
decision's first draft — see below): `CLAUDE.md`/`AGENTS.md` already state
the role boundary as `PLAN/VERIFY/FINAL_VERIFY = Claude first, Codex
fallback` and `IMPLEMENT/FIX = Codex first, Claude fallback`. That boundary
itself is unaffected by the coordinator's deletion — only the *mechanism*
that used to enforce/automate it is gone. The rewrite keeps both role-first
assignments exactly as they were and states plainly that fallback is now a
manual, operator- or session-level decision triggered by confirmed quota
exhaustion (not a generic 429/timeout/network blip), with no coordinator or
resolver detecting it automatically.

*First draft of this decision (superseded)*: initially written as "Claude
implements directly by default; Codex when the operator invokes it
directly" — reasoning that since no resolver exists, Claude is the only
implementation path "in practice." The user corrected this mid-apply:
Codex remains first-choice for IMPLEMENT/FIX exactly as before; the
practical difference the coordinator's deletion makes is only that
choosing to fall back is now manual rather than automatic. This preserved
record exists so a future reader who finds the corrected text doesn't
wonder whether the Codex-first framing was an oversight — it was
deliberately restored after being drafted the other way.

**Rewrite in place rather than deprecate-and-append**: edit the existing
"Required order for a non-trivial change" / "Working Model" text directly,
rather than leaving the old text and appending a correction note. Alternative
considered: mark the old pipeline "deprecated" and add new text alongside it
— rejected because a reader skimming the file would still see the dead
`phase-agent PLAN → IMPLEMENT → ...` pipeline as if it were live, which is
exactly the confusion this change exists to remove.

## Risks / Trade-offs

- **[Risk]** Rewriting `CLAUDE.md`'s Working Model is the highest-leverage
  edit in this change — every future session reads it. A wrong rewrite
  propagates further than the other edits. → **Mitigation**: keep the
  rewrite narrowly scoped to the routing-mechanism claim (what no longer
  automatically happens), not the role boundary itself (who is preferred
  for what) — the latter is unaffected by the coordinator's deletion and
  should not change.
- **[Risk]** `.claude/rules/phase-agent-coordinator.md` is currently a real
  file (not the expected symlink) per this session's earlier finding —
  deleting the canonical `.agents/rules/phase-agent-coordinator.md` leaves
  that real file behind as an orphaned copy with no source. → **Mitigation**:
  task list includes running `sync-agent-links` after the deletion and
  checking its output; if the tool reports the file as a stale link it
  removes it, but since it is currently a real file (not a symlink) the
  tool will not touch it — that real file must be removed by hand as part
  of this change's own cleanup, not left for a future session to discover
  again.
