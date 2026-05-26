---
name: ralph-omx-plan
description: "Prepare an execution-ready Open Ralph via OMX plan and command, including optional Codex /goal inner-loop mode. Use when the user invokes `$ralph-omx-plan`, especially with `$gitnexus`, `$ralplan`, `$ralph`, `$team`, `/goal`, `--codex-goal`, or Ralph outer loop + Codex goal inner loop requests, and wants the task rewritten into a clear ralph-omx prompt plus copy-paste commands with all important parameters explained for customization."
---

# Ralph OMX Plan

Create a runnable handoff for `ralph-omx` while preserving optional OMX-native lanes. This skill plans; it does **not** execute the command unless the user explicitly asks to run it.

## Core contract

Produce a concise artifact with:

1. **Task packet**: a polished prompt for Open Ralph's loop.
2. **Mode choice**: decide whether the handoff should use Prompt Loop Mode (no `--tasks`) or Task Ledger Mode (`--tasks`).
3. **Codex goal choice**: decide whether to enable Open Ralph `--codex-goal --codex-backend omx` for an inner Codex `/goal` loop inside each Ralph iteration.
4. **Parameter guide**: explain every included flag/env var and list common knobs.
5. **Optional OMX alternatives**: include `$ralph`, `$team`, and/or `$ralplan` commands when those workflows were requested or useful.
6. **GitNexus context hook**: when `$gitnexus` is present, include graph-grounding preflight/context commands or reference the existing GitNexus context path.
7. **Task ledger freshness guard**: in Task Ledger Mode, ensure `.ralph/ralph-tasks.md` exists, belongs to the current task/prompt, and contains unchecked work before any generated `ralph-omx --tasks` command can run.

## Composition behavior

- If invoked as `$ralph-omx-plan <task>`: output only the `ralph-omx` task packet, command, and parameter guide.
- If invoked with `$gitnexus`: include GitNexus preflight/context before the `ralph-omx` command. Do not replace the primary plan with GitNexus; treat it as grounding.
- If invoked with `$ralplan`: include both:
  - an OMX consensus-planning command (`$ralplan ...`) for plan-first workflow, and
  - a `ralph-omx` command for Open Ralph loop execution.
- If invoked with `$ralph`: include an OMX-native `$ralph ...` execution command alongside `ralph-omx`, and explain when to choose each.
- If invoked with `$team`: include an OMX `$team ...` / `omx team ...` command alongside `ralph-omx`, and explain that Team is tmux-runtime parallel execution.
- If both `$ralplan` and execution lanes are present, make the sequencing explicit: run planning first, then choose one execution lane.

## Mode selection

Choose the execution mode before writing the command. Make the chosen mode explicit in the output.

### Prompt Loop Mode (no `--tasks`)

Use this mode when the user explicitly asks for any of these:

- "不带 task", "不用 tasks", "不要 task list", "不维护 `.ralph/ralph-tasks.md`"
- "同一个 prompt 跑 N 次", "一个 prompt 执行 N 轮", "重复执行 N 次"
- small investigation/smoke/fix work where a task ledger would be overhead

Prompt Loop Mode means Open Ralph runs the same prompt across multiple iterations. The agent may make and revise its own plan inside the prompt, but final completion is **not** gated by `.ralph/ralph-tasks.md`. Do not include `--tasks` or `--task-promise`. Do not write or require `.ralph/ralph-tasks.md`. Still use loop-hardened iteration bounds and a strict slug-specific completion promise.

Prompt Loop Mode prompt requirements:

- State: `Do not use .ralph/ralph-tasks.md for this run.`
- State: `Continue iterating from the same objective across rounds; use each round to inspect, implement, verify, and tighten the result based on prior evidence.`
- Completion marker must require: minimum iterations reached, objective complete, no known unresolved errors, and fresh verification evidence collected.
- If the user asks for exactly N runs, set both `--min-iterations N` and `--max-iterations N`; warn that this is a hard cap and may stop before completion.
- If the user asks for at least N runs, set `--min-iterations N` and a higher safety cap such as `--max-iterations 10` or `20`.

### Task Ledger Mode (`--tasks`)

Use this mode when the user asks for task mode, ToDo lists, multi-phase implementation, substantial product work, or when the task is complex enough that early completion would be risky. This remains the default for real implementation work unless the user explicitly asks for Prompt Loop Mode. Include `--tasks`, `--task-promise READY_FOR_NEXT_TASK`, and the `.ralph/ralph-tasks.md` freshness guard.

