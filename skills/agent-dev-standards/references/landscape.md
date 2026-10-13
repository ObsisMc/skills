# Landscape: how well-run open-source projects instruct their agents

Surveyed September 2026. Read this when you need to justify a layering decision to the user, or when classifying paragraphs in adopt mode.

## Contents

1. The tier table (used in adopt mode)
2. deepseek-harness — rules with one home, enforced by gates
3. openclaw — a working agreement and authority boundaries
4. codex, opencode, goose, ghostty — the lean files
5. What the studies found
6. How agents load these files (a research item, not a table)

## 1. The tier table

Every paragraph in an agent-facing document belongs to exactly one tier. Adapted from deepseek-harness `docs/AGENTS.md`.

| Tier | Job | Does not belong there |
| --- | --- | --- |
| Root `AGENTS.md` | Standing orders an agent needs in context every session: commands, layout, Definition of Done, boundaries, pointers. 1–3 lines per rule, each linking its home | Stories, worked examples, procedures, anything restated from a linked home, generic advice |
| Subdirectory `AGENTS.md` | Orders specific to that subtree | Repo-wide rules the root already carries |
| Module `README.md` | The module's contract: purpose, public surface, invariants, allowed dependencies, how to test, known limitations | Restating code or docstrings; other modules' concerns |
| `docs/architecture.md` | The map: modules, ownership, dependency direction, extension points | Per-module detail (→ README), decision rationale (→ decisions), status annotations |
| `docs/engineering-standards.md`, `docs/testing.md` | Practice references read on demand | Project-specific commands (→ root) |
| `docs/decisions/` | Why a choice was made and what it beat | Migration plans once shipped; anything code and tests already explain |
| `docs/postmortem/` | Why an escaped bug got past every net; the only tier where narrative belongs | Design decisions |
| Skills (`.agents/skills/`) | Reusable multi-step workflows | Product contracts (→ docs or code) |
| Git history / PR bodies | What changed and when | — (never copy it into standing docs) |

Placement rule of thumb: bugs → postmortems; rationale → decisions; procedures → skills or cookbooks; contracts → module READMEs; standing orders → root with a link.

## 2. deepseek-harness

Root `AGENTS.md` (~1,900 words, budget-gated) is explicitly "standing orders": each rule is one to three lines linking its home. What makes the repo worth copying is the machinery around it:

