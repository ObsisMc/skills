#!/usr/bin/env bash
# verify-doc-pairs <git range>: documentation moved with the code.
#
# Two invariants over the files changed in <range>:
#   1. strict mode — code under a module listed in modules.txt changed
#      ⇒ that module's README.md changed too. Bypass: DOCS_NOT_NEEDED=1
#      (CI sets it from the `docs-not-needed` PR label).
#   2. pairs — a Markdown file changed and it has a translated sibling
#      (x.md ↔ x.<lang>.md for each lang in DOC_PAIR_LANGS) ⇒ the sibling
#      changed in the same range.
#
# Why: "update the docs with every change" is the rule most often skipped
# under time pressure, by humans and agents alike. This is the net.
#
# Usage: verify-doc-pairs.sh "origin/main...HEAD"
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# ---- configuration -----------------------------------------------------------
MODULES_FILE="${MODULES_FILE:-$HERE/modules.txt}"
DOC_PAIR_LANGS="${DOC_PAIR_LANGS-}"          # e.g. "zh" or "zh ja"; empty = no pairs
DOCS_STRICT="${DOCS_STRICT-1}"               # 1 = invariant 1 on; 0 = off
DOCS_NOT_NEEDED="${DOCS_NOT_NEEDED-}"        # non-empty = bypass invariant 1
# Paths inside a module that never require a README update (regex on the path
# relative to the module). Tests, fixtures, and snapshots by default.
CODE_EXCLUDE="${CODE_EXCLUDE-(^|/)(tests?|__tests__|spec|fixtures?|snapshots?|testdata)(/|$)|\.(md|txt|snap)$}"
# ------------------------------------------------------------------------------

range="${1:-}"
if [[ -z "$range" ]]; then
  echo "usage: verify-doc-pairs.sh <git range, e.g. origin/main...HEAD>" >&2
  exit 2
fi

mapfile -t changed < <(git diff --name-only "$range" -- | sort -u)
if [[ ${#changed[@]} -eq 0 ]]; then
  echo "verify-doc-pairs: nothing changed in $range"
  exit 0
fi

is_changed() { printf '%s\n' "${changed[@]}" | grep -qxF -- "$1"; }

fail=0

# ---- invariant 1: module code ⇒ module README ---------------------------------
if [[ "$DOCS_STRICT" == "1" && -f "$MODULES_FILE" ]]; then
  while IFS= read -r mod || [[ -n "$mod" ]]; do
    mod="${mod%%#*}"; mod="${mod%"${mod##*[![:space:]]}"}"; mod="${mod#"${mod%%[![:space:]]*}"}"
    [[ -z "$mod" ]] && continue
    mod="${mod%/}"
    code_changed=()
    for f in "${changed[@]}"; do
      [[ "$f" == "$mod/"* ]] || continue
      rel="${f#"$mod/"}"
      [[ "$rel" =~ $CODE_EXCLUDE ]] && continue
      code_changed+=("$f")
    done
    [[ ${#code_changed[@]} -eq 0 ]] && continue
    if is_changed "$mod/README.md"; then continue; fi
    if [[ -n "$DOCS_NOT_NEEDED" ]]; then
      echo "$mod: code changed without README.md — bypassed (docs-not-needed)"
      continue
    fi
    echo "$mod/README.md: not updated although module code changed:"
    printf '    %s\n' "${code_changed[@]}"
    echo "  fix: update Public surface / Invariants / Known limitations in $mod/README.md,"
    echo "       or label the PR docs-not-needed and say why in its Docs section"
    fail=1
  done < "$MODULES_FILE"
fi

# ---- invariant 2: translated pairs -------------------------------------------
for lang in $DOC_PAIR_LANGS; do
  for f in "${changed[@]}"; do
    [[ "$f" == *.md ]] || continue
    base="${f%.md}"
    if [[ "$base" == *".$lang" ]]; then
      # translated file changed; require the original
      orig="${base%."$lang"}.md"
      if [[ -e "$orig" ]] && ! is_changed "$orig"; then
        echo "$orig: not updated although its $lang translation $f changed"
        echo "  fix: the English file is the source of truth — change it too, or revert $f"
        fail=1
      fi
    else
      pair="$base.$lang.md"
      if [[ -e "$pair" ]] && ! is_changed "$pair"; then
        echo "$pair: not updated although $f changed"
        echo "  fix: apply the same change to $pair (same sections, same commit)"
        fail=1
      fi
    fi
  done
done

if [[ $fail -ne 0 ]]; then
  echo "verify-doc-pairs: FAILED"
  exit 1
fi
echo "verify-doc-pairs: ok (${#changed[@]} files in $range)"
