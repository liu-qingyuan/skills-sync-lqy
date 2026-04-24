---
name: step-01-load-context
description: Load feature context and produce a verification brief
nextStepFile: ./step-02-select-lanes.md
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/progress.md"
---

# Step 1: Load Context & Verification Brief

## Goal

Turn the user's request into a precise verification brief.

## Mandatory sequence

1. Read:
   - `{project-root}/_bmad-output/project-context.md`
   - `playwright.config.ts`
   - `package.json`
   - `tests/TESTING_KB.md`
2. Capture:
   - feature name
   - feature scope
   - risk level
   - runtime target
   - packaged requirement
   - impact tags
   - acceptance keywords
   - evidence depth (`minimal | standard | rich`)
   - whether the run is headless
3. Produce a brief that states:
   - what is being verified
   - what “usable” means
   - what “packaged usable” means
   - what acceptance keywords must be proven
   - what impact tags imply for lane eligibility
   - likely validation tiers
   - likely required lanes vs optional lanes
4. Save progress to `{outputFile}`.

Load next step: `{nextStepFile}`
