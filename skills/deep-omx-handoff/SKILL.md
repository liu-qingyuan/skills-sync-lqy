---
name: deep-omx-handoff
description: "[OMX] Clarify handoff ambiguities with OMX structured questions before generating a copy-paste $handoff-style work-contract prompt. Use when the user invokes $deep-omx-handoff or asks to make a handoff safer by asking focused questions first."
argument-hint: "What should the next AI receive and do?"
---

# Deep OMX Handoff

`deep-omx-handoff` is a prompt-generation skill with a short OMX clarification gate. It exists to reduce the risk that the next AI receives a technically plausible handoff that is not what the user intended.

It must preserve ordinary `$handoff`: do not modify, wrap, slow down, or add mandatory questions to `$handoff` itself.

## Purpose

Before outputting a copy-paste handoff prompt, ask the user only the highest-leverage unresolved question(s) about how the receiving AI should understand and execute the handoff. Then generate a compact `$handoff`-style work contract.

The interview target is the **handoff receiver's likely interpretation**, not a full PRD, deep-interview spec, or implementation plan.

The core test of this skill is behavioral, not textual: after the handoff is produced, a fresh AI should know what to do first, what not to do, what evidence proves success, and when to stop instead of widening scope. A prompt that merely summarizes context but leaves those receiver decisions implicit has failed this skill.

## Use when

- The user invokes `$deep-omx-handoff <target>`.
- The user asks for a handoff but says to clarify first, reduce ambiguity, ask questions first, or make the next AI less likely to do the wrong thing.
- The handoff target has unclear execution lane, non-goals, decision authority, validation evidence, or stop conditions.

## Do not use when

- The user invokes plain `$handoff`; generate the fast no-popup handoff instead.
- The user wants the current AI to execute the task rather than prepare another AI to continue.
- The task needs full requirements discovery or PRD-quality clarification; use `$deep-interview` first, then hand off from its artifact.
- The user asks for autonomous execution; do not start `$ultragoal`, `$team`, `$ralph`, `$autopilot`, or similar flows from this skill unless they separately ask after the handoff is generated.

## Non-negotiable boundaries

- Do not execute, fix, implement, research, commit, or validate the handed-off task itself.
- Do not save the generated handoff prompt to a file, `/tmp`, workspace, memory, or external system.
- Do not duplicate long artifacts, logs, diffs, transcripts, plans, PRDs, or historical conversation. Reference paths, commits, URLs, artifact names, or stable identifiers.
- Do not add dependencies, scripts, services, registries, background processes, hooks, or installation/runtime behavior.
- Stop and report before changing public APIs, persisted formats, cross-skill contracts, OMX runtime behavior, installation commands, or ordinary `$handoff` semantics.

## Workflow

### 1. Intake facts before asking

Read only the context needed to avoid asking the user for discoverable facts:

- user-provided target and current conversation facts;
- relevant repo paths/status if the handoff is about a local repository;
- obvious existing artifacts the user names, such as specs, plans, commits, logs, issues, or PR URLs;
- applicable skill instructions if the user mentions a downstream skill.

Keep this intake read-only. Use facts as references in the final prompt; do not paste long content.

### 2. Score handoff ambiguity

Use a lightweight handoff-readiness check. Treat a dimension as unresolved only if the answer would materially change what the receiving AI does.

Required dimensions:

- **Receiver objective**: what the next AI must accomplish.
- **Execution lane**: execute, plan only, research only, review only, continue conversation, or prepare another artifact.
- **Non-goals**: what the next AI must not do.
- **Decision boundaries**: what the next AI may decide versus when it must stop and ask/report.
- **Success and validation**: observable acceptance criteria and required evidence.
- **Required references**: paths, commits, URLs, artifacts, logs, or context identifiers the next AI must inspect or cite.
- **Safety boundaries**: privacy/security/destructive operations/dependency additions/install behavior/public contract changes.

### 3. Ask OMX structured questions

When an attached tmux OMX question renderer is available, every clarification round must use `omx question` with `source: "deep-omx-handoff"`.

Use one question per round. Do not batch a full requirements interview into one form. Prefer bounded `single-answerable` or `multi-answerable` options with `allow_other: true` only when a genuinely missing answer may be needed.

Suggested invocation pattern:

```bash
OMX_QUESTION_RETURN_PANE=$TMUX_PANE omx question --input '<json>' --json
```

Read the answer from `answers[0].answer`; use legacy top-level `answer` only as a compatibility fallback.

If `omx question` cannot render in the current runtime:

1. Ask exactly one concise plain-text fallback question if it can unblock the handoff safely; or
2. Report that the OMX clarification gate is blocked and offer to generate a warning-labeled plain `$handoff` prompt only if the user explicitly accepts the risk.

### 4. Question selection rules

Ask the single highest-leverage unresolved handoff question first. Typical question order:

1. **Execution lane** when unclear: should the next AI execute, plan, research, review, or only continue dialogue?
2. **Stop/ask boundary** when unsafe widening is possible.
3. **Non-goals** when the task could sprawl.
4. **Validation evidence** when success would otherwise be subjective.
5. **Required references** when missing artifacts would cause the receiver to reread the wrong context.
6. **Safety boundary** when privacy, security, destructive commands, dependency additions, installs, public APIs, or persistence may be touched.

Use `multi-answerable` for coexisting constraints, for example all non-goals or all required validation checks. Use `single-answerable` for mutually exclusive execution lanes or primary success definitions.

### 5. Stop conditions for questioning

Stop asking and generate the handoff when all are true:

