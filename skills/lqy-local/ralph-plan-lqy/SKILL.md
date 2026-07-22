---
name: ralph-plan-lqy
description: "规划或启动 Open Ralph GitHub issue backlog 串行循环：Pi worker 默认，优先使用 Pi 会话的 `run_ralph` 工具，支持 Pi/Codex/Claude Code CLI，包含 branch-aware eligibility gate、per-worktree lock、本地 commit。Use for `$ralph-plan`, `$ralph`, AFK coding loops, or clearing GitHub issue backlogs."
---

# Ralph Plan

为 Open Ralph 准备或执行一次 GitHub issue backlog 循环。worker 默认使用 Pi。只加载本 skill、询问参数或要求生成命令都属于规划；只有用户明确要求“启动”“运行”“清空 backlog”，或使用 `/skill:ralph-plan-lqy run` 等明确执行参数时，才启动长时间运行的 Ralph。

## 默认执行策略

1. 环境变量 `PI_RUN_RALPH_WORKER=1` 表示当前进程已经是 `run_ralph` 启动的 Pi iteration；禁止再调用工具或 CLI 启动嵌套 Ralph，只执行当前 backlog iteration。
2. 当前会话提供 `run_ralph` 工具时，明确执行请求默认直接调用该工具；规划请求只说明将使用的工具参数。
3. `run_ralph` 工具不可用且当前进程不是 Ralph worker 时，默认使用 locked Pi CLI 命令。
4. 只有用户明确点名 Codex 或 Claude Code worker 时才切换；不要在用户未指定时要求其选择 agent。

## 工作流

- Backlog 只看 GitHub Issues：open + `ready-for-agent`，并读取正文中的完整 `## Git` 契约。
- worker 只消费当前 attached branch 的 Tickets；其他 branch 正常跳过，assignees 完全不参与查询、排序或领取。
- 每轮按 issue number 升序找第一个通过 eligibility gate 的 issue。
- `Spec:` 父 issue 跳过；可实现 Ticket 交给 `$implement-lqy GitHub issue #N`。每个 issue 的 Mermaid Gate 由 `$implement-lqy` 按当前 issue 单独检查；父级 spec 的上级 Gate 不替代它。
- 不使用 `.ralph/ralph-tasks.md` 或 `--tasks`。
- `.ralph/` 是本地运行状态：不提交；`$setup-matt-pocock-skills-lqy` 默认应把它写入 `.gitignore`。
- 每个 worktree 的 Ralph 必须通过 locked runner 启动，并在完整进程生命周期内持有 `.ralph/worker.lock`。
- 使用 `--no-commit`；agent 完成后自己提交。
- 当前 branch 没有可领取 issue 时只输出 `<ralph-finished-no-ready-issues/>`；其他 branch 的 backlog 不阻止当前 worker 完成。
- 只要本轮处理过 issue，或当前 branch 还有后续工作，就禁止输出或提及 `<ralph-finished-no-ready-issues/>`。

## Eligibility Gate

本 skill 自带只读、branch-aware eligibility gate：

```bash
python3 ~/.agents/skills/ralph-plan-lqy/scripts/check_ready_issue_unblocked.py <issue-number>
```

候选 Ticket 正文最后一个 `## Git` section 必须依次包含 `Branch`、`Base branch` 和完整 40 位 `Base commit`。它还必须使用唯一的 `## Blocked by` 记录同 branch 依赖；没有 blocker 时写 `None — can start immediately`。

- `0`：可以开始。
- `1`：GitHub、git 或环境错误，停止并说明原因。
- `2`：其他 branch、父 spec、缺少 ready/open 状态或存在 open blocker；跳过并检查下一个 issue。
- `3`：持久契约错误，例如缺失/损坏 Git 契约、基线不是当前 HEAD 的祖先或跨 branch blocker；停止并修复 backlog。

gate 通过 `git symbolic-ref` 读取当前 branch，通过 `git merge-base --is-ancestor` 验证不可变 base commit。Git 契约解析由同目录的 `scripts/git_contract.py` 统一提供，不在其他调用方重复实现。

其他 producer skill 可通过 stdin 或文件复用只读 validator；成功时输出 JSON，I/O 错误返回 `1`，契约错误返回 `3`：

```bash
gh issue view <N> --json body --jq .body \
  | python3 ~/.agents/skills/ralph-plan-lqy/scripts/git_contract.py
```

producer 创建新 issue 时追加 `--require-unique`，确保正文只包含一个 `## Git`。`to-spec-lqy` 在发布父 spec 前使用共享 resolver；显式输入优先，否则 resolver 从 `--repo` 所在 worktree 的 attached branch 得到默认 `Branch`。该 branch 有 remote upstream 时用 upstream 作为 `Base branch`，否则回退 remote default；detached worktree 也回退 remote default。resolver fetch base ref 并固定完整 SHA：

