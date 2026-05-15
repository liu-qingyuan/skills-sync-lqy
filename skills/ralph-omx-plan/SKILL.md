---
name: ralph-omx-plan
description: "Prepare an execution-ready Open Ralph via OMX plan and command. Use when the user invokes `$ralph-omx-plan`, especially with `$gitnexus`, `$ralplan`, `$ralph`, or `$team`, and wants the task rewritten into a clear ralph-omx prompt plus copy-paste commands with all important parameters explained for customization."
---

# Ralph OMX Plan

Create a runnable handoff for `ralph-omx` while preserving optional OMX-native lanes. This skill plans; it does **not** execute the command unless the user explicitly asks to run it.

## Core contract

Produce a concise artifact with:

1. **Task packet**: a polished prompt for Open Ralph's loop.
2. **Primary `ralph-omx` command**: copy-paste ready, with safe defaults and explicit completion promise.
3. **Parameter guide**: explain every included flag/env var and list common knobs.
4. **Optional OMX alternatives**: include `$ralph`, `$team`, and/or `$ralplan` commands when those workflows were requested or useful.
5. **GitNexus context hook**: when `$gitnexus` is present, include graph-grounding preflight/context commands or reference the existing GitNexus context path.

## Composition behavior

- If invoked as `$ralph-omx-plan <task>`: output only the `ralph-omx` task packet, command, and parameter guide.
- If invoked with `$gitnexus`: include GitNexus preflight/context before the `ralph-omx` command. Do not replace the primary plan with GitNexus; treat it as grounding.
- If invoked with `$ralplan`: include both:
  - an OMX consensus-planning command (`$ralplan ...`) for plan-first workflow, and
  - a `ralph-omx` command for Open Ralph loop execution.
- If invoked with `$ralph`: include an OMX-native `$ralph ...` execution command alongside `ralph-omx`, and explain when to choose each.
- If invoked with `$team`: include an OMX `$team ...` / `omx team ...` command alongside `ralph-omx`, and explain that Team is tmux-runtime parallel execution.
- If both `$ralplan` and execution lanes are present, make the sequencing explicit: run planning first, then choose one execution lane.

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

Open Ralph iteration defaults:

```text
--min-iterations 1
--max-iterations unlimited
--completion-promise COMPLETE
```

Prefer an explicit `--max-iterations` in generated commands as a safety net. Common range: `10-30`; use `20` unless the task clearly needs less or more.

## Command template

Use this shape by default:

```bash
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --min-iterations 1 \
  --max-iterations 20 \
  --completion-promise COMPLETE \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

When the prompt is short, inline it instead of writing a prompt-file:

```bash
RALPH_OMX_MODEL=gpt-5.5 OMX_RALPH_REASONING=high \
ralph-omx "<task>. When done, output <promise>COMPLETE</promise>." \
  --min-iterations 1 \
  --max-iterations 20 \
  --completion-promise COMPLETE
```

Use `--prompt-file` for long tasks, multi-step specs, secret-safety constraints, or GitNexus/ralplan context.

## Prompt packet requirements

The generated Open Ralph prompt should include:

- Objective: one sentence.
- Context/evidence: repo paths, issue IDs, context files, GitNexus snapshot paths if known.
- Scope: what to change and what not to change.
- Deliverables: files/features/docs/tests expected.
- Verification: exact commands or evidence required.
- Safety: secret handling, no production side effects, no destructive operations unless already authorized.
- Completion marker: `When fully verified, output <promise>COMPLETE</promise>.`
- Optional abort marker: if prerequisites may be missing, define an abort phrase and suggest `--abort-promise`.

## Parameter guide to include in every output

Explain these included parameters:

- `RALPH_OMX_MODEL`: Open Ralph/Codex model; local default is `gpt-5.5`.
- `OMX_RALPH_REASONING`: Codex `model_reasoning_effort`; typical values `low`, `medium`, `high`, `xhigh`; default `high`.
- `OMX_RALPH_SANDBOX`: OMX/Codex sandbox; current default `danger-full-access`.
- `--min-iterations`: minimum loop rounds before completion promise can stop the loop.
- `--max-iterations`: hard safety cap; `0`/omitted means unlimited, but generated commands should set one.
- `--completion-promise`: text Open Ralph looks for inside `<promise>...</promise>` to stop.
- `--abort-promise`: optional early-abort phrase for unmet prerequisites.
- `--no-commit`: optional safety switch that prevents Open Ralph auto-commit behavior. Do **not** include it by default; list it under optional knobs unless the user asks for no commits or review-before-commit behavior.
- `--prompt-file`: safer for long prompts; generated path should be under `.omx/prompts/`. Keep the path on one shell line; never wrap a filename in the middle.
- `RALPH_OMX_SHIM_DEBUG=1`: optional debug to print adapter command.

Mention extra Open Ralph knobs when relevant:

- `--tasks` / `-t`: structured Tasks Mode.
- `--task-promise READY_FOR_NEXT_TASK`: used with Tasks Mode to advance tasks.
- `--continue`: resume existing Open Ralph state if appropriate.
- `--status`: inspect state instead of running.
- `--no-stream`: reduce live streaming noise if needed.
- `--last-activity-timeout-ms <ms>`: stop if the agent is silent too long, when supported by current Open Ralph.
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

## Primary command: ralph-omx
```bash
...
```

## Parameter customization
- ...
- Optional: add `--no-commit` if you want review-before-commit behavior.

## Optional OMX alternatives
```bash
# only when requested/useful
...
```

## Recommended choice
<short recommendation based on task shape>
```

If the user asks to create the prompt file, write it to `.omx/prompts/<slug>-ralph-omx.md` and report the path plus command. Otherwise, provide the content and command without modifying the repo.