Task Ledger Mode semantics to explain when relevant:

- One Open Ralph iteration is the loop unit, not one checkbox.
- One iteration may complete one task, multiple small tasks, or only part of a large task.
- The whole ledger is not "done once and then repeated". The loop keeps advancing unchecked work; once all in-scope checkboxes and verification are complete, final completion is allowed after `--min-iterations` is satisfied.
- While any task or verification remains, the agent should output `<promise>READY_FOR_NEXT_TASK</promise>`, not the final completion promise.

## Codex goal mode overlay

Treat Codex goal mode as an inner-session overlay, not as a replacement for Prompt Loop Mode or Task Ledger Mode. Open Ralph still owns the outer loop: fresh process per iteration, min/max iterations, promise detection, `.ralph/ralph-history.json`, git/file-system state, and optional commits. Codex `/goal` owns sustained work **inside one Ralph iteration**.

Enable this overlay when the user asks for any of these:

- `--codex-goal`, `RALPH_CODEX_GOAL`, `/goal`, `goal mode`, `Codex goal`, or `ultragoal`-style mechanics
- "外层 Ralph / 内层 /goal", "Ralph outer loop + Codex goal inner loop"
- One Ralph iteration should keep pushing within a single Codex session instead of behaving like a plain one-shot prompt

Generated command requirements when enabled:

- Prefer explicit flags: `--codex-goal --codex-backend omx`.
- Equivalent env form is allowed: `RALPH_CODEX_GOAL=1 RALPH_CODEX_BACKEND=omx`.
- Keep `ralph-omx` as the launcher; it still selects Open Ralph's built-in `codex` agent and model.
- Do not place `/goal` manually at the top of the task packet. Open Ralph goal mode constructs the final backend prompt so `/goal` is the first token sent to `omx exec`; putting `/goal` inside the normal Ralph prompt is not equivalent because Ralph wraps prompts.
- Mention durable state: `.harness/progress.md`, project progress files, git diff/history, `.ralph/ralph-history.json`, and `.ralph/codex-goal-ledger.jsonl`. Do not rely on old Codex thread state across Ralph iterations.
- Mention observability: `.ralph/codex-goal-ledger.jsonl` should contain `"promptStartsWithGoal":true`; if OMX/Codex output lacks stable native goal evidence, Ralph warns instead of silently claiming confirmation.

Goal mode can combine with either outer-loop mode:

- Prompt Loop + goal overlay: no `.ralph/ralph-tasks.md`; each iteration sends the same Ralph prompt inside a `/goal` objective.
- Task Ledger + goal overlay: keep `--tasks` and `--task-promise READY_FOR_NEXT_TASK`; each iteration sends the task-ledger-aware Ralph prompt inside a `/goal` objective.

## Defaults to assume for local `ralph-omx`

Current local wrapper behavior:

```bash
ralph-omx <open-ralph-args> --agent codex --model "${RALPH_OMX_MODEL:-gpt-5.5}"
```

Current OMX adapter defaults:

```bash
OMX_RALPH_OMX_BIN=/opt/homebrew/bin/omx
OMX_RALPH_SANDBOX=danger-full-access
OMX_RALPH_REASONING=high
```

Open Ralph's built-in iteration defaults are intentionally permissive:

```text
--min-iterations 1
--max-iterations unlimited
--completion-promise COMPLETE
--tasks disabled
```

Do **not** mirror those permissive defaults in generated commands. They allow the loop to stop as soon as the agent emits `<promise>COMPLETE</promise>`, often exactly at the requested minimum iteration count. Generated `ralph-omx` commands should override them with loop-hardened defaults.

Prompt Loop Mode defaults:

```text
--min-iterations 3
--max-iterations 10
--completion-promise <SLUG_UPPER>_VERIFIED
# no --tasks, no --task-promise
```

Task Ledger Mode defaults:

```text
--tasks
--task-promise READY_FOR_NEXT_TASK
--min-iterations 3
--max-iterations 20
--completion-promise <SLUG_UPPER>_VERIFIED
```

