#!/usr/bin/env python3
"""Create a deterministic architecture-web wiki scaffold for Codex to fill in.

The script does not analyze code and does not call an LLM. It creates an
offline-first static website skeleton plus machine-readable evidence files so
Codex can author final GitNexus-grounded architecture pages without recreating
boilerplate. The visual contract intentionally follows the project-explainer-web
knowledge-page pattern: one index.html entry, card-based Chinese-first pages,
local/offline Mermaid, and click-through module pages under modules/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


EXECUTION_BOUNDARY = (
    "GitNexus supplies graph/index evidence; Codex authors architecture-web "
    "pages directly. Native gitnexus wiki provider/API-key setup is separate."
)

DEFAULT_PROJECT_EXPLAINER_MERMAID = (
    Path.home() / ".codex" / "skills" / "project-explainer-web" / "assets" / "vendor" / "mermaid.min.js"
)
DEFAULT_ARCHITECTURE_FLOW_ASSETS = Path(__file__).resolve().parents[1] / "assets" / "architecture-flow" / "dist"

DIAGRAM_MODES = ("mermaid", "interactive-flow", "hybrid")


STYLE = """
:root {
  color-scheme: light;
  --bg: #eef4ff;
  --bg-2: #f9fbff;
  --panel: rgba(255, 255, 255, 0.92);
  --panel-strong: #ffffff;
  --text: #172033;
  --muted: #5c6882;
  --line: rgba(93, 122, 255, 0.14);
  --accent: #315efb;
  --accent-2: #7c3aed;
  --accent-soft: rgba(49, 94, 251, 0.1);
  --ok: #0f9f6e;
  --warn: #b26b00;
  --shadow: 0 20px 45px rgba(31, 45, 93, 0.09);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  color: var(--text);
  line-height: 1.7;
  background:
    radial-gradient(circle at top left, rgba(49, 94, 251, 0.16), transparent 26%),
    radial-gradient(circle at top right, rgba(124, 58, 237, 0.12), transparent 22%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.shell { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 64px; }
.hero, .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 24px; box-shadow: var(--shadow); backdrop-filter: blur(12px); }
.hero { position: relative; overflow: hidden; padding: 32px; margin-bottom: 18px; }
.hero::after { content: ""; position: absolute; inset: auto -60px -60px auto; width: 220px; height: 220px; border-radius: 50%; background: radial-gradient(circle, rgba(49, 94, 251, 0.18), transparent 70%); pointer-events: none; }
.eyebrow { display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px; background: linear-gradient(135deg, rgba(49, 94, 251, 0.12), rgba(124, 58, 237, 0.12)); color: var(--accent); font-size: 13px; font-weight: 700; letter-spacing: 0.02em; }
h1, h2, h3 { line-height: 1.2; margin: 0; }
h1 { font-size: clamp(32px, 5vw, 48px); margin-top: 16px; max-width: 900px; }
h2 { font-size: clamp(22px, 3vw, 28px); }
h3 { font-size: 16px; }
.hero p { margin: 14px 0 0; color: var(--muted); max-width: 860px; font-size: 15px; }
.meta { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
.meta span, .tag { display: inline-flex; align-items: center; gap: 6px; padding: 8px 12px; border-radius: 999px; border: 1px solid var(--line); background: rgba(255, 255, 255, 0.82); font-size: 14px; }
.tag { background: linear-gradient(135deg, rgba(49, 94, 251, 0.08), rgba(124, 58, 237, 0.08)); color: #314267; font-weight: 600; }
.nav { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 18px; }
.nav a { padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,.84); border: 1px solid var(--line); font-weight: 700; font-size: 14px; }
.grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 18px; }
.panel { padding: 22px; }
.span-12 { grid-column: span 12; }
.span-8 { grid-column: span 8; }
.span-6 { grid-column: span 6; }
.span-4 { grid-column: span 4; }
.section-title { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.section-title p { margin: 6px 0 0; color: var(--muted); }
.list { display: grid; gap: 12px; margin: 0; padding: 0; list-style: none; }
.card, .step, .tree, .note, .diagram-card { border: 1px solid var(--line); border-radius: 18px; background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(247,250,255,0.94)); }
.card, .step, .note, .diagram-card { padding: 16px; }
.card p, .step p, .panel p, li p { margin: 8px 0 0; color: var(--muted); }
.step strong, .card strong { display: block; }
.file { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; color: var(--accent); }
.tree, pre { margin: 0; padding: 18px; white-space: pre-wrap; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; line-height: 1.75; color: #203052; overflow-x: auto; }
pre, code { background: #f6f8fa; border-radius: 6px; }
code { padding: .2rem .35rem; }
.diagram-card { margin-top: 12px; }
.diagram-card .fallback { border-left: 4px solid var(--accent); padding-left: 12px; }
.diagram-card details { margin-top: 12px; }
.diagram-card summary { cursor: pointer; font-weight: 700; color: var(--accent); }
.interactive-flow-card .fallback-table { margin-top: 14px; }
table { width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 14px; }
th, td { border-bottom: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }
th { color: #314267; background: rgba(49, 94, 251, 0.07); }

.function-depth-entry { border: 1px solid rgba(15, 159, 110, .22); background: linear-gradient(135deg, rgba(15,159,110,.08), rgba(49,94,251,.08)); }
.function-inventory-toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin: 12px 0; }
.function-inventory-toolbar input { min-width: min(100%, 320px); border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; font: inherit; background: #fff; }
.function-inventory-status { color: var(--muted); font-size: 14px; }
.function-inventory-controls { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 10px 0 0; }
.function-inventory-controls button { border: 1px solid var(--line); border-radius: 999px; padding: 7px 12px; background: #fff; color: var(--accent); font-weight: 700; cursor: pointer; }
.function-inventory-controls button:disabled { cursor: not-allowed; opacity: .45; }
.function-inventory-table td:first-child { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; }
@media (max-width: 860px) { .span-8, .span-6, .span-4 { grid-column: span 12; } .hero { padding: 24px; } }
""".strip()


def run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, stderr=subprocess.STDOUT, text=True).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"unavailable: {exc}"


def slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in ascii_value).strip("-")
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned or "architecture"


def derive_slug(out: Path) -> str:
    name = out.name
    suffix = "-architecture-wiki"
    if name.endswith(suffix):
        name = name[: -len(suffix)]
    return slug(name)


def generated_at() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def copy_evidence(paths: Iterable[str], evidence_dir: Path, force: bool) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    used_names: set[str] = {"module-map.json", "route-service-trace.json"}
    for raw in paths:
        source = Path(raw).expanduser().resolve()
        base = slug(source.stem) or "evidence"
        suffix = source.suffix
        candidate = f"{base}{suffix}"
        index = 2
        while candidate in used_names:
            candidate = f"{base}-{index}{suffix}"
            index += 1
        used_names.add(candidate)
        target = evidence_dir / candidate
        if source.is_file():
            if force or not target.exists():
                shutil.copyfile(source, target)
            entries.append({"source": source.as_posix(), "path": f"evidence/{candidate}"})
        else:
            entries.append({"source": source.as_posix(), "path": source.as_posix(), "status": "missing"})
    return entries


def write(path: Path, text: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_architecture_flow_assets(assets_dir: Path, force: bool) -> None:
    required = [
        DEFAULT_ARCHITECTURE_FLOW_ASSETS / "architecture-flow.js",
        DEFAULT_ARCHITECTURE_FLOW_ASSETS / "architecture-flow.css",
        DEFAULT_ARCHITECTURE_FLOW_ASSETS / "architecture-flow-provenance.json",
    ]
    missing = [path for path in required if not path.is_file()]
    if missing:
        missing_text = ", ".join(path.as_posix() for path in missing)
        raise FileNotFoundError(f"missing architecture-flow asset(s): {missing_text}")
    assets_dir.mkdir(parents=True, exist_ok=True)
    for source in required[:2]:
        target = assets_dir / source.name
        if force or not target.exists():
            shutil.copyfile(source, target)
    provenance = json.loads((DEFAULT_ARCHITECTURE_FLOW_ASSETS / "architecture-flow-provenance.json").read_text(encoding="utf-8"))
    provenance.update(
        {
            "copied_at": generated_at(),
            "generated_site_asset_paths": ["assets/architecture-flow.js", "assets/architecture-flow.css"],
            "generated_assets": [
                {
                    "path": "assets/architecture-flow.js",
                    "sha256": sha256_file(assets_dir / "architecture-flow.js"),
                    "bytes": (assets_dir / "architecture-flow.js").stat().st_size,
                },
                {
                    "path": "assets/architecture-flow.css",
                    "sha256": sha256_file(assets_dir / "architecture-flow.css"),
                    "bytes": (assets_dir / "architecture-flow.css").stat().st_size,
                },
            ],
        }
    )
    target = assets_dir / "architecture-flow-provenance.json"
    if force or not target.exists():
        target.write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def evidence_refs(evidence_entries: list[dict[str, str]]) -> list[str]:
    refs: list[str] = []
    for entry in evidence_entries:
        source = entry.get("source", "")
        path = entry.get("path", "")
        # Primary React Flow payloads must describe the target system, not the
        # generated documentation artifact. Use original source/GitNexus labels
        # in graph evidence rather than evidence/*.json audit-file paths.
        if source and "TODO:" not in source:
            refs.append(source)
        elif path and not path.startswith("evidence/") and "TODO:" not in path:
            refs.append(path)
    return refs or ["GitNexus graph/source evidence for target runtime"]


def flow_node(node_id: str, node_type: str, label: str, x: int, y: int, evidence: list[str]) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": node_type,
        "label": label,
        "position": {"x": x, "y": y},
        "width": 230,
        "height": 96,
        "evidence": evidence,
    }


def flow_edge(
    edge_id: str,
    source: str,
    target: str,
    edge_type: str,
    label: str,
    evidence: list[str],
    source_handle: str = "right",
    target_handle: str = "left",
) -> dict[str, Any]:
    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "sourceHandle": source_handle,
        "targetHandle": target_handle,
        "type": edge_type,
        "label": label,
        "evidence": evidence,
    }



def function_symbol_id(module: str, file_path: str, line: int, symbol: str) -> str:
    return f"{module}:{file_path}:{line}:{symbol}"


def function_trace_graph(module: str, evidence: list[str]) -> dict[str, Any]:
    title = module_title(module)
    compact_title = title.replace(" ", "")
    entry_id = function_symbol_id(module, f"src/{module}/entry.ts", 1, f"{compact_title}Entry")
    boundary_id = function_symbol_id(module, f"src/{module}/boundary.ts", 24, "handleBoundaryCall")
    service_id = function_symbol_id(module, f"src/{module}/service.ts", 64, "runDomainLogic")
    fallback_id = function_symbol_id(module, f"src/{module}/service.ts", 112, "handleFallback")
    test_id = function_symbol_id(module, f"tests/low-level/{module}.test.ts", 1, "moduleContractTest")
    return {
        "id": f"function-trace-{module}",
        "title": f"{title} 函数调用链",
        "summary": "函数级 scaffold：把 TODO symbol 替换为 GitNexus/direct-source 证据后交付。",
        "nodes": [
            {**flow_node("entry-function", "component", f"{title} entry function", 0, 120, evidence), "symbolId": entry_id},
            {**flow_node("boundary-function", "ipc-handler", "handleBoundaryCall", 320, 120, evidence), "symbolId": boundary_id},
            {**flow_node("service-function", "service", "runDomainLogic", 640, 40, evidence), "symbolId": service_id},
            {**flow_node("fallback-function", "helper", "handleFallback", 640, 220, evidence), "symbolId": fallback_id},
            {**flow_node("test-function", "test-helper", "moduleContractTest", 960, 120, evidence), "symbolId": test_id},
        ],
        "edges": [
            flow_edge("entry-boundary-call", "entry-function", "boundary-function", "call", "calls", evidence),
            flow_edge("boundary-service-ipc", "boundary-function", "service-function", "ipc", "invokes IPC", evidence),
            flow_edge("service-fallback-error", "service-function", "fallback-function", "error", "error", evidence, "bottom", "top"),
            flow_edge("service-test-cover", "service-function", "test-function", "test", "test covers", evidence),
            flow_edge("fallback-test-cover", "fallback-function", "test-function", "test", "test covers", evidence),
        ],
        "layout": {"engine": "manual", "direction": "LR", "nodeWidth": 230, "nodeHeight": 96, "ranksep": 96, "nodesep": 64, "computedAtBuildTime": True, "readabilityCap": 30},
    }


def function_inventory_rows(module: str) -> list[dict[str, Any]]:
    compact_title = module_title(module).replace(" ", "")
    return [
        {"symbolId": function_symbol_id(module, f"src/{module}/entry.ts", 1, f"{compact_title}Entry"), "symbol": f"{compact_title}Entry", "kind": "component", "file": f"src/{module}/entry.ts", "line": 1, "responsibility": "TODO: replace with concrete entry function responsibility.", "traceIds": [f"function-trace-{module}"], "tests": [f"tests/low-level/{module}.test.ts"], "evidenceSource": "direct-source", "indexFreshness": "direct-source-fallback"},
        {"symbolId": function_symbol_id(module, f"src/{module}/boundary.ts", 24, "handleBoundaryCall"), "symbol": "handleBoundaryCall", "kind": "ipc-handler", "file": f"src/{module}/boundary.ts", "line": 24, "responsibility": "TODO: replace with concrete API/IPC/runtime boundary responsibility.", "traceIds": [f"function-trace-{module}"], "tests": [f"tests/low-level/{module}.test.ts"], "evidenceSource": "direct-source", "indexFreshness": "direct-source-fallback"},
        {"symbolId": function_symbol_id(module, f"src/{module}/service.ts", 64, "runDomainLogic"), "symbol": "runDomainLogic", "kind": "service", "file": f"src/{module}/service.ts", "line": 64, "responsibility": "TODO: replace with concrete service/runtime call responsibility.", "traceIds": [f"function-trace-{module}"], "tests": [f"tests/low-level/{module}.test.ts"], "evidenceSource": "direct-source", "indexFreshness": "direct-source-fallback"},
        {"symbolId": function_symbol_id(module, f"src/{module}/service.ts", 112, "handleFallback"), "symbol": "handleFallback", "kind": "helper", "file": f"src/{module}/service.ts", "line": 112, "responsibility": "TODO: replace with concrete fallback/error path responsibility.", "traceIds": [f"function-trace-{module}"], "tests": [f"tests/low-level/{module}.test.ts"], "evidenceSource": "direct-source", "indexFreshness": "direct-source-fallback"},
        {"symbolId": function_symbol_id(module, f"tests/low-level/{module}.test.ts", 1, "moduleContractTest"), "symbol": "moduleContractTest", "kind": "test-helper", "file": f"tests/low-level/{module}.test.ts", "line": 1, "responsibility": "TODO: replace with concrete test coverage helper/fixture responsibility.", "traceIds": [f"function-trace-{module}"], "tests": [f"tests/low-level/{module}.test.ts"], "evidenceSource": "direct-source", "indexFreshness": "direct-source-fallback"},
    ]


def function_inventory_section(module: str, use_interactive: bool) -> str:
    trace_block = interactive_flow_block("函数调用链 interactive-flow", f"function-trace-{module}") if use_interactive else "<p>Function-depth mode requires interactive-flow for primary trace graphs.</p>"
    rows = "\n".join(
        "<tr>"
        f"<td>{row['symbolId']}</td><td>{row['symbol']}</td><td>{row['kind']}</td>"
        f"<td><code>{row['file']}</code></td><td>{row['line']}</td>"
        f"<td>{row['responsibility']}</td><td>{', '.join(row['traceIds'])}</td>"
        f"<td>{', '.join(row['tests'])}</td><td>{row['evidenceSource']} / {row['indexFreshness']}</td>"
        "</tr>"
        for row in function_inventory_rows(module)
    )
    return f'''
<section class="panel span-12"><h2>函数调用链</h2>{trace_block}<p>把 scaffold 节点替换为真实函数、IPC facade/handler、runtime call、fallback/error path 与 test edge；每个节点必须能点击查看源码证据。</p></section>
<section class="panel span-12" data-function-inventory-scope><h2>函数清单</h2>
<div class="function-inventory-toolbar"><label>搜索函数 / 文件 / 职责 <input data-function-inventory-search aria-label="搜索函数清单" placeholder="输入 symbol、file、kind 或 trace"></label><span class="function-inventory-status" data-function-inventory-count></span></div>
<table class="function-inventory-table" data-function-inventory data-page-size="50" data-module-id="{module}"><thead><tr><th>symbolId</th><th>symbol</th><th>kind</th><th>file</th><th>line</th><th>responsibility</th><th>trace</th><th>tests</th><th>evidence</th></tr></thead><tbody>{rows}</tbody></table>
<p>默认 scaffold 使用 direct-source-fallback 占位；最终页面必须用 GitNexus/direct source 证据替换 TODO 并记录 freshness。</p></section>'''


def function_architecture_map(project_slug: str, modules: list[str], evidence_entries: list[dict[str, str]], git_head: str) -> dict[str, Any]:
    mapped_modules = []
    traces = []
    for module in modules:
        rows = function_inventory_rows(module)
        mapped_modules.append({
            "moduleId": module,
            "label": module_title(module),
            "page": f"modules/{module}.html",
            "sourceRoots": sorted({row["file"] for row in rows}),
            "symbols": [
                {"symbolId": row["symbolId"], "name": row["symbol"], "kind": row["kind"], "file": row["file"], "line": row["line"], "responsibility": row["responsibility"], "callers": [], "callees": [], "traceIds": row["traceIds"], "testRefs": row["tests"], "evidenceSource": row["evidenceSource"], "indexFreshness": row["indexFreshness"]}
                for row in rows
            ],
            "exclusions": [],
        })
        traces.append({
            "traceId": f"function-trace-{module}",
            "moduleId": module,
            "entrySymbolId": rows[0]["symbolId"],
            "nodeSymbolIds": [row["symbolId"] for row in rows],
            "edges": [
                {"from": rows[0]["symbolId"], "to": rows[1]["symbolId"], "kind": "calls"},
                {"from": rows[1]["symbolId"], "to": rows[2]["symbolId"], "kind": "invokes-ipc"},
                {"from": rows[2]["symbolId"], "to": rows[3]["symbolId"], "kind": "error"},
            ],
        })
    return {"schemaVersion": 1, "repo": project_slug, "git": {"head": git_head, "gitnexusIndexedCommit": "TODO: gitnexus indexed commit", "indexFreshness": "unknown"}, "coverageScope": "in-scope-architecture-functions", "evidenceRefs": [entry.get("path", entry.get("source", "")) for entry in evidence_entries], "modules": mapped_modules, "traces": traces}


def function_visual_qa_stub(modules: list[str]) -> dict[str, Any]:
    first_module = modules[0] if modules else "core"
    return {
        "schemaVersion": 1,
        "status": "scaffold-smoke-placeholder",
        "notes": "Scaffold smoke values prove schema shape only; final QA must replace with measured browser evidence from exact file:// pages.",
        "checks": [
            {
                "url": f"file:///TODO/{first_module}.html",
                "graph_id": f"function-trace-{first_module}",
                "node_id": "entry-function",
                "drag_delta": {"x": 24, "y": 0},
            }
        ],
        "inventory": {
            module: {
                "rowCount": len(function_inventory_rows(module)),
                "initialInteractiveLoadMs": 1,
                "searchFilterUpdateMs": 1,
                "defaultVisibleRows": 50,
                "pagination": True,
            }
            for module in modules
        },
    }


def architecture_flow_payload(slug_value: str, modules: list[str], evidence_entries: list[dict[str, str]], function_depth: bool = False) -> dict[str, Any]:
    refs = evidence_refs(evidence_entries)
    module_nodes = []
    module_edges = []
    for index, module in enumerate(modules[:4]):
        y = 90 + index * 132
        module_id = f"module-{module}"
        module_nodes.append(flow_node(module_id, "service", f"{module_title(module)} module", 660, y, refs))
        module_edges.append(flow_edge(f"runtime-{module_id}", "runtime", module_id, "call", "dispatches into module", refs))
    nodes = [
        flow_node("user", "actor", "用户 / operator", 0, 220, refs),
        flow_node("entry", "entrypoint", "UI route / command entrypoint", 300, 120, refs),
        flow_node("boundary", "boundary", "preload/API/IPC/HTTP boundary", 300, 340, refs),
        flow_node("runtime", "runtime", "main process / runtime orchestrator", 660, 220, refs),
        flow_node("storage", "data", "local storage / files", 1020, 90, refs),
        flow_node("external", "external", "cloud or external integrations", 1020, 240, refs),
        flow_node("fallback", "fallback", "error / fallback path", 1020, 390, refs),
        flow_node("verification", "test", "verification commands", 1020, 540, refs),
        *module_nodes,
    ]
    edges = [
        flow_edge("user-entry", "user", "entry", "call", "starts action", refs),
        flow_edge("entry-boundary", "entry", "boundary", "ipc", "crosses runtime boundary", refs, "bottom", "top"),
        flow_edge("boundary-runtime", "boundary", "runtime", "ipc", "validated API/IPC call", refs),
        flow_edge("runtime-storage", "runtime", "storage", "data", "reads/writes state", refs),
        flow_edge("runtime-external", "runtime", "external", "external", "calls integration", refs),
        flow_edge("runtime-fallback", "runtime", "fallback", "error", "handles invalid/degraded path", refs),
        flow_edge("fallback-verification", "fallback", "verification", "test", "covered by checks", refs, "bottom", "top"),
        *module_edges,
    ]
    module_graphs = []
    for module in modules:
        title = module_title(module)
        module_graphs.append(
            {
                "id": f"module-{module}",
                "title": f"{title} 模块运行时结构",
                "summary": "模块页用相同 payload contract 展示入口、边界、职责、依赖和验证证据。",
                "nodes": [
                    flow_node("trigger", "actor", "用户动作 / system event", 0, 160, refs),
                    flow_node("entry", "entrypoint", f"{title} source entrypoint", 300, 80, refs),
                    flow_node("boundary", "boundary", f"{title} runtime boundary", 300, 260, refs),
                    flow_node("logic", "service", f"{title} domain logic", 650, 160, refs),
                    flow_node("dependencies", "external", "services / storage / integrations", 980, 80, refs),
                    flow_node("checks", "test", "tests / lint / typecheck", 980, 260, refs),
                ],
                "edges": [
                    flow_edge("trigger-entry", "trigger", "entry", "call", "starts module action", refs),
                    flow_edge("entry-boundary", "entry", "boundary", "ipc", "enters runtime boundary", refs, "bottom", "top"),
                    flow_edge("boundary-logic", "boundary", "logic", "call", "invokes domain logic", refs),
                    flow_edge("logic-dependencies", "logic", "dependencies", "external", "uses dependency", refs),
                    flow_edge("logic-checks", "logic", "checks", "test", "verified by command", refs),
                    flow_edge("dependencies-logic", "dependencies", "logic", "data", "returns data/result", refs, "left", "right"),
                ],
                "layout": {
                    "engine": "manual",
                    "direction": "LR",
                    "nodeWidth": 230,
                    "nodeHeight": 96,
                    "ranksep": 96,
                    "nodesep": 64,
                    "computedAtBuildTime": True,
                },
            }
        )
    common_layout = {
        "engine": "manual",
        "direction": "LR",
        "nodeWidth": 230,
        "nodeHeight": 96,
        "ranksep": 96,
        "nodesep": 64,
        "computedAtBuildTime": True,
    }
    overview_graphs = [
        {
            "id": "runtime-overview",
            "title": f"{slug_value} 目标应用整体运行时结构",
            "summary": "从用户动作进入目标系统边界，穿过运行时服务、模块、存储、外部集成、错误分支和验证命令。",
            "nodes": nodes,
            "edges": edges,
            "layout": common_layout,
        },
        {
            "id": "source-structure",
            "title": f"{slug_value} 真实源码边界图",
            "summary": "用目标源码入口、运行时边界、领域模块、服务依赖和验证边界替代静态源码树 SVG。",
            "nodes": [
                flow_node("source-root", "entrypoint", "target source root", 0, 180, refs),
                flow_node("entrypoints", "entrypoint", "routes / commands / handlers", 300, 80, refs),
                flow_node("runtime-boundaries", "boundary", "API / IPC / runtime boundaries", 300, 280, refs),
                flow_node("domain-modules", "service", "domain modules", 650, 80, refs),
                flow_node("providers", "external", "services / providers", 980, 80, refs),
                flow_node("state", "data", "storage / state", 980, 250, refs),
                flow_node("checks", "test", "tests / build checks", 650, 360, refs),
            ],
            "edges": [
                flow_edge("root-entrypoints", "source-root", "entrypoints", "call", "contains entry files", refs),
                flow_edge("root-boundaries", "source-root", "runtime-boundaries", "ipc", "defines boundary files", refs, "right", "left"),
                flow_edge("entrypoints-modules", "entrypoints", "domain-modules", "call", "routes into modules", refs),
                flow_edge("boundaries-modules", "runtime-boundaries", "domain-modules", "ipc", "validates boundary call", refs),
                flow_edge("modules-providers", "domain-modules", "providers", "external", "uses integration", refs),
                flow_edge("modules-state", "domain-modules", "state", "data", "reads/writes state", refs, "right", "left"),
                flow_edge("modules-checks", "domain-modules", "checks", "test", "covered by checks", refs, "bottom", "top"),
            ],
            "layout": common_layout,
        },
        {
            "id": "technology-framework",
            "title": f"{slug_value} 技术框架图",
            "summary": "展示目标应用的框架、运行时、服务、数据和验证层，而不是文档网站技术栈。",
            "nodes": [
                flow_node("ui-framework", "runtime", "UI / renderer framework", 0, 130, refs),
                flow_node("routing", "entrypoint", "routes / commands", 300, 130, refs),
                flow_node("boundary-api", "boundary", "preload / API / IPC contract", 620, 130, refs),
                flow_node("runtime-core", "runtime", "runtime orchestrator", 940, 130, refs),
                flow_node("service-layer", "service", "service/provider layer", 1260, 40, refs),
                flow_node("data-layer", "data", "state/persistence layer", 1260, 220, refs),
                flow_node("test-layer", "test", "low-level/e2e checks", 940, 360, refs),
            ],
            "edges": [
                flow_edge("ui-routing", "ui-framework", "routing", "call", "user action enters route", refs),
                flow_edge("routing-boundary", "routing", "boundary-api", "ipc", "crosses safe boundary", refs),
                flow_edge("boundary-runtime-core", "boundary-api", "runtime-core", "ipc", "dispatches handler", refs),
                flow_edge("runtime-service-layer", "runtime-core", "service-layer", "external", "calls service/provider", refs),
                flow_edge("runtime-data-layer", "runtime-core", "data-layer", "data", "persists state", refs),
                flow_edge("runtime-test-layer", "runtime-core", "test-layer", "test", "verified by command", refs, "bottom", "top"),
            ],
            "layout": common_layout,
        },
        {
            "id": "branch-fallback-test",
            "title": f"{slug_value} 分支 / fallback / test 地图",
            "summary": "覆盖 success、error、fallback 和验证分支，避免只有一条直线的架构解释。",
            "nodes": [
                flow_node("action", "actor", "用户动作 / system event", 0, 220, refs),
                flow_node("decision", "boundary", "handler/API decision point", 300, 220, refs),
                flow_node("success", "service", "success path", 650, 80, refs),
                flow_node("error", "fallback", "error / invalid path", 650, 220, refs),
                flow_node("fallback", "fallback", "fallback / degraded mode", 650, 360, refs),
                flow_node("observe", "data", "logs/state/evidence", 980, 220, refs),
                flow_node("verify", "test", "tests / smoke / visual QA", 1280, 220, refs),
            ],
            "edges": [
                flow_edge("action-decision", "action", "decision", "call", "enters branch point", refs),
                flow_edge("decision-success", "decision", "success", "call", "valid request", refs, "right", "left"),
                flow_edge("decision-error", "decision", "error", "error", "invalid/error input", refs, "right", "left"),
                flow_edge("decision-fallback", "decision", "fallback", "error", "degraded/provider missing", refs, "right", "left"),
                flow_edge("success-observe", "success", "observe", "data", "records result", refs),
                flow_edge("error-observe", "error", "observe", "data", "records failure state", refs),
                flow_edge("fallback-observe", "fallback", "observe", "data", "records fallback state", refs),
                flow_edge("observe-verify", "observe", "verify", "test", "asserts branch behavior", refs),
            ],
            "layout": common_layout,
        },
    ]
    function_graphs = [function_trace_graph(module, refs) for module in modules] if function_depth else []
    return {"version": 1, "graphs": [*overview_graphs, *module_graphs, *function_graphs]}


def flow_payload_script(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f'<script type="application/json" data-architecture-flow>\n{data}\n</script>'


def interactive_flow_block(title: str, graph_id: str) -> str:
    return f"""<section class="diagram-card interactive-flow-card">
<h3>{title}</h3>
<div class="architecture-flow" data-flow-graph="{graph_id}" aria-label="Interactive React Flow architecture diagram"></div>
<div class="flow-legend" aria-label="Edge semantics legend"><span>call 控制流</span><span>ipc 边界穿越</span><span>data 数据</span><span>error 错误/降级</span><span>external 外部集成</span><span>test 验证</span></div>
<table class="fallback-table"><thead><tr><th>非视觉 fallback</th><th>说明</th></tr></thead><tbody><tr><td>节点</td><td>按用户动作、入口、边界、运行时、模块、存储/外部集成和验证命令阅读。</td></tr><tr><td>边</td><td>每条边有 type、label、direction marker 和 evidence；点击节点或边会在证据面板显示来源。</td></tr></tbody></table>
<p class="fallback">React Flow 交互：支持 zoom、pan、drag、fit-to-view，并通过页面内嵌 JSON payload 在 file:// 下工作。</p>
</section>"""


def collapsed_mermaid_source(title: str, body: str) -> str:
    return f"""<details class="diagram-card"><summary>{title} Mermaid source audit trail</summary><pre class="mermaid-source">{body}</pre></details>"""


def rendered_svg_block(title: str, label: str) -> str:
    return f"""<section class="diagram-card">
<h3>{title}</h3>
<div class="diagram"><svg role="img" aria-label="{label}" viewBox="0 0 720 170">
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#315efb"/></marker></defs>
<rect x="20" y="45" width="150" height="64" rx="14" fill="#fff" stroke="#315efb"/>
<text x="95" y="82" text-anchor="middle" font-size="14" font-weight="700">Source</text>
<line x1="170" y1="77" x2="270" y2="77" stroke="#315efb" stroke-width="2.4" marker-end="url(#arrow)"/>
<rect x="270" y="45" width="170" height="64" rx="14" fill="#fff" stroke="#7c3aed"/>
<text x="355" y="82" text-anchor="middle" font-size="14" font-weight="700">Runtime boundary</text>
<line x1="440" y1="77" x2="540" y2="77" stroke="#315efb" stroke-width="2.4" marker-end="url(#arrow)"/>
<rect x="540" y="45" width="160" height="64" rx="14" fill="#fff" stroke="#0f9f6e"/>
<text x="620" y="82" text-anchor="middle" font-size="14" font-weight="700">Service / data</text>
</svg></div>
<p class="fallback">非视觉 fallback：Source → Runtime boundary → Service/data；详细交互图使用 React Flow payload。</p>
</section>"""


def module_title(name: str) -> str:
    return " ".join(part.capitalize() for part in slug(name).split("-")) or "Core"


def mermaid_block(title: str, body: str, mermaid_script: bool) -> str:
    if mermaid_script:
        visual = f"""<div class=\"mermaid\">\n{body}\n</div>"""
    else:
        visual = f"""<pre class=\"mermaid-source\">{body}</pre>"""
    return f"""<section class=\"diagram-card\">\n<h3>{title}</h3>\n{visual}\n<p class=\"fallback\">非视觉 fallback：按上到下读取节点，父节点表示系统边界，子节点表示职责或调用方向。</p>\n</section>"""


def html_head(title: str, mermaid_ref: str | None, flow_ref: str | None = None, flow_css_ref: str | None = None) -> str:
    mermaid_script = f'\n<script defer src="{mermaid_ref}"></script>\n<script>window.addEventListener("DOMContentLoaded",()=>{{if(window.mermaid){{window.mermaid.initialize({{startOnLoad:true,securityLevel:"loose"}});}}}});</script>' if mermaid_ref else ""
    flow_css = f'\n<link rel="stylesheet" href="{flow_css_ref}">' if flow_css_ref else ""
    flow_script = f'\n<script defer src="{flow_ref}"></script>' if flow_ref else ""
    return f"""<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"UTF-8\" />\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n<title>{title}</title>{flow_css}\n<style>\n{STYLE}\n</style>{mermaid_script}{flow_script}\n</head>\n<body>\n<div class=\"shell\">\n"""


def module_links(modules: list[str]) -> str:
    return "\n".join(
        f'<a class="card" href="modules/{slug(name)}.html"><strong>{module_title(name)}</strong><p>点击进入模块页：职责、数据流、证据、验证命令。</p></a>'
        for name in modules
    )


def overview_html(slug_value: str, modules: list[str], evidence_entries: list[dict[str, str]], mermaid_script: bool, diagram_mode: str, function_depth: bool = False) -> str:
    module_rows = "\n".join(
        f'<tr><td><a href="modules/{slug(name)}.html">{module_title(name)}</a></td><td>TODO: 用源码证据说明这个产品/运行时模块负责什么。</td><td>TODO: 引用 GitNexus graph/source 证据。</td></tr>'
        for name in modules
    )
    evidence_rows = "\n".join(
        f"<tr><td>{entry['path']}</td><td>{entry['source']}</td><td>直接证据：需要 Codex 填入目标系统结论。</td></tr>" for entry in evidence_entries
    ) or "<tr><td>TODO: evidence file</td><td>TODO: source path</td><td>TODO: target-system conclusion</td></tr>"
    structure_tree = f"""{slug_value}/ target application
├─ user-facing entrypoints      UI/routes/commands that a user touches
├─ boundary adapters            preload/API/IPC/HTTP/CLI adapters found in source
├─ runtime services             orchestration, providers, domain services
├─ persistence/integrations     local files, storage, cloud or external systems
└─ verification surface         tests, typecheck, lint, smoke checks"""
    tech_tree = """Target-system evidence stack
├─ Source files                 real entrypoints and domain modules
├─ GitNexus graph/index         file, symbol, call-edge, and process evidence
├─ Runtime boundaries           UI/API/IPC/service/storage edges
└─ 验证命令        checks that prove the architecture still works"""
    diagram = mermaid_block(
        "目标应用整体架构 graph TB",
        """graph TB
  User["用户 / operator"] --> Entry["UI route / command entrypoint"]
  Entry --> Boundary["preload API / HTTP / CLI boundary"]
  Boundary --> Runtime["main process / runtime orchestrator"]
  Runtime --> Services[domain services]
  Services --> Storage["local storage / files"]
  Services --> External[cloud or external integrations]
  Services --> Tests[verification commands]""",
        mermaid_script,
    )
    structure_diagram = mermaid_block(
        "真实源码目录树",
        """graph TB
  App["Target application / system"] --> Entry[Source entrypoints]
  App --> Boundaries["Runtime/API boundaries"]
  App --> Modules[Domain modules]
  Modules --> Services["Services/providers"]
  Services --> Data["Persistence/integrations"]
  App --> 验证命令[Tests and checks]""",
        mermaid_script,
    )
    tech_diagram = mermaid_block(
        "技术框架图",
        """graph TB
  Source[Target source files] --> Graph[GitNexus graph evidence]
  Source --> Runtime["Runtime/framework boundaries"]
  Runtime --> Services[Services and integrations]
  Graph --> Claims[Source-grounded architecture claims]
  Claims --> 验证命令["Typecheck/lint/tests/smoke checks"]""",
        mermaid_script,
    )
    branch_diagram = mermaid_block(
        "分叉总览图",
        """graph TB
  Action["用户动作 / system event"] --> Boundary["route / API / IPC boundary"]
  Boundary --> Happy[success path]
  Boundary --> Failure["error / invalid path"]
  Boundary --> Fallback["fallback / degraded path"]
  Happy --> Verify[verification command]
  Failure --> Verify
  Fallback --> Verify""",
        mermaid_script,
    )
    use_interactive = diagram_mode in {"interactive-flow", "hybrid"}
    use_mermaid = diagram_mode in {"mermaid", "hybrid"}
    payload = architecture_flow_payload(slug_value, modules, evidence_entries, function_depth=function_depth) if use_interactive else None
    if use_interactive:
        diagram = interactive_flow_block("目标应用整体运行时 interactive-flow", "runtime-overview")
        if use_mermaid:
            diagram += collapsed_mermaid_source(
                "整体运行时结构图",
                """graph TB
  User["用户 / operator"] --> Entry["UI route / command entrypoint"]
  Entry --> Boundary["preload API / HTTP / CLI boundary"]
  Boundary --> Runtime["main process / runtime orchestrator"]
  Runtime --> Services[domain services]
  Services --> Storage["local storage / files"]
  Services --> External[cloud or external integrations]
  Services --> Tests[verification commands]""",
            )
        else:
            structure_diagram = interactive_flow_block("真实源码边界 interactive-flow", "source-structure")
            tech_diagram = interactive_flow_block("技术框架 interactive-flow", "technology-framework")
            branch_diagram = interactive_flow_block("分叉 / fallback / test interactive-flow", "branch-fallback-test")
    script_ref = "./assets/mermaid.min.js" if mermaid_script else None
    flow_ref = "./assets/architecture-flow.js" if use_interactive else None
    flow_css = "./assets/architecture-flow.css" if use_interactive else None
    function_entry_section = ""
    if function_depth:
        function_entry_section = '<section class="panel span-12 function-depth-entry"><h2>函数视图入口</h2><p>概览页保持可读；函数级调用链和可搜索清单位于每个模块页。点击模块入口进入 function trace 与 inventory。</p></section>'
    return html_head(f"{slug_value} 应用架构说明", script_ref, flow_ref, flow_css) + f"""
<nav class=\"nav\"><a href=\"index.html\">主页面</a><a href=\"#module-nav\">模块入口</a><a href=\"#verification\">验证命令</a></nav>
<header class=\"hero\">
<span class=\"eyebrow\">GitNexus evidence · Codex-authored · 目标系统架构</span>
<h1>{slug_value} 应用架构说明</h1>
<p>这是唯一主入口页面。它用目标项目源码和 GitNexus 证据解释应用如何运行；HTML 文件、模块页和 evidence JSON 只是承载说明的网页结构，不是被解释系统。</p>
<div class=\"meta\"><span>默认语言：中文</span><span>离线优先</span><span>语义守卫：主叙事必须是目标系统</span><span>Execution boundary: {EXECUTION_BOUNDARY}</span></div>
</header>

<main class=\"grid\">
<section class=\"panel span-12\"><div class=\"section-title\"><div><h2>总览摘要</h2><p>一句话说明目标应用/系统解决什么问题。</p></div></div><p>TODO: 用初学者能懂的话解释目标项目/子系统目标，并引用源码或 GitNexus 证据。</p></section>
<section class=\"panel span-6\"><h2>为什么要先理解它</h2><p>TODO: 说明为什么开发者需要先理解入口、边界、服务和数据流，而不是直接改代码。</p></section>
<section class=\"panel span-6\" id=\"module-nav\"><h2>模块入口</h2><div class=\"list\">{module_links(modules)}</div></section>
{function_entry_section}
<section class=\"panel span-12\"><h2>真实源码目录树</h2>{structure_diagram}<pre class=\"tree\">{structure_tree}</pre></section>
<section class=\"panel span-12\"><h2>整体运行时结构图</h2>{diagram}<p>TODO: 用费曼学习法解释图里的每条主要边：用户操作如何进入源码入口，如何穿过运行时/API/IPC 边界，最后到达服务、存储或外部集成。</p></section>
<section class=\"panel span-12\"><h2>用户动作到运行时流程</h2><ol><li>从一个真实用户动作或系统事件开始。</li><li>找到对应源码入口、路由、preload/API/IPC 或服务边界。</li><li>跟踪到运行时服务、数据存储、外部集成和验证命令。</li></ol></section>
<section class=\"panel span-12\"><h2>源码证据地图</h2><table><thead><tr><th>证据</th><th>来源</th><th>支持的目标系统结论</th></tr></thead><tbody>{evidence_rows}</tbody></table></section>
<section class=\"panel span-12\"><h2>优先阅读文件</h2><table><thead><tr><th>模块</th><th>产品/运行时职责</th><th>Graph/source evidence</th></tr></thead><tbody>{module_rows}</tbody></table></section>
<section class=\"panel span-12\"><h2>技术框架图</h2>{tech_diagram}<pre class=\"tree\">{tech_tree}</pre></section>
<section class=\"panel span-12\"><h2>分叉总览图</h2>{branch_diagram}<p>TODO: 用真实源码替换 success/error/fallback：列出至少三个分叉、触发条件、涉及的 handler/API/IPC/service 和验证命令。</p></section>
<section class=\"panel span-6\"><h2>边界与不变量</h2><ul><li>目标系统的运行时边界必须来自源码证据。</li><li>主入口 HTML 只是阅读导航，不是产品架构节点。</li><li>不要让证据文件、网页生成流程或 Mermaid 机制成为主叙事。</li><li>不要引入 CDN Mermaid；保持 file:// 可读。</li></ul></section>
<section class=\"panel span-6\"><h2>安全修改方式</h2><p>TODO: 先更新目标系统证据，再同步首页和对应模块页，最后跑验证器与项目相关检查。</p></section>
<section class=\"panel span-12\" id=\"verification\"><h2>验证命令</h2><ul><li><code>python3 ~/.codex/skills/gitnexus-codex-wiki/scripts/validate-skill.py ~/.codex/skills/gitnexus-codex-wiki --architecture-web-dir _learn_web/{slug_value}-architecture-wiki</code></li><li><code>rg -n "TODO|TBD|FIXME|PLACEHOLDER|REPLACE ME" _learn_web/{slug_value}-architecture-wiki</code></li></ul></section>
<section class=\"panel span-6\"><h2>常见反模式</h2><ul><li>把网页 artifact 当成被解释系统。</li><li>只写文件清单，不解释用户动作到服务边界的链路。</li><li>用英文 scaffold 交付给中文读者。</li><li>引用 CDN 导致离线打不开图。</li></ul></section>
<section class=\"panel span-6\"><h2>原理与背景知识</h2><p>TODO: 解释目标项目框架、运行时边界、GitNexus 图证据与交互式架构图如何帮助理解源码。</p></section>
<section class=\"panel span-6\"><h2>约束与风险</h2><p>TODO: 记录 stale index、dirty worktree、未验证推断等风险。</p></section>
<section class=\"panel span-6\"><h2>推荐维护方案</h2><p>TODO: 给出下一步维护目标系统架构说明的建议。</p></section>
<section class=\"panel span-12\"><h2>后续维护动作</h2><ol><li>补齐真实源码入口和模块页。</li><li>补齐 route/service/API/IPC trace。</li><li>运行验证命令。</li></ol></section>
 </main>
{flow_payload_script(payload) if payload else ""}
</div>
</body>
</html>
"""


def module_html(name: str, evidence_entries: list[dict[str, str]], mermaid_script: bool, diagram_mode: str, project_slug: str, modules: list[str], function_depth: bool = False) -> str:
    title = module_title(name)
    module_slug = slug(name)
    evidence_refs = ", ".join(entry["path"] for entry in evidence_entries) or "TODO: evidence reference"
    structure_tree = f"""{title} target-system module
├─ source entrypoints          files/symbols where this responsibility starts
├─ inbound boundary            route/API/IPC/command/event entry
├─ core responsibility         orchestration or domain logic
├─ outbound dependencies       services, storage, cloud/local integrations
└─ verification                smallest checks after changing this module"""
    tech_tree = """Module evidence stack
├─ Source files       real code positions in the target repo
├─ GitNexus commands  graph queries for context/impact/call edges
├─ Runtime flow       route/API/IPC/service/data boundary
└─ Tests              minimal verification command(s)"""
    diagram = mermaid_block(
        "模块边界 graph TB",
        f"""graph TB
  Trigger["用户动作 / system event"] --> Entry["{title} source entrypoint"]
  Entry --> Boundary["{title} runtime boundary"]
  Boundary --> Logic["{title} domain logic"]
  Logic --> Dependencies["services / storage / integrations"]
  Logic --> 验证命令["tests / lint / typecheck"]""",
        mermaid_script,
    )
    use_interactive = diagram_mode in {"interactive-flow", "hybrid"}
    use_mermaid = diagram_mode in {"mermaid", "hybrid"}
    payload = architecture_flow_payload(project_slug, [module_slug], evidence_entries, function_depth=function_depth) if use_interactive else None
    if use_interactive:
        diagram = interactive_flow_block("模块边界 interactive-flow", f"module-{module_slug}")
        if use_mermaid:
            diagram += collapsed_mermaid_source(
                "模块边界 graph TB",
                f"""graph TB
  Trigger["用户动作 / system event"] --> Entry["{title} source entrypoint"]
  Entry --> Boundary["{title} runtime boundary"]
  Boundary --> Logic["{title} domain logic"]
  Logic --> Dependencies["services / storage / integrations"]
  Logic --> 验证命令["tests / lint / typecheck"]""",
            )
    tech_section_body = f'<pre class="tree">{tech_tree}</pre>'
    if use_interactive and not use_mermaid:
        tech_section_body = (
            '<table class="fallback-table"><thead><tr><th>技术层</th><th>阅读方式</th></tr></thead>'
            '<tbody><tr><td>入口/边界</td><td>先看上方 React Flow 模块边界图里的 entrypoint 与 boundary 节点。</td></tr>'
            '<tr><td>服务/依赖</td><td>再看 service、external、data 与 test 类型边。</td></tr></tbody></table>'
            + tech_section_body
        )
    function_sections = function_inventory_section(module_slug, use_interactive) if function_depth else ""
    script_ref = "../assets/mermaid.min.js" if mermaid_script else None
    flow_ref = "../assets/architecture-flow.js" if use_interactive else None
    flow_css = "../assets/architecture-flow.css" if use_interactive else None
    return html_head(f"{title} 模块说明", script_ref, flow_ref, flow_css) + f"""
<nav class=\"nav\"><a href=\"../index.html\">返回主页面 index.html</a></nav>
<header class=\"hero\">
<span class=\"eyebrow\">目标系统模块 · 从首页进入</span>
<h1>{title}</h1>
<p>这个页面只解释目标应用里的一个真实模块：它做什么、为什么存在、数据怎么流、源码证据在哪里、怎么验证。</p>
<div class=\"meta\"><span>默认语言：中文</span><span>模块 slug：{module_slug}</span><span>语义守卫：解释产品/运行时模块</span><span>Execution boundary: {EXECUTION_BOUNDARY}</span></div>
</header>
<main class=\"grid\">
<section class=\"panel span-6\"><h2>模块职责</h2><p>TODO: 用初学者能懂的一句话说明目标系统模块职责，并引用源码。</p></section>
<section class=\"panel span-6\"><h2>为什么存在</h2><p>TODO: 说明如果没有这个产品/运行时模块，系统会缺什么边界或能力。</p></section>
<section class=\"panel span-12\"><h2>真实源码目录树</h2><pre class=\"tree\">{structure_tree}</pre></section>
<section class=\"panel span-12\"><h2>整体运行时结构图</h2>{diagram}<p>TODO: 解释每条边代表的职责交接，以及它对应的源码位置。</p></section>
<section class=\"panel span-12\"><h2>数据如何流动</h2><p>TODO: 按输入 → 边界 → 处理 → 输出/副作用描述数据流。</p></section>
<section class=\"panel span-12\"><h2>用户动作到运行时流程</h2><p>TODO: 用一个具体请求、用户动作或系统事件讲清楚端到端流程。</p></section>
{function_sections}
<section class=\"panel span-12\"><h2>源码阅读入口</h2><ul><li>TODO: 写入 <code>{module_slug}</code> 的首读源码文件或符号。</li></ul></section>
<section class=\"panel span-12\"><h2>源码证据地图</h2><ul><li>源码证据 refs: {evidence_refs}</li><li>GitNexus graph commands: TODO: 填入 repo-qualified <code>gitnexus context</code>/<code>gitnexus cypher</code>。</li></ul></section>
<section class=\"panel span-12\"><h2>优先阅读文件</h2><table><thead><tr><th>文件</th><th>为什么先读</th></tr></thead><tbody><tr><td>TODO: source file</td><td>TODO: product/runtime purpose</td></tr></tbody></table></section>
<section class=\"panel span-12\"><h2>技术框架图</h2>{tech_section_body}</section>
<section class=\"panel span-6\"><h2>边界与不变量</h2><p>TODO: 写出这个目标系统模块不能随便跨越的 API/IPC/service/data 边界。</p></section>
<section class=\"panel span-6\"><h2>安全修改方式</h2><p>TODO: 说明修改顺序：先读源码证据，再改代码/页面，再验证。</p></section>
<section class=\"panel span-12\"><h2>源码证据</h2><p>GitNexus/source evidence: {evidence_refs}</p></section>
<section class=\"panel span-12\"><h2>验证命令</h2><ul><li>TODO: 添加修改这个模块后的最小验证命令。</li></ul></section>
<section class=\"panel span-6\"><h2>常见反模式</h2><p>TODO: 列出最容易犯的错误与替代做法，例如绕开边界或忽略验证。</p></section>
<section class=\"panel span-6\"><h2>原理与背景知识</h2><p>TODO: 解释理解本模块前需要知道的目标项目框架/运行时背景。</p></section>
<section class=\"panel span-6\"><h2>约束与风险</h2><p>TODO: 记录 stale graph、dirty worktree、未验证推断。</p></section>
<section class=\"panel span-6\"><h2>推荐维护方案</h2><p>TODO: 给出维护这个目标系统模块的建议。</p></section>
<section class=\"panel span-12\"><h2>后续维护动作</h2><ol><li>替换 TODO 为证据化内容。</li><li>运行 architecture-web 验证器。</li></ol></section>
</main>
{flow_payload_script(payload) if payload else ""}
</div>
</body>
</html>
"""



def resolve_mermaid_source(arg_value: str | None, disable_default: bool) -> Path | None:
    if arg_value:
        return Path(arg_value).expanduser().resolve()
    if not disable_default and DEFAULT_PROJECT_EXPLAINER_MERMAID.is_file():
        return DEFAULT_PROJECT_EXPLAINER_MERMAID
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Repository root used for git metadata and relative source references")
    parser.add_argument("--out", help="Architecture-web output directory")
    parser.add_argument("--slug", help="Project slug; required when --out is omitted")
    parser.add_argument("--module", action="append", default=[], help="Module page name to create; repeatable")
    parser.add_argument("--evidence", action="append", default=[], help="源码证据 file to copy/reference; repeatable")
    parser.add_argument("--mermaid-js", help="Optional local mermaid.min.js file to copy into assets/")
    parser.add_argument("--diagram-mode", choices=DIAGRAM_MODES, default="interactive-flow", help="Diagram renderer mode: mermaid, interactive-flow (default), or hybrid")
    parser.add_argument("--function-depth", action="store_true", help="Enable function trace graph/inventory scaffold, functionDepth metadata, and canonical function map evidence")
    parser.add_argument("--no-default-mermaid-js", action="store_true", help="Do not auto-copy project-explainer-web's bundled Mermaid asset")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files")
    args = parser.parse_args(argv)

    repo = Path(args.repo).expanduser().resolve()
    if args.out:
        out = Path(args.out).expanduser().resolve()
        project_slug = slug(args.slug) if args.slug else derive_slug(out)
    else:
        if not args.slug:
            parser.error("--slug is required when --out is omitted")
        project_slug = slug(args.slug)
        out = repo / "_learn_web" / f"{project_slug}-architecture-wiki"

    modules = [slug(name) for name in (args.module or ["core"])]

    modules_dir = out / "modules"
    evidence_dir = out / "evidence"
    assets_dir = out / "assets"
    modules_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    use_interactive = args.diagram_mode in {"interactive-flow", "hybrid"}
    use_mermaid = args.diagram_mode in {"mermaid", "hybrid"}
    if args.function_depth and not use_interactive:
        parser.error("--function-depth requires --diagram-mode interactive-flow or hybrid")

    if use_interactive:
        try:
            copy_architecture_flow_assets(assets_dir, args.force)
        except FileNotFoundError as exc:
            parser.error(str(exc))

    mermaid_script = False
    source = resolve_mermaid_source(args.mermaid_js, args.no_default_mermaid_js) if use_mermaid else None
    if source and args.diagram_mode in ("mermaid", "hybrid"):
        if not source.is_file():
            parser.error(f"Mermaid asset does not exist: {source}")
        assets_dir.mkdir(parents=True, exist_ok=True)
        target = assets_dir / "mermaid.min.js"
        if args.force or not target.exists():
            shutil.copyfile(source, target)
        mermaid_script = True

    evidence_entries = copy_evidence(args.evidence, evidence_dir, args.force)
    if not evidence_entries:
        evidence_entries = [{"source": "TODO: collected GitNexus/source evidence", "path": "TODO: evidence reference"}]

    module_entries = [
        {
            "slug": module,
            "title": module_title(module),
            "source_files": ["TODO: cite source file"],
            "graph_commands": ["TODO: gitnexus context or cypher command"],
            "evidence_refs": [entry["path"] for entry in evidence_entries],
            "verification_commands": ["TODO: repo-specific verification command"],
        }
        for module in modules
    ]
    route_trace = {
        "flows": [
            {
                "slug": "TODO: flow-slug",
                "title": "TODO: route/service flow",
                "entrypoints": ["TODO: entrypoint"],
                "services": ["TODO: service"],
                "graph_edges": ["TODO: graph edge from GitNexus"],
                "evidence_refs": [entry["path"] for entry in evidence_entries],
            }
        ]
    }
    meta = {
        "generated_at": generated_at(),
        "repo": repo.as_posix(),
        "git_commit": run(["git", "rev-parse", "HEAD"], cwd=repo),
        "gitnexus_version": run(["gitnexus", "--version"]),
        "execution_boundary": EXECUTION_BOUNDARY,
        "mode": "architecture-web",
        "language": "zh-CN",
        "visual_style": "project-explainer-web",
        "diagram_mode": args.diagram_mode,
        "interactive_flow": use_interactive,
        "entrypoint": "index.html",
        "modules": modules,
        "evidence_files": evidence_entries,
    }
    if args.function_depth:
        meta["functionDepth"] = {"enabled": True, "coverageScope": "in-scope-architecture-functions", "mapPath": "evidence/function-architecture-map.json", "validatorMode": "function-depth"}

    write(out / "index.html", overview_html(project_slug, modules, evidence_entries, mermaid_script, args.diagram_mode, function_depth=args.function_depth), args.force)
    for module in modules:
        write(modules_dir / f"{module}.html", module_html(module, evidence_entries, mermaid_script, args.diagram_mode, project_slug, modules, function_depth=args.function_depth), args.force)
    if use_interactive:
        write(evidence_dir / "interactive-flow.json", json.dumps(architecture_flow_payload(project_slug, modules, evidence_entries, function_depth=args.function_depth), indent=2, ensure_ascii=False) + "\n", args.force)
    write(evidence_dir / "module-map.json", json.dumps({"modules": module_entries}, indent=2, ensure_ascii=False) + "\n", args.force)
    write(evidence_dir / "route-service-trace.json", json.dumps(route_trace, indent=2, ensure_ascii=False) + "\n", args.force)
    if args.function_depth:
        write(evidence_dir / "function-architecture-map.json", json.dumps(function_architecture_map(project_slug, modules, evidence_entries, meta["git_commit"]), indent=2, ensure_ascii=False) + "\n", args.force)
        write(evidence_dir / "visual-qa-function-drilldown.json", json.dumps(function_visual_qa_stub(modules), indent=2, ensure_ascii=False) + "\n", args.force)
    write(out / "wiki-meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n", args.force)

    print(f"Wrote architecture-web scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
