---
name: step-04-generate-report
description: Aggregate worker results and generate final release report
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/release-verification-report.md"
---

# Step 4: Aggregate and Report

## Goal

Aggregate worker results into:

- `summary.json`
- `release-verification-report.md`

## Mandatory sequence

1. Read all worker outputs.
2. Apply deterministic release gate rules:
   - blocker => `FAIL`
   - required lane skipped without accepted waiver => `FAIL`
   - no blockers, but warnings/concerns or waived required lane => `PASS-WITH-CONCERNS`
   - all required lanes pass => `PASS`
3. Write machine summary.
4. Write human report using:
   - `references/release-verification-template.md`
   - `references/checklist.md`
5. Ensure the report explicitly separates:
   - source-level verification
   - real-runtime verification
   - packaged verification
   - remote packaged verification
6. If Playwright failed, include:
   - failing test title
   - failing selector/assertion
   - screenshot/trace/error-context paths
   - strongest artifact to inspect next
   - likely first break point
7. Build an artifact manifest that records:
   - artifact path
   - existence confirmed or missing
   - source lane
   - sensitivity/redaction notes
   - rerun command
8. If a lane is skipped, explicitly state:
   - whether it was required
   - why it was skipped
   - what manual verification is still needed

This is the final create-mode step.
