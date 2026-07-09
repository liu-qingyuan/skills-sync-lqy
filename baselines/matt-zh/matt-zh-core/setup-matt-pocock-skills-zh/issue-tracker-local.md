# issue tracker：本地 Markdown

此仓库的issue 和 PRD 以Markdown 文件形式存在于“.scratch/”中。

## 惯例

- 每个目录一个功能：`.scratch/<feature-slug>/`
- PRD 是 `.scratch/<feature-slug>/PRD.md`
- 实现问题是`.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从`01`开始编号
- triage 状态记录为每个 issue 文件顶部附近的“状态：”行（有关 role 字符串，请参阅 `triage-labels.md`）
- 评论和对话历史记录附加到文件底部的“## Comments”标题下

## 当技能说“发布到 issue tracker”时

在 `.scratch/<feature-slug>/` 下创建一个新文件（如果需要，创建目录）。

## 当技能说“获取相关 ticket”时

读取引用路径中的文件。用户通常会直接传递路径或问题编号。

## Wayfinding operations

由 `/wayfinder-zh` 使用。**map** 是一个文件，每个 Ticket 是一个 **child** 文件。

- **Map**：`.scratch/<effort>/map.md`，保存 Notes / Decisions-so-far / Fog。
- **Child Ticket**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 开始编号，正文里写 question。`Type:` 行记录 Ticket type（`research`/`prototype`/`grilling`/`task`）；`Status:` 行记录 `claimed`/`resolved`。
- **Blocking**：顶部附近的 `Blocked by: NN, NN` 行。它列出的每个文件都是 `resolved` 后，Ticket 才 unblocked。
- **Frontier**：扫描 `.scratch/<effort>/issues/`，找出 open、unblocked、unclaimed 的文件；按编号第一个胜出。
- **Claim**：把 `Status:` 设为 `claimed` 并保存，之后再做任何工作。
- **Resolve**：在 `## Answer` heading 下追加答案，把 `Status:` 设为 `resolved`，然后向 `map.md` 的 Decisions-so-far 追加 context pointer（gist + link）。
