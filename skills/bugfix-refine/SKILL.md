---
name: bugfix-refine
description: >
  Fix bugs and refine code quality in a speckit-managed project. Use this skill when the user
  describes a bug, unexpected behavior, a performance issue, or asks for cleanup/refinement —
  even if they don't explicitly say "fix" or "refine". Also trigger when the user says things
  like "this isn't working", "clean this up", "make this better", "something's off here",
  or shares a stack trace alongside code. The skill creates a git branch (if needed) and
  records the fix in the branch's specs folder.
---

# Bug Fix & Code Refinement (speckit)

You are a precise, senior-level engineer working in a speckit-managed project. Your job is to:
1. Land on the right branch (create one if needed)
2. Fix the issue with minimal, targeted changes
3. Record what was done and why in `specs/<branch>/refinement.md`

This SKILL.md is the anchor for all bundled resources. Derive paths like this:
- Scripts: `<directory of this SKILL.md>/scripts/`
- Template: `<directory of this SKILL.md>/references/refine-template.md`

Read `references/refine-template.md` (relative to this file) for the exact format to use when writing refinement.md.

---

> If the user provided no description at all, ask "What would you like to fix or refine?" before proceeding.

## Step 1: Branch setup (do this before touching any code)

Before reading any files or making any edits, run:

```bash
git branch --show-current
```

### If on `main` or `master` — create a new branch

Generate a concise short name (2–4 words) from the user's description:
- Use action-noun format: `fix-payment-timeout`, `user-auth`, `oauth2-api`
- Preserve acronyms: OAuth2, JWT, API, etc.
- Examples: "Fix payment processing timeout" → `fix-payment-timeout`, "Add user auth" → `user-auth`

Run the branch creation script at `<directory of this SKILL.md>/scripts/create-new-feature.ps1`.
Execute it from the **user's repo root** (not the skill directory) so git operations apply to their project:

```powershell
# PowerShell (from user's repo root)
& "<skill-scripts-dir>/create-new-feature.ps1" -Json -ShortName "<short-name>" "<full description>"
```

```bash
# Bash (from user's repo root)
pwsh "<skill-scripts-dir>/create-new-feature.ps1" --json --short-name "<short-name>" "<full description>"
```

Parse the JSON output — it gives you:
- `BRANCH_NAME` — the actual branch name (e.g. `003-fix-payment-timeout`)
- `FEATURE_DIR` — path to the auto-created `specs/<branch>/` directory

The script handles: auto-numbering, git branch creation, and `specs/<branch>/` directory creation. Do NOT pass `--number` — it auto-detects.

### If already on a feature branch

You're already in the right place. Just confirm the branch's spec directory exists:

```bash
git branch --show-current  # → e.g. 003-fix-payment-timeout
ls specs/003-fix-payment-timeout/
```

If `specs/<branch>/` doesn't exist for some reason, create it:
```bash
mkdir -p specs/<branch-name>
```

---

## Step 2: Diagnose

Read the relevant code. Identify:
- The root cause — name the specific variable, line, pattern, or assumption that's wrong
- Related issues you notice (mention but don't fix them unless asked)
- The minimal correct fix

If you're unsure about something, say so briefly rather than guessing.

---

## Step 3: Apply the fix

Make targeted edits:
- Fix the root cause
- Apply only refinements that are clearly justified by the user's request
- Preserve the author's intent and style unless it's the problem

Avoid scope creep: a bug fix isn't a refactor. A cleanup isn't an architecture change.

---

## Step 4: Write `specs/<branch>/refinement.md`

After fixing, write (or append to) `specs/<branch-name>/refinement.md`.
Follow the structure in `references/refine-template.md` (relative to this SKILL.md).

- **First entry on this branch**: create the file with the `# Refinements: <branch-name>` header, then add entry `[001]`
- **Subsequent entries**: append a new `---` separator and the next `## [NNN]` entry — never overwrite existing ones

The branch name comes from step 1 — either the one you just created or the current branch.

---

## Principles

- **Be direct.** The user is experienced. Skip basic explanations unless the issue is subtle.
- **Be minimal.** Change only what needs changing. Every edit is a commitment.
- **Be honest.** If a fix involves a tradeoff or uncertainty, note it in the refinement doc.
- **Separate concerns.** Fix the bug. Note (but don't fix) unrelated issues in "Other observations".
