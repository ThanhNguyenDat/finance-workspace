#!/usr/bin/env bash
set -Eeuo pipefail

# Keep each tool's OpenSpec files local while sharing the remaining skills/rules.
# Run this script again after adding or removing entries under .agents/skills or
# .agents/rules.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd -P)"
AGENTS_DIR="$ROOT_DIR/.agents"

TOOLS=(.claude .kimi-code .opencode)
CHECK_ONLY=false

case "${1-}" in
  '') ;;
  --check) CHECK_ONLY=true ;;
  *)
    printf 'usage: %s [--check]\n' "$0" >&2
    exit 2
    ;;
esac

sync_entries() {
  local source_dir="$1"
  local target_dir="$2"
  local link_prefix="$3"
  local source name target raw

  if [ ! -d "$target_dir" ]; then
    if "$CHECK_ONLY"; then
      printf 'missing target directory: %s\n' "$target_dir" >&2
      return 1
    fi
    mkdir -p -- "$target_dir"
  fi

  # Remove only stale symlinks previously created by this script.
  for target in "$target_dir"/*; do
    [ -L "$target" ] || continue
    raw="$(readlink -- "$target")"
    case "$raw" in
      "$link_prefix"/*)
        if [ ! -e "$target" ]; then
          if "$CHECK_ONLY"; then
            printf 'stale link: %s -> %s\n' "$target" "$raw" >&2
            return 1
          fi
          unlink -- "$target"
          printf 'removed stale link: %s\n' "$target"
        fi
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
    expected="../../.agents/${source_dir#"$AGENTS_DIR/"}/$name"

    if [ -e "$target" ] || [ -L "$target" ]; then
      if [ -L "$target" ]; then
        raw="$(readlink -- "$target")"
        if [ "$raw" != "$expected" ]; then
          printf 'incorrect link: %s -> %s (expected %s)\n' \
            "$target" "$raw" "$expected" >&2
          return 1
        fi
      elif "$CHECK_ONLY"; then
        printf 'real local entry blocks shared link: %s\n' "$target" >&2
        return 1
      fi
      continue
    fi

    if "$CHECK_ONLY"; then
      printf 'missing link: %s (expected -> %s)\n' "$target" "$expected" >&2
      return 1
    fi

    ln -s "$expected" "$target"
    printf 'linked %s -> %s\n' "$target" "$expected"
  done
}

status=0
for tool in "${TOOLS[@]}"; do
  sync_entries "$AGENTS_DIR/skills" "$ROOT_DIR/$tool/skills" "../../.agents/skills" || status=1
  sync_entries "$AGENTS_DIR/rules" "$ROOT_DIR/$tool/rules" "../../.agents/rules" || status=1
done

if [ "$status" -ne 0 ]; then
  if "$CHECK_ONLY"; then
    printf '%s\n' 'Agent skill/rule links need synchronization.' >&2
  else
    printf '%s\n' 'Agent skill/rule synchronization failed.' >&2
  fi
  exit "$status"
fi

if "$CHECK_ONLY"; then
  printf '%s\n' 'Agent skill/rule links are synchronized.'
else
  printf '%s\n' 'Agent skill/rule links are up to date.'
fi
