# A decision record is the design document, with a frozen core and a proposed → accepted → implemented lifecycle

- Status: implemented
- Date: 2026-10-25
- Deciders: Ray
- Scope: agent-dev-standards
- Relations: supersedes frozen-thin-decision-records

The current convention ([#15](https://github.com/ObsisMc/skills/pull/15)). A record carries the full design and rollout while proposed and accepted, so a reviewer can judge it without reading code and an agent can implement it without asking; once implemented it states what the system promises. Only the decision drivers, invariants and considered options are frozen after acceptance; the rest is corrected during implementation and kept current afterwards. It was first run in between-pages (its PRs #6 and #7) and then ported into the skill. This record does not cover file naming, the header or supersession syntax, which carry over unchanged from the previous record.

## Context and problem

The frozen thin records of the previous convention failed at their first real use. The authentication record in between-pages stated the choice in a few lines, but not the design: no data model, flows, API contract, frontend behavior, configuration or rollout. An agent could not implement from it without asking, and the design had nowhere to go — the configuration was pushed into a spike README, and the rest stayed in conversation.

Two causes:

- **"Thin by design" conflated two things.** Facts that drift (paths, versions) were kept out of records, but so was the design itself, which does not drift before implementation and is exactly what a reviewer and an implementer need.
- **"Frozen whole" was too coarse.** Freezing protected the reasoning, but it also froze the plan, so a record could not be corrected as implementation taught something, and after implementation it could not say what was actually built.

Lessons carried into this record:

- Write a convention against its first real use before adopting it: the previous one was designed from a survey and failed at the first record that had to drive an implementation.
- Decide what a document is *for* before deciding what may change in it: a reader trusting the rationale and an implementer following the plan need different parts frozen.

## Decision drivers

1. A reviewer can judge the design without reading code; an implementer can build it without asking.
2. The reasoning a later reader relies on — why, what it beat, what it promises — stays as it was decided.
3. After implementation the record describes the system that exists, not the plan.
4. Progress is visible where work is tracked, without a parallel log.
5. An agent can implement an accepted design autonomously, within limits a human reviewed.
6. Follow established practice where it exists.

## Decision

### D1: The record is the design document

Required body: an opening summary, *Context and problem*, *Decision drivers*, *Decision* with `### D1…Dn` items (rule first, then why; data model, flows, interfaces and configuration inside the relevant D), optional *Failure and recovery*, numbered *Invariants*, *Considered options* as a table (Option / Strengths / Why rejected), *Risks and costs*, optional *Open questions* each with a default, *Rollout*, *Acceptance criteria*, *More information* with a mandatory *Revisit when*. Enough detail means driver 1.

### D2: proposed → accepted → implemented

`accepted` is a distinct stage: the design is approved and may be built. On `implemented`, *Rollout* and *Acceptance criteria* give way to *Verification*, the text moves to the present tense, and facts in *Decision* follow the code from then on. `rejected`, `deprecated` and `superseded` are frozen whole.

### D3: A frozen core, living facts

After acceptance only *Decision drivers*, *Invariants* and *Considered options* are frozen (`decision-amend` to change them). A difference in detail is written into *Decision* with its reason when the record becomes `implemented`; breaking an invariant or changing the decision needs a superseding record.

### D4: Progress lives in issues and PRs

The implementation log is removed. Implementation status is still computed from `[decision:<slug>#<n>]` tags, now on invariants.

### D5: The autonomous implementation agreement

*Rollout* may pre-approve the dependencies and migrations it lists, say what the agent may decide alone, when it must stop and ask, and how PRs are organized. It is on by default with two fixed limits: only what the record lists is pre-approved, and its stop conditions still stop the agent. The generated `AGENTS.md` carries the matching exception on its "ask first" line.

### D6: One configuration source

A *Required sections* paragraph in the template lists required and forbidden headings per status; together with the status table it is the configuration of `verify-decision-format` and `verify-decision-immutable`, word for word, so a translated README is translated together with its gates.

### D7: Only public sources are cited

Two patterns (D-numbered items, an options table that concedes strengths) also come from a private product spec repository. This repository is public, so that source is not named or quoted; `references/landscape.md` §6 attributes them to design-spec practice in a product repository.

## Invariants

1. A record that has left `proposed` keeps its decision drivers, invariants and considered options unchanged unless the change is explicitly labelled.
2. A `proposed` or `accepted` record has *Rollout* and *Acceptance criteria* and no *Verification*; an `implemented` record has *Verification* and neither of the other two.
3. Every record has at least one `### D` item, numbered invariants, and an options table with a *Strengths* column.
4. An agent following an autonomous implementation agreement adds no dependency or migration the record does not list.
5. The skill never names or quotes a private source.

## Considered options

| Option | Strengths | Why rejected |
| --- | --- | --- |
| **Keep frozen thin records** (the previous record) | The rationale can never be rewritten; short records | No home for the design; records could not be implemented from (drivers 1, 3) |
| **Fully living records** (deepseek-harness Agent Notes) | Always accurate; the lifecycle this record follows comes from it | Rationale and invariants could be rewritten along with facts (driver 2); no `accepted` stage between review and building (driver 5) |
| **Keep both conventions as interview options** | Users choose | Two sets of templates, gate specs and Definition of Done lines to keep consistent, and one of them is known to be insufficient (driver 6) |
| **Autonomous implementation off by default** | The ask-first boundary never widens | Every listed dependency or migration needs a second approval after the design was already reviewed (driver 5); the two fixed limits keep the widening to what was reviewed |
| **Name and quote the private spec repository** | Full attribution | The skills repository is public (D7) |

## Risks and costs

- Records get long; review takes longer, and a wrong design is more expensive to throw away.
- Keeping facts current after implementation is judgment, not a gate; records can drift.
- The autonomous agreement depends on the record listing dependencies and stop conditions precisely.
- The generated index still conflicts across parallel branches; regenerating resolves it. deepseek-harness forbids a central index for this reason.

## Verification

In between-pages, `verify-decision-format` (sections per status, D1, invariant numbering, the options table) and `verify-adr-immutable` (three frozen sections; whole body for terminal statuses and legacy) were proven red on planted records (between-pages #6). The authentication record was rewritten in the format with 13 invariants and an autonomous implementation agreement (between-pages #7). In this repository the convention is specified in `references/templates/decisions-README.md` and `references/gates.md`; there are no scripts to run.

## More information

- Revisit when: records become too long to review, facts in implemented records are found stale in practice, or an agent exceeds an autonomous implementation agreement.
- Evidence: between-pages PRs #6 and #7; this repository's [#15](https://github.com/ObsisMc/skills/pull/15); deepseek-harness `.agents/notes/README.md` and `.agents/notes/implemented/AGENTS.md`.
