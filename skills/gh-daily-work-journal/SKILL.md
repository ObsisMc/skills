---
name: gh-daily-work-journal
description: Generate a Chinese work diary from a GitHub user's complete recent activity by using the local GitHub CLI (`gh`), covering authored and committed code plus issues, pull requests, reviews, comments, replies, pushes, and other events across personal repositories, organizations, and external open-source projects. Organize the result into compact work-topic sections that distinguish accomplishments, difficulties, and learning. Use when the user asks to summarize today's or specified days' GitHub work, create diary text, explain changes and decisions, identify challenges, or extract learning.
---

# GitHub Daily Work Journal

Create a compact, readable work diary from GitHub activity evidence. Preserve the distinction between facts, reasonable inference, and missing context.

## Collect evidence

1. Determine the journal date. Use the user's local date when none is supplied.
2. Require both `gh` and an authenticated session:

   ```text
   gh --version
   gh auth status
   ```

   If either check fails, stop and give the exact recovery command `gh auth login`. Do not silently fall back to unauthenticated public-only data.
3. Run the bundled collector for each date:

   ```text
   python <skill-dir>/scripts/collect_github_activity.py --date YYYY-MM-DD --utc-offset +08:00 --output <temporary-json>
   ```

   Pass the user's local UTC offset. Add `--user LOGIN` only when the user explicitly requests another account. Do not apply repository or owner filters unless the user requests a limited scope: the default must cover personal repositories, organizations, forks, and external open-source repositories.
4. Use every evidence array:
   - `commits`: global author and committer searches, deduplicated by repository and SHA.
   - `activities`: authenticated recent Issue, PR, Review, comment/reply, Push, branch, release, Wiki, star, fork, and other events.
   - `created_issues` and `created_pull_requests`: global search cross-checks for work created on the requested date.
5. Deduplicate overlapping evidence before writing. An opened PR can appear in `activities` and `created_pull_requests`, while its commits and merge can also appear separately. Treat them as one work theme.
6. Read attribution carefully. A commit may be authored by a collaborator or coding agent but committed by the user. A merge or review remains user activity even when the user did not author the underlying commits.
7. Inspect `event_coverage` and `warnings`. GitHub exposes only a bounded recent user-event history. For dates outside that coverage, state that comments, replies, reviews, pushes, and other non-searchable activity may be incomplete. Never claim “no activity” when coverage is incomplete.
8. When all evidence arrays are empty and coverage is complete, produce a brief no-activity entry. Explain that GitHub still does not capture meetings, research, local uncommitted work, or work performed outside GitHub.

## Write the diary text

Group related commits, issues, PRs, reviews, and comments into work themes. Prefer shared repository, issue/PR number, feature or fix intent, and conversation context as grouping signals. Collapse mechanical pushes, PR open/merge pairs, follow-up commits, formatting, and typo fixes into the related theme.

Write only Chinese text that the user can paste into a personal diary:

- Follow this format exactly:

  ```markdown
  YYYY.MM.DD

  > 总结做了什么的简短标题

  - 做了什么：……
  - 遇到的问题和坑：……
  - 收获和启发：……
  ```

- Do not add a document-level title, overview, summary table, activity index, `###` heading, bold label, or additional bullet category.
- Write the date as four-digit year, two-digit month, and two-digit day separated by periods, such as `2026.07.22`.
- For multiple work themes on the same date, print the date once, then repeat the blockquote title and three bullets for each theme.
- For multiple dates, start each date group with its own `YYYY.MM.DD` line.
- Make each `> …` title a concise outcome summary. Do not use a repository name or generic phrase such as “开发工作” as the title when a more specific result is known.
- Under every title, always provide exactly these three bullets:
  - `- 做了什么：` Describe the outcome and important implementation, testing, Issue/PR, review, discussion, documentation, or cleanup work.
  - `- 遇到的问题和坑：` Describe concrete bugs, edge cases, tradeoffs, review feedback, investigation problems, or implementation friction supported by evidence. If absent, write `现有 GitHub 记录没有说明明确的问题或坑`.
  - `- 收获和启发：` State a concrete technical or workflow lesson grounded in the evidence. If evidence is weak, say what context is missing instead of inventing a generic lesson.
- Use natural first-person language. A bullet may contain several connected sentences.
- Treat Issue filing and investigation, PR creation and merging, code review, review feedback, and substantive comments or replies as first-class work.
- Prefer outcomes over event counts. Avoid repeatedly listing hashes, push events, or repository names.
- Include commit, Issue, PR, review, or comment links sparingly when they help future reconstruction.

Example:

```markdown
2026.07.22

> 完善长会话锚点导航

- 做了什么：我完成了……，并通过 PR 将改动合入……
- 遇到的问题和坑：锚点预览曾出现……；Review 中还指出……
- 收获和启发：这次修改说明复杂导航不能只验证跳转主流程，还需要覆盖……
```

## Evidence rules

- Never invent business context, decisions, incidents, Issue requirements, difficulties, or learning.
- Express evidence levels naturally with wording such as “提交信息明确提到”, “从讨论来看”, “根据改动可能是”, or “现有记录无法判断”.
- Do not mistake opening and merging the same PR for two separate accomplishments.
- Do not count routine pushes as separate work when commits or PRs explain the same change.
- Describe comments and reviews by their substance, not merely “回复了一条评论”.
- Avoid exposing secrets or reproducing patches, credentials, tokens, generated files, or sensitive source text. Paraphrase bodies and comments.

## Save and clean up

Return only the diary body. When the user asks to save it, or when invoked by an automation, write UTF-8 Markdown to the requested path. If no path is specified, use `work-journal/YYYY-MM-DD.md` under the active workspace. Do not overwrite an existing journal without reading and merging it first.

Delete temporary collector JSON after use because it may contain private-repository metadata and excerpts from comments or Issue bodies.

## Automation behavior

When invoked as a scheduled daily task, pass the automation's local UTC offset and requested date. Generate the journal even when no activity exists, so the sequence remains continuous. Surface authentication or incomplete-coverage failures rather than emitting a misleading empty journal.
