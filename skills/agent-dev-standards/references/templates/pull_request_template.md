# Template: pull request template

Write it at the path the repo's hosting platform reads for PR templates (check the platform's current docs).

Short. The *Evidence* section is the point: it makes "what did you actually run" a required field instead of an assumption, and it is where an agent's unrun checks become visible.

---

```markdown
## Problem

<!-- What is wrong or missing, in one or two sentences. Link the issue. -->

## Change

<!-- What this PR does and the one design choice worth knowing. Not a file list. -->

## Evidence

<!-- Every check you ran, with the result. Every check you did not run, with why. -->
- [ ] `<<format-check>>`
- [ ] `<<lint>>`
- [ ] `<<typecheck>>`
- [ ] `<<test-subset>>` — which subset:
- [ ] `<<task-runner>> check docs`
- Not run:

<!-- Behavior change: name the test that failed before and passes after. -->

## Docs

- [ ] Module README(s) updated: <!-- paths --> — or `docs-not-needed` because:
<<- [ ] `README.<<lang>>.md` pair(s) updated>>

## Decision

<!-- Link the docs/decisions/ record this PR adds or updates, or write "none needed". -->
```

---

## Notes for the generator

- Replace the command placeholders with the exact commands from `AGENTS.md`.
- If the repo already has a PR template, add the *Evidence* and *Docs* sections to it rather than replacing it.
- Do not add sections for screenshots, changelog, reviewers, etc. unless the repo's workflow already requires them.
