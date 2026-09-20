# Template: CONTRIBUTING.md

For humans and agents alike. Setup, branches, commits, PRs, and how to run the checks. Commands appear here *and* in `AGENTS.md`; to keep one home, `AGENTS.md` carries the check commands and this file carries setup and workflow, linking the other way for commands.

---

```markdown
# Contributing

## Setup

```sh
<<clone / install / bootstrap commands, exactly as run>>
<<hook install command — whatever mechanism the research chose>>
```

Hook installation is part of setup, not optional: the hooks run `<<format>>` and `<<lint>>` on staged files and check each commit message.

Day-to-day commands: [AGENTS.md#commands](AGENTS.md#commands).

## Branches

Short, hyphenated, at most <<three>> words, describing the change: `session-recovery`, `fix-scroll-state`. No slashes, no `feat/`-style prefixes — the commit type carries that.

<<If the repo uses a different scheme (e.g. `user/topic`), state it here instead.>>

## Commits

Format: `type(scope): summary` — [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)

- `type` ∈ `<<feat | fix | docs | refactor | test | chore | ci | perf | build>>`
- `scope` optional; the module or area (`core`, `api`, `cli`, `docs`).
- `summary`: imperative, lowercase, no trailing period, ≤ 72 characters.
- Body (optional) explains *why* when the diff does not. Reference issues in the footer.
- Breaking change: `type(scope)!: summary` and a `BREAKING CHANGE:` footer.

Examples:

```
feat(core): add retry policy to session runner
fix(api): reject empty page tokens instead of returning page 1
docs: update decision index for single-writer store
refactor(adapters)!: drop the legacy csv reader
```

The `commit-msg` hook rejects a non-conforming subject; CI's `commit-convention` job checks every commit in the PR and the PR title, and is a required check on `<<main>>`. Do not bypass with `--no-verify` — fix the message.

## Pull requests

- One PR per independent change. Split a refactor from the feature that needed it; fix the introducing PR rather than patching forward.
- Title follows the commit format.
- Fill the template: **Problem**, **Change**, **Evidence** (every check you ran, with results; every check you did not run, with why), **Docs** (which READMEs / decisions changed, or `docs-not-needed` with a reason), **Decision** (link, or "none needed").
- Keep the body current as the PR evolves; reviewers read the body, not the commit list.
- Draft PRs are welcome for early feedback; mark them.

## Running the checks locally

```sh
<<task-runner>> check docs      # module READMEs, links, doc pairs, decisions, AGENTS.md budget
<<task-runner>> check commits   # commit subjects on this branch vs <<main>>
<<task-runner>> check all       # everything CI runs
```

CI runs the same entry points. A green local `check all` predicts a green CI, except for the platform matrix and anything listed as CI-only in `<<CI definition path>>`.

## Documentation

Every behavior change updates the owning module's README in the same commit; the docs gate fails the PR otherwise. <<If pairs:>> `README.<<lang>>.md` is updated with its English original — same sections, same commit.

Design choices get a record in [docs/decisions/](docs/decisions/README.md). Escaped bugs that clear the bar get a [postmortem](docs/postmortem/README.md).

## Dependencies

Adding one is an *ask first* action: say what it replaces and what it costs. Use `<<package manager add command>>` so lockfiles stay consistent; never hand-edit the manifest.

## Security

Never commit secrets, tokens, or real user data — including in tests, fixtures, and logs. Use `<<.env.example / secret placeholder convention>>`. Report vulnerabilities via <<SECURITY.md / contact>>, not a public issue.
```

---

## Notes for the generator

- Commit types: keep the repo's existing set if `git log` shows one; otherwise the list above. The same list is the config of `verify-commit-convention` — one home means the script reads it from a data file in the checks directory, and this file links there rather than duplicating. If you keep the list here for readability, the script's list is authoritative and this file says so.
- Branch naming: record what the repo actually does. Do not impose opencode's three-word rule on a repo that uses `feature/…` — but do write the rule down, whichever it is.
- If a `CONTRIBUTING.md` exists, merge: keep its voice, add the missing sections (Commits with examples, Evidence expectation, Running the checks, Documentation).
