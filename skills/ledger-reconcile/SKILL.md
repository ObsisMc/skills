---
name: ledger-reconcile
disable-model-invocation: true
description: >
  Reconcile personal bank/card statements with payment-facade exports (WeChat Pay, Alipay,
  PayPal, Meituan, etc.) into a single deduplicated transaction ledger. Use when the user
  provides raw statement files (CSV, PDF, XLSX) and asks to 对账, 记账, 整理账单, reconcile
  transactions, merge bank and Alipay/WeChat records, or build a combined ledger — especially
  when the same purchase can appear on both a facade export and the underlying bank/card
  statement, or when accounts span multiple currencies, countries, or timezones.
---

# Ledger Reconciliation

Turn a pile of raw bank/card statements and payment-app exports into one trustworthy ledger,
without silently duplicating or dropping transactions.

This SKILL.md is the anchor for all bundled resources. Derive paths like this:
- Workspace/file-naming conventions: `<directory of this SKILL.md>/references/workspace-layout.md`
- Cross-source matching rules: `<directory of this SKILL.md>/references/matching-rules.md`
- Output column schema: `<directory of this SKILL.md>/references/column-schema.md`

## The core problem

- A "facade" app (WeChat Pay, Alipay, PayPal, and similar) settles purchases through
  whichever underlying card or its own store-of-value balance (微信零钱, 支付宝余额, PayPal
  balance) was selected at checkout. The same purchase can therefore show up once on the
  facade's own bill and once on the underlying bank/card statement — naively combining both
  sources double-counts it.
- People who hold cards issued in different countries often pay through the same domestic
  facade with a foreign card. Matching those records is hard: currencies differ (so amount
  can't be compared directly), foreign statements use a different timezone, and foreign
  credit cards distinguish a transaction date from a (later) post date.

## Ask, don't guess

This is a financial record — a wrong silent guess is worse than a question. Always surface
these to the user instead of picking an answer yourself:
- A file's institution/account/currency/timezone can't be determined from its name or content.
- More than one candidate transaction could match within date/amount tolerance.
- A transfer has no corresponding statement for the other side of the transfer.
- Any other genuine ambiguity encountered while classifying or matching a transaction.

## Workspace layout

Work inside (or create) this layout in the user's reconciliation project — never inside this
skill's own directory:

```
raw/                              # original exports, one file per account/statement, untouched
processed/                        # normalized, machine-readable version of each raw file
facade/                           # payment-app exports (WeChat, Alipay, PayPal, ...)
outputs/combined_ledger_<date>/   # final ledger (CSV + XLSX)
```

Read `references/workspace-layout.md` for the file-naming convention and how to identify a
file's source institution/account/currency/timezone when the filename alone doesn't say.

## Steps

1. **Inventory.** List everything in `raw/` and `facade/`. For each file, identify institution,
   account (and last 4 digits if it's a card), currency, and timezone/country. Ask the user
   about anything unclear rather than assuming.
2. **Normalize into `processed/`.** PDF statements need table extraction into a readable
   format (CSV/text); already-tabular files (CSV/XLSX) pass through with only encoding/header
   cleanup. Never reinterpret amounts, dates, or categories during this step — that happens
   later, deliberately, during matching.
3. **Split out facade balance accounts.** Transactions settled from a facade's own
   store-of-value balance (微信零钱, 支付宝余额, PayPal balance, ...) are their own account —
   they will never have a matching bank/card statement, so don't hold them to that expectation.
4. **Match remaining facade transactions against bank/card transactions.** Use date + amount,
   with FX-rate approximation and timezone/transaction-vs-post-date tolerance when currencies
   differ. Read `references/matching-rules.md` for the specific heuristics, the 匹配状态
   vocabulary, and special-case rules (transfers, credit-card repayments, still-pending
   foreign transactions, user-designated default facades that don't need reconciling).
5. **Assign IDs.** Sequential ledger record IDs (`TXN-0001`, `TXN-0002`, ...) plus a per-source
   reference ID that traces each row back to its raw file and row, so any entry can be audited.
6. **Produce the ledger.** Write `outputs/combined_ledger_<date>/` using the fixed column order
   in `references/column-schema.md`, an overview summary (totals by currency and by account,
   transfers excluded from spend totals), and a "待核对" view listing every row with 需核对=是.
7. **Report open questions.** Before treating the ledger as final, tell the user what was
   ambiguous, what's still pending, and what rules were applied (e.g. which facades were
   treated as default/no-reconciliation-needed) — don't bury this only inside the file.

## Revising

Later refinement requests (reorder a column, adjust a rule, fix one match) should update the
ledger in place. Only keep multiple dated/suffixed copies in `outputs/` if the user explicitly
wants to compare revisions side by side — don't accumulate versioned files by default.
