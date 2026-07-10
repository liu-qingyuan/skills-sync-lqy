from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
GATE = SKILL_DIR / "scripts" / "check_ready_issue_unblocked.py"
CONTRACT_VALIDATOR = SKILL_DIR / "scripts" / "git_contract.py"
BASE_COMMIT = "02b192be4d60ed1f57f27231b7e1d0b31fb5eec2"


def ticket_body(*, branch: str = "main", blocked_by: str = "None - can start immediately") -> str:
    return textwrap.dedent(
        f"""
        ## What to build

        Test ticket.

        ## Blocked by

        {blocked_by}

        ## Git

        - Branch: `{branch}`
        - Base branch: `origin/main`
        - Base commit: `{BASE_COMMIT}`
        """
    ).strip()


class EligibilityGateCliTests(unittest.TestCase):
    def run_contract_validator(self, body: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CONTRACT_VALIDATOR)],
            input=body,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_shared_contract_cli_outputs_structured_contract(self) -> None:
        result = self.run_contract_validator(ticket_body())

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            {
                "base_branch": "origin/main",
                "base_commit": BASE_COMMIT,
                "branch": "main",
            },
            json.loads(result.stdout),
        )

    def test_shared_contract_cli_rejects_malformed_sections(self) -> None:
        valid = ticket_body()
        git_section = valid[valid.index("## Git") :]
        cases = {
            "missing": valid.replace(git_section, ""),
            "duplicate": f"{valid}\n\n{git_section}",
            "unknown field": valid.replace("Base branch", "Remote branch"),
            "wrong order": valid.replace(
                "- Branch: `main`\n- Base branch: `origin/main`",
                "- Base branch: `origin/main`\n- Branch: `main`",
            ),
            "not final": f"{valid}\n\n## Notes\n\nUnexpected trailing section.",
        }

        for name, body in cases.items():
            with self.subTest(name=name):
                result = self.run_contract_validator(body)
                self.assertEqual(3, result.returncode, result.stdout + result.stderr)
                self.assertIn("CONTRACT ERROR", result.stderr)

    def run_gate(
        self,
        issues: dict[int, dict[str, object]],
        *,
        current_branch: str = "main",
        base_is_ancestor: bool = True,
        git_error: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            bin_dir = Path(temp_dir)
            gh = bin_dir / "gh"
            git = bin_dir / "git"
            gh.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, sys\n"
                "issues = json.loads(os.environ['TEST_ISSUES'])\n"
                "number = sys.argv[sys.argv.index('view') + 1]\n"
                "print(json.dumps(issues[number]))\n",
                encoding="utf-8",
            )
            git.write_text(
                "#!/usr/bin/env python3\n"
                "import os, sys\n"
                "args = sys.argv[1:]\n"
                "if os.environ['TEST_GIT_ERROR'] == '1':\n"
                "    print('simulated git failure', file=sys.stderr)\n"
                "    raise SystemExit(2)\n"
                "if args == ['symbolic-ref', '--quiet', '--short', 'HEAD']:\n"
                "    print(os.environ['TEST_CURRENT_BRANCH'])\n"
                "    raise SystemExit(0)\n"
                "if args[:2] == ['merge-base', '--is-ancestor']:\n"
                "    raise SystemExit(0 if os.environ['TEST_BASE_IS_ANCESTOR'] == '1' else 1)\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            gh.chmod(0o755)
            git.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env['PATH']}"
            env["TEST_CURRENT_BRANCH"] = current_branch
            env["TEST_BASE_IS_ANCESTOR"] = "1" if base_is_ancestor else "0"
            env["TEST_GIT_ERROR"] = "1" if git_error else "0"
            env["TEST_ISSUES"] = json.dumps({str(number): issue for number, issue in issues.items()})
            return subprocess.run(
                [sys.executable, str(GATE), "2"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )

    def test_other_branch_is_skipped(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(branch="feature/other"),
                }
            }
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("branch `feature/other` does not match current branch `main`", result.stdout)

    def test_base_commit_must_be_an_ancestor_of_head(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(),
                }
            },
            base_is_ancestor=False,
        )

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"base commit `{BASE_COMMIT}` is not an ancestor of HEAD", result.stderr)

    def test_cross_branch_blocker_is_a_contract_error_even_when_closed(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(blocked_by="- #1"),
                },
                1: {
                    "number": 1,
                    "title": "Earlier ticket",
                    "state": "CLOSED",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(branch="feature/other"),
                },
            }
        )

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("blocker #1 targets branch `feature/other`, expected `main`", result.stderr)

    def test_concrete_ticket_requires_blocked_by_section(self) -> None:
        body = ticket_body().replace(
            "## Blocked by\n\nNone - can start immediately\n\n",
            "",
        )
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": body,
                }
            }
        )

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("missing `## Blocked by` section", result.stderr)

    def test_invalid_branch_name_is_a_contract_error(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(branch="invalid branch"),
                }
            }
        )

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("invalid `Branch` Git ref", result.stderr)

    def test_valid_ticket_is_ready(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(),
                    "assignees": [{"login": "ignored-user"}],
                }
            }
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("READY #2 Ticket", result.stdout.strip())

    def test_open_same_branch_blocker_is_not_ready(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(blocked_by="- #1"),
                },
                1: {
                    "number": 1,
                    "title": "Earlier ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(),
                },
            }
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("blocked by open issues: #1", result.stdout)

    def test_parent_spec_is_skipped_without_blocked_by(self) -> None:
        body = ticket_body().replace(
            "## Blocked by\n\nNone - can start immediately\n\n",
            "",
        )
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Spec: Parent",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": body,
                }
            }
        )

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("parent spec", result.stdout)

    def test_malformed_git_contract_is_distinct_from_environment_error(self) -> None:
        malformed = ticket_body().replace("- Base branch: `origin/main`\n", "")
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": malformed,
                }
            }
        )

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("CONTRACT ERROR #2", result.stderr)

    def test_git_failure_returns_environment_error(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(),
                }
            },
            git_error=True,
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("simulated git failure", result.stderr)

    def test_github_failure_returns_environment_error(self) -> None:
        result = self.run_gate({})

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR #2", result.stderr)

    def test_unparseable_blocked_by_section_is_a_contract_error(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(blocked_by="Waiting for another team"),
                }
            }
        )

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("invalid `## Blocked by` section", result.stderr)

    def test_no_blocker_marker_must_not_match_a_substring(self) -> None:
        result = self.run_gate(
            {
                2: {
                    "number": 2,
                    "title": "Ticket",
                    "state": "OPEN",
                    "labels": [{"name": "ready-for-agent"}],
                    "body": ticket_body(blocked_by="Nonetheless waiting"),
                }
            }
        )

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
