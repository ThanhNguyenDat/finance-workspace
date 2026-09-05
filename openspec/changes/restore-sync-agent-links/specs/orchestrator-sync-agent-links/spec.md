## Purpose

Keep `.agents/rules/` and `.agents/skills/` as the single source of truth
for shared Finance knowledge by mirroring them into each agent-native tool's
own directory as symlinks, and let an operator or CI detect drift without
mutating anything.

## ADDED Requirements

### Requirement: sync-agent-links mirrors shared skills and rules
The system SHALL provide a `sync-agent-links` command that, for each
supported agent-native tool directory, creates a relative symlink for every
entry directly under `.agents/skills/` and `.agents/rules/` into that tool's
own `skills/`/`rules/` directory, skipping `.openspec-target` and any entry
whose name starts with `openspec`.

#### Scenario: A shared skill has no link yet
- **WHEN** `.agents/skills/<name>` exists and the tool's `skills/<name>` does
  not
- **THEN** `sync-agent-links` creates `skills/<name>` as a relative symlink
  to `.agents/skills/<name>`

#### Scenario: An openspec-prefixed skill is left alone
- **WHEN** `.agents/skills/<name>` starts with `openspec`
- **THEN** `sync-agent-links` does not create or modify any link for it

### Requirement: --check reports drift without changing anything
`sync-agent-links --check` SHALL report every missing link, incorrect link,
stale link, and real-file collision it finds, and SHALL exit non-zero when
any are found, without creating, removing, or modifying any file or symlink.

#### Scenario: Drift exists
- **WHEN** a shared skill or rule has no corresponding link, or an existing
  link points somewhere other than the current `.agents/` entry
- **THEN** `--check` reports it and exits non-zero, and the filesystem is
  unchanged after the command returns

#### Scenario: Everything is already in sync
- **WHEN** every expected link already exists and points correctly
- **THEN** `--check` exits 0

### Requirement: A real file blocking a shared link is reported, not overwritten
When a tool's `skills/<name>` or `rules/<name>` exists as a real file or
directory (not a symlink) where a shared link is expected, `sync-agent-links`
SHALL report it as an error and leave it untouched, in both `--check` and
normal (write) mode.

#### Scenario: A real file occupies a shared link's expected path
- **WHEN** `sync-agent-links` runs (with or without `--check`) and finds a
  real file at the expected link path
- **THEN** it prints an error naming that path and exits non-zero, without
  deleting or modifying that file

### Requirement: Stale links are only removed in write mode
A symlink under a tool's `skills/`/`rules/` directory that points into
`.agents/` but no longer resolves (its `.agents/` target was deleted) SHALL
be reported by `--check` and removed by a normal (non-`--check`) run.

#### Scenario: A shared entry was deleted from .agents/
- **WHEN** a tool directory still has a symlink to a `.agents/skills/<name>`
  or `.agents/rules/<name>` that no longer exists
- **THEN** `--check` reports it as a stale link without removing it, and a
  normal run removes it
