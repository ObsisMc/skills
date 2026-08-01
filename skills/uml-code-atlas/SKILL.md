---
name: uml-code-atlas
description: Produce a Mermaid UML architecture atlas that explains a codebase, a PR, or a design proposal — system layering, data model, core call chains, data flow, state machines, and a first-class failure-mode analysis with failure-scenario walkthroughs and acceptance criteria. Use this skill whenever someone asks for UML, architecture diagrams, sequence/class/state/ER diagrams, a call-chain or data-flow picture, "help me understand this PR/module/service", "画个图", "架构图", "时序图", "调用链", "数据流", a design review of a proposal doc, or says they want to intuitively grasp how a system works — even if they never say the word "UML". Also use it when reviewing a design document for gaps, since the atlas is how the gaps get found.
---

# UML Code Atlas

Turn real code (or a real proposal) into a diagram atlas that a reviewer can read in ten minutes and come away knowing not just how the system works, but where it breaks and what nobody has decided yet.

## The one idea that matters

**The atlas is an analysis instrument, not documentation.** A diagram that only restates what the code obviously does is wasted effort — the reader could have read the code. The value is in what the diagramming *forces you to discover*: the constraint that explains why the design is shaped this way, the failure that nobody can detect, the branch of the state machine that has no handler.

A good atlas ends by making the source document or the code look different than it did before. If you finish and have found nothing — no gap, no unstated invariant, no question worth asking — you have drawn pictures, not analyzed anything. Go back to §5.

Two habits carry most of the weight:

- **Every diagram is followed by 要点 / Key points that are not on the diagram.** If a bullet could be recovered by looking at the boxes and arrows, delete it. Write down the *reason* — usually found in a code comment, a doc paragraph, or the shape of an error path — not the mechanics.
- **Failure analysis is a section, not a footnote.** Roughly a third of a strong atlas is failure modes, silent failures, and scenario walkthroughs.

---

## 1. Identify what you are analyzing

Three input shapes, three different first moves. Decide before reading anything.

| Input | Signals | First move |
|---|---|---|
| **PR / diff** | a PR URL or number, "这个改动", branch names, "review this" | Get the diff and the commit list. The commit messages are the author's own decomposition — read them first. |
| **Existing repo / module** | a path, a service name, "how does X work" | Find the entry points and the module boundaries. Read any `docs/` first — a repo that documents itself tells you what it considers important. |
| **Design proposal (not yet built)** | a design doc, "提案", future tense, "we're planning to" | The doc is the source of truth, but treat it as a *claim*. Cross-check every claim against the code it says it will change. Gaps between the two are your best findings. |

Mixed inputs are common (a proposal doc plus the code it builds on). Diagram the proposal, ground it in the code, and mark clearly which parts exist and which are proposed — see §4's `(新增)` convention.

**Match the user's language.** Write the atlas in whatever language they asked in. Keep code identifiers, protocol method names, and error codes in their original form regardless.

---

## 2. Ground everything in real source

Never diagram from a PR title, a summary, or memory. Diagrams are load-bearing; a wrong arrow is worse than no arrow because it looks authoritative.

For a PR, this sequence gets you the full change reliably even when the API rate-limits or the diff endpoint 403s:

```bash
git clone --filter=blob:none -q <repo-url> repo && cd repo
git fetch -q origin pull/<N>/head:pr<N>
BASE=$(git merge-base HEAD pr<N>)
git log --oneline $BASE..pr<N>          # author's own decomposition
git diff --stat $BASE pr<N>             # where the mass is
git diff $BASE pr<N> -- docs/           # ★ read this first if it exists
```

Reading order that pays off:

1. **`docs/` diff.** When a repo keeps design docs next to code, the doc diff is the author explaining the change in prose. It is the single highest-value artifact and almost everyone skips it.
2. **Commit messages.** `fix(session): stop a warm session from being deleted while it is attached` is a failure mode handed to you for free. Bug-fix commits inside a feature PR are a map of the race conditions the author already hit.
3. **New files, in full.** Not the diff — the whole file. Doc comments on new types carry the *why* that the diff hides.
4. **Deleted code.** What was removed tells you what the new design replaces, which is how you build the before/after table.
5. **Tests.** Test names state invariants in plain language. A test called `returns_the_entry_when_the_reservation_is_dropped` is telling you the reservation's `Drop` is load-bearing.

Read enough that you could answer "why is this line here?" for anything you draw. If you can't, don't draw it — or draw it and mark it as an open question in §7.

---

## 3. Find the root constraint

