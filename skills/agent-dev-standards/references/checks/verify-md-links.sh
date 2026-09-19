#!/usr/bin/env bash
# verify-md-links: every relative link in a tracked Markdown file resolves to
# an existing file or directory.
#
# Why: the whole doc layout is "one home per fact, link the rest". A broken
# link is a rule an agent can no longer find.
#
# Checks: [text](path), [text](path#anchor), [text](path "title").
# Skips: http(s)://, mailto:, pure #anchors, and lines inside fenced code blocks.
# Anchors themselves are not validated (heading ids differ per renderer).
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

fail=0
checked=0

while IFS= read -r -d '' f; do
  dir=$(dirname "$f")
  in_fence=0
  lineno=0
  while IFS= read -r line || [[ -n "$line" ]]; do
    lineno=$((lineno + 1))
    if [[ "$line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
      in_fence=$((1 - in_fence)); continue
    fi
    [[ $in_fence -eq 1 ]] && continue
    # Extract every ](target) on the line.
    while IFS= read -r target; do
      [[ -z "$target" ]] && continue
      target="${target%% *}"          # drop "title"
      target="${target%%\"*}"
      case "$target" in
        http://*|https://*|mailto:*|\#*|\<*) continue ;;
      esac
      target="${target%%#*}"
      [[ -z "$target" ]] && continue
      checked=$((checked + 1))
      if [[ "$target" == /* ]]; then
        path=".$target"
      else
        path="$dir/$target"
      fi
      if [[ ! -e "$path" ]]; then
        echo "$f:$lineno: broken link -> $target"
        echo "  fix: correct the path or create the target"
        fail=1
      fi
    done < <(printf '%s\n' "$line" | grep -oE '\]\([^)]+\)' | sed -E 's/^\]\(//; s/\)$//' || true)
  done < "$f"
done < <(git ls-files -z -- '*.md')

if [[ $fail -ne 0 ]]; then
  echo "verify-md-links: FAILED"
  exit 1
fi
echo "verify-md-links: ok ($checked links)"
