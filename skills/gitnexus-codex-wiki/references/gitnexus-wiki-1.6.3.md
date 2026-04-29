# GitNexus wiki behavior reference for `gitnexus@1.6.3`

This reference records local evidence used by the `gitnexus-codex-wiki` skill. It is intentionally about GitNexus behavior, not about adding a new provider.

## CLI evidence

Observed with `/opt/homebrew/bin/gitnexus`:

```bash
gitnexus --version
# 1.6.3

gitnexus wiki --help
# Usage: gitnexus wiki [options] [path]
# Generate repository wiki from knowledge graph
# --provider <provider>    LLM provider: openai or cursor (default: openai)
# --api-key <key>          LLM API key or Azure api-key
# --review                 Stop after grouping to review module structure before generating pages
```

The native `gitnexus wiki` command checks for an existing index before resolving LLM configuration. In `dist/cli/wiki.js`, it loads `getStoragePaths(repoPath)`, calls `loadMeta(storagePath)`, and exits with: `Run gitnexus analyze first to index this repository` when no metadata exists.

## Internal wiki pipeline concepts

`dist/core/wiki/generator.d.ts` describes `WikiGenerator` as a pipeline with:

1. prerequisite validation and graph structure gathering,
2. module tree construction,
3. module page generation bottom-up,
4. overview page generation,
5. incremental updates through git diff plus module-file mapping.

`dist/core/wiki/graph-queries.d.ts` and `.js` expose the graph concepts this skill mirrors from the Codex side:

- files with exported symbols,
- all tracked files,
- inter-file call edges,
- intra-module call edges,
- outgoing/incoming module calls,
- processes for selected files,
- top repository processes,
- inter-module edge counts for overview diagrams.

`dist/core/wiki/prompts.d.ts` shows the page structure model:

- grouping prompt: module names mapped to file arrays,
- leaf/module prompt: source code plus internal calls, outgoing calls, incoming calls, and execution flows,
- parent prompt: child docs plus cross-module calls and shared processes,
- overview prompt: project info, module summaries, inter-module edges, and top processes.

## Boundary captured by the skill

The Codex skill reuses the above structure as an authoring model but does not route Codex through GitNexus providers. GitNexus supplies local graph/index context; Codex writes markdown directly in the Codex session.
