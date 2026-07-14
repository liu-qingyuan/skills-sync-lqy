#!/usr/bin/env python3
"""Thin operational helper for Amis local automation runs."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


class AmisTestError(RuntimeError):
    """Reports actionable skill failures without discarding the underlying detail."""


class RepositoryContext:
    """Owns repository-root validation and canonical guide discovery."""

    guide_relative_path = Path("docs/testing/automation.md")

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self._validate_root()

    @classmethod
    def from_current_directory(cls) -> "RepositoryContext":
        """Requires callers to start at the repository root instead of guessing upward."""
        return cls(Path.cwd())

    @property
    def guide_path(self) -> Path:
        """Returns the canonical testing guide that owns automation semantics."""
        return self.root / self.guide_relative_path

    @property
    def runs_directory(self) -> Path:
        """Returns the canonical retained-run directory."""
        return self.root / ".artifacts" / "automation"

    def read_guide(self) -> str:
        """Reads the guide before every CLI workflow so instructions cannot silently drift."""
        try:
            return self.guide_path.read_text(encoding="utf-8")
        except OSError as error:
            raise AmisTestError(f"Unable to read canonical testing guide at {self.guide_path}: {error}") from error

    def _validate_root(self) -> None:
        """Checks stable tracked markers rather than accepting an arbitrary working directory."""
        required_paths = [
            self.root / "Package.swift",
            self.root / "Sources" / "AutomationCLI",
            self.guide_path,
        ]
        missing_paths = [str(path) for path in required_paths if not path.exists()]
        if missing_paths:
            missing = ", ".join(missing_paths)
            raise AmisTestError(
                f"Current directory is not the Amis repository root ({self.root}); missing required paths: {missing}"
            )


class AutomationRunRepository:
    """Resolves retained runs and loads their canonical manifest data."""

    def __init__(self, context: RepositoryContext) -> None:
        self.context = context

    def resolve(self, run_selector: str) -> Path:
        """Accepts either `latest` or one explicit run ID without path traversal."""
        if run_selector == "latest":
            return self._latest_run()
        if Path(run_selector).name != run_selector or run_selector in {"", ".", ".."}:
            raise AmisTestError(f"Run selector must be `latest` or one run ID, received: {run_selector!r}")
        run_directory = self.context.runs_directory / run_selector
        self._require_manifest(run_directory)
        return run_directory

    def load_manifest(self, run_selector: str) -> tuple[Path, Dict[str, Any]]:
        """Loads one manifest while retaining its run directory for artifact resolution."""
        run_directory = self.resolve(run_selector)
        manifest_path = run_directory / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise AmisTestError(f"Unable to read manifest at {manifest_path}: {error}") from error
        if not isinstance(manifest, dict):
            raise AmisTestError(f"Manifest at {manifest_path} must contain a JSON object")
        return run_directory, manifest

    def _latest_run(self) -> Path:
        """Selects the most recently modified retained manifest."""
        if not self.context.runs_directory.is_dir():
            raise AmisTestError(f"Automation run directory does not exist: {self.context.runs_directory}")
        candidates = [path.parent for path in self.context.runs_directory.glob("*/manifest.json")]
        if not candidates:
            raise AmisTestError(f"No retained automation runs found under {self.context.runs_directory}")
        return max(candidates, key=lambda path: (path / "manifest.json").stat().st_mtime)

    def _require_manifest(self, run_directory: Path) -> None:
        """Rejects missing or partially retained run directories."""
        manifest_path = run_directory / "manifest.json"
        if not manifest_path.is_file():
            raise AmisTestError(f"Run does not contain a manifest: {manifest_path}")


class StepFailurePolicy:
    """Centralizes the canonical manifest-step failure predicate."""

    @classmethod
    def is_failed(cls, step: Dict[str, Any]) -> bool:
        """Treats timeout, nonzero exit, or a recorded failure reason as failure."""
        provenance = step.get("provenance") if isinstance(step.get("provenance"), dict) else {}
        return bool(
            provenance.get("timedOut")
            or (provenance.get("exitStatus") is not None and provenance.get("exitStatus") != 0)
            or step.get("failureReason")
        )


class RunInspector:
    """Builds a compact summary while preserving paths to complete artifacts."""

    def __init__(self, run_repository: AutomationRunRepository) -> None:
        self.run_repository = run_repository

    def inspect(self, run_selector: str) -> Dict[str, Any]:
        """Reports run status, first failure, logs, Scenario artifacts, and result bundles."""
        run_directory, manifest = self.run_repository.load_manifest(run_selector)
        steps = manifest.get("steps", [])
        if not isinstance(steps, list):
            raise AmisTestError("Manifest `steps` must be an array")
        step_summaries = [self._step_summary(step) for step in steps if isinstance(step, dict)]
        return {
            "runID": manifest.get("runID", run_directory.name),
            "commandName": manifest.get("commandName"),
            "manifestStatus": manifest.get("status"),
            "manifestPath": str(run_directory / "manifest.json"),
            "preflightFailures": self._preflight_failures(manifest),
            "firstFailedStep": next((step for step in step_summaries if step["failed"]), None),
            "steps": step_summaries,
            "scenarios": self._scenario_summaries(run_directory),
            "resultBundles": [str(path) for path in sorted(run_directory.glob("test-results/*.xcresult"))],
        }

    def _step_summary(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Keeps bounded failure text alongside the complete stdout and stderr paths."""
        provenance = step.get("provenance") if isinstance(step.get("provenance"), dict) else {}
        return {
            "stepName": step.get("stepName"),
            "failed": StepFailurePolicy.is_failed(step),
            "failureReason": step.get("failureReason"),
            "stdoutPath": step.get("stdoutPath"),
            "stderrPath": step.get("stderrPath"),
            "provenance": provenance,
        }

    def _preflight_failures(self, manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Surfaces failures that can occur before a manifest step exists."""
        report = manifest.get("preflightReport")
        checks = report.get("checks", []) if isinstance(report, dict) else []
        return [check for check in checks if isinstance(check, dict) and not check.get("succeeded", False)]

    def _scenario_summaries(self, run_directory: Path) -> List[Dict[str, Any]]:
        """Finds every ScenarioResult and follows its timeline, evidence, and diagnostic references."""
        summaries: List[Dict[str, Any]] = []
        for result_path in sorted(run_directory.glob("scenarios/*/result.json")):
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise AmisTestError(f"Unable to read ScenarioResult at {result_path}: {error}") from error
            if not isinstance(result, dict):
                raise AmisTestError(f"ScenarioResult at {result_path} must contain a JSON object")
            timeline_path = result.get("timelinePath") or str(result_path.parent / "timeline.json")
            summaries.append(
                {
                    "scenarioID": result.get("scenarioID", result_path.parent.name),
                    "status": result.get("status"),
                    "failureReason": result.get("failureReason"),
                    "resultPath": str(result_path),
                    "timelinePath": timeline_path,
                    "evidence": result.get("evidence", []),
                    "diagnostics": result.get("diagnostics", []),
                }
            )
        return summaries


class BoundedProcessRunner:
    """Runs external tools without a shell and enforces one explicit timeout."""

    def run(
        self,
        command: Sequence[str],
        working_directory: Path,
        timeout_seconds: float,
        environment: Optional[Dict[str, str]] = None,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess:
        """Preserves detailed launch and timeout failures for the caller."""
        if timeout_seconds <= 0:
            raise AmisTestError(f"Timeout must be greater than zero, received: {timeout_seconds}")
        try:
            return subprocess.run(
                list(command),
                cwd=str(working_directory),
                env=environment,
                timeout=timeout_seconds,
                check=False,
                text=True,
                capture_output=capture_output,
            )
        except subprocess.TimeoutExpired as error:
            rendered = " ".join(command)
            stdout = self._render_timeout_output(error.stdout)
            stderr = self._render_timeout_output(error.stderr)
            raise AmisTestError(
                f"Command timed out after {timeout_seconds} seconds: {rendered}"
                f"\nstdout:\n{stdout}\nstderr:\n{stderr}"
            ) from error
        except OSError as error:
            rendered = " ".join(command)
            raise AmisTestError(f"Unable to launch command `{rendered}` from {working_directory}: {error}") from error

    def _render_timeout_output(self, output: Any) -> str:
        """Normalizes partial timeout output from Python's string or byte representations."""
        if output is None:
            return ""
        if isinstance(output, bytes):
            return output.decode("utf-8", errors="replace")
        return str(output)


class AutomationLauncher:
    """Invokes the tracked permission-host launcher as the only automation entrypoint."""

    def __init__(self, context: RepositoryContext, process_runner: BoundedProcessRunner) -> None:
        self.context = context
        self.process_runner = process_runner

    def run(self, arguments: Sequence[str], timeout_seconds: float) -> int:
        """Forwards the selected command unchanged and preserves its observed exit code."""
        result = self.process_runner.run(
            ["swift", "run", "AutomationHostLauncher", *arguments],
            self.context.root,
            timeout_seconds,
        )
        return result.returncode


class FailureReproducer:
    """Reconstructs failed subprocesses while keeping orchestrated failures truthful."""

    scenario_commands = {"e2e-smoke", "e2e-cross"}

    environment_notice = (
        "The manifest records only explicit environment overrides; the reproduced process also uses the "
        "current inherited shell environment, which may contain unrecorded state."
    )

    def __init__(
        self,
        run_repository: AutomationRunRepository,
        process_runner: Optional[BoundedProcessRunner] = None,
    ) -> None:
        self.run_repository = run_repository
        self.process_runner = process_runner or BoundedProcessRunner()

    def preview(self, run_selector: str) -> Dict[str, Any]:
        """Returns recorded inputs and whether they represent a directly reproducible subprocess."""
        _, manifest = self.run_repository.load_manifest(run_selector)
        step = self._first_failed_step(manifest)
        provenance = step.get("provenance") if isinstance(step.get("provenance"), dict) else {}
        execution_kind = provenance.get("executionKind")
        step_name = step.get("stepName")
        if execution_kind == "scenario":
            preview = {
                "stepName": step_name,
                "executionKind": execution_kind,
                "reproducible": False,
                "failureReason": step.get("failureReason"),
                "stdoutPath": step.get("stdoutPath"),
                "stderrPath": step.get("stderrPath"),
                "recordedProvenance": provenance,
                "diagnostic": (
                    "Scenario failures depend on AutomationCLI orchestration and cannot be reproduced by "
                    "launching the recorded app executable directly; rerun the narrowest Scenario command "
                    "through AutomationHostLauncher."
                ),
                "environmentNotice": self.environment_notice,
            }
            if step_name in self.scenario_commands:
                preview["recommendedLauncherArguments"] = [step_name, "--retention", "all"]
            return preview
        executable = provenance.get("executable")
        if not executable:
            return {
                "stepName": step_name,
                "executionKind": execution_kind,
                "reproducible": False,
                "failureReason": step.get("failureReason"),
                "stdoutPath": step.get("stdoutPath"),
                "stderrPath": step.get("stderrPath"),
                "diagnostic": "The first failed step has no recorded executable; inspect its logs instead of inventing a command.",
                "environmentNotice": self.environment_notice,
            }
        arguments = provenance.get("arguments", [])
        environment_overrides = provenance.get("environmentOverrides", {})
        working_directory = provenance.get("workingDirectory")
        timeout_seconds = provenance.get("timeoutSeconds")
        if not isinstance(arguments, list) or not all(isinstance(value, str) for value in arguments):
            raise AmisTestError("Failed-step provenance `arguments` must be an ordered string array")
        if not isinstance(environment_overrides, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in environment_overrides.items()
        ):
            raise AmisTestError("Failed-step provenance `environmentOverrides` must be a string map")
        if not isinstance(working_directory, str) or not working_directory:
            raise AmisTestError("Failed-step provenance does not contain a working directory")
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise AmisTestError("Failed-step provenance does not contain a positive timeout")
        return {
            "stepName": step_name,
            "executionKind": execution_kind,
            "reproducible": True,
            "executable": executable,
            "arguments": arguments,
            "workingDirectory": working_directory,
            "timeoutSeconds": timeout_seconds,
            "environmentOverrides": environment_overrides,
            "stdoutPath": step.get("stdoutPath"),
            "stderrPath": step.get("stderrPath"),
            "environmentNotice": self.environment_notice,
        }

    def execute(self, run_selector: str) -> int:
        """Runs the previewed process with recorded inputs and the current inherited shell environment."""
        preview = self.preview(run_selector)
        if not preview["reproducible"]:
            raise AmisTestError(
                f"Step `{preview.get('stepName')}` cannot be reproduced: {preview.get('diagnostic')} "
                f"stdout={preview.get('stdoutPath')} stderr={preview.get('stderrPath')}"
            )
        environment = os.environ.copy()
        environment.update(preview["environmentOverrides"])
        result = self.process_runner.run(
            [preview["executable"], *preview["arguments"]],
            Path(preview["workingDirectory"]),
            float(preview["timeoutSeconds"]),
            environment=environment,
        )
        return result.returncode

    def _first_failed_step(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Uses manifest order because `all` and child commands are fail-fast."""
        steps = manifest.get("steps", [])
        if not isinstance(steps, list):
            raise AmisTestError("Manifest `steps` must be an array")
        for step in steps:
            if not isinstance(step, dict):
                continue
            if StepFailurePolicy.is_failed(step):
                return step
        raise AmisTestError("Manifest does not contain a failed step to reproduce")


class XcresultVerifier:
    """Validates a retained result bundle with Apple's supported xcresulttool summary command."""

    def __init__(
        self,
        run_repository: AutomationRunRepository,
        process_runner: Optional[BoundedProcessRunner] = None,
    ) -> None:
        self.run_repository = run_repository
        self.process_runner = process_runner or BoundedProcessRunner()

    def verify(self, run_selector: str, timeout_seconds: float) -> Dict[str, Any]:
        """Returns the compact Apple summary or raises with complete stdout and stderr detail."""
        run_directory, _ = self.run_repository.load_manifest(run_selector)
        bundles = sorted(run_directory.glob("test-results/*.xcresult"))
        if len(bundles) != 1:
            raise AmisTestError(
                f"Expected exactly one .xcresult under {run_directory / 'test-results'}, found {len(bundles)}"
            )
        bundle = bundles[0]
        command = [
            "/usr/bin/xcrun",
            "xcresulttool",
            "get",
            "test-results",
            "summary",
            "--path",
            str(bundle),
            "--compact",
        ]
        result = self.process_runner.run(
            command,
            self.run_repository.context.root,
            timeout_seconds,
            capture_output=True,
        )
        if result.returncode != 0:
            raise AmisTestError(
                "xcresulttool validation failed "
                f"with exit code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return {"resultBundle": str(bundle), "summary": result.stdout.strip()}


class AmisTestApplication:
    """Exposes the skill's narrow operational command interface."""

    def __init__(self, context: RepositoryContext) -> None:
        self.context = context
        self.run_repository = AutomationRunRepository(context)
        self.process_runner = BoundedProcessRunner()

    def run(self, arguments: argparse.Namespace) -> int:
        """Reads the guide first, then dispatches one bounded workflow."""
        self.context.read_guide()
        if arguments.action == "run":
            return AutomationLauncher(self.context, self.process_runner).run(
                arguments.launcher_arguments,
                arguments.timeout_seconds,
            )
        if arguments.action == "inspect":
            self._print_json(RunInspector(self.run_repository).inspect(arguments.run))
            return 0
        if arguments.action == "reproduce":
            reproducer = FailureReproducer(self.run_repository, self.process_runner)
            preview = reproducer.preview(arguments.run)
            self._print_json(preview)
            return reproducer.execute(arguments.run) if arguments.execute else 0
        if arguments.action == "verify-xcresult":
            self._print_json(
                XcresultVerifier(self.run_repository, self.process_runner).verify(
                    arguments.run,
                    arguments.timeout_seconds,
                )
            )
            return 0
        raise AmisTestError(f"Unsupported action: {arguments.action}")

    def _print_json(self, value: Dict[str, Any]) -> None:
        """Produces stable machine-readable output for agents and developers."""
        print(json.dumps(value, indent=2, sort_keys=True))


class ArgumentParserFactory:
    """Builds the helper CLI without mixing parsing into workflow classes."""

    @classmethod
    def create(cls) -> argparse.ArgumentParser:
        """Defines only launcher invocation, inspection, reproduction, and result verification."""
        parser = argparse.ArgumentParser(description="Operate Amis local automation from the repository root.")
        subparsers = parser.add_subparsers(dest="action", required=True)

        run_parser = subparsers.add_parser("run", help="Invoke the canonical permission-host launcher.")
        run_parser.add_argument("--timeout-seconds", type=float, default=1800)
        run_parser.add_argument("launcher_arguments", nargs=argparse.REMAINDER)

        inspect_parser = subparsers.add_parser("inspect", help="Inspect one retained automation run.")
        inspect_parser.add_argument("--run", default="latest")

        reproduce_parser = subparsers.add_parser("reproduce", help="Preview or execute the first failed step.")
        reproduce_parser.add_argument("--run", default="latest")
        reproduce_parser.add_argument("--execute", action="store_true")

        verify_parser = subparsers.add_parser("verify-xcresult", help="Validate one retained .xcresult.")
        verify_parser.add_argument("--run", default="latest")
        verify_parser.add_argument("--timeout-seconds", type=float, default=60)
        return parser


def main() -> int:
    """Translates detailed operational failures into a nonzero CLI result."""
    try:
        arguments = ArgumentParserFactory.create().parse_args()
        return AmisTestApplication(RepositoryContext.from_current_directory()).run(arguments)
    except AmisTestError as error:
        print(f"amis-test error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
