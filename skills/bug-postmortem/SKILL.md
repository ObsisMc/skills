---
name: bug-postmortem
disable-model-invocation: true
description: Write an engineering postmortem for a bug that escaped into production — real users, a merged PR, or a released version. Judge first whether the bug clears the subtle/systemic/costly-to-rediscover bar, gather evidence, then produce a fixed-section incident record whose center of gravity is why every safety net missed it, not the one-line fix, and whose guardrails are concrete enough that the same bug class fails loudly next time. Use when the user says postmortem, RCA, root cause analysis, incident report, retrospective, 复盘, 事故复盘, 根因分析, 故障报告, "why didn't our tests catch this", "这个 bug 为什么没被测出来", "write this up", "写个复盘", or has just finished debugging something painful and wants the lesson made durable. Also use when reviewing or improving an existing postmortem draft. This is a code-level postmortem about a specific defect and the tests, tooling, and conventions that failed to catch it; it does not cover team or project retrospectives, sprint reviews, or non-engineering incident reviews.
---

# Postmortem

A postmortem is not a fix record. The value of a bug is not in the line that fixed it — it is in **why the process let it through**, and **what new guardrail makes the same class fail loudly next time**.

Most of the effort belongs in the "why every safety net missed it" section. If that section is vague, the postmortem has failed.

## Output language

Write every user-facing artifact — the postmortem document, its section headings, commit messages, and your replies — in **the language the user is writing in**. This file is in English for maintenance; that is not the output language. Keep identifiers, file paths, commands, and verbatim error strings in their original form regardless of language.

## Workflow

1. **Clear the bar** — if it does not qualify, do not write one (see below).
2. **Gather evidence** — a postmortem records evidence, not a teaching sequence. Collect the material before drafting.
3. **Locate the escape gap** — the step that takes the longest. Interrogate the gap checklist below, item by item.
4. **Write the thirty-second executive summary** — write it first. If you cannot, you do not yet understand the incident.
5. **Fill in the required sections.**
6. **Land the guardrails** — first present the list of guardrails and where each one lands, get confirmation, then touch files. Changing git hook configuration or adding a new task-runner command needs its own separate confirmation.
7. **Archive and back-link.**

A typical run produces **one postmortem document plus one test change**. If three or four new scripts appear, the guardrails landed too high, or this bug should not have had a postmortem at all.

## Step 1: Clear the bar

Precondition: the bug already escaped somewhere it should not have reached — real users, a merged PR, a released version. A bug written and caught on a development branch does not get a postmortem.

On top of that, **all three** must hold:

| Bar | Meaning | Test question |
| --- | --- | --- |
| Subtle | The mechanism is non-obvious; a careful engineer would re-derive it the hard way | Would a different person walk into the same detour? |
| Systemic | It escaped through a gap in tests, tooling, or conventions — not a one-off typo | After this one-line fix, can the same class still enter through the same hole? |
| Costly to rediscover | It burned real debugging time, and would burn it again | How long did this take? Would it take that long again? |

Miss any one of the three and do not write a postmortem — a test case or a one-line rule in `AGENTS.md` is the right size. **Writing them freely dilutes the signal of the whole directory.**

## Step 2: Gather evidence

Before drafting, collect:

- The raw error string, copied verbatim, never paraphrased — it is the anchor for future searches.
- The trigger path: which entry point, which version, which configuration.
- Related PR / RFC / issue numbers.
- The minimal reproduction of the broken form, and the fixed form.
- **The detours taken during investigation** — a detour is direct evidence that something failed to report the truth in time. Keep it; do not smooth it away in hindsight.
- The actual state of the tests at the time (how many green, what coverage) — this is what proves "green does not mean correct".

## Step 3: Locate the escape gap (the core)

Attribute the escape to a **process gap**, never to a person. "The author did not notice" is a forbidden attribution.

Work through this checklist of common gaps:

