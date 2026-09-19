# Reference check scripts

Copy these into the project's checks directory (default `checks/`, name chosen in the interview), adapt the marked configuration lines, and wire `check` onto the project's task runner. They are plain bash: Git for Windows ships bash, GitHub runners have it, and no language runtime is added to the project. If the project already has a scripting convention in its own language, port them instead of adding bash.

Conventions every script follows (and every future guardrail should):

- One invariant per script, named `verify-<the-thing-checked>`; file name = command name = gate name.
- Exit non-zero on violation. Failure output names the offending path **and the fix**.
- Configuration at the top of the file or in a sibling `*.txt`, never hidden in the body.
- Deterministic and fast; anything slow or network-bound belongs in a CI job, not here.

| Script | Invariant | Config |
| --- | --- | --- |
| `verify-module-readmes.sh` | Every module in `modules.txt` has a `README.md` with the required headings | `modules.txt`, `REQUIRED_HEADINGS` |
| `verify-md-links.sh` | Every relative link in tracked `*.md` resolves | — |
| `verify-doc-pairs.sh <range>` | Module code changed ⇒ module README changed (strict); `x.md` changed ⇒ `x.<lang>.md` changed | `DOC_PAIR_LANGS`, `DOCS_STRICT`, `DOCS_NOT_NEEDED` (bypass), `CODE_EXCLUDE` |
| `verify-agents-md-budget.sh` | Root `AGENTS.md` ≤ `MAX_LINES` / `MAX_WORDS` | `MAX_LINES`, `MAX_WORDS` |
| `verify-decision-format.sh` | Decision records have the header, status/folder agreement, required headings, non-empty alternatives | `DECISIONS_DIR` |
| `verify-commit-convention.sh <range> \| --title <t>` | Commit subjects and PR titles match `type(scope)!?: summary` | `commit-types.txt`, `MAX_SUBJECT` |
| `check <docs\|commits\|all>` | Entry point; groups the above and the stack commands | `STACK_*` commands at the top |

Also ship `modules.txt` (one module directory per line) and `commit-types.txt` (one type per line) beside them.

## Testing the scripts

Each script has a dry-run mode or accepts a range, so you can prove it fails: create the violation on a scratch branch, watch red, revert. Do this once during initialization (SKILL.md Step 4) and record in the report which scripts you proved.

## Adding a guardrail later

A postmortem or a repeated agent mistake lands here as a new `verify-*` script. Register it in `check`, in `.github/workflows/ci.yml` under `docs-gates` (or a fitting job), and back-link the postmortem or decision in the script's header comment.