Use `--min-iterations 3` for normal implementation tasks, `5-8` for product/multi-feature work, and `1` only for explicit smoke tests or tiny fixes. Prefer an explicit `--max-iterations` as a safety net. Common range: `20-30`; use `20` unless the task clearly needs less or more.

## Task ledger defaults

In Task Ledger Mode, the handoff should include an initial `.ralph/ralph-tasks.md` plan, not just a prompt that asks the agent to invent tasks later. When the user asks to create files or when the plan is execution-ready, write the task ledger alongside the prompt file. If the user only asks for a draft, include the proposed task ledger content in the output. In Prompt Loop Mode, do not create or require a task ledger unless the user switches modes.

Default task-ledger shape:

```markdown
# Ralph Tasks

## Phase 0: Planning and acceptance baseline
- [ ] Read the referenced PRD/test spec/context and summarize acceptance criteria in the working notes
- [ ] Audit current implementation gaps against the acceptance criteria

## Phase 1: Core implementation
- [ ] Implement the first coherent backend/core slice and targeted tests
- [ ] Implement the next coherent UI/API/integration slice and targeted tests

## Phase 2: Product polish and documentation
- [ ] Update user-facing docs, run instructions, and examples
- [ ] Verify safety constraints such as secret redaction, offline/mock behavior, and non-goals

## Phase 3: Final verification
- [ ] Run required lint/typecheck/test/build/smoke commands
- [ ] Review generated artifacts and summarize evidence for final handoff
```

Adapt the phase/task names to the actual PRD. Keep tasks coarse enough that one Ralph iteration can complete one task, but detailed enough that final completion is objectively gated. Use nested subtasks only when they improve clarity; Open Ralph treats any unchecked nested checkbox as incomplete for final completion.

### Task ledger freshness guard

When generating or refreshing a runnable Task Ledger Mode `ralph-omx` handoff, treat `.ralph/ralph-tasks.md` as an execution artifact, not a static note. This prevents `ralph-omx --tasks` from exiting immediately because an older ledger is already fully checked. Skip this guard in Prompt Loop Mode because that mode intentionally does not use `--tasks`.

Required behavior:

- If you write or refresh `.omx/prompts/<slug>-ralph-omx.md` for real implementation work, also write or refresh `.ralph/ralph-tasks.md` in the same repo root unless the user explicitly asks for a draft/no-write plan.
- Never leave a prior fully checked task ledger in place for a new or revised handoff. If the existing ledger has `0` unchecked boxes, a different title/slug/objective, stale referenced plan files, or a different completion promise, rewrite it from the current task plan.
- A newly generated ledger should start with unchecked tasks (`- [ ]`) for every required deliverable and validation. Only pre-check an item when it was completed and verified in the current active execution and the ledger records that evidence.
- The prompt file must name the authoritative ledger path, for example: `Use /path/to/repo/.ralph/ralph-tasks.md as the task ledger; do not use a parent directory ledger.`
- Before presenting a command, include a quick sanity line in the report: unchecked count, checked count, prompt path, and repo root. If unchecked count is zero for real work, fix the ledger before showing the run command.
- If the user reports that Ralph exits immediately, first inspect the repo-local `.ralph/ralph-tasks.md`; if every checkbox is checked or the ledger is missing, regenerate the ledger and prompt before retrying.

Recommended local validation after writing files:

```bash
cd <repo-root>
test -f .omx/prompts/<slug>-ralph-omx.md
test -f .ralph/ralph-tasks.md
grep -q '^- \[ \]' .ralph/ralph-tasks.md
printf 'unchecked=%s checked=%s\n' "$(grep -c '^- \[ \]' .ralph/ralph-tasks.md || true)" "$(grep -c '^- \[x\]' .ralph/ralph-tasks.md || true)"
```

If the `grep -q` check fails for a real implementation task, do not tell the user to run `ralph-omx`; rewrite the ledger first.

## Command template

### Prompt Loop Mode command (no `--tasks`)

Use this shape when the user asks for the same prompt to run multiple rounds without task-list gating:

```bash
cd <repo-root>
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --min-iterations 3 \
  --max-iterations 10 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

For exactly three iterations, use a hard cap only when the user explicitly wants that behavior:

```bash
cd <repo-root>
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --min-iterations 3 \
  --max-iterations 3 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

### Prompt Loop Mode with Codex goal overlay

Use this shape when the user wants Open Ralph outer loop plus OMX/Codex `/goal` inner loop without task-list gating:

