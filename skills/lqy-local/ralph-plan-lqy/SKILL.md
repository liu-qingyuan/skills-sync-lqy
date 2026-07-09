---
name: ralph-plan-lqy
description: "规划 Open Ralph GitHub issue backlog 串行循环：Codex 默认、blocker gate、本地 commit。Use for `$ralph-plan`, `$ralph`, AFK coding loops, or clearing GitHub issue backlogs."
---

# Ralph Plan

为 `ralph` CLI 准备一次 GitHub issue backlog 循环。只做规划和交接；除非用户明确要求，不要替用户启动长时间运行的 Ralph。

## 工作流

- Backlog 只看 GitHub Issues：open + `ready-for-agent`。
- 每轮按 issue number 升序找第一个通过 blocker gate 的 issue。
- `Spec:` 父 issue 跳过；可实现 Ticket 交给 `$implement-lqy GitHub issue #N`。每个 issue 的 Mermaid Gate 由 `$implement-lqy` 按当前 issue 单独检查；父级 spec 的上级 Gate 不替代它。
- 不使用 `.ralph/ralph-tasks.md` 或 `--tasks`。
- `.ralph/` 是本地运行状态：不提交；`$setup-matt-pocock-skills-lqy` 默认应把它写入 `.gitignore`。
- 使用 `--no-commit`；agent 完成后自己提交。
- 没有可领取 issue 时只输出 `<ralph-finished-no-ready-issues/>`。
- 只要处理过 issue，或还有后续 issue，就禁止输出或提及 `<ralph-finished-no-ready-issues/>`。

## Blocker Gate

本 skill 自带只读 blocker gate：

```bash
python3 /Users/liuqingyuan/.agents/skills/ralph-plan-lqy/scripts/check_ready_issue_unblocked.py <issue-number>
```

- `0`：可以开始。
- `2`：该 issue 不可领取，跳过并检查下一个 issue。
- `1`：环境或 GitHub API 阻塞，停止并说明原因。

如果 skill 安装在不同位置，输出命令时按实际路径替换。

## Prompt 文件

默认直接引用本 skill 模板：

```text
/Users/liuqingyuan/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md
```

只有仓库需要特殊标签或额外安全规则时，才复制到 `.ralph/prompts/issue-backlog.md` 再修改。

## Codex 主命令

默认用 Codex。必须同时保留 `--no-allow-all` 和 `--dangerously-bypass-approvals-and-sandbox`。

```bash
cd <repo-root>
ralph \
  --agent codex \
  --completion-promise "<ralph-finished-no-ready-issues/>" \
  --max-iterations 20 \
  --last-activity-timeout 15m \
  --no-commit \
  --no-allow-all \
  --prompt-file /Users/liuqingyuan/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md \
  -- \
  --dangerously-bypass-approvals-and-sandbox
```

用户点名 Claude Code 时，把 `--agent codex` 改成 `--agent claude-code`，并移除 `--` 后面的 Codex 专属参数和 `--no-allow-all`。除非用户点名，否则省略 `--model`。

## 参数说明

- `--no-allow-all`：防止 Ralph 给 Codex 注入 `--full-auto`。
- `--dangerously-bypass-approvals-and-sandbox`：必须传给 Codex。
- `--max-iterations`、`--last-activity-timeout` 可按本轮预算调整。

## 输出格式

````markdown
## Ralph 任务包
<prompt 文件路径；如使用默认模板，说明直接引用>

## Agent
<codex|claude-code> —— <一句话理由>

## 主命令
```bash
...
```

## 参数定制
- <只解释实际用到的 flag>

````
