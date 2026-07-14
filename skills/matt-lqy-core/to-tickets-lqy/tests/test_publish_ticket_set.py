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


class SkillWorkflowTests(unittest.TestCase):
    def test_design_review_is_required_before_presentation_and_publication(self) -> None:
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        review = skill.index("在给出 Ticket 方案或发布前")

        for dependency in ("$codebase-design-lqy", "$gitnexus", "$simple"):
            self.assertGreater(skill.index(dependency), review)
        self.assertLess(review, skill.index("把提议拆分呈现为编号列表"))
        self.assertLess(review, skill.index("publish_ticket_set.py"))


def git_section(
    *,
    branch: str = "main",
    base_branch: str = "origin/main",
    base_commit: str = BASE_COMMIT,
) -> str:
    return textwrap.dedent(
        f"""
        ## Git

        - Branch: `{branch}`
        - Base branch: `{base_branch}`
        - Base commit: `{base_commit}`
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


def existing_ticket_body(*, contract: str | None = None) -> str:
    return (
        "## Parent\n\n"
        "#1\n\n"
        "## What to build\n\n"
        "Existing Ticket.\n\n"
        "## Acceptance criteria\n\n"
        "- [x] Existing behavior works.\n\n"
        "## Mermaid Gate\n\n"
        "No diagram was needed.\n\n"
        "## Blocked by\n\n"
        "- None — can start immediately\n\n"
        f"{git_section() if contract is None else contract}"
    )


class PublishTicketSetCliTests(unittest.TestCase):
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
        real_adapter = REAL_CONTRACT_VALIDATOR.with_name("producer_adapter.py")
        (scripts_dir / "producer_adapter.py").write_text(
            real_adapter.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        provisioner = scripts_dir / "provision_workspace.py"
        provisioner.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, pathlib, sys\n"
            "log = pathlib.Path(os.environ['TEST_EVENT_LOG'])\n"
            "with log.open('a', encoding='utf-8') as handle:\n"
            "    handle.write('provision ' + json.dumps(sys.argv[1:]) + '\\n')\n"
            "if os.environ.get('TEST_FAIL_PROVISION'):\n"
            "    print('PROVISION ERROR: requested failure', file=sys.stderr)\n"
            "    raise SystemExit(3)\n"
            "if os.environ.get('TEST_MALFORMED_PROVISION'):\n"
            "    print('{}')\n"
            "    raise SystemExit(0)\n"
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
            "expected_repo = pathlib.Path(os.environ['TEST_EXPECTED_REPO']).resolve()\n"
            "if pathlib.Path.cwd().resolve() != expected_repo:\n"
            "    print(f'wrong gh cwd: {pathlib.Path.cwd()}', file=sys.stderr)\n"
            "    raise SystemExit(2)\n"
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
            "        title = os.environ.get('TEST_EXTERNAL_TITLE', 'Existing blocker')\n"
            "        return {'number': 99, 'title': title, 'body': body, "
            "'state': 'OPEN', 'labels': [{'name': 'ready-for-agent'}]}\n"
            "    record = json.loads((issue_dir / f'{number}.json').read_text())\n"
            "    record['labels'] = [{'name': value} for value in labels.get(str(number), [])]\n"
            "    if os.environ.get('TEST_MUTATE_READBACK') == str(number):\n"
            "        record['body'] += '\\n\\n## Changed\\n\\nRemote mutation.\\n'\n"
            "    return record\n"
            "if args[:2] == ['issue', 'view']:\n"
            "    print(json.dumps(issue_data(int(args[2]))))\n"
            "elif args[:2] == ['issue', 'list']:\n"
            "    records = [issue_data(int(path.stem)) for path in sorted(issue_dir.glob('[0-9]*.json'))]\n"
            "    if os.environ.get('TEST_REVERSE_ISSUE_LIST'):\n"
            "        records.reverse()\n"
            "    print(json.dumps(records))\n"
            "elif args[:2] == ['issue', 'create']:\n"
            "    existing = sorted(int(path.stem) for path in issue_dir.glob('[0-9]*.json'))\n"
            "    number = max([41, *existing]) + 1\n"
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
            "        if os.environ.get('TEST_FAIL_REMOVE_LABEL') == str(number):\n"
            "            print('requested remove label failure', file=sys.stderr)\n"
            "            raise SystemExit(1)\n"
            "        labels[str(number)] = []\n"
            "    else:\n"
            "        print(f'unexpected edit argv: {args}', file=sys.stderr)\n"
            "        raise SystemExit(2)\n"
            "    labels_file.write_text(json.dumps(labels))\n"
            "elif args[:2] == ['issue', 'close']:\n"
            "    number = int(args[2])\n"
            "    record_path = issue_dir / f'{number}.json'\n"
            "    record = json.loads(record_path.read_text())\n"
            "    record['state'] = 'CLOSED'\n"
            "    record_path.write_text(json.dumps(record))\n"
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
        self.env["TEST_EXPECTED_REPO"] = str(self.repo)

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

    def publish(self, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PUBLISHER),
                "--repo",
                str(self.repo),
                "--parent",
                "1",
                "--manifest",
                str(self.manifest),
                *extra_args,
            ],
            text=True,
            capture_output=True,
            env=self.env,
            cwd=self.outside,
        )

    def events(self) -> list[str]:
        return self.event_log.read_text(encoding="utf-8").splitlines() if self.event_log.exists() else []

    def issue(self, number: int) -> dict[str, object]:
        return json.loads((self.issue_dir / f"{number}.json").read_text(encoding="utf-8"))

    def labels(self) -> dict[str, list[str]]:
        path = self.issue_dir / "labels.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def write_existing_issue(
        self,
        number: int,
        *,
        body: str | None = None,
        labels: list[str] | None = None,
        state: str = "OPEN",
    ) -> None:
        (self.issue_dir / f"{number}.json").write_text(
            json.dumps(
                {
                    "number": number,
                    "title": f"Existing Ticket {number}",
                    "body": existing_ticket_body() if body is None else body,
                    "state": state,
                }
            ),
            encoding="utf-8",
        )
        if labels:
            current = self.labels()
            current[str(number)] = labels
            (self.issue_dir / "labels.json").write_text(json.dumps(current), encoding="utf-8")

    def test_provisions_then_publishes_and_validates_the_complete_set_before_labeling(self) -> None:
        result = self.publish()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        events = self.events()
        operations = [
            "provision" if event.startswith("provision ") else json.loads(event[3:])[1]
            for event in events
        ]
        self.assertEqual(
            [
                "view",
                "list",
                "provision",
                "create",
                "create",
                "create",
                "view",
                "view",
                "view",
                "edit",
                "edit",
                "view",
                "view",
                "close",
            ],
            operations,
        )
        gate_body = str(self.issue(42)["body"])
        first_body = str(self.issue(43)["body"])
        second_body = str(self.issue(44)["body"])
        self.assertIn("## Blocked by\n\n- None — can start immediately", gate_body)
        self.assertIn("## Parent\n\n#1", first_body)
        self.assertIn("## Blocked by\n\n- #42", first_body)
        self.assertIn("## Blocked by\n\n- #42\n- #43", second_body)
        self.assertTrue(first_body.rstrip().endswith(git_section()))
        self.assertTrue(second_body.rstrip().endswith(git_section()))
        self.assertEqual("CLOSED", self.issue(42)["state"])
        self.assertEqual({"43": ["ready-for-agent"], "44": ["ready-for-agent"]}, self.labels())
        output = json.loads(result.stdout)
        self.assertEqual(42, output["publication_gate"])
        self.assertEqual([43, 44], [ticket["number"] for ticket in output["tickets"]])

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
        self.assertIn("branch `feature/other` does not match parent branch `main`", result.stderr)
        self.assertEqual(["view", "list", "view"], [json.loads(event[3:])[1] for event in self.events()])

    def test_same_branch_external_blocker_with_different_base_is_allowed(self) -> None:
        self.write_manifest(second_blockers=["#99"])
        self.external_body.write_text(
            "## Parent\n\n#77\n\n"
            "## What to build\n\nOther spec on the same branch.\n\n"
            f"{git_section(base_branch='origin/release', base_commit='1' * 40)}\n",
            encoding="utf-8",
        )

        result = self.publish()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("## Blocked by\n\n- #42\n- #99", str(self.issue(44)["body"]))

    def test_external_parent_spec_is_not_accepted_as_a_ticket_blocker(self) -> None:
        self.write_manifest(second_blockers=["#99"])
        self.env["TEST_EXTERNAL_TITLE"] = "Spec: Other work"

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("blocker #99 must be a concrete Ticket, not a parent spec", result.stderr)
        self.assertFalse((self.issue_dir / "42.json").exists())

    def test_malformed_external_blocker_contract_is_a_contract_error(self) -> None:
        self.write_manifest(second_blockers=["#99"])
        self.external_body.write_text("## Git\n\n- Branch: `main`\n", encoding="utf-8")

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("blocker #99 has an invalid Git contract", result.stderr)
        self.assertFalse((self.issue_dir / "42.json").exists())

    def test_matching_ready_child_freezes_contract_and_allows_incremental_publication(self) -> None:
        self.write_existing_issue(10, labels=["ready-for-agent"])
        existing_before = self.issue(10)

        result = self.publish()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("list", [json.loads(event[3:])[1] for event in self.events() if event.startswith("gh ")])
        self.assertEqual(existing_before, self.issue(10))
        mutations = [
            json.loads(event[3:])
            for event in self.events()
            if event.startswith("gh ") and json.loads(event[3:])[1] in {"edit", "close"}
        ]
        self.assertNotIn("10", [args[2] for args in mutations])

    def test_first_publication_uses_current_parent_contract_without_ready_children(self) -> None:
        result = self.publish()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue(str(self.issue(43)["body"]).rstrip().endswith(git_section()))

    def test_parent_and_ready_child_cannot_drift_past_the_existing_frontier_anchor(self) -> None:
        self.write_existing_issue(9)
        drifted_contract = git_section(base_commit="2" * 40)
        self.write_existing_issue(
            10,
            body=existing_ticket_body(contract=drifted_contract),
            labels=["ready-for-agent"],
        )
        self.parent_body.write_text(
            f"## Problem Statement\n\nEdited parent.\n\n{drifted_contract}\n",
            encoding="utf-8",
        )

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "child issue #9 Git contract does not match frozen contract from child #10",
            result.stderr,
        )
        self.assertFalse((self.issue_dir / "42.json").exists())

    def test_issue_list_order_does_not_change_the_earliest_frontier_anchor(self) -> None:
        self.write_existing_issue(10, labels=["ready-for-agent"])
        split_contract = git_section(base_commit="3" * 40)
        self.write_existing_issue(
            11,
            body=existing_ticket_body(contract=split_contract),
            labels=["ready-for-agent"],
        )
        self.env["TEST_REVERSE_ISSUE_LIST"] = "1"

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "child issue #11 Git contract does not match frozen contract from child #10",
            result.stderr,
        )

    def test_parent_contract_drift_stops_before_provisioning_or_creation(self) -> None:
        self.write_existing_issue(10, labels=["ready-for-agent"])
        self.parent_body.write_text(
            f"## Problem Statement\n\nEdited parent.\n\n{git_section(base_commit='2' * 40)}\n",
            encoding="utf-8",
        )

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("parent issue #1 Git contract drifted", result.stderr)
        self.assertNotIn(
            "provision",
            [event.split(" ", 1)[0] for event in self.events()],
        )
        self.assertFalse((self.issue_dir / "42.json").exists())

    def test_existing_child_contract_split_stops_before_provisioning_or_creation(self) -> None:
        self.write_existing_issue(10, labels=["ready-for-agent"])
        split_contract = git_section(base_branch="origin/other", base_commit="3" * 40)
        self.write_existing_issue(11, body=existing_ticket_body(contract=split_contract))

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("child issue #11 Git contract does not match frozen contract", result.stderr)
        self.assertFalse((self.issue_dir / "42.json").exists())

    def test_malformed_existing_child_contract_is_a_contract_error(self) -> None:
        self.write_existing_issue(10, labels=["ready-for-agent"])
        malformed = existing_ticket_body(contract="## Git\n\n- Branch: `main`")
        self.write_existing_issue(11, body=malformed)

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("child issue #11 has an invalid Git contract", result.stderr)
        self.assertFalse((self.issue_dir / "42.json").exists())

    def test_provision_failure_does_not_create_tickets(self) -> None:
        self.env["TEST_FAIL_PROVISION"] = "1"

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            ["view", "list", "provision"],
            [json.loads(event[3:])[1] if event.startswith("gh ") else "provision" for event in self.events()],
        )

    def test_malformed_provision_result_stops_before_creating_issues(self) -> None:
        self.env["TEST_MALFORMED_PROVISION"] = "1"

        result = self.publish()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("incomplete", result.stderr)
        self.assertEqual(
            ["view", "list", "provision"],
            [json.loads(event[3:])[1] if event.startswith("gh ") else "provision" for event in self.events()],
        )

    def test_explicit_old_base_choice_is_forwarded_to_the_provisioner(self) -> None:
        result = self.publish("--allow-base-drift")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        provision_event = next(event for event in self.events() if event.startswith("provision "))
        self.assertIn("--allow-base-drift", json.loads(provision_event.removeprefix("provision ")))

    def test_partial_create_failure_leaves_every_created_ticket_unlabeled(self) -> None:
        self.env["TEST_FAIL_CREATE"] = "44"

        result = self.publish()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertTrue((self.issue_dir / "42.json").exists())
        self.assertTrue((self.issue_dir / "43.json").exists())
        self.assertFalse((self.issue_dir / "44.json").exists())
        self.assertEqual("OPEN", self.issue(42)["state"])
        self.assertEqual({}, self.labels())
        self.assertNotIn("edit", [json.loads(event[3:])[1] for event in self.events() if event.startswith("gh ")])

    def test_failed_readback_validation_leaves_the_set_unlabeled(self) -> None:
        self.env["TEST_MUTATE_READBACK"] = "44"

        result = self.publish()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertEqual({}, self.labels())
        self.assertNotIn("edit", [json.loads(event[3:])[1] for event in self.events() if event.startswith("gh ")])

    def test_label_and_rollback_failure_remains_blocked_by_the_publication_gate(self) -> None:
        self.env["TEST_FAIL_LABEL"] = "43"
        self.env["TEST_FAIL_REMOVE_LABEL"] = "44"

        result = self.publish()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual(["ready-for-agent"], self.labels().get("44", []))
        self.assertEqual("OPEN", self.issue(42)["state"])
        self.assertIn("## Blocked by\n\n- #42", str(self.issue(43)["body"]))
        self.assertIn("## Blocked by\n\n- #42", str(self.issue(44)["body"]))


if __name__ == "__main__":
    unittest.main()