```bash
cd <repo-root>
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --codex-goal \
  --codex-backend omx \
  --min-iterations 3 \
  --max-iterations 10 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

### Task Ledger Mode command (`--tasks`)

Use this shape by default for substantial implementation work from the repo root that owns `.ralph/ralph-tasks.md` and `.omx/prompts/<slug>-ralph-omx.md`:

```bash
cd <repo-root>
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --tasks \
  --task-promise READY_FOR_NEXT_TASK \
  --min-iterations 3 \
  --max-iterations 20 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

### Task Ledger Mode with Codex goal overlay

Use this shape for substantial implementation when the user wants both `.ralph/ralph-tasks.md` gating and an inner Codex `/goal` session per Ralph iteration:

```bash
cd <repo-root>
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --codex-goal \
  --codex-backend omx \
  --tasks \
  --task-promise READY_FOR_NEXT_TASK \
  --min-iterations 3 \
  --max-iterations 20 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

For substantial product work, raise the minimum iteration count:

```bash
cd <repo-root>
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --tasks \
  --task-promise READY_FOR_NEXT_TASK \
  --min-iterations 5 \
  --max-iterations 30 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

When the prompt is genuinely short in Task Ledger Mode, inline it instead of writing a prompt-file, but still keep `--tasks`, `--task-promise`, and a strict completion promise. If the user explicitly asks for Prompt Loop Mode or a smoke test, use the no-ledger prompt-loop command shape instead:

```bash
RALPH_OMX_MODEL=gpt-5.5 OMX_RALPH_REASONING=high \
ralph-omx "<task>. Maintain .ralph/ralph-tasks.md. Output <promise>READY_FOR_NEXT_TASK</promise> while work remains, and only output <promise><SLUG_UPPER>_VERIFIED</promise> after all tasks and verification are complete." \
  --tasks \
  --task-promise READY_FOR_NEXT_TASK \
  --min-iterations 3 \
  --max-iterations 20 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m
```

Use `--prompt-file` for long tasks, multi-step specs, secret-safety constraints, GitNexus/ralplan context, or any task expected to run for more than one iteration. In Task Ledger Mode, when writing the prompt file, also write or refresh `.ralph/ralph-tasks.md` unless the user explicitly asks not to. Validate that the ledger contains at least one unchecked task before presenting a `--tasks` command. In Prompt Loop Mode, write only the prompt file and state that no task ledger is used.

## Prompt packet requirements

The generated Open Ralph prompt should include:

- Objective: one sentence.
- Context/evidence: repo paths, issue IDs, context files, GitNexus snapshot paths if known.
- Scope: what to change and what not to change.
- Deliverables: files/features/docs/tests expected.
- Verification: exact commands or evidence required.
- Mode behavior:
  - Prompt Loop Mode: explicitly say not to use `.ralph/ralph-tasks.md`; instruct the agent to continue iterating on the same objective across rounds and only emit the final promise after the minimum iterations, objective completion, and fresh verification.
  - Task Ledger Mode: create/propose `.ralph/ralph-tasks.md` with checkboxes before the loop starts; instruct the agent to maintain it and keep every in-scope deliverable represented there. Include a stale-ledger warning: if all boxes are checked, regenerate/reset the ledger for the current objective before running `ralph-omx --tasks`. Instruct the agent to output `<promise>READY_FOR_NEXT_TASK</promise>` when a task or iteration is complete but final completion is not yet proven.
  - Codex Goal Mode: state that Open Ralph owns cross-round state and Codex `/goal` owns only the current iteration; require failures/partial progress to be written to repo files such as `.harness/progress.md` or project progress files.
- Safety: secret handling, no production side effects, no destructive operations unless already authorized.
- Completion marker: use a strict slug-specific phrase. In Prompt Loop Mode, require minimum iterations reached plus objective completion and fresh verification before `<promise><SLUG_UPPER>_VERIFIED</promise>`. In Task Ledger Mode, use wording such as `When every checkbox in .ralph/ralph-tasks.md is complete and all verification evidence is fresh, output <promise><SLUG_UPPER>_VERIFIED</promise>. Do not output this promise while any task, test, UI check, review, or artifact scan remains.`
- Optional abort marker: if prerequisites may be missing, define an abort phrase and suggest `--abort-promise`.

