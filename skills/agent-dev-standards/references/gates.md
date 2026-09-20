# Gates: what the checks, the entry point, the CI, and the hooks must do

This file is a specification, not an implementation. Write the scripts in the language and convention the target repo already uses for scripting (see `stack-research.md`); if it has none, pick the lowest-dependency option available on the developer machines and the CI runners, and record the choice in the report. The names below are contracts — `AGENTS.md`, `CONTRIBUTING.md`, the PR template, and the postmortem convention refer to them.

## Conventions every verify script follows

- One invariant per script, named `verify-<the-thing-checked>`; **file name = command name = gate name**.
- Exit non-zero on violation. Failure output names the offending path **and the fix command**.
- Configuration at the top of the file or in a sibling data file, never buried in the body. A script that still holds a placeholder refuses to run and says which one.
- Deterministic and fast; anything slow or network-bound is a CI job, not a verify script.
- Range-based scripts accept the range as an argument and default to `<base-ref>...HEAD`.
- Each script has a way to be proven: a dry-run mode or a range argument you can point at a scratch commit that plants the violation.

## The verify scripts

Implement each of these. Add more only when the survey shows a repo-specific invariant worth a gate.

### `verify-module-readmes`

**Invariant**: every module directory in the module registry has a `README.md` containing every required heading.
**Config**: the module registry (one directory per line, the list confirmed in the interview); the required-heading list (must match the *(required)* headings in `templates/module-README.md`, exact English wording, because translated pairs translate the body, not the anchor).
**Failure output**: `path/README.md: missing heading "## X"` or `path/: no README.md`, plus the template path to copy from.
**Prove it**: remove one required heading on a scratch branch; expect red.

### `verify-md-links`

**Invariant**: every relative link and image reference in tracked Markdown files resolves to an existing file (anchors optional; report them only if you also parse headings).
**Config**: none, or an ignore list for generated docs.
**Failure output**: `file.md:line: broken link → target`.
**Prove it**: point one link at a missing file.

### `verify-doc-pairs <range>`

**Invariant**, two parts:
1. *Docs move with code (strict mode)*: for each module in the registry, if a code file under it changed in the range, its `README.md` changed in the same range. Bypass only through an explicit signal (an environment variable set by CI from a PR label whose name the interview fixed, default `docs-not-needed`), and print that the bypass was used.
2. *Translated pairs*: for each configured language, if `X.md` changed then `X.<lang>.md` changed, and vice versa.
**Config**: pair languages; strict on/off; bypass variable name; a code-file exclude pattern (tests, fixtures, generated files).
**Failure output**: `module/: code changed (n files) but README.md did not — update it or set <bypass> with a reason`; `docs/x.md changed but docs/x.<lang>.md did not`.
**Prove it**: change one source file without its README; change one doc without its pair.

### `verify-agents-md-budget`

**Invariant**: the root `AGENTS.md` is within its line and word ceilings (defaults 120 lines / 1,200 words; the interview may change them).
**Config**: `MAX_LINES`, `MAX_WORDS`.
**Failure output**: current figures, the ceilings, and the order of remedies: relocate → condense → raise the ceiling with a reason in the PR.
**Prove it**: pad the file past the ceiling.

### `verify-decision-format`

**Invariant**: every decision record under the decisions directory has the header fields, a `Status:` value that agrees with the lifecycle folder it sits in, every required heading, and a non-empty *Alternatives considered* section.
**Config**: decisions directory; the folder→status mapping and heading list from `templates/decisions-README.md`.
**Failure output**: `docs/decisions/<folder>/<file>: <what is missing or mismatched>`.
**Prove it**: empty the alternatives section of one record; move a record to the wrong folder.

### `verify-commit-convention <range> | --title <text> | --file <path>`

**Invariant**: each commit subject in the range (and a PR title, and a commit message file for the hook) matches `type(scope)!?: summary` with `type` from the allowed set, an imperative lowercase summary, no trailing period, at most the configured length.
**Config**: the allowed type list in a sibling data file (the single home; `CONTRIBUTING.md` links to it), `MAX_SUBJECT`.
**Failure output**: the offending subject, which rule it broke, and one conforming example.
**Prove it**: run it against the last 20 commits in dry-run mode during Step 4 and report how many would fail; plant one bad subject on a scratch branch.

## The `check` entry point

One command, on the repo's task runner, that local developers and CI call — never the individual scripts, so the two cannot drift.

```
check docs              module READMEs, links, decisions, AGENTS.md budget
check pairs [range]     docs moved with code + translated pairs
check commits [range]   commit subjects
check stack             format check, lint, typecheck, test with coverage — the same commands as CI
check all [range]       everything above
```

- Runs every gate in a group and reports all failures, not just the first.
- The stack commands are configuration at the top of the entry point, copied from `AGENTS.md#commands`; it refuses to run `stack` while any is still a placeholder.
- Adding a gate later means dropping a new `verify-*` script beside it and registering it in one group. The postmortem convention relies on this landing spot.
- The directory name is recorded in `AGENTS.md` and never changes afterwards.

## The CI contract

Implement on whatever CI platform the repo uses (see `stack-research.md` §5). Keep these job names; `CONTRIBUTING.md` and `AGENTS.md` refer to them.

| Job | Runs | Needs |
| --- | --- | --- |
| `format` | the format-check command | setup steps |
| `lint` | the lint command | setup steps |
| `typecheck` | the typecheck command — omit the job when the compiler owns it | setup steps |
| `test` | the test-with-coverage command; fails below the threshold | setup steps; a platform matrix only if the project targets several platforms today |
| `commit-convention` | `verify-commit-convention` over the PR's commits and its title; over the pushed range on push | full history; the base ref; the PR title |
| `docs-gates` | a whitespace / conflict-marker diff check; `check docs`; `verify-doc-pairs` over the PR range with the bypass label mapped to the bypass variable | full history; the base ref; read access to PR labels |

Principles:

- Triggers: every pull request, and pushes to the main branch. Cancel superseded runs of the same ref.
- Every job calls the same commands a developer runs locally. No CI-only incantations except the matrix.
- Docs-only PRs still run `docs-gates` and `commit-convention`; skipping them is what lets docs rot.
- Minimal permissions: read contents, read pull requests (for the label).

## The hook contract

- **pre-commit**: format check and lint on the *staged* files only; exit non-zero with the fix command. Nothing repo-wide.
- **commit-msg**: `verify-commit-convention --file <message file>`.
- The mechanism is the one the repo already has; otherwise the zero-dependency option the VCS itself supports, or a hook framework if the user prefers one. Whichever it is, installation is one command in `CONTRIBUTING.md#setup`, and the hooks are tracked in the repository.

## Proving the gates (Step 4)

A check nobody has seen fail is decoration. On a scratch branch in the target repo, plant one violation per script, run `check all`, confirm red, revert, delete the branch. Record in the report which gates you proved and which you could not (and why).
