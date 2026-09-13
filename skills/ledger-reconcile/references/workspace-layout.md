# Workspace layout and file identification

## Folders

- `raw/` — original exported files exactly as downloaded (CSV/PDF/XLSX). Never edit these.
- `processed/` — one normalized file per raw file, same base name, extraction/cleanup only.
- `facade/` — payment-app exports (WeChat Pay, Alipay, PayPal, etc.) that combine many
  underlying payment methods into one bill.
- `outputs/combined_ledger_<date>/` — the final ledger for a given run, dated `YYYYMMDD`.

If any of these folders don't exist yet, create them as needed rather than asking the user to
set them up first — creating empty folders is free. Sorting the user's actual files into `raw/`
vs `facade/` is different: see "Sorting loose files into raw/ vs facade/" below before moving
anything.

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

## Sorting loose files into raw/ vs facade/

When the user's statement files haven't been sorted into `raw/` and `facade/` yet (see SKILL.md
step 0), use these as quick, non-authoritative signals — never as the final word for a file
that's actually ambiguous:
- Filename or content names a payment app (微信/WeChat, 支付宝/Alipay, PayPal, and similar) →
  likely `facade/`.
- Filename or content names a bank/card issuer, or ends in what looks like a card's last 4
  digits → likely `raw/`.
- A project may have already settled on its own naming convention (e.g. "no trailing 4-digit
  suffix = facade") documented in that project's own AGENTS.md/CLAUDE.md — prefer that
  convention when one exists, since it reflects a choice the user already made for this project.

Anything that doesn't clearly fall into one of these — an unfamiliar filename, a file with no
recognizable header, or a naming convention that hasn't been established yet — gets asked about
directly rather than sorted on a guess.

## Default-facade allowlist

Ask the user whether any facade should be treated as a "default" that doesn't need its own
matching record beyond the bank-side abstract (in the example ai-reconcile project, 美团 played
this role). Keep this list explicit and user-supplied per project — don't hardcode any specific
facade name into this skill, since it's specific to how each person actually spends.
