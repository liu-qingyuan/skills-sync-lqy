#!/usr/bin/env python3
"""Validate the gitnexus-codex-wiki skill package and optional generated docs.

The checks are intentionally dependency-free so they can run in any Codex worker
without adding packages.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_SKILL_TERMS = {
    "codex_authors_docs": ["Codex reads", "Codex authors", "Codex can author", "Codex to create"],
    "gitnexus_context": ["GitNexus graph", "GitNexus index", "graph context"],
    "version_grounding": ["1.6.3", "gitnexus@1.6.3"],
    "index_first": ["gitnexus status", "gitnexus analyze", "missing index", "existing index"],
    "wiki_layers": ["overview.md", "module/parent", "leaf", "metadata"],
    "graph_evidence": ["call edges", "execution processes", "source file references", "graph evidence"],
    "large_repo_slicing": ["slice", "large repos", "large-context"],
    "native_wiki_boundary": ["native `gitnexus wiki`", "reference model", "not as this skill's execution engine"],
    "architecture_web_mode": ["architecture-web", "multi-page static architecture", "Feynman"],
    "architecture_web_semantic_guardrail": ["target repository", "target application", "target system", "被分析项目/系统"],
    "hybrid_mode": ["hybrid", "markdown-wiki"],
}

# Patterns that indicate unsupported positive claims. Negated guardrail text such
# as "do not describe a GitNexus-side Codex provider" is allowed and expected.
FORBIDDEN_POSITIVE_PATTERNS = [
    re.compile(r"codex subscription\s+(is|as|equals|works as|can be used as)\s+(?!not\b).*api key", re.I),
    re.compile(r"use (your )?codex subscription .*api key", re.I),
    re.compile(r"gitnexus\s+(has|includes|supports|ships with|provides)\s+(a\s+)?codex provider", re.I),
    re.compile(r"(?<!do not )(?<!never )configure\s+gitnexus\s+to\s+call\s+codex", re.I),
    re.compile(r"gitnexus\s+calls\s+codex\s+(to|for|when)", re.I),
]

REQUIRED_FILES = [
    "SKILL.md",
    "references/gitnexus-wiki-internals.md",
    "references/validation-checklist.md",
    "references/architecture-web-output.md",
    "scripts/validate-skill.py",
    "scripts/scaffold-wiki.py",
    "scripts/scaffold-architecture-web.py",
    "agents/openai.yaml",
]

OVERVIEW_HEADINGS = [
    "总览摘要",
    "为什么要先理解它",
    "真实源码目录树",
    "整体运行时结构图",
    "用户动作到运行时流程",
    "源码证据地图",
    "优先阅读文件",
    "技术框架图",
    "边界与不变量",
    "安全修改方式",
    "验证命令",
    "常见反模式",
    "原理与背景知识",
    "约束与风险",
    "推荐维护方案",
    "后续维护动作",
]

MODULE_HEADINGS = [
    "模块职责",
    "为什么存在",
    "真实源码目录树",
    "整体运行时结构图",
    "数据如何流动",
    "用户动作到运行时流程",
    "源码阅读入口",
    "源码证据地图",
    "优先阅读文件",
    "技术框架图",
    "边界与不变量",
    "安全修改方式",
    "源码证据",
    "验证命令",
    "常见反模式",
    "原理与背景知识",
    "约束与风险",
    "推荐维护方案",
    "后续维护动作",
]

PROJECT_EXPLAINER_STYLE_TERMS = ["--bg", "--panel", "--accent", "shell", "hero", "panel"]

META_FIELDS = [
    "generated_at",
    "repo",
    "git_commit",
    "gitnexus_version",
    "execution_boundary",
    "mode",
    "modules",
    "evidence_files",
]

OPTIONAL_META_POLICY_FIELDS = ["language", "visual_style", "entrypoint"]

MODULE_FIELDS = ["slug", "title", "source_files", "graph_commands", "evidence_refs", "verification_commands"]
FLOW_FIELDS = ["slug", "title", "entrypoints", "services", "graph_edges", "evidence_refs"]
PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|TBD|FIXME|PLACEHOLDER|LOREM IPSUM|REPLACE ME)\b", re.I)
NETWORK_SCRIPT_PATTERN = re.compile(r"<script\b[^>]*\bsrc=[\"'](?:https?:)?//", re.I)
CDN_NAME_PATTERN = re.compile(r"\b(cdnjs|jsdelivr|unpkg)\b", re.I)
SCRIPT_SRC_PATTERN = re.compile(r"<script\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.I)
LINK_HREF_PATTERN = re.compile(r"<link\b[^>]*\bhref=[\"']([^\"']+)[\"']", re.I)
IMG_SRC_PATTERN = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.I)
CSS_URL_PATTERN = re.compile(r"url\(\s*[\"']?([^\)\"']+)", re.I)
INTERACTIVE_PAYLOAD_PATTERN = re.compile(r"<script\b(?P<attrs>[^>]*\bdata-architecture-flow\b[^>]*)>(?P<body>.*?)</script>", re.I | re.S)
FLOW_GRAPH_CONTAINER_PATTERN = re.compile(r"\bdata-flow-graph\s*=\s*[\"']([^\"']+)[\"']", re.I)
INTERACTIVE_CONTAINER_PATTERN = re.compile(r"\bdata-flow-graph\s*=|\bdata-architecture-flow(?:-root)?\b|class=[\"'][^\"']*architecture-flow\b", re.I)
PRIMARY_STATIC_DIAGRAM_PATTERN = re.compile(
    r"\bgraph\s+TB\b|\bflowchart\s+(?:TB|TD|BT|LR|RL)\b|class\s*=\s*[\"'][^\"']*(?:mermaid|diagram-source|diagram-svg)[^\"']*[\"']|<svg\b",
    re.I,
)
ALLOWED_EDGE_TYPES = {"call", "ipc", "data", "error", "external", "test", "control"}
TAG_PATTERN = re.compile(r"<[^>]+>")
SCRIPT_STYLE_BLOCK_PATTERN = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.I | re.S)
HIDDEN_BLOCK_PATTERN = re.compile(
    r"<(?P<tag>[a-z0-9]+)\b(?P<attrs>[^>]*)>(?P<body>.*?)</(?P=tag)>",
    re.I | re.S,
)
EXPLICIT_HIDDEN_BLOCK_PATTERN = re.compile(
    r"<(?P<tag>[a-z0-9]+)\b(?P<attrs>[^>]*(?:\bhidden\b|display\s*:\s*none|visibility\s*:\s*hidden|aria-hidden\s*=\s*[\"']true[\"']|class\s*=\s*[\"'][^\"']*hidden)[^>]*)>(?P<body>.*?)</(?P=tag)>",
    re.I | re.S,
)
HEADING_PATTERN = re.compile(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", re.I | re.S)
MERMAID_BLOCK_PATTERN = re.compile(
    r"<(?:pre|div)\b[^>]*class=[\"'][^\"']*(?:mermaid|mermaid-source)[^\"']*[\"'][^>]*>(.*?)</(?:pre|div)>",
    re.I | re.S,
)
PRE_BLOCK_PATTERN = re.compile(r"<pre\b[^>]*>(.*?)</pre>", re.I | re.S)
RAW_GRAPH_PRE_PATTERN = re.compile(
    r"<pre\b(?P<attrs>[^>]*)>(?P<body>\s*(?:graph|flowchart)\s+(?:TB|TD|BT|LR|RL)\b.*?)</pre>",
    re.I | re.S,
)
DIAGRAM_SECTION_PATTERN = re.compile(
    r"<section\b(?P<attrs>[^>]*)>(?P<body>.*?)</section>",
    re.I | re.S,
)
MERMAID_EDGE_PATTERN = re.compile(
    r"(?P<src>[A-Za-z0-9_\-\u4e00-\u9fff]+)(?:\[[^\]]*\]|\([^\)]*\)|\{[^\}]*\})?\s*(?:-->|---|==>|-.->)\s*(?P<dst>[A-Za-z0-9_\-\u4e00-\u9fff]+)",
    re.I,
)

UNSAFE_MERMAID_LABEL_CHARS = re.compile(r"[/:()\\,;%#&|<>]")
MERMAID_LABEL_PATTERN = re.compile(
    r"(?P<id>[A-Za-z0-9_\-\u4e00-\u9fff]+)\s*(?P<shape>[\[\(\{])(?P<label>[^\]\)\}\n]+)(?P<close>[\]\)\}])"
)
COMPACT_OX_EDGE_PATTERN = re.compile(r"(?:---|-->|==>|-.->)[ox][A-Za-z0-9_\-]")

FORBIDDEN_FEYNMAN_REQUIREMENT_PATTERN = re.compile(
    r"(每页|每个页面|every page|all pages|each page)[^\n。；;]*(必须|must|required|include|包含)[^\n。；;]*费曼复述",
    re.I,
)
GENERIC_HIDDEN_CONTRACT_PATTERNS = [
    re.compile(r"this contract text supports strict validation", re.I),
    re.compile(r"uses renderer, preload, ipcmain", re.I),
    re.compile(r"hidden (generic )?contract", re.I),
]

# Semantic guardrail: architecture-web output must explain the target system,
# not the generated static website artifact. Navigation/footer mentions of
# index.html are allowed; artifact-centric diagrams and primary framing are not.
ARTIFACT_CENTRIC_PATTERNS = [
    re.compile(r"_learn_web", re.I),
    re.compile(r"architecture[- ]web flow", re.I),
    re.compile(r"codex\s*生成网页流程", re.I),
    re.compile(r"wiki-meta\.json", re.I),
    re.compile(r"evidence/\*\.json|evidence/[^\s<>'\"]+\.json", re.I),
    re.compile(r"modules/\*\.html|modules/[^\s<>'\"]+\.html", re.I),
    re.compile(r"\bIndex\[[^\]]*index\.html", re.I),
    re.compile(r"\bReader\[[^\]]*\]\s*-->", re.I),
    re.compile(r"\bWeb\[_learn_web", re.I),
    re.compile(r"\bFlow\[Architecture web flow", re.I),
]

TARGET_SYSTEM_PATTERNS = [
    re.compile(r"\b(user|operator|browser|app|application|system)\b", re.I),
    re.compile(r"\b(renderer|route|router|preload|electronapi|ipcmain|main process|runtime)\b", re.I),
    re.compile(r"\b(api|service|services|provider|storage|database|cloud|integration)\b", re.I),
    re.compile(r"\b(auth|session|chat|desktop|model|knowledge|download)\b", re.I),
    re.compile(r"src/[^\s<>'\"]+", re.I),
    re.compile(r"source:\s*[^\s<>'\"]+", re.I),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def contains_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def is_documented_invalid_example(text: str, line_start: int) -> bool:
    """Return true when a forbidden phrase appears in a labeled invalid example.

    The architecture-web reference intentionally includes short invalid
    snippets so readers can recognize provider-boundary mistakes. Those examples
    should remain testable documentation without weakening normal package scans.
    """
    context = text[max(0, line_start - 500) : line_start].lower()
    recent_lines = context.splitlines()[-8:]
    return any("invalid" in line or "forbidden" in line for line in recent_lines)


def unescape_html(text: str) -> str:
    return text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')


def is_network_url(value: str) -> bool:
    stripped = value.strip().strip("'\"")
    return stripped.startswith(("http://", "https://", "//")) or any(name in stripped.lower() for name in ("unpkg", "jsdelivr", "cdnjs", "//cdn"))


def has_interactive_flow(html: str) -> bool:
    return bool(INTERACTIVE_CONTAINER_PATTERN.search(html) or INTERACTIVE_PAYLOAD_PATTERN.search(html))


def extract_interactive_flow_payloads(html: str, path: Path | str = "<html>") -> list[Any]:
    payloads: list[Any] = []
    for match in INTERACTIVE_PAYLOAD_PATTERN.finditer(html):
        body = unescape_html(match.group("body")).strip()
        if not body:
            continue
        try:
            payloads.append(json.loads(body))
        except json.JSONDecodeError as exc:
            payloads.append({"__parse_error__": f"{path}: invalid interactive-flow JSON: {exc}"})
    return payloads


def extract_flow_graph_container_ids(html: str) -> list[str]:
    return [match.strip() for match in FLOW_GRAPH_CONTAINER_PATTERN.findall(html) if match.strip()]


def payload_graph_ids(payloads: list[Any]) -> tuple[set[str], list[str]]:
    ids: set[str] = set()
    duplicates: list[str] = []
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        graphs = payload.get("graphs")
        if not isinstance(graphs, list):
            continue
        for graph in graphs:
            if not isinstance(graph, dict):
                continue
            graph_id = str(graph.get("id", "")).strip()
            if not graph_id:
                continue
            if graph_id in ids:
                duplicates.append(graph_id)
            ids.add(graph_id)
    return ids, duplicates


def meta_requires_interactive_flow(meta: Any) -> bool:
    if not isinstance(meta, dict):
        return False
    if meta.get("diagram_mode") == "interactive-flow":
        return True
    interactive = meta.get("interactive_flow")
    if interactive is True or isinstance(interactive, dict):
        return True
    return "interactive-flow" in str(meta.get("diagram_strategy", "")).lower()


def validate_runtime_network_urls(path: Path, errors: list[str]) -> None:
    html = read_text(path)
    for label, pattern in (("script src", SCRIPT_SRC_PATTERN), ("link href", LINK_HREF_PATTERN), ("img src", IMG_SRC_PATTERN)):
        for value in pattern.findall(html):
            if is_network_url(value):
                fail(errors, f"{path} contains network runtime asset in {label}: {value}")
    for style_body in re.findall(r"<style\b[^>]*>(.*?)</style>", html, flags=re.I | re.S):
        for value in CSS_URL_PATTERN.findall(style_body):
            if is_network_url(value):
                fail(errors, f"{path} contains network runtime asset in CSS url(): {value}")


def hidden_attrs(attrs: str) -> bool:
    lowered = attrs.lower()
    return (
        "hidden" in lowered
        or "display:none" in lowered.replace(" ", "")
        or "visibility:hidden" in lowered.replace(" ", "")
        or "aria-hidden=\"true\"" in lowered
        or "aria-hidden='true'" in lowered
        or "class=\"hidden" in lowered
        or "class='hidden" in lowered
    )


def remove_hidden_blocks(html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return " " if hidden_attrs(match.group("attrs")) else match.group(0)

    previous = None
    current = html
    # Repeat because regex removal of nested-ish HTML is intentionally shallow.
    while previous != current:
        previous = current
        current = HIDDEN_BLOCK_PATTERN.sub(replace, current)
    return current


def visible_text(html: str) -> str:
    html = SCRIPT_STYLE_BLOCK_PATTERN.sub(" ", remove_hidden_blocks(html))
    return unescape_html(TAG_PATTERN.sub(" ", html))


def heading_texts(html: str) -> list[str]:
    return [visible_text(match.group(1)).strip() for match in HEADING_PATTERN.finditer(remove_hidden_blocks(html))]


def mermaid_sources(html: str) -> list[str]:
    sources: list[str] = []
    seen: set[str] = set()
    for pattern in (MERMAID_BLOCK_PATTERN, PRE_BLOCK_PATTERN):
        for match in pattern.finditer(html):
            source = visible_text(match.group(1)).strip()
            if not re.match(r"^(graph|flowchart)\s+(TB|TD|BT|LR|RL)\b", source, re.I):
                continue
            if source not in seen:
                seen.add(source)
                sources.append(source)
    return sources


def is_inside_closed_details(html: str, offset: int) -> bool:
    """Return true if offset sits inside a not-yet-closed <details> block.

    This is a lightweight HTML heuristic for the generated static pages. It is
    intentionally narrow: raw Mermaid source is acceptable as an inspectable
    source artifact only when it is collapsed behind <details>, not as the main
    visible diagram body.
    """
    before = html[:offset].lower()
    return before.rfind("<details") > before.rfind("</details>")


def section_heading(body: str) -> str:
    match = HEADING_PATTERN.search(body)
    return visible_text(match.group(1)).strip() if match else ""


def validate_no_visible_raw_graph_blocks(path: Path, allow_placeholders: bool, errors: list[str]) -> None:
    html = read_text(path)
    if allow_placeholders:
        return
    for match in RAW_GRAPH_PRE_PATTERN.finditer(html):
        attrs = match.group("attrs")
        klass_match = re.search(r"class=[\"']([^\"']+)[\"']", attrs, re.I)
        classes = klass_match.group(1).lower() if klass_match else ""
        if "diagram-source" not in classes and "mermaid-source" not in classes:
            continue
        if not is_inside_closed_details(html, match.start()):
            fail(
                errors,
                f"{path} exposes raw Mermaid graph source as visible page content; "
                "render it as SVG/local Mermaid and move source into collapsed <details>",
            )
            return
    for section in DIAGRAM_SECTION_PATTERN.finditer(html):
        body = section.group("body")
        heading = section_heading(body)
        if "技术框架图" in heading and not has_interactive_flow(html) and "<svg" not in body.lower() and "class=\"mermaid\"" not in body.lower() and "class='mermaid'" not in body.lower():
            fail(errors, f"{path} 技术框架图 section must contain a rendered SVG, local Mermaid render block, or valid interactive-flow contract elsewhere on the page")
        if re.search(r"</svg>\s*</div>\s*<pre\b[^>]*>\s*(?:graph|flowchart)\s+(?:TB|TD|BT|LR|RL)\b", body, re.I | re.S):
            fail(errors, f"{path} places raw graph source immediately after rendered SVG; wrap source in collapsed <details>")


def strip_allowed_non_primary_diagram_blocks(html: str) -> str:
    """Remove blocks where graph source/static previews are allowed for audit only.

    Full conversion is a page-wide contract: generated architecture-web pages
    must not keep Mermaid/source/SVG as visible primary or alternate diagrams.
    Collapsed source/audit details and explicit evidence/provenance blocks are
    still allowed so readers can inspect raw source or metadata.
    """
    stripped = SCRIPT_STYLE_BLOCK_PATTERN.sub(" ", html)
    patterns = [
        r"<details(?![^>]*\bopen\b)\b[^>]*>.*?</details>",
        r"<(?P<tag>section|div|aside)\b[^>]*(?:data-non-primary-diagram|data-evidence|data-provenance|class=[\"'][^\"']*(?:evidence|provenance|audit-source|source-audit|source-note)[^\"']*[\"'])[^>]*>.*?</(?P=tag)>",
    ]
    for pattern in patterns:
        previous = None
        while previous != stripped:
            previous = stripped
            stripped = re.sub(pattern, " ", stripped, flags=re.I | re.S)
    return stripped


def validate_no_visible_primary_static_diagrams(path: Path, errors: list[str]) -> None:
    html = strip_allowed_non_primary_diagram_blocks(read_text(path))
    if PRIMARY_STATIC_DIAGRAM_PATTERN.search(html):
        fail(
            errors,
            f"{path} has visible primary Mermaid/flowchart/static SVG diagram output; "
            "architecture-web primary dense diagrams must be React Flow, with raw/static sources only in collapsed audit/evidence/provenance blocks",
        )


def validate_interactive_runtime_source(skill_root: Path, errors: list[str]) -> None:
    source_path = skill_root / "assets" / "architecture-flow" / "src" / "architecture-flow.tsx"
    if not source_path.is_file():
        fail(errors, f"missing React Flow runtime source: {source_path}")
        return
    source = read_text(source_path)
    required = {
        "useNodesState": "persistent node state for manual drag",
        "onNodesChange": "React Flow node change handler",
        "nodesDraggable": "manual node dragging enabled",
        "data-flow-node": "stable node selector for browser QA",
    }
    for needle, label in required.items():
        if needle not in source:
            fail(errors, f"{source_path} missing {label}: {needle}")




def validate_mermaid_safe_syntax(source: str, path: Path | str, errors: list[str]) -> None:
    """Apply Mermaid flowchart syntax guardrails that catch common render failures.

    This is intentionally static and dependency-free. It complements browser-level
    visual QA: it prevents the common LLM mistakes documented by Mermaid itself
    before the page reaches a renderer.
    """
    source = unescape_html(source)
    nonempty_lines = [line.strip() for line in source.splitlines() if line.strip()]
    if not nonempty_lines:
        fail(errors, f"{path} contains an empty Mermaid graph block")
        return
    if not re.match(r"^(graph|flowchart)\s+(TB|TD|BT|LR|RL)\b", nonempty_lines[0], re.I):
        fail(errors, f"{path} Mermaid graph must start with graph/flowchart TB/TD/BT/LR/RL")
    for line_no, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("%%"):
            continue
        # Mermaid docs warn that compact links to o*/x* node IDs can be parsed as
        # circle/cross arrow syntax. Require whitespace or a capitalized ID.
        if COMPACT_OX_EDGE_PATTERN.search(stripped.replace(" ", "")) and not re.search(r"(?:---|-->|==>|-.->)\s+[ox][A-Za-z0-9_\-]", stripped):
            fail(errors, f"{path}:{line_no} Mermaid edge to o*/x* node should include a space or capitalized node id to avoid circle/cross edge parsing")
        for match in MERMAID_LABEL_PATTERN.finditer(line):
            node_id = match.group("id")
            label = match.group("label").strip()
            if node_id == "end":
                fail(errors, f"{path}:{line_no} Mermaid node id `end` must be capitalized or renamed; lowercase end is reserved")
            if not label:
                continue
            quoted = label.startswith(('"', "'", "`")) and label.endswith(('"', "'", "`"))
            if label == "end" and not quoted:
                fail(errors, f"{path}:{line_no} Mermaid label `end` must be quoted or capitalized")
            if UNSAFE_MERMAID_LABEL_CHARS.search(label) and not quoted:
                fail(errors, f"{path}:{line_no} Mermaid label `{label}` contains punctuation such as /, :, (), or comma; wrap the label in double quotes, e.g. Node[\"{label}\"]")

def graph_branch_score(source: str) -> tuple[int, int, int]:
    edges = MERMAID_EDGE_PATTERN.findall(source)
    out_degree: dict[str, int] = {}
    in_degree: dict[str, int] = {}
    for src, dst in edges:
        out_degree[src] = out_degree.get(src, 0) + 1
        in_degree[dst] = in_degree.get(dst, 0) + 1
    return len(edges), max(out_degree.values(), default=0), max(in_degree.values(), default=0)


def load_json(path: Path, errors: list[str]) -> Any:
    if not path.is_file():
        fail(errors, f"missing required JSON file: {path}")
        return None
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(errors, f"invalid JSON in {path}: {exc}")
        return None


def list_field_is_grounded(value: Any, allow_placeholders: bool) -> bool:
    if not isinstance(value, list) or not value:
        return False
    if allow_placeholders:
        return True
    return all(isinstance(item, str) and item.strip() and not PLACEHOLDER_PATTERN.search(item) for item in value)


def validate_skill(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            fail(errors, f"missing required file: {rel}")

    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return errors

    combined_parts = []
    for rel in REQUIRED_FILES:
        path = root / rel
        if path.is_file() and path.suffix in {".md", ".py", ".yaml", ".yml"}:
            combined_parts.append(f"\n--- {rel} ---\n{read_text(path)}")
    combined = "\n".join(combined_parts)
    skill_text = read_text(skill_path)

    for name, needles in REQUIRED_SKILL_TERMS.items():
        if not contains_any(skill_text, needles):
            fail(errors, f"SKILL.md missing required concept: {name} ({', '.join(needles)})")

    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        for match in pattern.finditer(combined):
            line_start = combined.rfind("\n", 0, match.start()) + 1
            line_end = combined.find("\n", match.end())
            if line_end == -1:
                line_end = len(combined)
            line = combined[line_start:line_end].lower()
            prefix = line[: max(0, match.start() - line_start)]
            # Guardrail/negative statements are required by the skill and should
            # not be treated as unsupported positive claims. The forbidden list
            # is for affirmative integration claims only.
            negation_terms = ("not", "do not", "does not", "never", "no ", "must not", "without")
            if any(term in prefix or term in line for term in negation_terms):
                continue
            if is_documented_invalid_example(combined, line_start):
                continue
            fail(errors, f"unsupported positive integration claim: {match.group(0)!r}")

    if "not GitNexus provider configuration" not in combined and "not configured as a GitNexus provider" not in combined:
        fail(errors, "missing explicit Codex-side/openai.yaml provider-boundary statement")

    for match in FORBIDDEN_FEYNMAN_REQUIREMENT_PATTERN.finditer(combined):
        fail(
            errors,
            "skill package must not require every architecture-web page to include a fixed `费曼复述` section; "
            f"found requirement-like text near: {match.group(0)!r}",
        )

    validate_interactive_runtime_source(root, errors)

    return errors


def validate_docs(docs_dir: Path) -> list[str]:
    errors: list[str] = []
    if not docs_dir.exists():
        return [f"docs dir does not exist: {docs_dir}"]
    overview = docs_dir / "overview.md"
    if not overview.is_file():
        fail(errors, "generated docs missing overview.md")

    markdown_files = [p for p in docs_dir.rglob("*.md") if p.name != "overview.md"]
    if len(markdown_files) < 2:
        fail(errors, "generated docs should include at least one module/parent page and one leaf page")

    all_text = "\n".join(read_text(p) for p in ([overview] if overview.is_file() else []) + markdown_files)
    if not re.search(r"(Source:|Sources:|Graph:|GitNexus:|gitnexus\s+(context|impact|cypher))", all_text, re.I):
        fail(errors, "generated docs lack visible source/GitNexus evidence references")
    if not re.search(r"(metadata|generated|GitNexus version|index status|commands used)", all_text, re.I):
        fail(errors, "generated docs lack metadata/generation/index evidence")

    return errors


def validate_required_headings(path: Path, headings: list[str], errors: list[str]) -> None:
    text = visible_text(read_text(path)).lower()
    for heading in headings:
        if heading.lower() not in text:
            fail(errors, f"{path} missing required heading: {heading}")


def validate_bundle_provenance(root: Path, errors: list[str]) -> None:
    provenance_path = root / "assets" / "architecture-flow-provenance.json"
    provenance = load_json(provenance_path, errors)
    if not isinstance(provenance, dict):
        return
    text = json.dumps(provenance).lower()
    for term in ("react", "react-dom", "@xyflow/react"):
        if term not in text:
            fail(errors, f"{provenance_path} missing React Flow provenance package: {term}")
    if "dagre" not in text and "elk" not in text:
        fail(errors, f"{provenance_path} missing layout package provenance (dagre or elk)")
    for term in ("build", "license"):
        if term not in text:
            fail(errors, f"{provenance_path} missing {term} metadata")
    for asset_name in ("architecture-flow.js", "architecture-flow.css"):
        if asset_name not in text or "sha256" not in text:
            fail(errors, f"{provenance_path} missing hash metadata for {asset_name}")


def has_grounding(value: Any) -> bool:
    if isinstance(value, list) and value:
        return all(isinstance(item, (str, dict)) and str(item).strip() for item in value)
    return isinstance(value, str) and bool(value.strip())


def validate_interactive_payload(payload: Any, path: Path, errors: list[str]) -> None:
    if isinstance(payload, dict) and "__parse_error__" in payload:
        fail(errors, str(payload["__parse_error__"]))
        return
    if not isinstance(payload, dict):
        fail(errors, f"{path} interactive-flow payload must be a JSON object")
        return
    if payload.get("version") != 1:
        fail(errors, f"{path} interactive-flow payload version must be 1")
    graphs = payload.get("graphs")
    if not isinstance(graphs, list) or not graphs:
        fail(errors, f"{path} interactive-flow payload must include non-empty graphs")
        return
    payload_text = json.dumps(payload, ensure_ascii=False)
    if any(pattern.search(payload_text) for pattern in ARTIFACT_CENTRIC_PATTERNS):
        fail(errors, f"{path} interactive-flow payload is artifact-centric; nodes/edges must center the target application/system")
    for graph_index, graph in enumerate(graphs):
        if not isinstance(graph, dict):
            fail(errors, f"{path} interactive-flow graphs[{graph_index}] must be an object")
            continue
        nodes = graph.get("nodes")
        edges = graph.get("edges")
        if not isinstance(nodes, list) or not nodes:
            fail(errors, f"{path} interactive-flow graphs[{graph_index}].nodes must be non-empty")
            continue
        if not isinstance(edges, list) or not edges:
            fail(errors, f"{path} interactive-flow graphs[{graph_index}].edges must be non-empty")
            continue
        node_ids: set[str] = set()
        for node_index, node in enumerate(nodes):
            if not isinstance(node, dict):
                fail(errors, f"{path} interactive-flow node {node_index} must be an object")
                continue
            node_id = str(node.get("id", ""))
            if node_id:
                node_ids.add(node_id)
            for field in ("id", "type", "label"):
                if not node.get(field):
                    fail(errors, f"{path} interactive-flow node {node_id or node_index} missing {field}")
            position = node.get("position")
            if not isinstance(position, dict) or not isinstance(position.get("x"), (int, float)) or not isinstance(position.get("y"), (int, float)):
                fail(errors, f"{path} interactive-flow node {node_id or node_index} missing stored position x/y")
            if not isinstance(node.get("width"), (int, float)) or not isinstance(node.get("height"), (int, float)):
                fail(errors, f"{path} interactive-flow node {node_id or node_index} missing width/height")
            if not (has_grounding(node.get("evidence")) or has_grounding(node.get("rationale"))):
                fail(errors, f"{path} interactive-flow node {node_id or node_index} missing evidence or fallback rationale")
        for edge_index, edge in enumerate(edges):
            if not isinstance(edge, dict):
                fail(errors, f"{path} interactive-flow edge {edge_index} must be an object")
                continue
            edge_id = str(edge.get("id", edge_index))
            for field in ("id", "source", "target", "type", "label"):
                if not edge.get(field):
                    fail(errors, f"{path} interactive-flow edge {edge_id} missing {field}")
            if edge.get("type") and edge.get("type") not in ALLOWED_EDGE_TYPES:
                fail(errors, f"{path} interactive-flow edge {edge_id} has unsupported semantic type: {edge.get('type')}")
            if edge.get("source") not in node_ids or edge.get("target") not in node_ids:
                fail(errors, f"{path} interactive-flow edge {edge_id} references unknown source/target")
            if not edge.get("sourceHandle") or not edge.get("targetHandle"):
                fail(errors, f"{path} interactive-flow edge {edge_id} missing sourceHandle/targetHandle for deterministic crossing control")
            if not (has_grounding(edge.get("evidence")) or has_grounding(edge.get("rationale"))):
                fail(errors, f"{path} interactive-flow edge {edge_id} missing evidence or fallback rationale")
        layout = graph.get("layout")
        if not isinstance(layout, dict) or layout.get("engine") not in ("dagre", "elk", "manual"):
            fail(errors, f"{path} interactive-flow graph {graph.get('id', graph_index)} missing deterministic layout metadata")


def validate_interactive_flow_page(path: Path, root: Path, errors: list[str], require_interactive: bool = False, allow_placeholders: bool = False) -> None:
    html = read_text(path)
    if require_interactive and not has_interactive_flow(html):
        fail(errors, f"{path} must include primary React Flow interactive containers and embedded payload")
    if not has_interactive_flow(html):
        return
    validate_runtime_network_urls(path, errors)
    for asset_name in ("architecture-flow.js", "architecture-flow.css"):
        if not (root / "assets" / asset_name).is_file():
            fail(errors, f"{path} uses interactive-flow but missing local interactive bundle asset: assets/{asset_name}")
    validate_bundle_provenance(root, errors)
    payloads = extract_interactive_flow_payloads(html, path)
    if not payloads:
        fail(errors, f"{path} uses interactive-flow but lacks embedded page-local data-architecture-flow payload")
    container_ids = extract_flow_graph_container_ids(html)
    if not allow_placeholders and not container_ids:
        fail(errors, f"{path} uses interactive-flow but has no data-flow-graph containers for React Flow mounting")
    graph_ids, duplicate_graph_ids = payload_graph_ids(payloads)
    for duplicate_graph_id in duplicate_graph_ids:
        fail(errors, f"{path} interactive-flow payload contains duplicate graph id: {duplicate_graph_id}")
    missing = sorted(set(container_ids) - graph_ids)
    if missing:
        fail(errors, f"{path} data-flow-graph containers missing matching payload graph ids: {', '.join(missing)}")
    if re.search(r"fetch\(\s*[\"']evidence/", html, re.I):
        fail(errors, f"{path} interactive-flow must not require fetch() from evidence/*.json for file:// rendering")
    for payload in payloads:
        validate_interactive_payload(payload, path, errors)
    visible = visible_text(html).lower()
    if not any(term in visible for term in ("fallback", "非视觉", "legend", "图例", "table")):
        fail(errors, f"{path} interactive-flow diagram missing textual fallback or legend")
    if not allow_placeholders:
        validate_no_visible_primary_static_diagrams(path, errors)


def validate_visual_qa_report(report: Any, errors: list[str], path: Path | str = "<visual-qa-report>") -> None:
    """Validate browser QA proves actual drag instead of marker-only enablement.

    Accepted report shape is intentionally flexible: either a top-level
    ``checks``/``pages`` list or a single top-level object may carry the fields.
    Each check must include a file:// URL, graph/node identity, and a measured
    drag delta whose absolute x or y movement is at least 20 CSS pixels.
    """
    if not isinstance(report, dict):
        fail(errors, f"{path} visual QA report must be a JSON object")
        return
    checks = report.get("checks") or report.get("pages") or report.get("results")
    if isinstance(checks, dict):
        checks = list(checks.values())
    if not isinstance(checks, list):
        checks = [report]
    measured = 0
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            fail(errors, f"{path} visual QA check {index} must be an object")
            continue
        url = str(check.get("url") or check.get("file_url") or "")
        if not url.startswith("file://"):
            fail(errors, f"{path} visual QA check {index} missing file:// URL")
        graph_id = check.get("graph_id") or check.get("graphId")
        node_id = check.get("node_id") or check.get("nodeId")
        if not graph_id or not node_id:
            fail(errors, f"{path} visual QA check {index} missing graph_id/node_id")
        delta = check.get("drag_delta") or check.get("dragDelta") or check.get("delta")
        dx = dy = None
        if isinstance(delta, dict):
            dx = delta.get("x", delta.get("dx"))
            dy = delta.get("y", delta.get("dy"))
        elif isinstance(delta, (list, tuple)) and len(delta) >= 2:
            dx, dy = delta[0], delta[1]
        if not isinstance(dx, (int, float)) or not isinstance(dy, (int, float)):
            fail(errors, f"{path} visual QA check {index} missing measured drag delta")
            continue
        if max(abs(dx), abs(dy)) < 20:
            fail(errors, f"{path} visual QA check {index} drag delta below threshold: x={dx}, y={dy}")
            continue
        measured += 1
    report_text = json.dumps(report, ensure_ascii=False).lower()
    if measured == 0:
        fail(errors, f"{path} visual QA report must prove drag with measured position delta")
    if "nodesdraggable" in report_text and "drag_delta" not in report_text and "dragdelta" not in report_text:
        fail(errors, f"{path} visual QA report is marker-only; include measured drag delta evidence")


def validate_page_scripts(path: Path, root: Path, errors: list[str], require_interactive: bool = False, allow_placeholders: bool = False) -> None:
    html = read_text(path)
    validate_runtime_network_urls(path, errors)
    if NETWORK_SCRIPT_PATTERN.search(html) or CDN_NAME_PATTERN.search(html):
        fail(errors, f"{path} references a CDN/network Mermaid script; architecture-web output must be offline/local")
    for src in SCRIPT_SRC_PATTERN.findall(html):
        if src.startswith(("http://", "https://", "//")):
            continue
        if src.endswith("mermaid.min.js") and not (path.parent / src).resolve().is_file():
            fail(errors, f"{path} references missing local Mermaid asset: {src}")
    validate_interactive_flow_page(path, root, errors, require_interactive=require_interactive, allow_placeholders=allow_placeholders)
    if "graph TB" not in html and not has_interactive_flow(html):
        fail(errors, f"{path} missing Mermaid graph TB source/render block or interactive-flow payload")
    if re.search(r"parse error|syntax error in text|diagram validation failed", visible_text(html), re.I):
        fail(errors, f"{path} contains visible Mermaid render/parser error text")


def validate_project_explainer_style(path: Path, errors: list[str]) -> None:
    html = read_text(path)
    lowered = html.lower()
    if 'lang="zh-cn"' not in lowered and "lang='zh-cn'" not in lowered:
        fail(errors, f"{path} should default to Chinese HTML language: lang=zh-CN")
    missing_style = [term for term in PROJECT_EXPLAINER_STYLE_TERMS if term.lower() not in lowered]
    if missing_style:
        fail(errors, f"{path} missing project-explainer-web style terms: {', '.join(missing_style)}")
    if 'class="hero"' not in lowered and "class='hero'" not in lowered:
        fail(errors, f"{path} missing project-explainer-web hero section")
    if 'class="panel' not in lowered and "class='panel" not in lowered:
        fail(errors, f"{path} missing project-explainer-web panel sections")


def validate_no_hidden_generic_contract(path: Path, errors: list[str]) -> None:
    html = read_text(path)
    for match in EXPLICIT_HIDDEN_BLOCK_PATTERN.finditer(html):
        attrs = match.group("attrs")
        if not hidden_attrs(attrs):
            continue
        body = visible_text(match.group("body"))
        if any(pattern.search(body) for pattern in GENERIC_HIDDEN_CONTRACT_PATTERNS):
            fail(
                errors,
                f"{path} contains 隐藏通用契约文本; strict validation must be satisfied by visible source-grounded content or evidence JSON",
            )
            return


def validate_feynman_sections(html_pages: list[Path], module_pages: list[Path], errors: list[str]) -> None:
    pages_with_heading: list[str] = []
    module_phrase_pages: list[str] = []
    for page in html_pages:
        html = read_text(page)
        if any("费曼复述" in heading for heading in heading_texts(html)):
            pages_with_heading.append(page.as_posix())
        if page in module_pages and "费曼复述" in visible_text(html):
            module_phrase_pages.append(page.as_posix())
    for page_name in pages_with_heading:
        fail(errors, f"{page_name} contains forbidden fixed section heading `费曼复述`; use plain Feynman-style explanation without a repeated section")
    if len(module_phrase_pages) >= 2:
        fail(errors, f"module pages repeat `费曼复述` across the architecture-web output: {', '.join(module_phrase_pages)}")


def validate_deep_graphs(path: Path, errors: list[str]) -> None:
    html = read_text(path)
    if has_interactive_flow(html):
        return
    sources = mermaid_sources(html)
    if not sources:
        return
    deep_sources = [source for source in sources if graph_branch_score(source)[0] >= 4]
    branched_sources = [
        source
        for source in sources
        if graph_branch_score(source)[1] >= 2 or graph_branch_score(source)[2] >= 2
    ]
    page_key = path.stem.lower()
    visible = visible_text(html).lower()
    needs_deep = path.name == "index.html" or any(
        token in page_key or token in visible
        for token in (
            "electron",
            "preload",
            "ipc",
            "chat",
            "runtime",
            "auth",
            "session",
            "lucyna",
            "desktop",
            "pet",
        )
    )
    if needs_deep and not deep_sources:
        fail(errors, f"{path} needs at least one non-trivial architecture graph with 4+ real edges")
    if needs_deep and not branched_sources:
        fail(errors, f"{path} needs at least one branched graph; a single straight line is not enough for deep architecture output")
    for source in sources:
        validate_mermaid_safe_syntax(source, path, errors)
        lowered_source = source.lower()
        edges, max_out, max_in = graph_branch_score(source)
        looks_like_primary_runtime_graph = edges >= 4 and sum(
            1 for term in ("user", "用户", "renderer", "preload", "main", "runtime", "ipc", "service") if term in lowered_source
        ) >= 4
        if looks_like_primary_runtime_graph and max_out <= 1 and max_in <= 1:
            fail(errors, f"{path} contains a primary runtime graph that is only a straight line; add real branch/fallback/service edges")


def validate_index_depth_contract(path: Path, allow_placeholders: bool, errors: list[str]) -> None:
    text = visible_text(read_text(path)).lower()
    requirements = {
        "visible source directory/structure tree": ["目录树", "affected structure tree", "source directory", "src/"],
        "technology framework tree": ["技术框架", "related technology tree", "electron", "react", "router", "preload", "ipc"],
        "runtime boundary graph": ["运行时", "runtime", "renderer", "preload", "main", "ipc"],
        "route/service/ipc flow graph": ["route", "service", "ipc", "流程", "flow"],
        "branch overview graph": ["分叉", "分支", "branch", "fallback", "降级", "失败"],
    }
    for label, needles in requirements.items():
        if not any(needle.lower() in text for needle in needles):
            fail(errors, f"{path} missing deep architecture requirement: {label}")


def validate_module_depth_contract(path: Path, allow_placeholders: bool, errors: list[str]) -> None:
    text = visible_text(read_text(path)).lower()
    if allow_placeholders and "todo" in text:
        return
    if not re.search(r"src/[^\s<>'\"]+", text, re.I):
        fail(errors, f"{path} missing visible real source file reference such as src/... in module content")
    if not any(term in text for term in ("关键符号", "handler", "api", "ipc", "service", "symbol", "函数", "入口")):
        fail(errors, f"{path} missing source relationship table terms: symbol/handler/API/IPC/service")
    if not any(term in text for term in ("分叉", "分支", "branch", "fallback", "降级", "失败", "error", "abort", "invalid", "refresh")):
        fail(errors, f"{path} missing branch/failure/fallback path coverage")


def validate_architecture_semantics(path: Path, errors: list[str]) -> None:
    html = read_text(path)
    searchable = html + "\n" + visible_text(html)
    artifact_hits = [pattern.pattern for pattern in ARTIFACT_CENTRIC_PATTERNS if pattern.search(searchable)]
    target_hits = [pattern.pattern for pattern in TARGET_SYSTEM_PATTERNS if pattern.search(searchable)]
    has_artifact_diagram = any(
        marker in html
        for marker in (
            "Index[index.html",
            "Index[index.html 主入口",
            "Reader[初学者读者] --> Index",
            "Web[_learn_web",
            "Flow[Architecture web flow",
            "Modules[modules/*.html",
            "源码证据[evidence/*.json",
        )
    )
    if has_artifact_diagram or (len(artifact_hits) >= 3 and len(target_hits) < 3):
        fail(
            errors,
            f"{path} is artifact-centric; architecture-web pages must center the target application/system, "
            "not _learn_web/index.html/modules/evidence/wiki-meta/Codex generation flow",
        )


def validate_index_navigation(root: Path, module_pages: list[Path], module_map: Any, errors: list[str]) -> None:
    root_html = sorted(p.name for p in root.glob("*.html"))
    if root_html != ["index.html"]:
        fail(errors, f"architecture-web root must have exactly one main HTML page index.html; found: {', '.join(root_html) or 'none'}")
    if not (root / "index.html").is_file():
        return
    index_html = read_text(root / "index.html")
    page_slugs = {p.stem for p in module_pages}
    map_slugs: set[str] = set()
    if isinstance(module_map, dict) and isinstance(module_map.get("modules"), list):
        map_slugs = {str(m.get("slug", "")) for m in module_map["modules"] if isinstance(m, dict) and m.get("slug")}
    for slug in sorted(page_slugs | map_slugs):
        href = f"modules/{slug}.html"
        if href not in index_html:
            fail(errors, f"index.html missing click-through link to module page: {href}")
    for page in module_pages:
        if '../index.html' not in read_text(page):
            fail(errors, f"{page} missing navigation link back to ../index.html")


def validate_meta(meta: Any, errors: list[str]) -> None:
    if not isinstance(meta, dict):
        fail(errors, "wiki-meta.json must be an object")
        return
    for field in META_FIELDS:
        if field not in meta:
            fail(errors, f"wiki-meta.json missing required field: {field}")
    if meta.get("mode") != "architecture-web":
        fail(errors, "wiki-meta.json mode must be architecture-web")
    if meta.get("language") not in (None, "zh-CN", "zh"):
        fail(errors, "wiki-meta.json language should default to zh-CN unless a future explicit language option is added")
    if meta.get("visual_style") not in (None, "project-explainer-web"):
        fail(errors, "wiki-meta.json visual_style should be project-explainer-web")
    if meta.get("entrypoint") not in (None, "index.html"):
        fail(errors, "wiki-meta.json entrypoint should be index.html")
    boundary = str(meta.get("execution_boundary", ""))
    if "GitNexus" not in boundary or "Codex" not in boundary or "provider" not in boundary:
        fail(errors, "wiki-meta.json missing provider-boundary metadata")
    if not isinstance(meta.get("modules"), list) or not meta.get("modules"):
        fail(errors, "wiki-meta.json modules must be a non-empty list")
    if not isinstance(meta.get("evidence_files"), list):
        fail(errors, "wiki-meta.json evidence_files must be a list")


def validate_module_map(module_map: Any, allow_placeholders: bool, errors: list[str]) -> None:
    if not isinstance(module_map, dict):
        fail(errors, "module-map.json must be an object")
        return
    modules = module_map.get("modules")
    if not isinstance(modules, list) or not modules:
        fail(errors, "module-map.json modules must be a non-empty list")
        return
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            fail(errors, f"module-map.json modules[{index}] must be an object")
            continue
        for field in MODULE_FIELDS:
            if field not in module:
                fail(errors, f"module-map.json modules[{index}] missing field: {field}")
        for field in ("source_files", "graph_commands", "evidence_refs", "verification_commands"):
            if not list_field_is_grounded(module.get(field), allow_placeholders):
                fail(errors, f"module-map.json modules[{index}].{field} must contain grounded non-placeholder entries")
        graph_commands = "\n".join(module.get("graph_commands", []) if isinstance(module.get("graph_commands"), list) else [])
        if "gitnexus" not in graph_commands.lower():
            fail(errors, f"module-map.json modules[{index}].graph_commands should cite GitNexus commands")


def validate_route_trace(route_trace: Any, errors: list[str]) -> None:
    if not isinstance(route_trace, dict):
        fail(errors, "route-service-trace.json must be an object")
        return
    flows = route_trace.get("flows")
    if not isinstance(flows, list):
        fail(errors, "route-service-trace.json flows must be a list")
        return
    for index, flow in enumerate(flows):
        if not isinstance(flow, dict):
            fail(errors, f"route-service-trace.json flows[{index}] must be an object")
            continue
        for field in FLOW_FIELDS:
            if field not in flow:
                fail(errors, f"route-service-trace.json flows[{index}] missing field: {field}")


def validate_architecture_web(architecture_web_dir: Path, allow_placeholders: bool = False) -> list[str]:
    errors: list[str] = []
    root = architecture_web_dir
    if not root.exists():
        return [f"architecture-web dir does not exist: {root}"]
    if not (root / "index.html").is_file():
        fail(errors, "architecture-web output missing index.html")
    modules_dir = root / "modules"
    if not modules_dir.is_dir():
        fail(errors, "architecture-web output missing modules/ directory")
    module_pages = sorted(modules_dir.glob("*.html")) if modules_dir.is_dir() else []
    if not module_pages:
        fail(errors, "architecture-web output must include at least one modules/*.html page")

    meta = load_json(root / "wiki-meta.json", errors)
    require_interactive = meta_requires_interactive_flow(meta)
    html_pages = ([root / "index.html"] if (root / "index.html").is_file() else []) + module_pages
    for page in html_pages:
        validate_page_scripts(page, root, errors, require_interactive=require_interactive, allow_placeholders=allow_placeholders)
        validate_project_explainer_style(page, errors)
        validate_no_hidden_generic_contract(page, errors)
        validate_no_visible_raw_graph_blocks(page, allow_placeholders, errors)
        validate_architecture_semantics(page, errors)
        validate_deep_graphs(page, errors)

    module_map = load_json(root / "evidence" / "module-map.json", errors)
    route_trace = load_json(root / "evidence" / "route-service-trace.json", errors)
    validate_index_navigation(root, module_pages, module_map, errors)
    validate_feynman_sections(html_pages, module_pages, errors)

    if (root / "index.html").is_file():
        validate_required_headings(root / "index.html", OVERVIEW_HEADINGS, errors)
        validate_index_depth_contract(root / "index.html", allow_placeholders, errors)
    for page in module_pages:
        validate_required_headings(page, MODULE_HEADINGS, errors)
        validate_module_depth_contract(page, allow_placeholders, errors)
        lowered = visible_text(read_text(page)).lower()
        has_evidence = "evidence" in lowered or "源码证据" in lowered or "证据" in lowered
        has_verification = "verification" in lowered or "验证" in lowered
        has_graph = "gitnexus" in lowered or "graph" in lowered or "图" in lowered
        if not has_evidence or not has_verification or not has_graph:
            fail(errors, f"{page} missing module evidence/graph/verification terms")

    validate_meta(meta, errors)
    validate_module_map(module_map, allow_placeholders, errors)
    validate_route_trace(route_trace, errors)

    if not allow_placeholders:
        for path in html_pages + [root / "wiki-meta.json", root / "evidence" / "module-map.json", root / "evidence" / "route-service-trace.json"]:
            if path.is_file() and PLACEHOLDER_PATTERN.search(read_text(path)):
                fail(errors, f"unresolved TODO/placeholder evidence in {path}")

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--docs-dir", type=Path, help="Optional generated markdown wiki docs directory to validate")
    parser.add_argument("--architecture-web-dir", type=Path, help="Optional generated architecture-web directory to validate")
    parser.add_argument(
        "--allow-placeholders",
        "--scaffold-ok",
        dest="allow_placeholders",
        action="store_true",
        help="Permit scaffold placeholders in --architecture-web-dir validation",
    )
    args = parser.parse_args(argv)

    root = Path(args.skill_root).expanduser().resolve()
    errors = validate_skill(root)
    if args.docs_dir:
        errors.extend(validate_docs(args.docs_dir.expanduser().resolve()))
    if args.architecture_web_dir:
        errors.extend(validate_architecture_web(args.architecture_web_dir.expanduser().resolve(), args.allow_placeholders))

    if errors:
        print("FAIL gitnexus-codex-wiki validation")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS gitnexus-codex-wiki validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
