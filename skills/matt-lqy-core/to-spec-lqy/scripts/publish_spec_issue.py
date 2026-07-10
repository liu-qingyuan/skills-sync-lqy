#!/usr/bin/env python3
"""Publish a validated Git-bound parent spec and apply ready label last."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from producer_adapter import ProducerToolAdapter


READY_LABEL = "ready-for-agent"
REQUIRED_SPEC_SECTIONS = (
    "Problem Statement",
    "Solution",
    "User Stories",
    "Implementation Decisions",
    "Testing Decisions",
    "Mermaid Gate",
    "Out of Scope",
    "Further Notes",
)


class PublishError(RuntimeError):
    """Raised when publication cannot preserve the Git-bound issue contract."""


def load_producer_adapter(repo: Path) -> ProducerToolAdapter:
    skill_dir = Path(
        os.environ.get("RALPH_PLAN_SKILL_DIR", Path.home() / ".agents" / "skills" / "ralph-plan-lqy")
    )
    adapter_path = skill_dir / "scripts" / "producer_adapter.py"
    if not adapter_path.is_file():
        raise PublishError(f"shared producer adapter is not installed: {adapter_path}")
    spec = importlib.util.spec_from_file_location("ralph_plan_producer_adapter", adapter_path)
    if spec is None or spec.loader is None:
        raise PublishError(f"cannot load shared producer adapter: {adapter_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return cast("ProducerToolAdapter", module.ProducerToolAdapter(repo, skill_dir=skill_dir))


def validate_spec_structure(body: str) -> None:
    headings = list(re.finditer(r"^##\s+([^\n]+?)\s*$", body, flags=re.MULTILINE))
    positions: list[int] = []
    for required in REQUIRED_SPEC_SECTIONS:
        matches = [match for match in headings if match.group(1) == required]
        if not matches:
            raise PublishError(f"missing `## {required}` section")
        if len(matches) != 1:
            raise PublishError(f"expected exactly one `## {required}` section, found {len(matches)}")
        match = matches[0]
        positions.append(match.start())
        next_heading = next((heading for heading in headings if heading.start() > match.start()), None)
        end = next_heading.start() if next_heading is not None else len(body)
        if not body[match.end() : end].strip():
            raise PublishError(f"`## {required}` section must not be empty")
    if positions != sorted(positions):
        raise PublishError("spec template sections are out of order")


def issue_number_from_url(output: str) -> tuple[int, str]:
    url = output.strip().splitlines()[-1] if output.strip() else ""
    match = re.search(r"/issues/(\d+)/?$", url)
    if match is None:
        raise OSError(f"gh issue create returned an unexpected URL: {url or '<empty>'}")
    return int(match.group(1)), url


def publish(repo: Path, title: str, body_file: Path) -> dict[str, object]:
    if not title.startswith("Spec: ") or not title.removeprefix("Spec: ").strip():
        raise PublishError("parent spec title must use `Spec: <short title>`")
    body_file = body_file.expanduser().resolve()
    body = body_file.read_text(encoding="utf-8")
    tools = load_producer_adapter(repo)
    validate_spec_structure(body)
    tools.validate_git_contract(body)

    number, url = issue_number_from_url(
        tools.gh("issue", "create", "--title", title, "--body-file", str(body_file))
    )
    readback = tools.gh("issue", "view", str(number), "--json", "body", "--jq", ".body")
    validate_spec_structure(readback)
    tools.validate_git_contract(readback)
    if readback.rstrip("\n") != body.rstrip("\n"):
        raise PublishError(f"issue #{number} body changed during publication; ready label was not applied")
    tools.gh("issue", "edit", str(number), "--add-label", READY_LABEL)
    return {"label": READY_LABEL, "number": number, "url": url}


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a Git-bound parent spec with label-last semantics.")
    parser.add_argument("--repo", default=".", type=Path, help="Any path inside the target Git repository.")
    parser.add_argument("--title", required=True, help="Parent issue title in `Spec: <short title>` form.")
    parser.add_argument("--body-file", required=True, type=Path, help="Complete spec body with final `## Git`.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = publish(args.repo, args.title, args.body_file)
    except (PublishError, ValueError) as exc:
        print(f"PUBLISH ERROR: {exc}", file=sys.stderr)
        return 3
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
