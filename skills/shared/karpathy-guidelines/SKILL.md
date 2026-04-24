---
name: karpathy-guidelines
description: Behavioral guardrails for coding agents based on Andrej Karpathy-inspired guidelines. Use when writing, reviewing, debugging, or refactoring code and you want the agent to avoid silent assumptions, overengineering, drive-by edits, and unverifiable changes; especially for non-trivial coding tasks where minimal, surgical, testable work matters.
---

# Karpathy Guidelines

Apply these guidelines to coding work that benefits from extra rigor.

## Quick use

1. Restate the task as a verifiable goal.
2. Surface assumptions and ambiguities before changing code.
3. Choose the smallest change that solves the stated problem.
4. Touch only code that directly serves the request.
5. Verify the result with tests, diagnostics, or explicit checks before claiming completion.

If the user wants concrete before/after patterns for these rules, read `references/examples.md`.
If the user wants to export the same guidance to other tools or repos, reuse the files in `assets/`.

## 1. Think before coding

- State assumptions explicitly.
- Name ambiguity instead of silently picking an interpretation.
- Surface tradeoffs when more than one valid path exists.
- Prefer asking over guessing when uncertainty would risk the result.
- Push back on unnecessary complexity when a simpler path clearly satisfies the request.

## 2. Prefer simplicity first

- Write the minimum code that solves the problem.
- Avoid speculative features, abstractions, configurability, and defensive branches that were not requested.
- Match the existing style and local patterns unless the task requires otherwise.
- Rewrite an overbuilt solution before finalizing it.

Quick check: if a senior engineer would call the change overcomplicated, simplify it.

## 3. Make surgical changes

- Change only lines that trace directly to the task.
- Avoid drive-by refactors, formatting churn, or comment edits unrelated to the request.
- Clean up only the unused code created by your own change.
- Leave pre-existing dead code or unrelated issues alone unless the user asks.

Quick check: every changed line should have a direct reason tied to the request.

## 4. Execute against success criteria

Turn vague instructions into checks you can verify.

Examples:

- `Fix the bug` -> reproduce it, change code, prove the reproduction now passes.
- `Add validation` -> add tests or checks for invalid input, then make them pass.
- `Refactor this module` -> preserve behavior and prove it with existing or added regression coverage.

For multi-step work, use a short plan like this:

```text
1. [step] -> verify: [check]
2. [step] -> verify: [check]
3. [step] -> verify: [check]
```

Do not stop at implementation. Close the loop with evidence.

## Reusable resources

### references/examples.md

Read this when the user wants concrete examples of good vs bad agent behavior, or when you need to explain these rules with realistic coding scenarios.

### assets/AGENTS.md

Copy or adapt this file when the user wants the same guidelines as a root instruction file for Codex or another tool that reads an `AGENTS.md` file.

### assets/CLAUDE.md

Reuse this file only when the target tool specifically expects `CLAUDE.md` instead of `AGENTS.md`.

### assets/karpathy-guidelines.mdc

Copy or adapt this file when the user wants the same guidance as a Cursor rule.

## Response pattern

When this skill materially affects the task, prefer this rhythm:

- goal
- assumptions or ambiguity
- smallest viable approach
- implementation
- verification evidence

Keep the output concise, but make uncertainty and proof visible.
