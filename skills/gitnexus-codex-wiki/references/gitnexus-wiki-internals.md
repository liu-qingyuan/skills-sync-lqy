# GitNexus wiki internals reference for `gitnexus-codex-wiki`

This reference is the source-grounded contract for the Codex-side `gitnexus-codex-wiki` skill. It records locally verified `gitnexus@1.6.3` behavior and maps native GitNexus wiki concepts to a Codex-authored documentation workflow.

## Verified local behavior

Verification commands run locally on 2026-04-28:

```bash
gitnexus --version
gitnexus wiki --help
```

Observed facts:

- `gitnexus --version` reports `1.6.3`.
- The CLI registers `wiki [path]` as “Generate repository wiki from knowledge graph” and exposes provider options for `openai` or `cursor`, plus OpenAI-compatible/Azure flags such as `--base-url`, `--api-key`, `--api-version`, and `--model` (`/opt/homebrew/lib/node_modules/gitnexus/dist/cli/index.js:76-90`).
- There is no native Codex provider in the verified `wiki` command option surface. The `gitnexus-codex-wiki` skill must therefore keep control inverted: GitNexus provides graph/index evidence; Codex reads that evidence and authors markdown.
- Do not say or imply that a Codex subscription is an API key, that GitNexus includes a Codex provider, or that the recommended v1 flow configures GitNexus to call Codex.

## Native `gitnexus wiki` preflight and provider boundary

`wikiCommand` resolves the target repository before any LLM setup:

- With no path, it calls `getGitRoot(process.cwd())`; outside a git repo it prints “Not inside a git repository” and exits (`dist/cli/wiki.js:74-85`).
- With a path, it resolves that path and verifies it is a git repository; otherwise it prints “Not a git repository” and exits (`dist/cli/wiki.js:76-91`).
- It computes storage paths, loads existing index metadata, and stops when no index exists, printing “No GitNexus index found” and “Run `gitnexus analyze` first to index this repository” (`dist/cli/wiki.js:93-100`).

Only after those checks does it resolve provider/API configuration (`dist/cli/wiki.js:102-150`). Non-interactive native wiki generation requires either an API key for an OpenAI-compatible path or the Cursor provider; in the no-config non-interactive branch it asks for `OPENAI_API_KEY`, `GITNEXUS_API_KEY`, `--api-key`, or `--provider cursor` (`dist/cli/wiki.js:151-162`). The interactive setup text lists OpenAI, OpenRouter, Azure OpenAI, custom endpoint, and Cursor CLI when available (`dist/cli/wiki.js:165-179`).

Skill implications:

1. Always check the GitNexus index before graph-grounded wiki authoring.
2. If no index exists, run or request `gitnexus analyze <repo>` before claiming graph-grounded output.
3. Keep native `gitnexus wiki` provider setup separate from Codex skill execution. The Codex skill can inspect GitNexus graph artifacts and source files, but GitNexus is not the caller of Codex in the recommended v1 flow.

## Native `WikiGenerator` pipeline concepts to reuse

The installed generator describes the native pipeline as:

1. validate prerequisites and gather graph structure;
2. build a module tree;
3. generate module pages bottom-up;
4. generate the overview page (`dist/core/wiki/generator.js:1-10`).

The Codex skill should reuse that page structure without reusing the native LLM-provider path:

- Gather source files and export data, then build or infer module grouping (`generator.js:180-185`).
- Generate leaf pages first, then parent pages after child pages exist; native code flattens the module tree into leaves and parents for that ordering (`generator.js:198-230`, `generator.js:782-799`).
- Generate an overview after module pages (`generator.js:247-250`, `generator.js:486-520`).
- Record metadata and module-tree data equivalent to `meta.json` and `module_tree.json` where practical (`generator.js:251-261`, `generator.js:883-896`).
- Treat native HTML viewer generation as optional: the viewer embeds markdown pages, module tree, and metadata into a self-contained `index.html` (`dist/core/wiki/html-viewer.js:1-12`, `html-viewer.js:31-41`).

## Graph evidence to collect or cite

The native graph query layer provides the concepts the Codex-authored wiki should use as evidence:

- Exported symbols per file via `DEFINES` relationships where `n.isExported = true` (`dist/core/wiki/graph-queries.js:28-50`).
- All graph-tracked files (`graph-queries.js:51-60`).
- Inter-file and intra-module `CALLS` relationships (`graph-queries.js:62-98`).
- Incoming and outgoing module-boundary calls (`graph-queries.js:99-134`).
- Process/flow traces that pass through selected files via `STEP_IN_PROCESS` relationships (`graph-queries.js:135-178`).
- Overview-level processes and inter-module edge summaries for architecture explanations and diagrams (`graph-queries.js:179-240`).

Codex-side documentation should cite or summarize these inputs rather than presenting generic architecture summaries. A minimal evidence bundle for a page should include at least source file paths plus one of: exported symbols, call edges, incoming/outgoing dependencies, process traces, or direct `gitnexus context`/`impact` output.

## Prompt/page semantics to mirror

Native prompts ask for three layers:

- **Leaf/module page:** source code plus internal calls, outgoing calls, incoming calls, and execution flows (`dist/core/wiki/prompts.js:42-57`).
- **Parent page:** child docs plus cross-module calls and shared execution flows (`prompts.js:68-77`).
- **Overview page:** project info, module summaries, inter-module call edges, and key system flows; the prompt asks for natural links to module pages and a small Mermaid diagram only when helpful (`prompts.js:79-106`).

Codex-authored docs should follow the same layers:

```text
docs/wiki/
  overview.md
  <parent-or-module>.md
  <leaf-or-focused-area>.md
  metadata.md          # or equivalent section/frontmatter
```

Each page should include “Evidence” or “Sources” lines such as:

```text
Sources: src/foo.ts, src/bar.ts
Graph: gitnexus context FooService; gitnexus impact src/foo.ts
Index: gitnexus status checked at <timestamp>
```

## Large-repo and staleness guidance

Native generation has a module token budget and truncates oversized source context (`generator.js:420-431`), and the overview limits process/edge summaries (`generator.js:502-518`). The Codex skill should likewise avoid loading the full graph for large repos. Slice by directory, module, symbol family, route, tool, or execution flow, then write pages incrementally.

If the index is stale or missing, do not hide that fact. Either refresh the index or mark generated docs as provisional and limited to directly inspected source evidence.

## Review checklist for this reference

- The skill boundary is truthful: GitNexus provides graph context; Codex authors docs.
- Native provider facts are described as OpenAI/OpenAI-compatible API or Cursor CLI, not Codex-provider support.
- Existing-index behavior is explicit and backed by source anchors.
- Page structure maps to leaf/module, parent, overview, metadata, and optional viewer concepts.
- Graph evidence requirements include exports, calls, incoming/outgoing boundaries, processes, and inter-module edges.
