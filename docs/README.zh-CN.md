# ObsisMc Skills

面向 Claude Code 及其他兼容 AI 工具的 [Agent Skills](https://agentskills.io) 合集。

**[English](../README.md) | 简体中文**

## 安装

通过 [`skills`](https://www.npmjs.com/package/skills) 安装本仓库中的技能：

```bash
npx skills@latest add ObsisMc/skills
```

本仓库遵循 [Agent Skills 开放标准](https://agentskills.io/specification)，`skills/` 目录下的技能可用于任何兼容的 agent 工具。

在 Claude Code 中，所有技能都配置了 `disable-model-invocation: true`，因此只能通过显式的 `/skill-name` 命令运行，模型不会隐式调用它们。

## 插件

| 插件 | 说明 |
|------|------|
| `speckit` | 一组实用的 agent 技能集合 |

## 技能列表

| 技能 | 所属插件 | 调用方式 | 说明 |
|------|---------|---------|------|
| [bug-postmortem](../skills/bug-postmortem/SKILL.md) | - | 仅显式调用 | 为逃逸到生产环境的 bug 撰写代码级复盘：重点是为什么每道安全网都没拦住，以及新增什么防护让同类问题下次明确报错 |
| [bugfix-refine](../skills/bugfix-refine/SKILL.md) | speckit | 仅显式调用 | 在 speckit 管理的项目中修复 bug 并优化代码质量 |
| [gh-daily-work-journal](../skills/gh-daily-work-journal/SKILL.md) | - | 仅显式调用 | 汇总完整 GitHub 活动与跨日推送、合入进展，并结合代码和项目背景生成带来源链接、突出成果、难点、项目位置、价值与下一步的中文工作日记 |
| [ledger-reconcile](../skills/ledger-reconcile/SKILL.md) | - | 仅显式调用 | 将银行/信用卡账单与支付类 facade（微信支付、支付宝、PayPal 等）导出的流水对账合并成一份去重后的交易台账 |
| [uml-code-atlas](../skills/uml-code-atlas/SKILL.md) | - | 仅显式调用 | 为代码库、PR 或设计方案生成 Mermaid UML 架构图集（分层、数据模型、调用链、数据流、状态机、失效模式分析） |

## 致谢

- [bug-postmortem](../skills/bug-postmortem/SKILL.md) —— 方法论改编自 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) 的事故复盘实践（`docs/postmortem/`、`docs/AGENTS.md`、`docs/testing.md`），并参考了[菜鸟教程的中文讲解](https://www.runoob.com/deepseek-harness/deeseek-harness-postmortem.html)。本技能为独立重写：已剥离该项目特有的技术栈与语言假设，内容自足。

## 维护本仓库

新增、修改或删除某个技能时，必须在同一次改动中同步更新上方的"技能列表"表格（英文版 [README.md](../README.md) 与本文件均需更新）。具体规则见 [AGENTS.md](../AGENTS.md)。

## 许可证

Apache-2.0
