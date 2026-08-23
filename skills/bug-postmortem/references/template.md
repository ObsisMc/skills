# Postmortem <YYYY-MM-DD>-<slug>: <a declarative sentence stating what broke>

Write the document in the user's language and translate these headings accordingly; keep the order. Keep error strings, paths, and identifiers verbatim.

## Executive summary

<One continuous paragraph, readable in thirty seconds: what broke → root cause in plain language → why it escaped → the durable lesson. No bullets, roughly 80 words.>

## Summary

<Full context: which scenario, which version, which configuration triggered it. Quote the error string verbatim: `...`>

## Impact

<Who was affected, how widely, for how long. State consequences; logs are not required here.>

## Timeline

- <First clue: who saw what, in what situation>
- <The detour: why the initial reading was wrong — this is the evidence that something failed to report the truth in time, and it must survive into the final text>
- <The turn: which clue finally pointed at the root cause>
- <Related PR / RFC / issue numbers>

## Root cause #1 — <a conclusion, not a topic>

<The mechanism in plain language. Never attribute it to a person.>

```
// broken — and why it looked correct
...

// fixed — where the decisive difference is
...
```

## Root cause #2 — <a conclusion, not a topic>

<Delete this section if there is only one root cause.>

## Why every test missed it

<The heart of the document. Attribute the escape to a gap in tests, tooling, or conventions.
State the gap as one checkable sentence:
"For the case of ____, our ____ was never executed / never constructed / never asserted.">

- Gap in the tests: <...>
- Gap in the tooling or gates: <...>
- Gap in the conventions: <...>

## Guardrails added

Choose landing spots in the order test → verify script → pre-commit → one line in `AGENTS.md`, and stop as early as possible.
For each entry, state the trigger: at which step will the same class of bug fail loudly next time?

- **Test**: <a case that travels the real entry path> — `<path/to/test>`
- **Verify script**: <one invariant per script, command name = file name, non-zero exit on violation> — `guardrails/verify-<x>` plus the project's existing task runner
- **pre-commit**: <only if fast, local, and scoped to staged files> — `.githooks/pre-commit` or `lefthook.yml`
- **One line in `AGENTS.md`**: <the fallback when nothing can be automated; one to three lines plus a link to the source of truth> — `<path/to/AGENTS.md>`
- **Architecture**: <turn an inexpressible constraint into an expressible type, or refuse to start at configuration time> — `<path>`
- **Known hole**: <what these guardrails do not cover, and where the fallback is>

## Lessons

- <A durable principle another document can cite>
- <A durable principle another document can cite>
