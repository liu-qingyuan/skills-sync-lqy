# Stage 02 — Validation Matrix Selection

## Goal

Map the feature into the correct test tiers and package lanes.

## Core distinction

- **Package lanes** = where/how to build or launch
- **Test tiers** = what evidence proves the feature is usable

## Default rules

### Default priority order

When a feature has any user-facing behavior, prefer this order:

1. `mock-ui`
2. `real-runtime` when runtime truth matters
3. `packaged-smoke` when package/startup/bundle truth matters

This keeps feature diagnosis Playwright-first and makes failures easier to localize.

### Low risk

- baseline-quality
- one matching mock-ui lane

### Medium risk

- baseline-quality
- matching mock-ui lane(s)
- build

### High risk

- baseline-quality
- matching mock-ui lane(s)
- build
- real-runtime when runtime/service behavior is affected
- packaged-smoke when main/preload/packaging/startup is affected

## Runtime rules

### Use `mock-ui` when:

- the question is about CTA
- routing
- state transitions
- task creation
- selector behavior
- non-runtime renderer logic
- the fastest way to localize the bug is a Playwright failure with screenshot/trace evidence

### Use `real-runtime` when:

- the feature must prove real send/receive behavior
- the feature installs or starts real agent runtime
- auth/session/runtime state is part of acceptance

### Use `packaged-smoke` when:

- `src/main`
- `src/preload`
- packaging scripts
- package resources
- startup chain
- packaged bundle correctness
are in scope

### Bug-localization rule

If a feature can fail in both source-level UI and packaged behavior:

- run the Playwright lane first to localize the feature regression,
- then run packaged-smoke to determine whether the packaged app is also affected.

Do not start from packaged-only validation when a cheaper Playwright lane can explain the bug location faster.

### Use `remote-lane` when:

- user explicitly asks for remote verification
- mac16/Mac mini behavior matters
- machine-specific deployment/signing differences are relevant

## Output

Produce a lane plan with:

- tiers to run
- package lanes to run
- why each lane is included
- why excluded lanes were skipped
- which lane is expected to provide the first useful debugging evidence
