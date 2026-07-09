# issue tracker：GitLab

此仓库的issue 和 PRD 作为 GitLab 问题存在。使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI 进行所有操作。

## 惯例

- **创建问题**：`glab issue create --title "..." --description "..."`。使用 heredoc 进行多行描述。通过 `--description -` 打开编辑器。
- **阅读问题**：`glab issue view <number> --comments`。使用 `-F json` 获得机器可读的输出。
- **列出问题**：`glab issue list -F json`，带有适当的 `--label` 过滤器。
- **对问题发表评论**：`glab issue note <number> --message "..."`。GitLab 将评论称为 notes。
- **应用/删除标签**：`glab issue update <number> --label "..."` / `glab issue update <number> --unlabel "..."`。多个标签可以用逗号分隔或通过重复标志来分隔。
- **关闭**：`glab issue close <number>`。`glab issue close` 不接受结束评论，因此首先使用 `glab issue note <number> --message "..."` 发布解释，然后关闭。
- **合并请求**：GitLab 将 PR 称为“合并请求”。使用 `glab mr create`、`glab mr view`、`glab mr note` 等——与 `gh pr ...` 形状相同，用 `mr` 代替 `pr`，用 `note`/`--message` 代替 `comment`/`--body`。

从 `git remote -v` 推断仓库 — `glab` 在克隆内运行时会自动执行此操作。

## 合并请求作为 triage 表面

**MR 作为请求表面：否。** _（如果此仓库将外部合并请求视为功能请求，则设置为“yes”；“/triage-zh”读取此标志。）_

当设置为“yes”时，MR 会使用“glab mr”等效项运行与问题相同的标签和状态：

- **阅读 MR**：`glab mr view <number> --comments` 和 `glab mr diff <number>` 进行比较。
- **列出外部 MR 进行 triage**：`glab mr list -F json`，然后仅保留作者不是项目成员/所有者的 MR（贡献者的 MR，而不是维护者的正在进行的工作）。
- **评论/标签/关闭**：`glab mr note <number> --message "..."`、`glab mr update <number> --label "..."` / `glab mr update <number> --unlabel "..."`、`glab mr close <number>`。

与 GitHub 不同，GitLab 分别对问题和 MR 进行编号，因此一旦您知道维护者指的是哪个表面，`#42` 就明确无误。

## 当技能说“发布到 issue tracker”时

创建一个 GitLab 问题。

## 当技能说“获取相关 ticket”时

运行 `glab issue view <number> --comments`。

## Wayfinding operations

由 `/wayfinder-zh` 使用。**map** 是一个单独 issue，带有作为 Ticket 的 **child** issues。

- **Map**：一个带 `wayfinder:map` 标签的 issue，正文保存 Notes / Decisions-so-far / Fog。使用 `glab issue create --label wayfinder:map`。（在支持 native epics 的 GitLab tier 上，也可以用 epic 保存 map；带标签的 issue 到处都能用。）
- **Child Ticket**：description 顶部带 `Part of #<map>` 的 issue，并带 `wayfinder:<type>` labels（`research`/`prototype`/`grilling`/`task`）。被 claim 后，把 Ticket assign 给驱动它的 dev。
- **Blocking**：GitLab 原生 blocking link，是 canonical 且 UI 可见的表示。通过 `/blocked_by #<n>` quick action 添加，把它作为 note 发布：`glab issue note <child> --message "/blocked_by #<blocker>"`。原生 blocking links 是 Premium/Ultimate 功能；free tier 或不可用时，回退到 description 顶部的 `Blocked by: #<n>, #<n>` 行。每个 blocker 都关闭后，Ticket 才 unblocked。
- **Frontier query**：`glab issue list -F json` scope 到 map 的 children，丢掉有 open blocker 的项（指向 open issue 的 native `blocked_by` link，可通过 `glab api projects/:id/issues/:iid/links` 查看；或 `Blocked by` 行里的 open issue）或已有 assignee 的项；map 顺序里的第一个胜出。
- **Claim**：`glab issue update <n> --assignee @me`，这是该会话的第一个 write。
- **Resolve**：`glab issue note <n> --message "<answer>"`，然后 `glab issue close <n>`，再向 map 的 Decisions-so-far 追加 context pointer（gist + link）。
