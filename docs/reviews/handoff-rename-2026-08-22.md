# Rename `docs/archive/legacy-handoff-agent.md` → `docs/archive/legacy-handoff-agent.md`

File itself already renamed locally (untracked, `raw/` is scratch space per
pending `.gitignore` change) and its title updated to "Agent handoff (Claude
↔ Codex)".

Five tracked repo docs still have their working-tree content updated but
**uncommitted**, ready for review/push:

- `.agents/skills/kline-data-quality/SKILL.md:194`
- `.agents/rules/production-deployment-verification.md:84`
- `.agents/skills/repository-delivery/SKILL.md:147`
- `.agents/skills/quant-research-loop/SKILL.md` (description + 3 body refs)
- `.agents/skills/repository-delivery/agents/openai.yaml:4`

All five are plain `handoff_codex.md` → `handoff_agent.md` string swaps, no
other content changed.

`docs/archive/legacy-handoff-agent.md` and the two `docs/archive/legacy-raw/system/prompt*.md` files were also
updated (untracked scratch, no action needed there).

Deliberately left untouched: `raw/researcher/*.md` and
`research/quant/studies/portfolio-btc-optimization-log.md` — those are frozen historical round
logs referencing the old name as it existed at the time, not forward-facing
docs.

**Done criteria:** the 5 diffs reviewed and pushed to `main`.
