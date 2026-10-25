# Decision records live in lifecycle folders and are kept current with the code

- Status: superseded
- Date: 2026-09-19
- Deciders: Ray
- Scope: agent-dev-standards
- Relations: superseded by frozen-thin-decision-records

The first decision-record convention that `agent-dev-standards` generated (added in [#13](https://github.com/ObsisMc/skills/pull/13), merged 2026-10-13): a lightweight ADR adapted from deepseek-harness Agent Notes, with the status encoded as the folder a record sits in and implemented records rewritten to match the shipped code. Reconstructed on 2026-10-25 from the skill as it stood at `2e00eb0` (`references/templates/decisions-README.md`, `references/landscape.md` §2); nothing below goes beyond what those files say.

## Context and problem

Agents start every session without memory. Without a record of why a choice was made and what it beat, they re-propose rejected designs and "clean up" code that is odd on purpose. The skill needed a decision-record convention it could generate into any repository, small enough to be written routinely and checkable by a gate.

## Decision drivers

1. A decision recorded without what it beat invites re-litigation (deepseek-harness).
2. Agents should find records by browsing or searching, without a central index.
3. Records must not describe a system that no longer exists.
4. The form must be checkable by a script (`verify-decision-format`).

## Decision

### D1: Status is the folder

Records live in `docs/decisions/{proposed|implemented|rejected}/yyyy-mm-dd-topic.md`. Moving a file between folders is the status change, made together with the `Status:` line. The template's stated reason: "agents grep folders faster than fields".

### D2: Fixed skeleton with a mandatory Alternatives considered

`# Decision: <title>`, `Status:`, then `## Problem`, `## Decision` (`## Proposal` while proposed), `## Alternatives considered`, `## Consequences` (`## Acceptance criteria` + `## Risks` while proposed). *Alternatives considered* may not be empty.

### D3: Implemented records describe reality

"Implemented records describe reality: no 'should', no migration plans, no acceptance checklists. When the code moves or renames what a record references, update the record's facts in the same change; the decision itself stays." A record is never edited into a different decision: a new one supersedes it and both are cross-linked.

### D4: Cite by file name

Records are cited by file name, never by number or prose title; module READMEs list the records that shape them.

## Invariants

1. A record's folder and its `Status:` line agree.
2. Every record has a non-empty *Alternatives considered*.
3. An implemented record contains no proposal-era sections.

## Considered options

| Option | Strengths | Why rejected |
| --- | --- | --- |
| **One folder with a status field** | One place to look; no file moves | The template rejected it because "agents grep folders faster than fields" (driver 2) |
| **Keep an existing ADR directory and format as is** (adopt mode) | No churn for repositories that already have ADRs | Not rejected: the generator notes kept existing ADRs in place and added only the *When to write one* and mandatory-alternatives rules |

No other alternatives are recorded in the material from this time.

## Risks and costs

Not recorded at the time. The superseding record names the costs that later surfaced.

## Verification

`verify-decision-format` as specified in `references/gates.md` at `2e00eb0`: header fields, the status/folder match, required headings, non-empty *Alternatives considered*. Proven by emptying the alternatives of one record and moving a record to the wrong folder.

## More information

- Revisit when: not recorded at the time.
- Evidence: `skills/agent-dev-standards/references/templates/decisions-README.md` and `references/landscape.md` at commit `2e00eb0`; deepseek-harness `.agents/notes/README.md`.
