---
name: gitnexus-codex-wiki
description: "Use GitNexus graph/index context so Codex can author graph-grounded wiki-style markdown or architecture-web pages without modifying GitNexus providers."
---

# GitNexus Codex Wiki

Use this skill when a user wants Codex to create or refresh wiki-style documentation from a repository's GitNexus graph/index context.

## Modes

Choose the lightest mode that satisfies the request:

1. **`markdown-wiki`** — the existing overview/modules/leaves markdown flow under `docs/gitnexus-codex-wiki/` or a user-selected docs directory. Use this for maintainers who want source-grounded markdown pages, backlinks, metadata, and graph evidence.
2. **`architecture-web`** — a project-explainer-web-style static architecture website under `_learn_web/<slug>-architecture-wiki/` by default. It has exactly one root main page, `index.html`, and optional `modules/*.html` detail pages that are reached by clicking links from `index.html`. Use this for Chinese-by-default, beginner-readable, Feynman-style architecture explanations with module pages, Mermaid `graph TB` diagrams or static Mermaid source blocks, evidence JSON, and verification guidance; Feynman is a writing principle, not a fixed `费曼复述` section.
3. **`hybrid`** — run `markdown-wiki` and `architecture-web` sequentially from the same evidence set. The first pass is not a new engine: scaffold markdown with `scripts/scaffold-wiki.py`, scaffold the static site with `scripts/scaffold-architecture-web.py`, then let Codex author both outputs from the same graph/source evidence.

## Boundary

- GitNexus supplies indexed code-graph evidence; Codex reads that evidence and writes the documentation.
- Codex authors docs/webpages directly; GitNexus never calls Codex in the recommended v1 flow.
- Do not describe a GitNexus-side Codex provider, and do not configure GitNexus to call Codex.
- `agents/openai.yaml` is a Codex skill/agent descriptor, not GitNexus provider configuration and not configured as a GitNexus provider.
- A Codex subscription is not an API key. If native `gitnexus wiki` provider setup comes up, keep that separate from this skill's Codex-authored flow.
- Target behavior is grounded in `gitnexus@1.6.3`. Re-check the local CLI before relying on version-specific behavior.

## Semantic guardrail for `architecture-web`

The subject of every `architecture-web` page is always the **target repository / target application / target system being analyzed**. The generated website artifact is only the teaching container. Do not let `_learn_web`, `index.html`, `modules/*.html`, `evidence/*.json`, `wiki-meta.json`, Mermaid rendering, or the Codex/GitNexus authoring process become the central architecture being explained.

Required framing:

- Main diagrams must put target-system entities at the center, such as users, UI/renderer surfaces, route or command entrypoints, preload/API bridges, main/runtime processes, services, persistence, cloud/local integrations, test boundaries, and named domain modules found in source.
- `index.html` is only the navigation entrypoint for the artifact; it is not a product architecture node.
- Module pages explain a product/runtime module's responsibility, source entry files, data flow, IPC/API/service boundaries, and verification path.
- Artifact metadata may appear only in footer, hidden metadata, evidence tables, or validation notes; it must not be the main narrative, central diagram, or module taxonomy.
- A final page whose primary visible text or diagrams center on `_learn_web`, `architecture-web flow`, `index.html`, `modules/*.html`, `wiki-meta.json`, `evidence/*.json`, or `Codex 生成网页流程` is invalid even if it passes structural checks.
- Never generate a repeated fixed section named `费曼复述`. Explain plainly in context instead: name the source evidence, state the simple mental model, then show the verification path.
- Do not satisfy validation with 隐藏通用契约文本. Required concepts must be visible in the page or present in structured evidence JSON.
- Deep architecture pages must include real branches, not only a straight `User -> Renderer -> Preload -> Main -> Runtime` line. For Electron apps, show renderer/preload/main security boundaries and multiple IPC/service branches; for runtime/chat/auth/Lucyna/desktop-pet pages, show success, failure, abort, refresh, readiness, fallback, or provider branches when those paths exist in source.

## Prerequisites

1. Local repository access.
2. GitNexus CLI available (`gitnexus --version` should report `1.6.3` for the validated first version).
3. A fresh, existing GitNexus index for the target repository, or clear authority to create one with `gitnexus analyze`.
4. A writable documentation output directory such as `docs/gitnexus-codex-wiki/`, `_learn_web/<slug>-architecture-wiki/`, or a user-specified equivalent.

## Default output structures

### `markdown-wiki`

