# Repo scan checklist

Use this order unless the task already points to a narrower surface.

## 1. Confirm the task target
- Read the user request, issue text, logs, or diff first.
- Determine whether the page should explain the whole project or only one subsystem.

## 2. Identify the stack
- Read `package.json`, lockfiles, and build config.
- Identify the frontend/runtime framework, language, bundler, and test tools.
- Note whether the repo is monolithic or layered.

## 3. Locate the real entry points
- Find app entry files, route roots, main services, IPC bridges, server startup, or workflow coordinators.
- Prefer source-of-truth directories over generated output.

## 4. Trace the relevant flow
- Follow the smallest end-to-end path related to the task.
- Capture the important transitions: input -> state/service -> integration -> output.

## 5. Extract the developer-facing knowledge
- Capture the concepts a future developer must know to modify this area safely.
- Note architecture boundaries, invariants, conventions, and common pitfalls.

## 6. Build evidence-backed recommendations
- Tie each recommendation to observed files, flows, or constraints.
- Distinguish facts, likely interpretation, and open questions.