```bash
python3 ~/.agents/skills/ralph-plan-lqy/scripts/resolve_spec_git.py \
  --repo <repo-path> \
  [--branch <target-branch>] \
  [--base-branch <remote/base>]
```

`--repo` 必须指向当前工作区所在的 exact worktree，不能为了方便替换成 primary/main worktree。resolver 只读取 branch/upstream，不创建 branch、worktree 或 upstream。已有目标 branch 不在解析出的 base commit 时返回 `3` 并报告 collision；Git/I/O 错误返回 `1`。

如果 skill 安装在不同位置，输出命令时按实际路径替换。

## Workspace Provision

`to-spec-lqy`、`to-tickets-lqy` 和普通 issue 的 `triage-lqy` 在创建 ready issue 或应用 `ready-for-agent` 前调用共享 provisioner。它读取正文最后一个 `## Git`，fetch 并检查 base drift，通过 exact branch worktree registry 创建或复用目标 worktree，并建立同名 remote upstream：

```bash
gh issue view <N> --json body --jq .body \
  | python3 ~/.agents/skills/ralph-plan-lqy/scripts/provision_workspace.py \
      --repo <repo-path> \
      [--allow-base-drift]
```

成功时输出包含 `path`、`branch`、`head` 和 `upstream` 的 JSON。退出码 `1` 表示 Git、I/O 或环境失败；退出码 `3` 表示 drift、dirty worktree、路径占用、意外 HEAD/upstream 或 Git 契约错误。provisioner 不执行 reset、rebase、force-push、覆盖或清理。

worktree dirty 时，producer agent 完成可确认的改动，验证并 commit/push 后重试。仅在意图不明时询问用户；禁止 stash、reset、`git clean` 或临时 workspace 绕过 gate。

默认严格拒绝 base drift。只有 producer 已展示旧/新 SHA 和提交摘要，并且用户明确选择保留父 spec 记录的旧 SHA 时，才可重新运行并传入 `--allow-base-drift`；不要把该 flag 作为默认值。已前进的目标 branch 只有在 worktree clean、`Base commit` 是 HEAD 祖先、upstream 精确匹配且 remote HEAD 与本地 HEAD 同步时才可复用。未 push、分叉或错误 upstream 的 advanced HEAD 仍返回 `3`。

默认 branch 复用已注册的主 worktree。未绑定的非主 branch 使用主 worktree 同级的 `<repo-name>-<branch-slug>`；已有 branch 只按 `git worktree list --porcelain` 的 exact branch 结果复用，不通过目录名猜测。

linked worktree 共享仓库 Git config、`.git/info/exclude` 和全局 excludes，tracked `.gitignore` 随 checkout 生效。local-config allowlist 只包含 `.codex/config.toml`：tracked 文件由 Git checkout；源 worktree 中 ignored/untracked 的 regular file 会复制到目标的相同路径。目标未忽略该文件、已有不同内容或任一路径使用 symlink 时返回 `3`，不覆盖。其他 ignored 内容不复制。

项目 `.codex/config.toml` 只在 trusted project 中加载。后续 Codex 必须从返回的 worktree 启动新会话并单独信任该路径；MCP 随新会话启动，`xcrun mcpbridge` 重新连接当前 Xcode。不要复制 trust、`MCP_XCODE_PID`、session ID 或其他临时绑定。

## Worker Lock

所有 Ralph 命令都通过 locked runner 执行：

```bash
python3 ~/.agents/skills/ralph-plan-lqy/scripts/run_locked_ralph.py \
  --worktree <repo-root> \
  -- <ralph-command-and-arguments>
```

runner 取得 `.ralph/worker.lock` 的 OS file lock，并把 lock FD 传给 Ralph 子进程；即使 wrapper 异常终止，锁也保持到 Ralph 退出。同一 worktree 已有 worker 时返回 `2` 并输出 `LOCK BUSY`；不同 worktree 的锁互不影响；成功取得锁后原样转发子进程退出码。`run_ralph` 工具内部已经调用该 runner，不要在工具调用外再套一层 runner。

## Prompt 文件

默认直接引用本 skill 模板：

```text
~/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md
```

只有仓库需要特殊标签或额外安全规则时，才复制到 `.ralph/prompts/issue-backlog.md` 再修改。

## 默认执行：Pi `run_ralph` 工具

