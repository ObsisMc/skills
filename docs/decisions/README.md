# Decisions

Decision records for the skills in this repository: **why a skill works the way it does, what it beat**, and — while a change is proposed — the design for it. They follow the convention the `agent-dev-standards` skill generates ([its template](../../skills/agent-dev-standards/references/templates/decisions-README.md)), applied to this repository with one deliberate change: records are grouped by skill (see *Layout*).

What a skill does *today* is the skill itself (`skills/<name>/SKILL.md` and its references); these records explain how it got there. A chain of superseding records is the iteration history: each superseded record stays frozen with the reasoning it had at the time, and the record that replaced it says why.

This repository has no CI and no `verify-decision-*` scripts, so the rules below are kept by hand, including the index.

## Index

*Implemented* is "—" throughout: skills have no test suite to tag.

### agent-dev-standards

| Record | Title | Status | Implemented |
| --- | --- | --- | --- |
| [decision-records-in-lifecycle-folders](./agent-dev-standards/2026-09-19-decision-records-in-lifecycle-folders.md) | Decision records live in lifecycle folders and are kept current with the code | superseded | — |
| [frozen-thin-decision-records](./agent-dev-standards/2026-10-25-frozen-thin-decision-records.md) | Decision records are flat, dated, frozen once accepted, and their progress is derived from test tags | superseded | — |
| [decision-records-as-design-documents](./agent-dev-standards/2026-10-25-decision-records-as-design-documents.md) | A decision record is the design document, with a frozen core and a proposed → accepted → implemented lifecycle | implemented | — |

### repository

No records yet.

## Layout

```
docs/decisions/
  README.md                 rules and the index
  <skill>/                  one folder per skill that has records; created with its first record
    YYYY-MM-DD-<slug>.md
  YYYY-MM-DD-<slug>.md      repository-wide decisions (e.g. how the README skill tables are kept)
```

The template defaults to one flat folder, because in an application most decisions span several modules. Here almost every decision belongs to exactly one skill, and each skill evolves on its own; grouping by skill keeps each skill's supersession chain in one place, the way Kubernetes groups KEPs by SIG. Records stay under `docs/`, not under `skills/<name>/`, because a skill's folder is copied whole when the skill is installed.

## Rules

- File names: `YYYY-MM-DD-<slug>.md`, the date the decision was first proposed (for a reconstructed record, the date of the change it reconstructs). The slug is unique across the whole repository, not just within a skill's folder, so a record is cited by its slug alone.
- Header: *Status*, *Date*, *Deciders*, *Scope*, *Relations*. *Scope* is the name of the folder the record sits in, or `repository` for a record at the root; the two must always agree.
- Status values, required sections per status, what is frozen after acceptance, and the relation syntax are exactly as in the [template](../../skills/agent-dev-standards/references/templates/decisions-README.md): `proposed | accepted | implemented | rejected | deprecated | superseded`; *Decision drivers*, *Invariants* and *Considered options* frozen once accepted; superseded records frozen whole.
- Each record that supersedes another explains, in *Context and problem*, why the previous one fell short. That is where the lessons of an iteration live.
- Alternatives are recorded, never invented: a reconstructed record lists only alternatives that the material from its time names.
- The index groups records by folder; add a section the first time a skill gets a record.

## When to write one

When a change to a skill reverses or reshapes how it works (a convention it generates, its workflow, its scope), not for wording fixes. Write it in the same PR as the skill change, in that skill's folder.
