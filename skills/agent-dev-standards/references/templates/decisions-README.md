# Template: docs/decisions/README.md

A lightweight decision-record convention, adapted from deepseek-harness Agent Notes (which extend the ADR practice for agents that forget between sessions). The README is the whole convention; `verify-decision-format` enforces the form. Also create the three lifecycle folders with a `.gitkeep` each.

---

```markdown
# Decisions

A decision record captures a choice that code, tests, and existing docs cannot explain on their own: **why** this and **what it beat**. Agents start every session without memory; without these records they re-propose rejected designs and "clean up" code that is odd on purpose.

Postmortems are the other kind of record and live in [../postmortem/](../postmortem/README.md): a decision looks forward (we chose A), a postmortem looks back (a bug escaped and here is why every net missed it).

## When to write one

Write a record in the same PR when the change involves any of:

- choosing A over a plausible B (library, pattern, data layout, protocol);
- deliberately *not* doing something an obvious reading of the code would expect;
- adding or removing an abstraction, owner, or module boundary;
- accepting a limitation or a tradeoff a future reader will want to reverse.

The test: *if another agent saw this code in three months, would they ask "why not B?"* If yes, write it. Mechanical and local edits — renames, formatting, a bug fix that has one correct form — do not need one.

Update the record that already owns a decision rather than writing a duplicate. Never edit a record into a different decision: write a new one, mark the old one superseded, and link both ways.

## Layout

```
docs/decisions/
  proposed/     reviewed before implementation; may speak in the future tense
  implemented/  shipped; present tense; kept current with the code
  rejected/     considered and declined; kept only while it prevents a tempting mistake
  yyyy-mm-dd-topic.md   ← file name: date first proposed + kebab topic
```

Moving a file between folders is the status change; update the `Status:` line in the same commit.

## Format

`verify-decision-format` checks the header, the status/folder match, the required headings, and that *Alternatives considered* is not empty.

```markdown
# Decision: <title as a declarative sentence>

Status: implemented          ← proposed | implemented | rejected — <one-line reason>

## Problem
The motivation, written so it stands without the solution.

## Decision                   ← "## Proposal" in proposed/
What is now true, in the present tense. Name files, types, and commands.

## Alternatives considered
- **<B>** — why it lost.
- **Do nothing** — why that was not acceptable.

## Consequences               ← "## Acceptance criteria" + "## Risks" in proposed/
What the tradeoff cost and what it bought. Include the reintroduction condition if something was given up.
```

`## Alternatives considered` is mandatory. A decision recorded without what it beat is the thing that invites re-litigation.

Implemented records describe reality: no "should", no migration plans, no acceptance checklists. When the code moves or renames what a record references, update the record's facts in the same change; the decision itself stays.

## Linking

- The module README's *Decisions* section links every record that shapes that module.
- Code that looks odd because of a decision carries a one-line comment with the record's file name.
- Cite by file name (`decisions/2026-03-04-single-writer.md`), never by number or prose title.

## Index

| Date | Status | Title |
| --- | --- | --- |
| <<none yet>> | | |
```

---

## Notes for the generator

- Do not write decision records during initialization unless the survey surfaced a decision the user confirms (e.g. "we deliberately don't use an ORM"). An empty, well-formed folder is the correct starting state.
- If the repo already has ADRs (`docs/adr/`, `docs/architecture/decisions/`, MADR files), keep their location and format; add only the *When to write one* and *Alternatives considered mandatory* rules and adapt `verify-decision-format` to their headings.
- The three folders exist so the folder is the status; do not collapse to one folder with a status field — agents grep folders faster than fields.
