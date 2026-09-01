# Retire the raw artifact root

On 2026-09-01 the workspace retired the top-level `raw/` artifact namespace.
This record captures migration evidence; it is not an active engineering queue.

## Safety evidence

- The existing `portfolio-measurement-integrity` OPS owner process was no
  longer alive. With explicit user authorization, its stale transaction was
  cleaned up to terminal `BLOCKED` state before any origin metadata changed,
  then moved from the active namespace to
  `.ops/archive/2026-09-01-portfolio-measurement-integrity/`.
- The pre-move inventory contained 340 tracked files and one preserved
  untracked request file.
- A content-hash multiset comparison passed 341/341 immediately after the
  Git-aware moves, before references inside text files were updated.
- Platform-native `openspec*` skills and `/opsx:*` commands were checksummed
  before migration and are verified again by the completion gate.

## Destination taxonomy

- Quant rounds, studies, audits, samples, reports, and navigation moved to
  `research/quant/`.
- Operational explanations moved to `docs/reviews/`.
- Historical handoff, prompts, proposals, and closed backlog moved to explicit
  `docs/archive/` locations.
- The untracked legacy request was preserved as
  `docs/archive/legacy-requests/rafactor.md`.

No compatibility symlink was created and no top-level `raw/` directory remains.

## Active origin mapping

The six immutable evidence references for `portfolio-measurement-integrity`
were migrated after lock release:

- five `raw/researcher/round*.md` references became matching
  `research/quant/rounds/round*.md` references;
- `raw/reports/optimize_loop_update_v2.csv` became
  `research/quant/reports/optimize_loop_update_v2.csv`.

The artifact count remained six, every destination exists, and a structural
comparison proved that `change`, `origin`, `research_iteration`, and
`instrument` were unchanged.
