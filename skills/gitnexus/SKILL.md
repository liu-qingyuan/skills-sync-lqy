---
name: gitnexus
description: Guide and router for local GitNexus code-graph tools. Use when the user asks how to use GitNexus, check or build an index, query code relationships, inspect callers/callees, assess impact, debug with graph context, refactor safely, review PRs, or choose a GitNexus-related skill. Requires a local GitNexus CLI/MCP setup and an indexed repository for graph-backed claims.
---

# GitNexus

`$gitnexus` is a lightweight guide for the local GitNexus toolset. It explains how to use the installed CLI/MCP, checks whether graph evidence is available, and routes to the most specific GitNexus skill.

GitNexus here is local/non-official project tooling. Treat graph output as a map: useful for candidates, relationships, and impact, but confirm important claims with source reads and tests.

## Default answer

When invoked, return only what is useful for the current task:

1. **Status** — whether GitNexus CLI/MCP/index evidence is known, or the smallest check/index command to run.
2. **Best route** — index first when needed, then use the GitNexus skill or command that fits the task.
3. **Minimal examples** — only commands/queries relevant to the task.
4. **Verification boundary** — what still needs direct source or test evidence.

## Quick commands

Use the project’s installed command shape when known; otherwise show both common forms briefly.

- Check tool/index: `gitnexus --version`, `gitnexus status`, `gitnexus list`, or `node .gitnexus/run.cjs status`.
- Build/refresh index: `gitnexus analyze <repo>` or `node .gitnexus/run.cjs analyze`. If the current repo is not indexed and GitNexus is available, run one normal index first instead of skipping graph use.
- Explore context: `gitnexus context <symbol-or-file>`.
- Impact/blast radius: `gitnexus impact <symbol-or-file>`.
- Exact graph query: `gitnexus cypher '<query>'`.
- Web UI: `gitnexus serve` then open the shown URL. A plain `Cannot GET /` at root is not by itself a GitNexus failure.

Do not run force cleanup, destructive repair, or broad graph operations unless the user asked or the task is blocked and the need is explicit. A normal first-time index for the current repo is allowed when graph evidence is relevant.

## Related skills

Prefer the most specific skill for actual work:

- `$gitnexus-cli` — install, index, status, clean, serve, generate wiki.
- `$gitnexus-guide` — available MCP tools, resources, schema, query reference.
- `$gitnexus-exploring` — understand architecture, flows, callers/callees.
- `$gitnexus-debugging` — trace bugs, errors, failing paths.
- `$gitnexus-impact-analysis` — assess what changes could break.
- `$gitnexus-refactoring` — rename, move, extract, split, restructure safely.
- `$gitnexus-pr-review` — review PRs/diffs with graph context.
- `$gitnexus-codex-wiki` — write graph-grounded docs/wiki pages.

## Use rules

- `$gitnexus` alone is for orientation, preflight, and routing; do not turn it into a full workflow.
- If GitNexus is unavailable, say that plainly and fall back to normal repository inspection.
- If the repo is unindexed, run one normal index first, then retry the GitNexus check. If indexing fails, report the failure and fall back.
- If the index is stale, prefer refresh/reindex before relying on graph evidence; fall back only when refresh is unavailable or fails.
- Use graph evidence for leads, not as the only proof for correctness.
- Keep outputs concise; add details only when the user asks or the task requires them.

## Optional references

Load only if needed:

- `references/cli-vs-mcp.md` — choosing CLI vs MCP.
- `references/query-patterns.md` — context, impact, and Cypher examples.
