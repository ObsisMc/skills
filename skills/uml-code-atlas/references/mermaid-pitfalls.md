# Mermaid Pitfalls

Two failure classes, and they need different defenses:

- **Parse errors** — the block is invalid; `scripts/check_mermaid.mjs` catches these.
- **Renders-nowhere** — the block parses against current Mermaid but the reader's runtime is older or restricted, so they see a code block. The validator says OK. Only prevention works.

Read this before writing, not after. Contents:

1. [Universal rules](#1-universal-rules)
2. [Per diagram type](#2-per-diagram-type)
3. [Constructs to avoid preemptively](#3-constructs-to-avoid-preemptively)
4. [Recovery when a user reports a blank diagram](#4-recovery-when-a-user-reports-a-blank-diagram)

---

## 1. Universal rules

**Quote every node label.** `A["文本 · 带 / 和 ()"]` always; `A[文本]` only when the text is a bare identifier. Unquoted labels break on `/`, `(`, `)`, `,`, `:`, `-` in ways that vary by diagram type.

**One colon per edge label.** In `stateDiagram-v2` and several others, the colon separates the edge from its label, and a second colon on the line restarts parsing. This is the single most common hand-written failure:

```
A --> B : Install::Refused          ❌ parse error
A --> B : Install 为 Refused         ✅
```

The same applies to `Foo::bar`, `namespace::type`, and `time: 30s` inside labels. Rewrite in prose or use a middle dot `·`.

**Avoid arrows and symbols inside labels.** `→ ≠ ⏱ ❌ ✓` are fine in surrounding Markdown prose and in tables, and they're valuable there — but inside Mermaid labels they interact badly with edge syntax in some parsers. Write "到", "不等于", "超时 30s". Keep the symbols for the impact matrix, which is a table, not a diagram.

**`#` starts an entity code.** `Attach #1` can be read as the start of `#35;`. Use `Attach A` / `Attach B`.

**`<br/>` works in node labels, sequence messages, and notes.** It does *not* reliably work in `stateDiagram-v2` transition labels — write those as one short clause instead.

**Keep it under ~20 nodes.** Beyond that, both rendering and comprehension degrade. Split the diagram.

---

## 2. Per diagram type

### `graph` / `flowchart`

The most robust type; prefer it when unsure. `graph TB` and `flowchart TB` are interchangeable in practice.

- Subgraph titles need quotes when they contain anything but word characters: `subgraph FE["前端 · TypeScript"]`.
- `direction TB` inside a subgraph works and is often needed.
- `classDef` + `class` and per-node `style` both work. `style nodeId fill:#2d6a4f,color:#fff` is the reliable form for one-off severity coloring.
- Dotted arrows with labels — `A -.->|"标签"| B` — need the quotes.
- `([...])` stadium, `[(...)]` cylinder, `{...}` diamond all render widely.

### `sequenceDiagram`

Very robust. Safe to use freely.

- `participant X as 显示名` — the alias may contain spaces; the participant id may not.
- `alt` / `else` / `opt` / `loop` / `par` all fine. Their condition text may contain slashes and parens.
- `--x` (failed message) and `-->>` (dashed reply) render fine.
- `Note over A,B: 文本<br/>更多` works, including `<br/>`.
- `rect rgb(90, 40, 40)` … `end` works and is the best tool for correct-vs-wrong comparisons. Use `rgb()`, not hex, inside `rect`.
- `autonumber` on the first line is worth it for anything over ~6 messages.

### `stateDiagram-v2`

Parses strictly. The main trap is the colon rule above.

- Avoid `<br/>` in transition labels.
- `note right of X` … `end note` works; keep each line short and colon-free.
- `[*]` for start and terminal is fine, including multiple terminals.
- Composite states parse but nest awkwardly; prefer separate diagrams.

### `classDiagram`

Parses, but has the widest rendering variance. Simplify defensively.

- **Avoid `~T~` generics.** `Vec~WarmEntry~` parses but is a common renderer casualty. Write `entries : Vec of WarmEntry`.
- **Avoid parenthesized return types.** `+warm(key, cwd) (SessionId, Vec~Option~)` is fragile. Drop the return, or state it in the 要点.
- Prefer `+field : Type` over `+Type field`; both parse, the former is more stable.
- `<<enum>>` works but escaping as `&lt;&lt;enum&gt;&gt;` is safer across renderers.
- Relationship syntax `*--`, `o--`, `..>`, `<|--` is fine. Cardinality strings like `"0..64"` parse but add little; drop them if a block misbehaves.

### `erDiagram`

Robust and underused. Ideal for schema diagrams.

- `TABLE ||--o{ OTHER : "关系说明"` — quote the label.
- Attribute lines are `TYPE name "comment"`; the comment must be quoted and is a great place for the *why* (`INTEGER synced_through "该 provider 已覆盖到第几轮"`).
- `PK` / `FK` after the name render as badges.

---

## 3. Constructs to avoid preemptively

These parse against current Mermaid and still commonly fail to render:

| Construct | Why | Use instead |
|---|---|---|
| `mindmap` | newer diagram type, absent from many bundled runtimes | `graph LR` with one branch per category |
| `timeline` | same | `graph LR` chain or a table |
| `quadrantChart`, `sankey`, `block-beta`, `packet-beta`, `architecture-beta` | newer or beta | `flowchart` / table |
| `gitGraph` | supported unevenly | `flowchart LR` |
| `~T~` generics in `classDiagram` | renderer variance | `X : Vec of Y` |
| `%%{init: ...}%%` directives | often stripped by sanitizers | per-node `style` |
| `click` handlers | stripped under strict security levels | plain labels |
| inline HTML beyond `<br/>` and `<b>` | sanitized | plain text |

`erDiagram`, `sequenceDiagram`, `flowchart`, `graph`, `stateDiagram-v2`, and `classDiagram` cover everything an architecture atlas needs. Stay inside that set.

---

## 4. Recovery when a user reports a blank diagram

Do not guess and do not apologize into a rewrite. In order:

1. **Run the validator** on the file. A real parse error usually explains one of them.
2. **Downgrade the pitfalls-list constructs** in *all* blocks, including those that parsed clean — a user reporting "好多图" usually has one parse error plus several renders-nowhere blocks, and only fixing the parse error leaves them still broken.
3. **Sanitize labels globally**: strip `→ ≠ ⏱ ❌`, collapse `::`, replace `#N`.
4. **Re-validate**, then say specifically what you changed and why. Distinguishing "this was an actual syntax error" from "this parsed but I downgraded it for compatibility" is useful information for them.
5. If a block still fails on their side, degrade its type: `classDiagram` → `graph TB` with fields in node labels; `stateDiagram-v2` → `flowchart` with labeled edges. Nothing is lost that the 要点 can't carry.
