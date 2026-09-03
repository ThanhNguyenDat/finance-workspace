#!/usr/bin/env bash
set -Eeuo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/hermetic-env.sh"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
fail() { printf 'test_quant_research_contract: %s\n' "$1" >&2; exit 1; }
files=(.claude/commands/quant-research.md .claude/commands/quant/codex-off.md .claude/commands/quant/codex-on.md .claude/commands/quant/codex-auto.md .claude/commands/quant/codex-manual.md .claude/commands/quant/codex-config.md .claude/commands/quant/agent-config.md)
for relative in "${files[@]}"; do file="$ROOT_DIR/$relative"; [[ -s "$file" ]] || fail "missing $relative"; [[ "$(head -n 1 "$file")" = --- ]] || fail "frontmatter missing: $relative"; done
quant="$ROOT_DIR/.claude/commands/quant-research.md"; ops="$ROOT_DIR/.claude/commands/ops/run.md"
grep -Fq 'uv run --project tools/phase-agent-orchestrator run-phase-agent-command quant-research' "$quant" || fail 'manual terminal entrypoint missing'
grep -Fq 'Không gọi' "$quant" && grep -Fq '`begin-iteration`' "$quant" || fail 'double-iteration guard missing'
grep -Fq 'phase-agent-state state' "$quant" || fail 'phase state read missing'
grep -Fq 'research_enabled=false' "$quant" || fail 'research gate missing'
for token in XAU BTC REJECTED NO-CHANGE DATA-ISSUE NEEDS-MORE-RESEARCH PROMOTE defensible trace-origin '@.claude/commands/ops/run.md'; do grep -Fq "$token" "$quant" || fail "quant contract missing $token"; done
if grep -Fq '/loop 20m /quant-research' "$quant"; then fail 'scheduled loop remains documented'; fi
if rg -n 'claude( -p| --print)|codex exec' "$quant" >/dev/null; then fail 'quant prompt invokes provider directly'; fi
grep -Fq 'provider-off codex' "$ROOT_DIR/.claude/commands/quant/codex-off.md" || fail 'Codex off alias not migrated'
grep -Fq 'provider-on codex' "$ROOT_DIR/.claude/commands/quant/codex-on.md" || fail 'Codex on alias not migrated'
grep -Fq 'provider-auto codex' "$ROOT_DIR/.claude/commands/quant/codex-auto.md" || fail 'Codex auto alias not migrated'
grep -Fq 'provider-manual codex' "$ROOT_DIR/.claude/commands/quant/codex-manual.md" || fail 'Codex manual alias not migrated'
grep -Fq 'configure-phase-agents' "$ROOT_DIR/.claude/commands/quant/agent-config.md" || fail 'phase config command missing'
grep -Fq 'run-phase-agent <change> <repository> IMPLEMENT' "$ops" || fail 'OPS implement resolver missing'
grep -Fq 'same-provider-process-separated' "$ops" || fail 'honest verification label missing'
grep -Fq '.ops/**/runtime/' "$ROOT_DIR/.gitignore" || fail 'runtime ignore missing'
git -C "$ROOT_DIR" check-ignore -q -- .ops/runtime/phase-agents/state.json || fail 'phase state not ignored'
printf '%s\n' 'test_quant_research_contract: all checks passed'
