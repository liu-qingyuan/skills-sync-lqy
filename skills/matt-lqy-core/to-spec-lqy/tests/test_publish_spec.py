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
PUBLISHER = SKILL_DIR / "scripts" / "publish_spec_issue.py"
REAL_RALPH_SKILL_DIR = Path(__file__).resolve().parents[3] / "lqy-local" / "ralph-plan-lqy"
BASE_COMMIT = "02b192be4d60ed1f57f27231b7e1d0b31fb5eec2"


class SkillWorkflowTests(unittest.TestCase):
    def test_design_review_is_required_before_presentation_and_publication(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        review = skill.index("在给出最终方案或发布前")

        for dependency in ("$codebase-design-lqy", "$gitnexus", "$simple"):
            self.assertGreater(skill.index(dependency), review)
        self.assertLess(review, skill.index("publish_spec_issue.py"))


def spec_body() -> str:
    return textwrap.dedent(
        f"""
        ## Problem Statement

        Test spec.

        ## Solution

        Publish safely.

        ## User Stories

        1. As a maintainer, I want a validated spec, so that Ralph sees complete work.

        ## Implementation Decisions

        - Resolve the Git contract from the remote.

        ## Testing Decisions

        - Test the publisher command.

        ## Mermaid Gate

        不需要图。测试 fixture 不改变架构或公共接口。

        ## Out of Scope

        - Swift implementation.

        ## Further Notes

        None.

        ## Git

        - Branch: `main`
        - Base branch: `origin/main`
        - Base commit: `{BASE_COMMIT}`
        """
    ).strip()


class PublishSpecIssueCliTests(unittest.TestCase):
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
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.body_file = self.root / "spec.md"
        self.body_file.write_text(spec_body(), encoding="utf-8")
        self.log_file = self.root / "gh.log"
        self.provision_log = self.root / "provision.json"
        self.skill_dir = self.root / "ralph-plan-lqy"
        scripts_dir = self.skill_dir / "scripts"
        scripts_dir.mkdir(parents=True)
        for name in ("producer_adapter.py", "git_contract.py"):
            (scripts_dir / name).write_text(
                (REAL_RALPH_SKILL_DIR / "scripts" / name).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        provisioner = scripts_dir / "provision_workspace.py"
        provisioner.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, re, sys\n"
            "body = sys.stdin.read()\n"
            "pathlib.Path(os.environ['TEST_PROVISION_LOG']).write_text(json.dumps({"
            "'argv': sys.argv[1:], 'body': body, 'cwd': str(pathlib.Path.cwd())}))\n"
            "if os.environ.get('TEST_FAIL_PROVISION'):\n"
            "    print('PROVISION ERROR: requested failure', file=sys.stderr)\n"
            "    raise SystemExit(3)\n"
            "branch = re.search(r'- Branch: `([^`]+)`', body).group(1)\n"
            "json.dump({'branch': branch, 'path': '/tmp/project-worktree', 'head': '"
            + BASE_COMMIT
            + "', 'upstream': 'origin/' + branch}, sys.stdout)\n",
            encoding="utf-8",
        )
        provisioner.chmod(0o755)
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "log = pathlib.Path(os.environ['TEST_GH_LOG'])\n"
            "with log.open('a', encoding='utf-8') as handle:\n"
            "    handle.write(json.dumps({'argv': sys.argv[1:], 'cwd': str(pathlib.Path.cwd())}) + '\\n')\n"
            "args = sys.argv[1:]\n"
            "if args[:2] == ['issue', 'create']:\n"
            "    print('https://github.com/example/project/issues/42')\n"
            "elif args[:3] == ['issue', 'view', '42']:\n"
            "    print(pathlib.Path(os.environ['TEST_VIEW_BODY']).read_text(encoding='utf-8'))\n"
            "elif args[:3] == ['issue', 'edit', '42']:\n"
            "    pass\n"
            "else:\n"
            "    print(f'unexpected gh argv: {args}', file=sys.stderr)\n"
            "    raise SystemExit(2)\n",
            encoding="utf-8",
        )
        gh.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{bin_dir}{os.pathsep}{self.env['PATH']}"
        self.env["TEST_GH_LOG"] = str(self.log_file)
        self.env["TEST_VIEW_BODY"] = str(self.body_file)
        self.env["RALPH_PLAN_SKILL_DIR"] = str(self.skill_dir)
        self.env["TEST_PROVISION_LOG"] = str(self.provision_log)

    def publish(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PUBLISHER),
                "--repo",
                str(self.repo),
                "--title",
                "Spec: Test flow",
                "--body-file",
                os.path.relpath(self.body_file, self.outside),
            ],
            text=True,
            capture_output=True,
            env=self.env,
            cwd=self.outside,
        )

    def calls(self) -> list[list[str]]:
        if not self.log_file.exists():
            return []
        return [
            json.loads(line)["argv"]
            for line in self.log_file.read_text(encoding="utf-8").splitlines()
        ]

    def call_cwds(self) -> list[str]:
        if not self.log_file.exists():
            return []
        return [
            json.loads(line)["cwd"]
            for line in self.log_file.read_text(encoding="utf-8").splitlines()
        ]

    def test_ready_label_is_applied_only_after_create_and_readback_validation(self) -> None:
        result = self.publish()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        calls = self.calls()
        self.assertEqual(["create", "view", "edit"], [call[1] for call in calls])
        self.assertNotIn("--label", calls[0])
        self.assertEqual(["--add-label", "ready-for-agent"], calls[2][-2:])
        self.assertEqual([str(self.repo.resolve())] * 3, self.call_cwds())
        output = json.loads(result.stdout)
        self.assertEqual(42, output["number"])
        self.assertEqual("/tmp/project-worktree", output["workspace"]["path"])
        provision = json.loads(self.provision_log.read_text(encoding="utf-8"))
        self.assertEqual(str(self.repo.resolve()), provision["cwd"])
        self.assertIn("## Git", provision["body"])

    def test_invalid_contract_stops_before_creating_issue(self) -> None:
        self.body_file.write_text(f"{spec_body()}\n\n{spec_body()}", encoding="utf-8")

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertEqual([], self.calls())
        self.assertFalse(self.provision_log.exists())

    def test_missing_mermaid_gate_stops_before_creating_issue(self) -> None:
        body = spec_body()
        start = body.index("## Mermaid Gate")
        end = body.index("## Out of Scope")
        self.body_file.write_text(body[:start] + body[end:], encoding="utf-8")

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("missing `## Mermaid Gate`", result.stderr)
        self.assertEqual([], self.calls())
        self.assertFalse(self.provision_log.exists())

    def test_provision_failure_stops_before_creating_issue(self) -> None:
        self.env["TEST_FAIL_PROVISION"] = "1"

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("requested failure", result.stderr)
        self.assertEqual([], self.calls())

    def test_failed_readback_validation_leaves_issue_without_ready_label(self) -> None:
        readback = self.root / "readback.md"
        readback.write_text(f"{spec_body()}\n\n## Notes\n\nChanged remotely.\n", encoding="utf-8")
        self.env["TEST_VIEW_BODY"] = str(readback)

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertEqual(["create", "view"], [call[1] for call in self.calls()])


if __name__ == "__main__":
    unittest.main()
