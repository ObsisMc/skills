# ObsisMc Skills

面向 Claude Code 及其他兼容 AI 工具的 [Agent Skills](https://agentskills.io) 合集。

**[English](../README.md) | 简体中文**

## 安装

通过 [`skills`](https://www.npmjs.com/package/skills) 安装本仓库中的技能：

```bash
npx skills@latest add ObsisMc/skills
```

本仓库遵循 [Agent Skills 开放标准](https://agentskills.io/specification)，`skills/` 目录下的技能可用于任何兼容的 agent 工具。

## 插件

| 插件 | 说明 |
|------|------|
| `speckit` | 一组实用的 agent 技能集合 |

## 技能列表

| 技能 | 所属插件 | 说明 |
|------|---------|------|
| [bugfix-refine](../skills/bugfix-refine/SKILL.md) | speckit | 在 speckit 管理的项目中修复 bug 并优化代码质量 |
| [gh-daily-work-journal](../skills/gh-daily-work-journal/SKILL.md) | - | 通过 `gh` CLI 汇总 GitHub 用户的近期完整活动，生成中文工作日报 |
| [ledger-reconcile](../skills/ledger-reconcile/SKILL.md) | - | 将银行/信用卡账单与支付类 facade（微信支付、支付宝、PayPal 等）导出的流水对账合并成一份去重后的交易台账 |
| [uml-code-atlas](../skills/uml-code-atlas/SKILL.md) | - | 为代码库、PR 或设计方案生成 Mermaid UML 架构图集（分层、数据模型、调用链、数据流、状态机、失效模式分析） |

## 维护本仓库

新增、修改或删除某个技能时，必须在同一次改动中同步更新上方的"技能列表"表格（英文版 [README.md](../README.md) 与本文件均需更新）。具体规则见 [AGENTS.md](../AGENTS.md)。

## 许可证

Apache-2.0
