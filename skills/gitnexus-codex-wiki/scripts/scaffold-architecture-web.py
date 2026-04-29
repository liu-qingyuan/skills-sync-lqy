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
import json
import shutil
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


EXECUTION_BOUNDARY = (
    "GitNexus supplies graph/index evidence; Codex authors architecture-web "
    "pages directly. Native gitnexus wiki provider/API-key setup is separate."
)

DEFAULT_PROJECT_EXPLAINER_MERMAID = (
    Path.home() / ".codex" / "skills" / "project-explainer-web" / "assets" / "vendor" / "mermaid.min.js"
)


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
table { width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 14px; }
th, td { border-bottom: 1px solid var(--line); padding: 10px; text-align: left; vertical-align: top; }
th { color: #314267; background: rgba(49, 94, 251, 0.07); }
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


def module_title(name: str) -> str:
    return " ".join(part.capitalize() for part in slug(name).split("-")) or "Core"


def mermaid_block(title: str, body: str, mermaid_script: bool) -> str:
    if mermaid_script:
        visual = f"""<div class=\"mermaid\">\n{body}\n</div>"""
    else:
        visual = f"""<pre class=\"mermaid-source\">{body}</pre>"""
    return f"""<section class=\"diagram-card\">\n<h3>{title}</h3>\n{visual}\n<p class=\"fallback\">非视觉 fallback：按上到下读取节点，父节点表示系统边界，子节点表示职责或调用方向。</p>\n</section>"""


def html_head(title: str, mermaid_ref: str | None) -> str:
    script = f'\n<script defer src="{mermaid_ref}"></script>\n<script>window.addEventListener("DOMContentLoaded",()=>{{if(window.mermaid){{window.mermaid.initialize({{startOnLoad:true,securityLevel:"loose"}});}}}});</script>' if mermaid_ref else ""
    return f"""<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n<meta charset=\"UTF-8\" />\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n<title>{title}</title>\n<style>\n{STYLE}\n</style>{script}\n</head>\n<body>\n<div class=\"shell\">\n"""


def module_links(modules: list[str]) -> str:
    return "\n".join(
        f'<a class="card" href="modules/{slug(name)}.html"><strong>{module_title(name)}</strong><p>点击进入模块页：职责、数据流、证据、验证命令。</p></a>'
        for name in modules
    )


def overview_html(slug_value: str, modules: list[str], evidence_entries: list[dict[str, str]], mermaid_script: bool) -> str:
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
    script_ref = "./assets/mermaid.min.js" if mermaid_script else None
    return html_head(f"{slug_value} 应用架构说明", script_ref) + f"""
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
<section class=\"panel span-6\"><h2>原理与背景知识</h2><p>TODO: 解释目标项目框架、运行时边界、GitNexus graph 与 Mermaid graph TB 如何帮助理解源码。</p></section>
<section class=\"panel span-6\"><h2>约束与风险</h2><p>TODO: 记录 stale index、dirty worktree、未验证推断等风险。</p></section>
<section class=\"panel span-6\"><h2>推荐维护方案</h2><p>TODO: 给出下一步维护目标系统架构说明的建议。</p></section>
<section class=\"panel span-12\"><h2>后续维护动作</h2><ol><li>补齐真实源码入口和模块页。</li><li>补齐 route/service/API/IPC trace。</li><li>运行验证命令。</li></ol></section>
</main>
</div>
</body>
</html>
"""


def module_html(name: str, evidence_entries: list[dict[str, str]], mermaid_script: bool) -> str:
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
    script_ref = "../assets/mermaid.min.js" if mermaid_script else None
    return html_head(f"{title} 模块说明", script_ref) + f"""
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
<section class=\"panel span-12\"><h2>源码阅读入口</h2><ul><li>TODO: 写入 <code>{module_slug}</code> 的首读源码文件或符号。</li></ul></section>
<section class=\"panel span-12\"><h2>源码证据地图</h2><ul><li>源码证据 refs: {evidence_refs}</li><li>GitNexus graph commands: TODO: 填入 repo-qualified <code>gitnexus context</code>/<code>gitnexus cypher</code>。</li></ul></section>
<section class=\"panel span-12\"><h2>优先阅读文件</h2><table><thead><tr><th>文件</th><th>为什么先读</th></tr></thead><tbody><tr><td>TODO: source file</td><td>TODO: product/runtime purpose</td></tr></tbody></table></section>
<section class=\"panel span-12\"><h2>技术框架图</h2><pre class=\"tree\">{tech_tree}</pre></section>
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

    mermaid_script = False
    source = resolve_mermaid_source(args.mermaid_js, args.no_default_mermaid_js)
    if source:
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
        "entrypoint": "index.html",
        "modules": modules,
        "evidence_files": evidence_entries,
    }

    write(out / "index.html", overview_html(project_slug, modules, evidence_entries, mermaid_script), args.force)
    for module in modules:
        write(modules_dir / f"{module}.html", module_html(module, evidence_entries, mermaid_script), args.force)
    write(evidence_dir / "module-map.json", json.dumps({"modules": module_entries}, indent=2, ensure_ascii=False) + "\n", args.force)
    write(evidence_dir / "route-service-trace.json", json.dumps(route_trace, indent=2, ensure_ascii=False) + "\n", args.force)
    write(out / "wiki-meta.json", json.dumps(meta, indent=2, ensure_ascii=False) + "\n", args.force)

    print(f"Wrote architecture-web scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
