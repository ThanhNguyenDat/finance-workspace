## Context

See `proposal.md` for motivation. The implementation repository is
`../finance-mw`; its Makefile, Compose files, configuration sources, and
health endpoints provide the evidence for the developer guide.

## Goals / Non-Goals

**Goals:**

- Extend one existing developer-facing documentation file in `finance-mw`.
- Derive every documented command and endpoint from the checked-out files.
- Keep the retry dev-only and skip production deployment intentionally.

**Non-Goals:**

- No application code, API, schema, dependency, Compose, CI/CD, or production
  configuration changes.
- No production service startup, restart, mutation, or deployment.

## Decisions

- Extend the repository README unless the worker finds a stronger existing
  documentation convention.
- Inspect configuration provenance and variable names without reading or
  printing environment values.
- The worker may modify only the declared developer documentation file in
  `finance-mw`; the orchestration workspace owns runtime and OpenSpec state.

## Risks / Trade-offs

- [Commands may evolve] → Verify every reference against current repository
  files before final verification.
- [Pre-existing `finance-mw` changes could be mixed into the work] → Preserve
  them and stage only the documentation file if a local commit is created.
