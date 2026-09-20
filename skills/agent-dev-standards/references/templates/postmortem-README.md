# Template: docs/postmortem/README.md

Self-contained: an agent with no postmortem skill installed can write a conforming postmortem from this file alone. The conventions match the `bug-postmortem` skill's landing rules, so when that skill is available it writes into this structure without adaptation. Create the folder with this README and no entries.

---

```markdown
# Postmortems

A postmortem records a bug that reached somewhere it should not have — <<real users / a merged PR / a release>> — and the interesting part is **why every safety net missed it**, not the one-line fix. It is the only document tier where narrative belongs.

A postmortem is not a [decision record](../decisions/README.md): decisions look forward, postmortems look back.

## When to write one

All four must hold:

1. **Escaped** — it reached <<users / main / a release>>. A bug you found and fixed before merging does not qualify.
2. **Subtle** — the mechanism is non-obvious; a careful engineer would re-derive it the hard way.
3. **Systemic** — it got through because of a gap in tests, tooling, or conventions, not a one-off slip.
4. **Costly to rediscover** — it cost real debugging time and would again.

Policy for agents: **<<ask | auto | manual>>**.
- `ask`: after fixing a bug that clears the bar, state which criteria it meets and ask before writing.
- `auto`: write it in the same PR.
- `manual`: write only when asked.

Most bugs do not clear the bar. Fix, test, move on.

## File

- Location: this directory. Name: `YYYY-MM-DD-kebab-short-title.md` (date avoids number collisions across branches and makes age visible).
- Title: a declarative conclusion — "A truthy config expression silently disabled the filesystem tools" — never "Notes on X".
- Cite elsewhere by slug: `postmortem: config-expression-disabled-fs-tools`.
- Register it in the index below.

## Required sections, in order

1. `## Executive summary` — one paragraph a busy reader absorbs in thirty seconds: what broke, root cause in plain terms, why it escaped, the durable lesson.
2. `## Summary` — full context. (`## Impact` — who was affected and how widely — goes directly after it when known.)
3. `## Timeline` — the investigation sequence and its evidence, citing PRs/issues. Which clue surfaced first and where the detour happened matter; a timestamp per line does not.
4. `## Root cause` — the mechanism in plain language, with a minimal code block showing the broken form and the fixed form together. Several causes: `Root cause #1 — <conclusion>`, each heading a conclusion in itself.
5. `## Why every test missed it` — the heart. For each net (unit, integration, e2e, lint, review, docs): what it checked, why that was not enough.
6. `## Guardrails added` — concrete defenses with file paths (see below).
7. `## Lessons` — durable principles, one per bullet, each phrased so another document can cite it.

## Guardrails

A defense counts only if something fires it automatically. Work down this order and stop as early as possible; give every guardrail its file path and back-link this postmortem's slug from that file.

| Order | Form | When |
| --- | --- | --- |
| 1 | **Test** in the file that already covers the code, travelling the real entry path | Whenever the invariant is one execution |
| 2 | **`<<checks/>>verify-<thing>`** script: one invariant, non-zero exit, output names the offending location and the fix command; wired into `<<task-runner>> check` and CI | When the invariant spans files or is structural |
| 3 | **Pre-commit hook** (`<<hook mechanism>>`), fast and staged-only | When the mistake is cheap to catch at commit time |
| 4 | **One line in `AGENTS.md`** (root or the subtree's), linking here | When nothing above can express it |

Never write "be more careful" or "review more thoroughly" — they cannot fail and are never forcibly read. If a rule now lives in `AGENTS.md` or `testing.md`, that is its home: cite it, do not copy it.

## Index

| Date | Title |
| --- | --- |
| <<none yet>> | |
```

---

## Notes for the generator

- Fill `<<escaped to>>` from the project's shape: a library → "a release"; a service → "production"; an internal tool → "main".
- The checks directory and hook mechanism names come from the interview and must match `AGENTS.md`.
- If the repo already has postmortems elsewhere, keep their location; add this README's *When to write one* and *Guardrails* sections there and adapt the index.
