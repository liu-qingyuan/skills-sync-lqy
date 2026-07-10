#!/usr/bin/env python3
"""Strict parser and read-only CLI for a GitHub issue Git contract."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path


GIT_HEADING = "Git"
FIELD_NAMES = ("Branch", "Base branch", "Base commit")
FULL_SHA_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
FIELD_PATTERN = re.compile(r"^- ([^:]+): `([^`]+)`$")
FORBIDDEN_REF_CHARS = re.compile(r"[\x00-\x20\x7f~^:?*\\[]")


class GitContractError(ValueError):
    """Raised when an issue body contains a malformed persistent Git contract."""


@dataclass(frozen=True)
class GitContract:
    branch: str
    base_branch: str
    base_commit: str


def is_valid_git_ref(value: str, *, branch: bool = False) -> bool:
    if not value or value == "@" or value.startswith("/") or value.endswith(("/", ".")):
        return False
    if branch and value.startswith("-"):
        return False
    if "//" in value or ".." in value or "@{" in value or FORBIDDEN_REF_CHARS.search(value):
        return False
    return all(component and not component.startswith(".") and not component.endswith(".lock") for component in value.split("/"))


def parse_git_contract(body: str, *, require_unique: bool = False) -> GitContract:
    headings = list(re.finditer(r"^##\s+([^\n]+?)\s*$", body or "", flags=re.MULTILINE))
    git_headings = [match for match in headings if match.group(1) == GIT_HEADING]
    if not git_headings:
        raise GitContractError("missing `## Git` section")
    if require_unique and len(git_headings) != 1:
        raise GitContractError(f"expected exactly one `## Git` section, found {len(git_headings)}")

    git_heading = git_headings[-1]
    if headings[-1] is not git_heading:
        raise GitContractError("`## Git` must be the final section")

    lines = [line for line in body[git_heading.end() :].strip().splitlines() if line.strip()]
    if len(lines) != len(FIELD_NAMES):
        raise GitContractError(f"`## Git` must contain exactly {len(FIELD_NAMES)} fields")

    values: list[str] = []
    for expected_name, line in zip(FIELD_NAMES, lines):
        match = FIELD_PATTERN.fullmatch(line.strip())
        if match is None or match.group(1) != expected_name:
            raise GitContractError(f"expected `- {expected_name}: `<value>``")
        values.append(match.group(2))

    branch, base_branch, base_commit = values
    if not is_valid_git_ref(branch, branch=True):
        raise GitContractError("invalid `Branch` Git ref")
    if not is_valid_git_ref(base_branch):
        raise GitContractError("invalid `Base branch` Git ref")
    if not FULL_SHA_PATTERN.fullmatch(base_commit):
        raise GitContractError("`Base commit` must be a full 40-character SHA")
    return GitContract(branch=branch, base_branch=base_branch, base_commit=base_commit)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the final `## Git` section in an issue body.")
    parser.add_argument("body_file", nargs="?", default="-", help="Issue body file, or `-` to read stdin.")
    parser.add_argument(
        "--require-unique",
        action="store_true",
        help="Reject bodies containing historical `## Git` sections; intended for issue producers.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        body = sys.stdin.read() if args.body_file == "-" else Path(args.body_file).read_text(encoding="utf-8")
        contract = parse_git_contract(body, require_unique=args.require_unique)
    except GitContractError as exc:
        print(f"CONTRACT ERROR: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(asdict(contract), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
