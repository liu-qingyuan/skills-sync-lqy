---
name: ralph-plan-lqy
description: "规划或启动 Open Ralph GitHub issue backlog：Pi worker 默认，优先使用 Pi 会话的 `run_ralph` 工具，并提供 locked Pi CLI 回退。Use for `$ralph-plan`, `$ralph`, AFK coding loops, or clearing GitHub issue backlogs."
---

# Ralph Plan

默认使用 Pi worker。本 skill 只负责启动策略；每轮的选票、gate、实现交接和完成条件以 `templates/issue-backlog-prompt.md` 为准。

## 边界

- 只有用户明确要求“启动”“运行”“清空 backlog”，或使用 `/skill:ralph-plan-lqy run` 时才执行；其他请求只返回计划。
- `PI_RUN_RALPH_WORKER=1` 表示当前进程已是 Ralph iteration；禁止再次调用工具或 CLI。
- 只运行当前 Pi 会话所在的 Git worktree。
- 非 Pi worker 仅在用户明确指定时使用。

## 默认执行

有 `run_ralph` 工具时直接调用，并只传用户要求的非默认参数。模板不在工具默认路径时，传入实际 `promptFile`。

`run_ralph` 已负责 Pi agent、project trust、`--no-commit`、`--no-questions`、worktree lock 和完整日志。不要再套 runner。工具返回任何状态后都直接报告结果与 `full_log`，不要自动启动 CLI 重试。

## CLI 回退

仅当 `run_ralph` 不可用且当前进程不是 Ralph worker 时使用：

```bash
cd <repo-root>
python3 ~/.agents/skills/ralph-plan-lqy/scripts/run_locked_ralph.py \
  --worktree . \
  -- \
  ralph \
    --agent pi \
    --completion-promise "<ralph-finished-no-ready-issues/>" \
    --max-iterations 20 \
    --last-activity-timeout 15m \
    --no-commit \
    --no-questions \
    --prompt-file ~/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md \
    -- \
    --approve
```

`--approve` 只批准本轮加载可信 worktree 的项目资源，不提供 sandbox。skill 安装在其他位置时替换命令中的路径。
