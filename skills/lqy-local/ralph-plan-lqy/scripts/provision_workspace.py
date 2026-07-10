#!/usr/bin/env python3
"""Provision the worktree and upstream declared by an issue Git contract."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from git_contract import GitContract, GitContractError, parse_git_contract


class ProvisionError(RuntimeError):
    """Raised when provisioning would violate the persistent Git contract."""


@dataclass(frozen=True)
class Worktree:
    path: Path
    head: str
    branch: str | None


@dataclass(frozen=True)
class WorktreeResult:
    path: str
    branch: str
    head: str
    upstream: str


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise OSError(f"git {' '.join(args)} failed: {detail}")
    return result


def parse_worktrees(output: str) -> list[Worktree]:
    worktrees: list[Worktree] = []
    for record in output.strip().split("\n\n"):
        fields: dict[str, str] = {}
        for line in record.splitlines():
            key, _, value = line.partition(" ")
            fields[key] = value
        if "worktree" not in fields or "HEAD" not in fields:
            raise OSError("git worktree list returned malformed porcelain output")
        branch_ref = fields.get("branch")
        branch = branch_ref.removeprefix("refs/heads/") if branch_ref else None
        worktrees.append(Worktree(path=Path(fields["worktree"]).resolve(), head=fields["HEAD"], branch=branch))
    if not worktrees:
        raise OSError("git worktree list returned no worktrees")
    return worktrees


def remote_for_contract(repo: Path, contract: GitContract) -> tuple[str, str]:
    remotes = git(repo, "remote").stdout.splitlines()
    matches = [remote for remote in remotes if contract.base_branch.startswith(f"{remote}/")]
    if matches:
        remote = max(matches, key=len)
        return remote, contract.base_branch[len(remote) + 1 :]
    if "origin" in remotes:
        return "origin", contract.base_branch
    if len(remotes) == 1:
        return remotes[0], contract.base_branch
    raise ProvisionError(f"cannot determine remote for base branch `{contract.base_branch}`")


def fetch_and_check_base(
    repo: Path,
    contract: GitContract,
    remote: str,
    remote_base: str,
    *,
    allow_base_drift: bool,
) -> None:
    git(repo, "fetch", remote, remote_base)
    resolved = git(repo, "rev-parse", "--verify", "FETCH_HEAD^{commit}").stdout.strip()
    if resolved.lower() != contract.base_commit.lower() and not allow_base_drift:
        raise ProvisionError(
            f"base drift: `{contract.base_branch}` is `{resolved}`, expected `{contract.base_commit}`"
        )


def remote_default_branch(repo: Path, remote: str) -> str:
    advertised = git(repo, "ls-remote", "--symref", remote, "HEAD").stdout.splitlines()
    prefix = "ref: refs/heads/"
    for line in advertised:
        if line.startswith(prefix) and line.endswith("\tHEAD"):
            return line[len(prefix) : -len("\tHEAD")]

    symbolic = git(repo, "symbolic-ref", "--quiet", "--short", f"refs/remotes/{remote}/HEAD", check=False)
    if symbolic.returncode == 0:
        prefix = f"{remote}/"
        value = symbolic.stdout.strip()
        if value.startswith(prefix):
            return value[len(prefix) :]
    raise ProvisionError(f"cannot determine default branch for remote `{remote}`")


def branch_slug(branch: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip(".-")
    if not slug:
        raise ProvisionError(f"branch `{branch}` cannot produce a worktree path")
    return slug


def target_path(primary: Worktree, branch: str) -> Path:
    return primary.path.parent / f"{primary.path.name}-{branch_slug(branch)}"


def local_branch_head(repo: Path, branch: str) -> str | None:
    branch_ref = f"refs/heads/{branch}"
    result = git(repo, "show-ref", "--verify", "--quiet", branch_ref, check=False)
    if result.returncode == 1:
        return None
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise OSError(f"git show-ref failed: {detail}")
    return git(repo, "rev-parse", "--verify", f"{branch_ref}^{{commit}}").stdout.strip()


def select_or_create_worktree(repo: Path, contract: GitContract, default_branch: str) -> Path:
    worktrees = parse_worktrees(git(repo, "worktree", "list", "--porcelain").stdout)
    primary = worktrees[0]
    if not primary.path.is_dir():
        raise ProvisionError(f"primary worktree path is missing: {primary.path}")
    if contract.branch == default_branch:
        if primary.branch != contract.branch:
            raise ProvisionError(
                f"default branch `{contract.branch}` is not attached to the primary worktree `{primary.path}`"
            )
        return primary.path

    matches = [worktree for worktree in worktrees if worktree.branch == contract.branch]
    if len(matches) > 1:
        raise ProvisionError(f"branch `{contract.branch}` is attached to multiple worktrees")
    if matches:
        if not matches[0].path.is_dir():
            raise ProvisionError(f"registered worktree path is missing: {matches[0].path}")
        return matches[0].path

    path = target_path(primary, contract.branch)
    if path.exists() or path.is_symlink():
        raise ProvisionError(f"target worktree path already exists: {path}")

    branch_head = local_branch_head(repo, contract.branch)
    if branch_head is not None and branch_head.lower() != contract.base_commit.lower():
        raise ProvisionError(
            f"branch `{contract.branch}` is `{branch_head}`, expected `{contract.base_commit}` before provisioning"
        )
    if branch_head is None:
        git(repo, "worktree", "add", "-b", contract.branch, str(path), contract.base_commit)
    else:
        git(repo, "worktree", "add", str(path), contract.branch)
    return path.resolve()


def validate_target(path: Path, contract: GitContract, remote: str) -> str:
    branch = git(path, "symbolic-ref", "--quiet", "--short", "HEAD").stdout.strip()
    if branch != contract.branch:
        raise ProvisionError(f"worktree `{path}` is on `{branch}`, expected `{contract.branch}`")
    head = git(path, "rev-parse", "HEAD").stdout.strip()
    if git(path, "status", "--porcelain").stdout:
        raise ProvisionError(f"worktree `{path}` is dirty")
    if head.lower() == contract.base_commit.lower():
        return head

    ancestor = git(path, "merge-base", "--is-ancestor", contract.base_commit, head, check=False)
    if ancestor.returncode == 1:
        raise ProvisionError(
            f"worktree `{path}` HEAD is `{head}`, which is not a descendant of `{contract.base_commit}`"
        )
    if ancestor.returncode != 0:
        raise OSError(ancestor.stderr.strip() or "git merge-base failed")

    expected_upstream = f"{remote}/{contract.branch}"
    upstream = git(
        path,
        "for-each-ref",
        "--format=%(upstream:short)",
        f"refs/heads/{contract.branch}",
    ).stdout.strip()
    if upstream != expected_upstream:
        raise ProvisionError(
            f"advanced branch `{contract.branch}` tracks `{upstream or '<none>'}`, expected `{expected_upstream}`"
        )
    remote_head = git(path, "ls-remote", "--heads", remote, f"refs/heads/{contract.branch}").stdout.strip()
    remote_commit = remote_head.split()[0] if remote_head else ""
    if remote_commit.lower() != head.lower():
        raise ProvisionError(
            f"advanced branch `{contract.branch}` is not synchronized with `{expected_upstream}`"
        )
    return head


def ensure_upstream(path: Path, contract: GitContract, remote: str, head: str) -> str:
    expected = f"{remote}/{contract.branch}"
    current = git(
        path,
        "for-each-ref",
        "--format=%(upstream:short)",
        f"refs/heads/{contract.branch}",
    ).stdout.strip()
    if current and current != expected:
        raise ProvisionError(
            f"branch `{contract.branch}` tracks `{current}`, expected `{expected}`"
        )

    remote_head = git(path, "ls-remote", "--heads", remote, f"refs/heads/{contract.branch}").stdout.strip()
    if remote_head:
        remote_commit = remote_head.split()[0]
        git(path, "fetch", remote, contract.branch)
        ancestor = git(path, "merge-base", "--is-ancestor", remote_commit, head, check=False)
        if ancestor.returncode == 1:
            raise ProvisionError(
                f"remote branch `{expected}` cannot fast-forward to `{head}`"
            )
        if ancestor.returncode != 0:
            raise OSError(ancestor.stderr.strip() or "git merge-base failed")

    git(path, "push", "--set-upstream", remote, contract.branch)
    return expected


def provision(repo: Path, contract: GitContract, *, allow_base_drift: bool = False) -> WorktreeResult:
    repo_root = Path(git(repo, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    remote, remote_base = remote_for_contract(repo_root, contract)
    fetch_and_check_base(
        repo_root,
        contract,
        remote,
        remote_base,
        allow_base_drift=allow_base_drift,
    )
    path = select_or_create_worktree(repo_root, contract, remote_default_branch(repo_root, remote))
    head = validate_target(path, contract, remote)
    upstream = ensure_upstream(path, contract, remote, head)
    return WorktreeResult(path=str(path), branch=contract.branch, head=head, upstream=upstream)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Provision a Git-bound branch worktree and upstream.")
    parser.add_argument("body_file", nargs="?", default="-", help="Issue body file, or `-` to read stdin.")
    parser.add_argument("--repo", default=".", help="Any path inside the common Git repository.")
    parser.add_argument(
        "--allow-base-drift",
        action="store_true",
        help="Continue from the recorded base only after the user explicitly chooses the old SHA.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        body = sys.stdin.read() if args.body_file == "-" else Path(args.body_file).read_text(encoding="utf-8")
        result = provision(
            Path(args.repo),
            parse_git_contract(body),
            allow_base_drift=args.allow_base_drift,
        )
    except (GitContractError, ProvisionError) as exc:
        print(f"PROVISION ERROR: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(asdict(result), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
