---
name: ralph-omx-plan
description: "Prepare a concise Open Ralph via OMX handoff: task packet, mode choice, ralph-omx command, optional Codex /goal inner-loop flags, and parameter guide. Use when the user invokes `$ralph-omx-plan` or asks for Ralph outer loop, OMX backend, Codex goal mode, Prompt Loop Mode, Task Ledger Mode, `$ralplan`, `$ralph`, `$team`, or GitNexus-grounded Ralph execution planning."
---

# Ralph OMX Plan

Create an execution-ready handoff for `ralph-omx`. Plan and format the run; do **not** execute it unless the user explicitly asks.

## Output contract

Always produce:

1. A polished Open Ralph task packet or prompt-file proposal.
2. A mode decision: **Prompt Loop Mode** or **Task Ledger Mode**.
3. A Codex goal decision: enabled or disabled.
4. A primary `ralph-omx` command with safe iteration limits.
5. A short parameter guide for every included flag/env var.
6. Optional OMX-native alternatives only when requested or useful: `$ralplan`, `$ralph`, `$team`.

If the user asks you to write files, write `.omx/prompts/<slug>-ralph-omx.md`. In Task Ledger Mode also write or refresh `.ralph/ralph-tasks.md` and validate it has unchecked tasks.

## Choose the outer Ralph mode

### Prompt Loop Mode: no `--tasks`

Use when the user asks for:

- no tasks / no task list / 不用 tasks / 不维护 `.ralph/ralph-tasks.md`
- the same prompt for N rounds / 同一个 prompt 跑 N 次
- a small smoke test or investigation where a ledger is overhead

Rules:

- Do **not** include `--tasks` or `--task-promise`.
- Do **not** create or require `.ralph/ralph-tasks.md`.
- Prompt must say: `Do not use .ralph/ralph-tasks.md for this run.`
- Completion requires: minimum iterations reached, objective complete, no known unresolved errors, and fresh verification evidence.
- If the user asks for exactly N runs, set `--min-iterations N --max-iterations N` and warn it is a hard cap.

Default command shape:

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

### Task Ledger Mode: `--tasks`

Use for substantial implementation, multi-phase work, ToDo/ledger requests, or when early completion would be risky. This is the default for real implementation unless the user explicitly chooses Prompt Loop Mode.

Rules:

- Include `--tasks --task-promise READY_FOR_NEXT_TASK`.
- When the user asks for a task/todo to run N Ralph rounds (for example `每个 todo 循环三次`, `task 最小循环次数 3`, or per-task verification pressure), include `--task-min-iterations N`. Do not confuse this with global `--min-iterations`.
- Ensure repo-local `.ralph/ralph-tasks.md` exists and belongs to this objective.
- Before showing a runnable command, report unchecked/checked counts. If unchecked count is `0` for real work, rewrite/reset the ledger first.
- While work remains, the agent should output `<promise>READY_FOR_NEXT_TASK</promise>`, not the final completion promise.

Default command shape:

```bash
cd <repo-root>
RALPH_OMX_MODEL=gpt-5.5 \
OMX_RALPH_REASONING=high \
OMX_RALPH_SANDBOX=danger-full-access \
ralph-omx \
  --tasks \
  --task-promise READY_FOR_NEXT_TASK \
  --task-min-iterations 3 \
  --min-iterations 3 \
  --max-iterations 20 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

Use `--min-iterations 5-8 --max-iterations 30` for large product work. Use `--min-iterations 1` only for explicit tiny smoke tests. Use `--task-min-iterations N` only in Task Ledger Mode when each top-level todo must receive N Ralph outer-loop attempts before it may complete.

## Codex goal overlay

Codex goal mode is an **inner-session overlay**, not a third outer mode.

- Open Ralph still owns the outer loop: fresh process per iteration, min/max iterations, promise detection, `.ralph/ralph-history.json`, git/file-system state, optional commits.
- Codex `/goal` owns sustained progress **inside one Ralph iteration**.
- Cross-iteration state must remain repo-native: files, git diff/history, `.harness/progress.md`, project progress files, `.ralph/ralph-history.json`, and `.ralph/codex-goal-ledger.jsonl`.

Enable it when the user mentions `--codex-goal`, `RALPH_CODEX_GOAL`, `/goal`, Codex goal mode, ultragoal-like behavior, or “外层 Ralph / 内层 /goal”.

Generated command requirements when enabled:

```bash
  --codex-goal \
  --codex-backend omx \
```

Or env equivalent when clearer:

```bash
RALPH_CODEX_GOAL=1 RALPH_CODEX_BACKEND=omx ralph-omx ...
```

Important:

- Do **not** tell the user to put `/goal` manually at the top of the task packet. Ralph wraps normal prompts, so that does not guarantee `/goal` reaches Codex as the first token.
- `--codex-goal --codex-backend omx` is the explicit path: Open Ralph constructs the backend prompt so `/goal` is first when it calls OMX/Codex.
- Mention verification evidence: `.ralph/codex-goal-ledger.jsonl` should include `"promptStartsWithGoal":true`. If native OMX/Codex goal evidence is not confirmed, the runner should warn and use the simulated goal prompt fallback.

Goal overlay examples:

```bash
# Prompt Loop + Codex goal overlay
ralph-omx \
  --codex-goal \
  --codex-backend omx \
  --min-iterations 3 \
  --max-iterations 10 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

```bash
# Task Ledger + Codex goal overlay
ralph-omx \
  --codex-goal \
  --codex-backend omx \
  --tasks \
  --task-promise READY_FOR_NEXT_TASK \
  --task-min-iterations 3 \
  --min-iterations 3 \
  --max-iterations 20 \
  --completion-promise <SLUG_UPPER>_VERIFIED \
  --last-activity-timeout 10m \
  --prompt-file .omx/prompts/<slug>-ralph-omx.md
```

