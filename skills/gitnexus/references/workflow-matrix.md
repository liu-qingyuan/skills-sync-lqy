# Workflow Matrix

Use this matrix when `$gitnexus` is composed with another OMX workflow.

| Primary workflow | GitNexus responsibility | Must not do |
| --- | --- | --- |
| `$deep-interview` | Preflight + brownfield facts before questions; produce evidence-backed interview prompts. | Do not ask implementation questions before intent/boundaries. |
| `$plan` | Provide repo context, likely files/symbols, and impact evidence for the work plan. | Do not write the final plan itself unless `$plan` is absent. |
| `$ralplan` | Provide grounding snapshot for Planner/Architect/Critic and ADR alternatives. | Do not run consensus review. |
| `$ralph` | Satisfy Ralph pre-context intake, map touchpoints, and identify verification targets before execution. | Do not bypass Ralph verification/deslop/cancel lifecycle. |
| `$team` | Add context path to team launch brief; split lanes by graph evidence; include impact risks for workers. | Do not manage tmux panes or team lifecycle unless `$team` has started them. |
| `$autopilot` | Supply initial code graph context, risk map, and likely test targets. | Do not narrow autonomous scope silently. |
| `$ultraqa` | Identify affected flows, test surfaces, and regression candidates. | Do not treat graph output as test pass evidence. |
| `$ultrawork` | Help partition independent execution lanes by files/symbols/processes. | Do not assign overlapping write scopes from graph guesses alone. |
| `$code-review` | Identify changed-symbol blast radius, callers, callees, and missing tests. | Do not approve without source/diff/test evidence. |
| `$security-review` | Trace auth/session/route/tool/data-flow entry points and consumers. | Do not replace security threat modeling with graph traversal. |
| `$visual-ralph` | Locate UI files/components/routes before visual implementation. | Do not skip `$visual-verdict` visual gates. |
| `$visual-verdict` | Map visual findings back to implementation files when code context matters. | Do not force GitNexus for pure image-only verdicts. |
| `$trace` | Add code graph interpretation to OMX runtime trace/log evidence. | Do not replace trace logs or state files. |

## Launch brief pattern

When handing to execution workflows, include:

```text
GitNexus context: .omx/context/gitnexus-<slug>-<timestamp>.md
Relevant files/symbols: ...
Impact risks: ...
Recommended tests: ...
Verification truth: source + tests, not GitNexus alone
```
