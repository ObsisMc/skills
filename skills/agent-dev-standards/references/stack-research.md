# Researching the project's toolchain

This skill names no languages, tools, CI platforms, or hook frameworks. The toolchain is a fact about the target repository and about the ecosystem *at the time you run*, so establish it by investigation, not from memory. Everything you put into `AGENTS.md#commands`, the CI configuration, and the hooks comes out of this research, and Step 4 of the workflow executes it.

## 1. The roles to fill

Whatever the language, the standards need a command for each role below. Fill the table for the target repo before generating anything; leave a role empty only with a reason the report will carry.

| Role | What the command must do | Empty is acceptable when |
| --- | --- | --- |
| Install | Reproduce the dev environment from a clean checkout | never |
| Format check / format fix | Report (and separately, apply) canonical formatting; exit non-zero on drift | the language has no formatter culture — say so |
| Lint | Static checks beyond formatting; exit non-zero on findings | rarely |
| Typecheck | Type analysis as a separate step | the compiler already owns it in the build/test step |
| Test subset | Run the tests for one module, fast | never |
| Test with coverage | Full suite with a measured coverage figure and a threshold that fails the run | never |
| Task runner | The thing `check <group>` hangs on so local and CI invoke one name | none exists and the user declines to add one — then document the direct invocation |
| Hook mechanism | Runs format + lint on staged files and validates each commit message; installs from the setup step; travels with the repo | never |
| CI platform | Runs the same commands on every PR and push to the main branch | the repo has no hosted CI — then generate the local `check all` only and say so |

## 2. Where the evidence lives

Read the repo before reading anything else. In order:

1. **Manifests and lockfiles** — they name the language, package manager, and often the dev tools (dev-dependency sections, tool configuration tables).
2. **Tool configuration files** at the root and in the manifest — a formatter, linter, or type checker that has a config file is *the* tool for that role. Do not add a competitor; two formatters fight and the loser's config rots.
3. **Existing CI definitions** — they hold the commands the maintainers already trust, the platform matrix, and the setup steps. Reuse them verbatim where they still pass.
4. **Existing hooks and hook-framework configs** — the mechanism the repo already has wins over any default.
5. **Task-runner files** (whatever the ecosystem uses: script tables in the manifest, a task file, a build file) — the `check` entry point goes here.
6. **`git log`** — the current commit convention and the last time each command was touched.
7. **Package documentation of the tools found** — check the *current* docs for the invocation flags (check mode vs. fix mode, coverage output format, threshold flags). Flags change between major versions; a flag remembered from training data is a guess until the tool's `--help` or docs confirm it.

## 3. When a role has no tool

If the repo fills a role with nothing, you have to choose one. Do not pick from memory. Research in this order and record the evidence in the report:

1. What the language's own tooling or foundation ships or recommends today.
2. What the repo's direct dependencies and any sibling repos by the same owner use.
3. What the current ecosystem consensus is — read the tool's docs and its recent release notes, not a years-old comparison.

Prefer the option with the fewest new runtimes, the smallest config footprint, and a check mode that exits non-zero. Present the pick as a proposal in the interview (Step 2) with one line of evidence; the user may already have an opinion.

## 4. Deriving the concrete commands

For every role, produce the exact command line with flags, then **run it** on the current tree. Record three things per command: what it does, the fix counterpart (for format and lint), and whether it passed. A command that fails on the current tree is fixed, dropped, or reported by name — never shipped silently.

Where a command needs a value from the interview (coverage threshold, base branch, checks directory), fill it now; `<<placeholders>>` never reach the output.

## 5. CI and hooks: implement the contract, not a template

`gates.md` describes the *contract* for the CI pipeline (job names, what each runs, what history it needs) and for the hooks (what runs at pre-commit, what runs at commit-msg). Implement that contract on the platform the repo uses:

- Read the platform's current documentation for the syntax of jobs, matrices, caching, base-ref access, and label access. Do not assume the action / orb / template versions you remember are current — look them up or copy from the repo's existing CI.
- Every CI job runs the same command a developer runs locally, taken from `AGENTS.md#commands`. No CI-only incantations except the platform matrix.
- Hooks are fast and staged-only; anything repo-wide stays in CI. The hook install command is part of `CONTRIBUTING.md#setup`.

## 6. Module detection

Modules are the directories that deserve a README contract. Derive them from the layout the language convention and the repo actually use (a package directory, a workspace member, a top-level directory under the source root). Skip generated, vendored, migration, and cache directories — list those as protected paths in `AGENTS.md#boundaries` instead. Confirm the list with the user in the interview; it becomes the module registry the docs gate reads.

## 7. Language-specific engineering rules

`docs/engineering-standards.md` may carry up to three language-specific rules. Pick them from what the survey shows the repo actually gets wrong (lint findings, patterns in recent diffs, past bug fixes in `git log`), not from a generic list. Each rule needs a Good/Bad example written in the project's language.