When the user does not specify a destination, write generated markdown docs under repository-local `docs/gitnexus-codex-wiki/`:

```text
docs/gitnexus-codex-wiki/
├─ overview.md
├─ modules/
│  ├─ <module-slug>.md
│  └─ <parent-slug>.md
├─ evidence/
│  ├─ preflight.md
│  ├─ graph-queries.md
│  └─ source-citations.md
└─ wiki-meta.json
```

`wiki-meta.json` should include generation time, repo root, git commit, GitNexus version, module tree or module list, evidence files, and the execution boundary that GitNexus supplied context while Codex authored markdown directly. Do not write secrets or provider API keys into metadata.

### `architecture-web`

When the user does not specify a destination, write the static website under repository-local `_learn_web/<slug>-architecture-wiki/`:

```text
_learn_web/<slug>-architecture-wiki/
├─ index.html                     # the only root/main HTML page and the click-through hub
├─ modules/
│  └─ <module>.html               # linked from index.html; no orphan module pages
├─ assets/
│  └─ mermaid.min.js              # local/offline Mermaid, auto-copied when available
├─ evidence/
│  ├─ module-map.json
│  └─ route-service-trace.json
└─ wiki-meta.json
```

`wiki-meta.json` must include `generated_at`, `repo`, `git_commit`, `gitnexus_version`, `execution_boundary`, `mode`, `modules`, and `evidence_files`. The metadata must preserve the provider boundary: GitNexus supplies graph/index evidence and Codex authors architecture-web pages directly.

## Workflow

### 1. Preflight the repo and index

Start from an existing GitNexus index whenever possible; native `gitnexus wiki` fails before LLM setup when index metadata is missing. Run the bundled preflight script when possible, then inspect the output:

```bash
~/.codex/skills/gitnexus-codex-wiki/scripts/preflight.sh --repo . --out docs/gitnexus-codex-wiki/evidence/preflight.md
```

At minimum, capture these read-only checks:

```bash
gitnexus --version
gitnexus status
gitnexus list
```

If `gitnexus status` reports a missing index, stop the wiki flow and build the index before collecting context:

```bash
gitnexus analyze <repo-path>
```

If the index is stale or the repo is very large, explain the stale/large-context risk and slice the work by modules or high-value flows instead of loading every artifact at once.

### 2. Gather GitNexus graph context for Codex

Prefer narrow, reproducible evidence. Useful commands include:

```bash
gitnexus list
gitnexus context <symbol-or-file>
gitnexus impact <symbol-or-file>
gitnexus cypher "MATCH (f:File) RETURN f.filePath AS filePath ORDER BY filePath LIMIT 200"
gitnexus cypher "MATCH (f:File)-[:CodeRelation {type: 'DEFINES'}]->(n) WHERE n.isExported = true RETURN f.filePath AS filePath, n.name AS name, labels(n)[0] AS type ORDER BY filePath LIMIT 200"
gitnexus cypher "MATCH (a)-[:CodeRelation {type: 'CALLS'}]->(b) WHERE a.filePath <> b.filePath RETURN DISTINCT a.filePath AS fromFile, a.name AS fromName, b.filePath AS toFile, b.name AS toName LIMIT 200"
gitnexus cypher "MATCH (p:Process) RETURN p.id AS id, p.heuristicLabel AS label, p.processType AS type, p.stepCount AS stepCount ORDER BY stepCount DESC LIMIT 20"
```

Capture enough context to support the documentation structure:

- files and symbols in each module;
- call edges and cross-module edges;
- exported/public entry points where available;
- execution processes/flows;
- module grouping and ownership hints;
- source file references for any claim that will appear in the wiki.

Treat GitNexus native `wiki` internals as a reference model for page shape, not as this skill's execution engine. Only run native `gitnexus wiki` if the user explicitly asks for GitNexus-managed wiki generation and separately provides compatible provider configuration.

### 3. Author `markdown-wiki` layers with Codex

Create markdown pages that preserve the useful GitNexus `WikiGenerator` structure:

- `overview.md` — project overview, major modules, key flows, and an optional high-level Mermaid diagram.
- module/parent pages — how submodules fit together, cross-module calls, and shared flows.
- leaf pages — source-grounded docs for a focused file/module with incoming calls, outgoing calls, internal calls, and relevant processes.
- metadata/backlinks — generation date, GitNexus version, index status, source files, graph commands used, and links between related pages. Prefer a `wiki-meta.json` or equivalent note for the overall run.
- module grouping — document how files were grouped into modules and cite the graph/source evidence behind that grouping.

