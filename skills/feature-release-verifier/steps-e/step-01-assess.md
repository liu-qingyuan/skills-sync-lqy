---
name: step-01-assess
description: Assess what needs to be edited in an existing verifier workflow or report
nextStepFile: ./step-02-apply-edit.md
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/edit-progress.md"
---

# Edit Assessment

## Goal

Determine whether the requested edit affects:

- workflow logic
- lane rules
- report structure
- output clarity only

## Mandatory sequence

1. Read the existing artifact/workflow files in scope.
2. Summarize the requested change and its blast radius.
3. Record whether the change is:
   - narrow wording change
   - structural workflow change
   - lane matrix change
   - output contract change

Load next step: `{nextStepFile}`

