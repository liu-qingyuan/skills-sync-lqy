# skills-sync-lqy

Private skill library for managing and syncing personal skills across Codex, OpenCode, Claude Code, and shared workflows.

## Layout

- `skills/codex/` — Codex / OMX oriented skills
- `skills/opencode/` — OpenCode oriented skills
- `skills/claude-code/` — Claude Code oriented skills
- `skills/shared/` — cross-tool reusable skills

## Seeded skills

- `skills/codex/finish-remaining-stories/` — currently Codex-first because it depends on OMX workflows like `$team`, `$ralplan`, `$deep-interview`, and `.codex` conventions.
- `skills/shared/karpathy-guidelines/` — cross-tool coding guardrails that are not tied to a single CLI path or runtime.
