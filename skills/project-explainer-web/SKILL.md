---
name: project-explainer-web
description: "Generate or incrementally maintain a minimal explainer webpage for a project or task, with offline-safe Mermaid graph TB diagrams that make the relevant architecture, structure, and technology relationships easier to understand. Use when Codex should create, extend, or revise a repository-local explainer page under _learn_web instead of restarting the page from scratch."
---

# Project Explainer Web

## Overview

Create a simple explainer webpage that helps a human quickly understand either the current project or the current task without reading the whole repository first.

Prefer the lightest implementation that preserves clarity. Default to a standalone static page. Only integrate into the existing app when the user explicitly asks for in-app navigation or when the repository already has a very obvious page slot that can be extended safely.

Do not build a fancy landing page. Build a knowledge page.

Prefer outputs that still work from `file://` without network access.

Default to incremental maintenance when an explainer page for the same subject already exists. Extend, reconcile, and reorganize the existing page in place unless the user explicitly asks for a reset or a separate page.

## Default outcome

Produce a page that lets a reader answer these questions in a few minutes:

- What is this project or task trying to do?
- Which framework, runtime, and layers matter?
- How do the important parts connect in one top-down Mermaid graph?
- How does the relevant flow work end to end?
- Which files, documents, or logs are the real source of truth for this explanation?
- Which architecture boundaries or invariants must not be broken?
- Which principles or background knowledge should the reader know?
- Which files should the next developer read first?
- If someone needs to change this area, where should they start and what should they avoid?
- Which commands should they run to verify understanding or validate changes?
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

Always follow these update rules:

- If a relevant explainer page already exists at the target path, read it first and treat it as user content to preserve unless it is clearly scaffold-only placeholder text
- Default to editing existing sections in place, appending new related sections, and refreshing stale details instead of deleting large working portions
- Only replace the whole page when the user explicitly asks for a reset, when the existing file is still mostly untouched scaffold content, or when the current structure is so broken that targeted edits would be less accurate than a rebuild
- When a follow-up request is adjacent to the same reader goal, prefer reusing the same page and expanding it; create a separate page only when the topic, audience, or reading goal is materially different
- When old content becomes partially outdated, keep the useful part, update the stale part, and make the change obvious in prose instead of silently discarding prior context

Always include these sections:

- Hero summary
- Why it matters
- **Affected structure tree**
- Architecture at a glance
- Flow explanation
- Source of truth / evidence map
- Key files to read first
- **Related technology tree** when technology is involved
- Boundaries and invariants
- How to modify this safely
- Verification commands
- Principles and background knowledge
- Constraints and risks
- Recommended solution
- Next actions

Always include at least one Mermaid `graph TB` diagram for the main project/task architecture.
Keep Mermaid rendering offline-safe by using bundled local assets, not CDN-only script references.

The structure tree must show:

- which parts are involved
- how they are grouped
- what each part specifically does
- how the main parent-child or dependency relationships connect from top to bottom

The structure tree must be shown in **both** forms:

- a Mermaid `graph TB` structure diagram
- a plain-text file/tree block such as:

```text
tests/
├─ e2e/        user-visible behavior
├─ low-level/  seam / state / contract
└─ support/    fixture and helper layer
```

Do not treat these as substitutes for each other. The Mermaid view explains relationships; the plain-text tree explains concrete filesystem shape.

The technology tree must show:

- which frameworks, runtimes, protocols, concepts, and parameters are involved
- what each technical point means
- which tradeoffs or dependencies matter

The technology tree must be shown in **both** forms when technology is involved:

- a Mermaid `graph TB` technology diagram
- a plain-text technology hierarchy or layered outline such as:

```text
Playwright
├─ runner / projects
├─ fixtures
└─ artifacts

Electron
├─ main
├─ preload
└─ renderer
```

Do not treat these as substitutes for each other. The Mermaid view explains relationships; the plain-text hierarchy explains the concrete technical stack and layered concepts.

When relationships between technologies matter, prefer Mermaid `graph TB` there as well. Keep node labels short and human-readable.

The evidence map must show:

- which files, docs, diffs, logs, or commands support the explanation
- which conclusions are direct facts vs reasoned interpretation
- any open questions that still require confirmation

The boundaries and invariants section must show:

- layer or ownership boundaries that should not be crossed casually
- critical invariants that future modifiers must preserve
- anti-patterns or tempting shortcuts that would weaken the design

The safe-modification section must show:

- where a developer should start reading before editing
- which file or layer should usually own a change
- what to modify first vs what should only be touched as a consequence

The verification commands section must show:

- the smallest useful commands for understanding or validating the area
- what each command proves
- when a command is optional, expensive, or environment-sensitive

The common anti-patterns section must show:

- the most tempting mistakes future modifiers are likely to make
- why each mistake is attractive but harmful
- what better alternative or guardrail to prefer instead

Project mode should bias toward:

- subsystem boundaries
- long-lived ownership and invariants
- major layers and integration surfaces
- recommended reading order for understanding the repository

Task mode should bias toward:

- touched flow and affected modules
- exact change points and safe modification path
- task-specific verification commands
- implementation recommendation for the current decision

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

### 2.5 Decide whether this is a new page or an update

Look for an existing explainer page before scaffolding a new one.

Check in this order:

