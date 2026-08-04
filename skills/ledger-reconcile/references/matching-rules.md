# Cross-source matching rules

## Date alignment

- A domestic and a foreign-issued card can log the "same" purchase under different calendar
  dates purely from timezone offset. Don't reject a match on date alone without checking
  whether a timezone shift explains the gap.
- Foreign credit cards commonly report both a transaction date and a (later) post date. Match
  on transaction date/time first; treat post date only as a secondary sanity check, since a
  purchase can post several days after it happened.

## Currency alignment

- When a foreign-currency card transaction should match a domestic-currency facade record (or
  vice versa), amounts can't be compared directly. Use an approximate FX rate for that date to
  narrow down candidate matches, then — once a match is confirmed — compute and store the
  actual effective FX rate implied by the two recorded amounts, plus both the original and the
  settled amount/currency.

## Transfers

- A transfer (资金方向 = transfer, not a purchase) with no statement covering the other side of
  the transfer must be marked `匹配状态=待核对`, `需核对=是`. Never drop it just because the
  counterpart account's statement wasn't provided.
- When recording a transfer's counterparty, include the counterparty's name plus the last 4
  digits of their account when available — the name alone often isn't enough to distinguish
  people/accounts later.

## Credit-card repayments

- Inbound entries like "Payment" / "Payment Thank You" on a credit card statement are debt
  repayments, not income. Exclude them from income totals. If the funding account's statement
  is available, link the repayment as an internal transfer between the two accounts; if not,
  flag `需核对=是` rather than guessing the source.

## Still-pending transactions

- Foreign-card transactions from the last few days before the statement's cutoff date may not
  have posted yet. If a facade-side purchase near the cutoff has no bank-side match, note that
  it may still be pending rather than concluding it's simply missing.

## 匹配状态 vocabulary

Keep these values consistent within a single ledger run; extend only when an existing value
genuinely doesn't fit:

| Value | Meaning |
|---|---|
| 已匹配 | Both the bank/card side and the facade side were found and linked. |
| 仅银行记录 | Only the bank/card side was found; no facade counterpart, and it isn't covered by a default-facade allowlist entry. |
| `<facade>`默认摘要（仅银行摘要） | Matches a user-designated default facade (see workspace-layout.md); the bank-side abstract is sufficient, no further reconciliation needed. |
| 余额账户直接交易 | A facade balance/store-of-value transaction with no bank side expected. |
| 待核对 | Anything else uncertain — always pair with `需核对=是`. |

`需核对` (是/否) is a separate flag from `匹配状态`: it marks whether the row needs the user's
attention, independent of which status it was given.
