#!/usr/bin/env python3
"""Repository guardrail for Matt Pocock LQY skill maintenance.

Checks that installable Matt skills are the self-contained LQY layer, while
Chinese baselines and English upstream mirrors remain outside top-level skills/.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
ZH_BASELINE = ROOT / "baselines" / "matt-zh"
UPSTREAM = ROOT / "upstream" / "mattpocock" / "skills"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
EXPECTED_MATT_LQY_COUNT = 35
EXPECTED_MATT_ZH_COUNT = 38
EXPECTED_UPSTREAM_COUNT = 38
EXPECTED_INSTALLABLE_COUNT = 50
POLLUTION_PATTERNS = [
    "这是 Matt Pocock",
    "中文本地化版本",
    "官方英文上游",
    "本地化说明",
    "upstream/mattpocock",
    "中文团队习惯",
]
FORBIDDEN_ZH_TERMS = [
    "烧烤",
    "拷问",
    "盘问",
    "采访",
    "特工",
    "降价",
    "回购",
    "代币",
    "深度模块",
    "深化模块",
    "设计树",
    "工作流程",
    "需求信息",
    "准备代理",
    "准备人员",
    "国家角色",
    "存储桶",
    "更新的图片",
    "/追问",
    "/领域建模",
    "/domain modeling",
    "/griling",
    "领领域",
    "领domain",
    "表面架构",
    "简单的英语",
    "人工智能导航",
    "票证",
    "门票",
    "故障单",
    "座席",
    "令牌",
    "经纪人",
    "公关",
    "每个人居住",
    "深层模块",
    "受过训练",
    "代理简介",
    "问题文件",
    "美人鱼",
    "代理人",
    "客服人员",
    "解释器",
    "解释者",
    "健全性检查",
    "固执己见",
    "发射它",
    "解雇",
    "懒惰地",
    "有人居住",
    "每个人",
]
REQUIRED_CONTEXT_TERMS = [
    "追问",
    "追问会话",
    "追问循环",
    "Agent",
    "Issue",
    "Issue tracker",
    "Ticket",
    "Triage",
    "Brief",
    "Explainer",
    "工作流",
    "深模块",
    "模块加深",
    "接缝",
    "设计决策树",
    "Markdown",
    "仓库",
    "Token",
    "Context map",
    "按需创建",
]
ENGLISH_COMMANDS = [
    "/grilling",
    "/setup-matt-pocock-skills",
    "/tdd",
    "/triage",
    "/to-issues",
    "/to-spec",
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
    installable_lqy = sorted(SKILLS.glob("matt-lqy-*/*-lqy/SKILL.md"))
    installable_zh = sorted(SKILLS.glob("matt-zh-*/*-zh/SKILL.md"))
    zh_baselines = sorted(ZH_BASELINE.glob("matt-zh-*/*-zh/SKILL.md"))
    upstream = list_skill_dirs(UPSTREAM)

    if len(installable) != EXPECTED_INSTALLABLE_COUNT:
        fail(errors, f"expected {EXPECTED_INSTALLABLE_COUNT} installable skills, found {len(installable)}")
    if len(installable_lqy) != EXPECTED_MATT_LQY_COUNT:
        fail(errors, f"expected {EXPECTED_MATT_LQY_COUNT} installable Matt lqy skills, found {len(installable_lqy)}")
    if installable_zh:
        fail(errors, "Matt zh baseline must not be installable under skills/: " + ", ".join(rel(p.parent) for p in installable_zh[:10]))
    if len(zh_baselines) != EXPECTED_MATT_ZH_COUNT:
        fail(errors, f"expected {EXPECTED_MATT_ZH_COUNT} non-installable Matt zh baselines, found {len(zh_baselines)}")
    if len(upstream) != EXPECTED_UPSTREAM_COUNT:
        fail(errors, f"expected {EXPECTED_UPSTREAM_COUNT} upstream Matt mirrors, found {len(upstream)}")

    forbidden_top_level = {"engineering", "productivity", "personal", "misc", "in-progress", "deprecated"}
    present = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    leaked = sorted(forbidden_top_level & present)
    if leaked:
        fail(errors, "official Matt categories must not be under skills/: " + ", ".join(leaked))


def check_readme_codex_setup_usage(errors: list[str]) -> None:
    text = (ROOT / "README.md").read_text()
    required = "$setup-matt-pocock-skills-lqy"
    forbidden_preferred = "$setup-matt-pocock-skills-zh"
    slash = "/setup-matt-pocock-skills-lqy"
    if required not in text:
        fail(errors, "README Quickstart must prefer Codex $setup-matt-pocock-skills-lqy usage")
    if forbidden_preferred in text:
        fail(errors, "README must not present $setup-matt-pocock-skills-zh as the installable setup skill")
    if slash in text and text.find(slash) < text.find(required):
        fail(errors, "README must mention $setup-matt-pocock-skills-lqy before slash-style setup usage")


def check_lqy_layer_links(errors: list[str]) -> None:
    for skill_md in sorted(SKILLS.glob("matt-lqy-*/*-lqy/SKILL.md")):
        skill_dir = skill_md.parent
        loc = skill_dir / "LOCALIZATION.md"
        if not loc.exists():
            fail(errors, f"missing LOCALIZATION.md for LQY skill {rel(skill_dir)}")
            continue
        provenance = loc.read_text()
        zh_match = re.search(r"Chinese baseline path: `([^`]+)`", provenance)
        upstream_match = re.search(r"Upstream path: `([^`]+)`", provenance)
        if not zh_match:
            fail(errors, f"LQY skill provenance must point to corresponding zh baseline: {rel(skill_dir)}")
        elif not (ROOT / zh_match.group(1) / "SKILL.md").exists():
            fail(errors, f"LQY zh baseline does not exist for {rel(skill_dir)}: {zh_match.group(1)}")
        if not upstream_match:
            fail(errors, f"LQY skill provenance must point to official upstream mirror: {rel(skill_dir)}")
        elif not (ROOT / upstream_match.group(1) / "SKILL.md").exists():
            fail(errors, f"LQY upstream SKILL.md does not exist for {rel(skill_dir)}: {upstream_match.group(1)}")

        name = read_frontmatter_name(skill_md)
        if name != skill_dir.name:
            fail(errors, f"frontmatter name mismatch in {rel(skill_md)}: expected {skill_dir.name}, got {name}")
        if not skill_dir.name.endswith("-lqy"):
            fail(errors, f"Matt LQY skill dir must end with -lqy: {rel(skill_dir)}")


def check_marketplace(errors: list[str]) -> None:
    data = json.loads(MARKETPLACE.read_text())
    listed: list[str] = []
    for plugin in data.get("plugins", []):
        for skill in plugin.get("skills", []):
            normalized = skill.removeprefix("./")
            listed.append(normalized)
            if normalized.startswith("upstream/") or normalized.startswith("baselines/"):
                fail(errors, f"marketplace must not list non-installable mirror/baseline: {skill}")
            if "/matt-zh-" in normalized or normalized.endswith("-zh"):
                fail(errors, f"marketplace must list Matt LQY layer, not zh baseline: {skill}")
            if re.search(r"skills/(engineering|productivity|personal|misc|in-progress|deprecated)/", normalized):
                fail(errors, f"marketplace must not list official English Matt skill: {skill}")

    discovered = sorted(rel(path.parent) for path in SKILLS.glob("*/*/SKILL.md"))
    if sorted(listed) != discovered:
        missing = sorted(set(discovered) - set(listed))
        extra = sorted(set(listed) - set(discovered))
        fail(errors, f"marketplace mismatch; missing={missing}; extra={extra}")


def check_zh_baseline_links(errors: list[str]) -> None:
    for skill_md in sorted(ZH_BASELINE.glob("matt-zh-*/*-zh/SKILL.md")):
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
            fail(errors, f"Matt zh baseline dir must end with -zh: {rel(skill_dir)}")


def check_context_glossary(errors: list[str]) -> None:
    context = ROOT / "CONTEXT.md"
    if not context.exists():
        fail(errors, "missing root CONTEXT.md glossary for Matt zh terminology")
        return
    text = context.read_text()
    for term in REQUIRED_CONTEXT_TERMS:
        if f"**{term}**" not in text:
            fail(errors, f"CONTEXT.md missing required glossary term: {term}")


def check_matt_body_clean(errors: list[str]) -> None:
    for skill_md in sorted(SKILLS.glob("matt-lqy-*/*-lqy/SKILL.md")) + sorted(ZH_BASELINE.glob("matt-zh-*/*-zh/SKILL.md")):
        text = skill_md.read_text()
        body = text.split("---", 2)[-1]
        for pattern in POLLUTION_PATTERNS:
            if pattern in body:
                fail(errors, f"localization maintenance text leaked into {rel(skill_md)}: {pattern}")

        suffix = "-lqy" if "/matt-lqy-" in rel(skill_md) else "-zh"
        for command in ENGLISH_COMMANDS:
            if command in body and f"{command}{suffix}" not in body:
                fail(errors, f"possible English command reference in {rel(skill_md)}: {command}")

    for md in sorted(SKILLS.glob("matt-lqy-*/*-lqy/**/*.md")) + sorted(ZH_BASELINE.glob("matt-zh-*/*-zh/**/*.md")):
        if md.name == "LOCALIZATION.md":
            continue
        text = md.read_text()
        for term in FORBIDDEN_ZH_TERMS:
            if term in text:
                fail(errors, f"forbidden inconsistent term in {rel(md)}: {term}")


def check_translation_shape(errors: list[str]) -> None:
    for skill_md in sorted(ZH_BASELINE.glob("matt-zh-*/*-zh/SKILL.md")):
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
    check_readme_codex_setup_usage(errors)
    check_lqy_layer_links(errors)
    check_context_glossary(errors)
    check_zh_baseline_links(errors)
    check_matt_body_clean(errors)
    check_translation_shape(errors)
    run_quick_validate(errors)

    if errors:
        print("Matt LQY skill checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Matt LQY skill checks passed")
    print(f"installable skills: {len(list_skill_dirs(SKILLS))}")
    print(f"installable Matt LQY skills: {len(list(SKILLS.glob('matt-lqy-*/*-lqy/SKILL.md')))}")
    print(f"non-installable Matt zh baselines: {len(list(ZH_BASELINE.glob('matt-zh-*/*-zh/SKILL.md')))}")
    print(f"upstream Matt mirrors: {len(list_skill_dirs(UPSTREAM))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
