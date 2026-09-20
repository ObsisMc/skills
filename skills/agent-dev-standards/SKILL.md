---
name: agent-dev-standards
disable-model-invocation: true
description: Initialize or audit a software project's AI-collaboration standards — a lean root AGENTS.md (with an alias file only if the user's agent tooling needs one), per-module README contracts, docs/ standards for engineering practice, testing, decisions (ADR) and postmortems, CONTRIBUTING + PR template, a CI pipeline with format / lint / typecheck / test-coverage / commit-convention / docs-gates jobs, a checks directory of verify scripts, and pre-commit hooks — all derived from the real repository, on the toolchain the repository already uses, and verified by running the commands. Every rule that says "always do X after a change" is paired with a check that fails when X was skipped. Use when the user says 初始化 AGENTS.md / CLAUDE.md, 给项目加 AI 开发规范, 约定开发流程, set up agent instructions, "make the AI follow our conventions", "add a Definition of Done", scaffold CI and commit conventions for an AI-driven repo, or asks to audit / tidy an existing AGENTS.md that has grown stale or bloated. Tool-agnostic — the output works for any agent that reads AGENTS.md.
---

# Agent Dev Standards

Give a repository a set of standards that an AI agent follows on **every** change, and make each standard fail loudly when skipped. The output is not a knowledge base about software engineering; it is a working agreement plus the gates that enforce it.

This skill deliberately ships **no scripts, no language catalogue, and no CI template**. It tells you what each artifact must do; you research the target repo and the current ecosystem to decide how. That keeps the skill valid when the toolchain changes — the contracts in `references/gates.md` do not.

Three ideas drive every decision below. Read `references/landscape.md` if you want the evidence behind them.

1. **The root file is always in context, so it must be lean and project-specific.** Generic advice the model already knows measurably *hurts* agent performance and raises cost. Every line in the root `AGENTS.md` has to pass the test: *would removing it make an agent do something wrong in this repo?*
2. **One home per fact.** Each rule lives in exactly one place; everything else links there. The root file carries standing orders (1–3 lines each, with a link); long explanations live in `docs/`; module-specific facts live in the module's README.
3. **A rule is only as strong as what fires it.** "Always update the docs" written in prose is followed most of the time. The rest is why every process rule you generate is paired with a check in the checks directory that runs locally and in CI.

## Output language

Write the root `AGENTS.md`, `CONTRIBUTING.md`, PR template, and every check script in **English** — agents read them and one canonical version avoids two homes for one rule. Write `docs/*.md` and module READMEs in English too, and add a translated pair (`README.<lang>.md`, `docs/<name>.<lang>.md`) when the user asks for one (see the interview). Talk to the user in the language they are using.

## Workflow

Follow these steps in order. Do not generate anything before the survey and the research are complete — generated files must be derived from the repository, not from the templates alone. The templates in `references/templates/` are skeletons that show shape and tone; the content comes from what you find.

### Step 1: Survey the repository

Establish facts before asking anything. Detect:

- Language(s), package manager, task runner, and the existing formatter / linter / type checker / test runner with their config files. **Never introduce a competing tool** for a role the repo already fills.
- Existing CI definitions, hook mechanism, and hook-framework configs.
- Top-level module directories (the things that deserve a README contract) — see `references/stack-research.md` §6.
- Existing `AGENTS.md`, `CLAUDE.md`, other agent instruction files, `docs/`, `CONTRIBUTING.md`, ADRs, postmortems. Their presence decides the mode:
  - **init** — no agent instructions exist. Generate the full set.
  - **adopt** — some exist. Keep everything that still holds, fill the gaps, and relocate content that sits in the wrong tier (a 400-line AGENTS.md usually contains three docs that want to be files). Never overwrite a file the user wrote without showing the diff first.
  - **audit** — the user only wants a review. Run `references/slop-checklist.md` against the existing files and report; change nothing unless asked.
- `git log --oneline -30` for the current commit message style; if it already follows Conventional Commits, keep its type set rather than imposing a new one.
- Branch protection / required status checks on the main branch, if the hosting platform exposes them — the gates are only mandatory once the CI jobs are required there.

