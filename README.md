# ObsisMc Skills

A collection of [Agent Skills](https://agentskills.io) for Claude Code and other compatible AI tools.

## Install

### Claude Code

Add this marketplace:

```
/plugin marketplace add ObsisMc/skills
```

Then install the skills plugin:

```
/plugin install skills@obsismc-skills
```

Skills are then available as `/skills:<skill-name>` commands, or Claude will load them automatically when relevant.

### Other compatible tools

This repository follows the [Agent Skills open standard](https://agentskills.io/specification). Skills in the `skills/` directory can be used with any compatible agent tool.

## Available Skills

| Skill | Description |
|-------|-------------|
| [git-commit](skills/git-commit/SKILL.md) | Write structured commit messages following Conventional Commits |

## Create Your Own Skill

Copy the template and fill it in:

```bash
cp -r template/ skills/your-skill-name/
```

Edit `skills/your-skill-name/SKILL.md` — see [template/SKILL.md](template/SKILL.md) for the format and all available fields.

Each skill directory can also include:

```
skills/your-skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: scripts Claude can run
├── references/       # Optional: additional docs
└── assets/           # Optional: templates, data files
```

## Specification

Skills follow the [Agent Skills specification](https://agentskills.io/specification). Required `SKILL.md` frontmatter fields:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase letters, numbers, hyphens; max 64 chars |
| `description` | Yes | What the skill does and when to use it; max 1024 chars |
| `license` | No | License identifier |
| `compatibility` | No | Environment requirements |
| `allowed-tools` | No | Pre-approved tools |

## License

Apache-2.0
