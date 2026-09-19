---
name: agent-dev-standards
disable-model-invocation: true
description: Initialize or audit a software project's AI-collaboration standards — a lean root AGENTS.md (with optional CLAUDE.md alias), per-module README contracts, docs/ standards for engineering practice, testing, decisions (ADR) and postmortems, CONTRIBUTING + PR template, a GitHub Actions CI with format / lint / typecheck / test-coverage / commit-convention / docs-gates jobs, a `checks/` directory of verify scripts, and pre-commit hooks — all derived from the real repository and verified by running the commands. Every rule that says "always do X after a change" is paired with a check that fails when X was skipped. Use when the user says 初始化 AGENTS.md / CLAUDE.md, 给项目加 AI 开发规范, 约定开发流程, set up agent instructions, "make the AI follow our conventions", "add a Definition of Done", scaffold CI and commit conventions for an AI-driven repo, or asks to audit / tidy an existing AGENTS.md that has grown stale or bloated. Tool-agnostic: the output works for Claude Code, Codex, opencode and any agent that reads AGENTS.md.
---

# Agent Dev Standards

Give a repository a set of standards that an AI agent follows on **every** change, and make each standard fail loudly when skipped. The output is not a knowledge base about software engineering; it is a working agreement plus the gates that enforce it.

Three ideas drive every decision below. Read `references/landscape.md` if you want the evidence behind them (deepseek-harness, openclaw, codex, opencode, goose, the GitHub 2,500-repo analysis, the ETH Zurich study).

1. **The root file is always in context, so it must be lean and project-specific.** Generic advice the model already knows ("write clean code", "high cohesion") measurably *hurts* agent performance and raises cost. Every line in the root `AGENTS.md` has to pass the test: *would removing it make an agent do something wrong in this repo?*
2. **One home per fact.** Each rule lives in exactly one place; everything else links there. The root file carries standing orders (1–3 lines each, with a link); long explanations live in `docs/`; module-specific facts live in the module's README.
3. **A rule is only as strong as what fires it.** "Always update the docs" written in prose is followed most of the time. The rest is why every process rule you generate is paired with a check in `checks/` that runs locally and in CI.

## Output language

Write the root `AGENTS.md`, `CONTRIBUTING.md`, PR template, and every check script in **English** — agents read them and one canonical version avoids two homes for one rule. Write `docs/*.md` and module READMEs in English too, and add a translated pair (`README.<lang>.md`, `docs/<name>.<lang>.md`) when the user asks for one (see the interview). Talk to the user in the language they are using.

## Workflow

Follow these steps in order. Do not generate anything before the survey is complete — generated files must be derived from the repository, not from the templates alone. The templates in `references/templates/` are skeletons that show shape and tone; the content comes from what you find.

### Step 1: Survey the repository

Establish facts before asking anything. Detect:

- Language(s), package manager, task runner (npm scripts, `just`, `cargo xtask`, nox, `make`…). Pick the matching file in `references/stacks/` for commands and CI snippets; if none matches, derive commands from the repo and say so.
- Existing formatter / linter / type checker / test runner and their config files. **Never introduce a competing tool** — if the repo uses Black, do not add Ruff format; if it uses ESLint, do not add oxlint.
- Existing CI workflows, pre-commit configuration, git hooks.
- Top-level module directories (the things that deserve a README contract). In a monorepo, packages; in a flat repo, the directories directly under `src/` or the language's equivalent.
- Existing `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `docs/`, `CONTRIBUTING.md`, ADRs, postmortems. Their presence decides the mode:
  - **init** — no agent instructions exist. Generate the full set.
  - **adopt** — some exist. Keep everything that still holds, fill the gaps, and relocate content that sits in the wrong tier (a 400-line AGENTS.md usually contains three docs that want to be files). Never overwrite a file the user wrote without showing the diff first.
  - **audit** — the user only wants a review. Run `references/slop-checklist.md` against the existing files and report; change nothing unless asked.
- Run `git log --oneline -30` to learn the current commit message style; if it is already conventional, keep its type set rather than imposing a new one.

### Step 2: Interview

Ask only what the survey cannot answer. One message, grouped. Suggest a default for each so a "go with defaults" reply is enough.

| Question | Default | Why it matters |
| --- | --- | --- |
| Translated doc pairs? Which language? | Infer from the language the user is writing in (Chinese → `zh`); offer it, let them decline or change | Pairs add a `verify-doc-pairs` gate and a DoD line; nobody wants that imposed silently |
| Coverage threshold for the `test` job | 80% line coverage if the repo has no history; keep the existing number otherwise | Too high blocks adoption, too low is theater |
| Target agents (Claude Code / Codex / opencode / others) | All — the output is tool-agnostic anyway | Decides whether to add a one-line `CLAUDE.md` alias and where to mention agent-specific loading behavior |
| Name of the checks directory | `checks/` (avoid `guardrails/` in LLM-adjacent projects — the word collides with model safety features) | The name is recorded in `AGENTS.md` and must never change afterwards, so it is worth one question |
| Pre-commit mechanism | Whatever the repo has; else `.githooks/` + `git config core.hooksPath` (zero dependencies); lefthook or the `pre-commit` framework if the user prefers | Hooks must travel with the repository and install from an existing setup step |
| Postmortem policy | `ask` — after fixing a bug that clears the bar, the agent explains why and asks before writing | `auto` writes without asking; `manual` removes the self-check from the DoD entirely |
| Strictness of the docs gate | `strict` — module code changed ⇒ module README touched in the same PR, bypass only with a `docs-not-needed` PR label | The user asked for "docs updated on every change"; make the bypass explicit rather than the rule soft |

Do not ask about things like "which sections do you want" — the layering is the point of the skill.

### Step 3: Generate

Produce the files below. Each has a template in `references/templates/`; read the template, then write the real file from the survey. Where the template has `<<PLACEHOLDER>>`, the value comes from the repo or the interview — never leave a placeholder in output. Where you genuinely cannot determine something (a module's invariants, say), write `TODO(owner): …` with a one-line question, so the gap is visible instead of papered over with plausible prose.

| File | Template | Notes |
| --- | --- | --- |
| `AGENTS.md` (root) | `templates/AGENTS.md` | ≤ 120 lines / ≤ 1,200 words. Standing orders only; every rule links its home. The **Definition of Done** section is the heart — it is what the agent reads before saying "done" |
| `CLAUDE.md` | — | Only if the user still runs Claude Code < v2.1.277 or already has one. Content is exactly one line: `@AGENTS.md`. Use the import, not a symlink — symlinks break on Windows clones |
| `<module>/README.md` (one per module) | `templates/module-README.md` | The module's contract. Pre-fill from code: purpose, public surface, invariants, allowed dependencies, how to test, known limitations, related decisions. Mark unknowns `TODO(owner)` |
| `<module>/AGENTS.md` | — | Only when a module has operating rules that differ from the root (a generated directory, a vendored tree, a package with its own test runner). Do not create empty ones |
| `docs/README.md` | — | A ten-line index: one line per doc under `docs/` with what it is for. The root's Layout table links here |
| `docs/architecture.md` | `templates/architecture.md` | Module map, one-line responsibility per module, dependency direction rules ("who may import whom"). If the repo already has one, link it instead |
| `docs/engineering-standards.md` | `templates/engineering-standards.md` | The general practice the user wants agents to follow — cohesion/coupling, code smells, comments, error handling, naming, size limits. Each rule is one decidable sentence plus a Good/Bad example **in the project's language**. Rewrite the template's examples; do not ship pseudocode |
| `docs/testing.md` | `templates/testing.md` | Test tiers, what must have a test and what must not, mock policy, flaky-test policy, coverage gate, how to run subsets |
| `docs/decisions/README.md` | `templates/decisions-README.md` | Lightweight ADR convention: lifecycle folders, skeleton, mandatory *Alternatives considered*, when to write one, the format check |
| `docs/postmortem/README.md` | `templates/postmortem-README.md` | Self-contained: the bar, required sections, naming, index table, guardrail landing order. Works without any postmortem skill installed; if one is installed it is used for the writing |
| `CONTRIBUTING.md` | `templates/CONTRIBUTING.md` | Setup, branch naming, commit convention with examples, PR expectations, how to run the checks locally |
| `.github/pull_request_template.md` | `templates/pull_request_template.md` | Problem / Change / **Evidence** (what ran, what did not) / Docs / Decision |
| `.github/workflows/ci.yml` | `templates/ci.yml` + `stacks/<lang>.md` | Jobs: `format`, `lint`, `typecheck`, `test` (with coverage threshold), `commit-convention`, `docs-gates`. Fill commands from the stack file; drop `typecheck` for languages where the compiler owns it |
| `checks/` | `references/checks/*` | Copy the verify scripts, adapt paths, add a `check` entry point on the repo's task runner. See "The checks directory" below |
| Pre-commit hook | `stacks/<lang>.md` | format + lint on staged files, commit-msg convention check. Fast, staged-only; everything repo-wide stays in CI |
| Translated pairs | — | If requested: `README.<lang>.md` beside every module README and `docs/<name>.<lang>.md` beside every doc except `AGENTS.md`. Same section structure, translated by you now, kept in sync by the `verify-doc-pairs` gate later |

Order of writing: `AGENTS.md` last. Everything else exists first so its links resolve.

### Step 4: Verify

Nothing goes into `AGENTS.md`'s command block that you have not executed. Run:

1. Every command listed in `AGENTS.md` (install, format check, lint, typecheck, test subset). A command that fails on the current tree either gets fixed, gets removed, or gets a note in the report — never silently shipped.
2. The `check` entry point end to end, so the docs gates pass on the tree you just produced (module READMEs exist, links resolve, budget holds, decisions folder parses).
3. `verify-commit-convention` against the last 20 commits in dry-run mode; report how many would fail so the user knows what the gate will do to their history.
4. The pre-commit hook once, on a scratch commit in a temporary branch, then delete the branch.

Anything you could not run (no network, missing toolchain, sandbox) goes into the final report as *unverified*, by name.

### Step 5: Report

Lead with what exists now and what enforces it, as a table: rule → where it is written → what check fires. Then the list of `TODO(owner)` items, then unverified commands. Keep it short; the files are the deliverable.

## The Definition of Done

This is the section that turns the root file from documentation into a process. Write it as a checklist an agent runs before declaring a task complete; keep each line decidable. Adapt the template's wording to the repo, but keep these four groups:

**Before changing**: read the affected module's README (and `AGENTS.md` if present); reproduce a bug through the real entry point; before restoring or deleting code that looks odd, check `docs/decisions/` and `git log -S`.

**While changing**: one owner per responsibility — a new abstraction needs a responsibility nothing else holds; comments state contracts and "why" (ownership, ordering, failure modes, platform constraints), never restate code; no parameters, config, or compatibility branches without a current consumer; prefer the smallest production diff.

**After changing** (each line has a gate):
- Behavior changed ⇒ the module README's interface / invariants / limitations sections updated in the same commit — *gate: `verify-doc-pairs`, strict mode*.
- Translated pair updated with the original — *gate: `verify-doc-pairs`*.
- A choice another agent might re-litigate ⇒ a record in `docs/decisions/` — *gate: `verify-decision-format`* (checks form; judgment stays with the agent).
- Meaningful behavior ⇒ a test that failed before and passes after; no tests for static values or that merely mirror the implementation — *gate: `test` job coverage threshold*.
- Ran format, lint, typecheck, the relevant test subset; the PR's Evidence section lists what ran and what did not — *gate: the CI jobs; the PR template makes omission visible*.
- Commits follow `type(scope): summary` — *gate: commit-msg hook + `commit-convention` job*.
- A bug that escaped to users / a merged PR / a release and clears the postmortem bar ⇒ follow the postmortem policy — *gate: none possible; the policy line says whether to ask, write, or wait to be asked*.

## The checks directory

Verify scripts are the enforcement layer. Conventions (they match the `bug-postmortem` skill's landing rules, so later postmortems have somewhere to put new guardrails):

- One invariant per script, named `verify-<the-thing-checked>`; **file name = command name = gate name**.
- Non-zero exit on violation; failure output names the offending path **and the fix command**.
- Written in bash (Git for Windows ships it; GitHub runners have it). If the project has a scripting convention in its own language, port the reference script rather than adding a runtime.
- One entry point `check` on the existing task runner, with groups: `check docs`, `check pairs [range]`, `check commits [range]`, `check stack`, `check all`. Local and CI call the same entry point, never individual scripts.
- The directory name is recorded in `AGENTS.md` and never changes.
- When copying, fill the configuration lines at the top of each script from the interview and `AGENTS.md#commands`: `DOC_PAIR_LANGS`, `DOCS_STRICT`, `MAX_LINES`/`MAX_WORDS`, `BASE_REF`, the `STACK_*` commands in `check`, `modules.txt`, `commit-types.txt`. `check stack` refuses to run while a `<<placeholder>>` remains.

Reference implementations in `references/checks/`:

| Script | Invariant |
| --- | --- |
| `verify-module-readmes.sh` | Every module directory listed in `checks/modules.txt` has a `README.md` with the required headings |
| `verify-md-links.sh` | Every relative link in `*.md` resolves to an existing file |
| `verify-doc-pairs.sh` | In a diff range: module code changed ⇒ its README changed (strict mode, bypass via env/label); `README.md` changed ⇒ `README.<lang>.md` changed |
| `verify-agents-md-budget.sh` | Root `AGENTS.md` within its line and word ceiling |
| `verify-decision-format.sh` | Each `docs/decisions/**/*.md` has a `Status:` matching its folder, the required headings, and a non-empty *Alternatives considered* |
| `verify-commit-convention.sh` | Each commit subject in a range (and optionally a PR title) matches `type(scope)?: summary` with the allowed type set |
| `check` | Entry point; groups the above plus the stack's format / lint / typecheck / test commands |

Ship `modules.txt` and `commit-types.txt` beside them. Every script was proven against a planted violation when this skill was written; prove them again in the target repo (Step 4) — a check nobody has seen fail is decoration.

## Maintenance rules baked into the output

Write these into the generated `AGENTS.md` (they are what keeps it lean after you leave):

- When an agent makes the same mistake twice, add **one line** here with a link to the explanation — do not add a paragraph.
- When a rule becomes enforced by a check or a linter, **delete it from here**; the check is its home now.
- When `verify-agents-md-budget` goes red: relocate → condense → and only then raise the ceiling, with the reason in the PR.
- Subdirectory rules go in that directory's `AGENTS.md` and do not consume the root budget.

## Adopt mode specifics

An existing `AGENTS.md` is usually valuable and bloated at once. Work section by section:

1. Classify each paragraph with the tier table in `references/landscape.md`: standing order (stays), procedure (→ `docs/` or a skill), module fact (→ module README), decision rationale (→ `docs/decisions/`), history (→ delete; git has it), generic advice (→ delete).
2. Show the user the proposed moves as a table before touching anything.
3. Keep the user's voice and specific gotchas — those are the highest-value lines in any agent file. What gets cut is restatement, not knowledge.

## Audit mode

Run `references/slop-checklist.md` against the root file and any `docs/AGENTS.md`-like files. Report findings as: file:line → which checklist item → suggested home. No edits.

## References

- `references/landscape.md` — what deepseek-harness, openclaw, codex, opencode, goose, ghostty do; what the studies found; the tier table used in adopt mode
- `references/slop-checklist.md` — the audit list
- `references/templates/` — one skeleton per generated file
- `references/stacks/{python,typescript,rust,go}.md` — commands, CI job bodies, hook configs, coverage tooling per language
- `references/checks/` — reference verify scripts and the `check` entry point