### Step 1b: Research the toolchain

Follow `references/stack-research.md`. Fill its role table (install, format, lint, typecheck, test subset, test with coverage, task runner, hooks, CI) with the exact commands for *this* repo, taken from the repo's own configuration and the tools' current documentation — not from memory. Where a role has no tool, research the current ecosystem and bring a proposal with one line of evidence to the interview. Also check how each target agent the user names currently loads instruction files (its own docs), since that decides whether an alias file is needed at all.

### Step 2: Interview

Ask only what the survey and research cannot answer. One message, grouped. Suggest a default for each so a "go with defaults" reply is enough.

| Question | Default | Why it matters |
| --- | --- | --- |
| Translated doc pairs? Which language? | Infer from the language the user is writing in (Chinese → `zh`); offer it, let them decline or change | Pairs add a `verify-doc-pairs` gate and a DoD line; nobody wants that imposed silently |
| Coverage threshold for the `test` job | 80% line coverage if the repo has no history; keep the existing number otherwise | Too high blocks adoption, too low is theater |
| Target agents | All — the output is tool-agnostic anyway | Decides whether an alias file is needed and where to mention agent-specific loading behavior (from the research, not assumed) |
| Tool proposals for empty roles | The research's pick, with its evidence | The user may already have an opinion; a tool imposed silently gets ripped out |
| Module list | The survey's detection | It becomes the module registry the docs gate reads |
| Name of the checks directory | `checks/` (avoid names that collide with domain terms in the project — e.g. `guardrails/` in an LLM project) | Recorded in `AGENTS.md` and never changes afterwards, so it is worth one question |
| Pre-commit mechanism | Whatever the repo has; else the zero-dependency option the VCS supports; a hook framework if the user prefers | Hooks must travel with the repository and install **automatically** from the existing install command — a hook nobody installed is not a gate |
| Postmortem policy | `ask` — after fixing a bug that clears the bar, the agent explains why and asks before writing | `auto` writes without asking; `manual` removes the self-check from the DoD entirely |
| Strictness of the docs gate | `strict` — module code changed ⇒ module README touched in the same PR, bypass only with an explicit PR label | The user asked for "docs updated on every change"; make the bypass explicit rather than the rule soft |

Do not ask about things like "which sections do you want" — the layering is the point of the skill.

### Step 3: Generate

