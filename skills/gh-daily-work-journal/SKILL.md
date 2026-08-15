---
name: gh-daily-work-journal
description: Generate a Chinese work diary from a GitHub user's complete recent activity by using the local GitHub CLI (`gh`) and reading relevant diffs, final source context, tests, project documentation, and cross-day delivery transitions. Cover authored and committed code plus issues, pull requests created earlier but merged today, reviews, comments, replies, pushes, and other events across personal repositories, organizations, and external open-source projects. Organize the result into compact, medium-detail memory cues that distinguish accomplishments, difficulties, project position and value, learning, and next steps, with every mentioned GitHub object linked through natural descriptive text. Use when the user asks to summarize today's or specified days' GitHub work, create diary text, recall code changes and decisions, identify challenges, track cross-day PR delivery, or explain each change's role and value in the project.
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
   - `commits`: global author and committer searches plus commits expanded from same-day Push events, deduplicated by repository and SHA. A commit with `matched_via: push` may have been authored or committed earlier; use its `pushes`, original timestamps, and `is_delayed_push` fields to distinguish publication from implementation.
   - `activities`: authenticated recent Issue, PR, Review, comment/reply, Push, branch, release, Wiki, star, fork, and other events.
   - `created_issues` and `created_pull_requests`: global search cross-checks for work created on the requested date.
   - `merged_pull_requests`: PRs authored earlier by the user and merged on the requested local date, including author, merger, merge time, and merge commit attribution.
5. Deduplicate overlapping evidence before writing. An opened PR can appear in `activities` and `created_pull_requests`, while its commits and merge can also appear separately. Treat them as one work theme. When a requested multi-day range includes both a commit's original date and its later push date, describe the implementation on the original date and mention the later push only if publishing, branch integration, or delivery was itself meaningful. Likewise, describe PR implementation and proposal on its creation/work date, then describe its later merge only as a delivery or project-state transition without repeating the implementation details.
6. Read attribution and timing carefully. A commit may be authored by a collaborator or coding agent but committed by the user. A merge or review remains user activity even when the user did not author the underlying commits. For `is_delayed_push: true`, write “今天推送/发布了此前完成的改动” rather than implying the implementation happened today. A push proves publication by the user, not authorship of every commit in the pushed range. For merged PRs, use `authored_by_user`, `merged_by_user`, and `merged_by_login`: say “我此前提交的 PR 今天被合入” when another person or automation merged it, and reserve “我合入了” for merges performed by the user.
7. Inspect `event_coverage` and `warnings`. GitHub exposes only a bounded recent user-event history. For dates outside that coverage, state that comments, replies, reviews, pushes, and other non-searchable activity may be incomplete. Never claim “no activity” when coverage is incomplete.
8. When all evidence arrays are empty and coverage is complete, produce a brief no-activity entry. Explain that GitHub still does not capture meetings, research, local uncommitted work, or work performed outside GitHub.

## Inspect implementation evidence

Inspect the actual implementation before writing every substantive PR, commit, review, or merge theme. Do not summarize a theme from PR descriptions, commit messages, or discussion alone.

1. Use the collector output to identify relevant repositories, PR numbers, commit SHAs, changed paths, and URLs.
2. For each relevant PR, fetch metadata and inspect its diff:

   ```text
   gh pr view <number> --repo <owner/repo> --json url,title,body,state,author,mergedAt,mergedBy,mergeCommit,files,commits,reviews,comments
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
9. If permissions, truncation, deleted refs, or unavailable source prevent code inspection, state that limitation in the diary instead of filling the gap from discussion alone. In particular, if `warnings` says a push range could only recover its head commit, do not claim the full delayed push was inspected.

## Understand project context and value

Before writing the first substantive theme for a repository, inspect enough project context to place the change in the system rather than treating the diff as an isolated task.

1. Read the repository description and README, plus the highest-signal linked Issue, milestone, roadmap, architecture document, or nearby module documentation when available. Prefer evidence directly connected to the changed area; do not read the entire repository.
2. Identify the project's stated purpose, the system layer affected by the work, the constraint or bottleneck it removes, and the capability it protects or unlocks. Distinguish an evidenced project goal from an inference based on code structure.
3. Build a concise causal chain for each theme: `change → capability → project effect → plausible next unlock`. Use this chain to write value, not generic claims such as “提高了可维护性”.
4. Classify the work internally by its main project role: foundation, end-to-end closure, guardrail, multiplier, delivery milestone, or technical-debt reduction. Express the role naturally in Chinese rather than printing the classification label mechanically.
5. Apply a counterfactual test: explain what risk, manual step, architectural gap, delivery block, or user limitation would remain without the change. Omit the counterfactual when evidence cannot support it.
6. Treat merge as a state transition. Moving into the default branch can establish a shared project baseline, but it does not prove deployment, release, adoption, or production impact. Claim those only with corresponding evidence.

## Write the diary text

Group related commits, issues, PRs, reviews, and comments into work themes. Prefer shared repository, issue/PR number, feature or fix intent, and conversation context as grouping signals. Collapse mechanical pushes, PR open/merge pairs, follow-up commits, formatting, and typo fixes into the related theme.

Write only Chinese text that the user can paste into a personal diary:

- Follow this format exactly:

  ```markdown
  YYYY.MM.DD

  > 总结做了什么的简短标题

  - 做了什么：……
  - 遇到的问题和坑：……
  - 项目中的位置与价值：……
  - 收获和下一步：……
  ```

- Do not add a document-level title, overview, summary table, activity index, `###` heading, bold label, or bullet category beyond the four required below.
- Write the date as four-digit year, two-digit month, and two-digit day separated by periods, such as `2026.07.22`.
- For multiple work themes on the same date, print the date once, then repeat the blockquote title and four bullets for each theme.
- For multiple dates, start each date group with its own `YYYY.MM.DD` line.
- Make each `> …` title a concise outcome summary. Do not use a repository name or generic phrase such as “开发工作” as the title when a more specific result is known.
- Under every title, always provide exactly these four bullets:
  - `- 做了什么：` Describe the outcome and important implementation, testing, Issue/PR, review, discussion, documentation, or cleanup work.
  - `- 遇到的问题和坑：` Describe concrete bugs, edge cases, tradeoffs, review feedback, investigation problems, or implementation friction supported by evidence. If absent, write `现有 GitHub 记录没有说明明确的问题或坑`.
  - `- 项目中的位置与价值：` Place the work in the project's architecture or delivery stage, then state the bottleneck, risk, or missing capability it removes and what it enables. Use the causal chain and counterfactual from project-context inspection. If project context is insufficient, state the narrow value proven by code and identify the missing context instead of guessing strategy or business impact.
  - `- 收获和下一步：` State a concrete technical or workflow lesson and the next unresolved step supported by evidence. Distinguish a documented next step from a reasonable inference. If no next step is visible, say so rather than inventing a roadmap.
