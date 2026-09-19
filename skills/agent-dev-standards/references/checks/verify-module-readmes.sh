#!/usr/bin/env bash
# verify-module-readmes: every module directory listed in modules.txt has a
# README.md carrying the required contract headings.
#
# Why: the root AGENTS.md tells agents to read a module's README before editing
# it; that rule is only worth something if the README exists and has the
# sections the Definition of Done refers to.
#
# Config: modules.txt beside this script (one path per line, # comments).
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
MODULES_FILE="${MODULES_FILE:-$HERE/modules.txt}"

# Headings the module README template marks (required). Matched at line start,
# case-insensitive, so "## Public surface" and "## Public Surface" both pass.
REQUIRED_HEADINGS=(
  "Public surface"
  "Invariants"
  "Allowed dependencies"
  "How to test"
  "Known limitations"
)

if [[ ! -f "$MODULES_FILE" ]]; then
  echo "verify-module-readmes: $MODULES_FILE not found." >&2
  echo "  fix: list one module directory per line in $MODULES_FILE" >&2
  exit 2
fi

fail=0
count=0
while IFS= read -r mod || [[ -n "$mod" ]]; do
  mod="${mod%%#*}"; mod="${mod%"${mod##*[![:space:]]}"}"; mod="${mod#"${mod%%[![:space:]]*}"}"
  [[ -z "$mod" ]] && continue
  mod="${mod%/}"
  count=$((count + 1))
  if [[ ! -d "$mod" ]]; then
    echo "$mod: listed in modules.txt but is not a directory"
    echo "  fix: remove the line or correct the path"
    fail=1; continue
  fi
  readme="$mod/README.md"
  if [[ ! -f "$readme" ]]; then
    echo "$readme: missing"
    echo "  fix: create it with the headings: ${REQUIRED_HEADINGS[*]/#/## }"
    fail=1; continue
  fi
  for h in "${REQUIRED_HEADINGS[@]}"; do
    if ! grep -qiE "^## ${h}([[:space:]]|$)" "$readme"; then
      echo "$readme: missing heading '## $h'"
      echo "  fix: add the section (write 'None known.' under Known limitations if that is true)"
      fail=1
    fi
  done
done < "$MODULES_FILE"

if [[ $count -eq 0 ]]; then
  echo "verify-module-readmes: modules.txt lists no modules" >&2
  exit 2
fi

if [[ $fail -ne 0 ]]; then
  echo "verify-module-readmes: FAILED"
  exit 1
fi
echo "verify-module-readmes: ok ($count modules)"
