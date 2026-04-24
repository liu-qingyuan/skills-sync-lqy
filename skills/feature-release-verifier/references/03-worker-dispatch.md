# Stage 03 — Worker Dispatch

## Goal

Run the selected verification lanes using the best supported execution mode.

## Baseline-quality commands

Always prefer repository-native commands:

```bash
npm run typecheck
npm run lint
```

Run `npm run build` when the touched surface or risk requires it.

## Mock-ui lane examples

Use Playwright as the primary feature-debugging surface. For every Playwright lane:

- keep screenshots enabled on failure,
- keep traces enabled on failure,
- keep error-context and report artifacts,
- record the artifact paths in the worker result,
- summarize the first failing selector/state transition in one sentence.
- synchronize via deterministic signals only: visible text, terminal button state, event/network completion, or persisted-state change.
- do **not** use `waitForTimeout(...)` as a success criterion.
- when testing Electron preload APIs, assume `window.electronAPI` may be frozen; prefer direct subscription or black-box assertions over method monkeypatching.
- for streaming/agent UIs, treat these as strongest end-state proofs:
  - assistant text visibly rendered,
  - explicit failure text rendered,
  - stop button disappears / send button returns,
  - runtime badge/status changes.

### OpenClaw

```bash
npx playwright test tests/e2e/openclaw.spec.ts --project=electron
```

### Hermes

```bash
npx playwright test tests/e2e/hermes.spec.ts --project=electron
npx playwright test tests/e2e/hermes-install-flow.spec.ts --project=chromium
```

## Real-runtime lane examples

### OpenClaw

```bash
OPENCLAW_REAL_RUNTIME=1 OPENCLAW_REAL_CLEANUP=on-success \
npx playwright test tests/e2e/openclaw-real-runtime.spec.ts --project=electron-real-runtime --workers=1
```

### Hermes

```bash
HERMES_REAL_RUNTIME=1 \
npx playwright test tests/e2e/hermes-real-runtime.spec.ts --project=electron-real-runtime --workers=1
```

If the environment is not prepared, return `SKIP` with a concrete reason instead of pretending the feature is verified.

## Packaged-smoke lane examples

### Local packaged

```bash
bash tests/run-packaged-local-mac-dir.sh --no-open
bash scripts/inspect-packaged-mac.sh --app-path dist/mac-arm64/Amis.app
```

### Packaged launch/log observation

```bash
npm run test:packaged:mac
```

## Remote package lane example

```bash
bash tests/run-packaged-remote-macmini-fast.sh --no-open
```

## Worker contract

Every lane should return:

- lane
- commands run
- status
- required (`true | false`)
- blockers
- warnings
- skip_reason
- artifacts
- evidence
- primary_failure_signal
- artifact_paths
- bug_location_hint
- failing_test_title
- rerun_command
- sensitivity

Do not generate human prose here beyond concise evidence notes.

## Playwright artifact policy

When a Playwright command fails, worker output should explicitly include:

- screenshot path
- trace path
- error-context path
- video path (if generated)
- failing test title
- failing selector or assertion summary
- rerun command
- whether the artifact is sensitive and needs redaction handling

The goal is to help the next AI step answer:

1. what failed,
2. where it failed,
3. what screenshot/trace to inspect next.
