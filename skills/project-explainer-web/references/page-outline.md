# Default page outline

Use the smallest subset that fits the task, but keep the two tree sections mandatory.

Default to Mermaid `graph TB` for the structure/technology tree views when relationships are easier to understand visually. For the structure tree, always pair the Mermaid diagram with a plain-text file/tree block so the reader can also see the concrete filesystem shape.
When generating a static page, assume the diagram must still work offline from a local file path.

## 1. Hero summary
- Project/task name
- One-sentence purpose
- One-sentence current objective
- Language marker when the page is not in the repository default language

## 2. Why this matters
- What problem is being solved
- Who benefits or what workflow improves

## 3. Affected structure tree (mandatory)
- Show which parts are involved
- Show each part's concrete function
- Include a Mermaid `graph TB` with top-down grouping
- Also include a plain-text file/tree block that mirrors the concrete structure
- Do not collapse everything into a flat bullet dump

## 4. Architecture at a glance
- Relevant layers or modules
- Short bullets for responsibilities
- Keep it visual with cards or grouped boxes when helpful

## 5. How the flow works
- Step-by-step path through the system
- Focus on the path touched by the current task

## 6. Source of truth / evidence map
- Show which files, docs, logs, commands, or diffs support the explanation
- Distinguish direct evidence from interpretation when useful
- Call out open questions instead of hiding uncertainty

## 7. Key files to read first
- File path
- Why it matters
- What a developer should look for inside it

## 8. Related technology tree (mandatory when technology is involved)
- Frameworks, runtimes, protocols, parameters, concepts, tradeoffs
- Sort them structurally so the reader can see what is involved
- Show dependency or influence relationships when useful
- Include a Mermaid `graph TB` when the technical relationships are important to the decision
- Also include a plain-text technology hierarchy or layered outline

## 9. Boundaries and invariants
- Show ownership boundaries, layering rules, and responsibilities
- State what future modifiers should preserve
- Mention anti-patterns or shortcuts that would damage the design

## 10. How to modify this safely
- State where a developer should start
- Indicate the likely owning files or layers
- Mention what to change first and what should only change secondarily

## 11. Verification commands
- Give the most useful commands for understanding or validating the area
- Explain what each command proves
- Mark commands that are optional, expensive, or environment-sensitive

## 12. Common anti-patterns
- Name the most tempting mistakes or shortcuts
- Explain why they are attractive but harmful
- Point to the safer alternative, boundary, or guardrail

## 13. Principles and background knowledge
- Concepts the reader must understand first
- Domain rules, invariants, or framework-specific behavior

## 14. Constraints and risks
- Technical constraints
- Product constraints
- Current unknowns or decisions that could change the solution

## 15. Recommended solution
- Preferred next step
- Why it is the best tradeoff
- Alternatives rejected or deferred

## 16. Next actions
- Concrete follow-up steps for implementation or investigation

## Scope emphasis

### Project mode
- Emphasize major layers, ownership, subsystem boundaries, and reading order
- Explain why the architecture is shaped this way over time
- Prefer recommendations about long-lived structure, not just the next local patch

### Task mode
- Emphasize the exact flow being changed, the touched files, and the safe modification path
- Prefer recommendations about the current decision, verification plan, and concrete next implementation steps
