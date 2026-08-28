## Context

See `proposal.md` for the motivation. The implementation repository is
`../finance-mw`, which already contains the Go service Make targets, local
configuration files, Compose definitions, and health endpoints needed to
describe development startup without changing runtime behavior.

## Goals / Non-Goals

**Goals:**

- Add one concise developer-facing section to an existing `finance-mw`
  documentation file.
- Derive every documented command and endpoint from repository evidence.
- Keep the workflow dev-only and leave production deployment intentionally
  skipped.

**Non-Goals:**

- No application code, API, schema, dependency, Compose, CI/CD, or production
  configuration changes.
- No production service startup, restart, mutation, or deployment.

## Decisions

- **Use existing developer documentation:** extend the repository's existing
  README rather than creating a parallel guide, so local instructions remain
  discoverable at the repository entry point. A dedicated file is an
  acceptable fallback only if the worker finds a stronger existing convention.
- **Evidence-first commands:** use Makefile targets, Compose commands, and
  health paths that are present in the checkout. Do not invent dependency
  names, environment values, or probe URLs.
- **Documentation-only verification:** inspect the final diff and run the
  narrowest repository checks needed to prove that only documentation changed;
  do not start services or touch production state for this smoke test.

## Risks / Trade-offs

- [Repository instructions may evolve] → Tie each command to current files and
  verify the references against the checked-out Makefile, Compose, and config
  sources before archiving.
- [Existing user changes in `finance-mw` could be mixed into the smoke test] →
  preserve them and stage only the documentation file if a local commit is
  created.
