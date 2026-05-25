#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import hashlib
import re
import shutil
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
        "hero_hint_project": "请用项目视角说明：系统目标是什么、当前架构重点是什么、这页会帮助读者建立哪些全局理解。",
        "hero_hint_task": "请用任务视角说明：当前要完成什么改动、它影响哪条链路、读完后读者应知道下一步如何执行。",
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
        "section_what_body_project": "请用 3-5 条要点说明项目目标、系统边界、主要子系统、当前演进重点，以及整体上要解决的问题。",
        "section_what_body_task": "请用 3-5 条要点说明这次任务的目标、影响范围、前后依赖、当前阻塞点，以及本次变更要真正解决的问题。",
        "section_why": "为什么重要",
        "section_why_sub": "说明价值、影响范围和收益。",
        "problem_label": "问题",
        "problem_body": "这里写业务问题、工程问题，或当前决策难点。",
        "outcome_label": "目标结果",
        "outcome_body": "这里写理想状态、成功标准或预期收益。",
        "section_structure_tree": "涉及部分结构树",
        "section_structure_tree_sub": "必须明确哪些部分会被涉及，以及每一部分的具体功能。",
        "structure_tree_body": "请把项目/任务涉及的模块按树状结构列出来，并在节点后标注功能说明。",
        "structure_tree_text": "src/\n├─ module-a/    这里写第一层目录和职责\n├─ module-b/    这里写第二层目录和职责\n└─ shared/      这里写共享层和它服务谁",
        "section_arch": "架构一览",
        "section_arch_sub": "用架构图和最小卡片说明相关层、边界和职责。",
        "arch_a": "层 / 模块 A",
        "arch_a_body": "说明它负责什么。",
        "arch_b": "层 / 模块 B",
        "arch_b_body": "说明它负责什么。",
        "arch_c": "层 / 模块 C",
        "arch_c_body": "说明它负责什么。",
        "section_sequence": "时序 / 交互图",
        "section_sequence_sub": "用 Mermaid sequenceDiagram 说明关键参与者如何按时间交互。",
        "sequence_1": "用户 / 入口",
        "sequence_1_body": "提供目标、请求、事件或任务输入。",
        "sequence_2": "拥有逻辑",
        "sequence_2_body": "读取上下文、做出决策、调用状态或外部依赖。",
        "sequence_3": "证据 / 输出",
        "sequence_3_body": "产出结果、日志、测试或需要人工确认的证据。",
        "section_flow": "相关流程如何工作",
        "section_flow_sub": "按顺序解释关键路径。",
        "section_flow_sub_project": "优先解释系统级主链路，以及跨模块如何协作。",
        "section_flow_sub_task": "优先解释当前任务真正会改动的那条链路，而不是泛泛介绍整个系统。",
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
        "section_runtime": "运行原理",
        "section_runtime_sub": "说明入口、状态模型、正常路径和失败路径。",
        "runtime_1": "入口 / 调度",
        "runtime_1_body": "这里写请求、CLI、Hook、路由、任务或事件从哪里进入。",
        "runtime_2": "状态 / 控制流",
        "runtime_2_body": "这里写状态在哪里变化，控制权如何在模块间传递。",
        "runtime_3": "失败 / 证据",
        "runtime_3_body": "这里写失败时看什么日志、命令或测试。",
        "section_evidence": "Source of truth / 证据地图",
        "section_evidence_sub": "说明哪些结论来自直接证据，哪些是推断，哪些仍有开放问题。",
        "evidence_1": "package.json / build config",
        "evidence_1_body": "这里写栈、脚本、运行方式等结论来自哪些 manifest 或 build 文件。",
        "evidence_2": "关键源码 / 日志 / diff",
        "evidence_2_body": "这里写主要行为判断来自哪些源码文件、错误日志或最近变更。",
        "evidence_3": "开放问题",
        "evidence_3_body": "这里写目前还不能 100% 确认、需要进一步验证的点。",
        "section_tech_tree": "相关技术知识结构树",
        "section_tech_tree_sub": "如果涉及技术，必须把相关技术点按结构排序；如果不涉及，请在首次内容更新时标记不适用或删除本节。",
        "tech_tree_body": "请把相关框架、运行时、协议、核心概念、参数、权衡点按树状结构列出。",
        "tech_tree_text": "技术栈/主题\n├─ 框架 / 运行时        这里写核心框架、版本和职责\n├─ 协议 / 接口          这里写通信方式、数据契约或外部依赖\n├─ 核心概念 / 模型      这里写必须理解的抽象\n└─ 权衡 / 限制          这里写关键参数、限制与设计取舍",
        "section_boundaries": "边界与不变量",
        "section_boundaries_sub": "说明哪些职责边界不能被随意打破，哪些规则必须被未来修改保持。",
        "boundary_1": "边界 1",
        "boundary_1_body": "这里写一个关键 ownership / layering boundary。",
        "boundary_2": "不变量 1",
        "boundary_2_body": "这里写一个必须持续保持的系统不变量或反模式提醒。",
        "section_ai_blind_spots": "AI 盲点 / 不确定性",
        "section_ai_blind_spots_sub": "指出 AI 不能从静态代码里安全假设的内容。",
        "ai_blind_spot_1": "缺少运行时证据",
        "ai_blind_spot_1_body": "这里写需要日志、真实环境、凭证、配置或用户决策确认的点。",
        "ai_blind_spot_2": "容易越界的假设",
        "ai_blind_spot_2_body": "这里写 AI 可能误判 owner、边界或问题根因的地方。",
        "section_handoff_ai": "如何交付给 AI",
        "section_handoff_ai_sub": "把目标、边界、证据和停止条件写清楚，方便后续让 AI 做事。",
        "handoff_ai_1": "最小上下文包",
        "handoff_ai_1_body": "目标、范围内/外、关键文件、边界、不变量、验收证据。",
        "handoff_ai_2": "可改与不可擅自改",
        "handoff_ai_2_body": "说明 AI 可以先改哪里，哪些需要人确认或真实环境验证。",
        "section_debugging": "调试入口",
        "section_debugging_sub": "从症状走到 owner 层、根因和验证证据。",
        "debugging_1": "最快探针",
        "debugging_1_body": "这里写最小命令、日志、状态文件或页面来定位问题。",
        "debugging_2": "归因路径",
        "debugging_2_body": "这里写如何区分调用层、状态层、外部依赖和展示层。",
        "section_safe_change": "如何安全修改这里",
        "section_safe_change_sub": "给未来开发者一条安全变更路径，而不只是结构介绍。",
        "safe_change_1": "从哪里开始读",
        "safe_change_1_body": "这里写如果要改这一块，应该先读哪些文件、先理解哪一层。",
        "safe_change_2": "先改哪里，后改哪里",
        "safe_change_2_body": "这里写通常应该先改的 owning layer，以及哪些文件只应被连带修改。",
        "section_verify_commands": "验证命令",
        "section_verify_commands_sub": "列出最有价值的理解/验证命令，并说明每条命令证明什么。",
        "section_antipatterns": "Common anti-patterns / 常见误区",
        "section_antipatterns_sub": "指出最容易踩坑的做法，并解释为什么它们看起来方便、其实会伤害架构。",
        "section_antipatterns_sub_project": "优先指出会破坏系统边界、ownership 和长期可维护性的常见误区。",
        "section_antipatterns_sub_task": "优先指出这次任务里最容易出现的短路式修复、越层修改和验证偷懒。",
        "antipattern_1": "把临时修补扩散到多个层",
        "antipattern_1_body": "这里写一个典型误区：为什么它常见、短期看似省事、长期却会让 ownership 混乱或验证变难。",
        "antipattern_2": "跳过 fixture / 边界，直接在 spec 或调用点硬修",
        "antipattern_2_body": "这里写另一个典型误区：为什么它诱人、它会破坏什么边界，以及更好的替代方案是什么。",
        "verify_cmd_1": "npm run test",
        "verify_cmd_1_body": "这里写这条命令证明什么，成功/失败时意味着什么。",
        "verify_cmd_2": "npm run typecheck",
        "verify_cmd_2_body": "这里写这条命令主要验证哪一层的健康度。",
        "verify_cmd_3": "自定义检查命令",
        "verify_cmd_3_body": "这里写环境敏感或成本更高的命令，以及何时才该运行。",
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
        "section_recommend_sub_project": "从系统演进、可维护性和长期一致性角度给建议。",
        "section_recommend_sub_task": "从当前任务的最小安全改动路径、验证成本和回滚难度角度给建议。",
        "recommend_body": "请写推荐方案、为什么推荐、以及它相对其他方案的优劣。",
        "section_actions": "下一步行动",
        "section_actions_sub": "让读者知道接下来该做什么。",
        "section_actions_sub_project": "给出理解系统、验证判断、继续演进的下一步动作。",
        "section_actions_sub_task": "给出完成当前任务、验证结果、继续下一改动的顺序动作。",
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
        "hero_hint_project": "Use a project lens: explain the system goal, the current architectural focus, and what global understanding the reader should gain from this page.",
        "hero_hint_task": "Use a task lens: explain the change to deliver now, which path it affects, and what the reader should know to execute the next step safely.",
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
        "section_what_body_project": "Use 3-5 bullets to explain the project goal, system boundaries, major subsystems, current evolution focus, and the overall problem this system is meant to solve.",
        "section_what_body_task": "Use 3-5 bullets to explain the task goal, affected scope, upstream/downstream dependencies, current blocker, and the concrete problem this change is meant to solve.",
        "section_why": "Why it matters",
        "section_why_sub": "Explain value, impact, and why this subject deserves attention.",
        "problem_label": "Problem",
        "problem_body": "Describe the business problem, engineering problem, or current decision challenge.",
        "outcome_label": "Desired outcome",
        "outcome_body": "Describe success, target state, or expected benefit.",
        "section_structure_tree": "Structure / hierarchy diagram",
        "section_structure_tree_sub": "Explicitly show which parts are involved, how they are layered, and what each part does.",
        "structure_tree_body": "List the involved modules as a tree and annotate each node with its concrete responsibility.",
        "structure_tree_text": "src/\n├─ module-a/    write the directory and responsibility here\n├─ module-b/    write the directory and responsibility here\n└─ shared/      write the shared layer and who it serves",
        "section_arch": "Architecture at a glance",
        "section_arch_sub": "Use an architecture diagram and small cards to summarize layers, boundaries, and responsibilities.",
        "arch_a": "Layer / Module A",
        "arch_a_body": "Explain what it owns.",
        "arch_b": "Layer / Module B",
        "arch_b_body": "Explain what it owns.",
        "arch_c": "Layer / Module C",
        "arch_c_body": "Explain what it owns.",
        "section_sequence": "Sequence / interaction view",
        "section_sequence_sub": "Use Mermaid sequenceDiagram to show how the key participants interact over time.",
        "sequence_1": "User / entry",
        "sequence_1_body": "Provides the goal, request, event, or task input.",
        "sequence_2": "Owning logic",
        "sequence_2_body": "Reads context, decides, and calls state or external dependencies.",
        "sequence_3": "Evidence / output",
        "sequence_3_body": "Produces a result, log, test, or human-confirmed evidence.",
        "section_flow": "How the flow works",
        "section_flow_sub": "Explain the important path in order.",
        "section_flow_sub_project": "Prefer the system-level main path and how modules collaborate across boundaries.",
        "section_flow_sub_task": "Prefer the specific path this task changes, rather than describing the whole system at a high level.",
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
        "section_runtime": "Runtime principles",
        "section_runtime_sub": "Explain entry points, state model, normal path, and failure path.",
        "runtime_1": "Entry / scheduling",
        "runtime_1_body": "Describe where requests, CLI commands, hooks, routes, jobs, or events enter.",
        "runtime_2": "State / control flow",
        "runtime_2_body": "Describe where state changes and how control moves between modules.",
        "runtime_3": "Failure / evidence",
        "runtime_3_body": "Describe which logs, commands, or tests prove failures and recovery.",
        "section_evidence": "Source of truth / evidence map",
        "section_evidence_sub": "Show which conclusions are direct evidence, which are interpretation, and which points still need confirmation.",
        "evidence_1": "package.json / build config",
        "evidence_1_body": "Use this card to explain which stack or runtime conclusions come directly from manifests or build files.",
        "evidence_2": "Key source / logs / diff",
        "evidence_2_body": "Use this card to explain which behavior claims come from source files, logs, or recent changes.",
        "evidence_3": "Open question",
        "evidence_3_body": "Use this card to call out anything still uncertain or not yet verified.",
        "section_tech_tree": "Related technology tree",
        "section_tech_tree_sub": "If technology is involved, sort the related technical topics as a tree; if not, mark this not applicable or remove it during the first content pass.",
        "tech_tree_body": "List the related frameworks, runtimes, protocols, concepts, parameters, and tradeoffs as a structured tree.",
        "tech_tree_text": "Technology stack / topic\n├─ Framework / runtime    write the core frameworks, versions, and ownership\n├─ Protocol / interface   write the communication style, contracts, or external dependencies\n├─ Core concepts / model  write the abstractions the reader must understand\n└─ Tradeoffs / limits     write the key parameters, constraints, and design tradeoffs",
        "section_boundaries": "Boundaries and invariants",
        "section_boundaries_sub": "State which ownership rules, layer boundaries, and invariants future changes should preserve.",
        "boundary_1": "Boundary 1",
        "boundary_1_body": "Describe an important ownership or layering boundary.",
        "boundary_2": "Invariant 1",
        "boundary_2_body": "Describe a system invariant or anti-pattern warning that should remain true over time.",
        "section_ai_blind_spots": "AI blind spots / uncertainty",
        "section_ai_blind_spots_sub": "Call out what AI cannot safely assume from static code alone.",
        "ai_blind_spot_1": "Missing runtime evidence",
        "ai_blind_spot_1_body": "Describe anything that needs logs, real environment, credentials, config, or user decisions.",
        "ai_blind_spot_2": "Risky assumption",
        "ai_blind_spot_2_body": "Describe where AI may misread ownership, boundaries, or root cause.",
        "section_handoff_ai": "Handoff to AI",
        "section_handoff_ai_sub": "Make goals, boundaries, evidence, and stop conditions explicit before asking AI to act.",
        "handoff_ai_1": "Minimal context packet",
        "handoff_ai_1_body": "Objective, in/out scope, key files, boundaries, invariants, and acceptance evidence.",
        "handoff_ai_2": "Safe vs gated edits",
        "handoff_ai_2_body": "State what AI may edit first and what needs human confirmation or live verification.",
        "section_debugging": "Debugging guide",
        "section_debugging_sub": "Move from symptom to owner layer, root cause, and verification evidence.",
        "debugging_1": "Fastest probe",
        "debugging_1_body": "List the smallest command, log, state file, or page that localizes the issue.",
        "debugging_2": "Attribution path",
        "debugging_2_body": "Explain how to distinguish caller layer, state layer, external dependency, and presentation layer.",
        "section_safe_change": "How to modify this safely",
        "section_safe_change_sub": "Give future developers a safe change path, not just a description of the current structure.",
        "safe_change_1": "Where to start reading",
        "safe_change_1_body": "Explain which files or layers should be read first before modifying this area.",
        "safe_change_2": "What to change first vs second",
        "safe_change_2_body": "Explain the likely owning layer and which files should only change as a consequence.",
        "section_verify_commands": "Verification commands",
        "section_verify_commands_sub": "List the most valuable commands for understanding or validating the area and say what each command proves.",
        "section_antipatterns": "Common anti-patterns",
        "section_antipatterns_sub": "Call out the easiest mistakes to make and explain why they look convenient but damage the design.",
        "section_antipatterns_sub_project": "Prefer anti-patterns that break subsystem boundaries, ownership, or long-term maintainability.",
        "section_antipatterns_sub_task": "Prefer anti-patterns that tempt the current task toward shortcut fixes, cross-layer edits, or weak verification.",
        "antipattern_1": "Let a temporary fix leak across multiple layers",
        "antipattern_1_body": "Use this card for a mistake that feels fast in the short term but creates ownership confusion or harder verification later.",
        "antipattern_2": "Patch the spec or call site directly instead of the owning fixture / boundary",
        "antipattern_2_body": "Use this card for a mistake that looks convenient but bypasses the real abstraction and makes future behavior harder to reason about.",
        "verify_cmd_1": "npm run test",
        "verify_cmd_1_body": "Explain what this command proves and what success or failure means.",
        "verify_cmd_2": "npm run typecheck",
        "verify_cmd_2_body": "Explain which layer or boundary this command validates.",
        "verify_cmd_3": "Custom verification command",
        "verify_cmd_3_body": "Explain a more expensive or environment-sensitive command and when it should be run.",
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
        "section_recommend_sub_project": "Recommend from the perspective of system evolution, maintainability, and long-term consistency.",
        "section_recommend_sub_task": "Recommend from the perspective of the smallest safe change path, verification cost, and rollback difficulty for this task.",
        "recommend_body": "Write the recommended approach, why it is preferred, and how it compares with alternatives.",
        "section_actions": "Next actions",
        "section_actions_sub": "Leave the reader with practical next steps.",
        "section_actions_sub_project": "Leave the reader with concrete next steps for learning the system, validating the model, and evolving it safely.",
        "section_actions_sub_task": "Leave the reader with the exact sequence for completing this task, validating the result, and continuing the next change.",
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

    resolved_i18n = dict(i18n)
    for base_key in (
        "hero_hint",
        "section_what_body",
        "section_flow_sub",
        "section_recommend_sub",
        "section_antipatterns_sub",
        "section_actions_sub",
    ):
        scoped_key = f"{base_key}_{args.scope}"
        if scoped_key in i18n:
            resolved_i18n[base_key] = i18n[scoped_key]

    script_dir = Path(__file__).resolve().parent
    template_path = script_dir.parent / "assets" / "minimal-explainer-site" / "index.html"
    mermaid_asset_path = script_dir.parent / "assets" / "vendor" / "mermaid.min.js"

    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1
    if not mermaid_asset_path.exists():
        print(f"Bundled Mermaid asset not found: {mermaid_asset_path}", file=sys.stderr)
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
    assets_dir = target_dir / "assets"
    output_mermaid_asset_path = assets_dir / "mermaid.min.js"

    if output_path.exists() and not args.force:
        print(
            f"Refusing to overwrite existing file without --force: {output_path}",
            file=sys.stderr,
        )
        return 2

    content = template_path.read_text(encoding="utf-8")
    replacements = {f"{{{{{key.upper()}}}}}": value for key, value in resolved_i18n.items()}
    replacements.update({
        "{{PAGE_TITLE}}": title,
        "{{PROJECT_NAME}}": project,
        "{{TASK_NAME}}": task,
        "{{SCOPE_LABEL}}": scope_label,
        "{{LAST_UPDATED}}": datetime.now().strftime("%Y-%m-%d"),
    })

    for needle, value in replacements.items():
        content = content.replace(needle, value)

    output_path.write_text(content, encoding="utf-8")
    assets_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mermaid_asset_path, output_mermaid_asset_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
