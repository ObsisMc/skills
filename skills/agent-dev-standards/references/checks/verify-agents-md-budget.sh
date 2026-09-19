#!/usr/bin/env bash
# verify-agents-md-budget: the root AGENTS.md stays within its line and word
# ceiling.
#
# Why: the root file is loaded into every session. Past ~150 lines it costs
# tokens without changing behavior (see docs/engineering-standards.md or the
# landscape notes). When this goes red: relocate → condense → and only then
# raise the ceiling, with the reason in the PR.
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

FILE="${AGENTS_MD:-AGENTS.md}"
MAX_LINES="${MAX_LINES:-120}"
MAX_WORDS="${MAX_WORDS:-1200}"

if [[ ! -f "$FILE" ]]; then
  echo "$FILE: missing"
  echo "  fix: the root instructions file must exist"
  exit 1
fi

lines=$(wc -l < "$FILE" | tr -d ' ')
words=$(wc -w < "$FILE" | tr -d ' ')
fail=0

if (( lines > MAX_LINES )); then
  echo "$FILE: $lines lines, ceiling $MAX_LINES"
  fail=1
fi
if (( words > MAX_WORDS )); then
  echo "$FILE: $words words, ceiling $MAX_WORDS"
  fail=1
fi

if [[ $fail -ne 0 ]]; then
  echo "  fix, in order: (1) relocate sections to docs/ or a subdirectory AGENTS.md,"
  echo "       (2) condense, (3) raise MAX_LINES/MAX_WORDS in $0 with the reason in the PR"
  echo "verify-agents-md-budget: FAILED"
  exit 1
fi
echo "verify-agents-md-budget: ok ($lines/$MAX_LINES lines, $words/$MAX_WORDS words)"
