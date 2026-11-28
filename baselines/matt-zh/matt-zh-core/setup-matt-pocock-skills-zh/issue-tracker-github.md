# issue tracker：GitHub

此仓库的 issue 和 spec 存放在 GitHub Issues 中。使用 `gh` CLI 进行所有操作。

## 惯例

- **创建问题**：`gh issue create --title "..." --body "..."`。对多行体使用定界符。
- **阅读问题**：`gh issue view <number> --json number,title,body,labels,comments`。
- **列出问题**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，带有适当的 `--label` 和 `--state` 过滤器。
- **把 issue 设为父 issue 的 sub-issue**：使用 `gh issue create --parent <parent> ...`，或事后执行 `gh issue edit <parent> --add-sub-issue <child>`（`gh` 2.94+）。旧版 `gh`：使用 `gh api --method POST repos/<owner>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>`（database id，见下文 **Blocking**）。不支持 sub-issues 时，在 child body 顶部写 `Part of #<parent>`。
- **Blocking**：GitHub 的**原生 issue dependencies** 是规范且在 UI 中可见的表示。用 `gh issue create --blocked-by <n>,<n> ...` 或 `gh issue edit <child> --add-blocked-by <blocker>`（`gh` 2.94+）添加依赖边。旧版 `gh` 使用 `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`；`<blocker-db-id>` 是 blocker 的数字 **database id**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`），*不是* `#number` 或 `node_id`。若不支持依赖关系，则回退到 child body 顶部的 `Blocked by: #<n>, #<n>` 行。全部 blocker 关闭后，Ticket 才解除阻塞。
- **统计未关闭的 blocker**：`gh api repos/<owner>/<repo>/issues/<n> --jq .issue_dependencies_summary.blocked_by`（仅统计 open blocker；0 表示可开工）。`gh issue view <n> --json blockedBy` 也会列出已关闭的 blocker，因此需要过滤：`--jq '[.blockedBy.nodes[] | select(.state == "OPEN")] | length'`。
- **对问题发表评论**：`gh issue comment <number> --body "..."`
- **应用/删除标签**：`gh issue edit <number> --add-label "..."` / `gh issue edit <number> --remove-label "..."`
- **关闭**：先用 `gh issue comment <number> --body "..."` 发布说明，再运行 `gh issue close <number>`。对于已经关闭的 issue，`gh issue close --comment` 会丢弃评论，却依然以 0 退出。

从 `git remote -v` 推断仓库 — `gh` 在克隆内运行时会自动执行此操作。

只在用户自己的仓库创建 issue。除非用户拥有 `mattpocock/skills`（这些 skills 的来源仓库），否则绝不要往那里创建 issue。在 fork 中，`gh` 可能默认选中上游父仓库；因此，每次会话第一次执行 `gh issue create` 前，使用 `gh repo view --json nameWithOwner` 检查目标，如果不是用户的仓库，就向用户确认。

## 将请求作为 triage 表面

**PR 作为请求表面：否。** _（如果此仓库将外部 PR 视为功能请求，则设置为“yes”；“/triage-zh”读取此标志。）_

当设置为“yes”时，PR 会使用与问题相同的标签和状态，使用“gh pr”等效项：

- **阅读 PR**：先运行 `gh pr view <number>`，再运行 `gh pr view <number> --comments`（非 TTY 下 `--comments` 只打印评论，不打印正文），并用 `gh pr diff <number>` 获取 diff。
- **列出外部 PR 进行 triage**：`gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`。
- **评论/标签/关闭**：`gh pr comment <number> --body "..."`、`gh pr edit <number> --add-label "..."` / `gh pr edit <number> --remove-label "..."`、`gh pr close <number>`。

GitHub 在问题和 PR 之间共享一个数字空间，因此裸露的 `#42` 可能是其中之一 - 使用 `gh pr view 42` 解析并回退到 `gh issue view 42`。

## 当技能说“发布到 issue tracker”时

创建 GitHub 问题。

## 当技能说“获取相关 ticket”时

按上面的 **阅读问题** 方式获取。

## Wayfinding operations

由 `/wayfinder-zh` 使用。**map** 是一个单独 issue，带有作为 Ticket 的 **child** issues。

- **Map**：一个带 `wayfinder:map` 标签的 issue，正文保存 Notes / Decisions-so-far / Fog。使用 `gh issue create --label wayfinder:map`。
- **Child Ticket**：作为 GitHub sub-issue 链接到 map 的 issue（见 **把 issue 设为父 issue 的 sub-issue**）。如果未启用 sub-issues，就把 child 加入 map body 的 task list，并在 child body 顶部写 `Part of #<map>`。Labels：`wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）。被 claim 后，把 Ticket assign 给驱动它的 dev。
- **Blocking**：见上文**惯例**中的 **Blocking**。
- **Frontier query**：列出 map 的 open children（`gh issue list --state open`，scope 到 map 的 sub-issues / task list），丢掉有 open blocker 的项（见**统计未关闭的 blocker**，或 `Blocked by` 行里有 open issue）或已有 assignee 的项；map 顺序里的第一个胜出。
- **Claim**：`gh issue edit <n> --add-assignee @me`，这是该会话的第一个 write。
- **Resolve**：`gh issue comment <n> --body "<answer>"`，然后 `gh issue close <n>`，再向 map 的 Decisions-so-far 追加 context pointer（gist + link）。
