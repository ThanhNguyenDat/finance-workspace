## Context

See `proposal.md` - Why. Relevant existing surface this builds on, all
already implemented and unchanged by this design:

- `orchestrator.providers.codex.CodexProvider` / `.base.BaseProvider`: one
  bounded turn, per-account failover on quota-exhaustion-shaped errors,
  `_classify_exception` hook.
- `orchestrator.cli._shared`: `build_arg_parser`, `resolve_log_path(command,
  change)` (`--change` is format-only validated kebab-case, not checked
  against `openspec/changes/` on disk; omitted falls back to
  `adhoc-<date>`), `check_role_scope`/`emit_warning` (advisory only),
  `emit_event`/`emit_result`/`emit_error` (redacted stdout + JSONL).
- `.agents/domain/quant-research-domain.md`: the round's domain rules
  (task scope, backlog-reading rules, backtest constraints, classification,
  promotion gate) — separated out of `.claude/commands/quant/research.md`
  (which now holds only the round lifecycle/flow) specifically so this
  command has one self-contained file to read for what Codex's IMPLEMENT/FIX
  turn must satisfy, without also pulling in lifecycle text that describes
  Claude's own PLAN/VERIFY actions. Has the same YAML frontmatter shape
  (`---\nname: ...\ndescription: "..."\n---`) as the command file did.
- `research/quant/rounds/round<N>-*.md`: the round-file sequence is the sole
  source of truth for the next round number (no launcher, no state file).

## Goals / Non-Goals

**Goals:**
- Let an operator run the Codex IMPLEMENT stage (and, given a fix
  instruction, the Codex FIX stage) of one quant-research round with a
  single command, instead of hand-copying the plan into a file and
  hand-building `--change`/`--role` flags for `codex-exec`.
- Keep the round's domain rules in exactly one place
  (`.agents/domain/quant-research-domain.md`); this command reads that
  file, it does not fork or restate its content.
- Reuse every existing `CodexProvider`/logging/redaction/failover behavior
  unchanged — this command is a thin, purpose-specific composition, not a
  new execution path.

**Non-Goals:**
- Driving the Claude PLAN or VERIFY stages. Those stay in the operator's
  interactive Claude Code session running `/quant:research`, unchanged.
- Deciding when to call `--role fix` vs. closing the round. That judgment
  (verify passed / found a problem / found a problem deep enough to
  re-plan) stays with whoever is running Claude's VERIFY stage.
- A `PROMOTE` → `/opsx:propose` path. Creating OpenSpec planning artifacts is
  Claude's job (`CLAUDE.md`: "Claude owns: ... OpenSpec planning
  artifacts"), and a scripted Codex SDK turn has no access to Claude Code's
  slash-command/skill discovery to invoke `/opsx:propose` even if it were
  Claude's turn running here. `quant-research-exec` never runs this step;
  the operator's own Claude session does it, exactly as documented in
  `.agents/domain/quant-research-domain.md`'s "Khi kết quả là
  PROMOTE" section.
- Any cross-invocation memory (which round is "in progress", how many fix
  attempts have run). Each invocation is independent and stateless, matching
  every other command in this package; the round number and stage are
  supplied by the caller (the operator, or Claude's session driving the
  round) on each call.

## Decisions

**1. CLI shape: a thin superset of `codex-exec`, not a new stage model.**

```
quant-research-exec [PROMPT] [--prompt-file FILE]
                     [--round N] --role {implement,fix}
                     [--cwd DIR] [--timeout-seconds N]
                     [--model NAME] [--effort LEVEL]
```

`PROMPT`/`--prompt-file` carry the stage-specific brief: for `--role
implement` this is Claude's PLAN output (hypothesis + test design) on the
first call of a round, or a short "verify passed, finalize: commit round N
and clean up" instruction on the closing call; for `--role fix` this is the
specific problem Claude's VERIFY raised. The command does not itself
distinguish "draft" vs. "finalize" as separate flags or stages — both are
`--role implement` calls whose only difference is prompt content, matching
`.claude/commands/quant/research.md`'s own step 3-5 ("draft ... but do not
commit yet") vs. step 8 ("commit... clean up") being driven by prompt
content, not new code. (Those step numbers live in the lifecycle command,
not the domain skill this command reads — see Decision 4.) Codex already has full tool access within a turn (as
demonstrated running round 452 by hand through plain `codex-exec`) to run
the backtest, write the draft round file, or commit it, once told which to
do — the wrapper's job is only to assemble the right prompt and resolve
`--change`, not to model "draft" and "commit" as distinct code paths.

Alternative considered: separate `implement`/`fix`/`finalize` subcommands.
Rejected — it would triple the CLI surface for no behavioral difference
`CodexProvider` needs to know about, and would tempt the tool into deciding
*when* to finalize, which is Claude's VERIFY call to make, not this
command's.

**2. Round-number resolution: auto-detect only for `implement`, required for
`fix`.**

