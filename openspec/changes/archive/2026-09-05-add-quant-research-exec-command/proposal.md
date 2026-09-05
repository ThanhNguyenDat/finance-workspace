## Why

Quant-research rounds are now split across two documents: `.claude/commands/
quant/research.md` and `.agents/skills/quant-research-loop/SKILL.md` define
the round **lifecycle** (Claude PLAN, Codex IMPLEMENT, Claude VERIFY, Codex
FIX-if-needed — all inside one round number, logged under `--change
quant-research-round-<N>`), while `.agents/domain/quant-research-domain.md`
defines the round's **domain rules** (task scope, backtest
constraints, classification, promotion gate) that whoever runs PLAN or
IMPLEMENT must satisfy. Today an operator drives the lifecycle by hand: run
`/quant:research` in an interactive Claude Code session for the PLAN/VERIFY
stages, then manually copy the plan into a file and shell out to
`codex-exec --role implement --change quant-research-round-<N> --prompt-file
<file>` for IMPLEMENT (and again with `--role fix` if verify finds a
problem). This was exercised once by hand for round 452 and works, but the
copy/shell-out step is repetitive and easy to get wrong (wrong round number,
forgotten `--change`, wrong role).

## What Changes

- Add a new `quant-research-exec` command to `tools/orchestrator` (a new
  `[project.scripts]` entry) that drives the Codex side of one round's
  lifecycle automatically: it resolves the round number and
  `--change quant-research-round-<N>` value, reads the round's domain rules
  from `.agents/domain/quant-research-domain.md` as the base brief
  (does not duplicate that text into its own source), and runs the Codex
  IMPLEMENT stage (and, given an operator-supplied fix instruction, the
  Codex FIX stage) through the existing `CodexProvider` machinery — same
  account failover, redaction, and JSONL logging as `codex-exec` today.
- The command does not run the Claude PLAN or VERIFY stages itself and does
  not attempt to invoke `/opsx:propose` for a `PROMOTE` result — those stay
  the operator's own interactive Claude Code session, unchanged from today.
  See `design.md` for why (a scripted Claude SDK turn has no access to
  slash-command/skill discovery, and PLAN/VERIFY/OpenSpec authoring are
  explicitly Claude's job, not something this Codex-facing command should
  attempt).
- No generic coordinator, lease, account-auto-rotation-across-invocations,
  or approval-question flow is introduced; this command is a fixed,
  single-purpose wrapper around one existing provider (`CodexProvider`) for
  one skill's round shape, not a new orchestration layer.

## Capabilities

### New Capabilities

None. This extends the existing `orchestrator-exec-cli` capability with one
more command; it does not introduce a new capability domain.

### Modified Capabilities

- `orchestrator-exec-cli`: add requirements for the new `quant-research-exec`
  command — round-number resolution, reading domain rules from
  `.agents/domain/quant-research-domain.md`, running the Codex
  IMPLEMENT/FIX stage through `CodexProvider`, and reusing the existing
  `--change`-scoped JSONL logging, redaction, and account-failover behavior
  unchanged.

## Impact

- `tools/orchestrator/pyproject.toml`: new `[project.scripts]` entry.
- `tools/orchestrator/src/orchestrator/cli/quant_research_exec.py`: new
  module.
- `tools/orchestrator/tests/`: new tests for round-number resolution and the
  IMPLEMENT/FIX stage wiring (fakes, not real Codex calls).
- `tools/orchestrator/README.md`: document the new command.
- `openspec/specs/orchestrator-exec-cli/spec.md`: gains requirements for the
  new command (delta in this change's `specs/`).
- `.claude/commands/quant/research.md`: its Bước 3/7 example commands switch
  from raw `codex-exec --role implement/fix` to `quant-research-exec --role
  implement/fix` now that the dedicated command exists (already restructured,
  separately from this change, to read domain rules from
  `.agents/domain/quant-research-domain.md` rather than embedding them
  — that restructuring is a prerequisite this change's design depends on,
  not part of this change's own scope).
- No changes to `.agents/skills/quant-research-loop/SKILL.md`,
  `.agents/domain/quant-research-domain.md`, `providers/base.py`,
  `providers/claude.py`, or `providers/codex.py` — this command is a
  consumer of that existing surface, not a change to it.
