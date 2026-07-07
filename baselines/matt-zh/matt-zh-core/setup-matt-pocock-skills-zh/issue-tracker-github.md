# issue tracker：GitHub

此仓库的issue 和 PRD 作为 GitHub 问题存在。使用 `gh` CLI 进行所有操作。

## 惯例

- **创建问题**：`gh issue create --title "..." --body "..."`。对多行体使用定界符。
- **阅读问题**：`gh issue view <number> --comments`，通过 `jq` 过滤评论并获取标签。
- **列出问题**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，带有适当的 `--label` 和 `--state` 过滤器。
- **对问题发表评论**：`gh issue comment <number> --body "..."`
- **应用/删除标签**：`gh issue edit <number> --add-label "..."` / `gh issue edit <number> --remove-label "..."`
- **关闭**：`gh issue close <number> --comment "..."`

从 `git remote -v` 推断仓库 — `gh` 在克隆内运行时会自动执行此操作。

## 将请求作为 triage 表面

**PR 作为请求表面：否。** _（如果此仓库将外部 PR 视为功能请求，则设置为“yes”；“/triage-zh”读取此标志。）_

当设置为“yes”时，PR 会使用与问题相同的标签和状态，使用“gh pr”等效项：

- **阅读 PR**：`gh pr view <number> --comments` 和 `gh pr diff <number>` 以获取差异。
- **列出外部 PR 进行 triage**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`，然后仅保留 `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR`或`NONE` 的 `authorAssociation`（删除 `OWNER`/`MEMBER`/`COLLABORATOR`）。
- **评论/标签/关闭**：`gh pr comment <number> --body "..."`、`gh pr edit <number> --add-label "..."` / `gh pr edit <number> --remove-label "..."`、`gh pr close <number>`。

GitHub 在问题和 PR 之间共享一个数字空间，因此裸露的 `#42` 可能是其中之一 - 使用 `gh pr view 42` 解析并回退到 `gh issue view 42`。

## 当技能说“发布到 issue tracker”时

创建 GitHub 问题。

## 当技能说“获取相关 ticket”时

运行 `gh issue view <number> --comments`。