`--round` is optional for `--role implement`: if omitted, the command scans
`research/quant/rounds/round<N>-*.md` under `--cwd` (same directory Codex's
sandbox will operate in) for the highest existing `N` and uses `N+1` —
identical logic to what `.claude/commands/quant/research.md` step 1 already
tells Claude's PLAN stage to do by hand, just also implemented here for
convenience. `--round` is **required** for `--role fix` and the parser
rejects `--role fix` without it: auto-detecting "highest + 1" for a fix call
would silently target a brand-new round instead of the one already in
progress, which is exactly the kind of round-number mixup a wrapper like
this exists to prevent, not introduce. The auto-detected/validated round
number in both cases must be a positive integer; the command does not check
that `round<N>-*.md` actually exists for a `--role fix` call (kept
format-only, matching `--change`'s existing "not checked against disk"
philosophy) — a nonexistent round number just means Codex's turn will find
nothing to fix, which surfaces naturally in that turn's own result.

Alternative considered: track "current round in progress" in a small state
file. Rejected — reintroduces exactly the persistent cross-invocation state
this package's design (and `CLAUDE.md`) deliberately removed; the round
number is one integer the operator/Claude session already has on hand from
the previous call's `--change quant-research-round-<N>` log path or output.

**3. `--change` is derived, never a raw flag.**

The resolved round number becomes `--change quant-research-round-<N>`
internally (reusing `_shared.resolve_log_path` unchanged); `quant-research-exec`
does not expose a raw `--change` override. This forces every invocation for
a given round onto the one naming convention
(`tools/orchestrator/logs/quant-research-round-<N>/quant-research-exec.log`),
which is the entire point of adding this command — `codex-exec` remains
available directly for anyone who wants a different `--change` value for a
one-off Codex turn.

**4. Prompt assembly: strip frontmatter, prepend the domain skill's body,
append the caller's brief.**

Read `.agents/domain/quant-research-domain.md` from
`<cwd>/.agents/domain/quant-research-domain.md`, split off the leading
`---\nname: ...\ndescription: "..."\n---\n` YAML frontmatter block, and use
everything after it as the base instructions. The final prompt sent to
Codex is `<domain skill body>\n\n## This round's brief\n\n<PROMPT>`. Missing
file or malformed frontmatter (no closing `---` found) is a hard error
(`emit_error`, exit 1) — this command has exactly one source of truth for
round domain rules and does not fall back to guessing or duplicating them
inline.

Reading the domain skill rather than `.claude/commands/quant/research.md`
(the lifecycle command) is deliberate, not incidental: the command file's
own body is about *who* does what and *when* (Claude PLAN/VERIFY vs. Codex
IMPLEMENT/FIX, which CLI to shell out to) — text that is meaningless, and
potentially confusing, inside a Codex turn that only needs to know *what a
round must satisfy* to do its own IMPLEMENT/FIX work correctly. The domain
skill is exactly that subset, factored out for this reason.

Alternative considered: read `.claude/commands/quant/research.md` (as
originally drafted in this design) and either send its whole body or try to
extract just the domain sections from it at runtime. Rejected once the
domain content was factored into its own skill file — reading the already-
separated file is simpler and more robust than parsing section headers out
of a longer, mixed-purpose document.

**5. Fix-loop bound is documentation, not code.** `quant-research-exec` runs
one stage per invocation and has no loop of its own — "how many times to
call `--role fix` before giving up" is a judgment the calling Claude VERIFY
session makes, not something this stateless command can enforce. This bound
is already documented as operator/session guidance rather than enforcement
machinery: `.claude/commands/quant/research.md`'s step 7 states a round
calls `--role fix` **at most once**, closing the round with an honest
`NEEDS-MORE-RESEARCH` or `DATA-ISSUE` classification instead of fixing again
if Claude's re-check still finds a problem, per
`.agents/skills/quant-research-loop/SKILL.md`'s existing round-split
guidance. `tools/orchestrator/README.md`'s new section for this command
repeats the same bound for anyone reading the tool's own docs rather than
the round flow. No further change to either file is needed for this
decision — both already state the bound.

## Risks / Trade-offs

- [Operator passes the wrong `--round` for `--role fix`, silently fixing the
  wrong round's file] → Not automatically preventable without reintroducing
  state (rejected in Decision 2); mitigated by keeping the number small and
  visible (it's the same number the operator just saw in the implement
  call's `--change` log path and round-file name), and by the command
  itself not modifying files directly — a wrong round number just means
  Codex's own turn finds a mismatched or missing round file and reports
  that, rather than silently corrupting the wrong file.
- [Frontmatter-splitting logic breaks if
  `.agents/domain/quant-research-domain.md`'s format changes] → Narrow,
  well-tested string operation (split on the second `---` line) with a hard
  error on failure rather than silent fallback; covered by a unit test using
  the real current file content.
- [A stray `codex-exec` call for the same round uses a hand-typed `--change`
  that does not match `quant-research-round-<N>`] → Out of scope for this
  command to prevent (raw `codex-exec` remains general-purpose); documented
  in the README section so operators know to prefer `quant-research-exec`
  for round work.

## Migration Plan

Purely additive: new module, new `[project.scripts]` entry, new README
section, new spec delta on the existing `orchestrator-exec-cli` capability.
No existing command, config shape, or log path changes. Nothing to migrate
or roll back beyond removing the new entry point if reverted.