- **`docs/AGENTS.md` is a documentation standard**, not more rules about code. It defines the tier table, writing rules, word budgets, and a slop checklist.
- **Every documentation rule has a script**: `verify-doc-budgets` (word ceilings), `verify-md-links`, `verify-md-wrap` (one physical line per paragraph), `doc-typecheck` (fenced `ts` blocks must compile), `verify-export-jsdoc` (every export documents its contract), `verify-agent-note-format`.
- **Agent Notes** (their ADR variant) live in `.agents/notes/{proposed|implemented|rejected}/<class>/yyyy-mm-dd-topic.md`. Fixed skeleton; `## Alternatives considered` mandatory ("a decision recorded without what it beat invites re-litigation"); implemented notes are present-tense and kept current with shipped reality; proposal-era headings (`## Plan`, `## Acceptance criteria`) are rejected by the gate once implemented; a note is never edited into a different decision — supersede and cross-link.
- **Comments state contracts, not reasoning transcripts.** Keep behavior, failure, timing, ownership, safe-use facts; delete narration, test walkthroughs, code restatement. "An empty `catch` names the error and why." Ban metaphors; name the exact thing (`response fields`, not `response shape`).
- **Testing policy** (`docs/testing.md`): unit / per-file 100% coverage gate / real-API e2e / recorded-session snapshot. Principles: *prefer the real implementation over a mock* (mock only the expensive or nondeterministic boundary); *verify the world, not the self-report* (e2e re-reads files externally instead of grepping the agent's output); *test the real entry path* (the built artifact, not the source shim); *a guard only guards if the regression fails it* — introduce the regression, watch red, revert.
- **Postmortems** are a separate tier with a hard bar (subtle + systemic + costly-to-rediscover) and an executive-summary-first structure. Guardrails from a postmortem land in tests, verify scripts, or one line in `AGENTS.md`, and back-link the postmortem.
- Package READMEs must carry `## Known Limitations and Deferred Work`, with an allowlist for packages that have none.

## 3. openclaw

Root `AGENTS.md` (~2,900 words) barely mentions code style. It is a **working agreement**:

- **Design priorities**: *One owner per responsibility* (an owner makes decisions and changes authoritative state; callers consume; adapters translate; caches derive with explicit invalidation); *small core, capable plugins*; *stable conversation context*.
- **"One owner, complete cutover"** as the change workflow: **Intent** (reproduce through the real entry point; before restoring a missing path, `git log -p -S <symbol>` to learn why it was removed) → **Owner** (find the existing code that absorbs the change; a new owner needs a missing responsibility) → **Cutover** (migrate all callers together; remove superseded code, wrappers, duplicate state, docs) → **Proof** (exercise the real flow; a helper test alone is insufficient).
- **Tests**: "must protect meaningful behavior; skip tests for reversible, low-impact changes that merely mirror the implementation"; "do not hide failures with retries, longer timeouts, weaker assertions, broader mocks, or altered baselines"; fix flaky tests you encounter, do not route around them.
- **Comments** "explain non-obvious ownership, lifecycle, ordering, cleanup, platform, and dependency constraints, not syntax."
- **Authority and safety** is a full section: what is read-only, what needs per-task approval, what is never done.
- **"Read when relevant"** is a pointer index to subtree `AGENTS.md` files and docs — the root does not repeat them.
- Explicitly: "Edit canonical `AGENTS.md` files directly; do not add `CLAUDE.md` aliases."
- Skills carry the procedures: `deslop` (diff-scoped cleanup of narrating comments, imagined-state defensive checks, `as any` laundering, single-use helpers, contract-less compatibility shims), `autoreview`, `openclaw-testing` (a table from change type → smallest sufficient proof).

## 4. The lean files

- **ghostty** (~40 lines): commands with the flags that matter, three directory pointers, a "never create issues or PRs" rule. Nothing else.
- **goose**: `CLAUDE.md` is literally `@AGENTS.md`. A `## Never` list. Comment rules: "never add comments that restate what code does; only 'why' not 'what'". "Avoid overly defensive code — trust the type system." "Booleans should default to false, not be optional."
- **opencode**: every style rule has a `// Good` / `// Bad` pair. "Do not extract single-use helpers preemptively." "Avoid mocks as much as possible." Branch names ≤ 3 words, no `feat/` prefixes. Commit format `type(scope): summary` with the allowed type list and three examples.
- **codex**: rules link the exact clippy lint they enforce. Hard size limits: modules target < 500 LoC, must split at ~800. "Features that change the agent logic MUST add an integration test." "Do not add tests for values that are statically defined." Model-visible context rules with a hard token cap.

Common to all of them: exact commands with flags; examples over paragraphs; an explicit never-list; no repository overview beyond a directory table.

## 5. What the studies found

- **GitHub, 2,500+ repositories** (github.blog, 2025): effective files share six elements — executable commands, testing protocol, project structure, code-style *examples*, git workflow, explicit boundaries (✅ always / ⚠️ ask first / 🚫 never). "Never commit secrets" was the single most common useful constraint. Paragraph-long explanations underperform one code example.
- **ETH Zurich, "Agent READMEs"** (arXiv 2511.12884, Feb 2026): LLM-generated context files *reduced* task success in 5 of 8 settings and raised inference cost 20–23%. 95–100% of them contained a repository overview, and agents with the file found relevant files no faster than agents without — the overview duplicated what the agent derives by reading. Human-written, minimal files gave a marginal (~4%) gain.
- **Red Hat Developer** (July 2026): keep the root under ~150 lines; treat it as an index with pointer tables; apply "would removing this line cause a mistake?" to every line; put procedures in skills, not in the root; update the file when an agent repeats a mistake.

Practical consequence: the generic best-practice content the user wants agents to follow is valuable, but it belongs in `docs/engineering-standards.md` (read on demand, with project-language examples), not in the root file.

## 6. How agents load these files

Which files an agent reads at start, which it loads lazily, and whether it honours an alias or import file are **tool facts that change between releases**. Do not rely on a remembered table; for each target agent the user names, check its current documentation during Step 1b and record what you found in the report. Three consequences hold regardless of the answers:

- `AGENTS.md` is canonical. If a tool needs an alias file at all, that file contains only the import line in the form the tool supports — never a copy of the content, and not a symlink (symlinks break on some clones).
- Do not use any tool-proprietary rule directory; path-scoped rules go in subdirectory `AGENTS.md` files, which most tools load automatically and the rest reach through the root rule "read the module's README/AGENTS.md before editing it".
- Because subdirectory files are loaded lazily by some tools and not at all by others, the root must carry the rule that makes reading them mandatory. That rule is what makes module READMEs part of the process rather than decoration.

Sources: deepseek-ai/deepseek-harness (`AGENTS.md`, `docs/AGENTS.md`, `docs/testing.md`, `.agents/notes/README.md`, `packages/AGENTS.md`); openclaw/openclaw (`AGENTS.md`, `docs/AGENTS.md`, `.agents/skills/deslop`, `.agents/skills/openclaw-testing`); openai/codex, sst/opencode, block/goose, ghostty-org/ghostty, cline/cline root files; github.blog "How to write a great agents.md"; arXiv 2511.12884; developers.redhat.com "Standardize project context with AGENTS.md and Agent Skills".
