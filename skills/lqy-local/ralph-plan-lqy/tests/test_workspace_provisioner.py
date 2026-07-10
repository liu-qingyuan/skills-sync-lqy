#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PROVISIONER = SKILL_ROOT / "scripts" / "provision_workspace.py"
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


class GitRepoFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.remote = self.root / "origin.git"
        self.repo = self.root / "project"

        run("git", "init", "--bare", "--initial-branch=main", str(self.remote))
        run("git", "clone", str(self.remote), str(self.repo))
        run("git", "config", "user.name", "Test User", cwd=self.repo)
        run("git", "config", "user.email", "test@example.com", cwd=self.repo)
        (self.repo / ".gitignore").write_text(".ralph/\n", encoding="utf-8")
        run("git", "add", ".gitignore", cwd=self.repo)
        run("git", "commit", "-m", "initial", cwd=self.repo)
        run("git", "push", "-u", "origin", "main", cwd=self.repo)
        self.base_commit = run("git", "rev-parse", "HEAD", cwd=self.repo)

    def contract_body(self, *, branch: str = "main") -> str:
        return (
            "## Git\n\n"
            f"- Branch: `{branch}`\n"
            "- Base branch: `origin/main`\n"
            f"- Base commit: `{self.base_commit}`\n"
        )

    def provision(self, *, branch: str = "main") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(PROVISIONER), "--repo", str(self.repo)],
            input=self.contract_body(branch=branch),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


class WorkspaceProvisionerCliTests(GitRepoFixture):

    def test_default_branch_reuses_primary_worktree(self) -> None:
        result = self.provision()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            {
                "branch": "main",
                "head": self.base_commit,
                "path": str(self.repo.resolve()),
                "upstream": "origin/main",
            },
            json.loads(result.stdout),
        )
        worktrees = run("git", "worktree", "list", "--porcelain", cwd=self.repo)
        self.assertEqual(1, worktrees.count("worktree "))

    def test_default_branch_is_not_created_as_a_sibling_worktree(self) -> None:
        run("git", "switch", "-c", "maintenance", cwd=self.repo)

        result = self.provision()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("default branch `main` is not attached to the primary worktree", result.stderr)
        self.assertFalse((self.root / "project-main").exists())

    def test_missing_branch_creates_deterministic_worktree_and_upstream(self) -> None:
        result = self.provision(branch="feature/alpha")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        expected_path = (self.root / "project-feature-alpha").resolve()
        self.assertEqual(
            {
                "branch": "feature/alpha",
                "head": self.base_commit,
                "path": str(expected_path),
                "upstream": "origin/feature/alpha",
            },
            json.loads(result.stdout),
        )
        self.assertEqual("feature/alpha", run("git", "branch", "--show-current", cwd=expected_path))
        self.assertEqual(
            self.base_commit,
            run("git", "ls-remote", "--heads", str(self.remote), "refs/heads/feature/alpha").split()[0],
        )

    def test_registered_branch_reuses_its_exact_worktree_path(self) -> None:
        custom_path = (self.root / "custom-location").resolve()
        run(
            "git",
            "worktree",
            "add",
            "-b",
            "feature/custom",
            str(custom_path),
            self.base_commit,
            cwd=self.repo,
        )

        result = self.provision(branch="feature/custom")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(str(custom_path), json.loads(result.stdout)["path"])

    def test_existing_unbound_branch_is_added_as_a_worktree(self) -> None:
        run("git", "branch", "feature/existing", self.base_commit, cwd=self.repo)

        result = self.provision(branch="feature/existing")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            str((self.root / "project-feature-existing").resolve()),
            json.loads(result.stdout)["path"],
        )

    def test_base_drift_stops_before_provisioning(self) -> None:
        (self.repo / "change.txt").write_text("remote advanced\n", encoding="utf-8")
        run("git", "add", "change.txt", cwd=self.repo)
        run("git", "commit", "-m", "advance base", cwd=self.repo)
        run("git", "push", "origin", "main", cwd=self.repo)

        result = self.provision(branch="feature/drifted")

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("base drift", result.stderr)
        self.assertFalse((self.root / "project-feature-drifted").exists())

    def test_occupied_deterministic_path_is_not_overwritten(self) -> None:
        occupied = self.root / "project-feature-occupied"
        occupied.mkdir()
        marker = occupied / "keep.txt"
        marker.write_text("keep\n", encoding="utf-8")

        result = self.provision(branch="feature/occupied")

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("target worktree path already exists", result.stderr)
        self.assertEqual("keep\n", marker.read_text(encoding="utf-8"))

    def test_dirty_target_worktree_is_rejected(self) -> None:
        (self.repo / "untracked.txt").write_text("dirty\n", encoding="utf-8")

        result = self.provision()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("is dirty", result.stderr)

    def test_unexpected_target_head_is_rejected(self) -> None:
        (self.repo / "local.txt").write_text("local commit\n", encoding="utf-8")
        run("git", "add", "local.txt", cwd=self.repo)
        run("git", "commit", "-m", "local advance", cwd=self.repo)

        result = self.provision()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("HEAD is", result.stderr)
        self.assertEqual("origin/main", run("git", "rev-parse", "--abbrev-ref", "main@{upstream}", cwd=self.repo))

    def test_unexpected_upstream_is_not_replaced(self) -> None:
        run("git", "remote", "add", "backup", str(self.remote), cwd=self.repo)
        run("git", "fetch", "backup", "main", cwd=self.repo)
        run("git", "branch", "--set-upstream-to=backup/main", "main", cwd=self.repo)

        result = self.provision()

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("tracks `backup/main`, expected `origin/main`", result.stderr)
        self.assertEqual("backup/main", run("git", "rev-parse", "--abbrev-ref", "main@{upstream}", cwd=self.repo))


