# Template: docs/engineering-standards.md

This is where the general software-engineering practice lives — the content the user wants agents to follow but which would hurt if it sat in the always-loaded root file. It is read on demand (linked from the root's *Read when relevant* and from the DoD).

Two rules for writing it:

1. **Every rule is one decidable sentence** — an agent or reviewer can answer yes/no about a given diff. "Keep functions small" is not decidable; "a function that needs a comment to separate its phases is two functions" is.
2. **Every rule has a Good/Bad pair in the project's language.** The template below uses TypeScript and Python as illustration. Rewrite every example in the repo's language with names that could plausibly appear in the repo. Do not ship the template's examples.

Keep the file under ~250 lines. If a section grows past that, it is a separate doc.

---

```markdown
# Engineering standards

How code in this repository is written. Each rule is one sentence you can check a diff against, followed by an example. Tooling enforces formatting and lint; this file covers what tooling cannot see. Commands live in [AGENTS.md](../AGENTS.md); test practice lives in [testing.md](testing.md).

## Ownership and coupling

**One owner per responsibility.** Exactly one module decides and mutates each piece of state; others call it. If two places can change the same thing, one of them is a bug waiting for a race.

**A new abstraction needs a responsibility nothing else holds.** Before adding a class, service, or helper, name the existing owner you would otherwise extend and say why it cannot absorb the change.

**Dependencies point inward.** <<core>> knows nothing about <<adapters/api/ui>>; the direction table in [architecture.md](architecture.md#dependency-direction) is the contract, `<<verify-dependency-direction or the linter rule>>` enforces it.

**Fix invalid state at its producer.** A defensive check at a consumer that "handles" bad input hides the bug that produced it; validate at the boundary where the data enters (parser, config load, request handler, file read) and trust typed values after that.

```<<lang>>
// Bad — every caller re-validates, so the producer never gets fixed
function render(user: User) {
  if (!user || !user.email) return null
  ...
}

// Good — the parser guarantees the shape; consumers trust the type
const user = parseUser(raw)   // throws on missing email
render(user)
```

**Explicit over implicit at module boundaries.** Defaults are resolved in one visible step (`resolve(request) → Spec`), not scattered `?? default` inside the implementation.

## Size and shape

**A function reads as its happy path.** Validation and edge cases move into named helpers below it; the main function stays scannable in one screen.

**Do not extract a single-use helper preemptively.** Inline it unless it names a real domain concept, is reused, or hides a genuinely complex boundary. Three trivial helpers are harder to read than one clear function.

**A module over <<~500>> lines (tests excluded) is a candidate for splitting; over <<~800>> it must not grow further** — add a new module instead. Move the related tests and docs with the extracted code.

**Prefer early return to `else`.** Nesting depth is a coupling smell.

```<<lang>>
# Bad
def price(item):
    if item.in_stock:
        if item.discount:
            return item.base * (1 - item.discount)
        else:
            return item.base
    else:
        return None

# Good
def price(item):
    if not item.in_stock:
        return None
    if not item.discount:
        return item.base
    return item.base * (1 - item.discount)
```

**Symmetry for parallel values.** If three similar things are handled three different ways, either one of them is special (say why in a comment) or an extraction was missed.

## Comments

**A comment states something the code cannot: why, ownership, ordering, failure modes, platform constraints, or a link to the decision.** Never what the code visibly does.

**No narration.** `// loop over users`, `// return the result`, `# initialize` — delete on sight.

**A docstring states what is not in the signature.** Failure modes, side effects, units, thread-safety, cost. If the signature says it all, no docstring.

**An empty or broad `catch`/`except` names the error and why swallowing it is correct**, and its `try` body is one statement.

**Comments stay local.** Do not explain distant behavior, restate another module's contract, or preserve review history. Link instead.

```<<lang>>
// Bad
// Increment the counter
count++

// Bad — restates the signature
/** Gets the user by id. */
function getUser(id: string): User

// Good — states the contract the signature cannot
/** Resolves from the cache first; a miss hits the DB and may take >100 ms. Throws NotFound rather than returning null so callers cannot forget the check. */
function getUser(id: string): User

// Good — names the reason
// Windows returns EPERM for a directory rename while a handle is open; retry once (see decisions/2026-02-11-rename-retry.md)
```

**TODO markers name an owner or an issue**: `TODO(<<name or #123>>): …`. A bare TODO is a comment nobody will act on.

## Errors and failure

**Fail loud at load time when a configuration is self-contained; otherwise at the earliest point it can be resolved.** Never silently skip a missing referent.

**Do not add error context that adds no information.** `raise … from e` / `.context("failed to X")` when the error already says it failed is noise; add the value that identifies *which* X.

**Every action has a visible outcome or a recorded intentional non-outcome.** A function that does nothing on a branch logs or returns a value that says so; silent no-ops are the hardest bugs to find.

**Do not add retries, fallbacks, or compatibility branches without a named consumer and a removal condition.** Write both in the comment.

## Types and data

**Trust the type system at typed same-process boundaries.** Runtime validation, hostile-input tests, and `None`/`null` checks belong where untrusted data enters (parsers, config, wire, file, process), not between typed functions.

**Opaque identifiers are distinct types, not bare strings**, when the language allows it (branded types, newtypes, `NewType`). A `user_id: str` next to an `order_id: str` is a swap waiting to happen.

**No type laundering.** `as any`, `as unknown as T`, `# type: ignore`, `unsafe` without an adjacent one-line reason is a lint failure, not a shortcut.

**Booleans default to false and are not optional; avoid boolean parameters that make call sites unreadable** (`save(true, false)`) — use an enum, a named option, or two functions.

**Switch on discriminant tags; closed unions end in an exhaustiveness check.** New variants then fail to compile instead of falling through.

## Naming

**Name the role that exists, not the pattern you used.** `UserRepository` over `UserManager`; `retryPolicy` over `helper`; a file named for its responsibility, not `utils.ts`.

**Do not alias imports or rename on import**; consistency of names across files is what lets an agent grep.

**Reserve words with a defined meaning.** <<List the project's reserved vocabulary — e.g. "session", "workspace", "plugin" — and what each means. Link the glossary if there is one.>>

## Dependencies

**Prefer a maintained dependency over hand-rolling when it genuinely deletes owned code and tests.** Otherwise, hand-roll: a dependency for one function is a supply-chain and upgrade cost for nothing.

**Adding a dependency is an *ask first* action** ([AGENTS.md](../AGENTS.md#boundaries)). Say what it replaces and what it costs.

## What this file is not

It does not repeat what `<<formatter>>` and `<<linter>>` enforce; run them. It does not carry project commands (root `AGENTS.md`) or module contracts (each module's README). When a rule here becomes enforceable by a lint rule or a `checks/verify-*` script, add the check and delete the rule.
```

---

## Notes for the generator

- Rewrite every example in the repo's language with plausible domain names from the repo. A Python repo gets no TypeScript.
- Drop rules that do not apply to the language (branded types in Go → drop or restate as "define named types for ids"). Add at most three language-specific rules the survey shows the codebase needs (e.g. "no `unwrap()` outside tests and `main`", "context is the first parameter").
- Size thresholds: use codex's 500/800 unless the repo already has a convention or the language makes it wrong (Go files are typically smaller; Rust modules larger).
- The *Reserved vocabulary* entry is where the project's terms of art go. If the survey found a glossary, link it and delete the list.
- Do not add a "Principles" or "Philosophy" section. Every line should be checkable against a diff.