## Parameter guide to include in every output

Explain these included parameters:

- `RALPH_OMX_MODEL`: Open Ralph/Codex model; local default is `gpt-5.5`.
- `OMX_RALPH_REASONING`: Codex `model_reasoning_effort`; typical values `low`, `medium`, `high`, `xhigh`; default `high`.
- `OMX_RALPH_SANDBOX`: OMX/Codex sandbox; current default `danger-full-access`.
- `--codex-goal`: optional Codex goal overlay; include when the user wants Open Ralph outer loop plus Codex `/goal` inner loop. It makes Open Ralph construct the final backend prompt with `/goal` as the first token.
- `--codex-backend omx`: pair with `--codex-goal` for OMX backend execution; prefer explicit backend selection over relying on auto-detection in handoff commands.
- `RALPH_CODEX_GOAL=1 RALPH_CODEX_BACKEND=omx`: env-var equivalent to the two flags; use only when an env-style command is clearer.
- `.ralph/codex-goal-ledger.jsonl`: durable goal-mode audit ledger; after a run, `"promptStartsWithGoal":true` proves Ralph sent `/goal` at the front of the final backend prompt.
- `--tasks`: included in Task Ledger Mode; omitted in Prompt Loop Mode. In Task Ledger Mode it makes Open Ralph gate final completion on `.ralph/ralph-tasks.md` checkboxes instead of trusting an early completion promise alone. If that ledger is already fully checked, `ralph-omx --tasks` can exit immediately, so the skill must refresh/validate the ledger before recommending the command.
- `--task-promise READY_FOR_NEXT_TASK`: included only with Task Ledger Mode; lets the agent advance/continue when a task or iteration is done but final completion is not proven. Do not include it in Prompt Loop Mode.
- `--min-iterations`: minimum loop rounds before completion promise can stop the loop. Generated commands should default to `3`, or `5-8` for substantial product work; use `1` only for explicit smoke tests. If the user says "execute this prompt N times" and does not say "at least", ask no follow-up: generate exactly-N Prompt Loop Mode with `--min-iterations N --max-iterations N` and warn it is a hard cap.
- `--max-iterations`: hard safety cap; `0`/omitted means unlimited, but generated commands should set one.
- `--completion-promise`: text Open Ralph looks for inside `<promise>...</promise>` to stop. Generated commands should use a strict slug-specific phrase like `<SLUG_UPPER>_VERIFIED`, not generic `COMPLETE`, to avoid premature exits.
- `--abort-promise`: optional early-abort phrase for unmet prerequisites.
- `--last-activity-timeout 10m`: optional but preferred for long autonomous runs; kills/restarts an iteration after prolonged silence when supported by the installed Open Ralph. Default generated value is `10m` to avoid long silent stalls.
- `--no-commit`: optional safety switch that prevents Open Ralph auto-commit behavior. Do **not** include it by default; list it under optional knobs unless the user asks for no commits or review-before-commit behavior.
- `--prompt-file`: safer for long prompts; generated path should be under `.omx/prompts/`. Keep the path on one shell line; never wrap a filename in the middle.
- `RALPH_OMX_SHIM_DEBUG=1`: optional debug to print adapter command.

Mention extra Open Ralph knobs when relevant:

- `--continue`: resume existing Open Ralph state if appropriate.
- `--status`: inspect state instead of running.
- `--no-stream`: reduce live streaming noise if needed.
- `--last-activity-timeout <duration>`: stop/restart if the agent is silent too long, when supported by current Open Ralph; examples: `10m`, `30m`, `1h`, `300s`.
- `--no-commit`: use only when the operator wants to inspect changes before committing.
- `-- <extra codex/omx flags>`: pass extra backend flags through the Open Ralph agent template.

## Optional OMX-native command block

When useful, include a chooser like:

```text
Choose one lane:
1. Plan first: $ralplan $gitnexus "<task>"
2. Persistent single-owner OMX loop: $ralph $gitnexus "<task>"
3. Parallel tmux workers: $team $gitnexus 3:executor "<task>"
4. Open Ralph loop via OMX backend: ralph-omx ...
```

Rules:

