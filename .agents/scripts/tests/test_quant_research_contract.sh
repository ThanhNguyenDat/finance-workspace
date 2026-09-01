#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../../.." && pwd -P)"

fail() {
  printf 'test_quant_research_contract: %s\n' "$1" >&2
  exit 1
}

command_files=(
  "$ROOT_DIR/.claude/commands/quant-research.md"
  "$ROOT_DIR/.claude/commands/quant/codex-off.md"
  "$ROOT_DIR/.claude/commands/quant/codex-on.md"
  "$ROOT_DIR/.claude/commands/quant/codex-auto.md"
  "$ROOT_DIR/.claude/commands/quant/codex-manual.md"
  "$ROOT_DIR/.claude/commands/quant/codex-config.md"
)
for file in "${command_files[@]}"; do
  test -s "$file" || fail "missing or empty command: $file"
  test "$(head -n 1 "$file")" = '---' || fail "missing frontmatter: $file"
  test "$(awk 'NR > 1 && /^---$/ { print NR; exit }' "$file")" != '' \
    || fail "unterminated frontmatter: $file"
done

quant_command="$ROOT_DIR/.claude/commands/quant-research.md"
off_command="$ROOT_DIR/.claude/commands/quant/codex-off.md"
on_command="$ROOT_DIR/.claude/commands/quant/codex-on.md"
auto_command="$ROOT_DIR/.claude/commands/quant/codex-auto.md"
manual_command="$ROOT_DIR/.claude/commands/quant/codex-manual.md"
config_command="$ROOT_DIR/.claude/commands/quant/codex-config.md"
grep -Fq '/loop 20m /quant-research' "$quant_command" || fail 'loop invocation missing'
grep -Fq 'quant-research-state.sh state' "$quant_command" || fail 'quant command does not read state'
grep -Fq 'quant-research-state.sh begin-iteration' "$quant_command" || fail 'quant command does not record iterations'
grep -Fq 'codex_mode=auto' "$quant_command" || fail 'quant command does not select auto behavior'
grep -Fq 'detect-codex-availability.sh' "$quant_command" || fail 'quant command does not invoke the detector'
grep -Fq 'codex_mode=manual' "$quant_command" || fail 'quant command does not suppress manual probing'
grep -Fq 'research_enabled=false' "$quant_command" || fail 'research_enabled gate missing'
grep -Fq 'XAU' "$quant_command" || fail 'XAU priority missing'
grep -Fq 'BTC' "$quant_command" || fail 'BTC priority missing'
grep -Fq 'tối đa 2 local strategy/service containers' "$quant_command" || fail 'container cap missing'
grep -Fq '@.claude/commands/ops/run.md' "$quant_command" || fail 'ops lifecycle reference missing'
grep -Fq 'implementation_backend=claude-fallback' "$quant_command" || fail 'fallback backend missing'
grep -Fq 'verification_mode=claude-fallback-self-review' "$quant_command" || fail 'fallback verification mode missing'
grep -Fq 'codex-off' "$off_command" || fail 'codex-off command missing'
grep -Fq 'codex-on' "$on_command" || fail 'codex-on command missing'
grep -Fq 'Không bắt đầu research' "$off_command" || fail 'codex-off side-effect guard missing'
grep -Fq 'không khởi động lại `/loop`' "$on_command" || fail 'codex-on loop guard missing'
grep -Fq 'quant-research-state.sh codex-auto' "$auto_command" || fail 'codex-auto mode mutation missing'
grep -Fq 'detect-codex-availability.sh' "$auto_command" || fail 'codex-auto immediate probe missing'
grep -Fq 'không retry' "$auto_command" || fail 'codex-auto retry guard missing'
grep -Fq 'quant-research-state.sh codex-manual' "$manual_command" || fail 'codex-manual mutation missing'
grep -Fq 'Không thay đổi `codex_available`' "$manual_command" || fail 'manual availability preservation missing'
grep -Fq 'profile-set <role>' "$config_command" || fail 'profile update contract missing'
grep -Fq 'profiles-reset' "$config_command" || fail 'profile reset-all contract missing'
grep -Fq '`VERIFY` và `FINAL_VERIFY` luôn do Claude độc lập' "$config_command" \
  || fail 'independent Claude verification ownership missing'
grep -Fq 'không chạy Codex' "$config_command" || fail 'config command execution guard missing'

if rg -n 'claude( -p| --print)|claude exec|nested Claude' "$quant_command" >/dev/null; then
  fail 'quant command contains a forbidden nested Claude invocation'
fi
if rg -n 'codex hết quota' "$ROOT_DIR/.claude/commands" "$ROOT_DIR/README.md" >/dev/null \
  || grep -RFq '/loop 20m /quant-research "' "$ROOT_DIR/.claude/commands" "$ROOT_DIR/README.md" \
  || grep -RFq "/loop 20m /quant-research '" "$ROOT_DIR/.claude/commands" "$ROOT_DIR/README.md"; then
  fail 'quota state is embedded in a persistent loop prompt'
fi

grep -Fq 'implementation_backend=codex' "$ROOT_DIR/.claude/commands/ops/run.md" \
  || fail 'ops default backend contract missing'
grep -Fq 'implementation_backend=claude-fallback' "$ROOT_DIR/.claude/commands/ops/run.md" \
  || fail 'ops fallback backend contract missing'
grep -Fq '.ops/**/runtime/' "$ROOT_DIR/.gitignore" || fail 'runtime ignore rule missing'
git -C "$ROOT_DIR" check-ignore -q -- .ops/runtime/quant-research/state.json \
  || fail 'quant runtime state is not ignored'
grep -Fq 'quant-research-state.sh' "$ROOT_DIR/.github/workflows/agent-contracts.yml" \
  || fail 'CI does not reference the quant state helper'
grep -Fq 'test_quant_research_state.sh' "$ROOT_DIR/.github/workflows/agent-contracts.yml" \
  || fail 'CI does not run the quant state test'
grep -Fq 'test_quant_research_contract.sh' "$ROOT_DIR/.github/workflows/agent-contracts.yml" \
  || fail 'CI does not run the quant contract test'

printf '%s\n' 'test_quant_research_contract: all checks passed'
