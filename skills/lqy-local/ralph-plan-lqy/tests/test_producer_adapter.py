from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from producer_adapter import (  # noqa: E402
    ProducerContractError,
    ProducerToolAdapter,
    ProducerToolError,
)


BASE_COMMIT = "02b192be4d60ed1f57f27231b7e1d0b31fb5eec2"


class ProducerToolAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(
            ["git", "init", "--initial-branch=main", str(self.repo)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "remote", "add", "origin", "https://github.com/example/project.git"],
            check=True,
        )
        self.skill_dir = self.root / "ralph-plan-lqy"
        self.scripts = self.skill_dir / "scripts"
        self.scripts.mkdir(parents=True)
        self.adapter = ProducerToolAdapter(self.repo, skill_dir=self.skill_dir)

    def write_script(self, name: str, source: str) -> Path:
        path = self.scripts / name
        path.write_text(f"#!/usr/bin/env python3\n{source}", encoding="utf-8")
        path.chmod(0o755)
        return path

    def test_gh_runs_in_the_explicit_repository(self) -> None:
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import os, pathlib\n"
            "print(os.environ.get('GH_REPO', '<unset>'))\n"
            "print(pathlib.Path.cwd())\n",
            encoding="utf-8",
        )
        gh.chmod(0o755)

        with patch.dict(
            os.environ,
            {
                "GH_REPO": "wrong/project",
                "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            },
        ):
            output = self.adapter.gh("repo", "view")

        self.assertEqual(["<unset>", str(self.repo.resolve())], output.splitlines())

    def test_issue_calls_bind_origin_despite_upstream_and_wrong_environment(self) -> None:
        subprocess.run(
            ["git", "-C", str(self.repo), "remote", "add", "upstream", "https://github.com/upstream/project.git"],
            check=True,
        )
        adapter = ProducerToolAdapter(self.repo, skill_dir=self.skill_dir)
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "args = sys.argv[1:]\n"
            "target = args[args.index('--repo') + 1] if '--repo' in args else 'upstream/project'\n"
            "print(json.dumps({'target': target, 'cwd': str(pathlib.Path.cwd()), "
            "'environment_repo': os.environ.get('GH_REPO')}))\n",
            encoding="utf-8",
        )
        gh.chmod(0o755)
        with patch.dict(os.environ, {"GH_REPO": "wrong/project", "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}"}):
            result = json.loads(adapter.gh("issue", "list", "--state", "open"))
        self.assertEqual("github.com/example/project", result["target"])
        self.assertEqual(str(self.repo.resolve()), result["cwd"])
        self.assertIsNone(result["environment_repo"])

    def test_first_create_verifies_bound_target_once_before_mutating(self) -> None:
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "args = sys.argv[1:]\n"
            "with pathlib.Path(os.environ['TEST_GH_LOG']).open('a') as log:\n"
            "    log.write(json.dumps(args) + '\\n')\n"
            "if args[:2] == ['repo', 'view']:\n"
            "    print(os.environ['TEST_VIEW_RESPONSE'])\n"
            "elif args[:2] == ['issue', 'create']:\n"
            "    print('https://github.com/example/project/issues/42')\n"
            "else:\n"
            "    raise SystemExit(2)\n",
            encoding="utf-8",
        )
        gh.chmod(0o755)
        log_file = self.root / "gh.log"
        with patch.dict(os.environ, {
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "TEST_GH_LOG": str(log_file),
            "TEST_VIEW_RESPONSE": json.dumps({"nameWithOwner": "Example/Project"}),
        }):
            self.adapter.gh("issue", "create", "--title", "First")
            self.adapter.gh("issue", "create", "--title", "Second")
        calls = [json.loads(line) for line in log_file.read_text().splitlines()]
        self.assertEqual(
            [
                ["repo", "view", "github.com/example/project", "--json", "nameWithOwner"],
                ["issue", "create", "--title", "First", "--repo", "github.com/example/project"],
                ["issue", "create", "--title", "Second", "--repo", "github.com/example/project"],
            ],
            calls,
        )

    def test_failed_target_check_never_creates_and_is_retried(self) -> None:
        for response in ("{}", "[]", '{"nameWithOwner": 7}', '{"nameWithOwner": "upstream/project"}', "not-json"):
            with self.subTest(response=response):
                adapter = ProducerToolAdapter(self.repo, skill_dir=self.skill_dir)
                result = subprocess.CompletedProcess([], 0, response, "")
                with patch("producer_adapter.subprocess.run", return_value=result) as run:
                    for _ in range(2):
                        with self.assertRaises(ProducerToolError):
                            adapter.gh("issue", "create", "--title", "Unsafe")
                self.assertEqual(2, run.call_count)
                self.assertTrue(all(call.args[0] == ["gh", "repo", "view", "github.com/example/project", "--json", "nameWithOwner"] for call in run.call_args_list))
        adapter = ProducerToolAdapter(self.repo, skill_dir=self.skill_dir)
        with patch("producer_adapter.subprocess.run", return_value=subprocess.CompletedProcess([], 1, "", "not reachable")) as run:
            with self.assertRaisesRegex(ProducerToolError, "not reachable"):
                adapter.gh("issue", "create")
        run.assert_called_once()
        self.assertEqual("repo", run.call_args.args[0][1])

    def test_repository_binding_supports_https_ssh_and_unambiguous_remote(self) -> None:
        for remote_url in ("https://github.com/example/project.git", "git@github.com:example/project.git", "ssh://git@github.com/example/project.git"):
            with self.subTest(remote_url=remote_url):
                subprocess.run(["git", "-C", str(self.repo), "remote", "set-url", "origin", remote_url], check=True)
                adapter = ProducerToolAdapter(self.repo, skill_dir=self.skill_dir)
                with patch("producer_adapter.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "ok", "")) as run:
                    self.assertEqual("ok", adapter.gh("issue", "list"))
                self.assertEqual(["gh", "issue", "list", "--repo", "github.com/example/project"], run.call_args.args[0])
        subprocess.run(["git", "-C", str(self.repo), "remote", "rename", "origin", "fork"], check=True)
        self.assertEqual("github.com/example/project", ProducerToolAdapter(self.repo, skill_dir=self.skill_dir).github_repository)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "upstream", "https://github.com/upstream/project.git"], check=True)
        with self.assertRaisesRegex(ProducerContractError, "multiple remotes"):
            ProducerToolAdapter(self.repo, skill_dir=self.skill_dir)

    def test_unresolvable_publication_target_is_rejected(self) -> None:
        subprocess.run(["git", "-C", str(self.repo), "remote", "set-url", "origin", str(self.root / "local.git")], check=True)
        with self.assertRaises(ProducerContractError):
            ProducerToolAdapter(self.repo, skill_dir=self.skill_dir)

    def test_repository_context_requires_a_git_remote(self) -> None:
        plain_directory = self.root / "plain"
        plain_directory.mkdir()

        with self.assertRaises(ProducerContractError):
            ProducerToolAdapter(plain_directory, skill_dir=self.skill_dir)

    def test_issue_queries_hide_github_json_behind_typed_snapshots(self) -> None:
        issue = {
            "number": 10,
            "title": "Existing Ticket",
            "body": "## Parent\n\n#1",
            "state": "OPEN",
            "labels": [{"name": "ready-for-agent"}],
        }
        with patch.object(self.adapter, "gh", return_value=json.dumps(issue)) as gh:
            snapshot = self.adapter.view_issue(10)
        gh.assert_called_once_with(
            "issue",
            "view",
            "10",
            "--json",
            "number,title,body,state,labels",
        )
        with patch.object(self.adapter, "gh", return_value=json.dumps([issue])) as gh:
            snapshots = self.adapter.list_issues()
        gh.assert_called_once_with(
            "issue",
            "list",
            "--state",
            "all",
            "--limit",
            "100000",
            "--json",
            "number,title,body,state,labels",
        )

        self.assertEqual(10, snapshot.number)
        self.assertEqual(frozenset({"ready-for-agent"}), snapshot.labels)
        self.assertEqual((snapshot,), snapshots)

    def test_issue_queries_reject_malformed_github_schema(self) -> None:
        malformed = {
            "number": 10,
            "title": "Existing Ticket",
            "body": "body",
            "state": "OPEN",
            "labels": ["ready-for-agent"],
        }

        with patch.object(self.adapter, "gh", return_value=json.dumps([malformed])):
            with self.assertRaises(ProducerToolError):
                self.adapter.list_issues()

    def test_exit_three_is_a_contract_error(self) -> None:
        command = self.write_script("contract_error.py", "raise SystemExit(3)\n")

        with self.assertRaises(ProducerContractError):
            self.adapter.run_json([sys.executable, str(command)], source="fixture")

    def test_other_exit_and_invalid_json_are_tool_errors(self) -> None:
        failed = self.write_script("tool_error.py", "raise SystemExit(1)\n")
        malformed = self.write_script("invalid_json.py", "print('not-json')\n")

        with self.assertRaises(ProducerToolError):
            self.adapter.run_json([sys.executable, str(failed)], source="fixture")
        with self.assertRaises(ProducerToolError):
            self.adapter.run_json([sys.executable, str(malformed)], source="fixture")

    def test_git_contract_fields_and_sha_have_one_typed_validator(self) -> None:
        invalid_payloads = (
            "{}",
            f'{{"branch": 1, "base_branch": "origin/main", "base_commit": "{BASE_COMMIT}"}}',
            '{"branch": "main", "base_branch": "origin/main", "base_commit": "short"}',
        )

        for index, payload in enumerate(invalid_payloads):
            with self.subTest(payload=payload):
                self.write_script("git_contract.py", f"print({payload!r})\n")
                with self.assertRaises(ProducerToolError):
                    self.adapter.validate_git_contract(f"body-{index}")

    def test_worktree_fields_and_sha_have_one_typed_validator(self) -> None:
        invalid_payloads = (
            "{}",
            f'{{"path": "/tmp/project", "branch": 1, "head": "{BASE_COMMIT}", "upstream": "origin/main"}}',
            '{"path": "/tmp/project", "branch": "main", "head": "short", "upstream": "origin/main"}',
        )

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                self.write_script("provision_workspace.py", f"print({payload!r})\n")
                with self.assertRaises(ProducerToolError):
                    self.adapter.provision_workspace("body", expected_branch="main")


if __name__ == "__main__":
    unittest.main()
