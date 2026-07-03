---
name: ralph-plan-lqy
description: "为 Open Ralph 规划一次 GitHub issue backlog 循环。默认 Codex，默认只处理 `ready-for-agent` 且 blocker gate 通过的 issues，产出 prompt 路径、主命令和运行/监控说明。Use when the user invokes `$ralph-plan`, `$ralph`, asks for an AFK coding loop, clearing a GitHub issue backlog, or 让 agent 循环跑 / 挂机跑 / 清 backlog."
---

# Ralph Plan

为 `ralph` CLI 准备一次 GitHub issue backlog 循环。只做规划和交接；除非用户明确要求，不要替用户启动长时间运行的 Ralph。

## 工作流

- GitHub Issues 是唯一 backlog 和状态机。
- 只处理 open 且带 `ready-for-agent` 的 issue。
- 每轮只领取一个 issue，按 issue 列表顺序扫描，先通过 blocker gate 的先做。
- 不使用 `.ralph/ralph-tasks.md`，不使用 `--tasks`。
- 使用 `--no-commit`；分支、commit、PR 由 agent 按 prompt 自己管理。
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
  --prompt-file ~/work/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md
```

用户点名 Claude Code 时，只把 `--agent codex` 改成 `--agent claude-code`。除非用户点名，否则省略 `--model`。HITL 先用 `--max-iterations 3`；跑顺后再提高到 `10` 或 `20`。

如果用户显式要求 Codex 绕过沙箱，可把 Codex 参数放在 `--` 后：

```bash
ralph ... -- \
  --sandbox danger-full-access \
  --dangerously-bypass-approvals-and-sandbox
```

## 参数说明

- `--agent`：每轮调用哪个 CLI。
- `--completion-promise "NO MORE TASKS"`：没有可领取 issue 时停止。
- `--max-iterations`：安全上限，必须设置。
- `--last-activity-timeout 15m`：静默超时后结束当前轮。
- `--no-commit`：禁止 Ralph 自动提交。
- `--prompt-file`：backlog prompt 文件。

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
