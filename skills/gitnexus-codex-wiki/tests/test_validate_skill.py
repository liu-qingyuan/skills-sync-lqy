#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-skill.py"
spec = importlib.util.spec_from_file_location("validate_skill", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


STYLE = """<style>
:root { --bg: #eef4ff; --panel: #fff; --accent: #315efb; }
.shell { max-width: 1180px; margin: 0 auto; }
.hero, .panel { background: var(--panel); }
</style>"""

SIMPLE_SVG = '<div class="diagram"><svg role="img" aria-label="rendered diagram" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4"/></svg></div>'


def graph_block(source: str) -> str:
    return f'{SIMPLE_SVG}<details class="source-note"><summary>图源</summary><pre class="mermaid-source">{source}</pre></details>'


OVERVIEW_TREE_SOURCE = """graph TB
  Root["src/"] --> Renderer["src/renderer"]
  Root --> Preload["src/preload"]
  Root --> Main["src/main"]
  Main --> Services[services]"""

OVERVIEW_RUNTIME_SOURCE = """graph TB
  User[用户] --> Renderer["React Renderer / Router"]
  Renderer --> Preload[preload electronAPI]
  Preload --> Main["ipcMain / Main process"]
  Main --> LocalService[local service]
  Main --> CloudService[cloud service]
  Main --> Runtime[external runtime]"""

OVERVIEW_TECH_SOURCE = """graph TB
  Electron --> React
  Electron --> Preload
  Electron --> IpcMain
  React --> Router
  IpcMain --> Service"""

MODULE_RUNTIME_SOURCE = """graph TB
  Entry["src/app.ts handler"] --> Core[Core service API]
  Core --> Success[success branch]
  Core --> Error[error branch]
  Core --> Fallback[fallback branch]"""

OVERVIEW_HTML = f"""<!doctype html>
<html lang="zh-CN"><head>{STYLE}</head><body><div class="shell">
<header class="hero"><h1>架构说明</h1><p>默认中文主入口。</p></header>
<main>
<section class="panel"><h2>总览摘要</h2><p>Source: src/app.ts. GitNexus graph evidence explains the entrypoint.</p></section>
<section class="panel"><h2>为什么要先理解它</h2><p>帮助新人先理解边界。</p></section>
<section class="panel"><h2>真实源码目录树</h2>{graph_block(OVERVIEW_TREE_SOURCE)}<pre class="tree">src/
├─ renderer/
├─ preload/
└─ main/index.ts</pre></section>
<section class="panel"><h2>整体运行时结构图</h2>{graph_block(OVERVIEW_RUNTIME_SOURCE)}<p>Non-visual fallback: 用户动作穿过 renderer、preload、main，再按 service/runtime 分支。</p></section>
<section class="panel"><h2>用户动作到运行时流程</h2><p>route → service → IPC 流程从 App 进入 Main，并按本地/云端/runtime 分支。</p></section>
<section class="panel"><h2>源码证据地图</h2><table><tr><td>evidence/preflight.md</td></tr></table></section>
<section class="panel"><h2>优先阅读文件</h2><a href="modules/core.html">Core</a></section>
<section class="panel"><h2>技术框架图</h2>{graph_block(OVERVIEW_TECH_SOURCE)}<pre class="tree">Electron
├─ React Router
├─ preload/electronAPI
└─ ipcMain services</pre></section>
<section class="panel"><h2>边界与不变量</h2><p>renderer/preload/main/runtime 边界必须清楚；分叉 branch 包括成功、失败和 fallback。</p></section>
<section class="panel"><h2>安全修改方式</h2><p>先改 evidence，再改页面。</p></section>
<section class="panel"><h2>验证命令</h2><p>Run python3 -m unittest discover tests.</p></section>
<section class="panel"><h2>常见反模式</h2><p>不要跳过 evidence。</p></section>
<section class="panel"><h2>原理与背景知识</h2><p>graph TB 表示自上而下关系。</p></section>
<section class="panel"><h2>约束与风险</h2><p>Stale index 需要标注。</p></section>
<section class="panel"><h2>推荐维护方案</h2><p>保持单入口 index。</p></section>
<section class="panel"><h2>后续维护动作</h2><p>补齐模块。</p></section>
</main></div></body></html>
"""

MODULE_HTML = f"""<!doctype html>
<html lang="zh-CN"><head>{STYLE}</head><body><div class="shell">
<nav><a href="../index.html">返回主页面 index.html</a></nav>
<header class="hero"><h1>Core</h1></header>
<main>
<section class="panel"><h2>模块职责</h2><p>Core receives requests. Source: src/app.ts.</p></section>
<section class="panel"><h2>为什么存在</h2><p>It coordinates services from one entrypoint.</p></section>
<section class="panel"><h2>真实源码目录树</h2><pre class="tree">modules/
└─ core.html</pre></section>
<section class="panel"><h2>整体运行时结构图</h2>{graph_block(MODULE_RUNTIME_SOURCE)}<p>Non-visual fallback: Entry calls Core, then Core chooses success, error, or fallback.</p></section>
<section class="panel"><h2>数据如何流动</h2><p>src/app.ts handler 通过 API/IPC/service 入口调用 Core。</p></section>
<section class="panel"><h2>用户动作到运行时流程</h2><p>输入先到入口，再进入服务；分支表覆盖 success/error/fallback。</p></section>
<section class="panel"><h2>源码阅读入口</h2><p>Start at src/app.ts.</p></section>
<section class="panel"><h2>源码证据地图</h2><p>GitNexus: gitnexus context src/app.ts. Graph: Entry -> Service.</p></section>
<section class="panel"><h2>优先阅读文件</h2><table><tr><th>文件</th><th>关键符号/handler/API</th></tr><tr><td>src/app.ts</td><td>AppService.handle API service entry</td></tr></table></section>
<section class="panel"><h2>技术框架图</h2>{SIMPLE_SVG}<pre class="tree">Service
└─ Core</pre></section>
<section class="panel"><h2>边界与不变量</h2><p>Keep entry/service boundaries.</p></section>
<section class="panel"><h2>Branch paths</h2><table><tr><th>分支</th><th>触发条件</th></tr><tr><td>success</td><td>service returns data</td></tr><tr><td>error</td><td>handler raises error</td></tr><tr><td>fallback</td><td>service unavailable</td></tr></table></section>
<section class="panel"><h2>安全修改方式</h2><p>Modify source and update tests.</p></section>
<section class="panel"><h2>源码证据</h2><p>GitNexus graph evidence.</p></section>
<section class="panel"><h2>验证命令</h2><p>Run python3 -m unittest discover tests.</p></section>
<section class="panel"><h2>常见反模式</h2><p>Do not bypass Core.</p></section>
<section class="panel"><h2>原理与背景知识</h2><p>Core owns orchestration.</p></section>
<section class="panel"><h2>约束与风险</h2><p>Keep graph current.</p></section>
<section class="panel"><h2>推荐维护方案</h2><p>Update Core evidence first.</p></section>
<section class="panel"><h2>后续维护动作</h2><p>Run validation.</p></section>
</main></div></body></html>
"""


INTERACTIVE_FLOW_PAYLOAD = {
    "version": 1,
    "graphs": [
        {
            "id": "runtime-overview",
            "title": "整体运行时结构",
            "nodes": [
                {"id": "user", "type": "actor", "label": "用户 / operator", "position": {"x": 0, "y": 120}, "width": 220, "height": 92, "evidence": ["src/renderer/App.tsx", "gitnexus context src/renderer/App.tsx"]},
                {"id": "renderer", "type": "runtime", "label": "React renderer / route", "position": {"x": 320, "y": 120}, "width": 240, "height": 92, "evidence": ["src/renderer/App.tsx", "src/renderer/routes/index.tsx"]},
                {"id": "preload", "type": "boundary", "label": "preload electronAPI", "position": {"x": 650, "y": 120}, "width": 240, "height": 92, "evidence": ["src/preload/index.ts"]},
                {"id": "main", "type": "runtime", "label": "ipcMain / main process", "position": {"x": 980, "y": 120}, "width": 240, "height": 92, "evidence": ["src/main/index.ts", "gitnexus cypher MATCH ipcMain"]},
                {"id": "service", "type": "service", "label": "OpenClaw service", "position": {"x": 1310, "y": 40}, "width": 240, "height": 92, "evidence": ["src/main/services/openclaw.ts"]},
                {"id": "storage", "type": "data", "label": "local config storage", "position": {"x": 1310, "y": 220}, "width": 240, "height": 92, "evidence": ["src/main/config.ts"]},
            ],
            "edges": [
                {"id": "user-renderer", "source": "user", "target": "renderer", "sourceHandle": "right", "targetHandle": "left", "type": "call", "label": "UI action", "evidence": ["src/renderer/App.tsx"]},
                {"id": "renderer-preload", "source": "renderer", "target": "preload", "sourceHandle": "right", "targetHandle": "left", "type": "ipc", "label": "electronAPI call", "evidence": ["src/preload/index.ts"]},
                {"id": "preload-main", "source": "preload", "target": "main", "sourceHandle": "right", "targetHandle": "left", "type": "ipc", "label": "ipcMain handler", "evidence": ["src/main/index.ts"]},
                {"id": "main-service", "source": "main", "target": "service", "sourceHandle": "right", "targetHandle": "left", "type": "external", "label": "provider call", "evidence": ["src/main/services/openclaw.ts"]},
                {"id": "main-storage", "source": "main", "target": "storage", "sourceHandle": "bottom", "targetHandle": "left", "type": "data", "label": "read/write config", "evidence": ["src/main/config.ts"]},
                {"id": "service-main-error", "source": "service", "target": "main", "sourceHandle": "left", "targetHandle": "top", "type": "error", "label": "fallback on provider error", "evidence": ["src/main/services/openclaw.ts", "tests/low-level/openclawManagedSupport.test.ts"]},
            ],
            "layout": {"engine": "dagre", "direction": "LR", "nodeWidth": 240, "nodeHeight": 92, "ranksep": 96, "nodesep": 64, "computedAtBuildTime": True},
        }
    ],
}

INTERACTIVE_STYLE = STYLE + """
.architecture-flow { min-height: 560px; border: 1px solid var(--line); border-radius: 18px; background: #fff; }
.evidence-panel { border-left: 4px solid var(--accent); padding-left: 12px; }
.edge-legend { display: flex; gap: 8px; flex-wrap: wrap; }
.edge-call { color: #315efb; }
.edge-ipc { color: #7c3aed; }
.edge-data { color: #0f766e; }
.edge-error { color: #dc2626; }
.edge-external { color: #b45309; }
"""


def architecture_flow_block(payload: dict | None = None) -> str:
    payload_text = json.dumps(payload or INTERACTIVE_FLOW_PAYLOAD, ensure_ascii=False, indent=2)
    return f"""<div class="architecture-flow" data-flow-graph="runtime-overview" aria-label="interactive runtime architecture"></div>
<script type="application/json" data-architecture-flow>{payload_text}</script>
<div class="evidence-panel" data-architecture-flow-evidence><strong>点击节点或边查看源码证据</strong><p>Source: src/renderer/App.tsx, src/preload/index.ts, src/main/index.ts. GitNexus graph evidence backs each node and edge.</p></div>
<div class="edge-legend"><span class="edge-call">call/control</span><span class="edge-ipc">ipc boundary</span><span class="edge-data">data/storage</span><span class="edge-error">error/fallback</span><span class="edge-external">external provider</span><span>test/verification</span></div>
<table><tr><th>节点/边</th><th>非视觉 fallback</th><th>证据</th></tr><tr><td>renderer-preload</td><td>React renderer 通过 preload electronAPI 进入 ipcMain。</td><td>src/preload/index.ts</td></tr></table>"""


def write_interactive_assets(root: Path) -> None:
    import hashlib
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    js = "/* local React Flow architecture bundle fixture */\nwindow.__architectureFlowBundle = { name: 'local-react-flow-fixture' };\n"
    css = "/* local React Flow architecture styles fixture */\n.architecture-flow { min-height: 560px; }\n"
    (assets / "architecture-flow.js").write_text(js, encoding="utf-8")
    (assets / "architecture-flow.css").write_text(css, encoding="utf-8")
    provenance = {
        "packages": [
            {"name": "react", "version": "19.1.0", "license": "MIT"},
            {"name": "react-dom", "version": "19.1.0", "license": "MIT"},
            {"name": "@xyflow/react", "version": "12.8.5", "license": "MIT"},
            {"name": "@dagrejs/dagre", "version": "1.1.5", "license": "MIT"},
        ],
        "build_command": "npm run build:architecture-flow",
        "source_template_path": "templates/architecture-flow/",
        "license_notes": "Fixture metadata mirrors required local React Flow bundle provenance fields.",
        "assets": [
            {"path": "assets/architecture-flow.js", "sha256": hashlib.sha256(js.encode()).hexdigest()},
            {"path": "assets/architecture-flow.css", "sha256": hashlib.sha256(css.encode()).hexdigest()},
        ],
    }
    (assets / "architecture-flow-provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")


def write_valid_interactive_architecture_web(root: Path, payload: dict | None = None) -> None:
    (root / "modules").mkdir(parents=True)
    (root / "evidence").mkdir()
    write_interactive_assets(root)
    flow = architecture_flow_block(payload)
    index = f"""<!doctype html>
<html lang="zh-CN"><head><style>{INTERACTIVE_STYLE}</style><link rel="stylesheet" href="assets/architecture-flow.css"><script defer src="assets/architecture-flow.js"></script></head><body><div class="shell">
<header class="hero"><h1>交互式架构说明</h1><p>默认中文主入口。</p></header>
<main>
<section class="panel"><h2>总览摘要</h2><p>Source: src/renderer/App.tsx. GitNexus graph evidence explains the target application entrypoint.</p></section>
<section class="panel"><h2>为什么要先理解它</h2><p>帮助新人先理解 renderer、preload、main、service 和 storage 边界。</p></section>
<section class="panel"><h2>真实源码目录树</h2><pre class="tree">src/
├─ renderer/
├─ preload/
└─ main/index.ts</pre></section>
<section class="panel"><h2>整体运行时结构图</h2>{flow}<p>Non-visual fallback: 用户动作穿过 renderer、preload、main，再按 service/storage/error fallback 分支。</p></section>
<section class="panel"><h2>用户动作到运行时流程</h2><p>route → service → IPC 流程从 App 进入 Main，并按本地/云端/runtime 分支。</p></section>
<section class="panel"><h2>源码证据地图</h2><table><tr><td>evidence/interactive-flow.json</td><td>src/main/index.ts</td></tr></table></section>
<section class="panel"><h2>优先阅读文件</h2><a href="modules/core.html">Core</a></section>
<section class="panel"><h2>技术框架图</h2><pre class="tree">Electron
├─ React Router
├─ preload/electronAPI
└─ ipcMain services</pre></section>
<section class="panel"><h2>边界与不变量</h2><p>renderer/preload/main/runtime 边界必须清楚；分叉 branch 包括成功、失败和 fallback。</p></section>
<section class="panel"><h2>安全修改方式</h2><p>先改 evidence，再改页面。</p></section>
<section class="panel"><h2>验证命令</h2><p>Run python3 -m unittest discover tests.</p></section>
<section class="panel"><h2>常见反模式</h2><p>不要跳过 evidence，不要把 index.html/evidence JSON 当成架构节点。</p></section>
<section class="panel"><h2>原理与背景知识</h2><p>React Flow interactive-flow 使用本地 bundle 和嵌入 payload。</p></section>
<section class="panel"><h2>约束与风险</h2><p>Stale index 需要标注。</p></section>
<section class="panel"><h2>推荐维护方案</h2><p>保持单入口 index。</p></section>
<section class="panel"><h2>后续维护动作</h2><p>补齐模块。</p></section>
</main></div></body></html>"""
    module = f"""<!doctype html>
<html lang="zh-CN"><head><style>{INTERACTIVE_STYLE}</style><link rel="stylesheet" href="../assets/architecture-flow.css"><script defer src="../assets/architecture-flow.js"></script></head><body><div class="shell">
<nav><a href="../index.html">返回主页面 index.html</a></nav>
<header class="hero"><h1>Core</h1></header>
<main>
<section class="panel"><h2>模块职责</h2><p>Core receives requests. Source: src/main/index.ts.</p></section>
<section class="panel"><h2>为什么存在</h2><p>It coordinates services from one entrypoint.</p></section>
<section class="panel"><h2>真实源码目录树</h2><pre class="tree">src/main/
└─ index.ts</pre></section>
<section class="panel"><h2>整体运行时结构图</h2>{flow}<p>Non-visual fallback: Entry calls Core, then Core chooses success, error, or fallback.</p></section>
<section class="panel"><h2>数据如何流动</h2><p>src/main/index.ts handler 通过 API/IPC/service 入口调用 Core。</p></section>
<section class="panel"><h2>用户动作到运行时流程</h2><p>输入先到入口，再进入服务；分支表覆盖 success/error/fallback。</p></section>
<section class="panel"><h2>源码阅读入口</h2><p>Start at src/main/index.ts.</p></section>
<section class="panel"><h2>源码证据地图</h2><p>GitNexus: gitnexus context src/main/index.ts. Graph: Entry -> Service.</p></section>
<section class="panel"><h2>优先阅读文件</h2><table><tr><th>文件</th><th>关键符号/handler/API</th></tr><tr><td>src/main/index.ts</td><td>ipcMain handler API service entry</td></tr></table></section>
<section class="panel"><h2>技术框架图</h2><pre class="tree">Electron main
└─ Core service</pre></section>
<section class="panel"><h2>边界与不变量</h2><p>Keep entry/service boundaries.</p></section>
<section class="panel"><h2>Branch paths</h2><table><tr><th>分支</th><th>触发条件</th></tr><tr><td>success</td><td>service returns data</td></tr><tr><td>error</td><td>handler raises error</td></tr><tr><td>fallback</td><td>service unavailable</td></tr></table></section>
<section class="panel"><h2>安全修改方式</h2><p>Modify source and update tests.</p></section>
<section class="panel"><h2>源码证据</h2><p>GitNexus graph evidence.</p></section>
<section class="panel"><h2>验证命令</h2><p>Run python3 -m unittest discover tests.</p></section>
<section class="panel"><h2>常见反模式</h2><p>Do not bypass Core.</p></section>
<section class="panel"><h2>原理与背景知识</h2><p>Core owns orchestration.</p></section>
<section class="panel"><h2>约束与风险</h2><p>Keep graph current.</p></section>
<section class="panel"><h2>推荐维护方案</h2><p>Update Core evidence first.</p></section>
<section class="panel"><h2>后续维护动作</h2><p>Run validation.</p></section>
</main></div></body></html>"""
    (root / "index.html").write_text(index, encoding="utf-8")
    (root / "modules" / "core.html").write_text(module, encoding="utf-8")
    (root / "evidence" / "interactive-flow.json").write_text(json.dumps(payload or INTERACTIVE_FLOW_PAYLOAD, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "wiki-meta.json").write_text(json.dumps({"generated_at": "2026-04-30T00:00:00Z", "repo": "/tmp/repo", "git_commit": "abc123", "gitnexus_version": "gitnexus 1.6.3", "execution_boundary": "GitNexus supplies graph/index evidence; Codex authors architecture-web pages directly. Native gitnexus wiki provider/API-key setup is separate.", "mode": "architecture-web", "diagram_mode": "interactive-flow", "language": "zh-CN", "visual_style": "project-explainer-web", "entrypoint": "index.html", "modules": ["core"], "evidence_files": [{"source": "/tmp/preflight.md", "path": "evidence/interactive-flow.json"}]}, indent=2), encoding="utf-8")
    (root / "evidence" / "module-map.json").write_text(json.dumps({"modules": [{"slug": "core", "title": "Core", "source_files": ["src/main/index.ts"], "graph_commands": ["gitnexus context src/main/index.ts"], "evidence_refs": ["evidence/interactive-flow.json"], "verification_commands": ["python3 -m unittest discover tests"]}]}, indent=2), encoding="utf-8")
    (root / "evidence" / "route-service-trace.json").write_text(json.dumps({"flows": [{"slug": "entry-to-service", "title": "Entry to service", "entrypoints": ["src/main/index.ts"], "services": ["OpenClawService"], "graph_edges": ["src/main/index.ts -> OpenClawService.send"], "evidence_refs": ["evidence/interactive-flow.json"]}]}, indent=2), encoding="utf-8")

def write_valid_architecture_web(root: Path) -> None:
    (root / "modules").mkdir(parents=True)
    (root / "evidence").mkdir()
    (root / "index.html").write_text(OVERVIEW_HTML, encoding="utf-8")
    (root / "modules" / "core.html").write_text(MODULE_HTML, encoding="utf-8")
    (root / "wiki-meta.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-04-28T00:00:00Z",
                "repo": "/tmp/repo",
                "git_commit": "abc123",
                "gitnexus_version": "gitnexus 1.6.3",
                "execution_boundary": "GitNexus supplies graph/index evidence; Codex authors architecture-web pages directly. Native gitnexus wiki provider/API-key setup is separate.",
                "mode": "architecture-web",
                "language": "zh-CN",
                "visual_style": "project-explainer-web",
                "entrypoint": "index.html",
                "modules": ["core"],
                "evidence_files": [{"source": "/tmp/preflight.md", "path": "evidence/preflight.md"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "evidence" / "module-map.json").write_text(
        json.dumps(
            {
                "modules": [
                    {
                        "slug": "core",
                        "title": "Core",
                        "source_files": ["src/app.ts"],
                        "graph_commands": ["gitnexus context src/app.ts"],
                        "evidence_refs": ["evidence/preflight.md"],
                        "verification_commands": ["python3 -m unittest discover tests"],
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "evidence" / "route-service-trace.json").write_text(
        json.dumps(
            {
                "flows": [
                    {
                        "slug": "entry-to-service",
                        "title": "Entry to service",
                        "entrypoints": ["src/app.ts"],
                        "services": ["AppService"],
                        "graph_edges": ["src/app.ts -> AppService.handle"],
                        "evidence_refs": ["evidence/preflight.md"],
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )


FUNCTION_TRACE_PAYLOAD = {
    "version": 1,
    "graphs": [
        {
            "id": "auth-session-trace",
            "title": "Auth session function trace",
            "nodes": [
                {
                    "id": "auth-provider",
                    "type": "component",
                    "label": "AuthProvider",
                    "symbolId": "auth-session:src/renderer/src/contexts/AuthContext.tsx:42:AuthProvider",
                    "position": {"x": 0, "y": 100},
                    "width": 240,
                    "height": 92,
                    "evidence": ["src/renderer/src/contexts/AuthContext.tsx:42 AuthProvider"],
                },
                {
                    "id": "login",
                    "type": "service",
                    "label": "AuthService.login",
                    "symbolId": "auth-session:src/renderer/src/services/AuthService.ts:88:login",
                    "position": {"x": 330, "y": 100},
                    "width": 240,
                    "height": 92,
                    "evidence": ["src/renderer/src/services/AuthService.ts:88 login"],
                },
                {
                    "id": "persist",
                    "type": "service",
                    "label": "TokenService.persist",
                    "symbolId": "auth-session:src/renderer/src/services/TokenService.ts:27:persist",
                    "position": {"x": 660, "y": 20},
                    "width": 240,
                    "height": 92,
                    "evidence": ["src/renderer/src/services/TokenService.ts:27 persist"],
                },
                {
                    "id": "failure",
                    "type": "branch",
                    "label": "AuthContext.handleLoginError",
                    "symbolId": "auth-session:src/renderer/src/contexts/AuthContext.tsx:133:handleLoginError",
                    "position": {"x": 660, "y": 190},
                    "width": 280,
                    "height": 92,
                    "evidence": ["src/renderer/src/contexts/AuthContext.tsx:133 handleLoginError"],
                },
            ],
            "edges": [
                {
                    "id": "auth-provider-login",
                    "source": "auth-provider",
                    "target": "login",
                    "type": "call",
                    "label": "calls",
                    "sourceHandle": "right",
                    "targetHandle": "left",
                    "evidence": ["src/renderer/src/contexts/AuthContext.tsx:77"],
                },
                {
                    "id": "login-persist",
                    "source": "login",
                    "target": "persist",
                    "type": "data",
                    "label": "updates state",
                    "sourceHandle": "right",
                    "targetHandle": "left",
                    "evidence": ["src/renderer/src/services/AuthService.ts:101"],
                },
                {
                    "id": "login-failure",
                    "source": "login",
                    "target": "failure",
                    "type": "error",
                    "label": "error",
                    "sourceHandle": "bottom",
                    "targetHandle": "left",
                    "evidence": ["tests/low-level/auth-session.test.ts:41"],
                },
            ],
            "layout": {"engine": "dagre", "direction": "LR", "nodeWidth": 240, "nodeHeight": 92},
        }
    ],
}


def function_trace_flow_block(payload: dict | None = None) -> str:
    payload_text = json.dumps(payload or FUNCTION_TRACE_PAYLOAD, ensure_ascii=False, indent=2)
    return f"""<div class="architecture-flow" data-flow-graph="auth-session-trace" aria-label="auth session function trace"></div>
<script type="application/json" data-architecture-flow>{payload_text}</script>
<div class="evidence-panel" data-architecture-flow-evidence><strong>点击函数节点查看源码证据</strong><p>Source: src/renderer/src/contexts/AuthContext.tsx, src/renderer/src/services/AuthService.ts, src/renderer/src/services/TokenService.ts.</p></div>
<div class="edge-legend"><span class="edge-call">calls</span><span class="edge-data">updates state</span><span class="edge-error">error</span><span>test covers</span></div>
<table><tr><th>函数边</th><th>非视觉 fallback</th><th>证据</th></tr><tr><td>AuthService.login → TokenService.persist</td><td>登录成功后持久化 token；失败进入错误分支。</td><td>src/renderer/src/services/AuthService.ts:101</td></tr></table>"""


def write_valid_function_depth_architecture_web(root: Path, payload: dict | None = None) -> None:
    write_valid_interactive_architecture_web(root)
    index = root / "index.html"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            "<section class=\"panel\"><h2>优先阅读文件</h2><a href=\"modules/core.html\">Core</a></section>",
            "<section class=\"panel\"><h2>函数视图入口</h2><p>函数级细节位于模块页，概览只保留可读的系统关系。</p></section><section class=\"panel\"><h2>优先阅读文件</h2><a href=\"modules/core.html\">Auth session 函数视图</a></section>",
        ),
        encoding="utf-8",
    )
    module = root / "modules" / "core.html"
    html = module.read_text(encoding="utf-8")
    html = re.sub(
        r'<section class="panel"><h2>整体运行时结构图</h2>.*?</section>',
        f'<section class="panel"><h2>整体运行时结构图</h2><p>函数级 trace 使用 React Flow 展示 Auth/session 的调用、状态更新和错误分支。</p>{function_trace_flow_block(payload)}</section>',
        html,
        count=1,
        flags=re.S,
    )
    html = html.replace(
        '<section class="panel"><h2>源码证据</h2><p>GitNexus graph evidence.</p></section>',
        """<section class="panel"><h2>函数清单</h2>
<input data-function-inventory-search aria-label="搜索函数清单" value="">
<table data-function-inventory data-module-id="auth-session">
<tr><th>symbolId</th><th>symbol</th><th>kind</th><th>file</th><th>line</th><th>trace</th><th>tests</th></tr>
<tr><td>auth-session:src/renderer/src/contexts/AuthContext.tsx:42:AuthProvider</td><td>AuthProvider</td><td>component</td><td>src/renderer/src/contexts/AuthContext.tsx</td><td>42</td><td>auth-login</td><td>tests/low-level/auth-session.test.ts</td></tr>
<tr><td>auth-session:src/renderer/src/services/AuthService.ts:88:login</td><td>AuthService.login</td><td>service</td><td>src/renderer/src/services/AuthService.ts</td><td>88</td><td>auth-login</td><td>tests/low-level/auth-session.test.ts</td></tr>
<tr><td>auth-session:src/renderer/src/services/TokenService.ts:27:persist</td><td>TokenService.persist</td><td>service</td><td>src/renderer/src/services/TokenService.ts</td><td>27</td><td>auth-login</td><td>tests/low-level/auth-session.test.ts</td></tr>
<tr><td>auth-session:src/renderer/src/contexts/AuthContext.tsx:133:handleLoginError</td><td>AuthContext.handleLoginError</td><td>helper</td><td>src/renderer/src/contexts/AuthContext.tsx</td><td>133</td><td>auth-login</td><td>tests/low-level/auth-session.test.ts</td></tr>
</table></section>
<section class="panel"><h2>源码证据</h2><p>GitNexus graph evidence and direct source evidence back every function row.</p></section>""",
    )
    module.write_text(html, encoding="utf-8")

    meta_path = root / "wiki-meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["functionDepth"] = {
        "enabled": True,
        "coverageScope": "in-scope-architecture-functions",
        "mapPath": "evidence/function-architecture-map.json",
        "validatorMode": "function-depth",
    }
    meta["evidence_files"].append({"source": "/tmp/function-architecture-map.json", "path": "evidence/function-architecture-map.json"})
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    function_map = {
        "schemaVersion": 1,
        "repo": "cpilot-web-lucyna",
        "git": {"head": "abc123", "gitnexusIndexedCommit": "abc123", "indexFreshness": "fresh"},
        "modules": [
            {
                "moduleId": "auth-session",
                "label": "Auth session",
                "page": "modules/core.html",
                "sourceRoots": [
                    "src/renderer/src/contexts/AuthContext.tsx",
                    "src/renderer/src/services/AuthService.ts",
                    "src/renderer/src/services/TokenService.ts",
                ],
                "symbols": [
                    {
                        "symbolId": "auth-session:src/renderer/src/contexts/AuthContext.tsx:42:AuthProvider",
                        "name": "AuthProvider",
                        "kind": "component",
                        "file": "src/renderer/src/contexts/AuthContext.tsx",
                        "line": 42,
                        "responsibility": "Owns renderer authentication state and delegates login.",
                        "callers": [],
                        "callees": ["auth-session:src/renderer/src/services/AuthService.ts:88:login"],
                        "traceIds": ["auth-login"],
                        "testRefs": ["tests/low-level/auth-session.test.ts"],
                        "evidenceSource": "both",
                        "indexFreshness": "fresh",
                    },
                    {
                        "symbolId": "auth-session:src/renderer/src/services/AuthService.ts:88:login",
                        "name": "AuthService.login",
                        "kind": "service",
                        "file": "src/renderer/src/services/AuthService.ts",
                        "line": 88,
                        "responsibility": "Performs login and returns token/session result.",
                        "callers": ["auth-session:src/renderer/src/contexts/AuthContext.tsx:42:AuthProvider"],
                        "callees": ["auth-session:src/renderer/src/services/TokenService.ts:27:persist"],
                        "traceIds": ["auth-login"],
                        "testRefs": ["tests/low-level/auth-session.test.ts"],
                        "evidenceSource": "both",
                        "indexFreshness": "fresh",
                    },
                    {
                        "symbolId": "auth-session:src/renderer/src/services/TokenService.ts:27:persist",
                        "name": "TokenService.persist",
                        "kind": "service",
                        "file": "src/renderer/src/services/TokenService.ts",
                        "line": 27,
                        "responsibility": "Persists login token.",
                        "callers": ["auth-session:src/renderer/src/services/AuthService.ts:88:login"],
                        "callees": [],
                        "traceIds": ["auth-login"],
                        "testRefs": ["tests/low-level/auth-session.test.ts"],
                        "evidenceSource": "both",
                        "indexFreshness": "fresh",
                    },
                    {
                        "symbolId": "auth-session:src/renderer/src/contexts/AuthContext.tsx:133:handleLoginError",
                        "name": "AuthContext.handleLoginError",
                        "kind": "helper",
                        "file": "src/renderer/src/contexts/AuthContext.tsx",
                        "line": 133,
                        "responsibility": "Handles failed login branch.",
                        "callers": ["auth-session:src/renderer/src/services/AuthService.ts:88:login"],
                        "callees": [],
                        "traceIds": ["auth-login"],
                        "testRefs": ["tests/low-level/auth-session.test.ts"],
                        "evidenceSource": "both",
                        "indexFreshness": "fresh",
                    },
                ],
                "exclusions": [
                    {
                        "file": "src/renderer/src/contexts/AuthContext.tsx",
                        "name": "AuthState",
                        "reason": "type-only",
                    }
                ],
            }
        ],
        "traces": [
            {
                "traceId": "auth-login",
                "moduleId": "auth-session",
                "entrySymbolId": "auth-session:src/renderer/src/contexts/AuthContext.tsx:42:AuthProvider",
                "nodeSymbolIds": [
                    "auth-session:src/renderer/src/contexts/AuthContext.tsx:42:AuthProvider",
                    "auth-session:src/renderer/src/services/AuthService.ts:88:login",
                    "auth-session:src/renderer/src/services/TokenService.ts:27:persist",
                    "auth-session:src/renderer/src/contexts/AuthContext.tsx:133:handleLoginError",
                ],
                "edges": [
                    {
                        "from": "auth-session:src/renderer/src/contexts/AuthContext.tsx:42:AuthProvider",
                        "to": "auth-session:src/renderer/src/services/AuthService.ts:88:login",
                        "kind": "calls",
                    },
                    {
                        "from": "auth-session:src/renderer/src/services/AuthService.ts:88:login",
                        "to": "auth-session:src/renderer/src/services/TokenService.ts:27:persist",
                        "kind": "updates-state",
                    },
                    {
                        "from": "auth-session:src/renderer/src/services/AuthService.ts:88:login",
                        "to": "auth-session:src/renderer/src/contexts/AuthContext.tsx:133:handleLoginError",
                        "kind": "error",
                    },
                ],
            }
        ],
    }
    (root / "evidence" / "function-architecture-map.json").write_text(
        json.dumps(function_map, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (root / "evidence" / "visual-qa-function-drilldown.json").write_text(
        json.dumps(
            {
                "checks": [
                    {
                        "url": "file:///tmp/core.html",
                        "graph_id": "auth-session-trace",
                        "node_id": "auth-provider",
                        "drag_delta": {"x": 44, "y": 21},
                    }
                ],
                "inventory": {
                    "auth-session": {
                        "rowCount": 4,
                        "initialInteractiveLoadMs": 180,
                        "searchFilterUpdateMs": 32,
                        "paginationOrVirtualization": False,
                        "defaultVisibleRows": 25,
                    }
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "evidence" / "architecture-review-function-drilldown.md").write_text(
        "# Architecture review\n\nPASS: function traces explain cpilot application architecture with branch evidence.\n",
        encoding="utf-8",
    )


class ValidateSkillTests(unittest.TestCase):
    def test_current_skill_package_passes(self) -> None:
        self.assertEqual(validator.validate_skill(ROOT), [])

    def test_detects_forbidden_positive_provider_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp) / "skill"
            shutil.copytree(ROOT, temp_root)
            skill = temp_root / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8")
                + "\n\nBad claim: GitNexus has a Codex provider.\n",
                encoding="utf-8",
            )
            errors = validator.validate_skill(temp_root)
            self.assertTrue(any("unsupported positive integration claim" in err for err in errors))

    def test_generated_docs_require_graph_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp) / "docs"
            docs.mkdir()
            (docs / "overview.md").write_text("# Overview\nNo evidence yet.\n", encoding="utf-8")
            (docs / "module.md").write_text("# Module\n", encoding="utf-8")
            (docs / "leaf.md").write_text("# Leaf\n", encoding="utf-8")
            errors = validator.validate_docs(docs)
            self.assertTrue(any("source/GitNexus evidence" in err for err in errors))

    def test_generated_docs_with_evidence_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp) / "docs"
            docs.mkdir()
            (docs / "overview.md").write_text(
                "# Overview\nGenerated with GitNexus version 1.6.3; index status current.\n"
                "Graph: gitnexus cypher MATCH ...\n",
                encoding="utf-8",
            )
            (docs / "module.md").write_text("# Module\nSource: src/module.ts\n", encoding="utf-8")
            (docs / "leaf.md").write_text("# Leaf\nGitNexus: gitnexus context Foo\n", encoding="utf-8")
            self.assertEqual(validator.validate_docs(docs), [])

    def test_scaffold_respects_explicit_module_without_default_append(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp) / "wiki"
            subprocess.check_call([
                "python3",
                str(ROOT / "scripts" / "scaffold-wiki.py"),
                "--repo",
                str(ROOT),
                "--out",
                str(docs),
                "--module",
                "app",
                "--leaf",
                "entrypoints",
            ])
            self.assertTrue((docs / "modules" / "app.md").is_file())
            self.assertFalse((docs / "modules" / "core.md").exists())
            self.assertEqual(validator.validate_docs(docs), [])

    def test_scaffold_interactive_flow_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample-architecture-wiki"
            subprocess.check_call([
                "python3",
                str(ROOT / "scripts" / "scaffold-architecture-web.py"),
                "--repo",
                str(ROOT),
                "--out",
                str(out),
                "--slug",
                "sample",
                "--module",
                "renderer",
                "--module",
                "preload",
                "--module",
                "main",
                "--force",
            ])
            self.assertTrue((out / "assets" / "architecture-flow.js").is_file())
            self.assertTrue((out / "assets" / "architecture-flow.css").is_file())
            html_and_css = "\n".join(p.read_text(encoding="utf-8") for p in [out / "index.html", out / "assets" / "architecture-flow.css"])
            self.assertNotRegex(html_and_css, r"<script[^>]+https?://|<link[^>]+https?://|<img[^>]+https?://|url\(https?://|unpkg|jsdelivr|//cdn")

    def test_scaffold_interactive_flow_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample-architecture-wiki"
            subprocess.check_call([
                "python3",
                str(ROOT / "scripts" / "scaffold-architecture-web.py"),
                "--repo",
                str(ROOT),
                "--out",
                str(out),
                "--slug",
                "sample",
                "--module",
                "renderer",
                "--module",
                "preload",
                "--module",
                "main",
                "--force",
            ])
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("data-architecture-flow", html)
            payloads = validator.extract_interactive_flow_payloads(html, out / "index.html")
            self.assertTrue(payloads)
            graph = payloads[0]["graphs"][0]
            self.assertTrue(graph["nodes"])
            self.assertTrue(graph["edges"])
            for node in graph["nodes"]:
                self.assertIn("position", node)
                self.assertIn("width", node)
                self.assertIn("height", node)
            for edge in graph["edges"]:
                self.assertIn("sourceHandle", edge)
                self.assertIn("targetHandle", edge)

    def test_no_flag_scaffold_default_has_required_interactive_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample-architecture-wiki"
            subprocess.check_call([
                "python3",
                str(ROOT / "scripts" / "scaffold-architecture-web.py"),
                "--repo",
                str(ROOT),
                "--out",
                str(out),
                "--slug",
                "sample",
                "--module",
                "renderer",
                "--module",
                "preload",
                "--module",
                "main",
                "--force",
            ])
            meta = json.loads((out / "wiki-meta.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["diagram_mode"], "interactive-flow")
            self.assertFalse((out / "assets" / "mermaid.min.js").exists())
            pages = [out / "index.html", *sorted((out / "modules").glob("*.html"))]
            for page in pages:
                html = page.read_text(encoding="utf-8")
                containers = re.findall(r'data-flow-graph="([^"]+)"', html)
                payloads = validator.extract_interactive_flow_payloads(html, page)
                graph_ids = {graph["id"] for payload in payloads for graph in payload.get("graphs", [])}
                if page.name == "index.html":
                    self.assertGreaterEqual(len(containers), 4)
                    self.assertTrue({"runtime-overview", "source-structure", "technology-framework", "branch-fallback-test"} <= set(containers))
                else:
                    self.assertGreaterEqual(len(containers), 1)
                self.assertTrue(set(containers) <= graph_ids)
            self.assertEqual(validator.validate_architecture_web(out, allow_placeholders=True), [])

    def test_payload_container_graph_id_consistency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "mismatched-container-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            index = out / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace('data-flow-graph="runtime-overview"', 'data-flow-graph="missing-runtime"'),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("missing matching payload graph ids" in err for err in errors))

    def test_validator_rejects_zero_interactive_output_when_meta_requests_interactive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "static-only-architecture-wiki"
            write_valid_architecture_web(out)
            meta_path = out / "wiki-meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["diagram_mode"] = "interactive-flow"
            meta["interactive_flow"] = {"mode": "interactive-flow", "file_url_safe": True}
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("primary React Flow" in err or "data-flow-graph" in err for err in errors))

    def test_validator_rejects_visible_primary_mermaid_or_svg_page_wide(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "visible-static-primary-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            index = out / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "</main>",
                    '<section class="panel"><h2>静态主图</h2><div class="diagram"><svg role="img"><path d="M0 0L10 10"/></svg></div><pre class="diagram-source">graph TB\\n  A --> B</pre></section></main>',
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("visible primary" in err for err in errors))

    def test_validator_allows_collapsed_audit_graph_source_for_interactive_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "collapsed-audit-interactive-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            index = out / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "</main>",
                    '<details class="source-audit"><summary>图源审计</summary><div class="diagram"><svg role="img"><path d="M0 0L10 10"/></svg></div><pre class="diagram-source">graph TB\\n  A --> B</pre></details></main>',
                ),
                encoding="utf-8",
            )
            self.assertEqual(validator.validate_architecture_web(out), [])

    def test_visual_qa_report_requires_measured_drag_delta(self) -> None:
        bad_errors: list[str] = []
        validator.validate_visual_qa_report(
            {"checks": [{"url": "file:///tmp/index.html", "graph_id": "runtime-overview", "node_id": "renderer", "nodesDraggable": True}]},
            bad_errors,
            Path("visual-qa-react-flow-drag.json"),
        )
        self.assertTrue(any("measured drag delta" in err or "marker-only" in err for err in bad_errors))
        good_errors: list[str] = []
        validator.validate_visual_qa_report(
            {"checks": [{"url": "file:///tmp/index.html", "graph_id": "runtime-overview", "node_id": "renderer", "drag_delta": {"x": 96, "y": 32}}]},
            good_errors,
            Path("visual-qa-react-flow-drag.json"),
        )
        self.assertEqual(good_errors, [])

    def test_function_depth_fixture_passes_strict_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "function-depth-architecture-wiki"
            write_valid_function_depth_architecture_web(out)
            self.assertEqual(validator.validate_architecture_web(out), [])

    def test_function_depth_meta_requires_canonical_function_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing-function-map-architecture-wiki"
            write_valid_function_depth_architecture_web(out)
            (out / "evidence" / "function-architecture-map.json").unlink()
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("function-architecture-map.json" in err for err in errors), errors)

    def test_function_depth_requires_module_inventory_and_trace_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing-inventory-architecture-wiki"
            write_valid_function_depth_architecture_web(out)
            module = out / "modules" / "core.html"
            module.write_text(
                re.sub(
                    r'<section class="panel"><h2>函数清单</h2>.*?</section>',
                    '<section class="panel"><h2>函数清单</h2><p>Missing inventory table.</p></section>',
                    module.read_text(encoding="utf-8"),
                    count=1,
                    flags=re.S,
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("function inventory" in err.lower() or "函数清单" in err for err in errors), errors)

    def test_function_depth_rejects_trace_node_without_inventory_symbol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing-trace-symbol-architecture-wiki"
            write_valid_function_depth_architecture_web(out)
            function_map_path = out / "evidence" / "function-architecture-map.json"
            function_map = json.loads(function_map_path.read_text(encoding="utf-8"))
            function_map["traces"][0]["nodeSymbolIds"].append("auth-session:src/renderer/src/services/Missing.ts:1:missing")
            function_map_path.write_text(json.dumps(function_map, ensure_ascii=False, indent=2), encoding="utf-8")
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("trace" in err.lower() and "inventory" in err.lower() for err in errors), errors)

    def test_function_depth_rejects_generic_trace_graph_without_function_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "generic-trace-architecture-wiki"
            payload = json.loads(json.dumps(FUNCTION_TRACE_PAYLOAD))
            for node, label in zip(payload["graphs"][0]["nodes"], ["Renderer", "Service", "Runtime", "Fallback"]):
                node["label"] = label
                node.pop("symbolId", None)
            write_valid_function_depth_architecture_web(out, payload)
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("generic" in err.lower() or "symbol" in err.lower() for err in errors), errors)

    def test_function_depth_requires_visual_qa_inventory_performance_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing-function-visual-qa-architecture-wiki"
            write_valid_function_depth_architecture_web(out)
            (out / "evidence" / "visual-qa-function-drilldown.json").unlink()
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("visual" in err.lower() and "function" in err.lower() for err in errors), errors)

    def test_function_depth_enforces_trace_node_readability_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "oversized-trace-architecture-wiki"
            payload = json.loads(json.dumps(FUNCTION_TRACE_PAYLOAD))
            base_node = payload["graphs"][0]["nodes"][0]
            payload["graphs"][0]["nodes"] = [
                {
                    **base_node,
                    "id": f"function-{index}",
                    "label": f"Function{index}",
                    "symbolId": f"auth-session:src/example.ts:{index}:Function{index}",
                    "position": {"x": index * 20, "y": (index % 5) * 120},
                }
                for index in range(41)
            ]
            payload["graphs"][0]["edges"] = [
                {
                    "id": f"edge-{index}",
                    "source": f"function-{index}",
                    "target": f"function-{index + 1}",
                    "type": "call",
                    "label": "calls",
                    "sourceHandle": "right",
                    "targetHandle": "left",
                    "evidence": [f"src/example.ts:{index}"],
                }
                for index in range(40)
            ]
            write_valid_function_depth_architecture_web(out, payload)
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("cap" in err.lower() or "40" in err or "readability" in err.lower() for err in errors), errors)

    def test_file_url_payload_does_not_require_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "interactive-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("data-architecture-flow", html)
            self.assertNotRegex(html, r"fetch\(['\"]evidence/")
            self.assertEqual(validator.validate_architecture_web(out), [])

    def test_validate_rejects_missing_interactive_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing-bundle-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            (out / "assets" / "architecture-flow.js").unlink()
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("architecture-flow.js" in err or "interactive bundle" in err for err in errors))

    def test_validate_rejects_network_react_flow_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "network-asset-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            index = out / "index.html"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "</head>",
                    '<script src="https://unpkg.com/@xyflow/react/dist/umd/index.js"></script><link rel="stylesheet" href="https://cdn.example/react-flow.css"><style>.bad{background:url(https://cdn.example/bg.png)}</style></head>',
                ).replace(
                    "</body>",
                    '<img src="https://cdn.example/tracker.png" alt="network runtime asset"></body>',
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("network" in err.lower() or "cdn" in err.lower() for err in errors))

    def test_validate_requires_bundle_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing-provenance-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            (out / "assets" / "architecture-flow-provenance.json").unlink()
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("provenance" in err.lower() for err in errors))

    def test_validate_rejects_nodes_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "node-without-evidence-architecture-wiki"
            payload = json.loads(json.dumps(INTERACTIVE_FLOW_PAYLOAD))
            payload["graphs"][0]["nodes"][0].pop("evidence")
            write_valid_interactive_architecture_web(out, payload)
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("node" in err.lower() and "evidence" in err.lower() for err in errors))

    def test_validate_rejects_untyped_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "untyped-edge-architecture-wiki"
            payload = json.loads(json.dumps(INTERACTIVE_FLOW_PAYLOAD))
            payload["graphs"][0]["edges"][0].pop("type")
            write_valid_interactive_architecture_web(out, payload)
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("edge" in err.lower() and "type" in err.lower() for err in errors))

    def test_validate_rejects_artifact_centric_interactive_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "artifact-interactive-architecture-wiki"
            payload = json.loads(json.dumps(INTERACTIVE_FLOW_PAYLOAD))
            payload["graphs"][0]["nodes"][0]["id"] = "index-html"
            payload["graphs"][0]["nodes"][0]["label"] = "index.html 主入口"
            payload["graphs"][0]["nodes"][0]["evidence"] = ["_learn_web/cpilot/index.html"]
            payload["graphs"][0]["edges"][0]["label"] = "modules/*.html navigation"
            payload["graphs"][0]["edges"][0]["evidence"] = ["wiki-meta.json", "evidence/*.json"]
            write_valid_interactive_architecture_web(out, payload)
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("artifact-centric" in err for err in errors))

    def test_validate_accepts_react_flow_without_mermaid_graph_tb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "interactive-no-mermaid-architecture-wiki"
            write_valid_interactive_architecture_web(out)
            self.assertNotIn("graph TB", (out / "index.html").read_text(encoding="utf-8"))
            self.assertEqual(validator.validate_architecture_web(out), [])

    def test_architecture_scaffold_allows_placeholders_but_strict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample-architecture-wiki"
            subprocess.check_call([
                "python3",
                str(ROOT / "scripts" / "scaffold-architecture-web.py"),
                "--repo",
                str(ROOT),
                "--out",
                str(out),
                "--module",
                "web routes",
            ])
            self.assertTrue((out / "index.html").is_file())
            self.assertTrue((out / "modules" / "web-routes.html").is_file())
            self.assertEqual(validator.validate_architecture_web(out, allow_placeholders=True), [])
            strict_errors = validator.validate_architecture_web(out)
            self.assertTrue(any("placeholder" in err.lower() for err in strict_errors))

    def test_valid_architecture_web_fixture_passes_strict_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "valid-architecture-wiki"
            write_valid_architecture_web(out)
            self.assertEqual(validator.validate_architecture_web(out), [])

    def test_architecture_web_requires_index_links_to_modules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "missing-link-architecture-wiki"
            write_valid_architecture_web(out)
            (out / "index.html").write_text(OVERVIEW_HTML.replace('href="modules/core.html"', 'href="modules/missing.html"'), encoding="utf-8")
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("click-through link" in err for err in errors))

    def test_architecture_web_requires_single_root_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "extra-root-architecture-wiki"
            write_valid_architecture_web(out)
            (out / "overview.html").write_text(OVERVIEW_HTML, encoding="utf-8")
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("exactly one main HTML page" in err for err in errors))

    def test_architecture_web_requires_chinese_project_explainer_style(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bad-style-architecture-wiki"
            write_valid_architecture_web(out)
            (out / "index.html").write_text(OVERVIEW_HTML.replace('lang="zh-CN"', 'lang="en"').replace('class="hero"', 'class="banner"'), encoding="utf-8")
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("lang=zh-CN" in err for err in errors))
            self.assertTrue(any("hero" in err for err in errors))

    def test_architecture_web_fails_cdn_mermaid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "cdn-architecture-wiki"
            write_valid_architecture_web(out)
            (out / "index.html").write_text(
                OVERVIEW_HTML.replace(
                    "</body>",
                    '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script></body>',
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("CDN" in err or "network" in err for err in errors))

    def test_architecture_web_fails_missing_schema_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bad-architecture-wiki"
            write_valid_architecture_web(out)
            (out / "evidence" / "module-map.json").write_text('{"modules":[{"slug":"core"}]}\n', encoding="utf-8")
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("missing field" in err for err in errors))

    def test_architecture_web_fails_artifact_centric_diagram(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "artifact-centric-architecture-wiki"
            write_valid_architecture_web(out)
            artifact_source = """graph TB
  Reader[初学者读者] --> Index[index.html 主入口]
  Index --> Modules["modules/*.html 模块页"]
  Index --> 源码证据["evidence/*.json"]
  源码证据 --> Meta[wiki-meta.json]
"""
            artifact_graph = graph_block(artifact_source)
            (out / "index.html").write_text(
                OVERVIEW_HTML.replace(
                    graph_block(OVERVIEW_RUNTIME_SOURCE),
                    artifact_graph,
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("artifact-centric" in err for err in errors))

    def test_architecture_web_rejects_repeated_feynman_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "feynman-repeat-architecture-wiki"
            write_valid_architecture_web(out)
            module = out / "modules" / "core.html"
            module.write_text(
                MODULE_HTML.replace(
                    "<section class=\"panel\"><h2>源码证据</h2>",
                    "<section class=\"panel\"><h2>费曼复述</h2><p>重复模板 section。</p></section><section class=\"panel\"><h2>源码证据</h2>",
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("费曼复述" in err for err in errors))

    def test_architecture_web_rejects_hidden_generic_contract_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hidden-contract-architecture-wiki"
            write_valid_architecture_web(out)
            index = out / "index.html"
            index.write_text(
                OVERVIEW_HTML.replace(
                    "</main>",
                    '<div style="display:none">This contract text supports strict validation and uses renderer, preload, ipcMain.</div></main>',
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("隐藏通用契约" in err or "hidden generic contract" in err for err in errors))

    def test_architecture_web_rejects_straight_line_deep_graph(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "straight-line-architecture-wiki"
            write_valid_architecture_web(out)
            straight_source = """graph TB
  User[用户] --> Renderer[Renderer]
  Renderer --> Preload[Preload]
  Preload --> Main[Main]
  Main --> Runtime[Runtime]
"""
            straight = graph_block(straight_source)
            (out / "index.html").write_text(
                OVERVIEW_HTML.replace(
                    graph_block(OVERVIEW_RUNTIME_SOURCE),
                    straight,
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("straight line" in err for err in errors))

    def test_architecture_web_rejects_visible_raw_graph_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "visible-raw-graph-architecture-wiki"
            write_valid_architecture_web(out)
            index = out / "index.html"
            index.write_text(
                OVERVIEW_HTML.replace(
                    graph_block(OVERVIEW_TECH_SOURCE),
                    '<pre class="diagram-source">graph TB\n  Electron --> Renderer\n  Renderer --> Main\n</pre>',
                ),
                encoding="utf-8",
            )
            errors = validator.validate_architecture_web(out)
            self.assertTrue(any("raw Mermaid graph source" in err or "技术框架图" in err for err in errors))

    def test_architecture_web_allows_collapsed_graph_source_with_svg(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "collapsed-graph-source-architecture-wiki"
            write_valid_architecture_web(out)
            self.assertEqual(validator.validate_architecture_web(out), [])

    def test_skill_rejects_required_feynman_recap_instruction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp) / "skill"
            shutil.copytree(ROOT, temp_root)
            skill = temp_root / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8")
                + "\n\nBad instruction: 每页必须包含费曼复述。\n",
                encoding="utf-8",
            )
            errors = validator.validate_skill(temp_root)
            self.assertTrue(any("费曼复述" in err for err in errors))

    def test_architecture_web_passes_target_system_diagram(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "target-system-architecture-wiki"
            write_valid_architecture_web(out)
            target_source = """graph TB
  User[用户] --> Renderer["Renderer UI / route"]
  Renderer --> Preload["preload / electronAPI"]
  Preload --> Main["ipcMain / Main process"]
  Main --> Services[Runtime services]
  Services --> Storage[Local storage]
  Services --> Cloud[Cloud integration]
"""
            target_graph = graph_block(target_source)
            (out / "index.html").write_text(
                OVERVIEW_HTML.replace(
                    graph_block(OVERVIEW_RUNTIME_SOURCE),
                    target_graph,
                ),
                encoding="utf-8",
            )
            self.assertEqual(validator.validate_architecture_web(out), [])

    def test_mermaid_guard_accepts_quoted_technology_graph(self) -> None:
        source = """graph TB
  Electron["Electron shell"] --> Renderer["React renderer"]
  Electron --> Preload["preload / electronAPI"]
  Preload --> IPC["ipcRenderer / ipcMain"]
  IPC --> Main["main process services"]
  Main --> OpenClaw["OpenClaw"]
  Main --> Hermes["Hermes"]
  Main --> Lucyna["Lucyna"]
  Main --> DesktopPet["Desktop Pet"]
  Main --> CloudGateway["CloudGateway / stores"]
  Renderer --> Router["HashRouter / contexts"]
  Renderer --> Tests["low-level / E2E / visual checks"]"""
        errors: list[str] = []
        validator.validate_mermaid_safe_syntax(source, Path("snippet.mmd"), errors)
        self.assertEqual(errors, [])

    def test_mermaid_guard_rejects_unquoted_special_labels(self) -> None:
        source = """graph TB
  Electron[Electron shell] --> Preload[preload / electronAPI]
  Preload --> IPC[ipcRenderer / ipcMain]
  IPC --> Main[main process services]"""
        errors: list[str] = []
        validator.validate_mermaid_safe_syntax(source, Path("bad-snippet.mmd"), errors)
        self.assertTrue(any("wrap the label in double quotes" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
