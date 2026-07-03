---
name: ralph-plan-lqy
description: "规划 Open Ralph GitHub issue backlog 循环：Codex 默认、blocker gate、worktree、PR。Use for `$ralph-plan`, `$ralph`, AFK coding loops, or clearing GitHub issue backlogs."
---

# Ralph Plan

为 `ralph` CLI 准备一次 GitHub issue backlog 循环。只做规划和交接；除非用户明确要求，不要替用户启动长时间运行的 Ralph。

## 工作流

- GitHub Issues 是唯一 backlog 和状态机。
- 只处理 open 且带 `ready-for-agent` 的 issue。
- 每轮只领取一个 issue，按 issue 列表顺序扫描，先通过 blocker gate 的先做。
- 不使用 `.ralph/ralph-tasks.md`，不使用 `--tasks`。
- 使用 `--no-commit`；agent 在 issue 专属 `git worktree` 里建语义分支、提交、开 PR。
- 没有可领取 issue 时输出 `<promise>NO MORE TASKS</promise>`。

## 最小检查

给出命令前检查：

```bash
command -v ralph
ralph --version
command -v gh
gh auth status
gh issue list --label ready-for-agent --state open
command -v codex
```

如果用户点名 Claude Code，把最后一行改为：

```bash
command -v claude
```

缺失工具时只提示用户安装或登录，不展开安装教程。

## Blocker Gate

本 skill 自带只读 blocker gate：

```bash
python3 ~/work/.agents/skills/ralph-plan-lqy/scripts/check_ready_issue_unblocked.py <issue-number>
```

- `0`：可以开始。
- `2`：该 issue 不可领取，跳过并检查下一个 issue。
- `1`：环境或 GitHub API 阻塞，停止并说明原因。

如果 skill 安装在不同位置，输出命令时按实际路径替换。

## Prompt 文件

默认直接引用本 skill 模板：

```text
~/work/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md
```

只有仓库需要特殊标签或额外安全规则时，才复制到 `.ralph/prompts/issue-backlog.md` 再修改。

## 主命令

默认用 Codex：

```bash
cd <repo-root>
ralph \
  --agent codex \
  --completion-promise "NO MORE TASKS" \
  --max-iterations 3 \
  --last-activity-timeout 15m \
  --no-commit \
  --prompt-file ~/work/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md \
  -- \
  --sandbox danger-full-access \
  --dangerously-bypass-approvals-and-sandbox
```

用户点名 Claude Code 时，把 `--agent codex` 改成 `--agent claude-code`，并移除 `--` 后面的 Codex 专属参数。除非用户点名，否则省略 `--model`。

## 参数说明

- `--agent`：每轮调用哪个 CLI。
- `--completion-promise "NO MORE TASKS"`：没有可领取 issue 时停止。
- `--max-iterations`：安全上限，必须设置。
- `--last-activity-timeout 15m`：静默超时后结束当前轮。
- `--no-commit`：禁止 Ralph 自动提交。
- `--prompt-file`：backlog prompt 文件。
- `--` 后参数：传给 Codex CLI，默认绕过沙箱和审批。

## 运行与监控

```bash
ralph --status
ralph --add-context "提示..."
ralph --clear-context
# 停止：终端 1 按 Ctrl+C；重跑同一命令继续。
```

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

## 如何运行与监控
<最短可执行说明>
````