当前会话提供 `run_ralph` 时，把它作为默认执行入口。该工具只运行当前 Pi 会话所在的 Git worktree；调用前确认当前 workspace 就是目标 worktree。它会阻塞到 Ralph 退出，把完整 stdout/stderr 写入当前 worktree 的 `.ralph/runs/`，并返回压缩结果和绝对日志路径。

默认 prompt 文件位于下列路径时，直接调用 `run_ralph`，不传覆盖参数；skill 安装在其他位置时，把实际模板绝对路径作为 `promptFile` 传入。工具默认值是：

- `completionPromise`: `<ralph-finished-no-ready-issues/>`
- `maxIterations`: `20`
- `lastActivityTimeout`: `15m`
- `promptFile`: `~/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md`
- `model`: 省略，由 Ralph/Pi 的默认模型配置决定

工具内部固定使用 Pi worker，并传入 `--no-commit`、`--no-questions` 和 `--approve`，同时通过 locked runner 持有 worktree lock。它给子 Pi iteration 设置 `PI_RUN_RALPH_WORKER=1` 并隐藏 `run_ralph` 工具；子 iteration 中工具缺失不是 CLI 回退条件。只在用户明确要求执行时调用；如果用户只要计划或命令，不要调用。工具返回 `failed`、`lock_busy` 或 `cancelled` 时报告结果与 `full_log`，不要自动再启动一条 CLI worker。

## 手动 CLI 回退

### Pi（默认回退）

只有当前会话没有 `run_ralph` 工具且 `PI_RUN_RALPH_WORKER` 不为 `1` 时，才把以下 locked Pi CLI 作为默认执行入口。Pi 的非交互模式不会显示 project trust 提示；为让每轮加载当前 worktree 的项目级 settings、resources、packages、extensions 和 `.agents/skills`，必须通过 Ralph 的 agent 参数分隔符传入 `--approve`。

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

`--approve` 只批准本轮加载项目级资源；它不是 sandbox 或工具权限开关，Pi 仍以启动用户的权限运行。只对已确认可信的 worktree 使用该命令。

### Codex（仅显式选择）

只有用户明确点名 Codex worker 时才使用以下命令。必须同时保留 `--no-allow-all` 和 `--dangerously-bypass-approvals-and-sandbox`。

```bash
cd <repo-root>
python3 ~/.agents/skills/ralph-plan-lqy/scripts/run_locked_ralph.py \
  --worktree . \
  -- \
  ralph \
    --agent codex \
    --completion-promise "<ralph-finished-no-ready-issues/>" \
    --max-iterations 20 \
    --last-activity-timeout 15m \
    --no-commit \
    --no-questions \
    --no-allow-all \
    --prompt-file ~/.agents/skills/ralph-plan-lqy/templates/issue-backlog-prompt.md \
    -- \
    --dangerously-bypass-approvals-and-sandbox
```

用户明确点名 Claude Code 时，把 `--agent codex` 改成 `--agent claude-code`，并移除 `--no-allow-all`、最后的参数分隔符以及 Codex 专属参数。除非用户明确点名，否则所有 worker 都省略 `--model`。

## 参数说明

- `run_ralph` 参数 `maxIterations`、`lastActivityTimeout`、`completionPromise` 和 `promptFile` 只在用户需要非默认值时传入。
- `--no-questions`：让 Ralph iteration 保持非交互；工具和手动 CLI 都必须保留。
- `--no-allow-all`：仅用于 Codex，防止 Ralph 注入 `--full-auto`。
- `--dangerously-bypass-approvals-and-sandbox`：仅用于 Codex，必须传入。
- `--approve`：仅用于 Pi，通过最后的 `--` 传给 Pi，显式批准本轮 project trust。
- Ralph 的 `--allow-all` / `--no-allow-all` 不会为 Pi 添加参数，也不改变 Pi 的工具权限。
- `run_locked_ralph.py --worktree .`：阻止同一 worktree 的多个 Ralph 同时修改代码和本地状态；`run_ralph` 已在内部使用它。

## 输出格式

规划请求输出：

````markdown
## Ralph 任务包
<prompt 文件路径；如使用默认模板，说明直接引用>

## Worker
pi —— 默认；只有用户明确点名时才写 codex 或 claude-code

## 执行入口
<run_ralph tool|locked Pi CLI|locked Codex/Claude Code CLI> —— <一句话理由>

## 参数定制
- <只列出偏离默认值的参数；没有则写“无”>
````

明确执行请求不要停在命令或计划；调用 `run_ralph`，或在工具不可用且当前进程不是 Ralph worker 时执行对应 locked CLI。完成后报告 `status`、iterations、elapsed、completion promise 状态、最终输出摘要和完整日志路径。
