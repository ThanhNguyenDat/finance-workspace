## Why

`quant-research-exec` (added in `add-quant-research-exec-command`) only runs
one Codex stage per invocation (`--role implement` or `--role fix`); the
operator's own interactive Claude Code session still has to manually chain
calls together (implement, read evidence, decide, maybe fix, finalize).
Real usage this session (round 453) confirmed the operator wants one
invocation to run the whole cycle instead: implement, verify, fix if
needed, and finalize — without hand-driving each stage.

The one constraint that must survive this simplification: verification must
stay genuinely independent. `.agents/skills/quant-research-loop/SKILL.md`
and `.agents/domain/quant-research-domain.md` both exist specifically so a
different actor (Claude, not Codex) checks Codex's own work before it's
trusted — a round that lets Codex grade its own homework can silently
promote a fabricated or cherry-picked result. This change keeps that
property by running the VERIFY stage through `ClaudeProvider` (already
built for `claude-exec`), not another Codex turn.

## What Changes

- `quant-research-exec` becomes a single-invocation, multi-stage cycle: it
  internally runs Codex IMPLEMENT (via `CodexProvider`), then Claude VERIFY
  (via `ClaudeProvider`) against the evidence Codex produced, then — only if
  VERIFY finds a problem — Codex FIX, then one bounded re-verify, then Codex
  finalize (commit). No stage re-implements the domain rules; VERIFY reads
  the same `.agents/domain/quant-research-domain.md` non-negotiable
  invariants IMPLEMENT was given.
- `--role` is removed from the CLI: the command no longer exposes separate
  implement/fix entry points, because there is only one entry point now (a
  full cycle). `--round` keeps its existing auto-detect-for-a-new-round
  behavior.
- Verify's spoken verdict is structured (a fixed marker line the orchestrator
  parses), not inferred from free text, so the Python code can reliably
  branch on PASS / FAIL / a clarifying QUESTION.
- When Claude's VERIFY step needs to ask a clarifying question before it can
  decide, the orchestrator sends that question to Codex as a follow-up turn
  (Codex is the one with full context of what it just did — the natural
  party to answer "why did you pick this window" or "confirm X") and feeds
  the answer back into one continued VERIFY turn. This round-trip happens at
  most once per verify pass, so it cannot loop indefinitely.
- The fix retry is bounded at one attempt (matching the domain rules' and
  round-flow's existing "fix at most once, then close the round honestly"
  guidance) — if the re-verify after that one fix still fails, the
  orchestrator has Codex close the round with an honest `NEEDS-MORE-RESEARCH`
  or `DATA-ISSUE` classification instead of continuing to fix.
- Each provider's own session/thread stays alive across the stages it
  participates in (Codex: implement→ask→fix→close-honest→finalize; Claude:
  verify→its own question-continuation→post-fix re-verify) via each SDK's
  existing resume support, instead of every stage being a fresh,
  memory-less turn that has to be re-told everything. This needs a small,
  additive change to `BaseProvider`/`CodexProvider`/`ClaudeProvider` (see
  design.md Decision 2) — `codex-exec`/`claude-exec` are unaffected since
  neither passes the new optional parameter.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `orchestrator-exec-cli`: `quant-research-exec`'s requirements change from
  "one Codex stage per invocation, `--role` required" to "one full
  implement→verify→fix→finalize cycle per invocation, no `--role` flag" —
  this replaces (not adds to) the requirements added in
  `add-quant-research-exec-command`.

## Impact

- `tools/orchestrator/src/orchestrator/cli/quant_research_exec.py`: rewritten
  to orchestrate both providers and the verify/fix/finalize state machine.
- `tools/orchestrator/src/orchestrator/providers/base.py`,
  `providers/codex.py`, `providers/claude.py`: add the optional
  `resume_id`/`last_session_id` session-continuity support (design.md
  Decision 2); additive only, existing callers unaffected.
- `tools/orchestrator/tests/test_quant_research_exec.py`,
  `tests/test_providers.py`: rewritten/extended for the new behavior
  (structured verdict parsing, bounded fix retry, bounded Q&A round-trip,
  session resume threading, `--role` flag removed).
- `tools/orchestrator/README.md`: rewrite the `quant-research-exec` section.
- `.claude/commands/quant/research.md`: Bước 3-8 collapse from "Claude
  drives implement/fix calls by hand, alternating with its own VERIFY" to
  "Claude hands the plan to one `quant-research-exec` call and reads back
  the finished round" — the command's flow section needs a matching rewrite
  once this lands.
- `openspec/specs/orchestrator-exec-cli/spec.md`: the `quant-research-exec`
  requirements from `add-quant-research-exec-command` are superseded here.
- Round 453 (already running under the current single-stage design when
  this change was scoped) is unaffected — it finishes under the design that
  was live when it started; this new cycle applies to rounds started after
  this change merges.
