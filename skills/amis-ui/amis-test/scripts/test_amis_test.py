import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess

from amis_test import (
    AutomationLauncher,
    AutomationRunRepository,
    AmisTestError,
    BoundedProcessRunner,
    FailureReproducer,
    RepositoryContext,
    RunInspector,
    XcresultVerifier,
)


class RecordingProcessRunner:
    """Records one bounded subprocess request without launching an external tool."""

    def __init__(self, return_code: int = 0, stdout: str = "") -> None:
        self.return_code = return_code
        self.stdout = stdout
        self.calls: list[dict] = []

    def run(
        self,
        command,
        working_directory,
        timeout_seconds,
        environment=None,
        capture_output=False,
    ) -> CompletedProcess:
        """Captures the complete execution contract and returns a deterministic result."""
        self.calls.append(
            {
                "command": list(command),
                "workingDirectory": working_directory,
                "timeoutSeconds": timeout_seconds,
                "environment": environment,
                "captureOutput": capture_output,
            }
        )
        return CompletedProcess(command, self.return_code, stdout=self.stdout, stderr="")


class AmisTestFixtureTests(unittest.TestCase):
    """Verifies the public inspection and reproduction workflows against temporary runs."""

    def setUp(self) -> None:
        """Creates the minimum repository markers required by the operational helper."""
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "Package.swift").write_text("// fixture\n", encoding="utf-8")
        (self.root / "Sources" / "AutomationCLI").mkdir(parents=True)
        guide = self.root / "docs" / "testing" / "automation.md"
        guide.parent.mkdir(parents=True)
        guide.write_text("# Automation Testing\n", encoding="utf-8")
        self.runs_directory = self.root / ".artifacts" / "automation"
        self.runs_directory.mkdir(parents=True)
        self.context = RepositoryContext(self.root)
        self.repository = AutomationRunRepository(self.context)

    def tearDown(self) -> None:
        """Releases fixture files after each behavior test."""
        self.temporary_directory.cleanup()

    def test_successful_run_inspection_reports_scenario_artifacts(self) -> None:
        """A retained successful run exposes its manifest, logs, ScenarioResult, and evidence."""
        run_directory = self.runs_directory / "20260711-120000-e2e-smoke-success"
        scenario_directory = run_directory / "scenarios" / "e2e-smoke"
        scenario_directory.mkdir(parents=True)
        stdout_path = run_directory / "e2e-smoke-stdout.log"
        stderr_path = run_directory / "e2e-smoke-stderr.log"
        stdout_path.write_text("passed\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        timeline_path = scenario_directory / "timeline.json"
        timeline_path.write_text('[{"stepID":"launch","status":"succeeded"}]\n', encoding="utf-8")
        result_path = scenario_directory / "result.json"
        result_path.write_text(
            json.dumps(
                {
                    "scenarioID": "e2e-smoke",
                    "status": "succeeded",
                    "timelinePath": str(timeline_path),
                    "evidence": [{"kind": "screenshot", "path": "evidence/main.png"}],
                    "diagnostics": [],
                }
            ),
            encoding="utf-8",
        )
        self._write_manifest(
            run_directory,
            status="succeeded",
            steps=[self._step("e2e-smoke", stdout_path, stderr_path, exit_status=0)],
        )

        summary = RunInspector(self.repository).inspect("latest")

        self.assertEqual(summary["manifestStatus"], "succeeded")
        self.assertIsNone(summary["firstFailedStep"])
        self.assertEqual(summary["steps"][0]["stdoutPath"], str(stdout_path))
        self.assertEqual(summary["scenarios"][0]["resultPath"], str(result_path.resolve()))
        self.assertEqual(summary["scenarios"][0]["timelinePath"], str(timeline_path))
        self.assertEqual(summary["scenarios"][0]["evidence"][0]["kind"], "screenshot")

    def test_failed_run_reproduction_rebuilds_recorded_process_inputs(self) -> None:
        """A failed subprocess preview preserves ordered provenance and explicit environment overrides."""
        run_directory = self.runs_directory / "20260711-120100-test-failed"
        run_directory.mkdir()
        stdout_path = run_directory / "test-stdout.log"
        stderr_path = run_directory / "test-stderr.log"
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text("compiler failed\n", encoding="utf-8")
        failed_step = self._step("test", stdout_path, stderr_path, exit_status=65)
        failed_step["failureReason"] = "Command exited with status 65"
        failed_step["provenance"].update(
            {
                "executable": "/usr/bin/xcodebuild",
                "arguments": ["test", "-scheme", "Amis-Wifi-Package"],
                "workingDirectory": str(self.root),
                "timeoutSeconds": 900,
                "environmentOverrides": {"DEVELOPER_DIR": "/Applications/Xcode.app/Contents/Developer"},
            }
        )
        self._write_manifest(run_directory, status="failed", steps=[failed_step])

        preview = FailureReproducer(self.repository).preview(run_directory.name)

        self.assertEqual(preview["executable"], "/usr/bin/xcodebuild")
        self.assertEqual(preview["arguments"], ["test", "-scheme", "Amis-Wifi-Package"])
        self.assertEqual(preview["workingDirectory"], str(self.root))
        self.assertEqual(preview["timeoutSeconds"], 900)
        self.assertEqual(
            preview["environmentOverrides"],
            {"DEVELOPER_DIR": "/Applications/Xcode.app/Contents/Developer"},
        )
        self.assertIn("inherited shell environment", preview["environmentNotice"])

    def test_failed_run_execution_uses_recorded_process_inputs(self) -> None:
        """Executing a reproduction passes manifest provenance to one bounded process call."""
        run_directory = self.runs_directory / "20260711-120200-test-failed"
        run_directory.mkdir()
        failed_step = self._step(
            "test",
            run_directory / "test-stdout.log",
            run_directory / "test-stderr.log",
            exit_status=65,
        )
        failed_step["provenance"].update(
            {
                "executable": "/usr/bin/xcodebuild",
                "arguments": ["test", "-scheme", "Amis-Wifi-Package"],
                "workingDirectory": str(self.root),
                "timeoutSeconds": 321,
                "environmentOverrides": {"AMIS_FIXTURE": "enabled"},
            }
        )
        self._write_manifest(run_directory, status="failed", steps=[failed_step])
        process_runner = RecordingProcessRunner(return_code=65)

        exit_code = FailureReproducer(self.repository, process_runner).execute(run_directory.name)

        self.assertEqual(exit_code, 65)
        self.assertEqual(
            process_runner.calls[0]["command"],
            ["/usr/bin/xcodebuild", "test", "-scheme", "Amis-Wifi-Package"],
        )
        self.assertEqual(process_runner.calls[0]["workingDirectory"], self.root)
        self.assertEqual(process_runner.calls[0]["timeoutSeconds"], 321)
        self.assertEqual(process_runner.calls[0]["environment"]["AMIS_FIXTURE"], "enabled")

    def test_local_failure_preview_preserves_logs_without_inventing_a_command(self) -> None:
        """A failed local operation remains inspectable even though it cannot be executed."""
        run_directory = self.runs_directory / "20260711-120250-build-failed"
        run_directory.mkdir()
        stdout_path = run_directory / "assemble-stdout.log"
        stderr_path = run_directory / "assemble-stderr.log"
        failed_step = self._step("assemble-app-bundle", stdout_path, stderr_path, exit_status=1)
        failed_step["failureReason"] = "Bundle assembly failed"
        failed_step["provenance"].update(
            {
                "executionKind": "local-operation",
                "workingDirectory": str(self.root),
            }
        )
        self._write_manifest(run_directory, status="failed", steps=[failed_step])

        preview = FailureReproducer(self.repository).preview(run_directory.name)

        self.assertFalse(preview["reproducible"])
        self.assertEqual(preview["failureReason"], "Bundle assembly failed")
        self.assertEqual(preview["stdoutPath"], str(stdout_path))
        self.assertEqual(preview["stderrPath"], str(stderr_path))
        self.assertIn("no recorded executable", preview["diagnostic"])

    def test_scenario_failure_requires_canonical_launcher_rerun(self) -> None:
        """A failed Scenario never treats the recorded app launch as the complete reproduction."""
        run_directory = self.runs_directory / "20260711-120275-e2e-cross-failed"
        run_directory.mkdir()
        stdout_path = run_directory / "e2e-cross-stdout.log"
        stderr_path = run_directory / "e2e-cross-stderr.log"
        failed_step = self._step("e2e-cross", stdout_path, stderr_path, exit_status=1)
        failed_step["failureReason"] = "History did not reopen the Chat Session"
        failed_step["provenance"].update(
            {
                "executionKind": "scenario",
                "executable": str(run_directory / "Amis-Wifi.app" / "Contents" / "MacOS" / "Amis-Wifi"),
                "arguments": [],
                "workingDirectory": str(self.root),
                "timeoutSeconds": 180,
                "environmentOverrides": {"AMIS_AUTOMATION_MODE": "1"},
            }
        )
        self._write_manifest(run_directory, status="failed", steps=[failed_step])

        process_runner = RecordingProcessRunner()
        reproducer = FailureReproducer(self.repository, process_runner)

        preview = reproducer.preview(run_directory.name)

        self.assertFalse(preview["reproducible"])
        self.assertEqual(preview["executionKind"], "scenario")
        self.assertEqual(preview["recommendedLauncherArguments"], ["e2e-cross", "--retention", "all"])
        self.assertIn("AutomationCLI orchestration", preview["diagnostic"])
        self.assertEqual(preview["stdoutPath"], str(stdout_path))
        self.assertEqual(preview["stderrPath"], str(stderr_path))
        with self.assertRaises(AmisTestError):
            reproducer.execute(run_directory.name)
        self.assertEqual(process_runner.calls, [])

    def test_launcher_forwards_arguments_through_tracked_permission_host(self) -> None:
        """The run workflow never invokes raw AutomationCLI or rewrites selected arguments."""
        process_runner = RecordingProcessRunner()

        exit_code = AutomationLauncher(self.context, process_runner).run(
            ["e2e-smoke", "--retention", "all"],
            timeout_seconds=600,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            process_runner.calls[0]["command"],
            ["swift", "run", "AutomationHostLauncher", "e2e-smoke", "--retention", "all"],
        )
        self.assertEqual(process_runner.calls[0]["timeoutSeconds"], 600)

    def test_xcresult_verification_uses_apple_supported_summary_command(self) -> None:
        """A retained result bundle is read only through xcrun xcresulttool with a timeout."""
        run_directory = self.runs_directory / "20260711-120300-test-success"
        result_bundle = run_directory / "test-results" / "swift-tests.xcresult"
        result_bundle.mkdir(parents=True)
        self._write_manifest(run_directory, status="succeeded", steps=[])
        process_runner = RecordingProcessRunner(stdout='{"result":"Passed"}\n')

        result = XcresultVerifier(self.repository, process_runner).verify(run_directory.name, 60)

        resolved_result_bundle = result_bundle.resolve()
        self.assertEqual(result["resultBundle"], str(resolved_result_bundle))
        self.assertEqual(result["summary"], '{"result":"Passed"}')
        self.assertEqual(
            process_runner.calls[0]["command"],
            [
                "/usr/bin/xcrun",
                "xcresulttool",
                "get",
                "test-results",
                "summary",
                "--path",
                str(resolved_result_bundle),
                "--compact",
            ],
        )
        self.assertEqual(process_runner.calls[0]["timeoutSeconds"], 60)
        self.assertTrue(process_runner.calls[0]["captureOutput"])

    def test_bounded_process_timeout_preserves_partial_output(self) -> None:
        """Timeout diagnostics retain stdout and stderr emitted before process termination."""
        command = [
            sys.executable,
            "-c",
            "import os,sys,time; print(os.environ['AMIS_TEST_STDOUT'], flush=True); "
            "print(os.environ['AMIS_TEST_STDERR'], file=sys.stderr, flush=True); time.sleep(2)",
        ]
        environment = os.environ.copy()
        environment.update({"AMIS_TEST_STDOUT": "partial-stdout", "AMIS_TEST_STDERR": "partial-stderr"})

        with self.assertRaises(AmisTestError) as error_context:
            BoundedProcessRunner().run(command, self.root, 0.1, environment=environment, capture_output=True)

        diagnostic = str(error_context.exception)
        self.assertIn("partial-stdout", diagnostic)
        self.assertIn("partial-stderr", diagnostic)

    def _write_manifest(self, run_directory: Path, status: str, steps: list[dict]) -> None:
        """Writes one canonical manifest shape used by the behavior fixtures."""
        manifest = {
            "runID": run_directory.name,
            "commandName": "test",
            "status": status,
            "artifactDirectory": str(run_directory),
            "steps": steps,
        }
        (run_directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def _step(self, name: str, stdout_path: Path, stderr_path: Path, exit_status: int) -> dict:
        """Builds a manifest step with the fields consumed by the skill helper."""
        return {
            "stepName": name,
            "stdoutPath": str(stdout_path),
            "stderrPath": str(stderr_path),
            "provenance": {
                "executionKind": "subprocess",
                "exitStatus": exit_status,
                "timedOut": False,
                "environmentOverrides": {},
            },
        }


if __name__ == "__main__":
    unittest.main()
