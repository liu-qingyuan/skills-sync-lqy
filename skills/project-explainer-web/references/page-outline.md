# Default page outline

Use the smallest subset that fits the task, but keep the required diagram and handoff sections unless the user explicitly asks for a narrower text-only artifact.

Default to Mermaid `graph TB` for architecture, structure/hierarchy, and technology tree views. Use Mermaid `sequenceDiagram` for interactions over time. Static pages must work offline from a local file path through `./assets/mermaid.min.js`.

## Stable section contract

Use stable section comments and DOM anchors so future updates can patch sections instead of rebuilding the page:

- `<!-- section: <key> -->` / `<!-- endsection: <key> -->`
- `id="section-<key>"`
- `data-section="<key>"`

Unconditional section keys: `hero`, `summary`, `why`, `boundaries`, `runtime-principles`, `structure`, `architecture`, `sequence`, `flow`, `evidence`, `key-files`, `ai-blind-spots`, `handoff-to-ai`, `debugging-guide`, `knowledge`, `safe-change`, `verification-commands`, `anti-patterns`, `risks`, `recommendation`, `next-actions`.

Conditional section key: `technology-tree` is required only when technology is materially involved. The default static scaffold includes a `technology-tree` placeholder so new pages are easy to fill; during the first real content pass, either fill it with the relevant stack or explicitly mark it not applicable / remove it cleanly when technology is not material.

## 1. Hero summary
- Project/task name
- One-sentence purpose
- One-sentence current objective
- What the reader should understand after 3-5 minutes

## 2. Why this matters
- What problem is being solved
- Who benefits or what workflow improves
- Why this explanation helps humans brief AI safely

## 3. Boundaries and invariants
- Ownership and layer boundaries
- Responsibilities that must not be mixed casually
- Invariants future humans and AI agents must preserve
- Tempting shortcuts that would damage the design

## 4. Runtime principles
- Entry points, process/runtime/hook/route/job model, or event loop involved
- State and control-flow model
- Normal path, failure path, retry/rollback path
- Logs, tests, or probes that prove runtime behavior

## 5. Affected structure tree (mandatory)
- Show which parts are involved
- Show each part's concrete function
- Include a Mermaid `graph TB` with top-down grouping
- Also include a plain-text file/tree block that mirrors the concrete structure
- Do not collapse everything into a flat bullet dump

## 6. Architecture at a glance (mandatory)
- Include a Mermaid `graph TB` architecture diagram
- Show major layers, ownership, dependencies, and integration boundaries
- Keep node labels short and human-readable

## 7. Sequence / interaction view (mandatory)
- Include a Mermaid `sequenceDiagram`
- Show the smallest useful interaction over time: user/AI/request/event -> entry point -> owning logic -> state/integration -> output/evidence
- Include validation, decision, retry, or failure points when they matter

## 8. Flow explanation
- Step-by-step path through the system
- Focus on the path touched by the current task or the main project path
- Tie the prose back to the architecture and sequence diagrams

## 9. Source of truth / evidence map
- Files, docs, logs, commands, diffs, screenshots, or traces supporting the explanation
- Direct facts vs reasoned interpretation
- Open questions that still require confirmation

## 10. Key files to read first
- File path
- Why it matters
- What a developer or AI agent should inspect inside it first

## 11. Related technology tree (conditional)
- Required when frameworks, runtimes, protocols, parameters, or technical tradeoffs materially affect the explanation
- Include both Mermaid `graph TB` and a plain-text hierarchy
- Explain what each technology point means and which dependency/tradeoff matters

## 12. AI blind spots / uncertainty map
- What AI cannot safely infer from static code alone
- Runtime state, credentials, production constraints, user intent, logs, or external systems that need human confirmation
- What evidence is missing before architecture design, bug fixing, or risky refactoring

## 13. Handoff to AI
- Minimal context packet: objective, scope in/out, boundaries, source-of-truth files, expected evidence, stop condition
- What AI may edit first vs what requires human confirmation
- How to ask AI for design, debugging, implementation, or review without breaking boundaries

## 14. Debugging guide
- Fastest high-truth probes and logs
- How to move from symptom -> owner layer -> root cause -> fix -> verification
- Common failure modes and where to start reading


## 15. Principles and background knowledge
- Concepts the reader must understand before changing this area
- Domain rules, invariants, or framework-specific behavior
- How these principles affect architecture, debugging, and AI handoff

## 16. How to modify this safely
- Where a developer should start
- Likely owning files/layers
- What to change first and what should only change as a consequence

## 17. Verification commands
- Most useful commands for understanding or validating the area
- What each command proves
- Which commands are optional, expensive, or environment-sensitive

## 18. Common anti-patterns
- Tempting mistakes or shortcuts
- Why they look convenient but are harmful
- Safer alternative or guardrail

## 19. Constraints and risks
- Technical/product constraints
- Unknowns or decisions that could change the solution
- Rollback or escalation conditions when relevant

## 20. Recommended solution
- Preferred next step
- Why it is the best tradeoff
- Alternatives rejected or deferred

## 21. Next actions
- Concrete follow-up steps for implementation, validation, or investigation

## Mermaid syntax guardrails

- Avoid node labels with `number. space`; prefer `Step 1 - Name`, `① Name`, or no numbering.
- Use IDs for nodes and subgraphs; do not reference display labels directly.
- Use `subgraph core["Core Layer"]` when display names contain spaces.
- Keep node labels short and avoid emoji.
- Prefer `graph TB` for architecture/structure/technology and `sequenceDiagram` for interactions over time.

## Scope emphasis

### Project mode
- Emphasize major layers, ownership, subsystem boundaries, runtime principles, and reading order
- Explain why the architecture is shaped this way over time
- Include AI handoff guidance for future architecture/design/debug work

### Task mode
- Emphasize the exact flow being changed, touched files, safe modification path, and task-specific verification
- Include AI blind spots and debugging probes for this change
