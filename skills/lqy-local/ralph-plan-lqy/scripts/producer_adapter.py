#!/usr/bin/env python3
"""Repository-bound command adapter shared by Ralph-ready issue producers."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FULL_SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")


class ProducerContractError(ValueError):
    """Raised when the requested publication violates a persistent contract."""


class ProducerToolError(OSError):
    """Raised when an external command or its output protocol is unusable."""


@dataclass(frozen=True)
class GitContract:
    branch: str
    base_branch: str
    base_commit: str


@dataclass(frozen=True)
class IssueSnapshot:
    number: int
    title: str
    body: str
    state: str
    labels: frozenset[str]


@dataclass(frozen=True)
class WorktreeResult:
    path: str
    branch: str
    head: str
    upstream: str


class ProducerToolAdapter:
    """Hide repository context, command execution, and JSON protocol validation."""

    def __init__(self, repository: Path, *, skill_dir: Path) -> None:
        resolved = repository.expanduser().resolve()
        if not resolved.is_dir():
            raise ProducerContractError(f"target repository is not a directory: {resolved}")
        repository_result = subprocess.run(
            ["git", "-C", str(resolved), "rev-parse", "--show-toplevel"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if repository_result.returncode != 0:
            raise ProducerContractError(f"target repository is not a Git repository: {resolved}")
        repository_root = Path(repository_result.stdout.strip()).resolve()
        remote_result = subprocess.run(
            ["git", "-C", str(repository_root), "remote"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if remote_result.returncode != 0:
            detail = remote_result.stderr.strip() or remote_result.stdout.strip()
            raise ProducerToolError(f"cannot inspect target repository remotes: {detail or 'git remote failed'}")
        remotes = remote_result.stdout.splitlines()
        if not remotes:
            raise ProducerContractError(f"target repository has no configured remote: {repository_root}")
        if not any(self._remote_url(repository_root, remote) for remote in remotes):
            raise ProducerContractError(f"target repository has no resolvable remote: {repository_root}")
        self.repository = repository_root
        self.skill_dir = skill_dir.expanduser().resolve()

    def run(
        self,
        command: list[str],
        *,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=self.repository,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def run_json(
        self,
        command: list[str],
        *,
        source: str,
        input_text: str | None = None,
    ) -> dict[str, Any]:
        result = self.run(command, input_text=input_text)
        if result.returncode == 3:
            detail = result.stderr.strip() or result.stdout.strip() or f"{source} failed"
            raise ProducerContractError(detail)
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
            raise ProducerToolError(f"{source} failed: {detail}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ProducerToolError(f"{source} returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ProducerToolError(f"{source} returned a non-object JSON value")
        return payload

    def gh(self, *args: str) -> str:
        environment = os.environ.copy()
        environment.pop("GH_REPO", None)
        result = subprocess.run(
            ["gh", *args],
            cwd=self.repository,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
            raise ProducerToolError(f"gh {' '.join(args)} failed: {detail}")
        return result.stdout

    def view_issue(self, number: int) -> IssueSnapshot:
        source = f"gh issue view {number}"
        payload = self._gh_json(
            "issue",
            "view",
            str(number),
            "--json",
            "number,title,body,state,labels",
            source=source,
        )
        if not isinstance(payload, dict):
            raise ProducerToolError(f"{source} returned a non-object JSON value")
        return self._issue_snapshot(payload, source=source)

    def list_issues(self) -> tuple[IssueSnapshot, ...]:
        source = "gh issue list"
        payload = self._gh_json(
            "issue",
            "list",
            "--state",
            "all",
            "--limit",
            "100000",
            "--json",
            "number,title,body,state,labels",
            source=source,
        )
        if not isinstance(payload, list):
            raise ProducerToolError(f"{source} returned a non-array JSON value")
        return tuple(
            self._issue_snapshot(item, source=f"{source} entry {index}")
            for index, item in enumerate(payload, start=1)
        )

    @staticmethod
    def _remote_url(repository: Path, remote: str) -> str | None:
        result = subprocess.run(
            ["git", "-C", str(repository), "remote", "get-url", remote],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    def shared_script(self, name: str) -> Path:
        script = self.skill_dir / "scripts" / name
        if not script.is_file():
            raise ProducerContractError(f"required ralph-plan-lqy script is not installed: {script}")
        return script

    def validate_git_contract(self, body: str) -> GitContract:
        source = "shared Git contract validator"
        payload = self.run_json(
            [sys.executable, str(self.shared_script("git_contract.py")), "--require-unique"],
            source=source,
            input_text=body,
        )
        return self._git_contract(payload, source=source)

    def resolve_git_contract(
        self,
        branch: str | None,
        base_branch: str | None,
    ) -> GitContract:
        source = "shared Git contract resolver"
        command = [
            sys.executable,
            str(self.shared_script("resolve_spec_git.py")),
            "--repo",
            str(self.repository),
        ]
        if branch is not None:
            command.extend(["--branch", branch])
        if base_branch is not None:
            command.extend(["--base-branch", base_branch])
        return self._git_contract(self.run_json(command, source=source), source=source)

    def provision_workspace(
        self,
        body: str,
        *,
        expected_branch: str,
        allow_base_drift: bool = False,
    ) -> WorktreeResult:
        source = "workspace provisioner"
        command = [
            sys.executable,
            str(self.shared_script("provision_workspace.py")),
            "--repo",
            str(self.repository),
        ]
        if allow_base_drift:
            command.append("--allow-base-drift")
        payload = self.run_json(command, source=source, input_text=body)
        fields = self._strings(payload, ("path", "branch", "head", "upstream"), source=source)
        if fields["branch"] != expected_branch:
            raise ProducerToolError(
                f"{source} returned branch `{fields['branch']}`, expected `{expected_branch}`"
            )
        if not Path(fields["path"]).is_absolute():
            raise ProducerToolError(f"{source} returned a non-absolute worktree path")
        if FULL_SHA_PATTERN.fullmatch(fields["head"]) is None:
            raise ProducerToolError(f"{source} returned an invalid HEAD commit")
        return WorktreeResult(**fields)

    def _git_contract(self, payload: dict[str, Any], *, source: str) -> GitContract:
        fields = self._strings(payload, ("branch", "base_branch", "base_commit"), source=source)
        if FULL_SHA_PATTERN.fullmatch(fields["base_commit"]) is None:
            raise ProducerToolError(f"{source} returned an invalid base commit")
        return GitContract(**fields)

    def _gh_json(self, *args: str, source: str) -> Any:
        output = self.gh(*args)
        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise ProducerToolError(f"{source} returned invalid JSON") from exc

    @staticmethod
    def _issue_snapshot(payload: Any, *, source: str) -> IssueSnapshot:
        if not isinstance(payload, dict):
            raise ProducerToolError(f"{source} is not an object")
        number = payload.get("number")
        title = payload.get("title")
        body = payload.get("body")
        state = payload.get("state")
        labels = payload.get("labels")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            raise ProducerToolError(f"{source} returned an invalid issue number")
        if not all(isinstance(value, str) for value in (title, body, state)):
            raise ProducerToolError(f"{source} returned invalid issue fields")
        if not isinstance(labels, list) or not all(
            isinstance(label, dict) and isinstance(label.get("name"), str) and label["name"]
            for label in labels
        ):
            raise ProducerToolError(f"{source} returned invalid issue labels")
        return IssueSnapshot(
            number=number,
            title=title,
            body=body,
            state=state,
            labels=frozenset(label["name"] for label in labels),
        )

    @staticmethod
    def _strings(
        payload: dict[str, Any],
        names: tuple[str, ...],
        *,
        source: str,
    ) -> dict[str, str]:
        missing = [name for name in names if name not in payload]
        if missing:
            raise ProducerToolError(f"{source} returned incomplete JSON; missing: {', '.join(missing)}")
        if not all(isinstance(payload[name], str) and payload[name] for name in names):
            raise ProducerToolError(f"{source} returned invalid field types")
        return {name: payload[name] for name in names}
