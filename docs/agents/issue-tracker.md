# issue tracker：GitHub

此仓库使用 GitHub issues 跟踪请求、spec 和 Ticket。使用 `gh` CLI 进行所有操作。

## 惯例

- **创建 issue**：`gh issue create --title "..." --body "..."`。
- **读取 issue**：`gh issue view <number> --comments`。
- **列出 issue**：使用 `gh issue list`，并显式指定需要的 state、label 和 JSON 字段。
- **评论**：`gh issue comment <number> --body "..."`。
- **修改标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`。
- **关闭**：`gh issue close <number> --comment "..."`。

从 `git remote -v` 推断仓库；在 clone 或 worktree 内运行时，`gh` 会使用对应的 GitHub 远程。

## 语言约定

issue 标题、正文、评论和完成摘要默认使用中文。labels、命令、路径、代码标识符、配置键和错误原文保留原 token。

## Triage 请求入口

**PR 作为请求入口：否。** 外部 PR 不进入 issue triage 状态机，也不进入 Ralph issue backlog。PR 继续使用正常 review 流程。

## Ralph-ready issue 契约

所有进入 Ralph backlog 的可实现 issue 必须是 open + `ready-for-agent`，并包含以下固定 section：

```markdown
## Blocked by

- #<issue-number>，或 `None — can start immediately`

## Git

- Branch: `<target-branch>`
- Base branch: `<base-ref>`
- Base commit: `<full-40-character-sha>`
```

- 一个 spec 恰好绑定一个 branch；同一 spec 的每个 Ticket 原样复制父 spec 的完整 `## Git`。
- 未显式指定 `Branch` 时，使用远程默认分支对应的本地主分支（本仓库为 `main`），并复用主 worktree；不得自动生成 feature slug branch。
- 只有用户显式指定非主分支时，才允许创建或复用该 branch 的独立 worktree。
- 多 Ticket 工作必须先由 `to-spec-lqy` 建立父 spec；`to-tickets-lqy` 不自行发明另一套 Git 契约。
- `triage-lqy` 可为直接实现的单个 issue 建立 Git 契约；PR 不应用此契约。
- `Base commit` 是不可变的启动锚点。首个 Ticket 加入 `ready-for-agent` 后，不自动修改 branch、base branch 或 base commit。
- 当前不支持跨 branch `Blocked by`。引用其他 branch 的 Ticket 是契约错误。
- `ready-for-agent` 是生产流程的最后提交点：Git 契约、worktree、正文和 blockers 全部验证后才应用。
- `to-spec-lqy`、`to-tickets-lqy` 和 `triage-lqy` 的 Ralph-ready 流程依赖已安装的 `ralph-plan-lqy` 共享验证与 worktree provision 脚本。

## Branch worktree

- 主分支使用主 worktree；显式指定的非主分支各自使用独立 `git worktree`。一个 worktree 同时只运行一个持有本地 OS 文件锁的 Ralph。
- 未指定 branch 时不创建 branch 或 worktree。显式指定的新 branch 若已存在，则按 exact branch 检查和复用，不自动追加随机后缀。
- 非主分支 worktree 默认位于主 worktree 同级目录，名称为 `<repo-name>-<branch-slug>`。
- 已有 worktree 通过 `git worktree list --porcelain` 和 exact branch 匹配，不通过目录名猜测。
- provision 可以创建 branch、worktree 和对应远程 upstream，但不能 reset、rebase、force-push、覆盖或删除已有内容。
- Ralph 只处理当前 branch 的 Tickets，按 issue number 升序选择，并忽略 assignees。
- `.ralph/` 是每个 worktree 的本地运行状态，不提交。

## 当 skill 说“发布到 issue tracker”时

创建 GitHub issue。若它将进入 Ralph backlog，必须先满足上述 Ralph-ready issue 契约。

## 当 skill 说“获取相关 Ticket”时

运行 `gh issue view <number> --comments`，并读取完整正文、标签和评论。

## Wayfinding operations

由 `wayfinder-lqy` 使用。Wayfinder 的 map、claim 和 frontier 是独立工作流，不改变 Ralph branch worker 的领取规则。

- **Map**：带 `wayfinder:map` 标签的 issue，正文保存 Notes、Decisions-so-far 和 Fog。
- **Child Ticket**：优先使用 GitHub sub-issue；不可用时，在 map body 使用 task list，并在 child body 引用 map。
- **Blocking**：优先使用 GitHub 原生 issue dependencies；不可用时回退到正文 blocker 表达。
- **Claim**：Wayfinder 可以把 child Ticket assign 给驱动它的 dev。Ralph backlog 不使用 assignee claim。
- **Resolve**：评论结果、关闭 child，并在 map 的 Decisions-so-far 中追加 context pointer。
