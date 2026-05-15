# GitNexus Composition

Use `$gitnexus` as a modifier when another workflow is present.

## Primary workflow selection

- `$deep-interview $gitnexus ...`: deep-interview remains primary. GitNexus runs preflight and grounding first, then deep-interview asks evidence-backed intent/boundary questions.
- `$plan $gitnexus ...`: plan remains primary. GitNexus provides repo context and impact evidence before the work plan is written.
- `$ralplan $gitnexus ...`: ralplan/consensus remains primary. GitNexus provides pre-context for Planner/Architect/Critic.
- `$ralph $gitnexus ...`: Ralph remains primary. GitNexus produces required pre-context and impact hints before the persistence loop starts.
- `$team $gitnexus ...`: Team remains primary. GitNexus grounding is included in the launch brief and worker assignments before panes start.
- `$autopilot $gitnexus ...`: Autopilot remains primary. GitNexus supplies initial brownfield context and risk map for the autonomous pipeline.
- `$ultraqa $gitnexus ...`: UltraQA remains primary. GitNexus supplies affected flows, likely regression surfaces, and candidate tests.
- `$ultrawork $gitnexus ...`: Ultrawork remains primary. GitNexus helps partition independent work by files/symbols/processes.
- `$code-review $gitnexus ...`: Code review remains primary. GitNexus supplies blast radius and hidden caller/consumer context.
- `$security-review $gitnexus ...`: Security review remains primary. GitNexus supplies route/tool/auth/session/data-flow map before security analysis.
- `$visual-ralph $gitnexus ...`: Visual Ralph remains primary. GitNexus finds UI implementation touchpoints before visual iteration.
- `$visual-verdict $gitnexus ...`: Visual Verdict remains primary. GitNexus is used only to connect verdict findings to code locations.
- `$trace $gitnexus ...`: Trace remains primary. GitNexus adds code graph context to OMX runtime trace interpretation.
- `$ralph-omx-plan $gitnexus ...` or `$gitnexus $ralph-omx-plan ...`: ralph-omx-plan remains primary. GitNexus runs preflight/grounding first, then the context path is embedded in the generated Open Ralph prompt and command.
- `$ralplan $gitnexus $ralph-omx-plan ...`: ralplan remains the planning workflow and ralph-omx-plan remains the command-generation handoff. GitNexus supplies brownfield evidence to both; output should include the ralplan command plus the ralph-omx command.

## Handoff artifact contract

Write `.omx/context/gitnexus-{slug}-{timestamp}.md` with:

1. Task and target repo.
2. Index health and MCP status.
3. Graph commands/tools used.
4. Source-confirmed file/line evidence.
5. Candidate symbols and impact risks.
6. Unknowns and recommended next workflow.

## Good behavior

- Ask fewer code-location questions; discover code facts directly.
- Phrase brownfield interview questions as: "I found X in file Y. Should the new behavior follow that pattern?"
- Keep user-facing output concise: context path, most relevant findings, next command.
- For `$ralph-omx-plan`, include the GitNexus context path in the prompt packet and list it as an input to the ralph-omx command.

## Bad behavior

- Do not turn `$gitnexus` into a competing planner.
- Do not copy the full logic of any primary workflow.
- Do not silently edit source during GitNexus grounding.
