#!/usr/bin/env bash
# verify-decision-format: every decision record has the header, a Status that
# agrees with its lifecycle folder, the required headings for that lifecycle,
# and a non-empty "Alternatives considered".
#
# Why: a decision without its alternatives is re-litigated; an implemented
# record still written as a plan misleads the next reader about what shipped.
#
# Layout checked: $DECISIONS_DIR/{proposed,implemented,rejected}/yyyy-mm-dd-topic.md
set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
DECISIONS_DIR="${DECISIONS_DIR:-docs/decisions}"

if [[ ! -d "$DECISIONS_DIR" ]]; then
  echo "verify-decision-format: $DECISIONS_DIR not found"
  echo "  fix: create it with proposed/ implemented/ rejected/ and a README.md"
  exit 1
fi

fail=0
count=0

has_heading() { grep -qE "^## $2([[:space:]]|$)" "$1"; }

section_nonempty() {
  # $1 file, $2 heading: true when at least one non-blank line sits between the
  # heading and the next "## " heading (or EOF).
  awk -v h="## $2" '
    $0 == h || index($0, h " ") == 1 { inside = 1; next }
    inside && /^## / { exit }
    inside && NF > 0 { found = 1; exit }
    END { exit found ? 0 : 1 }
  ' "$1"
}

for lifecycle in proposed implemented rejected; do
  dir="$DECISIONS_DIR/$lifecycle"
  [[ -d "$dir" ]] || { echo "$dir: missing folder"; echo "  fix: mkdir -p $dir && touch $dir/.gitkeep"; fail=1; continue; }
  for f in "$dir"/*.md; do
    [[ -e "$f" ]] || continue
    count=$((count + 1))
    name=$(basename "$f")
    errs=()

    [[ "$name" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*\.md$ ]] \
      || errs+=("file name must be yyyy-mm-dd-kebab-topic.md")

    head -n1 "$f" | grep -qE '^# Decision: .+' \
      || errs+=("line 1 must be '# Decision: <title>'")

    status_line=$(grep -m1 -E '^Status: ' "$f" || true)
    case "$status_line" in
      "Status: proposed")      status=proposed ;;
      "Status: implemented")   status=implemented ;;
      "Status: rejected — "*|"Status: rejected - "*) status=rejected ;;
      "")                      status=""; errs+=("missing 'Status:' line") ;;
      *)                       status=""; errs+=("Status must be 'proposed', 'implemented', or 'rejected — <reason>' (got: $status_line)") ;;
    esac
    [[ -n "$status" && "$status" != "$lifecycle" ]] \
      && errs+=("Status '$status' does not match folder '$lifecycle' — move the file or fix the line")

    has_heading "$f" "Problem" || errs+=("missing '## Problem'")
    has_heading "$f" "Alternatives considered" || errs+=("missing '## Alternatives considered'")
    if has_heading "$f" "Alternatives considered" && ! section_nonempty "$f" "Alternatives considered"; then
      errs+=("'## Alternatives considered' is empty — record what the decision beat")
    fi

    case "$lifecycle" in
      implemented)
        has_heading "$f" "Decision" || errs+=("missing '## Decision'")
        has_heading "$f" "Consequences" || errs+=("missing '## Consequences'")
        for banned in "Proposal" "Plan" "Migration plan" "Acceptance criteria"; do
          has_heading "$f" "$banned" && errs+=("'## $banned' is proposal-era — rewrite as present-tense Decision/Consequences")
        done
        ;;
      proposed)
        has_heading "$f" "Proposal" || errs+=("missing '## Proposal'")
        has_heading "$f" "Acceptance criteria" || errs+=("missing '## Acceptance criteria'")
        has_heading "$f" "Risks" || errs+=("missing '## Risks'")
        ;;
      rejected)
        has_heading "$f" "Proposal" || errs+=("missing '## Proposal' (a rejected record is the frozen proposal)")
        ;;
    esac

    if [[ ${#errs[@]} -gt 0 ]]; then
      echo "$f:"
      printf '  - %s\n' "${errs[@]}"
      echo "  fix: see $DECISIONS_DIR/README.md#format"
      fail=1
    fi
  done
done

if [[ $fail -ne 0 ]]; then
  echo "verify-decision-format: FAILED"
  exit 1
fi
echo "verify-decision-format: ok ($count records)"
