#!/usr/bin/env bash
# verify-commit-convention: commit subjects (and, optionally, a PR title)
# follow `type(scope)!?: summary` with the allowed type set.
#
# Why: agents and humans both write "update stuff"; a conventional subject
# is the only thing that makes `git log` and the changelog readable later.
#
# Usage:
#   verify-commit-convention.sh <git range>      # e.g. origin/main..HEAD
#   verify-commit-convention.sh --title "<text>" # a PR title
#   verify-commit-convention.sh --file <path>    # commit-msg hook: the message file
#   verify-commit-convention.sh --dry-run <range># report, exit 0
#
# Config: commit-types.txt beside this script (one type per line, # comments).
# Merge commits are ignored. `Revert "..."` and `fixup!/squash!` subjects pass.
set -euo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TYPES_FILE="${TYPES_FILE:-$HERE/commit-types.txt}"
MAX_SUBJECT="${MAX_SUBJECT:-72}"

if [[ -f "$TYPES_FILE" ]]; then
  types=$(grep -vE '^\s*(#|$)' "$TYPES_FILE" | tr -d ' \r' | paste -sd'|' -)
else
  types="feat|fix|docs|refactor|test|chore|ci|perf|build"
fi
# type, optional (scope) of [a-z0-9._/-], optional !, ": ", non-empty summary
pattern="^($types)(\([a-z0-9._/-]+\))?!?: [^ ].*$"

check_subject() {
  local subject="$1" label="$2" errs=()
  case "$subject" in
    "Revert \""*|"fixup! "*|"squash! "*) return 0 ;;
  esac
  [[ "$subject" =~ $pattern ]] || errs+=("does not match '<type>(<scope>)?: <summary>' with type in {${types//|/, }}")
  [[ "$subject" == *. ]] && errs+=("summary ends with a period")
  (( ${#subject} > MAX_SUBJECT )) && errs+=("subject is ${#subject} chars, max $MAX_SUBJECT")
  if [[ ${#errs[@]} -gt 0 ]]; then
    echo "$label: \"$subject\""
    printf '  - %s\n' "${errs[@]}"
    echo "  fix: e.g. 'fix(api): reject empty page tokens' — see CONTRIBUTING.md#commits"
    return 1
  fi
  return 0
}

mode="range"
dry=0
case "${1:-}" in
  --title) mode="title" ;;
  --file)  mode="file" ;;
  --dry-run) dry=1; shift ;;
  "") echo "usage: verify-commit-convention.sh <range> | --title <text> | --file <path> | --dry-run <range>" >&2; exit 2 ;;
esac

fail=0
case "$mode" in
  title)
    check_subject "$2" "PR title" || fail=1
    ;;
  file)
    subject=$(grep -vE '^\s*#' "$2" | sed -n '1p')
    check_subject "$subject" "commit message" || fail=1
    ;;
  range)
    range="$1"
    if ! git rev-list "$range" -- >/dev/null 2>&1; then
      echo "verify-commit-convention: invalid git range '$range'" >&2
      exit 2
    fi
    count=0
    while IFS=$'\t' read -r hash subject; do
      [[ -z "$hash" ]] && continue
      count=$((count + 1))
      check_subject "$subject" "$hash" || fail=1
    done < <(git log --no-merges --format='%h%x09%s' "$range" --)
    if [[ $dry -eq 1 ]]; then
      echo "verify-commit-convention (dry run): $count commits in $range checked; $( [[ $fail -eq 0 ]] && echo 'all conform' || echo 'violations listed above' )"
      exit 0
    fi
    [[ $count -eq 0 ]] && echo "verify-commit-convention: no commits in $range"
    ;;
esac

if [[ $fail -ne 0 ]]; then
  echo "verify-commit-convention: FAILED"
  exit 1
fi
echo "verify-commit-convention: ok"
