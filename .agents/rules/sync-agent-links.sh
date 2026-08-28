#!/usr/bin/env bash
set -Eeuo pipefail

# Keep each tool's OpenSpec files local while sharing the remaining skills/rules.
# Run this script again after adding or removing entries under .agents/skills or
# .agents/rules.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
AGENTS_DIR="$ROOT_DIR/.agents"

TOOLS=(.claude .kimi-code .opencode)

sync_entries() {
  local source_dir="$1"
  local target_dir="$2"
  local link_prefix="$3"
  local source name target raw

  mkdir -p -- "$target_dir"

  # Remove only stale symlinks previously created by this script.
  for target in "$target_dir"/*; do
    [ -L "$target" ] || continue
    raw="$(readlink -- "$target")"
    case "$raw" in
      "$link_prefix"/*)
        [ -e "$target" ] || unlink -- "$target"
        ;;
    esac
  done

  for source in "$source_dir"/*; do
    [ -e "$source" ] || continue
    name="${source##*/}"

    case "$name" in
      openspec*) continue ;;
    esac

    target="$target_dir/$name"
    [ -e "$target" ] || [ -L "$target" ] && continue

    ln -s "../../.agents/${source_dir#"$AGENTS_DIR/"}/$name" "$target"
    printf 'linked %s -> %s\n' "$target" "$(readlink -- "$target")"
  done
}

for tool in "${TOOLS[@]}"; do
  sync_entries "$AGENTS_DIR/skills" "$ROOT_DIR/$tool/skills" "../../.agents/skills"
  sync_entries "$AGENTS_DIR/rules" "$ROOT_DIR/$tool/rules" "../../.agents/rules"
done

printf '%s\n' 'Agent skill/rule links are up to date.'
