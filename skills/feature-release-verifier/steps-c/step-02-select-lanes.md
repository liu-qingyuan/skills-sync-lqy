---
name: step-02-select-lanes
description: Select validation matrix and package lanes
nextStepFile: ./step-03-run-workers.md
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/progress.md"
---

# Step 2: Select Validation Matrix

## Goal

Choose the correct verification tiers and package lanes.

## Mandatory sequence

1. Use the brief from Step 1.
2. Apply lane-selection rules from:
   - `references/02-lane-selection.md`
3. Output a lane plan that includes:
   - tiers to run
   - package lanes to run
   - which lanes are **required**
   - which lanes are **optional**
   - why each lane is included
   - why each skipped lane is skipped
   - which lane should provide the first useful debugging evidence
4. Save progress to `{outputFile}`.

Load next step: `{nextStepFile}`
