#!/usr/bin/env python3
"""Sync already-installed project skills from an installable skills repository.

This intentionally updates only skills already present under a target project's
`.agents/skills/`. It does not install new skills and never reads baselines or
upstream mirrors as sync sources.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_URL = "https://github.com/liu-qingyuan/skills-sync-lqy.git"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "skills-sync-lqy"


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def resolve_source_repo(repo_url: str | None, source: Path | None, cache_dir: Path) -> Path:
    if source is not None:
        source = source.expanduser().resolve()
        if not (source / "skills").is_dir():
            fail(f"source repo has no skills/ directory: {source}")
        return source

    if repo_url is None:
        candidate = Path(__file__).resolve().parents[1]
        if (candidate / "skills").is_dir():
            return candidate
        repo_url = DEFAULT_REPO_URL

    cache_dir = cache_dir.expanduser().resolve()
    if (cache_dir / ".git").is_dir():
        pull = run(["git", "pull", "--ff-only"], cwd=cache_dir)
        if pull.returncode != 0:
            fail(f"failed to update cached repo at {cache_dir}\n{pull.stderr.strip()}")
    else:
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        clone = run(["git", "clone", repo_url, str(cache_dir)])
        if clone.returncode != 0:
            fail(f"failed to clone {repo_url} into {cache_dir}\n{clone.stderr.strip()}")

    if not (cache_dir / "skills").is_dir():
        fail(f"cached repo has no skills/ directory: {cache_dir}")
    return cache_dir


def frontmatter_name(skill_md: Path) -> str | None:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, flags=re.S)
    if not match:
        return None
    for line in match.group(1).splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def validate_skill_dir(skill_dir: Path) -> tuple[bool, str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return False, "missing SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False, "missing frontmatter"
    if not re.match(r"^---\n.*?\n---", text, flags=re.S):
        return False, "invalid frontmatter block"
    name = frontmatter_name(skill_md)
    if not name:
        return False, "missing frontmatter name"
    if not re.match(r"^[a-z0-9-]+$", name):
        return False, f"invalid skill name: {name}"
    if "description:" not in text.split("---", 2)[1]:
        return False, "missing frontmatter description"
    return True, "valid"


def installable_skill_index(source_repo: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for skill_md in sorted((source_repo / "skills").glob("*/*/SKILL.md")):
        skill_dir = skill_md.parent
        name = frontmatter_name(skill_md) or skill_dir.name
        existing = index.get(name)
        if existing is not None:
            fail(f"duplicate installable skill name {name}: {existing} and {skill_dir}")
        index[name] = skill_dir
    return index


def installed_project_skills(project: Path) -> list[Path]:
    skills_dir = project / ".agents" / "skills"
    if not skills_dir.is_dir():
        fail(f"target project has no .agents/skills directory: {project}")
    return sorted(path for path in skills_dir.iterdir() if (path / "SKILL.md").is_file())


def copy_skill(source: Path, destination: Path, dry_run: bool) -> None:
    if dry_run:
        return
    temporary = destination.with_name(f".{destination.name}.sync-tmp")
    if temporary.exists():
        shutil.rmtree(temporary)
    shutil.copytree(source, temporary, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    if destination.exists():
        shutil.rmtree(destination)
    temporary.rename(destination)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update already-installed .agents/skills from skills-sync-lqy installable skills."
    )
    parser.add_argument("project", type=Path, help="Project root containing .agents/skills")
    parser.add_argument("--repo-url", default=None, help=f"Git repository to clone/pull. Default: {DEFAULT_REPO_URL}")
    parser.add_argument("--source", type=Path, default=None, help="Existing local skills-sync-lqy repo path")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Clone cache dir for --repo-url")
    parser.add_argument("--dry-run", action="store_true", help="Print what would change without copying")
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    if not project.is_dir():
        fail(f"project does not exist: {project}")

    source_repo = resolve_source_repo(args.repo_url, args.source, args.cache_dir)
    source_index = installable_skill_index(source_repo)
    installed = installed_project_skills(project)

    synced: list[str] = []
    skipped: list[str] = []
    failed_validation: list[str] = []

    for destination in installed:
        name = frontmatter_name(destination / "SKILL.md") or destination.name
        source = source_index.get(name)
        if source is None:
            skipped.append(f"{name} (no matching installable source)")
            continue

        valid, message = validate_skill_dir(source)
        if not valid:
            failed_validation.append(f"{name}: source invalid: {message}")
            continue

        copy_skill(source, destination, args.dry_run)
        synced.append(name)

        if not args.dry_run:
            valid, message = validate_skill_dir(destination)
            if not valid:
                failed_validation.append(f"{name}: synced copy invalid: {message}")

    mode = "DRY RUN" if args.dry_run else "UPDATED"
    print(f"{mode}: {project}")
    print(f"source: {source_repo}")
    print(f"synced ({len(synced)}):")
    for name in synced:
        print(f"  - {name}")
    print(f"skipped ({len(skipped)}):")
    for item in skipped:
        print(f"  - {item}")

    if failed_validation:
        print("validation failures:", file=sys.stderr)
        for item in failed_validation:
            print(f"  - {item}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
