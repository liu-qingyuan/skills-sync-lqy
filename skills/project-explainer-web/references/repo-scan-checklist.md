# Repo scan checklist

Use this order unless the task already points to a narrower surface.

## 1. Confirm the task target
- Read the user request, issue text, logs, screenshots, traces, or diff first.
- Determine whether the page should explain the whole project, one subsystem, or one task.
- Capture what the reader wants to do after reading: understand, brief AI, design architecture, debug, implement, or review.

## 2. Identify the stack
- Read manifests, lockfiles, build config, and top-level docs.
- Identify frontend/backend/runtime framework, language, bundler, test tools, and deployment/runtime assumptions.
- Note whether the repo is monolithic, layered, plugin-based, service-based, or script/tooling-oriented.

## 3. Locate the real entry points
- Find app entry files, route roots, CLI commands, main services, IPC bridges, server startup, hooks, jobs, or workflow coordinators.
- Prefer source-of-truth directories over generated output.
- Record which entry point a human or AI should inspect first.

## 4. Map boundaries and ownership
- Identify major layers/modules and what each owns.
- Record cross-layer calls, shared state, generated files, config surfaces, and external integrations.
- Mark boundaries future modifiers should not cross casually.

## 5. Trace the relevant sequence
- Follow the smallest end-to-end path related to the task.
- Capture actors/components in order: input -> entry point -> owning logic -> state/service/integration -> output/evidence.
- Note decision points, retries, failure paths, rollback paths, and verification points.

## 6. Extract runtime principles
- Summarize the process/runtime/event model and state model.
- Identify which logs, commands, or tests prove the runtime behavior.
- Separate normal behavior from failure behavior.

## 7. Identify AI blind spots
- List facts AI cannot safely infer without live checks, logs, credentials, production state, or user decisions.
- Identify assumptions that could cause an AI to edit the wrong layer or overfit a local symptom.
- Turn each blind spot into a required evidence check or human-confirmation note.

## 8. Build the AI handoff packet
- Objective and non-goals
- Source-of-truth files/logs/commands
- Boundaries and invariants
- Safe first edit location
- Required verification evidence and stop condition

## 9. Build evidence-backed recommendations
- Tie each recommendation to observed files, flows, logs, or constraints.
- Distinguish facts, likely interpretation, and open questions.
- Prefer the smallest safe next change path and clear rollback/escalation rules.
