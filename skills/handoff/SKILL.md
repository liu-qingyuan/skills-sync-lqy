---
name: handoff
description: Generate a copy-paste prompt for another AI or fresh session to continue work with enough context. Use when the user invokes $handoff or asks to hand off, delegate, transfer context, or prepare a prompt for another agent. Do not write files.
argument-hint: "What should the next AI do?"
---

Generate a handoff prompt that the user can copy and paste into another AI or fresh session. Output the prompt directly in chat. Do not save a file, do not write to `/tmp`, and do not modify the workspace.

If the user passed arguments, treat them as the target task for the next AI. Example: `$handoff 修一下这个bug` means produce a prompt asking another AI to fix that bug, with enough current context to start safely.

## Output format

Return exactly two sections:

1. `可复制 prompt`
   - Put the handoff prompt in a fenced Markdown code block.
   - The prompt should speak directly to the next AI.
2. `这个 handoff 写了什么`
   - Briefly explain what context and instructions you included.

## Handoff prompt requirements

The generated prompt should include, when available:

- The next AI's objective, based on the user's arguments or the current task.
- Relevant project/repo paths, branch/commit status, changed files, and artifact paths/URLs.
- Current conversation facts needed to continue without rereading everything.
- Constraints, non-goals, and user preferences.
- Suggested skills or tools to invoke, if useful.
- Concrete next steps and verification expectations.
- A clear stop condition for the next AI.

Do not duplicate long content already captured in artifacts such as PRDs, plans, ADRs, issues, commits, diffs, or generated docs. Reference those by path, URL, or commit instead.

Redact sensitive information such as API keys, passwords, tokens, private personal data, and credentials. If sensitive details are necessary, describe what kind of secret is needed without exposing the value.

Keep the prompt dense and practical. Prefer actionable context over narrative recap.
