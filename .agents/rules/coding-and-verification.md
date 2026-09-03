# Coding and Verification Rules

## Source of truth

- Treat the local Git repository and the pushed GitHub commit as the source of
  truth.
- Treat production as a deployment target, never as an editing workspace.
- Keep changes small, focused, reviewable, and reversible.
- Reuse existing patterns before adding abstractions or dependencies.

## Branch and merge discipline

- Every new branch starts from current `main` — pull `main` before creating
  it, never branch off another in-progress or unmerged branch.
- Finish one branch by merging it into `main` before starting the next piece
  of work; do not stack a new branch on top of an unmerged one.
- Keep local `main` and `origin/main` equal — fetch and fast-forward local
  `main` before branching and again immediately after every merge, so the
  two never drift apart.

### Solo-maintainer exception: commit directly to `main`

User confirmed explicitly (2026-08-19): this ecosystem (`finance-mw`,
`finance-broker`, `finance-live-action`, `mt5`) has exactly one maintainer,
so the branch/PR ceremony above exists to prevent conflicts between
concurrent writers — a problem this project doesn't have. **Commit and push
directly to `main`** for every change, across all four repos; do not create
feature branches or PRs as a matter of routine. This has already been the
actual practice throughout every session in this ecosystem (every commit in
`git log` on every repo lands directly on `main`) — this note makes that
explicit and searchable instead of leaving it as an unwritten, easy-to-miss
inconsistency between this file and observed behavior.

Direct-to-main means there is no mandatory feature-branch or PR ceremony, and
a local commit on `main` is allowed. The **push remains the release gate**:
non-trivial implementation must receive a fresh configured FINAL_VERIFY process
before it is pushed. Provider-independent verification is preferred. When quota
or an explicit phase pin yields the same provider, process-separated review plus
all applicable objective evidence is required and must not be called independent.

Required order for a non-trivial change:

```text
phase-agent PLAN → phase-agent IMPLEMENT → local checks → local commit
→ fresh phase-agent VERIFY → phase-agent FIX (if needed) → fresh FINAL_VERIFY
→ push main → GitHub Actions → Coolify → production verification
```

This does **not** relax anything else in this file: still run the full local
verification pass before committing, still keep each commit small and
reviewable, still push and track CI to a real green, still verify the deployed
revision and behavior in production. The exception is narrowly about branch
ceremony, not about skipping verification.

## Required verification order

1. Inspect the relevant local code, tests, configuration, and Git history.
2. Implement and validate the change locally.
3. Review the diff and commit every in-scope change.
4. Push the commit and verify the exact SHA on GitHub.
5. Track all required GitHub Actions jobs to success.
6. Let CI/CD deploy the immutable revision through Coolify.
7. Verify the deployed revision and behavior in production.

Do not skip directly to production inspection when the answer can be obtained
from the local repository or GitHub. Do not edit production code or
configuration over SSH.

### Claude role note: bug investigations & system reviews

This file is shared across agents; the exception below applies only to
Claude, not to other agents reading this file (e.g. Codex still owns the
full order above).

When the user's request to Claude is a bug investigation or a system review
(not an explicit "fix this" instruction), Claude stops after step 1 —
inspect, do not implement. Document the root cause with exact file:line
citations, a fix-direction note explicitly marked "not applied —
investigation only", and a verification checklist in `docs/reviews/<topic>.md`
instead of proceeding to steps 2-7. A separate Codex agent implements,
commits, pushes, and carries the change through the rest of this
verification order; Claude verifies the result afterward once Codex reports
done. If the user explicitly asks Claude for a direct code fix in a given
request, that overrides this note for that request only.

## Test timeout contract

- Give every unit, integration, load, contract, shell, and end-to-end test
  command a hard timeout.
- Use the test framework's native timeout when it can terminate the full test
  process, such as `go test -timeout=10m`; otherwise wrap the command with GNU
  `timeout --signal=TERM --kill-after=30s`.
- Set `timeout-minutes` on every GitHub Actions job as a final safety boundary.
- Keep a short TERM grace period, then force-kill the process tree so a
  deadlocked test cannot occupy a self-hosted runner indefinitely.
- Interactive watch-mode commands are the only exception; CI must never use
  watch mode.

## Language-specific checks

### Go

- Run `gofmt` or the repository formatting check.
- Run targeted Go tests, then `go test ./...`, `go vet ./...`, and the required
  build.
- Keep business logic tests deterministic and independent from production
  services.

### Web

- Run the applicable lint, tests, typecheck, and production build when web code
  changes.
- Display only data supported by the current backend contract.

### Native automation

- Keep scheduled automation in Go under `internal/automation` with operational
  entry points under `cmd/worker/`; run each business domain's schedule
  through exactly one owning worker process (currently `finance-trading-worker`,
  `finance-english-worker`, `finance-social-worker`, `finance-tvl-worker`) —
  splitting a single worker into per-domain processes for independent
  scaling/resource limits/failure isolation is expected and does not itself
  count as adding "a second schedule owner" below; that phrase means two
  processes racing to own the *same* job, not one job living in its own
  dedicated process.
- Do not add Python automation modules or fork language runtimes from the Go
  worker.
- Keep every domain's scheduler always enabled. Do not add a second process
  that can run the *same* scheduled job as another, and do not add a cutover
  flag for a job's schedule ownership without a tested distributed lease.
- Run native automation Go tests with a hard timeout in GitHub Actions.

### Phase-agent orchestration tooling

- `uv` is required for the Python-backed state and OPS CLIs under
  `tools/phase-agent-orchestrator/`.
- Bootstrap the project with `uv sync --project tools/phase-agent-orchestrator`
  before invoking the executable Python entrypoints in `.agents/scripts/`.
  The entrypoints use the bootstrapped project venv and import the shared
  package directly; no Bash shim or per-call `uv run` indirection is required.
- Keep `tools/phase-agent-orchestrator/pyproject.toml` and `uv.lock` committed together;
  do not introduce another Python package manager for this tooling.

## Completion evidence

A change is complete only when the local checks pass, the commit exists on
GitHub, CI succeeds, Coolify deploys the intended revision when deployment is
required, and production verification passes.
