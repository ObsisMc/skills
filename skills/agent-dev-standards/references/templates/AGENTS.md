# Template: root AGENTS.md

Target: ≤ 120 lines, ≤ 1,200 words. Every rule is 1–3 lines and links its home. Replace every `<<...>>`. Delete any section that does not apply rather than leaving it generic. The sections marked *(keep)* are load-bearing for the process; the others are shaped by the repo.

Tone: imperative, concrete, no adjectives. Explain a rule's reason only when a one-clause reason prevents a predictable mistake.

---

```markdown
# AGENTS.md

<<One sentence: what this project is and who uses it.>> Read [docs/architecture.md](docs/architecture.md) before changing anything under `<<src/ or packages/>>`; read the affected module's `README.md` before editing it.

## Layout

| Path | Owns |
| --- | --- |
| `<<src/core/>>` | <<one line>> |
| `<<src/api/>>` | <<one line>> |
| `docs/` | Standards, decisions, postmortems ([index](docs/README.md)) |
| `<<checks/>>` | Verify scripts; `<<task-runner>> check` runs them |

## Commands

```sh
<<install>>                 # e.g. pnpm install / uv sync
<<format-check>>            # e.g. ruff format --check . — fix with: <<format-fix>>
<<lint>>
<<typecheck>>               # delete the line if the compiler owns it
<<test-subset>>             # e.g. pytest tests/<module> -q; full suite is CI's job
<<check-docs>>              # module READMEs, links, doc pairs, decisions, budget
<<check-all>>               # everything CI runs, locally
```

Run the subset that matches what you changed. Do not run the full suite for a one-module change; CI owns exhaustive coverage. Do not repeat a check that already passed on the same tree.

## Definition of Done *(keep)*

A task is complete when every line below is true. Check them before reporting; report the ones you could not satisfy by name.

**Before changing**
- Read the module's `README.md` (and its `AGENTS.md` if present). Its *Invariants* and *Allowed dependencies* sections are constraints, not suggestions.
- Bug fix: reproduce through the real entry point (<<CLI / HTTP / test harness>>) before editing.
- Before deleting or restoring code that looks odd: `grep -r <symbol> docs/decisions/` and `git log -S <symbol>`. Odd code usually has a decision behind it.

**While changing**
- One owner per responsibility. A new module, class, or abstraction needs a responsibility no existing code holds; otherwise extend the owner. Fix leaked or invalid state at its producer, not at every consumer.
- Comments state contracts and reasons — ownership, ordering, failure modes, platform constraints — never what the code visibly does. See [engineering standards](docs/engineering-standards.md#comments).
- No parameter, config key, or compatibility branch without a current consumer you can name.
- Prefer the smallest production diff. Cleanup of unrelated code is a separate commit.
- <<Any repo-specific invariant that agents have violated before, one line, with a link.>>

**After changing** — each line is checked by CI
- Behavior changed ⇒ the module README's *Public surface* / *Invariants* / *Known limitations* updated in the same commit. `verify-doc-pairs` fails the PR otherwise; bypass only with the `docs-not-needed` label and a reason in the PR.
- <<If translated pairs:>> `README.<<lang>>.md` and `docs/*.<<lang>>.md` updated with their English original, same commit. `verify-doc-pairs`.
- A choice another agent might re-litigate (A over B, deliberately not doing X, adding or removing an abstraction) ⇒ a record in [docs/decisions/](docs/decisions/README.md). `verify-decision-format` checks the form.
- Meaningful behavior ⇒ a test that fails before and passes after, at the tier [docs/testing.md](docs/testing.md) names. No tests for static values or that mirror the implementation. Coverage gate: <<N>>% on <<changed files / project>>.
- Format, lint, typecheck, and the relevant test subset ran; the PR's *Evidence* section lists what ran and what did not.
- Commits: `type(scope): summary` — see [CONTRIBUTING.md](CONTRIBUTING.md#commits). Hook and `commit-convention` job enforce it.
- A bug that reached <<users / a merged PR / a release>> and clears the [postmortem bar](docs/postmortem/README.md#when-to-write-one) ⇒ <<policy: `ask` — say why it clears the bar and ask before writing | `auto` — write it | `manual` — only when asked>>.

## Boundaries *(keep)*

- ✅ Always: run `<<format-fix>>` before committing; add tests beside the code they cover (`<<tests/ layout>>`); keep secrets out of commits and logs.
- ⚠️ Ask first: schema or migration changes; new dependencies; deleting a public export; changing CI, hooks, or this file's budget; anything under `<<protected path>>`.
- 🚫 Never: `--no-verify`; weakening an assertion, widening a mock, or adding a retry to make a test pass; editing generated files (`<<generated paths>>`) by hand; force-pushing shared branches.

## Read when relevant

- Architecture and dependency direction → [docs/architecture.md](docs/architecture.md)
- Code practice with examples → [docs/engineering-standards.md](docs/engineering-standards.md)
- Test tiers, mocks, flakes → [docs/testing.md](docs/testing.md)
- Decisions → [docs/decisions/](docs/decisions/README.md) · Postmortems → [docs/postmortem/](docs/postmortem/README.md)
- Contributing, branches, commits, PRs → [CONTRIBUTING.md](CONTRIBUTING.md)
- <<Module-specific rules → `<<path>>/AGENTS.md`>>

## Maintaining this file *(keep)*

- An agent made the same mistake twice ⇒ add one line here with a link to the explanation, not a paragraph.
- A rule became enforced by a check or linter ⇒ delete it here; the check is its home.
- `verify-agents-md-budget` red ⇒ relocate, then condense, then raise the ceiling with the reason in the PR.
- Rules for one directory go in that directory's `AGENTS.md`.
```

---

## Notes for the generator

- **Layout table**: only directories an agent will edit or must not edit. Not every folder.
- **Commands**: every one executed by you in Step 4. Keep the fix command next to the check command so the agent never has to guess.
- **DoD "While changing"** may carry up to three repo-specific one-liners drawn from the survey (e.g. "all DB access goes through `repo/`; `verify-dependency-direction`"). More than three means they belong in `docs/engineering-standards.md`.
- **Boundaries**: fill from the survey (generated dirs, migrations, protected paths). "Never commit secrets" stays in every project — it is the single most effective line in the GitHub corpus.
- **Do not add**: a tech-stack section (the manifest carries it), a repository overview paragraph, style rules a formatter enforces, anything the model already knows.
- If the repo has a `CLAUDE.md` with content, move the content here and leave `@AGENTS.md` in `CLAUDE.md`.
