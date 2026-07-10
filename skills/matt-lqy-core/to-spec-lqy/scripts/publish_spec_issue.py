#!/usr/bin/env python3
"""Publish a validated Git-bound parent spec and apply ready label last."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path


READY_LABEL = "ready-for-agent"


class PublishError(RuntimeError):
    """Raised when publication cannot preserve the Git-bound issue contract."""


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def contract_validator() -> Path:
    skill_dir = Path(
        os.environ.get("RALPH_PLAN_SKILL_DIR", Path.home() / ".agents" / "skills" / "ralph-plan-lqy")
    )
    validator = skill_dir / "scripts" / "git_contract.py"
    if not validator.is_file():
        raise PublishError(f"shared Git contract validator is not installed: {validator}")
    return validator


def validate_body(validator: Path, body: str) -> None:
    result = run([sys.executable, str(validator), "--require-unique"], input_text=body)
    if result.returncode == 3:
        raise PublishError(result.stderr.strip())
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise OSError(f"shared Git contract validator failed: {detail}")


def gh(*args: str) -> str:
    result = run(["gh", *args])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise OSError(f"gh {' '.join(args)} failed: {detail}")
    return result.stdout


def issue_number_from_url(output: str) -> tuple[int, str]:
    url = output.strip().splitlines()[-1] if output.strip() else ""
    match = re.search(r"/issues/(\d+)/?$", url)
    if match is None:
        raise OSError(f"gh issue create returned an unexpected URL: {url or '<empty>'}")
    return int(match.group(1)), url


def publish(title: str, body_file: Path) -> dict[str, object]:
    if not title.startswith("Spec: ") or not title.removeprefix("Spec: ").strip():
        raise PublishError("parent spec title must use `Spec: <short title>`")
    body = body_file.read_text(encoding="utf-8")
    validator = contract_validator()
    validate_body(validator, body)

    number, url = issue_number_from_url(
        gh("issue", "create", "--title", title, "--body-file", str(body_file))
    )
    readback = gh("issue", "view", str(number), "--json", "body", "--jq", ".body")
    validate_body(validator, readback)
    if readback.rstrip("\n") != body.rstrip("\n"):
        raise PublishError(f"issue #{number} body changed during publication; ready label was not applied")
    gh("issue", "edit", str(number), "--add-label", READY_LABEL)
    return {"label": READY_LABEL, "number": number, "url": url}


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a Git-bound parent spec with label-last semantics.")
    parser.add_argument("--title", required=True, help="Parent issue title in `Spec: <short title>` form.")
    parser.add_argument("--body-file", required=True, type=Path, help="Complete spec body with final `## Git`.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = publish(args.title, args.body_file)
    except PublishError as exc:
        print(f"PUBLISH ERROR: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
