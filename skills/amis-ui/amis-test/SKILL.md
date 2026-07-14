---
name: amis-test
description: Operate Amis local automation from the repository root. Use when Codex needs to select the narrowest AutomationCLI workflow, invoke the canonical permission-host launcher, inspect a retained latest or explicit run, reproduce the first failed step from recorded provenance, or verify a retained .xcresult with Apple tooling.
---

# Amis Test

Keep this skill operational and thin. Before every use, confirm the current
directory is the Amis repository root and read `docs/testing/automation.md` as
the only source of truth for command semantics, permissions, retention, artifact
layout, and exit codes.

Use `.agents/skills/amis-test/scripts/amis_test.py` for bounded subprocesses and
structured artifact output. Do not invoke raw `AutomationCLI`, recreate the app
host, or maintain signing commands in this skill.

## Select And Run

Read the guide's Commands section and choose the narrowest command that covers
the requested behavior. Invoke it through the tracked permission-host launcher:

```bash
python3 .agents/skills/amis-test/scripts/amis_test.py run \
  --timeout-seconds 1800 doctor --retention all
```

Set a timeout appropriate to the selected workflow. Preserve the helper's exit
status and detailed launcher error instead of replacing it with a generic
failure.

## Inspect A Run

Inspect the most recently modified retained manifest or one explicit run ID:

```bash
python3 .agents/skills/amis-test/scripts/amis_test.py inspect --run latest
python3 .agents/skills/amis-test/scripts/amis_test.py inspect --run <run-id>
```

Report `manifestStatus`, preflight failures, `firstFailedStep`, complete
`stdoutPath` and `stderrPath` values, ScenarioResult paths, timelines, evidence,
diagnostics, and result bundles. Read referenced files when the user needs their
contents; do not treat the bounded `failureReason` as the complete log.

## Reproduce A Failure

Preview the first failed step before executing it:

```bash
python3 .agents/skills/amis-test/scripts/amis_test.py reproduce --run <run-id>
python3 .agents/skills/amis-test/scripts/amis_test.py reproduce --run <run-id> --execute
```

The helper reconstructs the recorded executable, ordered arguments, working
directory, timeout, and explicit environment overrides. State that the process
also uses the current inherited shell environment, which can contain state the
manifest did not record. If the first failure is a local operation without an
executable, report its logs and diagnostic rather than inventing a command.
If it is a Scenario failure, report the recorded launch provenance but do not
execute the app binary directly because that omits AutomationCLI orchestration.
Use the returned launcher arguments to rerun the narrowest Scenario command
through the canonical permission host with retained artifacts.

After reproduction, rerun the narrowest failed automation command through the
canonical launcher according to the guide.

## Verify An Xcresult

Validate the retained run's single result bundle with Apple-supported
`xcresulttool`:

```bash
python3 .agents/skills/amis-test/scripts/amis_test.py verify-xcresult \
  --run <run-id> --timeout-seconds 60
```

Preserve `xcresulttool` stdout, stderr, timeout, and exit status in failure
reports. Do not interpret custom Scenario artifacts as native Xcode results.
