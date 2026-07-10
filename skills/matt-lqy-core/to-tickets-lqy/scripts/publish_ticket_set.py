#!/usr/bin/env python3
"""Publish a validated Git-bound Ticket set and apply ready labels last."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


READY_LABEL = "ready-for-agent"
REQUIRED_DRAFT_SECTIONS = ("What to build", "Acceptance criteria", "Mermaid Gate")
TICKET_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
EXTERNAL_BLOCKER_PATTERN = re.compile(r"^#([1-9][0-9]*)$")


class PublishError(RuntimeError):
    """Raised when publication cannot preserve the Ticket-set contract."""


@dataclass(frozen=True)
class Issue:
    number: int
    title: str
    body: str
    state: str
    labels: frozenset[str]


@dataclass(frozen=True)
class TicketDraft:
    ticket_id: str
    title: str
    body: str
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class PublishedTicket:
    ticket_id: str
    number: int
    title: str
    body: str
    url: str


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def shared_script(name: str) -> Path:
    skill_dir = Path(
        os.environ.get("RALPH_PLAN_SKILL_DIR", Path.home() / ".agents" / "skills" / "ralph-plan-lqy")
    )
    script = skill_dir / "scripts" / name
    if not script.is_file():
        raise PublishError(f"required ralph-plan-lqy script is not installed: {script}")
    return script


def command_json(command: list[str], *, input_text: str | None = None) -> dict[str, Any]:
    result = run(command, input_text=input_text)
    if result.returncode == 3:
        raise PublishError(result.stderr.strip() or result.stdout.strip() or f"{' '.join(command)} failed")
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise OSError(f"{' '.join(command)} failed: {detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise OSError(f"{' '.join(command)} returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise OSError(f"{' '.join(command)} returned a non-object JSON value")
    return payload


def validate_contract(body: str) -> dict[str, str]:
    payload = command_json(
        [sys.executable, str(shared_script("git_contract.py")), "--require-unique"],
        input_text=body,
    )
    try:
        return {
            "branch": str(payload["branch"]),
            "base_branch": str(payload["base_branch"]),
            "base_commit": str(payload["base_commit"]),
        }
    except KeyError as exc:
        raise OSError("shared Git contract validator returned incomplete JSON") from exc


def provision_workspace(repo: Path, parent_body: str) -> dict[str, Any]:
    return command_json(
        [sys.executable, str(shared_script("provision_workspace.py")), "--repo", str(repo)],
        input_text=parent_body,
    )


def gh(*args: str) -> str:
    result = run(["gh", *args])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise OSError(f"gh {' '.join(args)} failed: {detail}")
    return result.stdout


def issue_from_json(payload: dict[str, Any]) -> Issue:
    try:
        labels = frozenset(
            str(label["name"])
            for label in payload.get("labels", [])
            if isinstance(label, dict) and label.get("name")
        )
        return Issue(
            number=int(payload["number"]),
            title=str(payload.get("title") or ""),
            body=str(payload.get("body") or ""),
            state=str(payload.get("state") or ""),
            labels=labels,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise OSError("gh issue view returned malformed issue JSON") from exc


def view_issue(number: int) -> Issue:
    output = gh("issue", "view", str(number), "--json", "number,title,body,state,labels")
    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise OSError(f"gh issue view {number} returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise OSError(f"gh issue view {number} returned a non-object JSON value")
    return issue_from_json(payload)


def validate_parent(issue: Issue) -> dict[str, str]:
    if issue.state.upper() != "OPEN":
        raise PublishError(f"parent issue #{issue.number} is {issue.state or 'not open'}")
    if not re.match(r"^\s*Spec\s*:", issue.title, flags=re.IGNORECASE):
        raise PublishError(f"parent issue #{issue.number} title must start with `Spec:`")
    return validate_contract(issue.body)


def validate_draft_body(body: str, *, ticket_id: str) -> None:
    headings = list(re.finditer(r"^##\s+([^\n]+?)\s*$", body, flags=re.MULTILINE))
    names = [match.group(1) for match in headings]
    if names != list(REQUIRED_DRAFT_SECTIONS):
        for required in REQUIRED_DRAFT_SECTIONS:
            count = names.count(required)
            if count == 0:
                raise PublishError(f"ticket `{ticket_id}` is missing `## {required}` section")
            if count != 1:
                raise PublishError(
                    f"ticket `{ticket_id}` expected exactly one `## {required}` section, found {count}"
                )
        raise PublishError(
            f"ticket `{ticket_id}` draft sections must be exactly: "
            + ", ".join(f"`## {name}`" for name in REQUIRED_DRAFT_SECTIONS)
        )

    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        if not body[heading.end() : end].strip():
            raise PublishError(f"ticket `{ticket_id}` section `## {heading.group(1)}` must not be empty")


def load_manifest(path: Path) -> list[TicketDraft]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublishError(f"cannot read Ticket manifest `{path}`: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("tickets"), list) or not payload["tickets"]:
        raise PublishError("Ticket manifest must contain a non-empty `tickets` array")

    drafts: list[TicketDraft] = []
    seen: set[str] = set()
    for index, item in enumerate(payload["tickets"], start=1):
        if not isinstance(item, dict):
            raise PublishError(f"Ticket manifest entry {index} must be an object")
        ticket_id = item.get("id")
        title = item.get("title")
        body_file = item.get("body_file")
        blockers = item.get("blocked_by")
        if not isinstance(ticket_id, str) or not TICKET_ID_PATTERN.fullmatch(ticket_id):
            raise PublishError(f"Ticket manifest entry {index} has invalid `id`")
        if ticket_id in seen:
            raise PublishError(f"duplicate Ticket id `{ticket_id}`")
        if not isinstance(title, str) or not title.strip() or re.match(r"^\s*Spec\s*:", title, flags=re.IGNORECASE):
            raise PublishError(f"ticket `{ticket_id}` must have a non-spec title")
        if not isinstance(body_file, str) or not body_file.strip():
            raise PublishError(f"ticket `{ticket_id}` must have a `body_file`")
        if not isinstance(blockers, list) or not all(isinstance(blocker, str) for blocker in blockers):
            raise PublishError(f"ticket `{ticket_id}` must have a string `blocked_by` array")
        if len(set(blockers)) != len(blockers):
            raise PublishError(f"ticket `{ticket_id}` contains duplicate blockers")
        for blocker in blockers:
            if blocker in seen or EXTERNAL_BLOCKER_PATTERN.fullmatch(blocker):
                continue
            if blocker in {entry.get("id") for entry in payload["tickets"] if isinstance(entry, dict)}:
                raise PublishError(f"ticket `{ticket_id}` is ordered before blocker `{blocker}`")
            raise PublishError(f"ticket `{ticket_id}` references unknown blocker `{blocker}`")

        draft_path = (path.parent / body_file).resolve()
        try:
            body = draft_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise PublishError(f"cannot read body for ticket `{ticket_id}`: {exc}") from exc
        validate_draft_body(body, ticket_id=ticket_id)
        drafts.append(
            TicketDraft(
                ticket_id=ticket_id,
                title=title.strip(),
                body=body,
                blockers=tuple(blockers),
            )
        )
        seen.add(ticket_id)
    return drafts


def validate_external_blockers(
    drafts: Sequence[TicketDraft],
    *,
    parent_number: int,
    parent_contract: dict[str, str],
) -> dict[str, int]:
    resolved: dict[str, int] = {}
    for draft in drafts:
        for blocker in draft.blockers:
            match = EXTERNAL_BLOCKER_PATTERN.fullmatch(blocker)
            if match is None or blocker in resolved:
                continue
            number = int(match.group(1))
            if number == parent_number:
                raise PublishError(f"ticket `{draft.ticket_id}` cannot be blocked by its parent spec #{number}")
            issue = view_issue(number)
            blocker_contract = validate_contract(issue.body)
            if blocker_contract != parent_contract:
                raise PublishError(f"blocker #{number} does not match parent Git contract")
            resolved[blocker] = number
    return resolved


def render_git_contract(contract: dict[str, str]) -> str:
    return (
        "## Git\n\n"
        f"- Branch: `{contract['branch']}`\n"
        f"- Base branch: `{contract['base_branch']}`\n"
        f"- Base commit: `{contract['base_commit']}`"
    )


def render_ticket_body(
    draft: TicketDraft,
    *,
    parent_number: int,
    internal_numbers: dict[str, int],
    external_numbers: dict[str, int],
    contract: dict[str, str],
) -> str:
    blocker_numbers = [
        internal_numbers[blocker] if blocker in internal_numbers else external_numbers[blocker]
        for blocker in draft.blockers
    ]
    blockers = "\n".join(f"- #{number}" for number in blocker_numbers)
    if not blockers:
        blockers = "- None — can start immediately"
    return (
        f"## Parent\n\n#{parent_number}\n\n"
        f"{draft.body}\n\n"
        f"## Blocked by\n\n{blockers}\n\n"
        f"{render_git_contract(contract)}\n"
    )


def issue_number_from_url(output: str) -> tuple[int, str]:
    url = output.strip().splitlines()[-1] if output.strip() else ""
    match = re.search(r"/issues/(\d+)/?$", url)
    if match is None:
        raise OSError(f"gh issue create returned an unexpected URL: {url or '<empty>'}")
    return int(match.group(1)), url


def create_ticket(draft: TicketDraft, body: str, body_dir: Path) -> PublishedTicket:
    body_file = body_dir / f"{draft.ticket_id}.md"
    body_file.write_text(body, encoding="utf-8")
    number, url = issue_number_from_url(
        gh("issue", "create", "--title", draft.title, "--body-file", str(body_file))
    )
    return PublishedTicket(
        ticket_id=draft.ticket_id,
        number=number,
        title=draft.title,
        body=body,
        url=url,
    )


def validate_published_set(
    tickets: Sequence[PublishedTicket],
    *,
    contract: dict[str, str],
) -> None:
    for ticket in tickets:
        issue = view_issue(ticket.number)
        if issue.title != ticket.title or issue.body.rstrip("\n") != ticket.body.rstrip("\n"):
            raise PublishError(f"issue #{ticket.number} changed during publication; ready labels were not applied")
        if issue.state.upper() != "OPEN":
            raise PublishError(f"issue #{ticket.number} is {issue.state or 'not open'} after publication")
        if READY_LABEL in issue.labels:
            raise PublishError(f"issue #{ticket.number} received `{READY_LABEL}` before set validation")
        if validate_contract(issue.body) != contract:
            raise PublishError(f"issue #{ticket.number} Git contract does not match parent")


def apply_ready_labels(tickets: Sequence[PublishedTicket]) -> None:
    applied: list[int] = []
    try:
        for ticket in reversed(tickets):
            gh("issue", "edit", str(ticket.number), "--add-label", READY_LABEL)
            applied.append(ticket.number)
    except OSError as exc:
        rollback_errors: list[str] = []
        for number in reversed(applied):
            try:
                gh("issue", "edit", str(number), "--remove-label", READY_LABEL)
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        if rollback_errors:
            detail = "; ".join(rollback_errors)
            raise OSError(f"ready label publication failed: {exc}; rollback incomplete: {detail}") from exc
        raise OSError(f"ready label publication failed; applied labels were rolled back: {exc}") from exc


def publish(repo: Path, parent_number: int, manifest: Path) -> dict[str, Any]:
    parent = view_issue(parent_number)
    parent_contract = validate_parent(parent)
    drafts = load_manifest(manifest)
    external_numbers = validate_external_blockers(
        drafts,
        parent_number=parent_number,
        parent_contract=parent_contract,
    )
    workspace = provision_workspace(repo, parent.body)

    published: list[PublishedTicket] = []
    internal_numbers: dict[str, int] = {}
    with tempfile.TemporaryDirectory(prefix="to-tickets-lqy-") as temporary:
        body_dir = Path(temporary)
        for draft in drafts:
            body = render_ticket_body(
                draft,
                parent_number=parent_number,
                internal_numbers=internal_numbers,
                external_numbers=external_numbers,
                contract=parent_contract,
            )
            ticket = create_ticket(draft, body, body_dir)
            published.append(ticket)
            internal_numbers[draft.ticket_id] = ticket.number

    validate_published_set(published, contract=parent_contract)
    apply_ready_labels(published)
    return {
        "label": READY_LABEL,
        "parent": parent_number,
        "tickets": [
            {"id": ticket.ticket_id, "number": ticket.number, "title": ticket.title, "url": ticket.url}
            for ticket in published
        ],
        "workspace": workspace,
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a Git-bound Ticket set with label-last semantics.")
    parser.add_argument("--repo", default=".", type=Path, help="Any path inside the target Git repository.")
    parser.add_argument("--parent", required=True, type=int, help="Git-bound parent spec issue number.")
    parser.add_argument("--manifest", required=True, type=Path, help="JSON Ticket manifest in dependency order.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = publish(args.repo, args.parent, args.manifest)
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
