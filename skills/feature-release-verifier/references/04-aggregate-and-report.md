# Stage 04 — Aggregate and Report

## Goal

Convert worker outputs into one release decision.

## Machine summary

Write:

- `{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/summary.json`

Include:

- feature
- scope
- risk
- tiers run
- package lanes run
- blockers
- warnings
- evidence
- required lane statuses
- final gate

## Human report

Write:

- `{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/release-verification-report.md`

Include:

- verification brief
- selected matrix
- commands executed
- lane-by-lane results
- blockers
- concerns
- skipped lanes and why
- artifact paths
- Playwright evidence summary:
  - screenshot paths
  - trace paths
  - error-context paths
  - first failing selector / assertion
- final release decision

## Release gate rules

- Any blocker => `FAIL`
- No blockers, but one or more concerns/warnings => `PASS-WITH-CONCERNS`
- All required lanes pass => `PASS`

## Final answer contract

The final response to the user should explicitly separate:

- source-level verification status
- real-runtime verification status
- packaged verification status
- remote packaged verification status

## Required-lane rule

If a lane was marked `required: true` and its final status is `SKIP`, treat that as:

- `FAIL` by default, or
- `PASS-WITH-CONCERNS` only when the report records an explicit accepted waiver and a manual verification path

If the user asked “打包后是否可用”, answer that directly and explicitly.

## Bug localization summary

If any Playwright lane failed, the final report should include a short section:

- **Likely first break point**
- **Strongest artifact to inspect next**
- **Whether the failure appears source-level, runtime-level, or packaged-only**
