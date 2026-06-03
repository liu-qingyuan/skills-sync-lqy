# Matt Pocock skills 外部链接

此文件只保存外部仓库链接，方便人类阅读后自行跳转安装。

## 重要约束

- 除 README 明确列出的已选择镜像外，本仓库不镜像、不安装、不同步 `mattpocock/skills` 内的 skill 文件。当前已选择镜像：`skills/handoff`。
- 不要在本仓库 `skills/` 目录下创建其他 Matt Pocock skills 的副本、symlink、submodule 或占位目录。
- Codex/AI Agent 读取本仓库时，必须把本页当作文档链接清单，而不是可安装 skill 清单。
- 本页不提供未镜像 skills 的本仓库安装命令；若要使用其他 Matt Pocock skills，请先打开 upstream README，自行选择安装方式。

## Upstream

- Repository: https://github.com/mattpocock/skills
- README: https://github.com/mattpocock/skills/blob/main/README.md
- Source commit inspected: `aaf2453fbdfe7a15c07f11d861224f34ab4b53cb`
- Skills directory: https://github.com/mattpocock/skills/tree/main/skills
- skills.sh entry: https://skills.sh/mattpocock/skills

除 `skills/handoff` 已作为本仓库可安装 skill 提供外，请从 upstream README 或 skills.sh 页面进入其他 skills 的安装流程；不要让本仓库代装其他 Matt Pocock skills。

## Skill 链接清单

### Engineering

