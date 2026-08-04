# Workspace layout and file identification

## Folders

- `raw/` — original exported files exactly as downloaded (CSV/PDF/XLSX). Never edit these.
- `processed/` — one normalized file per raw file, same base name, extraction/cleanup only.
- `facade/` — payment-app exports (WeChat Pay, Alipay, PayPal, etc.) that combine many
  underlying payment methods into one bill.
- `outputs/combined_ledger_<date>/` — the final ledger for a given run, dated `YYYYMMDD`.

If any of these folders don't exist yet, create them as needed rather than asking the user to
set them up first.

## File naming

Prefer `<institution>_<identifier>[_<date range>].<ext>`, where `<identifier>` is the account
name or the card's last 4 digits (e.g. `Chase2919_Activity_20260802.csv`, `amex_71008.xlsx`).
Last-4-digit identifiers matter because many people hold several cards from the same issuer —
without it, statements can't be told apart. If the user hands over files that don't follow this
convention, don't rename their originals; just track institution/account/last-4 as metadata
you carry through `processed/` and into the ledger's 账户 column.

## Identifying a file when the name doesn't say enough

Check, in order:
1. The statement header or first few rows — issuer name, account/card number, statement period
   are usually printed there.
2. Currency symbols/codes and date format (MM/DD/YYYY vs DD/MM/YYYY vs YYYY-MM-DD) as a hint
   toward country/timezone.
3. Column names and language — a domestic bank export and a US card export rarely share a
   schema.

If institution, account, currency, or timezone still isn't clear after checking the file
itself, ask the user. Don't infer a timezone from country stereotypes alone — ask if unsure,
since this feeds directly into date-matching in `matching-rules.md`.

## Facade vs. bank/card account

A **facade** is an app whose bill is an outer wrapper around one or more underlying payment
methods (a linked bank card, or the facade's own balance). Its bill needs to be matched against
the underlying bank/card statement for anything not paid from its own balance.

A facade's own store-of-value sub-account (WeChat's 零钱, Alipay's 余额, PayPal's balance, and
equivalents) behaves like an independent account: transactions from it will never appear on any
bank/card statement, so don't try to match them — record them directly under that pseudo-account
name (e.g. `微信零钱`) instead.

## Default-facade allowlist

Ask the user whether any facade should be treated as a "default" that doesn't need its own
matching record beyond the bank-side abstract (in the example ai-reconcile project, 美团 played
this role). Keep this list explicit and user-supplied per project — don't hardcode any specific
facade name into this skill, since it's specific to how each person actually spends.
