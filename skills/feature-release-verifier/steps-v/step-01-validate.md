---
name: step-01-validate
description: Validate an existing release verification report
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/validation-report.md"
---

# Validate Existing Output

## Goal

Validate an existing `feature-release-verifier` run against `references/checklist.md`.

## Mandatory sequence

1. Read the existing summary/report artifacts.
2. Validate them against `references/checklist.md`.
3. Report:
   - missing fields
   - inconsistent lane decisions
   - missing Playwright artifacts
   - missing artifact existence/redaction metadata
   - missing KB-derived safeguards from `tests/TESTING_KB.md`
   - required lanes that were skipped without explicit waiver
   - ambiguous release decision
4. Write the validation result to `{outputFile}`.
