#!/usr/bin/env python3
"""Resolve and validate the Git contract for a new Ralph parent spec."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from git_contract import GitContract, GitContractError, is_valid_git_ref, parse_git_contract


class ResolutionError(RuntimeError):
    """Raised when repository state cannot produce a safe spec contract."""


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


def configured_remote(repo: Path, base_branch: str | None) -> tuple[str, str | None]:
    remotes = git(repo, "remote").stdout.splitlines()
    if not remotes:
        raise ResolutionError("cannot determine remote: repository has no remotes")
    if base_branch is not None:
        matches = [remote for remote in remotes if base_branch.startswith(f"{remote}/")]
        if not matches:
            raise ResolutionError(f"base branch `{base_branch}` does not name a configured remote")
        remote = max(matches, key=len)
        return remote, base_branch[len(remote) + 1 :]
    if "origin" in remotes:
        return "origin", None
    if len(remotes) == 1:
        return remotes[0], None
    raise ResolutionError("cannot determine remote: specify `Base branch` when multiple remotes exist")


def remote_default_branch(repo: Path, remote: str) -> str:
    advertised = git(repo, "ls-remote", "--symref", remote, "HEAD").stdout.splitlines()
    prefix = "ref: refs/heads/"
    for line in advertised:
        if line.startswith(prefix) and line.endswith("\tHEAD"):
            return line[len(prefix) : -len("\tHEAD")]

    symbolic = git(repo, "symbolic-ref", "--quiet", "--short", f"refs/remotes/{remote}/HEAD", check=False)
    if symbolic.returncode == 0:
        value = symbolic.stdout.strip()
        remote_prefix = f"{remote}/"
        if value.startswith(remote_prefix):
            return value[len(remote_prefix) :]
    raise ResolutionError(f"cannot determine default branch for remote `{remote}`")


def resolve_base_commit(repo: Path, remote: str, remote_base: str) -> str:
    git(repo, "fetch", remote, remote_base)
    return git(repo, "rev-parse", "--verify", "FETCH_HEAD^{commit}").stdout.strip()


def local_branch_head(repo: Path, branch: str) -> str | None:
    ref = f"refs/heads/{branch}"
    exists = git(repo, "show-ref", "--verify", "--quiet", ref, check=False)
    if exists.returncode == 1:
        return None
    if exists.returncode != 0:
        raise OSError(exists.stderr.strip() or "git show-ref failed")
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip()


def check_branch_collision(repo: Path, remote: str, branch: str, base_commit: str) -> None:
    head = local_branch_head(repo, branch)
    if head is not None and head.lower() != base_commit.lower():
        raise ResolutionError(
            f"branch collision: local branch `{branch}` is `{head}`, expected `{base_commit}`"
        )

    advertised = git(repo, "ls-remote", "--heads", remote, f"refs/heads/{branch}").stdout.strip()
    if not advertised:
        return
    remote_head = advertised.split()[0]
    if remote_head.lower() == base_commit.lower():
        return

    git(repo, "fetch", remote, branch)
    ancestor = git(repo, "merge-base", "--is-ancestor", remote_head, base_commit, check=False)
    if ancestor.returncode == 1:
        raise ResolutionError(
            f"remote branch collision: `{remote}/{branch}` at `{remote_head}` cannot fast-forward to `{base_commit}`"
        )
    if ancestor.returncode != 0:
        raise OSError(ancestor.stderr.strip() or "git merge-base failed")


def render_contract(contract: GitContract) -> str:
    return (
        "## Git\n\n"
        f"- Branch: `{contract.branch}`\n"
        f"- Base branch: `{contract.base_branch}`\n"
        f"- Base commit: `{contract.base_commit}`\n"
    )


def resolve(repo: Path, branch: str | None, base_branch: str | None) -> GitContract:
    repo_root = Path(git(repo, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    remote, explicit_remote_base = configured_remote(repo_root, base_branch)
    default_branch: str | None = None
    if branch is None or explicit_remote_base is None:
        default_branch = remote_default_branch(repo_root, remote)
    target_branch = branch if branch is not None else default_branch
    remote_base = explicit_remote_base if explicit_remote_base is not None else default_branch
    if target_branch is None or remote_base is None:
        raise ResolutionError("cannot resolve branch defaults")
    target_base_branch = base_branch or f"{remote}/{remote_base}"

    if not is_valid_git_ref(target_branch, branch=True):
        raise ResolutionError(f"invalid target branch `{target_branch}`")
    if not is_valid_git_ref(target_base_branch):
        raise ResolutionError(f"invalid base branch `{target_base_branch}`")

    base_commit = resolve_base_commit(repo_root, remote, remote_base)
    check_branch_collision(repo_root, remote, target_branch, base_commit)
    contract = GitContract(
        branch=target_branch,
        base_branch=target_base_branch,
        base_commit=base_commit,
    )
    return parse_git_contract(render_contract(contract), require_unique=True)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve the Git contract for a new Ralph parent spec.")
    parser.add_argument("--repo", default=".", help="Any path inside the target Git repository.")
    parser.add_argument("--branch", help="Explicit target branch; defaults to the remote default branch.")
    parser.add_argument("--base-branch", help="Explicit remote base ref, for example `origin/release`.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        contract = resolve(Path(args.repo), args.branch, args.base_branch)
    except (GitContractError, ResolutionError) as exc:
        print(f"RESOLUTION ERROR: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(asdict(contract), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
