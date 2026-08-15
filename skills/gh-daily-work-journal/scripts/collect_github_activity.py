#!/usr/bin/env python3
"""Collect commits and user activity for a GitHub work journal via GitHub CLI."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def fail(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def run_gh(args: list[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if process.returncode and not allow_failure:
        detail = process.stderr.strip() or process.stdout.strip() or f"exit code {process.returncode}"
        fail(f"`gh {' '.join(args)}` failed: {detail}")
    return process


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect commits, issues, PRs, reviews, comments, and other GitHub activity for one day."
    )
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Journal date (YYYY-MM-DD)")
    parser.add_argument("--user", help="GitHub login; defaults to the authenticated gh user")
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        metavar="OWNER/REPO",
        help="Limit search to a repository; repeat for multiple repositories",
    )
    parser.add_argument(
        "--owner",
        action="append",
        default=[],
        metavar="OWNER",
        help="Limit search to a repository owner or organization; repeat for multiple owners",
    )
    parser.add_argument(
        "--utc-offset",
        help="Local UTC offset used to assign event dates, such as +08:00; defaults to system local time",
    )
    parser.add_argument("--limit", type=int, default=200, help="Maximum commits to collect (default: 200)")
    parser.add_argument("--output", type=Path, help="Write UTF-8 JSON to this path instead of stdout")
    return parser.parse_args()


def validate_date(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError:
        fail(f"invalid --date {value!r}; expected YYYY-MM-DD")
    raise AssertionError("unreachable")


def parse_timezone(value: str | None) -> dt.tzinfo:
    if value is None:
        return dt.datetime.now().astimezone().tzinfo or dt.timezone.utc
    match = re.fullmatch(r"([+-])(\d{2}):(\d{2})", value)
    if not match:
        fail(f"invalid --utc-offset {value!r}; expected +HH:MM or -HH:MM")
    hours, minutes = int(match.group(2)), int(match.group(3))
    if hours > 23 or minutes > 59:
        fail(f"invalid --utc-offset {value!r}")
    delta = dt.timedelta(hours=hours, minutes=minutes)
    if match.group(1) == "-":
        delta = -delta
    return dt.timezone(delta)


def normalize_repository(value: Any) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return ""
    return str(
        value.get("nameWithOwner")
        or value.get("fullName")
        or value.get("name_with_owner")
        or value.get("name")
        or ""
    )


def commit_message(item: dict[str, Any]) -> str:
    commit = item.get("commit")
    if isinstance(commit, dict):
        return str(commit.get("message") or "")
    return str(item.get("message") or "")


def commit_timestamp(item: dict[str, Any], role: str) -> str:
    commit = item.get("commit")
    if not isinstance(commit, dict):
        return ""
    identity = commit.get(role)
    if isinstance(identity, dict) and identity.get("date"):
        return str(identity["date"])
    return ""


def account_login(item: dict[str, Any], role: str) -> str:
    identity = item.get(role)
    if isinstance(identity, dict) and identity.get("login"):
        return str(identity["login"])
    return ""


def excerpt(value: Any, limit: int = 1200) -> str:
    if not isinstance(value, str):
        return ""
    cleaned = value.strip()
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1].rstrip() + "…"


def search_commits(
    user: str,
    journal_date: str,
    repositories: list[str],
    owners: list[str],
    limit: int,
    role: str,
) -> list[dict[str, Any]]:
    date_flag = "--author-date" if role == "author" else "--committer-date"
    search_args = [
        "search",
        "commits",
        f"--{role}",
        user,
        date_flag,
        journal_date,
        "--limit",
        str(limit),
        "--sort",
        f"{role}-date",
        "--order",
        "asc",
        "--json",
        "author,commit,committer,parents,repository,sha,url",
    ]
    for repo in repositories:
        search_args.extend(["--repo", repo])
    for owner in owners:
        search_args.extend(["--owner", owner])
    search = run_gh(search_args)
    try:
        items = json.loads(search.stdout or "[]")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON from `gh search commits` ({role}): {exc}")
    if not isinstance(items, list):
        fail(f"unexpected response from `gh search commits` ({role})")
    return [item for item in items if isinstance(item, dict)]


def parse_json_list(process: subprocess.CompletedProcess[str], source: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(process.stdout or "[]")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON from {source}: {exc}")
    if not isinstance(payload, list):
        fail(f"unexpected response from {source}")
    if payload and all(isinstance(page, list) for page in payload):
        payload = [item for page in payload for item in page]
    return [item for item in payload if isinstance(item, dict)]


def repository_allowed(repository: str, repositories: list[str], owners: list[str]) -> bool:
    if repositories and repository not in repositories:
        return False
    if owners and repository.split("/", 1)[0] not in owners:
        return False
    return True


def event_local_date(timestamp: str, timezone: dt.tzinfo) -> str:
    try:
        parsed = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return ""
    return parsed.astimezone(timezone).date().isoformat()


def collect_events(
    user: str,
    journal_date: str,
    timezone: dt.tzinfo,
    repositories: list[str],
    owners: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    process = run_gh(
        [
            "api",
            "--method",
            "GET",
            "--paginate",
            "--slurp",
            f"users/{user}/events",
            "-f",
            "per_page=100",
        ]
    )
    raw_events = parse_json_list(process, "GitHub user events API")
    target_cache: dict[tuple[str, int], dict[str, Any]] = {}
    activities: list[dict[str, Any]] = []

    for event in raw_events:
        timestamp = str(event.get("created_at") or "")
        if event_local_date(timestamp, timezone) != journal_date:
            continue
        repository = normalize_repository(event.get("repo"))
        if not repository_allowed(repository, repositories, owners):
            continue
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        issue = payload.get("issue") if isinstance(payload.get("issue"), dict) else {}
        pull_request = (
            payload.get("pull_request") if isinstance(payload.get("pull_request"), dict) else {}
        )
        discussion = (
            payload.get("discussion") if isinstance(payload.get("discussion"), dict) else {}
        )
        comment = payload.get("comment") if isinstance(payload.get("comment"), dict) else {}
        review = payload.get("review") if isinstance(payload.get("review"), dict) else {}
        release = payload.get("release") if isinstance(payload.get("release"), dict) else {}
        target = pull_request or issue or discussion
        number_value = target.get("number") or payload.get("number")
        number = int(number_value) if isinstance(number_value, int) else None

        if number and repository and not target.get("title"):
            key = (repository, number)
            if key not in target_cache:
                detail = run_gh(["api", f"repos/{repository}/issues/{number}"], allow_failure=True)
                if detail.returncode == 0:
                    try:
                        parsed_detail = json.loads(detail.stdout)
                    except json.JSONDecodeError:
                        parsed_detail = {}
                    target_cache[key] = parsed_detail if isinstance(parsed_detail, dict) else {}
                else:
                    target_cache[key] = {}
            if target_cache[key]:
                target = target_cache[key]

        event_type = str(event.get("type") or "")
        is_pr = bool(
            event_type.startswith("PullRequest")
            or pull_request
            or issue.get("pull_request")
            or target.get("pull_request")
        )
        action = payload.get("action") or {
            "PushEvent": "pushed",
            "CreateEvent": "created",
            "DeleteEvent": "deleted",
            "ForkEvent": "forked",
            "WatchEvent": "starred",
            "GollumEvent": "edited_wiki",
        }.get(event_type, "performed")
        url = (
            comment.get("html_url")
            or review.get("html_url")
            or target.get("html_url")
            or release.get("html_url")
        )
        body = (
            comment.get("body")
            or review.get("body")
            or target.get("body")
            or release.get("body")
        )
        push_commits = payload.get("commits") if isinstance(payload.get("commits"), list) else []
        activities.append(
            {
                "event_id": str(event.get("id") or ""),
                "type": event_type,
                "action": action,
                "created_at": timestamp,
                "local_date": journal_date,
                "repository": repository,
                "target_kind": (
                    "pull_request"
                    if is_pr
                    else ("issue" if issue else ("discussion" if discussion else ""))
                ),
                "number": number,
                "title": target.get("title") or release.get("name") or release.get("tag_name"),
                "url": url,
                "body_excerpt": excerpt(body),
                "review_state": review.get("state"),
                "ref": payload.get("ref"),
                "ref_type": payload.get("ref_type"),
                "push_before": payload.get("before"),
                "push_head": payload.get("head"),
                "push_size": payload.get("size"),
                "push_commits": [
                    {
                        "sha": str(item.get("sha") or ""),
                        "short_sha": str(item.get("sha") or "")[:8],
                        "message": str(item.get("message") or ""),
                    }
                    for item in push_commits
                    if isinstance(item, dict)
                ],
                "public": event.get("public"),
            }
        )

    oldest_timestamp = min(
        (str(event.get("created_at")) for event in raw_events if event.get("created_at")),
        default="",
    )
    oldest_local_date = event_local_date(oldest_timestamp, timezone) if oldest_timestamp else ""
    requested = dt.date.fromisoformat(journal_date)
    retention_start = dt.datetime.now(timezone).date() - dt.timedelta(days=90)
    complete = requested >= retention_start
    if len(raw_events) >= 300 and oldest_local_date and journal_date <= oldest_local_date:
        complete = False
    coverage = {
        "events_fetched": len(raw_events),
        "oldest_event_at": oldest_timestamp,
        "retention_start_estimate": retention_start.isoformat(),
        "complete_for_requested_date": complete,
        "note": (
            "Authenticated user event stream; GitHub exposes at most 300 recent events "
            "and generally retains events for about 90 days."
        ),
    }
    return sorted(activities, key=lambda item: item["created_at"]), coverage


def search_created_items(
    kind: str,
    user: str,
    journal_date: str,
    repositories: list[str],
    owners: list[str],
    limit: int,
) -> list[dict[str, Any]]:
    command = "issues" if kind == "issue" else "prs"
    args = [
        "search",
        command,
        "--author",
        user,
        "--created",
        journal_date,
        "--limit",
        str(limit),
        "--sort",
        "created",
        "--order",
        "asc",
        "--json",
        "author,body,commentsCount,createdAt,number,repository,state,title,updatedAt,url",
    ]
    for repo in repositories:
        args.extend(["--repo", repo])
    for owner in owners:
        args.extend(["--owner", owner])
    process = run_gh(args)
    items = parse_json_list(process, f"`gh search {command}`")
    return [
        {
            "kind": kind,
            "repository": normalize_repository(item.get("repository")),
            "number": item.get("number"),
            "title": item.get("title"),
            "body_excerpt": excerpt(item.get("body")),
            "url": item.get("url"),
            "state": item.get("state"),
            "comments_count": item.get("commentsCount"),
            "created_at": item.get("createdAt"),
            "updated_at": item.get("updatedAt"),
        }
        for item in items
    ]


def collect_detail(repository: str, sha: str) -> tuple[dict[str, Any], str | None]:
    if not repository or not sha:
        return {}, "missing repository or SHA in search result"
    process = run_gh(["api", f"repos/{repository}/commits/{sha}"], allow_failure=True)
    if process.returncode:
        detail = process.stderr.strip() or process.stdout.strip() or f"exit code {process.returncode}"
        return {}, detail
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError as exc:
        return {}, f"invalid JSON from commit API: {exc}"
    if not isinstance(payload, dict):
        return {}, "unexpected commit API response"
    return payload, None


def collect_pushed_commits(
    activities: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Expand same-day PushEvents into commits while preserving push evidence."""
    discovered: dict[tuple[str, str], dict[str, Any]] = {}
    warnings: list[str] = []
    zero_sha = "0" * 40

    for activity in activities:
        if activity.get("type") != "PushEvent":
            continue
        repository = str(activity.get("repository") or "")
        before = str(activity.get("push_before") or "")
        head = str(activity.get("push_head") or "")
        if not repository or not head or head == zero_sha:
            continue

        push = {
            "event_id": activity.get("event_id"),
            "pushed_at": activity.get("created_at"),
            "ref": activity.get("ref"),
            "before": before,
            "head": head,
        }
        pushed_items: list[dict[str, Any]] = []
        range_is_complete = False

        if before and before != zero_sha and before != head:
            comparison = run_gh(
                ["api", f"repos/{repository}/compare/{before}...{head}"],
                allow_failure=True,
            )
            if comparison.returncode == 0:
                try:
                    comparison_payload = json.loads(comparison.stdout or "{}")
                except json.JSONDecodeError as exc:
                    warnings.append(
                        f"{repository} push {head[:8]}: invalid compare JSON ({exc}); "
                        "falling back to the pushed head commit."
                    )
                    comparison_payload = {}
                if isinstance(comparison_payload, dict):
                    raw_commits = comparison_payload.get("commits")
                    if isinstance(raw_commits, list):
                        pushed_items = [item for item in raw_commits if isinstance(item, dict)]
                    total_commits = comparison_payload.get("total_commits")
                    if isinstance(total_commits, int) and total_commits > len(pushed_items):
                        warnings.append(
                            f"{repository} push {head[:8]}: GitHub compare returned "
                            f"{len(pushed_items)} of {total_commits} commits; pushed history is incomplete."
                        )
                    else:
                        range_is_complete = bool(pushed_items)
            else:
                detail = comparison.stderr.strip() or comparison.stdout.strip()
                warnings.append(
                    f"{repository} push {head[:8]}: could not expand {before[:8]}...{head[:8]}"
                    + (f" ({detail})" if detail else "")
                    + "; falling back to the pushed head commit."
                )

        if not pushed_items:
            head_detail, head_error = collect_detail(repository, head)
            if head_detail:
                pushed_items = [head_detail]
            elif head_error:
                warnings.append(
                    f"{repository} push {head[:8]}: could not inspect pushed head ({head_error})."
                )
            if before == zero_sha:
                warnings.append(
                    f"{repository} push {head[:8]} created a new ref; GitHub events did not expose "
                    "the full pushed commit list, so only the head commit could be recovered."
                )
            elif before == head:
                warnings.append(
                    f"{repository} push {head[:8]} did not expose an expandable commit range; "
                    "only the head commit could be recovered."
                )
            elif before and not range_is_complete and not head_error:
                if not any(
                    f"{repository} push {head[:8]}:" in warning for warning in warnings
                ):
                    warnings.append(
                        f"{repository} push {head[:8]} returned no compare commits; "
                        "only the head commit could be recovered."
                    )

        for item in pushed_items:
            sha = str(item.get("sha") or item.get("id") or "")
            if not sha:
                continue
            key = (repository, sha)
            if key not in discovered:
                copied = dict(item)
                copied["_repository"] = repository
                copied["_matched_via"] = ["push"]
                copied["_pushes"] = [push]
                discovered[key] = copied
            else:
                pushes = discovered[key].setdefault("_pushes", [])
                if push not in pushes:
                    pushes.append(push)

    return list(discovered.values()), warnings


