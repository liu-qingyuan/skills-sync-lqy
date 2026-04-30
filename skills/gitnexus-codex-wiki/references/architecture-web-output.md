# Architecture-web output reference

This reference defines the `architecture-web` mode for `gitnexus-codex-wiki`. It is a Codex-authored static website flow: GitNexus supplies graph/index evidence, and Codex writes the pages directly. It is not native `gitnexus wiki`, not GitNexus provider configuration, and not a Codex-subscription-as-API-key flow.

## Design contract: project-explainer-web style

Architecture-web pages must follow the same reader experience as `$project-explainer-web`:

- Default language is Chinese (`zh-CN`) unless the user explicitly requests English.
- The root has **exactly one** main HTML page: `index.html`.
- `index.html` is the click-through hub. It links to every `modules/<slug>.html` page listed in `evidence/module-map.json`.
- Module/detail pages live under `modules/` and link back to `../index.html`. They must not become separate root landing pages.
- Styling should use the project-explainer-web visual grammar: soft gradient background, `.shell`, `.hero`, `.panel`, cards, tags, tree blocks, readable tables, and short scannable sections.
- Mermaid is offline-safe: use local `assets/mermaid.min.js` or hand-authored inline SVG for rendered diagrams. CDN Mermaid is invalid.
- Dense diagrams should use `interactive-flow`: a local React Flow canvas with zoom/pan/drag, typed nodes/edges, visible direction markers, click-to-evidence, and a nearby text/table fallback. For full-coverage deliveries, React Flow is the required primary renderer across `index.html` and module pages; simple Mermaid/SVG may remain only as collapsed audit/source or explicit non-primary evidence/provenance.
- Interactive-flow is offline and no CDN: use local `assets/architecture-flow.js/css` or equivalent, embed the graph payload page-locally, and include bundle provenance with package versions, license notes, build command, generated asset paths, and hashes.
- Final pages must not show raw `graph TB` / `flowchart` text as the visible diagram. Keep graph source only in collapsed `<details class="source-note">` after the rendered diagram when auditability is needed.

## Semantic contract: explain the target system, not the artifact

The architecture-web artifact is a container. Its subject is the target application/system. In final output:

- `index.html` is a navigation hub, not an architecture component.
- `modules/*.html`, `evidence/*.json`, `_learn_web`, `wiki-meta.json`, Mermaid rendering, and the Codex/GitNexus generation workflow are supporting artifact details only.
- Main headings, diagrams, module cards, and flow explanations must center target-system entities found in source: UI/renderer entrypoints, route handlers, preload/API or IPC bridges, main/runtime processes, services, storage, cloud/local integrations, tests, and domain modules.
- Artifact details may be listed in evidence/metadata sections or footer notes, but must never be the central diagram or primary module taxonomy.

Invalid artifact-centric overview diagram:

```mermaid
graph TB
  Reader[初学者读者] --> Index[index.html 主入口]
  Index --> Modules["modules/*.html 模块页"]
  Index --> 源码证据["evidence/*.json"]
  源码证据 --> Meta[wiki-meta.json]
```

Valid target-system-centric overview diagram:

```mermaid
graph TB
  User[用户] --> Renderer["Renderer UI / routes"]
  Renderer --> Preload["preload / exposed API"]
  Preload --> Main["ipcMain / Main process"]
  Main --> Services[Runtime services]
  Services --> Storage["Local storage / files"]
  Services --> Cloud[Cloud or external integrations]
```

## Directory tree

Default output when `--out` is omitted:

```text
_learn_web/<slug>-architecture-wiki/
├─ index.html                     # the only root/main HTML page
├─ modules/
│  └─ <module>.html               # linked from index.html
├─ assets/
│  ├─ mermaid.min.js              # local/offline Mermaid when available
│  ├─ architecture-flow.js         # local/offline React Flow bundle when interactive-flow is used
│  ├─ architecture-flow.css
│  └─ architecture-flow-provenance.json
├─ evidence/
│  ├─ module-map.json
│  ├─ route-service-trace.json
│  └─ interactive-flow.json        # optional audit copy; runtime uses embedded/page-local payload
└─ wiki-meta.json
```

