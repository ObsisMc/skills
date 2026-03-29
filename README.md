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

## Plugins

| Plugin | Description |
|--------|-------------|
| `speckit` | A collection of useful agent skills |

## Skills

| Skill | Plugin | Description |
|-------|--------|-------------|
| [bugfix-refine](skills/bugfix-refine/SKILL.md) | speckit | Fix bugs and refine code quality in a speckit-managed project |

## License

Apache-2.0