def evidence_timestamp(item: dict[str, Any]) -> str:
    pushes = item.get("_pushes")
    if isinstance(pushes, list):
        pushed_at = [str(push.get("pushed_at") or "") for push in pushes if isinstance(push, dict)]
        if pushed_at:
            return max(pushed_at)
    return commit_timestamp(item, "committer") or commit_timestamp(item, "author") or ""


def main() -> None:
    args = parse_args()
    journal_date = validate_date(args.date)
    timezone = parse_timezone(args.utc_offset)
    if args.limit < 1 or args.limit > 1000:
        fail("--limit must be between 1 and 1000")
    if shutil.which("gh") is None:
        fail("GitHub CLI (`gh`) is required; install it, then run `gh auth login`")

    auth = run_gh(["auth", "status"], allow_failure=True)
    if auth.returncode:
        fail("GitHub CLI is not authenticated; run `gh auth login`")

    user = args.user
    if not user:
        user_process = run_gh(["api", "user", "--jq", ".login"])
        user = user_process.stdout.strip()
    if not user:
        fail("could not determine the GitHub login")

    activities, event_coverage = collect_events(
        user, journal_date, timezone, args.repo, args.owner
    )
    warnings: list[str] = []
    pushed_items, push_warnings = collect_pushed_commits(activities)
    warnings.extend(push_warnings)

    matches: dict[tuple[str, str], dict[str, Any]] = {}
    for role in ("author", "committer"):
        for item in search_commits(user, journal_date, args.repo, args.owner, args.limit, role):
            repository = normalize_repository(item.get("repository"))
            sha = str(item.get("sha") or item.get("id") or "")
            key = (repository, sha)
            if key not in matches:
                item["_matched_via"] = [role]
                matches[key] = item
            elif role not in matches[key]["_matched_via"]:
                matches[key]["_matched_via"].append(role)

    for item in pushed_items:
        repository = str(item.get("_repository") or normalize_repository(item.get("repository")))
        sha = str(item.get("sha") or item.get("id") or "")
        key = (repository, sha)
        if key not in matches:
            matches[key] = item
            continue
        matched_via = matches[key].setdefault("_matched_via", [])
        if "push" not in matched_via:
            matched_via.append("push")
        existing_pushes = matches[key].setdefault("_pushes", [])
        for push in item.get("_pushes", []):
            if push not in existing_pushes:
                existing_pushes.append(push)

    items = sorted(
        matches.values(),
        key=evidence_timestamp,
    )[: args.limit]

    commits: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        repository = str(item.get("_repository") or normalize_repository(item.get("repository")))
        sha = str(item.get("sha") or item.get("id") or "")
        message = commit_message(item)
        detail, detail_error = collect_detail(repository, sha)
        if detail_error:
            warnings.append(f"{repository}@{sha[:8]}: {detail_error}")

        files = []
        for changed in detail.get("files", []) if isinstance(detail.get("files"), list) else []:
            if not isinstance(changed, dict):
                continue
            files.append(
                {
                    "path": changed.get("filename"),
                    "status": changed.get("status"),
                    "additions": changed.get("additions"),
                    "deletions": changed.get("deletions"),
                    "changes": changed.get("changes"),
                    "previous_path": changed.get("previous_filename"),
                }
            )
        stats = detail.get("stats") if isinstance(detail.get("stats"), dict) else {}
        parents = item.get("parents") if isinstance(item.get("parents"), list) else detail.get("parents", [])
        authored_at = commit_timestamp(item, "author")
        committed_at = commit_timestamp(item, "committer")
        authored_local_date = event_local_date(authored_at, timezone) if authored_at else ""
        committed_local_date = event_local_date(committed_at, timezone) if committed_at else ""
        pushes = item.get("_pushes", []) if isinstance(item.get("_pushes"), list) else []
        original_dates = {date for date in (authored_local_date, committed_local_date) if date}
        commits.append(
            {
                "repository": repository,
                "sha": sha,
                "short_sha": sha[:8],
                "url": item.get("url") or item.get("html_url") or detail.get("html_url"),
                "title": message.splitlines()[0] if message else "",
                "message": message,
                "matched_via": item.get("_matched_via", []),
                "author_login": account_login(item, "author"),
                "committer_login": account_login(item, "committer"),
                "authored_at": authored_at,
                "committed_at": committed_at,
                "authored_local_date": authored_local_date,
                "committed_local_date": committed_local_date,
                "pushes": pushes,
                "is_delayed_push": bool(
                    pushes and original_dates and journal_date not in original_dates
                ),
                "is_merge": isinstance(parents, list) and len(parents) > 1,
                "stats": {
                    "additions": stats.get("additions"),
                    "deletions": stats.get("deletions"),
                    "total": stats.get("total"),
                    "files_changed": len(files),
                },
                "files": files,
            }
        )

    created_issues = search_created_items(
        "issue", user, journal_date, args.repo, args.owner, args.limit
    )
    created_pull_requests = search_created_items(
        "pull_request", user, journal_date, args.repo, args.owner, args.limit
    )
    if not event_coverage["complete_for_requested_date"]:
        warnings.append(
            "The GitHub event stream does not fully cover this date; comments, replies, "
            "reviews, and other non-searchable activity may be incomplete."
        )

    payload = {
        "journal_date": journal_date,
        "utc_offset": args.utc_offset or str(dt.datetime.now().astimezone().utcoffset()),
        "github_user": user,
        "repository_filters": args.repo,
        "owner_filters": args.owner,
        "commit_count": len(commits),
        "pushed_commit_count": sum(bool(commit.get("pushes")) for commit in commits),
        "delayed_push_commit_count": sum(
            bool(commit.get("is_delayed_push")) for commit in commits
        ),
        "activity_count": len(activities),
        "created_issue_count": len(created_issues),
        "created_pull_request_count": len(created_pull_requests),
        "coverage_note": (
            "Commits are searched globally by author and committer. Same-day PushEvents "
            "are also expanded from their before...head ranges, so commits created earlier "
            "but pushed on the requested date remain visible with their original timestamps. "
            "Recent non-commit work is collected from the authenticated user event stream, "
            "and created issues/PRs are cross-checked with global search."
        ),
        "event_coverage": event_coverage,
        "warnings": warnings,
        "commits": commits,
        "activities": activities,
        "created_issues": created_issues,
        "created_pull_requests": created_pull_requests,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    main()