## Scaffold CLI examples

```bash
python3 ~/.codex/skills/gitnexus-codex-wiki/scripts/scaffold-architecture-web.py \
  --repo . \
  --slug lucyna \
  --module frontend-routes \
  --module ipc-services \
  --evidence docs/gitnexus-codex-wiki/evidence/preflight.md
```

The scaffold defaults to Chinese and auto-copies project-explainer-web's bundled Mermaid runtime when available. Use `--no-default-mermaid-js` only during scaffolding or when you will replace static source with inline SVG before final delivery.


## Function-depth architecture output

Function-depth output is the deep version of `architecture-web`: overview pages stay readable, module pages carry concrete function trace graphs, and exhaustive function detail appears in searchable inventories. Enable it when `wiki-meta.json` contains:

```json
{
  "functionDepth": {
    "enabled": true,
    "coverageScope": "in-scope-architecture-functions",
    "mapPath": "evidence/function-architecture-map.json",
    "validatorMode": "function-depth"
  }
}
```

Required page behavior:

- `index.html` includes a visible “函数视图入口” or equivalent section that sends readers to module-level traces and inventories instead of promising one giant all-function graph.
- Every module page includes at least one React Flow function trace graph and one searchable/filterable function inventory table.
- Trace graph nodes use concrete functions/components/hooks/services/IPC handlers/test helpers from source evidence; generic-only graphs are invalid.
- Edge labels use `calls`, `invokes IPC`, `returns`, `updates state`, `fallback`, `error`, or `test covers` where applicable.
- Inventory rows include symbol, kind, file + line, responsibility, callers/callees when known, trace membership, tests, evidence source, and index freshness.
- Branch/fallback/error paths appear in traces where source evidence exists.
- Large inventories render only 25-100 rows by default and use search/filter plus pagination, virtualization, or chunking when needed.

Canonical evidence artifact:

```text
evidence/function-architecture-map.json
```

The map records repo/head/index freshness, module source roots, function-like symbols, exclusions, traces, and trace edges. Complete coverage claims apply only to `in-scope-architecture-functions` unless the map explicitly covers all repo function-like symbols.

Validation and QA evidence must prove:

- every in-scope architecture function appears exactly once in one module inventory or appears in exclusions with a valid reason;
- every function trace node references a valid inventory `symbolId` or documented boundary node;
- every trace edge references valid nodes and has a semantic kind;
- every inventory symbol links to file/line evidence and source freshness;
- search/filter works from `file://`;
- visual QA records React Flow readability/click traces plus inventory row counts, load timings, search timings, and pagination/virtualization status.

## Required page contracts

Overview headings in `index.html`:

- `总览摘要`
- `为什么要先理解它`
- `真实源码目录树`
- `整体运行时结构图`
- `用户动作到运行时流程`
- `源码证据地图`
- `优先阅读文件`
- `技术框架图`
- `边界与不变量`
- `安全修改方式`
- `验证命令`
- `常见反模式`
- `原理与背景知识`
- `约束与风险`
- `推荐维护方案`
- `后续维护动作`

Every `modules/<module>.html` page must include:

- `模块职责`
- `为什么存在`
- `真实源码目录树`
- `整体运行时结构图`
- `数据如何流动`
- `用户动作到运行时流程`
- `源码阅读入口`
- `源码证据地图`
- `优先阅读文件`
- `技术框架图`
- `边界与不变量`
- `安全修改方式`
- `源码证据`
- `验证命令`
- `常见反模式`
- `原理与背景知识`
- `约束与风险`
- `推荐维护方案`
- `后续维护动作`

The writing style should be Feynman-style: explain a small piece plainly, name the source or graph evidence behind it, then show how a beginner can verify it. Treat this as a prose principle only; do not generate a repeated fixed section named `费曼复述`.

