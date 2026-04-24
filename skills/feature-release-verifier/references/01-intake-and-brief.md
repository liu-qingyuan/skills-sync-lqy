# Stage 01 — Intake and Verification Brief

## Goal

Turn the user's request into a concrete verification brief.

## Required inputs

- feature name
- feature scope (changed files, directories, or feature slug)
- risk level (`low | medium | high`)
- packaged requirement (`none | local | remote | both`)

## Helpful additional inputs

- runtime target (`none | openclaw | hermes | both`)
- impact tags (`renderer-ui`, `renderer-service`, `preload`, `main`, `packaging`, `runtime`, `auth-session`)
- acceptance keywords (`能发消息`, `能启动`, `打包后可打开`)
- preferred evidence depth (`minimal | standard | rich`)
  - `minimal` = command result only
  - `standard` = Playwright screenshot + trace on failure
  - `rich` = screenshot + trace + video + error-context + packaged inspect when applicable

## Output

Write a brief that includes:

- feature
- scope
- risk
- requested packaged depth
- requested runtime depth
- likely validation tiers
- expected evidence level

## Playwright-first note

Unless the feature is purely structural or packaging-only, default to a Playwright-first mindset:

- first prove behavior with Playwright,
- then use packaged smoke to confirm the packaged app carries the correct behavior,
- then use real-runtime only when real service/runtime behavior must be proven.

If the user is vague and headless mode is off, ask only the smallest set of questions needed to classify the matrix.
