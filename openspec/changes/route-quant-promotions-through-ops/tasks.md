## 1. OPS Trace Metadata

- [x] 1.1 Add an owner-checked, PLAN-only immutable `trace-origin` operation to `finance-workspace` OPS runtime and verify valid quant metadata, same-change storage, safe path validation, and no research-content duplication with bounded fixture tests.
- [x] 1.2 Verify invalid iteration/instrument/path, missing artifact, wrong owner/phase, and overwrite attempts fail without changing runtime state or backend selection.

## 2. Quant Promotion Contract

- [x] 2.1 Rewrite `/quant-research` around the five result classifications and explicit promotion criteria, verifying non-PROMOTE outcomes remain research-only and PROMOTE creates/reuses OpenSpec before entering canonical OPS.
- [x] 2.2 Preserve Codex/fallback backend gates, model policy, backend immutability, FIX findings, and existing OPS lifecycle references; verify current backend/worker/orchestration suites remain green.
- [x] 2.3 Add bounded static and fixture promotion tests for OpenSpec/OPS same-name identity, trace references, canonical OPS reuse, and no real loop/model/backtest/deploy behavior.

## 3. Source-of-Truth Migration

- [x] 3.1 Mark `raw/handoff_agent.md` legacy/non-authoritative without deleting or moving concurrent history, and verify the staged change contains only the banner hunk for that file.
- [x] 3.2 Update shared quant, delivery, deployment-verification, and domain guidance so OpenSpec tasks and OPS state/archive replace Todo/Dev-done/Verify/Done handoff semantics; run managed-link synchronization and contract searches.
- [x] 3.3 Document RAW/OpenSpec/OPS/Git ownership, promotion criteria, trace example, legacy migration, and archive behavior in README and command contracts; verify documentation assertions pass.

## 4. Validation and Delivery

- [x] 4.1 Run shell syntax, all bounded orchestration/quant/backend/model/promotion suites, JSON validation, strict OpenSpec validation, sync check, and diff check.
- [x] 4.2 Complete the mandatory skill upsert review and verify the updated skills no longer recreate the legacy engineering queue.
- [x] 4.3 Commit only scoped changes, push `main`, verify local/remote SHA equality and successful exact-SHA Agent Contracts, and do not deploy production.