Deep architecture pages must show real source relationships and branches:

- `index.html` visibly includes a real source directory tree, a technology/framework tree, a runtime boundary graph, a route/service/IPC or equivalent flow graph, and a branch overview graph.
- Module pages include files plus key symbols/handlers/API/IPC/service entrypoints, a relationship graph, and a branch/failure/fallback table or graph with at least three source-grounded paths.
- Electron pages show renderer/preload/main trust boundaries and multiple IPC/service branches.
- Chat/runtime pages show provider/runtime branches, local/cloud or model-sync branches, and stream event branches when present.
- Auth/session pages show login, refresh, logout, invalid-auth, and credential/provider branches when present.
- Hidden generic contract text must never be used to satisfy validation; required concepts must be visible or stored in structured evidence JSON.

## Required JSON schemas

`wiki-meta.json` requires the base fields and should include the UI contract fields:

```json
{
  "generated_at": "2026-04-28T00:00:00Z",
  "repo": "/path/to/repo",
  "git_commit": "<commit-or-unavailable>",
  "gitnexus_version": "gitnexus 1.6.3",
  "execution_boundary": "GitNexus supplies graph/index evidence; Codex authors architecture-web pages directly. Native gitnexus wiki provider/API-key setup is separate.",
  "mode": "architecture-web",
  "language": "zh-CN",
  "visual_style": "project-explainer-web",
  "entrypoint": "index.html",
  "modules": ["core"],
  "evidence_files": [{"source": "/path/preflight.md", "path": "evidence/preflight.md"}],
  "functionDepth": {
    "enabled": false,
    "coverageScope": "overview|in-scope-architecture-functions|all-repo-function-like-symbols",
    "mapPath": "evidence/function-architecture-map.json",
    "validatorMode": "standard|function-depth"
  }
}
```

`evidence/module-map.json` requires `modules[]` objects with `slug`, `title`, `source_files`, `graph_commands`, `evidence_refs`, and `verification_commands`.

`evidence/route-service-trace.json` requires `flows[]` objects with `slug`, `title`, `entrypoints`, `services`, `graph_edges`, and `evidence_refs`.


## Interactive-flow React Flow policy

Use `interactive-flow` for dense architecture maps where zoom, pan, drag, and click-to-evidence make the target system easier to inspect than a Mermaid/SVG diagram. In full-coverage architecture-web output, React Flow is the primary diagram surface: the homepage contains multiple primary graphs for overview/runtime/action/branch coverage, and every module page contains at least one primary graph. Keep Mermaid/SVG only for simple non-primary branch/tree material or collapsed audit/source details.

Runtime contract:

- The page contains one or more React Flow containers, for example `<div class="architecture-flow" data-flow-graph="runtime-overview"></div>` plus a side panel/drawer for evidence. Every `data-flow-graph` value must match a `graphs[].id` entry in the page-local payload.
- The runtime graph payload is embedded in the HTML through `<script type="application/json" data-architecture-flow>...</script>` or a JS-assigned payload. `evidence/interactive-flow.json` may be written for audit, but `file://` rendering must not require `fetch()` from evidence JSON.
- Visible primary Mermaid `graph TB` / `flowchart` text and visible static SVG diagram blocks are invalid in full-coverage React Flow output. Retain source only inside collapsed `<details>` audit/source blocks or explicit non-primary evidence/provenance areas.
- Runtime-bearing URLs are local only. Reject `http://`, `https://`, protocol-relative CDN URLs, `unpkg`, and `jsdelivr` in script/link/img attributes and CSS `url()` used by the delivered renderer.
- `assets/architecture-flow-provenance.json` records source packages and versions (`react`, `react-dom`, `@xyflow/react`, and layout package such as `@dagrejs/dagre`), build command, source/template path, license notes, generated asset paths, and hashes for `architecture-flow.js/css`.
- Visual QA must open exact `file://` URLs, capture screenshots, confirm no obvious overlap in default viewport, confirm edge direction/semantics, and record at least one node click and one edge click that opens evidence.

