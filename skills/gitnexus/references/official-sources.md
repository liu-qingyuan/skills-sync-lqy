# Official Sources

Use these as design anchors when refreshing the skill.

## GitNexus

- GitNexus README: CLI + MCP recommended; `npx gitnexus analyze`; `gitnexus setup`; Codex MCP config; CLI command list; MCP tools/resources; multi-repo registry.
  - https://github.com/abhigyanpatwari/GitNexus
- GitNexus ARCHITECTURE: CLI/MCP/HTTP are three interfaces to the same backend; MCP tools include `list_repos`, `query`, `cypher`, `context`, `impact`, and change/route/tool analysis tools.
  - https://github.com/abhigyanpatwari/GitNexus/blob/main/ARCHITECTURE.md

## OpenAI / Codex

- Codex config docs: MCP servers are configured in `~/.codex/config.toml`; server tools can be controlled through MCP server config.
  - https://github.com/openai/codex/blob/main/docs/config.md
  - https://developers.openai.com/codex/config-reference
- OpenAI Docs MCP: Codex can connect to MCP servers; config is shared between CLI and IDE extension; `codex mcp list` verifies configuration.
  - https://developers.openai.com/learn/docs-mcp
- Codex App Server article: MCP is useful for callable tools, but richer session semantics may need native Codex/App Server surfaces. Use this to avoid overclaiming MCP as a replacement for all CLI/workflow behavior.
  - https://openai.com/index/unlocking-the-codex-harness/
