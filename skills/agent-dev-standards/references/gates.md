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

**Invariant**: every commit message in the range (and a PR title, and a commit message file for the hook) conforms to the [Conventional Commits 1.0.0 specification](https://www.conventionalcommits.org/en/v1.0.0/#summary): subject `type(scope)!?: description` with `type` from the allowed set, a non-empty description, at most the configured subject length; a `!` or a `BREAKING CHANGE:` footer marks a breaking change (either is valid per the spec; when the footer is present the description must be non-empty too); footers follow the `token: value` / `token #value` form. House rules on top of the spec (imperative mood, lowercase description, no trailing period) are configurable and reported separately from spec violations. Read the spec when implementing; do not reconstruct it from memory.
**Config**: the allowed type list in a sibling data file (the single home; `CONTRIBUTING.md` links to it), `MAX_SUBJECT`, the house-rule toggles.
**Failure output**: the offending subject, which rule it broke, and one conforming example.
**Prove it**: run it against the last 20 commits in dry-run mode during Step 4 and report how many would fail; plant one bad subject on a scratch branch.

## The `check` entry point

One command, on the repo's task runner, that local developers and CI call — never the individual scripts, so the two cannot drift.

```
check <any group>       always runs verify-hooks-installed first; refuses if hooks are missing
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
| `docs-gates` | a whitespace / conflict-marker diff check; `verify-hooks-installed` (static part); `check docs`; `verify-doc-pairs` over the PR range with the bypass label mapped to the bypass variable | full history; the base ref; read access to PR labels |

Principles:

- Triggers: every pull request, and pushes to the main branch. Cancel superseded runs of the same ref.
- Every job calls the same commands a developer runs locally. No CI-only incantations except the matrix.
- Docs-only PRs still run `docs-gates` and `commit-convention`; skipping them is what lets docs rot.
- Minimal permissions: read contents, read pull requests (for the label).

## The hook contract

Hooks are the gate that fires *before* a bad commit exists. They are only a gate if every clone has them, so the contract covers installation as much as behavior.

**Behavior**

- **pre-commit**: format check and lint on the *staged* files only; exit non-zero with the fix command. Nothing repo-wide. If a staged file is left unformatted, the commit does not happen — the hook never auto-fixes and continues silently.
- **commit-msg**: `verify-commit-convention --file <message file>`; a non-conforming message aborts the commit with the rule broken and one conforming example.
- Both are tracked in the repository, so they change with the rules they enforce.

**Installation is automatic, never a separate step**

- Wire hook installation into the command a developer already has to run on a fresh clone — the dependency-install lifecycle hook, the bootstrap script, or the task runner's setup target, whichever the research (`stack-research.md`) found the repo uses. Read that mechanism's current docs for how it runs post-install commands. `AGENTS.md#commands` lists that one install command; there is no "then install the hooks" line for anyone to skip.
- The mechanism is the one the repo already has; otherwise the zero-dependency option the VCS itself supports (a tracked hooks directory the VCS is pointed at); a hook framework only if the user prefers one and it can be installed by the same automatic step.

**`verify-hooks-installed`** — one more verify script:

- **Invariant**: the VCS is configured to run the tracked hooks (hooks path or framework installation points at them), the tracked hook files exist and are executable, and the automatic install wiring is still present in the install command.
- **Where it runs**: first thing in the `check` entry point, before any group — `check` refuses to run and prints the install command if hooks are missing locally. In CI it runs the static part (tracked files exist, are executable, wiring present) under `docs-gates`, so nobody can delete the wiring quietly.
- **Prove it**: unset the hooks path on a scratch clone; expect `check` to refuse.

**Bypass**

- The VCS's no-verify flag cannot be disabled client-side; `AGENTS.md#boundaries` forbids it (🚫), and the `commit-convention` and `docs-gates` CI jobs re-run the same checks server-side so a bypassed hook still fails the PR. Say this chain plainly in `CONTRIBUTING.md`: hooks stop the mistake, CI catches the bypass, branch protection blocks the merge.

## Making the gates mandatory

A gate that can be bypassed is a suggestion. Three layers, each covering the previous one's hole:

1. **Hooks** catch the mistake before it becomes a commit, on every clone because installation rides on the install command (see *The hook contract*). They can be skipped with the VCS's no-verify flag, so `AGENTS.md#boundaries` forbids that flag — but that is a rule, not a gate.
2. **CI jobs** re-run every check on the PR and the pushed range, independent of the developer's machine. They cannot be skipped, but a red job does not stop a merge by itself.
3. **Branch protection** on the main branch: every job in the CI contract is a *required status check*, and merging with a failing required check is disabled. Set this up through the hosting platform if you have the permission; otherwise put the exact setting (platform, branch, the six job names) in the report as a `TODO(owner)` and say plainly that until it is done the gates are advisory.

Also require the PR title to pass `verify-commit-convention --title` if the repo squash-merges — the title becomes the commit subject on the main branch.

## Proving the gates (Step 4)

A check nobody has seen fail is decoration. On a scratch branch in the target repo, plant one violation per script, run `check all`, confirm red, revert, delete the branch. Record in the report which gates you proved and which you could not (and why).
