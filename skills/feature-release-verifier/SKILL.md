---
name: feature-release-verifier
description: Verify whether a feature is ready to release, whether the packaged app is usable, and what evidence supports the release decision. Use when the user asks to verify a new feature, check release readiness, confirm packaged-app usability, validate launch/startup after packaging, or says things like '验证新功能是否可用', '验证这个功能能不能发布', '检查打包后是否可用', or 'run feature release verifier'.
---

# feature-release-verifier

## Overview

This workflow verifies whether a newly implemented feature is ready to ship by choosing the right validation matrix for the feature, executing the right lanes, and aggregating the evidence into a release decision. Act as a release-readiness architect for cpilot-web, using Playwright as the primary evidence collector for feature behavior, and using the repository's existing mock-ui, real-runtime, and packaged-smoke lanes instead of inventing one-off validation paths. Your output is a machine-readable release summary plus a human-readable release verification report that says whether the feature is usable and whether the packaged app is usable.

## On Activation

Load config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` if present. Use sensible defaults if config is missing.

Load `{project-root}/_bmad-output/project-context.md` as the foundational reference for:

- test architecture,
- package lanes,
- runtime tiers,
- repository validation conventions.

When available, also read:

- `playwright.config.ts`
- `package.json`
- `tests/TESTING_KB.md`

This workflow supports `--headless` for non-interactive execution.

In headless mode:

- do not ask mode-selection questions,
- default to **Create**,
- infer the smallest sufficient verification matrix from the provided feature context,
- record any missing runtime/package prerequisites as `SKIP` or `FAIL` with explicit reasons.

## Workflow Shape

This is a multi-mode Codex workflow:

- **Create** — run a new verification flow
- **Resume** — continue an interrupted verification run
- **Validate** — review an existing verification artifact/checklist
- **Edit** — revise an existing workflow/report

Start with `references/workflow.md`.

## What this workflow must do

- Identify the feature scope and risk level
- Select the correct validation matrix from:
  - baseline-quality
  - mock-ui
  - real-runtime
  - packaged-smoke
  - remote package lane
- Reuse existing repository commands and test files whenever possible
- Prefer Playwright evidence first for feature behavior:
  - screenshots,
  - traces,
  - videos,
  - error-context,
  - failing selector/state evidence
- For Electron/real-runtime assertions, prefer **user-visible terminal states** (rendered reply, explicit failure text, button-state recovery, status badge changes) over brittle internal monkeypatching.
- Do not rely on monkeypatching `window.electronAPI` objects in renderer tests; Electron preload surfaces may be frozen/non-writable.
- Do not use fixed sleeps as correctness checks. Use condition-based waits tied to DOM, event, network, or persisted-state changes.
- Produce:
  - `{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/summary.json`
  - `{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/release-verification-report.md`

## Non-negotiable rules

- Do not invent new verification lanes if the repository already has one
- Do not treat a failing Playwright assertion as “just a flaky UI issue” without first collecting screenshot/trace/error-context evidence
- When a Playwright lane fails, always capture enough evidence to answer:
  - what the page rendered,
  - what selector failed,
  - what state transition did not happen,
  - what artifact path contains the failure evidence
- Do not treat packaged validation as a substitute for real-runtime validation
- Do not treat real-runtime validation as required when the environment is not opt-in ready; record `SKIP` with reason instead
- Do not duplicate business E2E logic inside packaging scripts
- Package lanes answer **where/how to build or launch**
- Test tiers answer **what evidence proves the feature is usable**

## Execution mode

Support:

- `auto`
- `subagent`
- `agent-team`
- `sequential`

Resolve execution mode before launching workers. If runtime capability probing is enabled, use it to choose the best supported mode. If probing is disabled, honor the requested mode strictly.

## Worker model

Workers should be split by verification dimension, not by arbitrary file count:

- **baseline-quality**
- **mock-ui**
- **real-runtime**
- **packaged-smoke**
- **remote-lane**

Every worker should output the same shape:

- lane
- status (`PASS` / `FAIL` / `SKIP`)
- required (`true | false`)
- blockers
- warnings
- skip_reason (when status is `SKIP`)
- artifacts
- evidence
- commands
- failing_test_title
- primary_failure_signal
- artifact_paths
- bug_location_hint
- rerun_command
- sensitivity
- next action (if needed)

## Completion contract

A complete run must end with:

- one machine-readable summary
- one human-readable report
- a release decision:
  - `PASS`
  - `PASS-WITH-CONCERNS`
  - `FAIL`

If the user asks for the packaged decision specifically, the report must state whether:

- the source build is verified,
- the packaged app is verified,
- the remote packaged lane was run or intentionally skipped.
