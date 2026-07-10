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
PUBLISHER = SKILL_DIR / "scripts" / "publish_ticket_set.py"
REAL_CONTRACT_VALIDATOR = (
    Path(__file__).resolve().parents[3]
    / "lqy-local"
    / "ralph-plan-lqy"
    / "scripts"
    / "git_contract.py"
)
BASE_COMMIT = "02b192be4d60ed1f57f27231b7e1d0b31fb5eec2"


def git_section(*, branch: str = "main") -> str:
    return textwrap.dedent(
        f"""
        ## Git

        - Branch: `{branch}`
        - Base branch: `origin/main`
        - Base commit: `{BASE_COMMIT}`
        """
    ).strip()


def ticket_draft(name: str) -> str:
    return textwrap.dedent(
        f"""
        ## What to build

        Deliver {name}.

        ## Acceptance criteria

        - [ ] {name} works through the public command.

        ## Mermaid Gate

        No diagram is needed because this fixture does not change an interface.
        """
    ).strip()


class PublishTicketSetCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.parent_body = self.root / "parent.md"
        self.parent_body.write_text(f"## Problem Statement\n\nTest parent.\n\n{git_section()}\n", encoding="utf-8")
        self.external_body = self.root / "external.md"
        self.external_body.write_text(f"## What to build\n\nExisting work.\n\n{git_section()}\n", encoding="utf-8")
        self.first_draft = self.root / "first.md"
        self.first_draft.write_text(ticket_draft("foundation"), encoding="utf-8")
        self.second_draft = self.root / "second.md"
        self.second_draft.write_text(ticket_draft("feature"), encoding="utf-8")
        self.manifest = self.root / "tickets.json"
        self.write_manifest()
        self.event_log = self.root / "events.log"
        self.issue_dir = self.root / "issues"
        self.issue_dir.mkdir()
        self.skill_dir = self.root / "ralph-plan-lqy"
        scripts_dir = self.skill_dir / "scripts"
        scripts_dir.mkdir(parents=True)
        (scripts_dir / "git_contract.py").write_text(
            REAL_CONTRACT_VALIDATOR.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        provisioner = scripts_dir / "provision_workspace.py"
        provisioner.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "log = pathlib.Path(os.environ['TEST_EVENT_LOG'])\n"
            "with log.open('a', encoding='utf-8') as handle:\n"
            "    handle.write('provision\\n')\n"
            "if os.environ.get('TEST_FAIL_PROVISION'):\n"
            "    print('PROVISION ERROR: requested failure', file=sys.stderr)\n"
            "    raise SystemExit(3)\n"
            "json.dump({'branch': 'main', 'path': '/tmp/project', 'head': '"
            + BASE_COMMIT
            + "', 'upstream': 'origin/main'}, sys.stdout)\n",
            encoding="utf-8",
        )
        provisioner.chmod(0o755)

        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        gh.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "args = sys.argv[1:]\n"
            "log = pathlib.Path(os.environ['TEST_EVENT_LOG'])\n"
            "with log.open('a', encoding='utf-8') as handle:\n"
            "    handle.write('gh ' + json.dumps(args) + '\\n')\n"
            "issue_dir = pathlib.Path(os.environ['TEST_ISSUE_DIR'])\n"
            "labels_file = issue_dir / 'labels.json'\n"
            "labels = json.loads(labels_file.read_text()) if labels_file.exists() else {}\n"
            "def issue_data(number):\n"
            "    if number == 1:\n"
            "        body = pathlib.Path(os.environ['TEST_PARENT_BODY']).read_text()\n"
            "        return {'number': 1, 'title': 'Spec: Parent', 'body': body, "
            "'state': 'OPEN', 'labels': [{'name': 'ready-for-agent'}]}\n"
            "    if number == 99:\n"
            "        body = pathlib.Path(os.environ['TEST_EXTERNAL_BODY']).read_text()\n"
            "        return {'number': 99, 'title': 'Existing blocker', 'body': body, "
            "'state': 'OPEN', 'labels': [{'name': 'ready-for-agent'}]}\n"
            "    record = json.loads((issue_dir / f'{number}.json').read_text())\n"
            "    record['labels'] = [{'name': value} for value in labels.get(str(number), [])]\n"
            "    if os.environ.get('TEST_MUTATE_READBACK') == str(number):\n"
            "        record['body'] += '\\n\\n## Changed\\n\\nRemote mutation.\\n'\n"
            "    return record\n"
            "if args[:2] == ['issue', 'view']:\n"
            "    print(json.dumps(issue_data(int(args[2]))))\n"
            "elif args[:2] == ['issue', 'create']:\n"
            "    existing = sorted(int(path.stem) for path in issue_dir.glob('[0-9]*.json'))\n"
            "    number = 42 if not existing else max(existing) + 1\n"
            "    if os.environ.get('TEST_FAIL_CREATE') == str(number):\n"
            "        print('requested create failure', file=sys.stderr)\n"
            "        raise SystemExit(1)\n"
            "    title = args[args.index('--title') + 1]\n"
            "    body_file = pathlib.Path(args[args.index('--body-file') + 1])\n"
            "    record = {'number': number, 'title': title, 'body': body_file.read_text(), 'state': 'OPEN'}\n"
            "    (issue_dir / f'{number}.json').write_text(json.dumps(record))\n"
            "    print(f'https://github.com/example/project/issues/{number}')\n"
            "elif args[:2] == ['issue', 'edit']:\n"
            "    number = int(args[2])\n"
            "    if '--add-label' in args:\n"
            "        if os.environ.get('TEST_FAIL_LABEL') == str(number):\n"
            "            print('requested label failure', file=sys.stderr)\n"
            "            raise SystemExit(1)\n"
            "        labels[str(number)] = ['ready-for-agent']\n"
            "    elif '--remove-label' in args:\n"
            "        labels[str(number)] = []\n"
            "    else:\n"
            "        print(f'unexpected edit argv: {args}', file=sys.stderr)\n"
            "        raise SystemExit(2)\n"
            "    labels_file.write_text(json.dumps(labels))\n"
            "else:\n"
            "    print(f'unexpected gh argv: {args}', file=sys.stderr)\n"
            "    raise SystemExit(2)\n",
            encoding="utf-8",
        )
        gh.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{bin_dir}{os.pathsep}{self.env['PATH']}"
        self.env["RALPH_PLAN_SKILL_DIR"] = str(self.skill_dir)
        self.env["TEST_EVENT_LOG"] = str(self.event_log)
        self.env["TEST_ISSUE_DIR"] = str(self.issue_dir)
        self.env["TEST_PARENT_BODY"] = str(self.parent_body)
        self.env["TEST_EXTERNAL_BODY"] = str(self.external_body)

    def write_manifest(self, *, second_blockers: list[str] | None = None) -> None:
        self.manifest.write_text(
            json.dumps(
                {
                    "tickets": [
                        {
                            "id": "foundation",
                            "title": "Build foundation",
                            "body_file": self.first_draft.name,
                            "blocked_by": [],
                        },
                        {
                            "id": "feature",
                            "title": "Build feature",
                            "body_file": self.second_draft.name,
                            "blocked_by": ["foundation"] if second_blockers is None else second_blockers,
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )

    def publish(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PUBLISHER),
                "--repo",
                str(self.root),
                "--parent",
                "1",
                "--manifest",
                str(self.manifest),
            ],
            text=True,
            capture_output=True,
            env=self.env,
        )

    def events(self) -> list[str]:
        return self.event_log.read_text(encoding="utf-8").splitlines() if self.event_log.exists() else []

    def issue(self, number: int) -> dict[str, object]:
        return json.loads((self.issue_dir / f"{number}.json").read_text(encoding="utf-8"))

    def labels(self) -> dict[str, list[str]]:
        path = self.issue_dir / "labels.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def test_provisions_then_publishes_and_validates_the_complete_set_before_labeling(self) -> None:
        result = self.publish()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        events = self.events()
        operations = ["provision" if event == "provision" else json.loads(event[3:])[1] for event in events]
        self.assertEqual(
            ["view", "provision", "create", "create", "view", "view", "edit", "edit"],
            operations,
        )
        first_body = str(self.issue(42)["body"])
        second_body = str(self.issue(43)["body"])
        self.assertIn("## Parent\n\n#1", first_body)
        self.assertIn("## Blocked by\n\n- None — can start immediately", first_body)
        self.assertIn("## Blocked by\n\n- #42", second_body)
        self.assertTrue(first_body.rstrip().endswith(git_section()))
        self.assertTrue(second_body.rstrip().endswith(git_section()))
        self.assertEqual({"42": ["ready-for-agent"], "43": ["ready-for-agent"]}, self.labels())
        output = json.loads(result.stdout)
        self.assertEqual([42, 43], [ticket["number"] for ticket in output["tickets"]])

    def test_invalid_parent_contract_stops_before_provisioning_or_creation(self) -> None:
        self.parent_body.write_text(f"{git_section()}\n\n{git_section()}\n", encoding="utf-8")

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertEqual(["view"], [json.loads(event[3:])[1] for event in self.events()])

    def test_missing_mermaid_gate_stops_before_provisioning_or_creation(self) -> None:
        self.second_draft.write_text(
            "## What to build\n\nIncomplete.\n\n"
            "## Acceptance criteria\n\n- [ ] Still incomplete.\n",
            encoding="utf-8",
        )

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("missing `## Mermaid Gate`", result.stderr)
        self.assertEqual(["view"], [json.loads(event[3:])[1] for event in self.events()])

    def test_cross_branch_external_blocker_is_rejected_before_provisioning(self) -> None:
        self.write_manifest(second_blockers=["#99"])
        self.external_body.write_text(
            f"## What to build\n\nOther branch.\n\n{git_section(branch='feature/other')}\n",
            encoding="utf-8",
        )

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("does not match parent Git contract", result.stderr)
        self.assertEqual(["view", "view"], [json.loads(event[3:])[1] for event in self.events()])

    def test_provision_failure_does_not_create_tickets(self) -> None:
        self.env["TEST_FAIL_PROVISION"] = "1"

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertEqual(["view", "provision"], [
            json.loads(event[3:])[1] if event.startswith("gh ") else event for event in self.events()
        ])

    def test_partial_create_failure_leaves_every_created_ticket_unlabeled(self) -> None:
        self.env["TEST_FAIL_CREATE"] = "43"

        result = self.publish()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertTrue((self.issue_dir / "42.json").exists())
        self.assertFalse((self.issue_dir / "43.json").exists())
        self.assertEqual({}, self.labels())
        self.assertNotIn("edit", [json.loads(event[3:])[1] for event in self.events() if event.startswith("gh ")])

    def test_failed_readback_validation_leaves_the_set_unlabeled(self) -> None:
        self.env["TEST_MUTATE_READBACK"] = "43"

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertEqual({}, self.labels())
        self.assertNotIn("edit", [json.loads(event[3:])[1] for event in self.events() if event.startswith("gh ")])

    def test_label_failure_rolls_back_labels_from_the_complete_set(self) -> None:
        self.env["TEST_FAIL_LABEL"] = "42"

        result = self.publish()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual([], self.labels().get("43", []))
        edit_events = [
            json.loads(event[3:])
            for event in self.events()
            if event.startswith("gh ") and json.loads(event[3:])[1] == "edit"
        ]
        self.assertEqual(
            [
                ["issue", "edit", "43", "--add-label", "ready-for-agent"],
                ["issue", "edit", "42", "--add-label", "ready-for-agent"],
                ["issue", "edit", "43", "--remove-label", "ready-for-agent"],
            ],
            edit_events,
        )


if __name__ == "__main__":
    unittest.main()