- **Tests bypassed the real entry path** — tests hand-construct objects and mock away the real loading or startup flow, so the path the product actually takes was never executed. A fully green unit suite at 100% line coverage does not rule this out.
- **Line coverage treated as proof of behavior** — coverage proves a line ran, not that the feature works as shipped. It is a necessary condition, never a sufficient one.
- **Deterministic replay mistaken for correct behavior** — refreshing a snapshot proves the current behavior reproduces stably, not that it is right. A wrong result replays just as stably.
- **Assertions read the subject's self-report instead of the outside world** — probing output for keywords lets an implementation that claims success without doing the work pass. Re-run the command, or re-read the file or data externally.
- **Test doubles prove plumbing, not integration** — mocks, stubs, and credential-less fallback branches prove the pipeline connects. Only a run against the real dependency proves the feature works.
- **The type or result model cannot express the real constraint** — the decision logic can only say "matches this substring", not "must be this exit code, carrying this diagnostic", so the misclassification could never be caught at the type level.
- **A combination was never constructed** — for example a harmless warning line followed by a non-zero exit code; the test matrix has no cell for it.
- **The runtime never told the caller what it was talking to** — not knowing which address, which process, or which config is live, and so validating the wrong target.
- **The tests exercise the source plane, not the shipped artifact** — module resolution, bundling, and duplicated-singleton problems surface only in the built output.

When nothing on the list matches, state the gap as one checkable sentence: "**For the case of ____, our ____ was never executed / never constructed / never asserted.**"

## Step 4: The thirty-second executive summary

One continuous paragraph, no bullets, absorbable by a busy reader in thirty seconds. The formula:

> **what broke** → **the root cause in plain language** → **why it escaped** → **the durable lesson**

## Required sections

Required, in this order:

1. `## Executive summary` — the paragraph above.
2. `## Summary` — full context.
3. `## Timeline` — the investigation sequence and its evidence, citing PR/RFC numbers. What matters is which clue surfaced first and where the detour happened, not a timestamp for every line.
4. `## Root cause` — the mechanism in plain language; **inline a minimal code block showing the broken form and the fixed form together**. Number multiple causes as `Root cause #1 — ...`, and make each heading a conclusion in itself.
5. `## Guardrails added` — concrete defenses with file paths.

Recommended additions:

6. `## Impact` — who was affected and how widely; place it directly after Summary.
7. `## Why every test missed it` — must stand as its own section. This is the heart of the document; it deserves its own heading.
8. `## Lessons` — durable principles, one per bullet, each phrased so another document can cite it.

Translate these headings into the user's language when that is the document's language; keep the order.

## Guardrail requirements

Every guardrail must answer: **at which step will the same class of bug fail loudly next time?** If it cannot, it is not a guardrail.

### Three tiers of trigger

A defense is only as strong as whatever fires it automatically. This has nothing to do with owning CI.

| Trigger | Strength | Form |
| --- | --- | --- |
| A check that fails | Strong; cannot be ignored | Test case, `verify-*` script, pre-commit hook |
| A rule file forcibly read into context | Medium; relies on an unavoidable path | One line in `AGENTS.md` — read at the start of every session |
| Human memory, "be more careful next time" | Useless | — |

The postmortem exists because the bug was **systemic**: it escaped through a process gap. **Patching a systemic gap with human memory means relying on the exact net that just failed.**

If the project has nothing even at the second tier, still write the postmortem — its first guardrail is then "build the first net". That is the highest-value kind of postmortem, not a reason to skip it.

### Choosing where a guardrail lands

Work down this order and stop as early as possible: **test → verify script → pre-commit → one line in `AGENTS.md`**.

**1. Test** (first choice)
Add it to the test file that already covers the changed code. It must travel the real entry path or the real shipped artifact, not a hand-assembled in-memory object.

**2. `verify-*` script** (when the invariant cannot be expressed as a single execution)

Language-independent. Write it in a language the project already uses; never introduce a new runtime for a gate. Four hard requirements: **non-zero exit** on violation; one invariant per script; a stable name the postmortem can cite; failure output naming the offending location **and the fix command**.

