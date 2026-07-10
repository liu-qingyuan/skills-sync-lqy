#!/usr/bin/env python3
"""Publish a validated Git-bound Ticket set and apply ready labels last."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast


if TYPE_CHECKING:
    from producer_adapter import GitContract, IssueSnapshot, ProducerToolAdapter


READY_LABEL = "ready-for-agent"
REQUIRED_DRAFT_SECTIONS = ("What to build", "Acceptance criteria", "Mermaid Gate")
TICKET_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
EXTERNAL_BLOCKER_PATTERN = re.compile(r"^#([1-9][0-9]*)$")
PARENT_SECTION_PATTERN = re.compile(
    r"^##[ \t]+Parent[ \t]*\r?\n(?P<body>.*?)(?=^##[ \t]+|\Z)",
    flags=re.MULTILINE | re.DOTALL,
)


class PublishError(RuntimeError):
    """Raised when publication cannot preserve the Ticket-set contract."""


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


def list_child_issues(tools: ProducerToolAdapter, parent_number: int) -> list[IssueSnapshot]:
    children: list[IssueSnapshot] = []
    expected_reference = f"#{parent_number}"
    for issue in tools.list_issues():
        parent_sections = PARENT_SECTION_PATTERN.findall(issue.body)
        if len(parent_sections) == 1 and parent_sections[0].strip() == expected_reference:
            children.append(issue)
    return sorted(children, key=lambda issue: issue.number)


def validate_parent(tools: ProducerToolAdapter, issue: IssueSnapshot) -> GitContract:
    if issue.state.upper() != "OPEN":
        raise PublishError(f"parent issue #{issue.number} is {issue.state or 'not open'}")
    if not re.match(r"^\s*Spec\s*:", issue.title, flags=re.IGNORECASE):
        raise PublishError(f"parent issue #{issue.number} title must start with `Spec:`")
    return tools.validate_git_contract(issue.body)


def validate_child_contract(tools: ProducerToolAdapter, issue: IssueSnapshot) -> GitContract:
    try:
        return tools.validate_git_contract(issue.body)
    except ValueError as exc:
        raise PublishError(f"child issue #{issue.number} has an invalid Git contract: {exc}") from exc


def resolve_frozen_contract(
    tools: ProducerToolAdapter,
    *,
    parent: IssueSnapshot,
    parent_contract: GitContract,
) -> GitContract:
    children = list_child_issues(tools, parent.number)
    ready_children = [issue for issue in children if READY_LABEL in issue.labels]
    if not ready_children:
        return parent_contract

    frozen_source = ready_children[0]
    frozen_contract = validate_child_contract(tools, frozen_source)
    for child in children:
        child_contract = validate_child_contract(tools, child)
        if child_contract != frozen_contract:
            raise PublishError(
                f"child issue #{child.number} Git contract does not match frozen contract "
                f"from child #{frozen_source.number}"
            )
    if parent_contract != frozen_contract:
        raise PublishError(
            f"parent issue #{parent.number} Git contract drifted from frozen contract "
            f"in child #{frozen_source.number}"
        )
    return frozen_contract


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
    tools: ProducerToolAdapter,
    drafts: Sequence[TicketDraft],
    *,
    parent_number: int,
    parent_contract: GitContract,
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
            issue = tools.view_issue(number)
            if re.match(r"^\s*Spec\s*:", issue.title, flags=re.IGNORECASE):
                raise PublishError(f"blocker #{number} must be a concrete Ticket, not a parent spec")
            try:
                blocker_contract = tools.validate_git_contract(issue.body)
            except ValueError as exc:
                raise PublishError(f"blocker #{number} has an invalid Git contract: {exc}") from exc
            if blocker_contract.branch != parent_contract.branch:
                raise PublishError(
                    f"blocker #{number} branch `{blocker_contract.branch}` does not match "
                    f"parent branch `{parent_contract.branch}`"
                )
            resolved[blocker] = number
    return resolved


def render_git_contract(contract: GitContract) -> str:
    return (
        "## Git\n\n"
        f"- Branch: `{contract.branch}`\n"
        f"- Base branch: `{contract.base_branch}`\n"
        f"- Base commit: `{contract.base_commit}`"
    )


def render_ticket_body(
    draft: TicketDraft,
    *,
    parent_number: int,
    internal_numbers: dict[str, int],
    external_numbers: dict[str, int],
    contract: GitContract,
    publication_gate: int | None,
) -> str:
    blocker_numbers = ([] if publication_gate is None else [publication_gate]) + [
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


def create_ticket(
    tools: ProducerToolAdapter,
    draft: TicketDraft,
    body: str,
    body_dir: Path,
) -> PublishedTicket:
    body_file = body_dir / f"{draft.ticket_id}.md"
    body_file.write_text(body, encoding="utf-8")
    number, url = issue_number_from_url(
        tools.gh("issue", "create", "--title", draft.title, "--body-file", str(body_file))
    )
    return PublishedTicket(
        ticket_id=draft.ticket_id,
        number=number,
        title=draft.title,
        body=body,
        url=url,
    )


def publication_gate_draft(parent_number: int) -> TicketDraft:
    body = (
        "## What to build\n\n"
        f"为父 spec #{parent_number} 的 Ticket frontier 保存发布 gate 状态。\n\n"
        "## Acceptance criteria\n\n"
        "- [ ] 仅在每个 Ticket 的 `ready-for-agent` 状态都已回读验证后关闭。\n\n"
        "## Mermaid Gate\n\n"
        "不需要图。此 issue 只保存发布事务状态，不改变模块接口或调用流程。"
    )
    return TicketDraft(
        ticket_id="publication-gate",
        title=f"发布 #{parent_number} Ticket frontier",
        body=body,
        blockers=(),
    )


def validate_published_set(
    tools: ProducerToolAdapter,
    tickets: Sequence[PublishedTicket],
    *,
    contract: GitContract,
) -> None:
    for ticket in tickets:
        issue = tools.view_issue(ticket.number)
        if issue.title != ticket.title or issue.body.rstrip("\n") != ticket.body.rstrip("\n"):
            raise PublishError(f"issue #{ticket.number} changed during publication; ready labels were not applied")
        if issue.state.upper() != "OPEN":
            raise PublishError(f"issue #{ticket.number} is {issue.state or 'not open'} after publication")
        if READY_LABEL in issue.labels:
            raise PublishError(f"issue #{ticket.number} received `{READY_LABEL}` before set validation")
        if tools.validate_git_contract(issue.body) != contract:
            raise PublishError(f"issue #{ticket.number} Git contract does not match parent")


def validate_ready_labels(
    tools: ProducerToolAdapter,
    tickets: Sequence[PublishedTicket],
) -> None:
    for ticket in tickets:
        issue = tools.view_issue(ticket.number)
        if issue.state.upper() != "OPEN" or READY_LABEL not in issue.labels:
            raise PublishError(
                f"issue #{ticket.number} did not retain the validated `{READY_LABEL}` state; publication gate stays open"
            )


def apply_ready_labels(tools: ProducerToolAdapter, tickets: Sequence[PublishedTicket]) -> None:
    applied: list[int] = []
    try:
        for ticket in reversed(tickets):
            tools.gh("issue", "edit", str(ticket.number), "--add-label", READY_LABEL)
            applied.append(ticket.number)
    except OSError as exc:
        rollback_errors: list[str] = []
        for number in reversed(applied):
            try:
                tools.gh("issue", "edit", str(number), "--remove-label", READY_LABEL)
            except OSError as rollback_exc:
                rollback_errors.append(str(rollback_exc))
        if rollback_errors:
            detail = "; ".join(rollback_errors)
            raise OSError(f"ready label publication failed: {exc}; rollback incomplete: {detail}") from exc
        raise OSError(f"ready label publication failed; applied labels were rolled back: {exc}") from exc


def publish(
    repo: Path,
    parent_number: int,
    manifest: Path,
    *,
    allow_base_drift: bool,
) -> dict[str, Any]:
    tools = load_producer_adapter(repo)
    parent = tools.view_issue(parent_number)
    parent_contract = validate_parent(tools, parent)
    drafts = load_manifest(manifest)
    parent_contract = resolve_frozen_contract(
        tools,
        parent=parent,
        parent_contract=parent_contract,
    )
    external_numbers = validate_external_blockers(
        tools,
        drafts,
        parent_number=parent_number,
        parent_contract=parent_contract,
    )
    workspace = tools.provision_workspace(
        parent.body,
        expected_branch=parent_contract.branch,
        allow_base_drift=allow_base_drift,
    )

    published: list[PublishedTicket] = []
    internal_numbers: dict[str, int] = {}
    with tempfile.TemporaryDirectory(prefix="to-tickets-lqy-") as temporary:
        body_dir = Path(temporary)
        gate_draft = publication_gate_draft(parent_number)
        gate_body = render_ticket_body(
            gate_draft,
            parent_number=parent_number,
            internal_numbers={},
            external_numbers={},
            contract=parent_contract,
            publication_gate=None,
        )
        publication_gate = create_ticket(tools, gate_draft, gate_body, body_dir)
        for draft in drafts:
            body = render_ticket_body(
                draft,
                parent_number=parent_number,
                internal_numbers=internal_numbers,
                external_numbers=external_numbers,
                contract=parent_contract,
                publication_gate=publication_gate.number,
            )
            ticket = create_ticket(tools, draft, body, body_dir)
            published.append(ticket)
            internal_numbers[draft.ticket_id] = ticket.number

    validate_published_set(tools, [publication_gate, *published], contract=parent_contract)
    apply_ready_labels(tools, published)
    validate_ready_labels(tools, published)
    tools.gh(
        "issue",
        "close",
        str(publication_gate.number),
        "--comment",
        "Ticket frontier 已完整验证并发布。",
    )
    return {
        "label": READY_LABEL,
        "parent": parent_number,
        "publication_gate": publication_gate.number,
        "tickets": [
            {"id": ticket.ticket_id, "number": ticket.number, "title": ticket.title, "url": ticket.url}
            for ticket in published
        ],
        "workspace": asdict(workspace),
    }


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a Git-bound Ticket set with label-last semantics.")
    parser.add_argument("--repo", default=".", type=Path, help="Any path inside the target Git repository.")
    parser.add_argument("--parent", required=True, type=int, help="Git-bound parent spec issue number.")
    parser.add_argument("--manifest", required=True, type=Path, help="JSON Ticket manifest in dependency order.")
    parser.add_argument(
        "--allow-base-drift",
        action="store_true",
        help="Continue from the recorded base only after the user explicitly chooses the old SHA.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = publish(
            args.repo,
            args.parent,
            args.manifest,
            allow_base_drift=args.allow_base_drift,
        )
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
