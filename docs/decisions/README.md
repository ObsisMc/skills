# Decisions

Decision records for the skills in this repository: **why a skill works the way it does, what it beat**, and — while a change is proposed — the design for it. They follow the convention the `agent-dev-standards` skill generates ([its template](../../skills/agent-dev-standards/references/templates/decisions-README.md)), applied to this repository.

What a skill does *today* is the skill itself (`skills/<name>/SKILL.md` and its references); these records explain how it got there. A chain of superseding records is the iteration history: each superseded record stays frozen with the reasoning it had at the time, and the record that replaced it says why.

This repository has no CI and no `verify-decision-*` scripts, so the rules below are kept by hand, including the index.

## Index

| Record | Title | Status | Scope | Implemented |
| --- | --- | --- | --- | --- |
| [decision-records-in-lifecycle-folders](./2026-09-19-decision-records-in-lifecycle-folders.md) | Decision records live in lifecycle folders and are kept current with the code | superseded | agent-dev-standards | — |
| [frozen-thin-decision-records](./2026-10-25-frozen-thin-decision-records.md) | Decision records are flat, dated, frozen once accepted, and their progress is derived from test tags | superseded | agent-dev-standards | — |
| [decision-records-as-design-documents](./2026-10-25-decision-records-as-design-documents.md) | A decision record is the design document, with a frozen core and a proposed → accepted → implemented lifecycle | implemented | agent-dev-standards | — |

*Implemented* is "—" throughout: skills have no test suite to tag.

## Rules

- File names: `YYYY-MM-DD-<slug>.md`, the date the decision was first proposed (for a reconstructed record, the date of the change it reconstructs); the slug is unique and is how records are cited.
- Header: *Status*, *Date*, *Deciders*, *Scope*, *Relations*. *Scope* is the skill name, or `repository` for repository-wide rules.
- Status values, required sections per status, what is frozen after acceptance, and the relation syntax are exactly as in the [template](../../skills/agent-dev-standards/references/templates/decisions-README.md): `proposed | accepted | implemented | rejected | deprecated | superseded`; *Decision drivers*, *Invariants* and *Considered options* frozen once accepted; superseded records frozen whole.
- Each record that supersedes another explains, in *Context and problem*, why the previous one fell short. That is where the lessons of an iteration live.
- Alternatives are recorded, never invented: a reconstructed record lists only alternatives that the material from its time names.

## When to write one

When a change to a skill reverses or reshapes how it works (a convention it generates, its workflow, its scope), not for wording fixes. Write it in the same PR as the skill change.
