from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
RESOLVER = SKILL_DIR / "scripts" / "resolve_spec_git.py"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result


class SpecGitResolverCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.remote = self.root / "remote.git"
        self.repo = self.root / "project"
        run("git", "init", "--bare", str(self.remote), cwd=self.root)
        run("git", "init", "-b", "main", str(self.repo), cwd=self.root)
        run("git", "config", "user.name", "Test User", cwd=self.repo)
        run("git", "config", "user.email", "test@example.com", cwd=self.repo)
        (self.repo / "README.md").write_text("base\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=self.repo)
        run("git", "commit", "-m", "base", cwd=self.repo)
        self.main_commit = run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        run("git", "remote", "add", "origin", str(self.remote), cwd=self.repo)
        run("git", "push", "-u", "origin", "main", cwd=self.repo)
        run("git", "symbolic-ref", "HEAD", "refs/heads/main", cwd=self.remote)

    def resolve(self, *args: str, repo: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(RESOLVER), "--repo", str(repo or self.repo), *args],
            text=True,
            capture_output=True,
        )

    def test_default_contract_uses_the_branch_attached_to_the_requested_worktree(self) -> None:
        worktree = self.root / "project-feature"
        run("git", "worktree", "add", "-b", "feature/spec", str(worktree), "main", cwd=self.repo)

        result = self.resolve(repo=worktree)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            {
                "base_branch": "origin/main",
                "base_commit": self.main_commit,
                "branch": "feature/spec",
            },
            json.loads(result.stdout),
        )

    def test_explicit_branch_and_base_branch_override_defaults(self) -> None:
        run("git", "checkout", "-b", "release", cwd=self.repo)
        (self.repo / "release.txt").write_text("release\n", encoding="utf-8")
        run("git", "add", "release.txt", cwd=self.repo)
        run("git", "commit", "-m", "release base", cwd=self.repo)
        release_commit = run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        run("git", "push", "origin", "release", cwd=self.repo)

        result = self.resolve("--branch", "feature/spec", "--base-branch", "origin/release")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            {
                "base_branch": "origin/release",
                "base_commit": release_commit,
                "branch": "feature/spec",
            },
            json.loads(result.stdout),
        )

    def test_current_branch_upstream_becomes_the_default_base_branch(self) -> None:
        run("git", "checkout", "-b", "release", cwd=self.repo)
        (self.repo / "release.txt").write_text("release\n", encoding="utf-8")
        run("git", "add", "release.txt", cwd=self.repo)
        run("git", "commit", "-m", "release base", cwd=self.repo)
        release_commit = run("git", "rev-parse", "HEAD", cwd=self.repo).stdout.strip()
        run("git", "push", "-u", "origin", "release", cwd=self.repo)

        result = self.resolve()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            {
                "base_branch": "origin/release",
                "base_commit": release_commit,
                "branch": "release",
            },
            json.loads(result.stdout),
        )

    def test_local_branch_upstream_falls_back_to_the_remote_default(self) -> None:
        run("git", "checkout", "-b", "feature/local-upstream", cwd=self.repo)
        run("git", "branch", "--set-upstream-to=main", cwd=self.repo)

        result = self.resolve()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(
            {
                "base_branch": "origin/main",
                "base_commit": self.main_commit,
                "branch": "feature/local-upstream",
            },
            json.loads(result.stdout),
        )

    def test_fully_explicit_contract_does_not_require_remote_default(self) -> None:
        run("git", "update-ref", "--no-deref", "HEAD", self.main_commit, cwd=self.remote)

        result = self.resolve("--branch", "feature/spec", "--base-branch", "origin/main")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("feature/spec", json.loads(result.stdout)["branch"])

    def test_detached_checkout_falls_back_to_the_remote_default_branch(self) -> None:
        run("git", "checkout", "--detach", self.main_commit, cwd=self.repo)

        result = self.resolve()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("main", json.loads(result.stdout)["branch"])

    def test_existing_explicit_branch_at_another_commit_is_a_collision(self) -> None:
        run("git", "checkout", "-b", "feature/spec", cwd=self.repo)
        (self.repo / "collision.txt").write_text("collision\n", encoding="utf-8")
        run("git", "add", "collision.txt", cwd=self.repo)
        run("git", "commit", "-m", "collision", cwd=self.repo)
        run("git", "checkout", "main", cwd=self.repo)

        result = self.resolve("--branch", "feature/spec")

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("branch collision", result.stderr)

    def test_existing_remote_branch_that_cannot_fast_forward_to_base_is_a_collision(self) -> None:
        run("git", "checkout", "-b", "feature/remote-collision", cwd=self.repo)
        (self.repo / "remote-collision.txt").write_text("collision\n", encoding="utf-8")
        run("git", "add", "remote-collision.txt", cwd=self.repo)
        run("git", "commit", "-m", "remote collision", cwd=self.repo)
        run("git", "push", "origin", "feature/remote-collision", cwd=self.repo)
        run("git", "checkout", "main", cwd=self.repo)
        run("git", "branch", "-D", "feature/remote-collision", cwd=self.repo)

        result = self.resolve("--branch", "feature/remote-collision")

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("remote branch collision", result.stderr)

    def test_repository_without_remote_stops(self) -> None:
        isolated = self.root / "isolated"
        run("git", "init", "-b", "main", str(isolated), cwd=self.root)
        run("git", "config", "user.name", "Test User", cwd=isolated)
        run("git", "config", "user.email", "test@example.com", cwd=isolated)
        (isolated / "README.md").write_text("isolated\n", encoding="utf-8")
        run("git", "add", "README.md", cwd=isolated)
        run("git", "commit", "-m", "isolated", cwd=isolated)

        result = self.resolve(repo=isolated)

        self.assertEqual(3, result.returncode, result.stdout + result.stderr)
        self.assertIn("cannot determine remote", result.stderr)


if __name__ == "__main__":
    unittest.main()
