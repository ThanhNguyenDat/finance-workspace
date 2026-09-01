## 1. Persistent mode and state migration

- [x] 1.1 Upgrade quant state to schema version 2 with
  `codex_mode=auto|manual`, default new state to manual/available, and atomically
  migrate valid v1 state to manual mode without changing existing values;
  verify migration and malformed/unsupported-state preservation in fixtures.
- [x] 1.2 Add atomic operations for selecting auto, selecting manual without
  changing availability, explicit on/off manual overrides, and detected
  availability updates that preserve auto mode; verify every transition and
  lock-safety behavior in the state test.
- [x] 1.3 Add validated atomic inspect/update/reset operations for probe,
  implement, fix, and fix-fallback model/effort profiles; verify role isolation,
  defaults, invalid input rejection, and v1 migration fixtures.

## 2. Bounded availability detector

- [x] 2.1 Add a finance-workspace detector script that validates dependencies
  and timeout configuration, runs exactly one isolated `codex exec` probe with
  the installed CLI's supported yolo-equivalent flag, classifies it with the
  existing result classifier, and removes private temporary logs; verify
  `bash -n` passes and no repository/additional-directory access is granted.
- [x] 2.2 Route only `success` and `global-quota-exhausted` to detected-result
  state mutations that preserve auto mode; return an inconclusive result without
  changing the last resolved availability for every other class; verify
  before/after values using offline fake-Codex fixtures.
- [x] 2.3 Make the detector consume only the persisted probe profile and make
  the Codex phase runner consume implement, primary-fix, and fallback-fix
  profiles independently while preserving explicit environment override
  precedence; verify effective model/effort arguments and worker metadata.

## 3. Claude commands and iteration integration

- [x] 3.1 Add `.claude/commands/quant/codex-auto.md` to persist auto mode and
  probe immediately, plus `.claude/commands/quant/codex-manual.md` to persist
  manual mode without changing resolved availability; verify valid frontmatter,
  Vietnamese output, and guards against research/loop/runtime-log side effects.
- [x] 3.2 Update `codex-on.md` and `codex-off.md` to act as manual overrides,
  and update `/quant-research` to probe exactly once at iteration start only
  when mode is auto, re-read resolved state, and continue on inconclusive probe;
  verify static contracts cover mode selection and no recursive scheduling.
- [x] 3.3 Extend quant Agent Contracts with fake Codex cases
  for success, explicit global quota, generic 429, model-local failure, timeout,
  missing executable, repeated auto iterations, manual probe suppression, and
  last-value preservation; verify tests never contact a real Codex or Claude
  service and every invocation is bounded.
- [x] 3.4 Add `.claude/commands/quant/codex-config.md` for safe profile display,
  per-role update, per-role reset, and reset-all; verify invalid roles/models/
  efforts fail without mutation and VERIFY/FINAL_VERIFY remain Claude-owned.

## 4. Documentation and verification

- [x] 4.1 Update current `quant-research-control` and `codex-worker-policy`
  specs plus applicable quant skill guidance to document auto mode while
  preserving explicit overrides and active-backend immutability; verify shared
  links remain synchronized.
- [x] 4.2 Run changed-script syntax checks, all bounded Agent Contract suites,
  changed-skill validation, strict OpenSpec validation, link synchronization,
  and `git diff --check`; verify all commands exit successfully and no
  platform-native OpenSpec command or skill implementation changed.
