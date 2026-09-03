# Round 424 — DATA-ISSUE: nine already-committed round files (412-415, 417-418, 420-421, 423) plus their `index.md` entries were missing from the working tree, uncommitted; restored from HEAD

Classification: **DATA-ISSUE**. Zero containers, zero SSH tunnels, zero
backtest compute — a repository-hygiene defect in the research evidence
trail itself, same category as round422's finding three rounds ago.

Research-state iteration at round start: 226 (mechanically recorded by the
launcher before this prompt; not re-incremented here — `quant-research-state
state` itself still read back `225` mid-round, a read-timing artifact, not
acted on). Round-file numbering and the launcher's iteration counter remain
two independent counters, as round422 already documented; this is `round424`.

## What was found

`git status --short` at session start showed:

- `research/quant/index.md` modified (135 deleted lines — the `## Round 423`
  through `## Round 412` navigation entries, minus round416/419/422, see
  below).
- Nine round files deleted from the working tree but still present in
  `HEAD`'s tree (`git cat-file -e HEAD:<path>` succeeded for all nine):
  `round412`, `round413`, `round414`, `round415`, `round417`, `round418`,
  `round420`, `round421`, `round423`.
- One unrelated file, `tools/orchestrator/accounts.yaml.example`, also
  deleted from the working tree (last touched by an unrelated orchestrator
  commit `08fcaeb`) — **not** part of this finding, left untouched, noted
  separately below per scope control.

The deletion pattern was selective, not blanket: exactly the "pure
status-check, nothing changed" rounds were gone, while every round carrying
a real finding — `round411` (genuinely-blocked summary), `round416`
(release-decision resolution), `round419` (first real holdout score),
`round422` (the prior DATA-ISSUE fix) — was still present on disk. That
selectivity was checked as a possible sign of *intentional* curation (e.g. an
editorial pass pruning redundant no-op entries) before treating it as data
loss:

1. `git log -1 --format=%ct HEAD` (`3b1315b`, 2026-09-03T22:15:50+07:00) vs.
   `stat -c %Y research/quant/index.md` showed the working-tree edit landed
   **~5 minutes after** that commit.
2. `git show 3b1315b --stat` touched only `openspec/changes/*` (deleting
   already-superseded proposal/design/tasks/spec files for
   `phase-agent-lifecycle-flow`, `phase-agent-python-spawn-layer`,
   `portfolio-measurement-integrity`, `relocate-orchestrator-out-of-agents`)
   and one orchestrator handoff doc — it never touched
   `research/quant/*`, so the commit itself is not the source.
3. `research/quant/reports/optimize_loop_update_v2.csv` had **zero** diff —
   every round's CSV row, including the nine missing `.md` files' rows,
   was intact. A deliberate content-curation pass would be expected to touch
   the CSV too, or at minimum leave a rationale somewhere in the repo. A
   repo-wide search (`grep -ril "prune\|consolidat\|redundant.*round\|dedup"`)
   found no note anywhere — not in `index.md`, `docs/`, `.ops/`, or any
   commit message — explaining or authorizing the removal.
4. The same ~5-minute window that produced this diff also carried a large,
   unrelated `phase-agent`-orchestrator relocation/refactor session (per
   `3b1315b`'s own commit message and the surrounding reflog:
   `815f5bf`, `58a5466`, `0caa758`, `1c9531a`, `3cf41b7`, `fe3b4ad`, ... — all
   orchestrator/OPS lifecycle work, none quant-research). The one collateral
   deletion outside `research/quant/` (`accounts.yaml.example`) is itself
   orchestrator-tooling, reinforcing that this was accidental collateral from
   that session rather than a reasoned quant-research editorial decision.