- Use natural first-person language. A bullet may contain several connected sentences.
- Treat Issue filing and investigation, PR creation and merging, code review, review feedback, and substantive comments or replies as first-class work.
- When a PR authored on an earlier date is merged today, describe today's outcome as entering the shared branch or completing a delivery gate. Do not repeat the full implementation summary, and do not equate merge with release.
- Prefer outcomes over event counts. Avoid repeatedly listing hashes, push events, or repository names.
- Ground implementation summaries in the inspected code, tests, and documentation. Use discussion evidence for intent and tradeoffs rather than as a substitute for reading code.

## Write at a memory-cue level

- Optimize each theme to help the user later remember what they built, what made it difficult, where it sits in the project, why it mattered, and what remained next.
- Use a medium level of detail. Anchor the theme with the observable outcome and one or two memorable technical ideas, failure modes, or design choices, then explain their significance.
- In `做了什么`, translate code into product or architectural behavior: what capability changed, the key mechanism that made it work, and the resulting outcome. Do not enumerate files, functions, commits, or patches.
- In `遇到的问题和坑`, capture the main non-obvious bug, constraint, tradeoff, or review discovery and why it was difficult. Prefer one meaningful difficulty over a catalog of minor fixes.
- In `项目中的位置与价值`, move one abstraction level above the diff. Explain whether the work establishes a foundation, closes a workflow, adds a guardrail, multiplies future delivery speed, crosses a delivery milestone, or reduces debt, and connect that role to a concrete project effect.
- In `收获和下一步`, state the durable technical or workflow lesson, then identify the next verification, integration, release, monitoring, or design step when evidence supports one. Avoid generic lessons or speculative roadmaps.
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
- 项目中的位置与价值：这项工作位于……层，补上了……缺口；如果没有它，……仍会限制……，而现在可以进一步支持……。
- 收获和下一步：这次修改说明复杂导航不能只验证跳转主流程，还需要覆盖……；下一步需要通过……确认它已经形成完整闭环。
```

## Evidence rules

- Never invent business context, decisions, incidents, Issue requirements, difficulties, or learning.
- Express evidence levels naturally with wording such as “提交信息明确提到”, “从讨论来看”, “根据改动可能是”, or “现有记录无法判断”.
- Do not mistake opening and merging the same PR for two separate accomplishments.
- Do not imply that the user performed a merge when `merged_by_user` is false. Treat the merge of a user-authored PR as the realized outcome of earlier work, not newly authored implementation.
- Do not count routine pushes as separate work when commits or PRs explain the same change.
- Describe comments and reviews by their substance, not merely “回复了一条评论”.
- Avoid exposing secrets or reproducing patches, credentials, tokens, generated files, or sensitive source text. Paraphrase bodies and comments.

## Save and clean up

Return only the diary body. When the user asks to save it, or when invoked by an automation, write UTF-8 Markdown to the requested path. If no path is specified, use `work-journal/YYYY-MM-DD.md` under the active workspace. Do not overwrite an existing journal without reading and merging it first.

Delete temporary collector JSON after use because it may contain private-repository metadata and excerpts from comments or Issue bodies.

## Automation behavior

When invoked as a scheduled daily task, pass the automation's local UTC offset and requested date. Generate the journal even when no activity exists, so the sequence remains continuous. Surface authentication or incomplete-coverage failures rather than emitting a misleading empty journal.
