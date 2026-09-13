# Output column schema

## Ledger columns (fixed order)

| Column | Meaning |
|---|---|
| 记录编号 | Sequential ledger ID, `TXN-0001`, `TXN-0002`, ... |
| 交易日期 | Transaction date (`YYYY-MM-DD`), kept separate from time so the user can filter/group by date. |
| 交易时间 | Transaction time when the source provides it; `00:00:00` when the source only gives a date. |
| 原始金额 | Amount as it appears on the matched source record before any currency conversion. |
| 原始币种 | Currency of 原始金额. |
| 记账类型 | 支出 / 收入 / 转账. |
| 分类 | Spend category (e.g. 餐饮美食, 日用百货, 网购, 网上支付, 公益捐赠, Other-Miscellaneous). |
| 交易对方 | Counterparty; for transfers, name plus last 4 of their account when known. |
| 商品/说明 | Merchant/description text from the source record. |
| 账户 | The bank/card/facade-balance account this row is recorded against. |
| 入账日期 | Post/settlement date, when it differs from the transaction date. |
| 需核对 | 是/否 — whether this row needs the user's attention. |
| 匹配状态 | See the vocabulary in `matching-rules.md`. |
| 资金方向 | 流入 / 流出. |
| 入账金额 | Amount actually settled to 账户, after FX conversion if needed. |
| 入账币种 | Currency of 入账金额. |
| 来源 | Path to the source file (raw/processed/facade) this row was derived from. |
| 关联记录 | Per-source reference ID tracing this row back to its raw source row, for audit. |
| 备注 | Free-text notes — e.g. which rule caused a status, why something is flagged. |

The first 9 columns (交易日期, 交易时间, 原始金额, 原始币种, 记账类型, 分类, 交易对方, 商品/说明, 账户)
are the ones read most often and must stay in this exact order; the remaining columns may
follow in any order.

Keep this exact column order across a project; if the user asks to add/reorder columns, treat
it as a deliberate schema change to apply consistently, not a one-off edit.

## Overview summary

Alongside the row-level ledger, include a short overview (a separate sheet in the XLSX, or a
clearly separated section):

- **消费口径**（by original currency): 支出 / 退款 / 收入 / 净消费, with transfers excluded from
  spend totals — a transfer moves money between the user's own accounts, it isn't spend.
- **账户入账口径**（by account and currency): 支出入账 / 退款入账 / 转账流入 / 转账流出.
- **对账提示**: a short numbered list of the special-case rules actually in effect for this run
  (e.g. which facades are on the default allowlist, how repayments are treated) so the summary
  is self-explanatory without opening this skill's references.

## 待核对 view

Also produce a filtered view/sheet containing every row where 需核对=是, so the user can review
open items without scanning the full ledger.

## XLSX formatting defaults

On every row-level sheet (台账, 待核对 — not the 概览 summary sheet, which isn't a flat table):
- Bold header row, frozen (`freeze_panes = 'A2'`) so it stays visible while scrolling.
- Auto-filter enabled on the header row.
- Alternating white/light-gray row banding (e.g. `FFFFFF` / `F2F2F2`) instead of a single
  highlight color, even for the 待核对 sheet — rely on the sheet's filter/name to signal
  "needs review", not a distinct fill.
