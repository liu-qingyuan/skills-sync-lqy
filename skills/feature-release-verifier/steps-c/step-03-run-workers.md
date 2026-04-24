---
name: step-03-run-workers
description: Resolve execution mode and run verification workers
nextStepFile: ./step-04-generate-report.md
outputFile: "{project-root}/_bmad-output/test-artifacts/feature-release-verifier/{feature-slug}/progress.md"
---

# Step 3: Run Verification Workers

## Goal

Resolve execution mode, run selected workers, and collect structured worker outputs.

## Mandatory sequence

1. Resolve execution mode:
   - `auto`
   - `subagent`
   - `agent-team`
   - `sequential`
   In `--headless` mode, default to `sequential` unless a stronger mode is explicitly requested and supported.
2. Always run **baseline-quality** first:
   - `npm run typecheck`
   - `npm run lint`
   - `npm run build` when required by the selected matrix
3. If baseline fails, record a `FAIL` worker result.
   - If the brief says Playwright evidence is the first useful debugging layer, still allow the primary Playwright lane to run unless the failure makes that impossible.
   - Record why a lane was skipped versus blocked.
4. Dispatch selected lanes using `references/03-worker-dispatch.md`.
5. Each worker must return:
   - lane
   - commands run
   - status
   - required (`true | false`)
   - blockers
   - warnings
   - skip reason (if skipped)
   - artifacts
   - evidence
   - failing test title (when applicable)
   - primary failure signal
   - artifact paths
   - bug location hint
   - rerun command
   - sensitivity / redaction note
6. Save worker outputs and progress to `{outputFile}`.

Load next step: `{nextStepFile}`
