---
name: step-01b-resume
description: Resume an interrupted verification run
nextStepFile: ./step-02-select-lanes.md
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/progress.md"
---

# Step 1B: Resume

## Goal

Resume from the latest saved verification brief and lane plan.

## Mandatory sequence

1. Read `{outputFile}`.
2. Recover:
   - verification brief
   - selected lanes
   - already completed lanes
   - blockers / warnings so far
3. If required context is missing, rebuild the brief before proceeding.

Load next step: `{nextStepFile}`