Graph payload schema:

```json
{
  "version": 1,
  "graphs": [
    {
      "id": "runtime-overview",
      "title": "整体运行时结构",
      "nodes": [
        {
          "id": "renderer",
          "type": "runtime",
          "label": "React renderer",
          "position": {"x": 0, "y": 0},
          "width": 220,
          "height": 92,
          "evidence": ["src/renderer/App.tsx"]
        }
      ],
      "edges": [
        {
          "id": "renderer-preload",
          "source": "renderer",
          "target": "preload",
          "sourceHandle": "right",
          "targetHandle": "left",
          "type": "ipc",
          "label": "electronAPI call",
          "evidence": ["src/preload/index.ts"]
        }
      ],
      "layout": {
        "engine": "dagre",
        "direction": "LR",
        "nodeWidth": 220,
        "nodeHeight": 92,
        "ranksep": 96,
        "nodesep": 64,
        "computedAtBuildTime": true
      }
    }
  ]
}
```

Payload rules:

- Nodes and edges explain the target application/system, not the generated documentation artifact. Do not center `_learn_web`, `index.html`, `modules/*.html`, `wiki-meta.json`, evidence JSON, or the generation workflow.
- Every clickable node/edge has evidence (`evidence`) or an explicit `evidenceNote`/fallback rationale.
- Edges have a semantic `type` and visible `label`. First-pass edge taxonomy includes `call`, `ipc`, `data`, `error`, `external`, and `test`; each type must have distinct styling such as color, stroke pattern, marker, or badge.
- Store deterministic `position`, expected `width`/`height`, and layout metadata. Dense or crossing-prone edges carry `sourceHandle` and `targetHandle`; if omitted, the validator/reference must define the fixed-handle convention.
- Provide a non-visual fallback table, legend, tree, or prose explanation near the canvas.

## Mermaid policy

Use Mermaid `graph TB` source for diagram audit trails, but final HTML pages need a rendered visual form: local Mermaid-rendered `<div class="mermaid">...</div>` or hand-authored inline SVG. If source is included, put it inside collapsed `<details>` after the rendered diagram, not as a visible raw `<pre>` block.

At least one relevant graph on the homepage and each deep module page should branch (one node has multiple outgoing or incoming edges). A single straight line such as `User -> Renderer -> Preload -> Main -> Runtime` is not enough for final architecture-web output.

Mermaid-safe syntax rules:

- Quote labels with punctuation or separators: `Preload["preload / electronAPI"]`, not `Preload[preload / electronAPI]`.
- Avoid lowercase `end` as a node id or unquoted label; use `End` or `EndNode["end"]`.
- Add whitespace after arrows when a destination node id starts with lowercase `o` or `x`; otherwise Mermaid can interpret the link as a circle/cross edge.
- Final pages must not contain visible `parse error`, `syntax error in text`, or diagram-validation failure text.
- Final pages must not leave `graph TB` / `flowchart` source visibly exposed as body text; browser visual QA should fail if raw graph source is visible.
- Use the skill validator as a static preflight, then run browser visual QA for rendered diagrams.

Invalid Mermaid reference:

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
```

Valid local rendered Mermaid reference:

```html
<script defer src="./assets/mermaid.min.js"></script>
```

Valid source audit trail after a rendered diagram:

```html
<div class="diagram"><svg role="img" aria-label="runtime flow">...</svg></div>
<details class="source-note">
  <summary>图源</summary>
  <pre class="diagram-source">graph TB
    Route["UI route"] --> Service["runtime service"]
  </pre>
</details>
```

## Strict vs scaffold validation

Scaffolds are allowed to contain `TODO` placeholders until Codex replaces them with evidence-grounded content. Final outputs are not.

```bash
python3 ~/.codex/skills/gitnexus-codex-wiki/scripts/validate-skill.py \
  ~/.codex/skills/gitnexus-codex-wiki \
  --architecture-web-dir _learn_web/lucyna-architecture-wiki
```