class LockedRalphRunnerCliTests(GitRepoFixture):
    def wait_for(self, path: Path) -> None:
        deadline = time.monotonic() + 5
        while not path.exists():
            if time.monotonic() >= deadline:
                self.fail(f"timed out waiting for {path}")
            time.sleep(0.01)

    def start_holder(self, worktree: Path, marker: Path, release: Path) -> subprocess.Popen[str]:
        child = (
            "import pathlib,time; "
            f"pathlib.Path({str(marker)!r}).write_text('ready'); "
            f"release=pathlib.Path({str(release)!r}); "
            "deadline=time.monotonic()+10; "
            "\nwhile not release.exists() and time.monotonic()<deadline: time.sleep(0.01)"
        )
        return subprocess.Popen(
            [
                "python3",
                str(LOCKED_RUNNER),
                "--worktree",
                str(worktree),
                "--",
                "python3",
                "-c",
                child,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def test_second_runner_for_same_worktree_is_rejected(self) -> None:
        marker = self.root / "holder-ready"
        release = self.root / "release-holder"
        holder = self.start_holder(self.repo, marker, release)
        self.addCleanup(lambda: holder.poll() is None and holder.kill())
        self.wait_for(marker)

        contender = subprocess.run(
            [
                "python3",
                str(LOCKED_RUNNER),
                "--worktree",
                str(self.repo),
                "--",
                "python3",
                "-c",
                "raise SystemExit(99)",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(2, contender.returncode, contender.stdout + contender.stderr)
        self.assertIn("LOCK BUSY", contender.stderr)
        release.write_text("release\n", encoding="utf-8")
        stdout, stderr = holder.communicate(timeout=5)
        self.assertEqual(0, holder.returncode, stdout + stderr)

    def test_different_worktrees_can_hold_locks_concurrently(self) -> None:
        other = (self.root / "other-worktree").resolve()
        run("git", "worktree", "add", "-b", "feature/other", str(other), self.base_commit, cwd=self.repo)
        release = self.root / "release-both"
        first_marker = self.root / "first-ready"
        second_marker = self.root / "second-ready"
        first = self.start_holder(self.repo, first_marker, release)
        second = self.start_holder(other, second_marker, release)
        self.addCleanup(lambda: first.poll() is None and first.kill())
        self.addCleanup(lambda: second.poll() is None and second.kill())

        self.wait_for(first_marker)
        self.wait_for(second_marker)
        self.assertIsNone(first.poll())
        self.assertIsNone(second.poll())

        release.write_text("release\n", encoding="utf-8")
        first_stdout, first_stderr = first.communicate(timeout=5)
        second_stdout, second_stderr = second.communicate(timeout=5)
        self.assertEqual(0, first.returncode, first_stdout + first_stderr)
        self.assertEqual(0, second.returncode, second_stdout + second_stderr)

    def test_child_runs_in_worktree_and_exit_code_is_forwarded(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(LOCKED_RUNNER),
                "--worktree",
                str(self.repo),
                "--",
                "python3",
                "-c",
                "import pathlib; print(pathlib.Path.cwd()); raise SystemExit(7)",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.assertEqual(7, result.returncode, result.stdout + result.stderr)
        self.assertEqual(str(self.repo.resolve()), result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