- receiver objective is specific enough to act on;
- execution lane is explicit;
- non-goals and stop/ask boundaries are explicit enough to prevent likely misexecution;
- success criteria and validation evidence are known or marked intentionally unavailable;
- required references are listed or the final prompt says what to inspect first;
- no remaining question would materially change the receiving AI's first safe actions.

Hard cap: normally ask at most **3 rounds**. For small tasks, ask **0-1 rounds** and then produce a compact handoff. If the cap is reached with unresolved risk, preserve the residual risk in the generated prompt.

### 6. Generate the handoff prompt

Output directly in chat using the `$handoff` compatibility envelope:

1. `可复制 prompt`
   - Put the prompt in a fenced Markdown code block.
   - Speak directly to the next AI.
2. `这个 handoff 写了什么`
   - Briefly explain which clarified choices, constraints, validation expectations, references, and stop condition were included.

The copyable prompt must be a compact work contract, not a narrative recap or rigid implementation script. Choose the smallest task-appropriate shape and include the relevant subset of:

- Objective / Goal
- Context and references
- Desired behavior or output
- Invariants
- Scope
- Explicit non-goals
- Decision boundaries
- Likely touched surfaces, labeled as investigation starting points
- Acceptance criteria
- Validation expectations
- Expected final response
- Stop condition

Always include a clear stop condition. Do not include long raw artifacts.

Keep the receiving agent's agency intact. State outcomes, constraints, evidence expectations, likely starting points, and stop/ask boundaries; do not prescribe a step-by-step implementation script, exact command sequence, exact `git add` list, class/function names, or file operation order unless the user or an existing contract makes that exact action non-negotiable. Prefer "validate with appropriate static checks and real-call evidence" over a long command recipe, and prefer "commit only the relevant skill/README changes" over enumerating every staging command.

## Maintenance and release validation

When modifying this skill, static checks are not enough. Before claiming the change works, perform a real forward test of the installed skill:

1. Sync or install the edited skill into the active Codex skills directory.
2. Invoke a fresh agent with an actual `$deep-omx-handoff ...` prompt, not just by reading this file.
3. Use a realistic handoff target with at least one ambiguous receiver decision, such as execution lane, non-goal, validation evidence, or stop/ask boundary.
4. Verify from the produced behavior or blocker that the skill was actually selected and that it either:
   - asks an OMX structured question with `source: "deep-omx-handoff"` before generating the prompt; or
   - explicitly reports that the current runtime cannot render OMX questions and preserves that risk instead of silently producing an unclarified handoff.
5. Verify the generated handoff, if produced, includes receiver objective, non-goals, decision boundaries, validation evidence, required references, and stop condition without copying long artifacts.
6. Run a consumer test: pass the generated copyable prompt to a fresh receiving agent/session and verify that the receiver follows the intended lane and boundaries instead of doing the wrong thing. For example, if the handoff says "review only", the receiver should inspect/report without modifying files.
7. Also run a plain `$handoff ...` real-call smoke test to confirm ordinary `$handoff` still generates directly without the deep OMX clarification gate.

If a real-call test is skipped, say so explicitly and do not claim the skill behavior is validated. `git diff --check`, frontmatter inspection, and grep checks are useful but insufficient because they do not prove the model routes to or follows the skill.

## Defaults when the user does not specify

The next AI may decide:

- local naming;
- small file splits or consolidation;
- local implementation approach that preserves public behavior and contracts;
- targeted tests or checks that prove the requested behavior.

The next AI must stop and ask/report before:

- changing public APIs, persisted formats, user-visible contracts, or cross-skill behavior beyond the handoff;
- adding dependencies, scripts, services, registries, plugin systems, hooks, background processes, or broad abstractions;
- running destructive commands or modifying unrelated files;
- weakening validation, privacy, security, or architecture boundaries;
- copying private or oversized raw artifacts into the prompt or final answer.

## Compact path for small tasks

If the target is already narrow, ask at most one OMX question only if it materially changes execution. Then use a short prompt like:

```markdown
目标：<observable target result>。
范围/非目标：<what to change or inspect, and what not to widen>。
接手方式：<execute | plan only | research only | review only | continue conversation>。
参考：<paths/commits/URLs/artifacts to inspect; no long pasted content>。
验收与验证：<tests/checks/manual smoke/evidence expected>。
停止规则：如果需要改变 <public API/persistence/destructive behavior/dependencies/security/etc.>，先报告选项和风险。
```

## Example OMX question payloads

Execution lane:

```json
{
  "question": "What should the next AI do with this handoff?",
  "type": "single-answerable",
  "options": [
    {"label": "Execute", "value": "execute", "description": "Implement the requested change and verify it."},
    {"label": "Plan only", "value": "plan-only", "description": "Produce a plan/spec; do not modify files."},
    {"label": "Research only", "value": "research-only", "description": "Gather evidence and recommendations; do not implement."},
    {"label": "Continue conversation", "value": "continue-conversation", "description": "Pick up context and ask/finalize with the user."}
  ],
  "allow_other": true,
  "other_label": "Other lane",
  "source": "deep-omx-handoff"
}
```

Non-goals:

```json
{
  "question": "Which boundaries must the next AI not cross?",
  "type": "multi-answerable",
  "options": [
    {"label": "Do not change public APIs", "value": "no-public-api-change"},
    {"label": "Do not add dependencies", "value": "no-new-dependencies"},
    {"label": "Do not run destructive commands", "value": "no-destructive-commands"},
    {"label": "Do not execute, only plan", "value": "plan-only"}
  ],
  "allow_other": true,
  "other_label": "Other boundary",
  "source": "deep-omx-handoff"
}
```
