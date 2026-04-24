---
name: step-02-apply-edit
description: Apply an edit to an existing verifier workflow or report
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/edit-progress.md"
---

# Apply Edit

## Goal

Apply the requested change while preserving the verifier’s core model:

- Playwright-first evidence
- lane/tier separation
- deterministic release gate

## Mandatory sequence

1. Apply only the requested change.
2. Re-check path and structure rules.
3. Summarize what changed and what stayed intentionally unchanged.

