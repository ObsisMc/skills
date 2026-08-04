# AGENTS.md

Instructions for any AI agent (Claude, or otherwise) working in this repository.

## Rule: keep README.md AND docs/README.zh-CN.md in sync with `skills/`

This repo maintains **two** README files that both contain a **Skills** table listing every skill in `skills/`, with a link to its `SKILL.md` and a one-line description:

- [README.md](README.md) — English, repo root
- [docs/README.zh-CN.md](docs/README.zh-CN.md) — Chinese (简体中文) translation

These two files must always be kept in sync with each other and with the contents of `skills/`. Whenever a change touches the `skills/` directory, the same change must update **both** README files accordingly, in the same commit/PR:

- **New skill added** (a new `skills/<name>/SKILL.md`): add a row to the Skills table in both READMEs — skill name linked to its `SKILL.md`, its plugin (if any), and a one-line description taken from (or summarizing) the `description` field in the skill's frontmatter, translated into Chinese for `docs/README.zh-CN.md`.
- **Existing skill modified** in a way that changes its purpose, scope, or description (e.g. the `description` frontmatter field changes, or the skill is renamed or moved): update the corresponding row's link and/or description in both files to match.
- **Skill removed** (a `skills/<name>/` directory deleted): remove its row from the Skills table in both files.
- **Plugin association changes** (a skill is added to or removed from a plugin grouping): update the Plugin column for that row, and the Plugins table if a plugin is added/removed entirely — in both files.

Do not treat this as optional cleanup — it is a required part of any skill-affecting change, not a separate follow-up task. Never update only one of the two README files.

## Verification before finishing

Before considering a skill-related change complete, confirm:

1. Every directory under `skills/` containing a `SKILL.md` has exactly one corresponding row in the Skills table of **both** README.md and docs/README.zh-CN.md.
2. Every row in both Skills tables points to a `SKILL.md` that still exists.
3. The description in each row (in both languages) is still an accurate, current summary of the skill (not stale wording left over from a previous version).
4. The two README files list the same set of skills, in the same relative order, with matching Plugin columns — only the description language differs.

## Scope

This rule applies regardless of how the change is made — directly editing files, generating a new skill from scratch, or refactoring/deleting one. It applies to both human-directed and autonomous edits.