- Put it in a **dedicated directory**, by default `guardrails/verify-<the-thing-checked>`, and hang a command of the same name off the task runner, so **file name = command name = gate name**.
- Do not bury it in the project's existing `scripts/`: that directory usually already mixes build, deploy, and one-off scripts. A dedicated directory makes `ls guardrails/` the inventory of every defense the project has accumulated. Follow an existing convention if the project has one; otherwise pick a name that does not yet exist (`guardrails/`, `checks/`, `invariants/`). In LLM-adjacent projects avoid the word `guardrails` and use `checks/`. Record the choice in `AGENTS.md` and never change it.
- Choose the task runner in this order: **whatever the project already has** (npm script, `cargo xtask`, `./gradlew`, nox/tox, `dotnet run`) → otherwise `just` (a justfile: cross-platform, none of Make's tab traps) → or skip the runner entirely and call the script directly (`./guardrails/verify-x.sh`, where the registry is simply `ls guardrails/`). Never introduce a second task runner for a gate, and never assume `make` exists — it is absent by default on Windows.
- If a generator already exists, let the checker reuse it behind `--check`, so the fix command is the same command without `--check` and the two cannot drift. This is the common pattern: `cargo fmt --check`, `black --check`, `gofmt -l`, `terraform fmt -check`.
- Once there are several gates, group them behind one entry point with group names; run groups locally and in CI, never one gate at a time.
- The verify scripts themselves need tests.
- The weakest form that still counts: one `grep` in CI that turns the build red. If it runs by itself, it is first-tier.

**3. pre-commit** (use sparingly)
Zero-dependency approach: `git config core.hooksPath .githooks`, and commit `.githooks/pre-commit` as a plain shell script so the hook travels with the repository (on Windows, the bash that ships with Git runs it). For more capability use lefthook (a single Go binary plus YAML, where `run:` takes any command and nothing is tied to the project's language) or the pre-commit framework (`language: system` runs arbitrary commands).
Whichever you choose, attach installation to a setup step the project already has; never rely on a developer remembering to install hooks.
Only put **fast, local checks scoped to staged files** here; everything slow or repository-wide (coverage, snapshots, e2e, documentation gates) belongs to CI.
Prefer **regenerate rather than reject** where a fix can be automated: regenerate and `git add`, instead of failing the commit.
Where the hook cannot cover a case, write the **known hole and its fallback** into the comment.

**4. One line in `AGENTS.md`** (the fallback when nothing can be automated)
- One to three lines plus a link to the source of truth. The rule lives here; the reasoning and the case live behind the link.
- A rule scoped to one subdirectory goes in that subtree's `AGENTS.md` and does not consume the root file's budget.
- Give the root file a word ceiling and enforce it as a gate. When it goes red, the order is **relocate → condense → and only then raise the ceiling**.
- Anything expressible as a test or a verify script must never consume space here. That, not discipline, is what keeps `AGENTS.md` from bloating.

**Never** write entries like "be more careful" or "strengthen review" — they cannot fail and are never forcibly read.
Give every guardrail its landing file path, and back-link the postmortem's slug from that file so "why does this rule exist" can be traced back.

## Voice and style

- **Past-tense narrative.** Other documentation tiers describe current state; the postmortem is the one tier where the war story and the timeline belong.
- **Name actors and facts.** No metaphors, no grand adjectives.
- **Never blame a person.** Describe the mechanism, not who overlooked it.
- **Never write what did not happen.** Record what was found, not what is suspected; label a suspicion as one.
- Error strings, config keys, and function names go in inline code, copied verbatim.

## Archiving

- Directory: **follow the project's existing location**; otherwise `docs/postmortem/`, or `postmortem/` at the repository root if the project has no `docs/`. Create the `README.md` index along with the first entry.
- File name: `YYYY-MM-DD-kebab-short-title.md`, e.g. `2026-08-23-config-overlay-silently-disabled-fs-tools.md`. A date prefix avoids collisions across parallel branches (an incrementing number has to be allocated while drafting, so two people each writing one both take the same number), and it makes the age visible — whether an old postmortem's guardrails still hold is itself worth doubting.
- Cite by slug, not by number: write "postmortem: config-overlay-silently-disabled" elsewhere.
- The document title is a declarative conclusion ("An expression in the config was read as truthy and silently disabled a whole tool group"), never "Notes on X".
- Register it in the `README.md` index.
- One home per fact: if a rule from the postmortem now lives in `AGENTS.md` or the testing docs, that is its home — cite it, do not copy it.

## Reference

- Postmortem document template: `references/template.md`
