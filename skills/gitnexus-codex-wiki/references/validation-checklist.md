# Validation checklist for `gitnexus-codex-wiki`

Use this checklist before marking the skill or generated wiki docs complete.

## Skill package review

- [ ] `SKILL.md` states that Codex reads GitNexus graph/index context and writes markdown/webpages itself.
- [ ] `SKILL.md` documents `markdown-wiki`, `architecture-web`, and `hybrid` modes without changing the provider boundary.
- [ ] Prerequisites include GitNexus CLI availability and an existing or explicitly buildable index.
- [ ] Instructions target `gitnexus@1.6.3` behavior unless newer local evidence is recorded.
- [ ] Failure handling covers missing CLI, non-git directory, missing index, stale index, large repo slicing, and unavailable graph results.
- [ ] The skill references this internals file or equivalent local evidence.
- [ ] The architecture-web reference exists and documents directory tree, CLI examples, heading contracts, JSON schemas, Mermaid policy, strict/scaffold validation, and valid/invalid examples.

## Forbidden-claim review

The skill and docs must not imply any of the following:

- Equating a Codex subscription with an OpenAI-compatible API key.
- GitNexus calls Codex during the recommended v1 flow.
- Users must configure GitNexus provider settings for Codex-side document generation.
- `gitnexus wiki` can run without an existing GitNexus index.

Useful local scan:

```bash
skill_dir="${CODEX_HOME:-$HOME/.codex}/skills/gitnexus-codex-wiki"
rg -n "subscription.*API key|API key.*subscription|GitNexus calls Codex|configure GitNexus.*Codex|wiki.*without.*index" "$skill_dir"
```

The command should return no unsupported positive claims. Review any negated guardrail matches manually.

Mermaid network scan for architecture-web outputs:

```bash
rg -n "https?://|cdn\\.jsdelivr|unpkg|esm\\.sh|mermaid.*cdn" _learn_web/*-architecture-wiki
```

The command should return no Mermaid CDN/script references. Review ordinary source links separately if a final page intentionally cites external documentation.

## Graph-grounding review

For each generated wiki output set, verify:

- [ ] An overview page exists.
- [ ] At least one parent/module page exists when the repo has multiple areas.
- [ ] At least one leaf/module page cites concrete source files or symbols.
- [ ] Pages mention graph evidence such as call edges, process flows, exports, or direct source paths.
- [ ] Claims are traceable to GitNexus output or direct source reads.
- [ ] Large repos are sliced; the skill does not ask Codex to ingest all graph artifacts blindly.

## Architecture-web review

For each generated architecture-web output set, verify:

- [ ] `wiki-meta.json` includes `generated_at`, `repo`, `git_commit`, `gitnexus_version`, `execution_boundary`, `mode`, `modules`, and `evidence_files`.
- [ ] `wiki-meta.json` uses `mode: "architecture-web"` and states that GitNexus supplied graph/index evidence while Codex authored pages directly.
- [ ] `evidence/module-map.json` includes `modules[]`, and each module has `slug`, `title`, `source_files`, `graph_commands`, `evidence_refs`, and `verification_commands`.
- [ ] `evidence/route-service-trace.json` includes `flows[]`, and each flow has `slug`, `title`, `entrypoints`, `services`, `graph_edges`, and `evidence_refs`.
- [ ] `index.html` includes the project-explainer-web headings: `总览摘要`, `为什么要先理解它`, `真实源码目录树`, `整体运行时结构图`, `用户动作到运行时流程`, `源码证据地图`, `优先阅读文件`, `技术框架图`, `边界与不变量`, `安全修改方式`, `验证命令`, `常见反模式`, `原理与背景知识`, `约束与风险`, `推荐维护方案`, and `后续维护动作`.
- [ ] Every module page includes the required headings: `模块职责`, `为什么存在`, `数据如何流动`, `源码阅读入口`, `源码证据`, and `验证命令`.
- [ ] Applicable diagrams cover system context, structure tree, runtime flow, module boundaries, route-service/IPC, and verification map.
- [ ] Each diagram has a rendered visual form (inline SVG or local Mermaid render block), collapsed Mermaid `graph TB` source for auditability when useful, a plain-language explanation, evidence references, and a non-visual fallback.
- [ ] Mermaid labels with `/`, `:`, parentheses, comma, `%`, `#`, `&`, `|`, `<`, or `>` are quoted; lowercase `end` is not used as an unquoted node id/label; compact `-->o*` / `-->x*` edge ambiguity is avoided.
- [ ] No final HTML page contains visible `parse error`, `syntax error in text`, or diagram validation failure text.
- [ ] No final HTML page visibly exposes raw `graph TB` / `flowchart` text as the diagram body; source is collapsed under `<details>` after a rendered diagram.
- [ ] Mermaid rendering uses only local `assets/mermaid.min.js`; there are no CDN or network script references.
- [ ] Scaffold validation is run with `--scaffold-ok` or `--allow-placeholders`; final validation is strict and has no TODO/placeholder evidence.
- [ ] Semantic QA confirms the primary visible narrative and diagrams explain the target repository/application, not the generated website artifact.
- [ ] Main diagrams and module cards include target-system entities, source entrypoints, runtime/service boundaries, and verification paths.
- [ ] The central architecture is not `_learn_web`, `architecture-web flow`, `index.html`, `modules/*.html`, `evidence/*.json`, `wiki-meta.json`, Mermaid rendering, or `Codex 生成网页流程`. Those may appear only as metadata/evidence/navigation details.

## Dry-run command transcript template

```bash
repo=/path/to/repo
cd "$repo"
command -v gitnexus
gitnexus --version
gitnexus status
# If indexed and a candidate symbol/file is known:
gitnexus context <symbol-or-file>
gitnexus impact <symbol-or-file>
```

Record stdout summaries in the generated docs' metadata or in a local validation note. Do not include secrets or API keys.

## Completion bar

A first release is complete when:

1. The skill has clear invocation examples and guardrails.
2. The docs explain the native wiki internals used as reference structure.
3. A local dry-run or checklist confirms index handling.
4. Forbidden-claim review is clean or any matches are explicitly negated guardrails.
5. Architecture-web scaffold validation and strict final validation are treated as separate bars.


## Project-explainer-web architecture-web checks

For `architecture-web` outputs, verify these before completion:

- Root contains exactly one main HTML page: `index.html`.
- `index.html` links to every `modules/<slug>.html` page in `evidence/module-map.json`.
- Every module page links back to `../index.html`.
- Pages default to Chinese (`lang=zh-CN`) unless the user explicitly requested English.
- Pages use the project-explainer-web visual grammar: `.shell`, `.hero`, `.panel`, cards, tree blocks, readable tables, soft gradient variables.
- Overview page contains the project-explainer-web section set: 总览摘要, 为什么要先理解它, 真实源码目录树, 整体运行时结构图, 用户动作到运行时流程, 源码证据地图, 优先阅读文件, 技术框架图, 边界与不变量, 安全修改方式, 验证命令, 常见反模式, 原理与背景知识, 约束与风险, 推荐维护方案, 后续维护动作.
- Module pages contain the module-specific teaching section set and retain 源码证据 + 验证命令.
- No CDN Mermaid or network script is referenced; local `assets/mermaid.min.js` or inline SVG renders diagrams, and raw graph source is collapsed rather than visible by default.
