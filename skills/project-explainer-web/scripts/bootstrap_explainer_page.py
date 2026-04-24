#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import hashlib
import re
import sys
import unicodedata


TRANSLATIONS = {
    "zh": {
        "html_lang": "zh-CN",
        "default_title": "项目说明页",
        "default_project": "当前项目",
        "default_task": "当前任务",
        "scope_project": "项目",
        "scope_task": "任务",
        "eyebrow": "{{SCOPE_LABEL}}学习说明页",
        "hero_hint": "请把这里替换为一段简明说明：这个项目或任务要解决什么、当前重点是什么、读完后应该理解什么。",
        "meta_scope": "范围",
        "meta_language": "语言",
        "meta_project": "项目",
        "meta_task": "任务",
        "meta_updated": "更新日期",
        "lang_name": "中文",
        "tag_overview": "总览",
        "tag_context": "背景",
        "tag_tree": "结构树",
        "tag_flow": "流程",
        "tag_code": "代码地图",
        "tag_knowledge": "知识树",
        "tag_risk": "约束",
        "tag_recommend": "建议",
        "tag_action": "行动",
        "section_what": "这是什么",
        "section_what_sub": "先给结论，再给细节。",
        "section_what_body": "请用 3-5 条要点说明目标、边界、当前重点和最终想解决的问题。",
        "section_why": "为什么重要",
        "section_why_sub": "说明价值、影响范围和收益。",
        "problem_label": "问题",
        "problem_body": "这里写业务问题、工程问题，或当前决策难点。",
        "outcome_label": "目标结果",
        "outcome_body": "这里写理想状态、成功标准或预期收益。",
        "section_structure_tree": "涉及部分结构树",
        "section_structure_tree_sub": "必须明确哪些部分会被涉及，以及每一部分的具体功能。",
        "structure_tree_body": "请把项目/任务涉及的模块按树状结构列出来，并在节点后标注功能说明。",
        "section_arch": "架构一览",
        "section_arch_sub": "用最小卡片说明相关层和职责。",
        "arch_a": "层 / 模块 A",
        "arch_a_body": "说明它负责什么。",
        "arch_b": "层 / 模块 B",
        "arch_b_body": "说明它负责什么。",
        "arch_c": "层 / 模块 C",
        "arch_c_body": "说明它负责什么。",
        "section_flow": "相关流程如何工作",
        "section_flow_sub": "按顺序解释关键路径。",
        "flow_1": "1. 输入进入系统",
        "flow_1_body": "说明第一步发生了什么。",
        "flow_2": "2. 核心逻辑执行",
        "flow_2_body": "说明中间如何处理、分发或决策。",
        "flow_3": "3. 输出或状态产生",
        "flow_3_body": "说明最后结果是什么。",
        "section_files": "优先阅读的关键文件",
        "section_files_sub": "让后续开发者快速定位代码。",
        "file_1": "src/example.ts",
        "file_1_body": "说明这个文件为什么重要。",
        "file_2": "src/feature/service.ts",
        "file_2_body": "说明这个文件里应该重点看什么。",
        "file_3": "docs/decision.md",
        "file_3_body": "说明它补充了什么背景。",
        "section_tech_tree": "相关技术知识结构树",
        "section_tech_tree_sub": "如果涉及技术，必须把相关技术点按结构排序，方便知道涉及哪些内容。",
        "tech_tree_body": "请把相关框架、运行时、协议、核心概念、参数、权衡点按树状结构列出。",
        "section_knowledge": "原理与背景知识",
        "section_knowledge_sub": "补充完成这项工作前必须理解的知识。",
        "concept_1": "概念 1",
        "concept_1_body": "用通俗语言解释这个概念。",
        "concept_2": "概念 2",
        "concept_2_body": "说明这个概念在当前项目里的意义。",
        "section_risks": "约束与风险",
        "section_risks_sub": "先明确边界，再谈方案。",
        "constraint_label": "已知约束",
        "constraint_body": "说明一个技术、产品或架构约束。",
        "risk_label": "开放风险",
        "risk_body": "说明一个还不确定的风险或权衡点。",
        "section_recommend": "推荐方案",
        "section_recommend_sub": "给出当前最值得采用的方向。",
        "recommend_body": "请写推荐方案、为什么推荐、以及它相对其他方案的优劣。",
        "section_actions": "下一步行动",
        "section_actions_sub": "让读者知道接下来该做什么。",
        "action_1": "步骤 1",
        "action_1_body": "写下第一个可执行动作。",
        "action_2": "步骤 2",
        "action_2_body": "写下后续动作。",
        "footer": "保持页面简单、基于证据、并且方便持续更新。",
        "language_code": "zh",
    },
    "en": {
        "html_lang": "en",
        "default_title": "Project Explainer",
        "default_project": "Current Project",
        "default_task": "Current Task",
        "scope_project": "Project",
        "scope_task": "Task",
        "eyebrow": "{{SCOPE_LABEL}} explainer page",
        "hero_hint": "Replace this with a short explanation of what this project or task is trying to do, what matters now, and what the reader should understand after reading.",
        "meta_scope": "Scope",
        "meta_language": "Language",
        "meta_project": "Project",
        "meta_task": "Task",
        "meta_updated": "Updated",
        "lang_name": "English",
        "tag_overview": "Overview",
        "tag_context": "Context",
        "tag_tree": "Structure tree",
        "tag_flow": "Flow",
        "tag_code": "Code map",
        "tag_knowledge": "Knowledge tree",
        "tag_risk": "Constraints",
        "tag_recommend": "Recommendation",
        "tag_action": "Actions",
        "section_what": "What this is",
        "section_what_sub": "Lead with the answer, then add detail.",
        "section_what_body": "Use 3-5 bullets to explain the goal, boundaries, current focus, and what this work is meant to solve.",
        "section_why": "Why it matters",
        "section_why_sub": "Explain value, impact, and why this subject deserves attention.",
        "problem_label": "Problem",
        "problem_body": "Describe the business problem, engineering problem, or current decision challenge.",
        "outcome_label": "Desired outcome",
        "outcome_body": "Describe success, target state, or expected benefit.",
        "section_structure_tree": "Affected structure tree",
        "section_structure_tree_sub": "Explicitly show which parts are involved and what each part does.",
        "structure_tree_body": "List the involved modules as a tree and annotate each node with its concrete responsibility.",
        "section_arch": "Architecture at a glance",
        "section_arch_sub": "Use small cards to summarize the relevant layers and responsibilities.",
        "arch_a": "Layer / Module A",
        "arch_a_body": "Explain what it owns.",
        "arch_b": "Layer / Module B",
        "arch_b_body": "Explain what it owns.",
        "arch_c": "Layer / Module C",
        "arch_c_body": "Explain what it owns.",
        "section_flow": "How the flow works",
        "section_flow_sub": "Explain the important path in order.",
        "flow_1": "1. Input enters the system",
        "flow_1_body": "Describe the first important event.",
        "flow_2": "2. Core logic runs",
        "flow_2_body": "Describe how the system processes, dispatches, or decides.",
        "flow_3": "3. Output or state is produced",
        "flow_3_body": "Describe the resulting output or state change.",
        "section_files": "Key files to read first",
        "section_files_sub": "Point the next developer to the right code quickly.",
        "file_1": "src/example.ts",
        "file_1_body": "Explain why this file matters.",
        "file_2": "src/feature/service.ts",
        "file_2_body": "Explain what to inspect here.",
        "file_3": "docs/decision.md",
        "file_3_body": "Explain what context this document adds.",
        "section_tech_tree": "Related technology tree",
        "section_tech_tree_sub": "If technology is involved, sort the related technical topics as a tree so the reader can see what is involved.",
        "tech_tree_body": "List the related frameworks, runtimes, protocols, concepts, parameters, and tradeoffs as a structured tree.",
        "section_knowledge": "Principles and background knowledge",
        "section_knowledge_sub": "Teach the minimum knowledge needed before changing this area.",
        "concept_1": "Concept 1",
        "concept_1_body": "Explain the concept in plain language.",
        "concept_2": "Concept 2",
        "concept_2_body": "Explain why it matters in this repository.",
        "section_risks": "Constraints and risks",
        "section_risks_sub": "Capture the boundaries before proposing a solution.",
        "constraint_label": "Known constraint",
        "constraint_body": "Describe a technical, product, or architectural constraint.",
        "risk_label": "Open risk",
        "risk_body": "Describe a current uncertainty or tradeoff.",
        "section_recommend": "Recommended solution",
        "section_recommend_sub": "State the best current direction and why.",
        "recommend_body": "Write the recommended approach, why it is preferred, and how it compares with alternatives.",
        "section_actions": "Next actions",
        "section_actions_sub": "Leave the reader with practical next steps.",
        "action_1": "Step 1",
        "action_1_body": "Describe the first actionable step.",
        "action_2": "Step 2",
        "action_2_body": "Describe the follow-up step.",
        "footer": "Keep this page simple, evidence-based, and easy to maintain.",
        "language_code": "en",
    },
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_only = ascii_only.replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]+", "-", ascii_only)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if slug:
        return slug
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"explainer-{digest}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy the minimal explainer page template into a target directory."
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        help=(
            "Directory that should receive the page. "
            "If omitted, write to <repo-root>/_learn_web/<scope>-<ascii-slug>/."
        ),
    )
    parser.add_argument(
        "--filename",
        default="index.html",
        help="Output filename inside the target directory (default: index.html)",
    )
    parser.add_argument("--title", help="Page title shown in the browser tab and hero section")
    parser.add_argument("--project", help="Short project name shown in the hero metadata")
    parser.add_argument("--task", help="Short task label shown in the hero metadata")
    parser.add_argument(
        "--scope",
        choices=("project", "task"),
        default="task",
        help="Whether this page explains a project or a task (default: task)",
    )
    parser.add_argument(
        "--language",
        choices=("zh", "en"),
        default="zh",
        help="Page language (default: zh)",
    )
    parser.add_argument(
        "--slug",
        help=(
            "ASCII folder slug used under _learn_web when target_dir is omitted. "
            "If omitted, derive one from task, project, or title; non-ASCII input falls back to an ASCII hash slug."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used when target_dir is omitted (default: current working directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    i18n = TRANSLATIONS[args.language]

    title = args.title or i18n["default_title"]
    project = args.project or i18n["default_project"]
    task = args.task or i18n["default_task"]
    scope_label = i18n[f"scope_{args.scope}"]

    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "minimal-explainer-site" / "index.html"

    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1

    if args.target_dir:
        target_dir = Path(args.target_dir).resolve()
    else:
        repo_root = Path(args.repo_root).resolve()
        derived = task if args.scope == "task" else project
        folder_slug = slugify(args.slug or derived or title)
        target_dir = repo_root / "_learn_web" / f"{args.scope}-{folder_slug}"

    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / args.filename

    if output_path.exists() and not args.force:
        print(
            f"Refusing to overwrite existing file without --force: {output_path}",
            file=sys.stderr,
        )
        return 2

    content = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{PAGE_TITLE}}": title,
        "{{PROJECT_NAME}}": project,
        "{{TASK_NAME}}": task,
        "{{SCOPE_LABEL}}": scope_label,
        "{{LAST_UPDATED}}": datetime.now().strftime("%Y-%m-%d"),
    }
    replacements.update({f"{{{{{key.upper()}}}}}": value for key, value in i18n.items()})

    for needle, value in replacements.items():
        content = content.replace(needle, value)

    output_path.write_text(content, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