- Do not claim `$team` is app-safe outside an OMX/tmux runtime; say it needs the OMX tmux runtime.
- Do not run any lane automatically.
- Keep `ralph-omx` separate from OMX-native `$ralph`: Open Ralph owns the outer loop; OMX is only the backend executor.
- If `$gitnexus` appears after `$ralph-omx-plan` (for example `$ralph-omx-plan $gitnexus ...`), still include only GitNexus context plus `ralph-omx` unless the user also requested `$ralplan`, `$ralph`, or `$team`.

## Command formatting rules

- Prefer auto-commit by default. Open Ralph's default behavior commits completed iterations; show `--no-commit` only as an optional variation.
- Include `--codex-goal --codex-backend omx` whenever the task asks for Codex `/goal`, ultragoal-style inner-loop behavior, or Open Ralph outer loop + Codex goal inner loop. Do not add those flags for ordinary `ralph-omx` handoffs unless the user or task shape calls for them.
- Prefer Task Ledger Mode by default for substantial real work. Include `--tasks` and `--task-promise READY_FOR_NEXT_TASK` unless the user explicitly asks for Prompt Loop Mode (for example "不带 task", "不用 tasks", or "同一个 prompt 跑 N 次") or a one-shot smoke test. For Task Ledger Mode real work, do not emit the command until `.ralph/ralph-tasks.md` exists in the same repo root and has at least one unchecked task. For Prompt Loop Mode, do not create or require `.ralph/ralph-tasks.md`.
- Avoid generic completion promises in generated commands. Use a slug-specific promise such as `LOCAL_WEB_CONSOLE_VERIFIED` or `IMPORT_LOOP_VERIFIED`; reserve `COMPLETE` only for throwaway smoke tests.
- Keep every shell-continuation line syntactically valid: a trailing `\` must be the final character on the line and must not be separated from the next flag by blank lines.
- Keep `--prompt-file .omx/prompts/<slug>-ralph-omx.md` on one line. Do not wrap long paths across lines.
- If a command becomes too wide, use a variable:

```bash
PROMPT_FILE=.omx/prompts/<slug>-ralph-omx.md
ralph-omx ... --prompt-file "$PROMPT_FILE"
```

## Output format

Use this structure:

```markdown
## Ralph OMX task packet
<polished prompt or path proposal>

## Mode
<Prompt Loop Mode or Task Ledger Mode, with one-line reason>

## Codex goal mode
<enabled|disabled; if enabled, say `--codex-goal --codex-backend omx` and note `.ralph/codex-goal-ledger.jsonl` evidence>

## Ralph tasks ledger
<Task Ledger Mode: path `.ralph/ralph-tasks.md` if written, otherwise proposed markdown content. Prompt Loop Mode: `not used` and explicitly say no task ledger is required.>

## Ledger sanity
- repo root: `<repo-root>`
- prompt file: `.omx/prompts/<slug>-ralph-omx.md`
- mode: `<prompt-loop|task-ledger>`
- unchecked tasks: `<n|not-applicable>`
- checked tasks: `<n|not-applicable>`
- stale-ledger action: `<rewritten|created|proposed-only|not-needed|not-applicable>`

## Primary command: ralph-omx
```bash
...
```

## Parameter customization
- ...
- Default for Codex goal requests: add `--codex-goal --codex-backend omx` and expect `.ralph/codex-goal-ledger.jsonl` to record `promptStartsWithGoal:true`.
- Default for substantial real work: keep `--tasks` and `--task-promise READY_FOR_NEXT_TASK` on.
- Default for explicit same-prompt multi-run requests: omit `--tasks` and `--task-promise`; use Prompt Loop Mode.
- Default: use a strict slug-specific `--completion-promise`, not generic `COMPLETE`.
- Optional: add `--no-commit` if you want review-before-commit behavior.

## Optional OMX alternatives
```bash
# only when requested/useful
...
```

## Recommended choice
<short recommendation based on task shape>
```

If the user asks to create the prompt file, write it to `.omx/prompts/<slug>-ralph-omx.md`. In Task Ledger Mode, also write or refresh `.ralph/ralph-tasks.md` from the current task ledger, validate that it has unchecked tasks, and report both paths plus command. In Prompt Loop Mode, do not write `.ralph/ralph-tasks.md`; report `task ledger: not used`. Otherwise, provide the prompt content, proposed mode, and command without modifying the repo. If an existing ledger is fully checked or belongs to an older objective and Task Ledger Mode is selected, explicitly report that it was stale and was rewritten/reset.
