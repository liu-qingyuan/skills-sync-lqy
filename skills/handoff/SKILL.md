---
name: handoff
description: Generate a structured, copy-paste work-contract prompt for another AI or fresh session to continue safely. Use when the user invokes $handoff or asks to hand off, delegate, transfer context, or prepare a prompt for another agent. Do not write files and do not execute the handed-off task.
argument-hint: "What should the next AI do?"
---

Generate a handoff prompt that the user can copy and paste into another AI or fresh session. Output the prompt directly in chat. Do not save a file, do not write to `/tmp`, and do not modify the workspace.

`handoff` is a prompt-generation skill only: do not implement, fix, research, commit, run destructive commands, or otherwise execute the handed-off task unless the user separately asks for execution outside this skill.

If the user passed arguments, treat them as the target task for the next AI. Example: `$handoff 修一下这个bug` means produce a prompt asking another AI to fix that bug, with enough current context to start safely.

## Output format

Default to the current two-section compatibility envelope:

1. `可复制 prompt`
   - Put the handoff prompt in a fenced Markdown code block.
   - The prompt should speak directly to the next AI.
2. `这个 handoff 写了什么`
   - Briefly explain which context, constraints, validation expectations, and stop condition you included.

Treat this as the stable user-facing default, not a permanent schema promise. If a future user explicitly requests a different handoff shape or machine-readable metadata, preserve the same prompt-generation/no-write/no-execution boundaries while adapting the envelope.

## Core style

The copyable prompt should be a compact work contract, not a narrative recap or a rigid implementation script.

Prioritize:

- observable outcome over vague intent;
- architecture/product invariants over premature class/function/file prescriptions;
- explicit scope and non-goals over open-ended cleanup;
- validation evidence and stop condition over “looks good” completion;
- artifact references over pasted long content.

Only include absolute rules when they are truly non-negotiable. Give the next AI discretion over local naming, small file organization, and implementation approach unless the user or existing contracts make those decisions binding.

## Choose a task-appropriate prompt shape

Select the smallest structure that preserves the task's outcome, constraints, validation, and stop condition. Do not force every heading into tiny handoffs, but never omit the result, important boundaries, verification expectations, and stop rule when they are known.

### New feature

Use this when the next AI must add capability or extend an existing system.

Include:

- `Goal`
- `Architecture invariants`
- `Scope`
- `Acceptance criteria`
- `Agent discretion`

Emphasize shared seams, existing ownership, compatibility, and tests. Avoid telling the next AI to create specific classes or inheritance structures unless that is already a hard contract.

### Product behavior

Use this when the main question is how users/system behavior should change.

Include:

- `Summary`
- `Desired behavior`
- `Non-goals / constraints`
- `Why`

Make user-visible behavior observable. Include what must not happen, such as silent model/session changes, privacy leaks, permanent setting changes, or broad routing changes, when relevant.

### Engineering fix or refactor

Use this for bugs, infrastructure fixes, test isolation, cleanup, or narrowly scoped refactors.

Include:

- `Problem`
- `Why it matters`
- `Exact scope`
- `Explicit non-goals`
- `Likely touched surfaces`
- `Test plan`
- `Stop rule`

Keep touched surfaces as investigation starting points, not mandatory edits. State when the next AI must stop and report instead of widening the change.

### Research task

Use this when the next AI should investigate a claim, compare options, or gather evidence.

Include:

- `Research question`
- `Claims to investigate`
- `Unknowns`
- `Evidence needed`
- `Counterexample queries`
- `Source conflict policy`
- `Drop condition`
- `Verifier checks`
- `Required output`

Require confidence levels and evidence-vs-inference separation. Do not ask for a strong conclusion when repeatable evidence is missing.

### General fallback

Use this when no specialized shape fits, or when the task mixes several types.

Include the relevant subset of:

- `Objective`
- `Context`
- `Current behavior`
- `Desired behavior`
- `Invariants`
- `Scope`
- `Explicit non-goals`
- `Decision boundaries`
- `Likely touched surfaces`
- `Acceptance criteria`
- `Validation`
- `Expected output`
- `Stop condition`

## Handoff prompt requirements

The generated prompt should include, when available:

- The next AI's objective, based on the user's arguments or the current task.
- Why the task matters, if that helps the next AI make tradeoffs.
- Relevant project/repo paths, branch/commit status, changed files, artifact paths, issue/PR links, specs, plans, ADRs, logs, or URLs.
- Current conversation facts needed to continue without rereading everything.
- Current behavior and desired behavior, when applicable.
- Invariants that must hold: compatibility, architecture boundaries, data/state ownership, privacy/security, performance/cost, or platform behavior.
- In-scope work and explicit non-goals.
- Decision boundaries: what the next AI may decide independently, and what requires stopping to ask or report.
- Likely touched surfaces, clearly labeled as starting points rather than a forced edit list.
- Suggested skills, tools, or subagents to invoke, if useful.
- Acceptance criteria that are testable or observable.
- Validation expectations: targeted tests, typecheck, lint, build, integration/smoke tests, manual smoke steps, contract tests, or review gates as relevant.
- Expected final response: changed files, investigation findings, validation evidence, skipped checks, and residual risks.
- A clear stop condition for the next AI.

Do not duplicate long content already captured in artifacts such as PRDs, plans, ADRs, issues, commits, diffs, generated docs, traces, or logs. Reference those by path, URL, commit, artifact name, or stable identifier instead.

## Decision-boundary defaults

When the user has not said otherwise, tell the next AI it may decide:

- internal naming;
- small local file splits or consolidation;
- local implementation approach that preserves public behavior and contracts;
- targeted tests that prove the requested behavior.

Tell the next AI to stop and ask/report before:

- changing public APIs, persisted formats, or user-visible contracts beyond the request;
- adding dependencies, scripts, services, registries, plugin systems, or broad abstractions;
- running destructive commands or modifying unrelated files;
- weakening validation, privacy, security, or architecture boundaries;
- copying private or oversized raw artifacts into the prompt or final answer.

## Compact handoffs for small tasks

For a small, well-bounded task, produce a shorter prompt instead of a full template. It still must include:

- the observable target result;
- known constraints or non-goals;
- validation expectations or manual smoke evidence;
- a stop condition.

Example shape:

```markdown
目标：修复 <specific observable problem>。
当前行为：<what happens now, with environment/error if known>。
期望行为：<what should be observable after the fix>。
范围/非目标：<what to investigate/change, and what not to widen>。
验收与验证：<tests/checks/manual smoke expected>。
停止规则：如果需要改变 <public API/persistence/destructive behavior/etc.>，先报告选项和风险。
```

Keep the prompt dense and practical. Prefer actionable context over narrative recap.
