# Decision records are flat, dated, frozen once accepted, and their progress is derived from test tags

- Status: superseded
- Date: 2026-10-25
- Deciders: Ray
- Scope: agent-dev-standards
- Relations: supersedes decision-records-in-lifecycle-folders; superseded by decision-records-as-design-documents

The second convention ([#14](https://github.com/ObsisMc/skills/pull/14)): a flat folder of `YYYY-MM-DD-<slug>` records with a controlled status field, a MADR 4.0 body, the whole body frozen once accepted, changes only through recorded supersession, and implementation progress computed from tags in tests. It was designed and run first in a real repository (between-pages, its PRs #4 and #3) and then ported into the skill.

## Context and problem

Applying the lifecycle-folder convention to between-pages surfaced four problems:

- **Bundled decisions.** One ADR held 25 decisions across runtime, frontend, collaboration, contracts and auth; changing one meant editing the whole record, and nothing said which parts still held.
- **Accepted records edited in place.** Status lines and whole sections were rewritten after acceptance, so the reasoning that was true when a choice was made disappeared. "Keep implemented records current" (the previous D3) gave no line between updating facts and rewriting the decision.
- **Free-text status.** Status lines like "technical validation done; see ADR-0006 (equivalent to path B …)" could not be checked, and a script could only confirm that *some* status existed.
- **Sequential numbers.** Two branches each adding the next number collide on merge.

A survey of how large projects manage decisions (Python PEPs, Rust RFCs, Kubernetes KEPs, MADR, log4brains; `references/landscape.md` §6) showed a common core: proposal-style records are not substantially changed after acceptance, status is a controlled field, supersession is an explicit relation, and the current state lives in a separate document.

## Decision drivers

1. The reasoning a later reader relies on must stay exactly as it was when the decision was made.
2. Agents work on parallel branches; record identifiers must not collide.
3. Status and supersession must be checkable by a script on both sides.
4. Whether a decision is implemented must be visible without anyone remembering to write it down.
5. A record must not carry facts that go stale (paths, versions, test locations).
6. Follow established practice where it exists.

## Decision

### D1: One flat folder, dated slugs

`YYYY-MM-DD-<slug>.md`; the slug is unique and is how records are cited. No lifecycle folders, no sequence numbers. Legacy numbered records keep their names and are frozen.

### D2: A five-field header with controlled values

*Status* (`proposed | accepted | rejected | deprecated | superseded`), *Date*, *Deciders*, *Scope*, *Relations* (`depends on`, `supersedes`, `superseded by`, each optionally for a named part).

### D3: MADR 4.0 body, thin by design

*Context and problem*, *Decision drivers*, *Considered options* judged against the drivers, *Decision outcome* (one-sentence conclusion plus points, no configuration values or code), optional numbered *Constraints* with *Confirmation*, *Consequences*, *More information* with a mandatory *Revisit when*, and an append-only *Implementation log* for how open items were settled.

### D4: Frozen once accepted

After acceptance only the status and relations lines, broken links, typos and appended log lines may change; anything else needs the `decision-amend` label. A changed decision — including an implementation that contradicts it — is a new record that supersedes it, wholly or in part, written on both sides.

### D5: Implementation status is computed

Tests carry `[decision:<slug>#<n>]` for the constraint they verify; a generated index counts covered constraints. Records never link to tests. Ordinary PRs that follow a record leave it untouched.

### D6: Current state lives in architecture.md

A *Current decisions* table in `docs/architecture.md` says what holds today, by scope, and may not link superseded or deprecated records.

## Invariants

1. An accepted record's body changes only in the status line, the relations line and the end of its implementation log.
2. Every supersession is written on both records.
3. Status takes one of five values, and is `superseded` exactly when the record is wholly superseded.
4. New record names are dated slugs; no two records share a slug.
5. Implementation progress comes only from tags in tests, never from hand-written notes.

## Considered options

| Option | Strengths | Why rejected |
| --- | --- | --- |
| **Keep lifecycle folders as status** (the previous record) | Status visible in the path; grep by folder | Cannot express partial supersession or two-way links; every status change moves the file and breaks links (drivers 3, 2) |
| **Living records kept current with the code** (deepseek-harness Agent Notes) | One document stays accurate | Overwrites the reasoning that was true at decision time (driver 1); KEPs make it work only with a per-release review process |
| **Sequential numbers, assigned at merge or by the PR number** | Short references | Numbering at merge needs a human; PR numbers collided with the existing `0001`–`0007` range (driver 2) |
| **Links from records to their tests** | One click from decision to proof | Test paths change, so links go stale (driver 5) |
| **A hand-written "implemented" line in the log** | Simple | Not written is indistinguishable from not done (driver 4) |
| **Subfolders per module** | Locality | Most decisions span modules; KEP-style grouping fits organizations with independent groups (driver 6) |
| **Split the bundled ADR into one record per decision** | Clean history | It was merged and its clause numbers were cited across the repository; future changes supersede single clauses instead |

## Risks and costs

- Records stay deliberately thin: design detail (data model, flows, contracts, rollout) has no home in them.
- Partial supersession by clause number is awkward for legacy bundled records.
- The generated index changes in every record PR and can conflict across branches; regenerating resolves it.

## Verification

In between-pages: `verify-decision-format`, `verify-adr-index`, `verify-adr-tags` and `verify-adr-immutable` were each proven red on a planted violation. The proofs caught two bugs before merge: dated file names matched the legacy numbered pattern, so new-format rules were skipped; and spike tests counted as implementation. In this repository the convention is specified in `references/gates.md`; there are no scripts to run.

## More information

- Revisit when: records turn out too thin to implement from, or immutability blocks legitimate corrections.
- Evidence: between-pages PRs #4 (process) and #3 (first record in the format); this repository's [#14](https://github.com/ObsisMc/skills/pull/14).
- Lessons: verify every claim taken from another project against its primary source (a status list was first written from memory and was incomplete); commit a fix to a gate before switching to a scratch branch to prove it, or the fix leaves with the branch.
