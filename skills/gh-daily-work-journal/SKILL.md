---
name: gh-daily-work-journal
description: Generate a Chinese work diary from a GitHub user's complete recent activity by using the local GitHub CLI (`gh`) and reading relevant diffs, final source context, tests, and documentation. Cover authored and committed code plus issues, pull requests, reviews, comments, replies, pushes, and other events across personal repositories, organizations, and external open-source projects. Organize the result into compact, medium-detail memory cues that distinguish accomplishments, difficulties, learning, and why the work mattered, with every mentioned GitHub object linked through natural descriptive text. Use when the user asks to summarize today's or specified days' GitHub work, create diary text, recall code changes and decisions, identify challenges, or extract learning and significance.
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

## Inspect implementation evidence

Inspect the actual implementation before writing every substantive PR, commit, review, or merge theme. Do not summarize a theme from PR descriptions, commit messages, or discussion alone.

1. Use the collector output to identify relevant repositories, PR numbers, commit SHAs, changed paths, and URLs.
2. For each relevant PR, fetch metadata and inspect its diff:

   ```text
   gh pr view <number> --repo <owner/repo> --json url,title,body,state,mergedAt,mergeCommit,files,commits,reviews,comments
   gh pr diff <number> --repo <owner/repo>
   ```

3. For a relevant commit not adequately represented by a PR, inspect its changed files and patches:

   ```text
   gh api repos/<owner>/<repo>/commits/<sha>
   ```

4. Read the final form of the highest-signal changed files at the PR head or merge commit, not only isolated diff hunks. Use an available checked-out repository, the GitHub connector, or raw file content from `gh`, for example:

   ```text
   gh api --method GET -H "Accept: application/vnd.github.raw+json" "repos/<owner>/<repo>/contents/<path>?ref=<sha>"
   ```

   Read enough surrounding code to understand the entry point, state or data flow, important failure path, and how the change fits the existing design. A diff can be misleading without unchanged context.
5. For large changes, prioritize high-signal implementation files, public contracts, state transitions, error paths, tests, and documentation. Skip generated output, dependency locks, and mechanical formatting unless they are themselves the work. Stop once the evidence supports a reliable explanation of the outcome, key mechanism, main difficulty, and significance; do not read every changed file by default.
6. Read changed tests alongside implementation code to identify which behavior and edge cases are actually covered. Do not say tests passed unless checks, logs, or other evidence prove they ran successfully.
7. Treat source and test behavior as stronger evidence of what changed than prose. Use PR bodies and discussions to explain intent, tradeoffs, review findings, and unresolved context, while distinguishing them from behavior confirmed in code.
8. When the user's activity is a review or merge of code authored by someone else, inspect the reviewed code and attribute the outcome accurately. Do not imply the user authored the implementation.
9. If permissions, truncation, deleted refs, or unavailable source prevent code inspection, state that limitation in the diary instead of filling the gap from discussion alone.

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
- Ground implementation summaries in the inspected code, tests, and documentation. Use discussion evidence for intent and tradeoffs rather than as a substitute for reading code.

## Write at a memory-cue level

- Optimize each theme to help the user later remember what they built, what made it difficult, what they learned, and why it mattered.
- Use a medium level of detail. Anchor the theme with the observable outcome and one or two memorable technical ideas, failure modes, or design choices, then explain their significance.
- In `做了什么`, translate code into product or architectural behavior: what capability changed, the key mechanism that made it work, and the resulting outcome. Do not enumerate files, functions, commits, or patches.
- In `遇到的问题和坑`, capture the main non-obvious bug, constraint, tradeoff, or review discovery and why it was difficult. Prefer one meaningful difficulty over a catalog of minor fixes.
- In `收获和启发`, state the durable technical or workflow lesson and connect it to why the work matters, such as reliability, user experience, maintainability, performance, safety, or future extensibility. Avoid generic lessons that could describe any task.
- Mention class, function, protocol, field, or error names only when they are useful retrieval cues or essential to the design decision. Omit line-by-line mechanics, exhaustive test cases, file lists, raw statistics, and incidental refactors.
- Combine closely related fixes and follow-up commits into one coherent outcome. Split themes only when the work had distinct goals or distinct lessons.
- Do not write “我检查了代码” merely because this skill inspected it. Code inspection is the evidence method, not an accomplishment, unless the user's actual work was code review.

## Link every external reference

- Make every mentioned GitHub PR a descriptive Markdown link, including repeated mentions on different dates: `[PR #123](https://github.com/owner/repository/pull/123)`.
- Apply the same rule to every mentioned Issue, commit, review, comment, repository, release, or other external GitHub object, for example `[Issue #45](verified-url)`, `[commit abc1234](verified-url)`, or `[owner/repository](verified-url)`.
- Attach the link to natural text. Never print a raw URL in the diary body and never leave a PR number or other external object as unlinked plain text.
- Use URLs returned by the collector, `gh`, or the GitHub API as the source of truth. Do not guess an object URL from an ambiguous name or number.
- Keep the prose readable by mentioning an object once per work-theme block when possible. If the same object must be mentioned again in another block or date, link it again.
- If a referenced external object has no verifiable URL, either omit the reference when it is nonessential or explicitly state that its link could not be verified without inventing one.

Example:

```markdown
2026.07.22

> 完善长会话锚点导航

- 做了什么：我完成了……，通过……机制解决了……，并由 [PR #123](https://github.com/owner/repository/pull/123) 将改动合入……
- 遇到的问题和坑：锚点预览曾出现……；Review 中还指出……
- 收获和启发：这次修改说明复杂导航不能只验证跳转主流程，还需要覆盖……；这样可以避免……，也为后续……保留空间。
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
