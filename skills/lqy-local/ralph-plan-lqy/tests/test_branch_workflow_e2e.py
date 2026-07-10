#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROVISIONER = SKILL_ROOT / "scripts" / "provision_workspace.py"
ELIGIBILITY_GATE = SKILL_ROOT / "scripts" / "check_ready_issue_unblocked.py"
LOCKED_RUNNER = SKILL_ROOT / "scripts" / "run_locked_ralph.py"


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


class BranchWorkflowEndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.remote = self.root / "origin.git"
        self.repo = self.root / "project"
        self.bin_dir = self.root / "bin"
        self.bin_dir.mkdir()

        run("git", "init", "--bare", "--initial-branch=main", str(self.remote))
        run("git", "clone", str(self.remote), str(self.repo))
        run("git", "config", "user.name", "Test User", cwd=self.repo)
        run("git", "config", "user.email", "test@example.com", cwd=self.repo)
        (self.repo / ".gitignore").write_text(".ralph/\n", encoding="utf-8")
        run("git", "add", ".gitignore", cwd=self.repo)
        run("git", "commit", "-m", "initial", cwd=self.repo)
        run("git", "push", "-u", "origin", "main", cwd=self.repo)
        self.base_commit = run("git", "rev-parse", "HEAD", cwd=self.repo)

        self.issues_file = self.root / "issues.json"
        self.gh_log = self.root / "gh-calls.jsonl"
        self._write_gh_stub()

    def contract_body(self, branch: str) -> str:
        return textwrap.dedent(
            f"""
            ## Git

            - Branch: `{branch}`
            - Base branch: `origin/main`
            - Base commit: `{self.base_commit}`
            """
        ).strip()

    def spec_body(self, branch: str) -> str:
        return (
            "## Problem Statement\n\nExercise one Git-bound branch worker.\n\n"
            "## User Stories\n\n1. Run an isolated worker.\n\n"
            "## Implementation Decisions\n\nUse one branch and one worktree.\n\n"
            f"{self.contract_body(branch)}"
        )

    def ticket_body(self, branch: str, parent: int, blocked_by: str) -> str:
        return (
            f"## Parent\n\n#{parent}\n\n"
            "## What to build\n\nExercise the branch-local Ralph workflow.\n\n"
            f"## Blocked by\n\n{blocked_by}\n\n"
            f"{self.contract_body(branch)}"
        )

    def issue(
        self,
        number: int,
        branch: str,
        *,
        state: str = "OPEN",
        blocked_by: str = "None - can start immediately",
        labels: list[str] | None = None,
    ) -> dict[str, object]:
        return {
            "number": number,
            "title": f"Ticket {number}",
            "state": state,
            "labels": [
                {"name": label}
                for label in (["ready-for-agent"] if labels is None else labels)
            ],
            "assignees": [{"login": "must-not-be-read"}],
            "body": self.ticket_body(branch, 10 if "alpha" in branch else 19, blocked_by),
        }

    def spec_issue(self, number: int, branch: str) -> dict[str, object]:
        return {
            "number": number,
            "title": f"Spec: {branch}",
            "state": "OPEN",
            "labels": [{"name": "ready-for-agent"}],
            "body": self.spec_body(branch),
        }

    def write_issues(self, issues: dict[int, dict[str, object]]) -> None:
        self.issues_file.write_text(
            json.dumps({str(number): issue for number, issue in issues.items()}),
            encoding="utf-8",
        )

    def _write_gh_stub(self) -> None:
        stub = self.bin_dir / "gh"
        stub.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                import json
                import os
                import pathlib
                import sys

                args = sys.argv[1:]
                log = pathlib.Path(os.environ["GH_STUB_LOG"])
                with log.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(args) + "\\n")
                issues = json.loads(pathlib.Path(os.environ["GH_STUB_ISSUES"]).read_text(encoding="utf-8"))
                if args[:2] == ["issue", "list"]:
                    ready = [
                        issue
                        for issue in issues.values()
                        if issue["state"] == "OPEN"
                        and any(label["name"] == "ready-for-agent" for label in issue["labels"])
                    ]
                    for issue in sorted(ready, key=lambda item: item["number"]):
                        print(json.dumps({key: issue[key] for key in ("number", "title", "body")}))
                    raise SystemExit(0)
                if len(args) < 3 or args[:2] != ["issue", "view"]:
                    print("unsupported gh invocation", file=sys.stderr)
                    raise SystemExit(1)
                issue = issues.get(args[2])
                if issue is None:
                    print(f"issue {args[2]} not found", file=sys.stderr)
                    raise SystemExit(1)
                print(json.dumps(issue))
                """
            ),
            encoding="utf-8",
        )
        stub.chmod(0o755)

    def environment(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PATH"] = f"{self.bin_dir}{os.pathsep}{env['PATH']}"
        env["GH_STUB_ISSUES"] = str(self.issues_file)
        env["GH_STUB_LOG"] = str(self.gh_log)
        return env

    def provision(self, branch: str) -> Path:
        result = subprocess.run(
            [sys.executable, str(PROVISIONER), "--repo", str(self.repo)],
            input=self.spec_body(branch),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return Path(json.loads(result.stdout)["path"])

    def gate(self, worktree: Path, issue_number: int) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ELIGIBILITY_GATE), str(issue_number)],
            cwd=worktree,
            env=self.environment(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def wait_for(self, path: Path) -> None:
        deadline = time.monotonic() + 10
        while not path.exists():
            if time.monotonic() >= deadline:
                self.fail(f"timed out waiting for {path}")
            time.sleep(0.01)

    def stop_worker(self, worker: subprocess.Popen[str]) -> None:
        if worker.poll() is None:
            worker.terminate()
        try:
            worker.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            worker.kill()
            worker.communicate(timeout=5)

    def start_worker(
        self,
        worktree: Path,
        marker: Path,
        release: Path,
    ) -> subprocess.Popen[str]:
        probe = self.root / "worker_probe.py"
        if not probe.exists():
            probe.write_text(
                textwrap.dedent(
                    """
                    import json
                    import os
                    import pathlib
                    import subprocess
                    import sys
                    import time

                    root = pathlib.Path.cwd()
                    branch = subprocess.run(
                        ["git", "branch", "--show-current"],
                        check=True,
                        text=True,
                        stdout=subprocess.PIPE,
                    ).stdout.strip()
                    backlog = subprocess.run(
                        [
                            "gh", "issue", "list",
                            "--label", "ready-for-agent",
                            "--state", "open",
                            "--json", "number,title,body",
                            "--jq", "sort_by(.number)[] | {number,title,body}",
                        ],
                        check=False,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    if backlog.returncode != 0:
                        print(backlog.stderr, file=sys.stderr, end="")
                        raise SystemExit(1)
                    results = []
                    selected = None
                    for issue in (json.loads(line) for line in backlog.stdout.splitlines() if line):
                        number = issue["number"]
                        result = subprocess.run(
                            [sys.executable, os.environ["ELIGIBILITY_GATE"], str(number)],
                            cwd=root,
                            env=os.environ.copy(),
                            text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        results.append({"number": number, "returncode": result.returncode})
                        if result.returncode == 0:
                            selected = number
                            break
                        if result.returncode in (1, 3):
                            pathlib.Path(os.environ["WORKER_MARKER"]).write_text(
                                json.dumps({
                                    "branch": branch,
                                    "outcome": "error",
                                    "returncode": result.returncode,
                                    "results": results,
                                }),
                                encoding="utf-8",
                            )
                            print(result.stderr, file=sys.stderr, end="")
                            raise SystemExit(result.returncode)

                    if selected is None:
                        pathlib.Path(os.environ["WORKER_MARKER"]).write_text(
                            json.dumps({"branch": branch, "outcome": "complete", "results": results}),
                            encoding="utf-8",
                        )
                        print("<ralph-finished-no-ready-issues/>")
                        raise SystemExit(0)

                    slug = branch.replace("/", "-")
                    state_file = root / ".ralph" / "branch-state.txt"
                    state_file.write_text(branch + "\\n", encoding="utf-8")
                    committed = root / f"committed-{slug}.txt"
                    committed.write_text(f"selected={selected}\\n", encoding="utf-8")
                    subprocess.run(["git", "add", committed.name], check=True)
                    subprocess.run(["git", "commit", "-m", f"worker {branch}"], check=True)
                    subprocess.run(["git", "push"], check=True)
                    (root / f"dirty-{slug}.txt").write_text(branch + "\\n", encoding="utf-8")
                    pathlib.Path(os.environ["WORKER_MARKER"]).write_text(
                        json.dumps({
                            "branch": branch,
                            "outcome": "selected",
                            "selected": selected,
                            "results": results,
                        }),
                        encoding="utf-8",
                    )
                    if release_value := os.environ.get("WORKER_RELEASE"):
                        release = pathlib.Path(release_value)
                        deadline = time.monotonic() + 15
                        while not release.exists() and time.monotonic() < deadline:
                            time.sleep(0.01)
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

        env = self.environment()
        env["ELIGIBILITY_GATE"] = str(ELIGIBILITY_GATE)
        env["WORKER_MARKER"] = str(marker)
        env["WORKER_RELEASE"] = str(release)
        return subprocess.Popen(
            [
                sys.executable,
                str(LOCKED_RUNNER),
                "--worktree",
                str(worktree),
                "--",
                sys.executable,
                str(probe),
            ],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def run_worker(self, worktree: Path, marker: Path) -> subprocess.CompletedProcess[str]:
        probe = self.root / "worker_probe.py"
        env = self.environment()
        env["ELIGIBILITY_GATE"] = str(ELIGIBILITY_GATE)
        env["WORKER_MARKER"] = str(marker)
        return subprocess.run(
            [
                sys.executable,
                str(LOCKED_RUNNER),
                "--worktree",
                str(worktree),
                "--",
                sys.executable,
                str(probe),
            ],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_two_git_bound_branch_workers_are_isolated_end_to_end(self) -> None:
        alpha = "feature/alpha"
        beta = "feature/beta"
        alpha_worktree = self.provision(alpha)
        beta_worktree = self.provision(beta)
        issues = {
            10: self.spec_issue(10, alpha),
            11: self.issue(11, alpha),
            12: self.issue(12, alpha),
            19: self.spec_issue(19, beta),
            20: self.issue(20, beta, labels=[]),
            21: self.issue(21, beta, blocked_by="- #20"),
            22: self.issue(22, beta),
            30: self.issue(30, "feature/other"),
        }
        self.write_issues(issues)

        release = self.root / "release-workers"
        alpha_marker = self.root / "alpha-ready.json"
        beta_marker = self.root / "beta-ready.json"
        alpha_worker = self.start_worker(alpha_worktree, alpha_marker, release)
        beta_worker = self.start_worker(beta_worktree, beta_marker, release)
        self.addCleanup(self.stop_worker, alpha_worker)
        self.addCleanup(self.stop_worker, beta_worker)
        self.wait_for(alpha_marker)
        self.wait_for(beta_marker)

        alpha_result = json.loads(alpha_marker.read_text(encoding="utf-8"))
        beta_result = json.loads(beta_marker.read_text(encoding="utf-8"))
        self.assertEqual(11, alpha_result["selected"], alpha_result)
        self.assertEqual(
            [{"number": 10, "returncode": 2}, {"number": 11, "returncode": 0}],
            alpha_result["results"],
        )
        self.assertEqual(
            [
                {"number": 10, "returncode": 2},
                {"number": 11, "returncode": 2},
                {"number": 12, "returncode": 2},
                {"number": 19, "returncode": 2},
                {"number": 21, "returncode": 2},
                {"number": 22, "returncode": 0},
            ],
            beta_result["results"],
        )
        self.assertIsNone(alpha_worker.poll())
        self.assertIsNone(beta_worker.poll())

        same_worktree = subprocess.run(
            [
                sys.executable,
                str(LOCKED_RUNNER),
                "--worktree",
                str(alpha_worktree),
                "--",
                sys.executable,
                "-c",
                "raise SystemExit(99)",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(2, same_worktree.returncode, same_worktree.stdout + same_worktree.stderr)
        self.assertIn("LOCK BUSY", same_worktree.stderr)

        release.write_text("release\n", encoding="utf-8")
        alpha_stdout, alpha_stderr = alpha_worker.communicate(timeout=10)
        beta_stdout, beta_stderr = beta_worker.communicate(timeout=10)
        self.assertEqual(0, alpha_worker.returncode, alpha_stdout + alpha_stderr)
        self.assertEqual(0, beta_worker.returncode, beta_stdout + beta_stderr)

        for worktree, own, other in (
            (alpha_worktree, "feature-alpha", "feature-beta"),
            (beta_worktree, "feature-beta", "feature-alpha"),
        ):
            self.assertTrue((worktree / f"committed-{own}.txt").exists())
            self.assertFalse((worktree / f"committed-{other}.txt").exists())
            self.assertFalse((worktree / f"dirty-{other}.txt").exists())
            self.assertEqual(
                f"{own.replace('-', '/', 1)}\n",
                (worktree / ".ralph" / "branch-state.txt").read_text(encoding="utf-8"),
            )
            status = run("git", "status", "--short", cwd=worktree)
            self.assertEqual(f"?? dirty-{own}.txt", status)
            upstream = run("git", "rev-parse", "--abbrev-ref", "@{upstream}", cwd=worktree)
            self.assertEqual(f"origin/{own.replace('-', '/', 1)}", upstream)
            self.assertEqual(
                run("git", "rev-parse", "HEAD", cwd=worktree),
                run("git", "rev-parse", "@{upstream}", cwd=worktree),
            )
            (worktree / f"dirty-{own}.txt").unlink()
            self.assertEqual("", run("git", "status", "--short", cwd=worktree))

        issues[11]["state"] = "CLOSED"
        issues[12]["state"] = "CLOSED"
        issues[22]["state"] = "CLOSED"
        self.write_issues(issues)
        alpha_completion = self.run_worker(alpha_worktree, self.root / "alpha-complete.json")
        beta_completion = self.run_worker(beta_worktree, self.root / "beta-complete.json")
        self.assertEqual(0, alpha_completion.returncode, alpha_completion.stdout + alpha_completion.stderr)
        self.assertEqual("<ralph-finished-no-ready-issues/>", alpha_completion.stdout.strip())
        self.assertEqual(0, beta_completion.returncode, beta_completion.stdout + beta_completion.stderr)
        self.assertEqual("<ralph-finished-no-ready-issues/>", beta_completion.stdout.strip())

        malformed = self.issue(40, alpha)
        malformed["body"] = str(malformed["body"]).replace(self.base_commit, "not-a-sha")
        issues[40] = malformed
        self.write_issues(issues)
        contract_error = self.run_worker(alpha_worktree, self.root / "alpha-contract-error.json")
        self.assertEqual(3, contract_error.returncode, contract_error.stdout + contract_error.stderr)
        self.assertIn("CONTRACT ERROR", contract_error.stderr)

        gh_calls = [json.loads(line) for line in self.gh_log.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(gh_calls)
        self.assertTrue(all("assignees" not in " ".join(call) for call in gh_calls))

if __name__ == "__main__":
    unittest.main()
