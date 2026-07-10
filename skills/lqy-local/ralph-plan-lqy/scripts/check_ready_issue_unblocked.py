#!/usr/bin/env python3
"""Read-only branch-aware eligibility gate for Ralph issue-backlog runs."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from git_contract import GitContractError, parse_git_contract

READY_LABEL = "ready-for-agent"
BLOCKER_HEADING = "Blocked by"
NO_BLOCKER_PATTERN = re.compile(
    r"^(?:none(?:\s*[-–—]\s*can start immediately)?|no blockers?|无(?:\s*[-–—]\s*可以立即开始)?|可以立即开始)[.!。]?$",
    flags=re.IGNORECASE,
)
PARENT_TITLE_PATTERN = re.compile(r"^\s*Spec\s*:", flags=re.IGNORECASE)
SPEC_BODY_MARKERS = (
    "## Problem Statement",
    "## User Stories",
    "## Implementation Decisions",
    "## Testing Decisions",
)

EXIT_READY = 0
EXIT_ERROR = 1
EXIT_NOT_READY = 2
EXIT_CONTRACT_ERROR = 3


@dataclass(frozen=True)
class IssueInfo:
    number: int
    title: str
    state: str
    labels: frozenset[str]
    body: str


@dataclass(frozen=True)
class BlockerParseResult:
    blocker_numbers: tuple[int, ...]
    section_found: bool


class BlockerContractError(ValueError):
    """Raised when a concrete Ticket has a malformed blocker contract."""


def extract_blocker_sections(body: str) -> list[str]:
    pattern = re.compile(
        rf"^##\s+{re.escape(BLOCKER_HEADING)}\s*$\n?(.*?)(?=^##\s+|\Z)",
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    return [match.group(1).strip() for match in pattern.finditer(body or "")]


def parse_blockers(body: str) -> BlockerParseResult:
    sections = extract_blocker_sections(body)
    if not sections:
        return BlockerParseResult(blocker_numbers=(), section_found=False)
    if len(sections) != 1:
        raise BlockerContractError(f"expected exactly one `## Blocked by` section, found {len(sections)}")

    section = sections[0]
    normalized = re.sub(r"^\s*[-*]\s*", "", section.strip()).strip("` ")
    numbers: list[int] = []
    seen: set[int] = set()
    for raw_number in re.findall(r"(?:#|/issues/)(\d+)\b", section):
        number = int(raw_number)
        if number not in seen:
            numbers.append(number)
            seen.add(number)
    has_no_blocker_marker = NO_BLOCKER_PATTERN.fullmatch(normalized) is not None
    if numbers and has_no_blocker_marker:
        raise BlockerContractError("invalid `## Blocked by` section: mixes blockers with a no-blocker marker")
    if not numbers and not has_no_blocker_marker:
        raise BlockerContractError("invalid `## Blocked by` section: expected issue references or an explicit no-blocker marker")
    return BlockerParseResult(blocker_numbers=tuple(numbers), section_found=True)


def is_parent_spec_issue(issue: IssueInfo) -> bool:
    if PARENT_TITLE_PATTERN.search(issue.title):
        return True
    return sum(marker in issue.body for marker in SPEC_BODY_MARKERS) >= 3


def issue_from_gh_json(payload: dict[str, Any]) -> IssueInfo:
    labels = frozenset(str(label.get("name", "")) for label in payload.get("labels", []) if label.get("name"))
    return IssueInfo(
        number=int(payload["number"]),
        title=str(payload.get("title", "")),
        state=str(payload.get("state", "")),
        labels=labels,
        body=str(payload.get("body") or ""),
    )


def gh_issue_view(issue_number: int) -> IssueInfo:
    cmd = [
        "gh",
        "issue",
        "view",
        str(issue_number),
        "--json",
        "number,title,state,labels,body",
    ]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"`{' '.join(cmd)}` failed: {message}")
    return issue_from_gh_json(json.loads(completed.stdout))


def current_branch() -> str:
    cmd = ["git", "symbolic-ref", "--quiet", "--short", "HEAD"]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout).strip() or "HEAD is not attached to a branch"
        raise RuntimeError(f"`{' '.join(cmd)}` failed: {message}")
    return completed.stdout.strip()


def base_commit_is_ancestor(base_commit: str) -> bool:
    cmd = ["git", "merge-base", "--is-ancestor", base_commit, "HEAD"]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    message = (completed.stderr or completed.stdout).strip()
    raise RuntimeError(f"`{' '.join(cmd)}` failed: {message}")


def validate_blocker_contracts(target_branch: str, blockers: Sequence[IssueInfo]) -> None:
    for blocker in blockers:
        try:
            blocker_contract = parse_git_contract(blocker.body)
        except GitContractError as exc:
            raise GitContractError(f"blocker #{blocker.number} has invalid Git contract: {exc}") from exc
        if blocker_contract.branch != target_branch:
            raise GitContractError(
                f"blocker #{blocker.number} targets branch `{blocker_contract.branch}`, expected `{target_branch}`"
            )


def not_ready_reasons(target: IssueInfo, blockers: Sequence[IssueInfo]) -> list[str]:
    reasons: list[str] = []
    if target.state.upper() != "OPEN":
        reasons.append(f"target issue is {target.state}")
    if READY_LABEL not in target.labels:
        reasons.append(f"target issue is missing `{READY_LABEL}` label")

    open_blockers = [issue for issue in blockers if issue.state.upper() != "CLOSED"]
    if open_blockers:
        reasons.append("blocked by open issues: " + " ".join(f"#{issue.number}" for issue in open_blockers))
    return reasons


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether a ready-for-agent issue is eligible on this branch.")
    parser.add_argument("issue_number", type=int)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        target = gh_issue_view(args.issue_number)
        contract = parse_git_contract(target.body)
        attached_branch = current_branch()
        if contract.branch != attached_branch:
            print(f"NOT READY #{target.number} {target.title}")
            print(f"- branch `{contract.branch}` does not match current branch `{attached_branch}`")
            return EXIT_NOT_READY
        if not base_commit_is_ancestor(contract.base_commit):
            raise GitContractError(f"base commit `{contract.base_commit}` is not an ancestor of HEAD")
        if is_parent_spec_issue(target):
            print(f"NOT READY #{target.number} {target.title}")
            print("- target issue is a parent spec, not an implementation Ticket")
            return EXIT_NOT_READY
        blocker_parse = parse_blockers(target.body)
        if not blocker_parse.section_found:
            raise GitContractError("missing `## Blocked by` section")
        blockers = [gh_issue_view(number) for number in blocker_parse.blocker_numbers]
        validate_blocker_contracts(contract.branch, blockers)
    except (GitContractError, BlockerContractError) as exc:
        print(f"CONTRACT ERROR #{args.issue_number}: {exc}", file=sys.stderr)
        return EXIT_CONTRACT_ERROR
    except (OSError, RuntimeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"ERROR #{args.issue_number}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    reasons = not_ready_reasons(target, blockers)
    if reasons:
        print(f"NOT READY #{target.number} {target.title}")
        for reason in reasons:
            print(f"- {reason}")
        return EXIT_NOT_READY

    print(f"READY #{target.number} {target.title}")
    return EXIT_READY


if __name__ == "__main__":
    raise SystemExit(main())
