---
name: ralph-plan-lqy
description: "为 Claude Code 或 Codex 规划一次 Open Ralph Wiggum GitHub issue backlog 循环。默认只处理 `ready-for-agent` issues，产出可直接执行的 `ralph` 命令、prompt 路径、blocker gate 和运行/监控说明。Use when the user invokes `$ralph-plan`, `$ralph`, asks for an AFK coding loop, clearing a GitHub issue backlog, or 让 agent 循环跑 / 挂机跑 / 清 backlog."
---

# Ralph Plan

为 `ralph` CLI 准备一次 GitHub issue backlog 循环。只做规划和交接，默认不要替用户启动长时间运行的 Ralph。

## 默认工作流

只保留 Issue Backlog 模式：

- GitHub Issues 是 backlog 和状态机。
- 只处理 `ready-for-agent` 且未被 blocker 阻塞的 open issue。
- 每轮只领取一个 issue。
- Agent 自己读实时状态：`gh issue list`、`gh issue view --comments`、`gh pr list`、`git log`。
- 不使用 `.ralph/ralph-tasks.md`，不使用 `--tasks`。
- Ralph 不自动 commit；分支、commit、PR 由 agent 按 prompt 管理。

## 前置检查

给出命令前，只做最小检查：

```bash
command -v ralph
ralph --version
command -v gh
gh auth status
gh issue list --label ready-for-agent --state open
```

如果使用 Claude Code：

```bash
command -v claude
```

如果使用 Codex：

```bash
command -v codex
```

缺失工具时提示用户安装或登录，不在本 skill 内展开安装教程。

## Blocker Gate

本 skill 自带只读 blocker gate：

```bash
python3 ~/work/.agents/skills/ralph-plan-lqy/scripts/check_ready_issue_unblocked.py <issue-number>
```

只有退出码为 `0` 时才能开始实现。退出码为 `2` 表示 issue 当前不可领取；agent 必须跳过并检查下一个 issue。退出码为 `1` 表示环境或 GitHub API 问题；agent 应停止并说明阻塞。

如果用户把 skill 安装在不同位置，输出命令时按实际 skill 路径替换。

## Agent 选择

- 用户提到 Codex / GPT，或当前仓库以 Codex 为主：用 `--agent codex`。
- 用户提到 Claude Code，或 prompt 依赖 Claude Code skill：用 `--agent claude-code`。
- 除非用户点名，否则省略 `--model`。

## Prompt 文件

默认引用本 skill 自带模板：

```text
~/work/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md
```

只有仓库需要特殊标签、安全规则或命令时，才复制到：

```text
.ralph/prompts/issue-backlog.md
```

## 主命令

Codex 默认：

```bash
cd <repo-root>
ralph \
  --agent codex \
  --completion-promise "NO MORE TASKS" \
  --max-iterations 3 \
  --last-activity-timeout 15m \
  --no-commit \
  --prompt-file ~/work/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md
```

Claude Code 默认：

```bash
cd <repo-root>
ralph \
  --agent claude-code \
  --completion-promise "NO MORE TASKS" \
  --max-iterations 3 \
  --last-activity-timeout 15m \
  --no-commit \
  --prompt-file ~/work/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md
```

HITL 先用 `--max-iterations 3`。跑顺后再提高到 `10` 或 `20`。

## 参数说明

- `--agent`：每轮调用哪个 CLI。
- `--completion-promise "NO MORE TASKS"`：没有可领取 issue 时停止。
- `--max-iterations`：安全上限，必须设置。
- `--last-activity-timeout 15m`：静默超时后结束当前轮。
- `--no-commit`：禁止 Ralph 自动提交；issue workflow 由 agent 自己建分支、提交、开 PR。
- `--prompt-file`：backlog prompt 文件。

如果用户显式要求 Codex 绕过沙箱，可把 agent 参数放在 `--` 后，例如：

```bash
ralph ... -- \
  --sandbox danger-full-access \
  --dangerously-bypass-approvals-and-sandbox
```

## 运行与监控

```bash
# 终端 1：在仓库根目录启动
<主命令>

# 终端 2：监控
ralph --status
ralph --add-context "提示..."
ralph --clear-context
```

停止：在终端 1 按 `Ctrl+C`。状态保存在 GitHub、git 分支、PR 和 issue 评论中；重跑同一命令即可继续。

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
<终端 1 / 终端 2 说明>
````
