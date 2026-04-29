#!/usr/bin/env python3
"""Create a minimal graph-grounded wiki skeleton for Codex to fill in.

This script does not summarize code or call an LLM. It creates deterministic
page/metadata scaffolding so the Codex skill can author overview/module/leaf
pages from gathered GitNexus evidence without repeatedly recreating boilerplate.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.STDOUT, text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"unavailable: {exc}"


def slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned or "module"


def read_evidence(paths: Iterable[Path]) -> list[str]:
    evidence = []
    for path in paths:
        if path.exists():
            evidence.append(path.as_posix())
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root used for git metadata")
    parser.add_argument("--out", required=True, help="Wiki output directory")
    parser.add_argument("--evidence", action="append", default=[], help="Evidence file path to cite in pages/metadata")
    parser.add_argument("--module", action="append", default=[], help="Module/parent page name to create")
    parser.add_argument("--leaf", action="append", default=[], help="Leaf page name to create")
    args = parser.parse_args()
    if not args.module:
        args.module = ["core"]
    if not args.leaf:
        args.leaf = ["entrypoints"]

    repo = Path(args.repo).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    modules_dir = out / "modules"
    leaves_dir = out / "leaves"
    modules_dir.mkdir(parents=True, exist_ok=True)
    leaves_dir.mkdir(parents=True, exist_ok=True)

    git_commit = run(["git", "rev-parse", "HEAD"], cwd=repo)
    gitnexus_version = run(["gitnexus", "--version"])
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence_paths = read_evidence(Path(p).expanduser().resolve() for p in args.evidence)

    overview = out / "overview.md"
    if not overview.exists():
        overview.write_text(
            "# Repository overview\n\n"
            f"Generated: {generated_at}\n\n"
            "## GitNexus evidence\n\n"
            + "\n".join(f"- Evidence: {p}" for p in evidence_paths or ["TODO: add GitNexus preflight/context evidence"])
            + "\n\n## Modules\n\n"
            + "\n".join(f"- [{name}](modules/{slug(name)}.md)" for name in args.module)
            + "\n\n## Key flows\n\nTODO: Summarize graph-backed processes/call edges.\n",
            encoding="utf-8",
        )

    for name in args.module:
        path = modules_dir / f"{slug(name)}.md"
        if not path.exists():
            path.write_text(
                f"# Module: {name}\n\n"
                "## Source and graph evidence\n\n"
                "- GitNexus: TODO cite `gitnexus context`, `gitnexus impact`, or focused `gitnexus cypher` output.\n"
                "- Sources: TODO cite source files confirmed by direct reads.\n\n"
                "## Responsibilities\n\nTODO\n\n"
                "## Incoming/outgoing calls\n\nTODO\n\n"
                "## Related leaf pages\n\n"
                + "\n".join(f"- [Leaf: {leaf}](../leaves/{slug(leaf)}.md)" for leaf in args.leaf)
                + "\n",
                encoding="utf-8",
            )

    for name in args.leaf:
        path = leaves_dir / f"{slug(name)}.md"
        if not path.exists():
            path.write_text(
                f"# Leaf: {name}\n\n"
                "## Evidence\n\n"
                "- Source: TODO cite exact file(s).\n"
                "- Graph: TODO cite command/output, e.g. `gitnexus context <symbol-or-file>`.\n\n"
                "## Behavior\n\nTODO\n\n"
                "## Calls and processes\n\nTODO\n",
                encoding="utf-8",
            )

    meta = {
        "generated_at": generated_at,
        "repo": repo.as_posix(),
        "git_commit": git_commit,
        "gitnexus_version": gitnexus_version,
        "execution_boundary": "GitNexus supplies graph/index context; Codex authors markdown directly.",
        "modules": args.module,
        "leaves": args.leaf,
        "evidence_files": evidence_paths,
    }
    (out / "wiki-meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote wiki scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
