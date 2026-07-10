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
RALPH_SKILL_DIR = Path(__file__).resolve().parents[3] / "lqy-local" / "ralph-plan-lqy"
BASE_COMMIT = "02b192be4d60ed1f57f27231b7e1d0b31fb5eec2"


def spec_body() -> str:
    return textwrap.dedent(
        f"""
        ## Problem Statement

        Test spec.

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
        self.body_file = self.root / "spec.md"
        self.body_file.write_text(spec_body(), encoding="utf-8")
        self.log_file = self.root / "gh.log"
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "log = pathlib.Path(os.environ['TEST_GH_LOG'])\n"
            "with log.open('a', encoding='utf-8') as handle:\n"
            "    handle.write(json.dumps(sys.argv[1:]) + '\\n')\n"
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
        self.env["RALPH_PLAN_SKILL_DIR"] = str(RALPH_SKILL_DIR)

    def publish(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PUBLISHER),
                "--title",
                "Spec: Test flow",
                "--body-file",
                str(self.body_file),
            ],
            text=True,
            capture_output=True,
            env=self.env,
        )

    def calls(self) -> list[list[str]]:
        if not self.log_file.exists():
            return []
        return [json.loads(line) for line in self.log_file.read_text(encoding="utf-8").splitlines()]

    def test_ready_label_is_applied_only_after_create_and_readback_validation(self) -> None:
        result = self.publish()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        calls = self.calls()
        self.assertEqual(["create", "view", "edit"], [call[1] for call in calls])
        self.assertNotIn("--label", calls[0])
        self.assertEqual(["--add-label", "ready-for-agent"], calls[2][-2:])
        self.assertEqual(42, json.loads(result.stdout)["number"])

    def test_invalid_contract_stops_before_creating_issue(self) -> None:
        self.body_file.write_text(f"{spec_body()}\n\n{spec_body()}", encoding="utf-8")

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
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
