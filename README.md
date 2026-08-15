# ObsisMc Skills

A collection of [Agent Skills](https://agentskills.io) for Claude Code and other compatible AI tools.

**English | [简体中文](docs/README.zh-CN.md)**

## Install

Install skills from this repo with [`skills`](https://www.npmjs.com/package/skills):

```bash
npx skills@latest add ObsisMc/skills
```

This repository follows the [Agent Skills open standard](https://agentskills.io/specification). Skills in the `skills/` directory can be used with any compatible agent tool.

## Plugins

| Plugin | Description |
|--------|-------------|
| `speckit` | A collection of useful agent skills |

## Skills

| Skill | Plugin | Description |
|-------|--------|-------------|
| [bugfix-refine](skills/bugfix-refine/SKILL.md) | speckit | Fix bugs and refine code quality in a speckit-managed project |
| [gh-daily-work-journal](skills/gh-daily-work-journal/SKILL.md) | - | Generate a linked Chinese work diary from complete GitHub activity, cross-day push and merge delivery, and inspected code and project context, highlighting outcomes, difficulties, project position, value, and next steps |
| [ledger-reconcile](skills/ledger-reconcile/SKILL.md) | - | Reconcile bank/card statements with payment-facade exports (WeChat Pay, Alipay, PayPal, etc.) into a single deduplicated transaction ledger |
| [uml-code-atlas](skills/uml-code-atlas/SKILL.md) | - | Produce a Mermaid UML architecture atlas (layering, data model, call chains, data flow, state machines, failure-mode analysis) for a codebase, PR, or design proposal |

## Maintaining this repo

When adding, modifying, or removing a skill, the corresponding entry in the Skills table above **and** in the [Chinese README](docs/README.zh-CN.md) must be added, updated, or removed in the same change. See [AGENTS.md](AGENTS.md) for the enforced rule.

## License

Apache-2.0
