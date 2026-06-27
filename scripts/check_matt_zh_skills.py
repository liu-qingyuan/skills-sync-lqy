#!/usr/bin/env python3
"""Repository guardrail for Matt Pocock Chinese skill maintenance.

Checks that installable Matt skills are clean Chinese forks, while English
upstream mirrors remain outside top-level skills/.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
UPSTREAM = ROOT / "upstream" / "mattpocock" / "skills"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
EXPECTED_MATT_ZH_COUNT = 35
EXPECTED_INSTALLABLE_COUNT = 49
POLLUTION_PATTERNS = [
    "这是 Matt Pocock",
    "中文本地化版本",
    "官方英文上游",
    "本地化说明",
    "upstream/mattpocock",
    "中文团队习惯",
]
ENGLISH_COMMANDS = [
    "/grilling",
    "/setup-matt-pocock-skills",
    "/tdd",
    "/triage",
    "/to-issues",
    "/to-prd",
    "/handoff",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_frontmatter_name(skill_md: Path) -> str | None:
    text = skill_md.read_text()
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.S)
    if not match:
        return None
    for line in match.group(1).splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"\'')
    return None


def list_skill_dirs(base: Path) -> list[Path]:
    return sorted(path.parent for path in base.glob("*/*/SKILL.md"))


def check_installable_boundary(errors: list[str]) -> None:
    installable = list_skill_dirs(SKILLS)
    matt_zh = sorted(SKILLS.glob("matt-zh-*/*-zh/SKILL.md"))
    upstream = list_skill_dirs(UPSTREAM)

    if len(installable) != EXPECTED_INSTALLABLE_COUNT:
        fail(errors, f"expected {EXPECTED_INSTALLABLE_COUNT} installable skills, found {len(installable)}")
    if len(matt_zh) != EXPECTED_MATT_ZH_COUNT:
        fail(errors, f"expected {EXPECTED_MATT_ZH_COUNT} Matt zh skills, found {len(matt_zh)}")
    if len(upstream) != EXPECTED_MATT_ZH_COUNT:
        fail(errors, f"expected {EXPECTED_MATT_ZH_COUNT} upstream Matt mirrors, found {len(upstream)}")

    forbidden_top_level = {"engineering", "productivity", "personal", "misc", "in-progress", "deprecated"}
    present = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    leaked = sorted(forbidden_top_level & present)
    if leaked:
        fail(errors, "official Matt categories must not be under skills/: " + ", ".join(leaked))


def check_marketplace(errors: list[str]) -> None:
    data = json.loads(MARKETPLACE.read_text())
    listed: list[str] = []
    for plugin in data.get("plugins", []):
        for skill in plugin.get("skills", []):
            normalized = skill.removeprefix("./")
            listed.append(normalized)
            if normalized.startswith("upstream/"):
                fail(errors, f"marketplace must not list upstream mirror: {skill}")
            if re.search(r"skills/(engineering|productivity|personal|misc|in-progress|deprecated)/", normalized):
                fail(errors, f"marketplace must not list official English Matt skill: {skill}")

    discovered = sorted(rel(path.parent) for path in SKILLS.glob("*/*/SKILL.md"))
    if sorted(listed) != discovered:
        missing = sorted(set(discovered) - set(listed))
        extra = sorted(set(listed) - set(discovered))
        fail(errors, f"marketplace mismatch; missing={missing}; extra={extra}")


def check_localization_links(errors: list[str]) -> None:
    for skill_md in sorted(SKILLS.glob("matt-zh-*/*-zh/SKILL.md")):
        skill_dir = skill_md.parent
        loc = skill_dir / "LOCALIZATION.md"
        if not loc.exists():
            fail(errors, f"missing LOCALIZATION.md for {rel(skill_dir)}")
            continue
        match = re.search(r"Upstream path: `([^`]+)`", loc.read_text())
        if not match:
            fail(errors, f"missing upstream path in {rel(loc)}")
            continue
        upstream_dir = ROOT / match.group(1)
        if not (upstream_dir / "SKILL.md").exists():
            fail(errors, f"upstream SKILL.md does not exist for {rel(skill_dir)}: {match.group(1)}")

        name = read_frontmatter_name(skill_md)
        if name != skill_dir.name:
            fail(errors, f"frontmatter name mismatch in {rel(skill_md)}: expected {skill_dir.name}, got {name}")
        if not skill_dir.name.endswith("-zh"):
            fail(errors, f"Matt zh skill dir must end with -zh: {rel(skill_dir)}")


def check_zh_body_clean(errors: list[str]) -> None:
    for skill_md in sorted(SKILLS.glob("matt-zh-*/*-zh/SKILL.md")):
        text = skill_md.read_text()
        body = text.split("---", 2)[-1]
        for pattern in POLLUTION_PATTERNS:
            if pattern in body:
                fail(errors, f"localization maintenance text leaked into {rel(skill_md)}: {pattern}")

        for command in ENGLISH_COMMANDS:
            if command in body and f"{command}-zh" not in body:
                fail(errors, f"possible English command reference in {rel(skill_md)}: {command}")


def check_translation_shape(errors: list[str]) -> None:
    for skill_md in sorted(SKILLS.glob("matt-zh-*/*-zh/SKILL.md")):
        loc = skill_md.with_name("LOCALIZATION.md")
        if not loc.exists():
            continue
        match = re.search(r"Upstream path: `([^`]+)`", loc.read_text())
        if not match:
            continue
        upstream_md = ROOT / match.group(1) / "SKILL.md"
        if not upstream_md.exists():
            continue
        zh_lines = len(skill_md.read_text().splitlines())
        up_lines = len(upstream_md.read_text().splitlines())
        # Frontmatter names/descriptions differ; allow small variance. Flag only likely truncation.
        if up_lines >= 20 and zh_lines < max(12, int(up_lines * 0.55)):
            fail(errors, f"possible incomplete translation: {rel(skill_md)} has {zh_lines} lines vs upstream {up_lines}")


def run_quick_validate(errors: list[str]) -> None:
    validator = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    if not validator.exists():
        fail(errors, f"quick_validate.py not found: {validator}")
        return
    for skill_dir in list_skill_dirs(SKILLS):
        result = subprocess.run([sys.executable, str(validator), str(skill_dir)], cwd=ROOT, text=True, capture_output=True)
        if result.returncode != 0:
            fail(errors, f"quick_validate failed for {rel(skill_dir)}\n{result.stdout}{result.stderr}")


def main() -> int:
    errors: list[str] = []
    check_installable_boundary(errors)
    check_marketplace(errors)
    check_localization_links(errors)
    check_zh_body_clean(errors)
    check_translation_shape(errors)
    run_quick_validate(errors)

    if errors:
        print("Matt zh skill checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Matt zh skill checks passed")
    print(f"installable skills: {len(list_skill_dirs(SKILLS))}")
    print(f"Matt zh skills: {len(list(SKILLS.glob('matt-zh-*/*-zh/SKILL.md')))}")
    print(f"upstream Matt mirrors: {len(list_skill_dirs(UPSTREAM))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