Before any diagram, answer one question: **what single constraint makes this design necessary?** Most non-trivial architecture is downstream of one immovable fact — a protocol limitation, a consistency requirement, a latency budget, an ownership boundary.

Examples of the shape:

- *"The protocol only reports a session's model list in the reply to session creation, so a model cannot be chosen until a session exists — therefore opening a chat surface must create one."* Everything else (the pool, the reservation, the eviction bounds) is a consequence.
- *"The protocol has no way to inject history into a provider session, so switching agents can only replay history as text."* Everything about fidelity tiers follows.

Put this in the opening section, before the first diagram, as a paragraph plus a before/after table when the input is a PR. A reader who has this can predict most of the diagrams. A reader who doesn't will experience the atlas as arbitrary complexity.

If you cannot state the root constraint, you have not read enough. Return to §2.

---

## 4. Compose the diagram set

Pick from this menu; don't draw all of them mechanically. A typical atlas runs 8–13 diagrams, of which 4–6 are failure-related.

| # | Diagram | Mermaid type | Draw it when | Must show |
|---|---|---|---|---|
| 1 | System layering & components | `graph TB` with subgraphs | almost always | Every layer the change touches, with file paths in the node labels |
| 2 | Data model | `erDiagram` | persistence or schema is involved | Which tables are on the truth path vs. which are runtime bookkeeping |
| 3 | Core domain types | `classDiagram` | in-memory state machines, pools, registries | Ownership and the enums that encode decisions |
| 4 | Happy-path call chain | `sequenceDiagram` | always | Timeouts, locks taken/not taken, what's awaited |
| 5 | Secondary call chains | `sequenceDiagram` | 1–3 more for the other real paths | The branch structure via `alt`/`else` |
| 6 | Lifecycle state machine | `stateDiagram-v2` | any entity with >2 states | The exemption rules and the terminal states |
| 7 | Data flow panorama | `flowchart LR` | data has multiple sources or consumers | What is *dropped*, and which consumer reads which subset |
| 8 | Evolution walkthrough | `flowchart TB` | a value changes meaning over a sequence | The value at each step, not just the transitions |
| 9–13 | Failure diagrams | see §5 | always | — |

Conventions that make an atlas readable:

- **Mark what's new.** In a PR or proposal atlas, label new components `(新增)` / `(new)` and style them distinctly. Readers need to know what they're being asked to evaluate versus what they must accept as given.
- **Encode severity in color.** Reserve one color for "this is a real design gap", another for "known but undefined", another for "new". Keep it consistent across every diagram and say so in the intro.
- **Node labels carry file paths.** `warm_pool.rs<br/>WarmPool<br/>纯决策 · 无 I/O` is worth three sentences of prose.
- **Put a TOC at the top** with anchor links once you pass ~6 diagrams.

### Writing the 要点

After each diagram, 2–5 bullets. The test for every bullet: *could a careful reader get this from the diagram alone?* If yes, cut it.

Good: "The pool lock is a blocking `std::sync::Mutex` on purpose — a reservation can only be returned from `Drop`, which cannot await, so the compiler rejects any later change that holds the guard across a suspension point."

Bad: "The manager calls the warm sessions module, which calls the pool."

The best 要点 come from doc comments explaining *why*, from asymmetries (why is this path guarded and that one not?), and from things the code deliberately does **not** do.

---

## 5. Failure analysis

This is the part that distinguishes an atlas from a picture book, and the three items below are required output. Read `references/failure-analysis.md` for the full method, taxonomies, and templates — the summary here is only the shape.

**5.1 Failure-mode panorama.** Every point on the main path where something can go wrong, with how it's detected and what happens. A `flowchart` with the happy path down the middle and failure injections pointing at it, plus a table.

**5.2 Silent failures and detectability grading.** The dangerous failures are the ones that don't raise anything. Grade every failure by detectability and mark the ones that silently corrupt data:

`✅ 会报错或留痕 · ⚠ 部分可见 · ❌ 完全静默 · ☠ 会静默损坏数据`

A "belief vs. reality vs. impact" three-column flowchart is the clearest way to show these. Any row marked ❌ or ☠ deserves a paragraph on whether it can be mitigated and what mitigation costs *now* versus *later*.

**5.3 Failure scenario walkthroughs.** Distinct from failure modes: a *mode* is "what can go wrong", a *scenario* is one concrete story followed end to end. Pick 3–8 of the nastiest. Each gets: trigger, sequence diagram, what the user sees, final persisted state as a table, the key judgment call, and a checklist of **acceptance criteria** that can be lifted directly into tests.