## Prompt packet checklist

Include only task-relevant detail:

- Objective and acceptance criteria.
- Repo root, important paths, issues, specs, or GitNexus context.
- Scope and non-goals.
- Deliverables: code, docs, tests, artifacts.
- Required verification commands/evidence.
- State model:
  - Prompt Loop: no task ledger; keep improving the same objective across rounds.
  - Task Ledger: maintain `.ralph/ralph-tasks.md`; final promise only after all checkboxes and verification are complete.
  - Codex goal overlay: do not rely on old Codex thread state; write partial progress/failures to repo files.
- Safety constraints: secrets, destructive operations, external production side effects.
- Final promise: use a strict slug-specific marker like `<promise><SLUG_UPPER>_VERIFIED</promise>`, not generic `COMPLETE` except throwaway tests.

## Task ledger guard

In Task Ledger Mode, treat `.ralph/ralph-tasks.md` as a fresh execution artifact.

Before presenting a runnable `--tasks` command:

```bash
cd <repo-root>
test -f .ralph/ralph-tasks.md
grep -q '^- \[ \]' .ralph/ralph-tasks.md
printf 'unchecked=%s checked=%s\n' \
  "$(grep -c '^- \[ \]' .ralph/ralph-tasks.md || true)" \
  "$(grep -c '^- \[x\]' .ralph/ralph-tasks.md || true)"
```

Rewrite/reset the ledger if it is missing, fully checked, stale, points to another objective, or uses a different completion promise. Skip this guard in Prompt Loop Mode.

Suggested ledger skeleton for new substantial work:

```markdown
# Ralph Tasks

## Phase 0: Baseline
- [ ] Read relevant specs/context and summarize acceptance criteria
- [ ] Audit current implementation and git status

## Phase 1: Implementation
- [ ] Implement the first coherent code slice with targeted tests
- [ ] Implement the next integration/UI/API slice with targeted tests

## Phase 2: Verification and handoff
- [ ] Run required lint/typecheck/test/build/smoke checks
- [ ] Record evidence, risks, and final handoff notes
```

Adapt names and tasks to the actual work. Keep checkboxes coarse but objectively verifiable.

## Parameter guide

Explain every included item briefly:

- `RALPH_OMX_MODEL`: model for the Codex-backed run; local default commonly `gpt-5.5`.
- `OMX_RALPH_REASONING`: reasoning effort, usually `high`.
- `OMX_RALPH_SANDBOX`: sandbox, commonly `danger-full-access` for local autonomous repair.
- `--codex-goal`: enable inner Codex `/goal` behavior per Ralph iteration.
- `--codex-backend omx`: run goal mode through OMX backend.
- `--tasks`: Task Ledger Mode only; final completion gated by `.ralph/ralph-tasks.md`.
- `--task-promise READY_FOR_NEXT_TASK`: Task Ledger Mode continuation marker.
- `--task-min-iterations`: Task Ledger Mode only; minimum Ralph outer-loop attempts required for each top-level `.ralph/ralph-tasks.md` item before task/final completion is accepted.
- `--min-iterations`: minimum outer Ralph rounds for the whole run before final completion can stop; this is global and separate from per-task `--task-min-iterations`.
- `--max-iterations`: safety cap; set one instead of relying on unlimited defaults.
- `--completion-promise`: strict slug-specific final marker.
- `--last-activity-timeout 10m`: stop/restart a silent iteration when supported.
- `--prompt-file`: preferred for non-trivial prompts; keep under `.omx/prompts/`.

Optional knobs when relevant: `--abort-promise`, `--continue`, `--status`, `--no-stream`, `--no-commit`, `RALPH_OMX_SHIM_DEBUG=1`, and `-- <extra backend flags>`.

## Optional OMX-native alternatives

Only include lanes the user asked for or that genuinely help:

```text
Choose one lane:
1. Plan first: $ralplan $gitnexus "<task>"
2. OMX single-owner loop: $ralph $gitnexus "<task>"
3. OMX tmux team: $team $gitnexus 3:executor "<task>"
4. Open Ralph via OMX backend: ralph-omx ...
```

Keep distinctions clear:

- `ralph-omx` = Open Ralph owns the outer loop; OMX is the backend runner.
- `$ralph` = OMX-native Ralph workflow.
- `$team` requires OMX/tmux runtime.
- `$gitnexus` is context grounding, not a replacement execution mode.

## Output format

```markdown
## Ralph OMX task packet
<polished prompt or prompt-file path/content>

## Mode
<Prompt Loop Mode|Task Ledger Mode> — <one-line reason>

## Codex goal mode
<enabled|disabled>. If enabled: use `--codex-goal --codex-backend omx`; verify `.ralph/codex-goal-ledger.jsonl` has `promptStartsWithGoal:true`.

## Ralph tasks ledger
<Task Ledger: path/content and freshness action. Prompt Loop: not used.>

## Ledger sanity
- repo root: `<repo-root>`
- prompt file: `.omx/prompts/<slug>-ralph-omx.md`
- mode: `<prompt-loop|task-ledger>`
- unchecked tasks: `<n|not-applicable>`
- checked tasks: `<n|not-applicable>`
- stale-ledger action: `<created|rewritten|proposed-only|not-needed|not-applicable>`

## Primary command: ralph-omx
```bash
...
```

## Parameter customization
- <brief bullets for included flags/env vars>

## Optional OMX alternatives
```bash
# only when requested/useful
...
```

## Recommended choice
<short recommendation>
```
