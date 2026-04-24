# skills-sync-test

Private test repository for validating Skills Manager sync with per-CLI separation.

## Layout

- `skills/codex/` — Codex / OMX oriented skills
- `skills/opencode/` — OpenCode oriented skills
- `skills/claude-code/` — Claude Code oriented skills
- `skills/shared/` — cross-tool reusable skills

## Current skills

- `skills/codex/finish-remaining-stories/` — currently Codex-first because it depends on OMX workflows like `$team`, `$ralplan`, `$deep-interview`, and `.codex` conventions.
