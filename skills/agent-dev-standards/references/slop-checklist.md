# Slop checklist

Run this against any agent-facing document — the root `AGENTS.md` first, then `docs/*.md`, then module READMEs. Report each hit as `file:line → item → where it should go`. Adapted from deepseek-harness `docs/AGENTS.md` and openclaw's `deslop` skill.

## In the root AGENTS.md

1. **Generic advice.** "Write clean code", "follow SOLID", "keep functions small", "high cohesion, low coupling" — the model knows this and the line changes nothing. Delete, or replace with the one project-specific consequence (e.g. "`core/` may not import `adapters/`; `verify-dependency-direction` enforces it").
2. **Repository overview prose.** Paragraphs describing what the project is and how the pieces fit. A one-line description and a directory table are enough; the agent reads code faster than prose. Move the rest to `docs/architecture.md`.
3. **Rules already enforced by a tool.** If a formatter, linter, type checker, or verify script fails on the violation, the rule's home is the tool. Delete the line; keep the command.
4. **Procedures.** Any multi-step "how to add an X" or "how to release". Move to `docs/cookbook/` or a skill; leave a pointer.
5. **Duplicated rules.** Search a distinctive phrase across the repo's docs. Keep one home, link the rest.
6. **History.** "We used to…", "since the migration…", "as of v2…". Git and PRs own history. Delete or move the durable rationale to `docs/decisions/`.
7. **Status annotations.** "implemented!", "TODO: future", "(WIP)". Status rots; the code and manifests carry it.
8. **Emphasis inflation.** Bold, CAPS, "CRITICAL", "ALWAYS/NEVER" on every line means nothing stands out. Reserve emphasis for the clause that changes behavior.
9. **Unexecutable commands.** A command without its flags, or one nobody has run recently. Run it; fix or delete.
10. **Missing pointer.** A rule with no link to its explanation invites re-litigation. Add the link or write the home.
11. **Over budget.** Past the line/word ceiling. Relocate → condense → raise the ceiling with a reason, in that order.

## In module READMEs and docs

12. **Restated code.** Prose that walks through what a function does line by line. Delete; the code is the source. Keep the contract: inputs, outputs, invariants, failure modes, ownership.
13. **Hand-maintained inventories.** Lists of tests, files, or exports that a generator or `ls` already provides. Delete or generate.
14. **Reasoning transcripts.** "We first considered… then realised…". Keep the resulting contract or move the rationale to `docs/decisions/`.
15. **Spec-speak in shipped docs.** "should", "will", "plan to" describing code that already exists. Rewrite in present tense.
16. **Metaphor where a noun exists.** "boundary", "surface", "shape", "layer" when the exact thing has a name: `HTTP handler`, `response fields`, `ESM exports`, `process boundary`. Name it.
17. **Unpaired translation.** A `README.md` whose `README.<lang>.md` has different sections or an older date. Fix or flag.

## In code comments (when reviewing a diff)

18. **Narration.** `// loop over items`, `// return result`, `// initialize`. Delete.
19. **Restatement of the signature.** A docstring that says `Gets the user by id` above `get_user(id)`. Delete or state what is not in the signature: failure modes, ownership, timing.
20. **Imagined-state defenses.** `try/except` or null checks that guard states the type system or the caller contract already excludes. Delete unless a real producer can emit that state — then name the producer.
21. **Type laundering.** `as any`, `as unknown as T`, `# type: ignore` without a reason. Fix the type or explain the exception in place.
22. **Compatibility without a contract.** Aliases, fallbacks, retries, shims with no named consumer and no removal plan. Delete or record the consumer.
23. **Single-use helpers.** A function called once whose name adds no domain meaning. Inline.

## How to report

```
AGENTS.md:14  → 1 (generic advice)      → delete; project consequence is already line 31
AGENTS.md:40-58 → 4 (procedure)         → docs/cookbook/adding-a-provider.md, leave one pointer
src/auth/README.md:22 → 12 (restated code) → delete; keep the invariant on line 25
```

Findings first, counts last. Do not fix anything in audit mode; in adopt mode, show the table and wait.