Produce the files below. Documents have a template in `references/templates/`; read the template, then write the real file from the survey. Where the template has `<<PLACEHOLDER>>`, the value comes from the repo, the research, or the interview — never leave a placeholder in output. Where you genuinely cannot determine something (a module's invariants, say), write `TODO(owner): …` with a one-line question, so the gap is visible instead of papered over with plausible prose.

| File | Source | Notes |
| --- | --- | --- |
| `AGENTS.md` (root) | `templates/AGENTS.md` | ≤ 120 lines / ≤ 1,200 words. Standing orders only; every rule links its home. The **Definition of Done** section is the heart — it is what the agent reads before saying "done" |
| Alias file (e.g. `CLAUDE.md`) | — | Only if the research shows the user's agent tooling does not read `AGENTS.md` natively, or one already exists. Content is one import line in the form that tool supports, pointing at `AGENTS.md`. Use the import, not a symlink |
| `<module>/README.md` (one per module) | `templates/module-README.md` | The module's contract. Pre-fill from code: purpose, public surface, invariants, allowed dependencies, how to test, known limitations, related decisions. Mark unknowns `TODO(owner)` |
| `<module>/AGENTS.md` | — | Only when a module has operating rules that differ from the root (a generated directory, a vendored tree, a package with its own test runner). Do not create empty ones |
| `docs/README.md` | — | A ten-line index: one line per doc under `docs/` with what it is for. The root's Layout table links here |
| `docs/architecture.md` | `templates/architecture.md` | Module map, one-line responsibility per module, dependency direction rules ("who may import whom"). If the repo already has one, link it instead |
| `docs/engineering-standards.md` | `templates/engineering-standards.md` | The general practice the user wants agents to follow. Each rule is one decidable sentence plus a Good/Bad example **in the project's language**. Rewrite the template's examples; do not ship pseudocode |
| `docs/testing.md` | `templates/testing.md` | Test tiers, what must have a test and what must not, mock policy, flaky-test policy, coverage gate, how to run subsets |
| `docs/decisions/README.md` | `templates/decisions-README.md` | Lightweight ADR convention: lifecycle folders, skeleton, mandatory *Alternatives considered*, when to write one, the format check |
| `docs/postmortem/README.md` | `templates/postmortem-README.md` | Self-contained: the bar, required sections, naming, index table, guardrail landing order. Works without any postmortem skill installed; if one is installed it is used for the writing |
| `CONTRIBUTING.md` | `templates/CONTRIBUTING.md` | Setup, branch naming, commit convention with examples, PR expectations, how to run the checks locally |
| PR template | `templates/pull_request_template.md` | At the path the repo's hosting platform reads. Problem / Change / **Evidence** (what ran, what did not) / Docs / Decision |
| CI pipeline | `references/gates.md` → *The CI contract* | Jobs `format`, `lint`, `typecheck`, `test`, `commit-convention`, `docs-gates`, implemented on the platform the repo uses with the commands from the research. Drop `typecheck` where the compiler owns it |
| Checks directory | `references/gates.md` → *The verify scripts* and *The `check` entry point* | Write each verify script and the `check` entry point to the spec, in the repo's scripting convention, wired onto its task runner |
| Hooks | `references/gates.md` → *The hook contract* | pre-commit: format + lint on staged files; commit-msg: Conventional Commits check. Installed by the repo's install command, not a separate step; `verify-hooks-installed` guards that. Fast, staged-only; everything repo-wide stays in CI |
| Translated pairs | — | If requested: `README.<lang>.md` beside every module README and `docs/<name>.<lang>.md` beside every doc except `AGENTS.md`. Same section structure, translated by you now, kept in sync by the `verify-doc-pairs` gate later |

Order of writing: `AGENTS.md` last. Everything else exists first so its links resolve.

### Step 4: Verify

Nothing goes into `AGENTS.md`'s command block that you have not executed. Run:

1. Every command listed in `AGENTS.md` (install, format check, lint, typecheck, test subset). A command that fails on the current tree either gets fixed, gets removed, or gets a note in the report — never silently shipped.
2. The `check` entry point end to end, so the docs gates pass on the tree you just produced (module READMEs exist, links resolve, budget holds, decisions folder parses).
3. Every verify script against a planted violation on a scratch branch (`references/gates.md` → *Proving the gates*): watch it go red, revert. `verify-commit-convention` additionally in dry-run mode over the last 20 commits; report how many would fail so the user knows what the gate will do to their history.
4. The hooks: clone the repo to a temporary directory, run only the install command from `AGENTS.md#commands`, and confirm the hooks are active there (`verify-hooks-installed` passes); then, on a scratch branch, make one commit with an unformatted file and one with a bad message and watch both be rejected. Delete the branch and the clone.
5. The CI definition with whatever local validation the platform offers (a linter, a dry run); if none exists, at least confirm every command it calls is one you ran in item 1.

Anything you could not run (no network, missing toolchain, sandbox) goes into the final report as *unverified*, by name.

### Step 5: Report

Lead with what exists now and what enforces it, as a table: rule → where it is written → what check fires. Then the toolchain decisions with their evidence, whether branch protection makes the CI jobs required (or the `TODO(owner)` to do so — see `references/gates.md` → *Making the gates mandatory*), the list of `TODO(owner)` items, then unverified commands and unproven gates. Keep it short; the files are the deliverable.

## The Definition of Done

This is the section that turns the root file from documentation into a process. Write it as a checklist an agent runs before declaring a task complete; keep each line decidable. Adapt the template's wording to the repo, but keep these four groups:

**Before changing**: read the affected module's README (and `AGENTS.md` if present); reproduce a bug through the real entry point; before restoring or deleting code that looks odd, check `docs/decisions/` and the VCS history for the symbol.

**While changing**: one owner per responsibility — a new abstraction needs a responsibility nothing else holds; comments state contracts and "why" (ownership, ordering, failure modes, platform constraints), never restate code; no parameters, config, or compatibility branches without a current consumer; prefer the smallest production diff.

**After changing** (each line has a gate):
- Behavior changed ⇒ the module README's interface / invariants / limitations sections updated in the same commit — *gate: `verify-doc-pairs`, strict mode*.
- Translated pair updated with the original — *gate: `verify-doc-pairs`*.
- A choice another agent might re-litigate ⇒ a record in `docs/decisions/` — *gate: `verify-decision-format`* (checks form; judgment stays with the agent).
- Meaningful behavior ⇒ a test that failed before and passes after; no tests for static values or that merely mirror the implementation — *gate: `test` job coverage threshold*.
- Ran format, lint, typecheck, the relevant test subset; the PR's Evidence section lists what ran and what did not — *gate: the CI jobs; the PR template makes omission visible*.
- Commits follow Conventional Commits (`type(scope)!?: description`, `BREAKING CHANGE:` footer) — *gate: commit-msg hook rejects the commit; `commit-convention` job catches a bypass; branch protection blocks the merge*.
- A bug that escaped to users / a merged PR / a release and clears the postmortem bar ⇒ follow the postmortem policy — *gate: none possible; the policy line says whether to ask, write, or wait to be asked*.

## The checks directory

Verify scripts are the enforcement layer; `references/gates.md` specifies each one. The conventions that matter to the rest of the output (they match the `bug-postmortem` skill's landing rules, so later postmortems have somewhere to put new guardrails):

- One invariant per script, named `verify-<the-thing-checked>`; **file name = command name = gate name**.
- Non-zero exit on violation; failure output names the offending path **and the fix command**.
- Written in the repo's own scripting convention, adding no runtime the repo does not already have.
- One entry point `check` on the existing task runner, with groups `docs`, `pairs`, `commits`, `stack`, `all`. Local and CI call the same entry point, never individual scripts.
- The directory name is recorded in `AGENTS.md` and never changes.
- Configuration (pair languages, strictness, budget ceilings, base ref, stack commands, module registry, commit types) sits at the top of each script or in a sibling data file; `check stack` refuses to run while a placeholder remains.

A check nobody has seen fail is decoration — Step 4 proves every one in the target repo.

## Maintenance rules baked into the output

Write these into the generated `AGENTS.md` (they are what keeps it lean after you leave):

- When an agent makes the same mistake twice, add **one line** here with a link to the explanation — do not add a paragraph.
- When a rule becomes enforced by a check or a linter, **delete it from here**; the check is its home now.
- When `verify-agents-md-budget` goes red: relocate → condense → and only then raise the ceiling, with the reason in the PR.
- Subdirectory rules go in that directory's `AGENTS.md` and do not consume the root budget.

## Adopt mode specifics

An existing `AGENTS.md` is usually valuable and bloated at once. Work section by section:

1. Classify each paragraph with the tier table in `references/landscape.md`: standing order (stays), procedure (→ `docs/` or a skill), module fact (→ module README), decision rationale (→ `docs/decisions/`), history (→ delete; the VCS has it), generic advice (→ delete).
2. Show the user the proposed moves as a table before touching anything.
3. Keep the user's voice and specific gotchas — those are the highest-value lines in any agent file. What gets cut is restatement, not knowledge.

## Audit mode

Run `references/slop-checklist.md` against the root file and any `docs/AGENTS.md`-like files. Report findings as: file:line → which checklist item → suggested home. No edits.

## References

- `references/stack-research.md` — how to establish the repo's toolchain and commands by investigation, and how to choose a tool when a role is empty
- `references/gates.md` — the contract for every verify script, the `check` entry point, the CI jobs, and the hooks
- `references/landscape.md` — the evidence behind the layering: what well-run agent-driven projects do, what the studies found, the tier table used in adopt mode
- `references/slop-checklist.md` — the audit list
- `references/templates/` — one skeleton per generated document
