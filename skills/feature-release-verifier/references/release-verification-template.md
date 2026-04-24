# Feature Release Verification Report

## Verification Brief

- **Feature:** {feature_name}
- **Scope:** {feature_scope}
- **Risk:** {risk_level}
- **Runtime target:** {runtime_target}
- **Packaged requirement:** {packaged_requirement}
- **Impact tags:** {impact_tags}
- **Acceptance keywords:** {acceptance_keywords}
- **Headless mode:** {headless_mode}

## Selected Validation Matrix

- **Tiers:** {tiers_run}
- **Package lanes:** {package_lanes_run}
- **Why:** {selection_rationale}

## Baseline Quality

- **Typecheck:** {typecheck_status}
- **Lint:** {lint_status}
- **Build:** {build_status}

## Lane Results

### mock-ui

- **Status:** {mock_ui_status}
- **Required:** {mock_ui_required}
- **Skip reason:** {mock_ui_skip_reason}
- **Commands:** {mock_ui_commands}
- **Failing test title:** {mock_ui_failing_test_title}
- **Primary failure signal:** {mock_ui_failure_signal}
- **Rerun command:** {mock_ui_rerun_command}
- **Artifacts:** {mock_ui_artifacts}
- **Sensitivity:** {mock_ui_sensitivity}

### real-runtime

- **Status:** {real_runtime_status}
- **Required:** {real_runtime_required}
- **Skip reason:** {real_runtime_skip_reason}
- **Commands:** {real_runtime_commands}
- **Failing test title:** {real_runtime_failing_test_title}
- **Primary failure signal:** {real_runtime_failure_signal}
- **Rerun command:** {real_runtime_rerun_command}
- **Artifacts:** {real_runtime_artifacts}
- **Sensitivity:** {real_runtime_sensitivity}

### packaged-smoke

- **Status:** {packaged_smoke_status}
- **Required:** {packaged_smoke_required}
- **Skip reason:** {packaged_smoke_skip_reason}
- **Commands:** {packaged_smoke_commands}
- **Failing test title:** {packaged_smoke_failing_test_title}
- **Primary failure signal:** {packaged_smoke_failure_signal}
- **Rerun command:** {packaged_smoke_rerun_command}
- **Artifacts:** {packaged_smoke_artifacts}
- **Sensitivity:** {packaged_smoke_sensitivity}

### remote-lane

- **Status:** {remote_lane_status}
- **Required:** {remote_lane_required}
- **Skip reason:** {remote_lane_skip_reason}
- **Commands:** {remote_lane_commands}
- **Failing test title:** {remote_lane_failing_test_title}
- **Primary failure signal:** {remote_lane_failure_signal}
- **Rerun command:** {remote_lane_rerun_command}
- **Artifacts:** {remote_lane_artifacts}
- **Sensitivity:** {remote_lane_sensitivity}

## Artifact Manifest

{artifact_manifest}

## Bug Localization Summary

- **Likely first break point:** {first_break_point}
- **Strongest artifact to inspect next:** {best_artifact}
- **Likely layer:** {bug_layer}

## Blockers

{blockers}

## Concerns

{concerns}

## Skipped Lanes

{skipped_lanes}

## Manual Verification Needed

{manual_verification}

## Final Release Decision

- **Gate:** {release_gate}
- **Conclusion:** {release_conclusion}