- [diagnose](https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnose/SKILL.md) — Disciplined diagnosis loop for hard bugs and performance regressions. Reproduce → minimise → hypothesise → instrument → fix → regression-test. Use when user says "diagnose this" / "debug this", reports a bug, says something is broken/throwing/failing, or describes a performance regression.
- [grill-with-docs](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md) — Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates documentation (CONTEXT.md, ADRs) inline as decisions crystallise. Use when user wants to stress-test a plan against their project's language and documented decisions.
- [improve-codebase-architecture](https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md) — Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable.
- [prototype](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md) — Build a throwaway prototype to flesh out a design before committing to it. Routes between two branches — a runnable terminal app for state/business-logic questions, or several radically different UI variations toggleable from one route. Use when the user wants to prototype, sanity-check a data model or state machine, mock up a UI, explore design options, or says "prototype this", "let me play with it", "try a few designs".
- [setup-matt-pocock-skills](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md) — Sets up an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/` so the engineering skills know this repo's issue tracker (GitHub or local markdown), triage label vocabulary, and domain doc layout. Run before first use of `to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, or `zoom-out` — or if those skills appear to be missing context about the issue tracker, triage labels, or domain docs.
- [tdd](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md) — Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development.
- [to-issues](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-issues/SKILL.md) — Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
- [to-prd](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-prd/SKILL.md) — Turn the current conversation context into a PRD and publish it to the project issue tracker. Use when user wants to create a PRD from the current context.
- [triage](https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md) — Triage issues through a state machine driven by triage roles. Use when user wants to create an issue, triage issues, review incoming bugs or feature requests, prepare issues for an AFK agent, or manage issue workflow.
- [zoom-out](https://github.com/mattpocock/skills/blob/main/skills/engineering/zoom-out/SKILL.md) — Tell the agent to zoom out and give broader context or a higher-level perspective. Use when you're unfamiliar with a section of code or need to understand how it fits into the bigger picture.

### Productivity

- [caveman](https://github.com/mattpocock/skills/blob/main/skills/productivity/caveman/SKILL.md) — Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler, articles, and pleasantries while keeping full technical accuracy. Use when user says "caveman mode", "talk like caveman", "use caveman", "less tokens", "be brief", or invokes /caveman.
- [grill-me](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md) — Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
- [handoff](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md) — Compact the current conversation into a handoff document for another agent to pick up.
- [write-a-skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/write-a-skill/SKILL.md) — Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, or build a new skill.

### Misc

- [git-guardrails-claude-code](https://github.com/mattpocock/skills/blob/main/skills/misc/git-guardrails-claude-code/SKILL.md) — Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code.
- [migrate-to-shoehorn](https://github.com/mattpocock/skills/blob/main/skills/misc/migrate-to-shoehorn/SKILL.md) — Migrate test files from `as` type assertions to @total-typescript/shoehorn. Use when user mentions shoehorn, wants to replace `as` in tests, or needs partial test data.
- [scaffold-exercises](https://github.com/mattpocock/skills/blob/main/skills/misc/scaffold-exercises/SKILL.md) — Create exercise directory structures with sections, problems, solutions, and explainers that pass linting. Use when user wants to scaffold exercises, create exercise stubs, or set up a new course section.
- [setup-pre-commit](https://github.com/mattpocock/skills/blob/main/skills/misc/setup-pre-commit/SKILL.md) — Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing.

### Personal

- [edit-article](https://github.com/mattpocock/skills/blob/main/skills/personal/edit-article/SKILL.md) — Edit and improve articles by restructuring sections, improving clarity, and tightening prose. Use when user wants to edit, revise, or improve an article draft.
- [obsidian-vault](https://github.com/mattpocock/skills/blob/main/skills/personal/obsidian-vault/SKILL.md) — Search, create, and manage notes in the Obsidian vault with wikilinks and index notes. Use when user wants to find, create, or organize notes in Obsidian.

### In progress

- [review](https://github.com/mattpocock/skills/blob/main/skills/in-progress/review/SKILL.md) — Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/PRD asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
- [teach](https://github.com/mattpocock/skills/blob/main/skills/in-progress/teach/SKILL.md) — Teach the user a new skill or concept, within this workspace.
- [writing-beats](https://github.com/mattpocock/skills/blob/main/skills/in-progress/writing-beats/SKILL.md) — Shape an article as a journey of beats, choose-your-own-adventure style. The user picks a starting beat from the raw material, you write only that beat, then offer options for where to pivot next, beat by beat, until the article reaches a natural end. Use when the user has raw material and wants to assemble it as a narrative rather than an argument.
- [writing-fragments](https://github.com/mattpocock/skills/blob/main/skills/in-progress/writing-fragments/SKILL.md) — Grilling session that mines the user for fragments — heterogeneous nuggets of writing (claims, vignettes, sharp sentences, half-thoughts) — and appends them to a single document as raw material for a future article. Use when the user wants to develop ideas before imposing structure, or mentions "fragments", "ideate", or "raw material" for writing.
- [writing-shape](https://github.com/mattpocock/skills/blob/main/skills/in-progress/writing-shape/SKILL.md) — Take a markdown file of raw material and shape it into an article through a conversational session — drafting candidate openings, growing the piece paragraph by paragraph, arguing about format (lists, tables, callouts, quotes) at each step. Use when the user has a pile of notes, fragments, or a rough draft and wants help turning it into something publishable.

### Deprecated

- [design-an-interface](https://github.com/mattpocock/skills/blob/main/skills/deprecated/design-an-interface/SKILL.md) — Generate multiple radically different interface designs for a module using parallel sub-agents. Use when user wants to design an API, explore interface options, compare module shapes, or mentions "design it twice".
- [qa](https://github.com/mattpocock/skills/blob/main/skills/deprecated/qa/SKILL.md) — Interactive QA session where user reports bugs or issues conversationally, and the agent files GitHub issues. Explores the codebase in the background for context and domain language. Use when user wants to report bugs, do QA, file issues conversationally, or mentions "QA session".
- [request-refactor-plan](https://github.com/mattpocock/skills/blob/main/skills/deprecated/request-refactor-plan/SKILL.md) — Create a detailed refactor plan with tiny commits via user interview, then file it as a GitHub issue. Use when user wants to plan a refactor, create a refactoring RFC, or break a refactor into safe incremental steps.
- [ubiquitous-language](https://github.com/mattpocock/skills/blob/main/skills/deprecated/ubiquitous-language/SKILL.md) — Extract a DDD-style ubiquitous language glossary from the current conversation, flagging ambiguities and proposing canonical terms. Saves to UBIQUITOUS_LANGUAGE.md. Use when user wants to define domain terms, build a glossary, harden terminology, create a ubiquitous language, or mentions "domain model" or "DDD".
