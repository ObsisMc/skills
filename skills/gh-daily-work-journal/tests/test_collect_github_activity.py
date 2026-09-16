import json
import sys
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import collect_github_activity as collector  # noqa: E402


class PushedCommitAttributionTests(unittest.TestCase):
    def test_excludes_collaborator_commits_from_a_user_push_range(self) -> None:
        comparison = CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps(
                {
                    "commits": [
                        {
                            "sha": "foreign",
                            "author": {"login": "wanglongan587"},
                            "committer": {"login": "wanglongan587"},
                        },
                        {
                            "sha": "mine",
                            "author": {"login": "ObsisMc"},
                            "committer": {"login": "web-flow"},
                        },
                    ],
                    "total_commits": 2,
                }
            ),
            stderr="",
        )
        activities = [
            {
                "type": "PushEvent",
                "event_id": "push-1",
                "repository": "owner/repo",
                "created_at": "2026-09-15T10:00:00Z",
                "ref": "refs/heads/main",
                "push_before": "before",
                "push_head": "head",
            }
        ]

        with patch.object(collector, "run_gh", return_value=comparison):
            commits, warnings = collector.collect_pushed_commits(activities, "ObsisMc")

        self.assertEqual(["mine"], [item["sha"] for item in commits])
        self.assertEqual([], warnings)

    def test_excludes_foreign_head_when_push_range_cannot_be_expanded(self) -> None:
        comparison = CompletedProcess(args=[], returncode=1, stdout="", stderr="not found")
        foreign_head = {
            "sha": "foreign-head",
            "author": {"login": "fanj2057-spec"},
            "committer": {"login": "fanj2057-spec"},
        }
        activities = [
            {
                "type": "PushEvent",
                "event_id": "push-2",
                "repository": "owner/repo",
                "created_at": "2026-09-15T10:00:00Z",
                "ref": "refs/heads/main",
                "push_before": "before",
                "push_head": "head",
            }
        ]

        with patch.object(collector, "run_gh", return_value=comparison), patch.object(
            collector, "collect_detail", return_value=(foreign_head, None)
        ):
            commits, _warnings = collector.collect_pushed_commits(activities, "ObsisMc")

        self.assertEqual([], commits)


if __name__ == "__main__":
    unittest.main()
