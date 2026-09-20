# Template: module README.md

One per module directory in the module registry the checks directory reads. This is the module's **contract** — what other code and other agents may rely on — not a tour of its implementation. `verify-module-readmes` requires the headings marked *(required)* — the marker is for you, not for the output; keep the headings' exact English wording so the check can find them (translated pairs translate the body, not the heading anchor — see the pair template note below).

Pre-fill from code. Where you cannot tell, write `TODO(owner): <one-line question>` rather than plausible prose; an honest gap is cheaper than a wrong invariant.

---

```markdown
# <<module name>>

<<One or two sentences: the responsibility this module owns and for whom. If you need a third sentence, the module probably has two responsibilities — say so in Known limitations.>>

## Public surface *(required)*

What other modules may import or call. Everything not listed here is internal and may change without notice.

| Export | Contract |
| --- | --- |
| `<<function / class / endpoint>>` | <<inputs → outputs; what it guarantees; how it fails>> |

## Invariants *(required)*

Facts that must stay true; a change that breaks one needs a decision record and a version note.

- <<e.g. "Every write goes through `Repository.save`; nothing else touches the table.">>
- <<e.g. "`Config` is immutable after `load()`; mutation raises.">>

## Allowed dependencies *(required)*

- May import: <<`core/`, `util/`>>
- Must not import: <<`api/`, anything under `adapters/`>> — <<reason or link to docs/architecture.md#dependency-direction>>

## How to test *(required)*

```sh
<<exact command for this module's tests>>
```

- Tier: <<unit / integration / e2e>> — see [docs/testing.md](../../docs/testing.md#tiers).
- <<Anything nonstandard: fixtures, required env vars, what is mocked and why.>>

## Known limitations *(required)*

Durable gaps a consumer should know about. Ordinary cleanup goes in a TODO or a decision, not here. Write `None known.` when true rather than deleting the section.

- <<e.g. "Not safe under concurrent writers; see decision 2026-03-04-single-writer.">>

## Decisions

Records in `docs/decisions/` that shape this module. Read them before changing anything they describe.

- [<<yyyy-mm-dd-topic>>](../../docs/decisions/implemented/<<yyyy-mm-dd-topic>>.md) — <<one line>>
```

---

## Translated pair (`README.<<lang>>.md`)

Same file, same section order. Translate headings and body. `verify-module-readmes` checks only the English file for headings; `verify-doc-pairs` checks that the pair changed in the same range. Add a first line in each file linking the other:

```markdown
English | [中文](README.zh.md)
```
```markdown
[English](README.md) | 中文
```

## Notes for the generator

- Read the module's exports (its `__init__.py`, `index.ts`, `mod.rs`, `lib.rs`, `mod` declarations, or public package API) to fill *Public surface*. Do not list private helpers.
- *Invariants* are the hardest to derive. Look for: asserts, validation at entry points, comments that say "must", locks, single-writer patterns, `frozen`/`readonly`, ordering requirements in tests. Everything else is `TODO(owner)`.
- *Allowed dependencies* come from the import graph you observe plus `docs/architecture.md`. If the observed graph violates the intended direction, record the violation under Known limitations instead of legitimizing it.
- *How to test* must be a command you ran.
- Skip the *Decisions* section entirely when `docs/decisions/` is empty at generation time; the decisions README tells agents to add the link when they write the first record.
