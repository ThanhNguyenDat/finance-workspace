## Context

See `proposal.md` for motivation. `utils/config.py` already has
`resolve_account_list(env_var, config_section)` reading `<section>.accounts`
from `config.yaml`; this adds a sibling read for `<section>.scope`.
`cli/_shared.py::build_arg_parser` already centralizes flags shared by both
commands (`--cwd`, `--timeout-seconds`, `--model`, `--effort`); `--role`
joins that list.

## Goals / Non-Goals

**Goals:**
- Purely advisory: a mismatch is only ever a printed line, never a
  behavior change to the turn or its exit code.
- Zero behavior change when `--role` is omitted or `scope` is unconfigured
  — this is opt-in on both sides (the flag and the config key).

**Non-Goals:**
- Not enforcing role/provider matching (rejected explicitly in
  `proposal.md` — a mismatch is a valid fallback, not an error).
- Not inferring `--role` automatically from context (prompt content,
  calling command, etc.) — the operator or calling command states it
  explicitly, consistent with `--change` in
  `scope-orchestrator-logs-by-change` (no magic inference anywhere in this
  tool).
- Not adding an env var override for `scope` (unlike `accounts`, which has
  `ORCHESTRATOR_*_ACCOUNTS`) — `scope` is a standing per-machine policy
  declaration, not something that needs a quick one-off override the way
  an account list does; `config.yaml` alone is sufficient.

## Decisions

**Warning goes to stderr via a new `_shared.py::emit_warning`, not
`emit_error`**: reusing `emit_error` would make a purely advisory message
indistinguishable from an actual turn failure to anything parsing stderr or
the JSONL log (where `emit_error` writes `{"type": "error", ...}`).
`emit_warning` writes `{"type": "warning", ...}` when a `log_path` is
available (from `scope-orchestrator-logs-by-change`, if applied first) or
just prints to stderr otherwise, so a future log viewer can visually
distinguish "the provider did something outside its usual scope" from "the
turn failed."

**`--role` uses `choices=[...]` in argparse**: fixed to the five
`CLAUDE.md` phase names (lowercased) rather than a free-form string,
because these are enumerated, well-known values shared with the role
boundary CLAUDE.md/AGENTS.md already define — unlike `--change`, which
names an open-ended, caller-defined identifier and stays free-form
(kebab-case-validated, not a fixed enum).

**Scope-mismatch check runs before `start_turn`, not wrapped around it**:
the warning is pure output with no side effects on control flow, so it is
emitted once, synchronously, immediately after argument parsing and before
`provider.run_turn(...)` is called — no need to thread it through
`BaseProvider` or any provider-specific code.

## Risks / Trade-offs

- **[Risk]** An operator could come to rely on the warning as if it were
  enforcement, then be surprised nothing stops a genuinely wrong call. →
  **Mitigation**: the warning text itself states the scope explicitly
  rather than implying an error, and `proposal.md`/`README.md` document
  plainly that this never blocks.
- **[Risk]** `scope` in `config.yaml` could drift out of sync with
  `CLAUDE.md`'s role boundary if one is edited without the other (the same
  two-sources-of-truth risk `retire-phase-agent-coordinator-docs` fixed
  elsewhere). → **Mitigation**: `config.yaml` is gitignored and
  machine-local by design (account paths must not be shared); `scope` is
  an optional, advisory mirror of shared policy for local convenience, not
  a second authoritative copy — `README.md` states `CLAUDE.md`/`AGENTS.md`
  remain the source of truth for the role boundary itself.