- an explicit path from the user
- the likely `_learn_web/<scope>-<slug>/index.html` destination
- nearby existing explainer pages for the same subsystem, task family, or decision

Treat the work as an **update** when the current request is extending the same explainer, the same task family, or the same developer-reading journey.

Treat the work as a **new page** only when the reader goal is materially different, the prior page would become confusing if expanded, or the user explicitly wants a separate explainer.

### 3. Convert findings into a teaching outline

Turn the repo scan into a page outline before building the page.

Use `references/page-outline.md` for the default structure.

Keep sections short. Prefer bullets, callout cards, and tree blocks over dense prose.

Explain each important term once in plain language.

Draft the Mermaid `graph TB` blocks early so the page has a clear top-down architecture view before you polish the prose.

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

If an existing explainer page already covers the same subject, keep the same path and update that file in place. Do not create a sibling page with a slightly different slug unless there is a clear reason to split the material.

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
It also copies the bundled Mermaid runtime into the generated page's local `assets/` directory so the diagrams keep rendering offline.

Use `--scope project` when the subject is a whole project or subsystem.

Use an explicit directory only when the user asks for a custom location.

Only use the bootstrap script for a brand-new page.

If the target page already exists:

- read the existing HTML first
- preserve the sections that are still valid
- edit the generated HTML directly in place
- do not rerun the bootstrap script with `--force` unless the user explicitly asks to reset the page

Do not introduce unnecessary abstractions.

### 7. Fill the page with useful content

At minimum, include:

- a short project or task summary
- the relevant stack or framework snapshot
- a Mermaid `graph TB` architecture diagram that shows the main relationships
- a visible structure tree of involved parts and functions in **both** Mermaid and plain-text file-tree form
- a flow explanation of how the relevant part works
- a source-of-truth / evidence map
- key files and why they matter
- a visible technology tree when technology is involved
- the technology tree in **both** Mermaid and plain-text hierarchy form when technology is involved
- boundaries and invariants
- a safe-modification guide
- concrete verification commands
- common anti-patterns or tempting mistakes to avoid
- related principles, concepts, or background knowledge
- constraints, risks, or open questions
- a recommended solution or next-step direction

If the task is narrow, focus the page on the affected subsystem instead of summarizing the entire repository.

If the user asks a knowledge-seeking question such as:

> 我想设计一个自动化选择模型是全量加载还是用动态加载参数启动，我需要先了解相关背景知识

Treat it as **task mode** unless the user explicitly asks for a whole-project overview.

When possible, point to exact file paths so the reader can jump into the codebase immediately.

When updating an existing page:

- keep the current narrative spine when it is still valid
- add new evidence, files, diagrams, or caveats where they naturally belong
- reorganize sections only when that improves comprehension for the combined old + new scope
- preserve prior useful explanations unless they are superseded by better evidence
- prefer additive section edits over whole-file replacement

### 8. Keep the page readable

Optimize for skimming:

- lead with the answer
- keep paragraphs short
- prefer lists over dense prose
- prefer one simple visual grouping over many nested containers
- prefer one clear Mermaid `graph TB` over several fragmented diagrams
- make the structure tree explicit instead of implied
- make the technology tree explicit instead of scattered
- make evidence, boundaries, safe-change guidance, and anti-patterns explicit instead of assuming the reader can infer them
- prefer a comfortable, non-harsh visual style instead of a plain white document
- surface the recommendation near the end in a dedicated section

A reader should understand the page in 3-5 minutes.

### 9. Validate before finishing

Check that the page:

- answers the core project/task questions
- uses repository evidence instead of generic filler
- stays simple enough to maintain
- names the important files and boundaries accurately
- distinguishes evidence-backed facts from interpretation where that distinction matters
- includes a concrete recommended solution or next step
- includes a Mermaid `graph TB` diagram for the main architecture
- includes the structure tree in both Mermaid and plain-text file-tree form
- includes the technology tree in both Mermaid and plain-text hierarchy form when relevant
- includes a source-of-truth / evidence map
- includes boundaries and invariants
- includes a safe-modification guide
- includes verification commands
- includes a common anti-patterns section when architectural understanding would benefit from it
- uses Chinese by default unless English was explicitly requested
- uses ASCII-only file and directory names
- lands under `_learn_web/` unless the user requested another destination
- does not depend on CDN Mermaid assets when offline-safe output is expected

If you created a static page, inspect the generated HTML and verify the placeholders were replaced.
Also verify the generated page includes a local Mermaid asset path such as `./assets/mermaid.min.js`.

If you updated an existing page, also verify that:

- previously useful sections were preserved unless intentionally superseded
- the new material is integrated into the same reader journey instead of pasted as an isolated appendix
- the page path stayed stable when the subject remained the same

## Resources

### scripts/bootstrap_explainer_page.py

Use this script to copy the minimal single-file template into a target folder and prefill localized placeholders.

### references/repo-scan-checklist.md

Read this file when you need a fast order of operations for understanding an unfamiliar codebase or task.

### references/page-outline.md

Read this file when you need a default page structure or section prompts.

### assets/minimal-explainer-site/index.html

Use this self-contained template when you want the fastest path to a readable explainer webpage. It already includes Mermaid runtime wiring that points to a local bundled script so `graph TB` blocks can render offline.

### assets/vendor/mermaid.min.js

This bundled Mermaid runtime is copied into each generated page's local `assets/` directory so the output stays fully offline-capable.
