---
name: gitnexus
description: "GitNexus code-graph grounding for OMX workflows. Use `$gitnexus` alone or as a modifier with interview, planning, execution, QA, review, security, visual, or trace workflows."
---

# GitNexus

GitNexus is a code-graph grounding layer for OMX/Codex workflows. Use it to collect repository facts before asking the user about code internals, planning changes, or editing source.

## Composition Rule

When `$gitnexus` appears with another workflow keyword, treat the other workflow as primary and GitNexus as a modifier/context provider.

Examples:

```text
$deep-interview $gitnexus "我想添加一个新的对话功能"
$plan $gitnexus "调查图片生成后 UI 不显示"
$ralplan $gitnexus "重构 OpenClaw media recovery 链路"
$team $gitnexus "compare CLI and MCP for this bug"
$ralph $gitnexus "finish the OpenClaw media recovery fix"
$autopilot $gitnexus "ship a new conversation feature"
$ultraqa $gitnexus "verify the chat/media flow"
$code-review $gitnexus "review this diff for graph-aware regressions"
$security-review $gitnexus "review auth/session changes"
$visual-ralph $gitnexus "match this reference UI in the existing app"
$visual-verdict $gitnexus "score this screenshot against the app implementation"
$trace $gitnexus "explain the agent flow and code context for this run"
```

Behavior:
1. Keep the primary workflow in charge of its lifecycle and output contract.
2. Run GitNexus grounding before the primary workflow asks codebase questions or writes a plan.
3. Save the grounding report under `.omx/context/gitnexus-{slug}-{timestamp}.md`.
4. Feed that context into the primary workflow as brownfield evidence.
5. Do not duplicate or replace the primary workflow logic. GitNexus only supplies repository graph context, health checks, and impact/navigation evidence.

If `$gitnexus` is invoked alone, run the grounding workflow and return the context path plus recommended next command.

## Grounding Workflow

1. **Preflight**
   - Run `scripts/gitnexus-preflight.sh --task "<task>"` from the target repo root when available.
   - Confirm `gitnexus` exists, current git root, `gitnexus status`, `gitnexus list`, and `codex mcp list`.
   - If the index is stale/missing, report it and recommend `gitnexus analyze` or `gitnexus index`; do not auto-reindex unless the user asked for indexing or execution authority is already clear.

2. **Choose CLI vs MCP**
   - Prefer CLI for health, setup, repair, reproducible transcripts, `serve`, and WAL/database errors.
   - Prefer MCP for in-session agent automation after repo/symbol names are known.
   - Use both when a result will guide a plan or code change.
   - See `references/cli-vs-mcp.md` for the evidence-backed split.

3. **Collect graph context**
   - Read repo context first: `gitnexus list`, `gitnexus status`, or MCP `list_repos` / repo context resource if exposed.
   - Use `gitnexus context <symbol-or-file>` for known symbols.
   - Use `gitnexus impact <symbol-or-file>` before planning edits.
   - Use `gitnexus cypher '<query>'` for exact graph relationships.
   - Use `gitnexus query '<concept>'` only as a broad hint; validate because local experiments showed query can return empty results in read-only DB/FTS-warning scenarios.
   - Always confirm critical claims with direct source reads (`rg`, `sed`, IDE, or code-intel) and tests.

4. **Write handoff context**
   Include:
   - Task statement and target repo.
   - Index/MCP health.
   - Commands or MCP calls used.
   - File/line evidence from direct source confirmation.
   - Graph findings: candidate files, symbols, callers/callees, impact risks.
   - Unknowns, assumptions, and recommended next workflow.

5. **Primary workflow integration**
   - For `$deep-interview`: use GitNexus facts to avoid asking the user where code lives; ask intent, outcome, non-goals, decision boundaries, and acceptance criteria.
   - For `$plan` / `$ralplan`: cite the GitNexus context snapshot and direct source lines in the plan; keep implementation steps sized to real scope.
   - For `$ralph` / `$team`: run pre-context and impact grounding before execution/delegation; pass the context path into worker assignments; tests and source remain the verification source of truth.
   - For `$autopilot`: run GitNexus preflight before autonomous planning/execution so the pipeline starts with indexed repo context and known impact risks.
   - For `$ultraqa`: use GitNexus to find likely test surfaces, affected flows, and regression targets before cycling QA.
   - For `$ultrawork`: use GitNexus to split independent work lanes by files/symbols/processes and avoid overlapping edits.
   - For `$code-review`: use GitNexus impact/context to identify changed-symbol blast radius, hidden callers, and missing regression tests.
   - For `$security-review`: use GitNexus to trace auth/session/data-flow entry points and consumers, then apply security reasoning directly to source.
   - For `$visual-ralph`: use GitNexus to locate UI implementation files before visual iterations; still run `$visual-verdict` every visual edit loop.
   - For `$visual-verdict`: use GitNexus only when a screenshot verdict must be tied back to code locations; pure image comparison can skip graph context.
   - For `$trace`: use GitNexus context as a codebase layer in the execution trace, not as a replacement for OMX trace logs.

## Command Patterns

For simple preflight:

```bash
~/.codex/skills/gitnexus/scripts/gitnexus-preflight.sh --task "describe the task"
```

For known symbols:

```bash
gitnexus context SymbolName
gitnexus impact SymbolName
gitnexus cypher 'MATCH (a)-[r]->(b) WHERE r.type = "CALLS" RETURN a.name, b.name LIMIT 25'
```

For web UI:

```bash
gitnexus serve
# open https://gitnexus.vercel.app?server=http://localhost:4747
```

`http://localhost:4747/` returning `Cannot GET /` is expected for the API server root; use `/api/...` endpoints or the hosted/local web UI.

## Safety and Verification

- Do not use GitNexus output as the final truth for code edits; it is a map, not the terrain.
- Do not run real product side effects (for example vMLX image generation) just to build graph context.
- Do not auto-run expensive `gitnexus analyze --force` unless the user asked to index/reindex or stale index blocks the task.
- If GitNexus emits WAL/corruption/segfault errors, stop graph-dependent conclusions and repair index state first.
- Preserve upstream OMX skills; prefer this composable skill over editing `$deep-interview`, `$plan`, or `$ralplan`.

## References

Load only what is needed:
- `references/composition.md` — how `$gitnexus` composes with OMX workflows.
- `references/workflow-matrix.md` — per-workflow GitNexus integration rules.
- `references/cli-vs-mcp.md` — CLI/MCP decision table and local experiment findings.
- `references/query-patterns.md` — practical query/context/impact/cypher patterns.
- `references/official-sources.md` — official source notes used to design this skill.