The correct-vs-wrong pattern deserves its own diagram whenever a value can be derived two ways and one of them is subtly wrong. Show both in the same sequence diagram using `rect` blocks — this is the single most valuable diagram in an atlas about state consistency.

---

## 6. Validate every diagram before delivering

**Non-negotiable.** Hand-written Mermaid fails often, and a parse error means the reader sees a code block instead of a diagram. Never ship unvalidated diagrams.

```bash
node scripts/check_mermaid.mjs <path-to-atlas.md>
```

First run in a fresh container needs `npm i mermaid jsdom` in the script's directory; the script prints the exact command if the modules are missing. It reports OK/FAIL per block with the parse error and line number.

Parsing is necessary but not sufficient — some constructs parse and still fail to render in older or restricted Mermaid runtimes. `references/mermaid-pitfalls.md` lists the ones worth avoiding preemptively (`mindmap`, class-diagram generics, extra colons in edge labels, and more). Read it before writing diagrams, not after.

If the user reports a diagram didn't render, do not guess: run the validator, and separately downgrade the constructs on the pitfalls list even for blocks that parsed clean.

---

## 7. Close the loop back onto the design

The last section of the atlas is where the analysis pays for itself. Two parts:

**Cross-reference table** (when there is a companion design doc): map each section of the atlas to the section of the design it visualizes. This makes the atlas navigable *and* exposes design sections that no diagram covers — often a sign the design is vague there.

**Open questions / findings.** 4–8 items, each a specific thing a reviewer should push on. Not generic ("consider adding metrics") — specific and grounded:

> §10.1 发现了一处需要收紧的设计：`synced_through_turn_seq` 应改为只在 turn 成功完成时推进，取消"注入成功即推进"那条。设计文档 §5.3 待同步。

> `MAX_LIVE_ENTRIES = 8` 且没有空闲回收：开着 8+ 个聊天界面的用户，最早的会被静默淘汰、下次进入付一次 30s 级别重建。这个数字有依据吗？

Sources for these: constants with no stated justification; comments admitting a tradeoff; error paths that swallow failures; anything the code marks TODO/unwrap/deliberately ignores; asymmetries between similar paths; and any state-machine branch you couldn't find a handler for.

When the atlas contradicts the design doc, say so explicitly and name the section that needs updating. That is the highest-value output this skill produces.

---

## Output format

A single Markdown file, delivered with `present_files`. Structure:

```markdown
# <系统/改动名> — 架构图集
> 配套文档 · 基线 commit / PR 链接 · 状态（已实现 / 提案）
> 图例：(新增) 标记 · 颜色语义

## 0. 这个改动到底做了什么     ← root constraint + before/after table
## 目录                        ← anchors, once past ~6 diagrams
## 1..N 图 + 要点
## N+1 失败模式                 ← panorama / silent failures / matrix
## N+2 失败场景走查             ← per scenario: 时序 · 用户看到 · 最终状态 · 验收标准
## N+3 关键常量与边界           ← every timeout, bound, and retry policy in one table
## N+4 图与设计文档的对应
## N+5 值得追问的点
```

Write to `/mnt/user-data/outputs/` when that path exists; otherwise the working directory. Keep the response after `present_files` to a few sentences: the root constraint you found, and the one or two most interesting findings. Don't narrate the diagram list — the file has it.

---

## Anti-patterns

- **Diagramming from the PR description.** It describes intent; you need behavior.
- **要点 that restate the diagram.** The most common failure. Cut ruthlessly.
- **Failure section that's just a list of `Result::Err` sites.** Failure analysis is about detectability and consequence, not about error enumeration.
- **Softening real gaps.** If the design has an undefined case, draw it in red and label it undefined. An atlas that makes everything look resolved is worse than useless during review.
- **One giant diagram.** If a diagram needs more than ~20 nodes, it's two diagrams.
- **Shipping unvalidated Mermaid.** See §6.
- **Uniform depth.** Spend diagrams where the complexity is. A CRUD endpoint in the same PR as a concurrency-sensitive pool does not get equal treatment.

---

## Reference files

- `references/failure-analysis.md` — the failure-mode method in full: taxonomies, the detectability legend, the correct-vs-wrong pattern, scenario walkthrough template, impact matrix template. Read before writing §5.
- `references/mermaid-pitfalls.md` — syntax that breaks or silently fails to render, per diagram type, plus safe alternatives. Read before writing diagrams.
- `scripts/check_mermaid.mjs` — parses every Mermaid block in a Markdown file and reports failures with line numbers.
