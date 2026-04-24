---
name: project-explainer-web
description: "Generate a minimal explainer webpage for a project or task."
---

# Project Explainer Web

## Overview

Create a simple explainer webpage that helps a human quickly understand either the current project or the current task without reading the whole repository first.

Prefer the lightest implementation that preserves clarity. Default to a standalone static page. Only integrate into the existing app when the user explicitly asks for in-app navigation or when the repository already has a very obvious page slot that can be extended safely.

Do not build a fancy landing page. Build a knowledge page.

## Default outcome

Produce a page that lets a reader answer these questions in a few minutes:

- What is this project or task trying to do?
- Which framework, runtime, and layers matter?
- How does the relevant flow work end to end?
- Which principles or background knowledge should the reader know?
- Which files should the next developer read first?
- What solution direction is recommended next, and why?
- Which parts are involved, in a visible structure tree?
- Which technical topics are involved, in a visible technology tree?

Support both scopes:

- **Project mode**: explain the repository, subsystem, or product surface as a whole
- **Task mode**: explain a concrete change request, technical question, or implementation decision

Support both languages:

- **Chinese mode**: default output language
- **English mode**: use when the user explicitly asks for English

When the user does not force a location, write the output under the repository `_learn_web/` folder.

Default placement:

- project page: `./_learn_web/project-<ascii-slug>/index.html`
- task page: `./_learn_web/task-<ascii-slug>/index.html`

## Required rules

Always follow these filename and path rules:

- Page content language can be Chinese or English
- Directory names and file names must remain ASCII-only
- Never generate Chinese directory names or file names under `_learn_web/`
- If the task title is Chinese-only, prefer passing an explicit English `--slug`
- If no explicit slug is provided, fall back to an ASCII-safe derived slug

Always include these sections:

- Hero summary
- Why it matters
- **Affected structure tree**
- Architecture at a glance
- Flow explanation
- Key files to read first
- **Related technology tree** when technology is involved
- Principles and background knowledge
- Constraints and risks
- Recommended solution
- Next actions

The structure tree must show:

- which parts are involved
- how they are grouped
- what each part specifically does

The technology tree must show:

- which frameworks, runtimes, protocols, concepts, and parameters are involved
- what each technical point means
- which tradeoffs or dependencies matter

## Workflow

### 1. Gather the minimum grounding

Inspect only the files that define the stack, entry points, task scope, and affected modules.

Start with:

- repository manifests and build files
- top-level docs and plans
- task-related source files
- recent errors, diffs, or logs from the user

Use `references/repo-scan-checklist.md` when you need a fast scan order.

Treat user-provided requirements, logs, stack traces, and current branch artifacts as the primary source of truth.

Separate evidence from inference. Do not present guesses as facts.

### 2. Decide scope and language early

Choose one scope:

- `project`
- `task`

Choose one language:

- `zh` by default
- `en` only when the user explicitly requests English

Do not mix languages unless the user explicitly asks for bilingual output.

### 3. Convert findings into a teaching outline

Turn the repo scan into a page outline before building the page.

Use `references/page-outline.md` for the default structure.

Keep sections short. Prefer bullets, callout cards, and tree blocks over dense prose.

Explain each important term once in plain language.

### 4. Choose the simplest implementation path

Use this order by default:

1. Standalone static HTML page copied from `assets/minimal-explainer-site/index.html`
2. Minimal page inside the repository's existing frontend stack when the user explicitly wants the page inside the app
3. Slightly richer interactivity only when it directly improves comprehension

Avoid:

- new dependencies
- complex routing
- backend changes
- state management libraries
- heavy charting or animation
- architecture changes made only for presentation

If a static page is enough, keep it static.

### 5. Decide the output path

Prefer repository-local learning pages over scattered scratch files.

Use these defaults unless the user explicitly gives another directory:

- `./_learn_web/project-<ascii-slug>/index.html`
- `./_learn_web/task-<ascii-slug>/index.html`

Derive `<ascii-slug>` from the subject being explained. Keep it short and readable.

Examples:

- `./_learn_web/task-auto-model-loading/index.html`
- `./_learn_web/project-electron-architecture/index.html`

If the source title is non-ASCII, either:

- pass an explicit English `--slug`, or
- accept the tool's ASCII fallback slug

### 6. Scaffold the page

Use the bootstrap script when a fast starting point helps:

```bash
python3 scripts/bootstrap_explainer_page.py \
  --repo-root . \
  --scope task \
  --language zh \
  --slug auto-model-loading \
  --title "任务说明页" \
  --project "项目名" \
  --task "当前任务"
```

For English:

```bash
python3 scripts/bootstrap_explainer_page.py \
  --repo-root . \
  --scope task \
  --language en \
  --slug model-loading-strategy \
  --title "Task Explainer" \
  --project "Project Name" \
  --task "Current Task"
```

The script copies the single-file template, fills the localized placeholders, and by default writes to `_learn_web/<scope>-<ascii-slug>/index.html`.

Use `--scope project` when the subject is a whole project or subsystem.

Use an explicit directory only when the user asks for a custom location.

After scaffolding, edit the generated HTML directly. Do not introduce unnecessary abstractions.

### 7. Fill the page with useful content

At minimum, include:

- a short project or task summary
- the relevant stack or framework snapshot
- a visible structure tree of involved parts and functions
- a flow explanation of how the relevant part works
- key files and why they matter
- a visible technology tree when technology is involved
- related principles, concepts, or background knowledge
- constraints, risks, or open questions
- a recommended solution or next-step direction

If the task is narrow, focus the page on the affected subsystem instead of summarizing the entire repository.

If the user asks a knowledge-seeking question such as:

> 我想设计一个自动化选择模型是全量加载还是用动态加载参数启动，我需要先了解相关背景知识

Treat it as **task mode** unless the user explicitly asks for a whole-project overview.

When possible, point to exact file paths so the reader can jump into the codebase immediately.

### 8. Keep the page readable

Optimize for skimming:

- lead with the answer
- keep paragraphs short
- prefer lists over dense prose
- prefer one simple visual grouping over many nested containers
- make the structure tree explicit instead of implied
- make the technology tree explicit instead of scattered
- prefer a comfortable, non-harsh visual style instead of a plain white document
- surface the recommendation near the end in a dedicated section

A reader should understand the page in 3-5 minutes.

### 9. Validate before finishing

Check that the page:

- answers the core project/task questions
- uses repository evidence instead of generic filler
- stays simple enough to maintain
- names the important files and boundaries accurately
- includes a concrete recommended solution or next step
- includes the structure tree
- includes the technology tree when relevant
- uses Chinese by default unless English was explicitly requested
- uses ASCII-only file and directory names
- lands under `_learn_web/` unless the user requested another destination

If you created a static page, inspect the generated HTML and verify the placeholders were replaced.

## Resources

### scripts/bootstrap_explainer_page.py

Use this script to copy the minimal single-file template into a target folder and prefill localized placeholders.

### references/repo-scan-checklist.md

Read this file when you need a fast order of operations for understanding an unfamiliar codebase or task.

### references/page-outline.md

Read this file when you need a default page structure or section prompts.

### assets/minimal-explainer-site/index.html

Use this self-contained template when you want the fastest path to a readable explainer webpage.