Conclusion: no evidence of an intentional, authorized pruning was found; the
selective pattern is coincidental (the surviving files happen to be the ones
with real findings, but nothing in the repo says so was the *reason* for the
others' removal). Per round422's own precedent — preserve the evidence trail,
treat unexplained uncommitted deletion of already-committed research evidence
as at-risk — the safe, reversible action is to restore from `HEAD`, not to
complete or interpret the deletion as intentional.

## What was done

1. `git checkout -- research/quant/index.md research/quant/rounds/round412-*.md
   research/quant/rounds/round413-*.md research/quant/rounds/round414-*.md
   research/quant/rounds/round415-*.md research/quant/rounds/round417-*.md
   research/quant/rounds/round418-*.md research/quant/rounds/round420-*.md
   research/quant/rounds/round421-*.md research/quant/rounds/round423-*.md`
   — restored all ten paths to their `HEAD` content byte-for-byte (this is a
   scoped, path-specific restore of already-committed content, not
   `git checkout -- .` / `git clean`).
2. Verified: `git status --short` now shows only the pre-existing, unrelated
   `tools/orchestrator/accounts.yaml.example` deletion; all nine round files
   present on disk again (`ls research/quant/rounds/round41*.md
   research/quant/rounds/round42*.md`); `index.md`'s `## Round 423` and
   `## Round 412` headers both present again (`grep -c`).
3. Left `tools/orchestrator/accounts.yaml.example` untouched — unrelated to
   quant research, out of this round's scope; reported here only so a future
   round (or whoever owns the orchestrator relocation work) doesn't miss it.

## Standard status re-check (same three threads as round422/423)

Confirmed unchanged, same calendar day as round423 (2026-09-03):

- `finance-live-action`: `git fetch origin main` — `HEAD` still `ca23b05` =
  `origin/main`, `gh run list --branch main --limit 5` shows the same two
  most-recent green runs already recorded (`Build and Deploy`,
  `Production Live Action Verification` for `ca23b05`). No new commit.
- Target 2 metric definition: still no metric in the tool (round401,
  unchanged); `docs/adr/` does not exist in this checkout — no ADR to check
  against.
- Forward-time thread: baseline 2026-08-30 (round403), today 2026-09-03 — 4
  days elapsed, same as round422/423 (same day, no new elapsed time),
  ~26 more needed against the ~30-day threshold.
- `finance-workspace`/`origin/main`: both now at `3b1315b`, fully synced —
  no lead to push, no lag to pull.

## OpenSpec/OPS lifecycle observation (context only, out of scope)

While checking `portfolio-measurement-integrity` task 6.4 (round419/422/423's
third tracked thread), `openspec/changes/portfolio-measurement-integrity/`
(proposal/design/tasks/spec) no longer exists — deleted by `3b1315b`, and not
present under `openspec/changes/archive/` either, so it was removed outright
rather than archived. `.ops/changes/portfolio-measurement-integrity/` (the
separate OPS runtime-state directory) still exists with a **stale**
`handoff.md` reading `BLOCKED (2026-09-03)` and restating the *pre-round419*
blocker text (network/Finance MW unavailable) — it was never updated to
reflect round419's resolution (a real gate score was produced that round).
This OpenSpec-artifact-removed / OPS-state-still-open inconsistency is a
lifecycle irregularity, but per round416/419's own established boundary this
loop does not own OPS/OpenSpec lifecycle disposition — reported as context
for whoever owns that orchestrator work, not acted on here.

## What this does and does not change

**Does not change** any prior strategy or measurement conclusion — the
missing files were pure evidence records of already-made findings (mostly
"nothing changed since last check"); their content is unchanged by this
restore. **Does** close a second evidence-trail integrity gap in three
rounds: round422 recovered eleven never-committed rounds and fixed a CRLF
drift; this round recovered nine already-committed rounds and one navigation
doc from an unexplained working-tree deletion. Repeated occurrence of the
same failure mode (evidence present on disk or in git but not verified
end-to-end before a round or an unrelated task touches the tree) suggests the
existing round-structure step 8 check ("confirm `git status --short` is
clean... before ending the round") catches divergence introduced *by this
loop*, but not divergence introduced by *other, concurrent* sessions working
in the same checkout between rounds — worth a persistent skill note.

## Named next step

Unchanged from round422/423 on the trading-research side: Target 2's metric
definition still needs a product/human decision; the forward-time re-read
still needs calendar time (~26 more days from today against the 2026-08-30
baseline). No new backtest direction opens from this round.