Write concise docs for maintainers, not raw graph dumps. Cite graph/source evidence inline where practical, for example `Source: src/foo.ts; graph: gitnexus context FooService`.

### 4. Author `architecture-web` pages with Codex

Use `scripts/scaffold-architecture-web.py` to create deterministic offline-first scaffolding, then replace every scaffold placeholder with evidence-grounded content. The final website must be beginner-readable and mechanically validateable.

Architecture-web must visually and structurally follow `$project-explainer-web`:

- **Chinese by default**: page prose and HTML language default to `zh-CN` unless the user explicitly requests English.
- **One root main page**: root must contain one main HTML page, `index.html`; all other topic/detail pages live under `modules/` or evidence files.
- **Click-through navigation**: every module listed in `evidence/module-map.json` must have a linked card or table link from `index.html` to `modules/<slug>.html`; every module page must link back to `../index.html`.
- **Same visual grammar as project-explainer-web**: use the soft gradient background, `.shell`, `.hero`, `.panel`, cards, tags, tree blocks, and readable knowledge-page layout rather than plain documentation styling.
- **Offline-safe Mermaid**: prefer local `assets/mermaid.min.js` copied from project-explainer-web when available, or hand-authored inline SVG when Mermaid runtime is unavailable; never use CDN scripts.
- **No visible raw graph dumps**: final architecture pages must not expose `graph TB` / `flowchart` source as the visible diagram body. If keeping source for auditability, put it in collapsed `<details class="source-note"><summary>图源</summary><pre class="diagram-source">...</pre></details>` after a rendered SVG or local Mermaid render block. This avoids the common failure where users see Mermaid text instead of a diagram.
- **Mermaid-safe syntax**: quote every node label containing `/`, `:`, parentheses, comma, `%`, `#`, `&`, `|`, `<`, or `>`; avoid lowercase node id/label `end`; keep a space after arrows when the destination id starts with lowercase `o` or `x`; and never ship pages with visible `parse error` / `syntax error` text. This follows Mermaid's official flowchart guidance on special characters and parser pitfalls.

Required overview headings in `index.html` mirror project-explainer-web:

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

Required headings for every `modules/<module>.html` page include both module-specific and project-explainer-web teaching sections:

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

Architecture-web diagrams should include these categories where applicable:

- system-context graph;
- structure-tree graph;
- runtime-flow graph;
- module-boundary graph per module;
- route-service-ipc graph when frontend routes exist;
- branch/fallback graph for auth, chat/runtime, readiness, desktop windows, or other conditional flows;
- verification-map graph.

Each diagram needs a rendered visual form (inline SVG or local Mermaid render block), Mermaid `graph TB` source kept behind collapsed details for auditability, a plain-language/Feynman-style explanation, source/GitNexus evidence references, and a non-visual fallback such as a table, tree, or prose explanation. Do not create a heading named `费曼复述`. Do not reference Mermaid from a CDN; if rendered Mermaid is needed, pass a local `--mermaid-js` file so the scaffold copies `assets/mermaid.min.js`. Before delivery, run the validator and visual QA so Mermaid syntax errors and visible raw `graph TB` blocks are caught by both static checks and browser-level rendering checks.

Deep architecture quality gates:

- `index.html` must visibly include a real source directory tree, technology/framework tree, runtime boundary graph, route/service/IPC or equivalent flow graph, and branch overview graph.
- Module pages must include a source relationship table with files plus key symbols/handlers/API/IPC/service entrypoints, a module relationship graph, and at least one branch/failure/fallback graph or table with 3+ source-grounded paths.
- Hidden content must not be used to satisfy visible headings, graph terms, or source relationship requirements.

`evidence/module-map.json` must contain `modules[]`; each module object must include `slug`, `title`, `source_files`, `graph_commands`, `evidence_refs`, and `verification_commands`. `evidence/route-service-trace.json` must contain `flows[]`; each flow object must include `slug`, `title`, `entrypoints`, `services`, `graph_edges`, and `evidence_refs`.

### 5. Validate the result

Run the packaged validator against the skill itself:

```bash
python3 /Users/amis/.codex/skills/gitnexus-codex-wiki/scripts/validate-skill.py /Users/amis/.codex/skills/gitnexus-codex-wiki
```

To scaffold a minimal markdown output structure from collected evidence, use:

