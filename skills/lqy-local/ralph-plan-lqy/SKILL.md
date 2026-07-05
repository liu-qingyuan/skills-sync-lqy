---
name: ralph-plan-lqy
description: "规划 Open Ralph GitHub issue backlog 串行循环：Codex 默认、blocker gate、本地 commit。Use for `$ralph-plan`, `$ralph`, AFK coding loops, or clearing GitHub issue backlogs."
---

# Ralph Plan

为 `ralph` CLI 准备一次 GitHub issue backlog 循环。只做规划和交接；除非用户明确要求，不要替用户启动长时间运行的 Ralph。

## 工作流

- GitHub Issues 是唯一 backlog 和状态机。
- 只处理 open 且带 `ready-for-agent` 的 issue。
- 每轮只领取一个 issue，按 issue number 升序扫描，先通过 blocker gate 的先做。
- 领取到可实现 issue 后，交给 `$implement-lqy GitHub issue #N` 执行。
- 不使用 `.ralph/ralph-tasks.md`，不使用 `--tasks`。
- 使用 `--no-commit`；agent 在当前 checkout 串行实现并自己提交 commit。
- 没有可领取 issue 时输出 `<promise>NO MORE TASKS</promise>`。

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

默认用 Codex。Open Ralph 1.3.x 的 `--allow-all` 默认会给 Codex 自动加 `--full-auto`；当前 Codex CLI 下它不能和 `--dangerously-bypass-approvals-and-sandbox` 混用。需要无沙箱权限时，先用 `--no-allow-all` 关闭 Ralph 的自动 `--full-auto`，再把 Codex bypass flag 放在 `--` 后传给 Codex：

```bash
cd <repo-root>
ralph \
  --agent codex \
  --completion-promise "NO MORE TASKS" \
  --max-iterations 3 \
  --last-activity-timeout 15m \
  --no-commit \
  --no-allow-all \
  --prompt-file ~/work/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md \
  -- \
  --dangerously-bypass-approvals-and-sandbox
```

如果只需要 `danger-full-access` 而不需要完全 bypass，也可以省略 `--no-allow-all` 和 `--dangerously-bypass-approvals-and-sandbox`，只在 `--` 后传 `--sandbox danger-full-access`。但当 Codex 需要通过本机代理访问 GitHub API、或此前出现 `127.0.0.1:<proxy-port>` 被 sandbox 拦截时，使用上面的默认命令。

用户点名 Claude Code 时，把 `--agent codex` 改成 `--agent claude-code`，并移除 `--` 后面的 Codex 专属参数和 `--no-allow-all`。除非用户点名，否则省略 `--model`。

## 参数说明

- `--agent`：每轮调用哪个 CLI。
- `--completion-promise "NO MORE TASKS"`：没有可领取 issue 时停止。
- `--max-iterations`：安全上限，必须设置。
- `--last-activity-timeout 15m`：静默超时后结束当前轮。
- `--no-commit`：禁止 Ralph 自动提交。
- `--no-allow-all`：关闭 Open Ralph 对 Codex 自动注入的 `--full-auto`，避免和 Codex bypass flag 冲突。
- `--prompt-file`：backlog prompt 文件。
- `--` 后参数：传给 Codex CLI；默认传 `--dangerously-bypass-approvals-and-sandbox`，让 Codex 子进程可使用本机代理访问 GitHub API。

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
