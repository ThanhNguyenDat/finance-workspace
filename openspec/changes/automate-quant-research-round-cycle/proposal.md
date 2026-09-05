## Why

`quant-research-exec` (added in `add-quant-research-exec-command`) only ran
one Codex stage per invocation, given an operator-supplied plan, with a
required `--role` flag. Real usage this session (round 453) confirmed the
operator wants a single bare invocation — no required arguments — to run
an entire round autonomously, explicitly so it can be run as
`while true; do quant-research-exec; sleep <n>; done` with nothing inserted.
That means the command must now also choose its own hypothesis (the PLAN
stage), not just implement a supplied one.

The one constraint that must survive this: verification (and now planning)
must stay genuinely independent from implementation. `.agents/skills/
quant-research-loop/SKILL.md` and `.agents/domain/quant-research-domain.md`
both exist specifically so a different actor (Claude, not Codex) chooses
the hypothesis and checks Codex's own work before it's trusted — a round
that lets Codex both plan and grade its own homework can silently promote
a fabricated or cherry-picked result. This change keeps that property by
running PLAN and VERIFY through `ClaudeProvider` (already built for
`claude-exec`), never through Codex.

## What Changes

- `quant-research-exec` becomes a single, zero-required-argument invocation
  that runs an entire round: Claude PLAN (reads the backlog, picks one open
  hypothesis, designs the test) via `ClaudeProvider`, Codex IMPLEMENT via
  `CodexProvider`, Claude VERIFY against the evidence Codex produced, and —
  only if VERIFY finds a defect — up to 5 escalating Codex FIX + re-VERIFY
  attempts, then Codex FINALIZE (commit). `--round` still auto-detects the
  next round; an optional positional prompt becomes PLAN *guidance*, not a
  required brief.
- Verify's (and PLAN's own "I've decided" statement) verdict is structured
  (a fixed marker line the orchestrator parses), not inferred from free
  text. `VERIFY_RESULT: PASS` means the evidence and classification are
  trustworthy regardless of whether the research outcome itself is
  positive or negative — an honestly-measured `REJECTED` passes verify
  exactly like a `PROMOTE` would. `DEFECT` is reserved for an actual
  execution problem (fabricated/cherry-picked evidence, a non-disjoint
  holdout, a classification that doesn't match the numbers).
- When VERIFY needs to ask a clarifying question before it can decide, the
  orchestrator sends that question to Codex as a follow-up turn (Codex has
  full context of what it just did) and feeds the answer back into one
  continued VERIFY turn — bounded to one round-trip per verify pass.
- The fix loop is bounded to 5 attempts, escalating to each provider's
  highest effort (and an operator-configured escalated model, if any) from
  the 3rd attempt onward. If the 5th re-verify still returns `DEFECT`, the
  command stops with an error rather than guessing a classification or
  looping further.
- Each actor's SDK session/thread is resumed across the stages it
  participates in (Claude: PLAN→VERIFY→its own question-continuation→every
  re-VERIFY; Codex: IMPLEMENT→ASK→every FIX attempt→FINALIZE) instead of
  every stage being a fresh, memory-less turn.
- `--role` is removed. `--model`/`--effort` split into six per-provider
  flags (`--codex-model`/`--codex-effort`/`--codex-escalated-model`/
  `--claude-model`/`--claude-effort`/`--claude-escalated-model`), all
  optional.
- `PROMOTE` still stops at FINALIZE (commit the evidence) and reports the
  stable change name; creating the OpenSpec change via `/opsx:propose`
  remains the operator's own interactive Claude session's job, unchanged —
  a scripted turn has no slash-command/skill discovery to invoke it anyway.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `orchestrator-exec-cli`: `quant-research-exec`'s requirements change from
  "one Codex stage per invocation, `--role` required, operator supplies the
  plan" to "one full plan→implement→verify→fix→finalize cycle per
  invocation, zero required arguments" — this replaces (not adds to) the
  requirements added in `add-quant-research-exec-command`.

## Impact

- `tools/orchestrator/src/orchestrator/cli/quant_research_exec.py`: rewritten
  to orchestrate both providers through the full plan/implement/verify/fix/
  finalize state machine.
- `tools/orchestrator/src/orchestrator/providers/base.py`, `providers/codex.py`,
  `providers/claude.py`: add the optional `resume_id`/`last_session_id`
  session-continuity support (design.md Decision 2); additive only,
  existing callers (`codex-exec`/`claude-exec`) unaffected.
- `tools/orchestrator/tests/test_quant_research_exec.py`,
  `tests/test_providers.py`: rewritten/extended for the new behavior.
- `tools/orchestrator/README.md`: rewrite the `quant-research-exec` section.
- `.claude/commands/quant/research.md`: rewritten — Claude's interactive
  session no longer drives PLAN/IMPLEMENT/VERIFY/FIX step by step; it runs
  (or the operator runs directly) one `quant-research-exec` invocation per
  round and reads back the result.
- `openspec/specs/orchestrator-exec-cli/spec.md`: the `quant-research-exec`
  requirements from `add-quant-research-exec-command` are superseded here.
- Round 453 (already running under the prior design when this change was
  scoped) is unaffected — it finishes under the design that was live when
  it started; this new cycle applies to rounds started after this change
  merges.