```bash
python3 /Users/amis/.codex/skills/gitnexus-codex-wiki/scripts/scaffold-wiki.py \
  --repo . \
  --out docs/wiki \
  --evidence docs/wiki/evidence/preflight.md \
  --module core \
  --leaf entrypoints
```

To scaffold a static architecture-web output structure, use:

```bash
python3 /Users/amis/.codex/skills/gitnexus-codex-wiki/scripts/scaffold-architecture-web.py \
  --repo . \
  --slug my-project \
  --module routing \
  --module services \
  --evidence docs/wiki/evidence/preflight.md
```

The scaffold defaults to Chinese and, when available, auto-copies project-explainer-web's bundled Mermaid runtime to `assets/mermaid.min.js`. Use `--no-default-mermaid-js` only when you intentionally want static Mermaid source blocks without rendered diagrams.

For generated markdown docs, add `--docs-dir`:

```bash
python3 /Users/amis/.codex/skills/gitnexus-codex-wiki/scripts/validate-skill.py \
  /Users/amis/.codex/skills/gitnexus-codex-wiki \
  --docs-dir docs/wiki
```

For generated architecture-web pages, strict final validation is the default:

```bash
python3 /Users/amis/.codex/skills/gitnexus-codex-wiki/scripts/validate-skill.py \
  /Users/amis/.codex/skills/gitnexus-codex-wiki \
  --architecture-web-dir _learn_web/my-project-architecture-wiki
```

Scaffold smoke validation may allow placeholders before final authoring:

```bash
python3 /Users/amis/.codex/skills/gitnexus-codex-wiki/scripts/validate-skill.py \
  /Users/amis/.codex/skills/gitnexus-codex-wiki \
  --architecture-web-dir _learn_web/my-project-architecture-wiki \
  --allow-placeholders
```

Manual validation checklist:

- overview, parent/module, and leaf pages exist for `markdown-wiki`;
- architecture-web root has exactly one `index.html` main page; module pages are linked from `index.html` and link back to it;
- architecture-web overview and module pages include required project-explainer-web headings;
- architecture-web pages default to Chinese (`lang=zh-CN`) and use project-explainer-web-style `.shell`, `.hero`, `.panel` layout;
- no repeated fixed `费曼复述` sections appear in final pages;
- deep architecture graphs contain meaningful branches, not only straight-line happy paths;
- no 隐藏通用契约文本 is used to satisfy strict validation;
- every important claim traces to source or GitNexus graph evidence;
- no text implies a GitNexus Codex provider, a Codex API key from a subscription, or GitNexus calling Codex;
- no architecture-web page references CDN or network Mermaid scripts;
- no final architecture-web page leaves raw `graph TB` / `flowchart` source visibly exposed as the diagram; source belongs in collapsed `<details>` after a rendered SVG/local Mermaid block;
- context slicing is documented for large repos;
- missing/stale index behavior is handled before documentation generation.

## Invocation examples

- "Use `gitnexus-codex-wiki` to generate wiki docs from this repo's GitNexus graph."
- "Refresh `docs/wiki` using GitNexus context and keep the docs graph-grounded."
- "Create an `architecture-web` wiki under `_learn_web/app-architecture-wiki` with module pages for routes and services."
- "Run the `hybrid` flow: markdown wiki plus architecture-web pages from the same GitNexus evidence."
- "Validate that my Codex-authored wiki pages are backed by GitNexus evidence."

## Failure modes

- **Missing GitNexus CLI:** install or expose `gitnexus`; do not invent graph evidence.
- **Missing index:** run `gitnexus analyze` before wiki authoring.
- **Stale index:** refresh or scope the generated docs to confirmed-current files.
- **Huge graph:** slice by modules/flows and generate pages incrementally.
- **Provider confusion:** clarify that this skill does not add or rely on GitNexus provider support for Codex.
- **Architecture-web placeholders:** final validation fails unresolved `TODO`/placeholder text; use `--allow-placeholders` only for scaffold smoke checks.
- **Network Mermaid:** architecture-web output must be offline-first; copy local Mermaid with `--mermaid-js` or keep Mermaid as readable static source blocks.

## References

Load only when needed:

- `references/gitnexus-wiki-internals.md` — verified GitNexus wiki internals and review risks.
- `references/validation-checklist.md` — package and generated-doc validation checks.
- `references/architecture-web-output.md` — architecture-web directory tree, heading contracts, JSON schemas, Mermaid policy, and validation examples.
