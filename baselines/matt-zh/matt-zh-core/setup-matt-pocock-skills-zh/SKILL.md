---
name: setup-matt-pocock-skills-zh
description: 为工程 Skill 配置仓库的 Issue tracker、triage 标签与领域文档布局。首次使用其他工程 Skill 前运行一次。
disable-model-invocation: true
---

# 配置 Matt Pocock Skills

搭建工程 Skill 假定存在的每仓库配置：

- **Issue tracker**：Issue 所在处（默认 GitHub；本地 Markdown 开箱即用）。
- **Triage 标签**：五种规范 triage 角色对应的字符串。
- **领域文档**：`GLOSSARY.md` 和 ADR 的位置，以及使用方的读取规则。

本 Skill 由提示词驱动，不是确定性脚本：探索、展示发现、与用户确认，最后写入。

## 流程

### 1. 探索

查看仓库现状。只根据实际文件判断，不要臆测：

- `git remote -v` 和 `.git/config`：是否为 GitHub 仓库？对应哪个仓库？
- 根目录的 `AGENTS.md`、`CLAUDE.md`：存在吗？是否已有 `## Agent skills`？
- 根目录的 `GLOSSARY.md`、`GLOSSARY-MAP.md`。
- `docs/adr/` 和所有 `src/*/docs/adr/` 目录。
- `docs/agents/`：此前是否已运行过本 Skill？
- `.scratch/`：是否已有本地 Markdown Issue tracker 约定？
- 是否安装 `triage-zh` Skill？检查同级目录或可用 Skill 列表；由此决定是否执行 B 节。
- Monorepo 信号：`pnpm-workspace.yaml`、`package.json` 中的 `workspaces`，或已有自身 `src/` 的 `packages/*`。只有真正的大型多 package 仓库才有这些信号；没有则按单上下文处理，绝大多数仓库都如此。

### 2. 展示发现并提问

总结已有和缺失的配置，然后按顺序处理下列章节：一次一节，每节等用户回答后再进入下一节。**先给建议答案**，用户可以用一个词接受。只有选择确有分支时才附一句解释；若探索已消除某节的选择，则跳过该节（未安装 `triage-zh` 时跳过 B；没有 monorepo 时跳过 C 的提问）。

**A：Issue tracker。**

> Issue tracker 是仓库实际存放 Issue 的地方。`to-tickets-zh`、`triage-zh` 与 `to-spec-zh` 会读写它：需要知道是运行 `gh issue create`、在 `.scratch/` 下写 Markdown，还是遵循其他流程。请选择实际使用的工作跟踪位置。

默认倾向 GitHub：Git remote 指向 GitHub 时推荐 GitHub；指向 GitLab（`gitlab.com` 或自托管）时推荐 GitLab。否则或用户另有偏好时提供：

- **GitHub**：仓库的 GitHub Issues，使用 `gh` CLI。
- **GitLab**：仓库的 GitLab Issues，使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI。
- **本地 Markdown**：仓库 `.scratch/<feature>/` 下的文件，适合个人项目或没有 remote 的仓库。
- **其他**（Jira、Linear 等）：请用户用一段话描述流程，作为自由文本记录。

将选择记入 `docs/agents/issue-tracker.md`。GitHub/GitLab 模板包含“PR 作为请求入口”开关，默认**关闭**。保持关闭，不主动向用户提出此选择；想将外部 PR 纳入 triage 队列的用户之后可以自行修改文件。

**B：Triage 标签。**若未安装 `triage-zh`，完全跳过；未安装的 Skill 不需要标签。否则只问一个问题：

> 是否保留默认 triage 标签？（建议：**是**）

默认五种规范角色，每个标签字符串与其名称相同：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。同意则照写；仅当用户回答“不”（通常因为 tracker 已使用 `bug:triage` 之类的替代名称），才收集覆盖映射，以免 `triage-zh` 创建重复标签。

**C：领域文档。**默认**单上下文**：仓库根目录一个 `GLOSSARY.md` 加 `docs/adr/`。绝大多数仓库适用，直接写入，无需提问。仅当探索发现 monorepo 信号时，才提供**多上下文**选项（根目录 `GLOSSARY-MAP.md` 指向各上下文自己的 `GLOSSARY.md`），并请用户确认所选布局。

### 3. 确认并编辑

向用户展示以下草稿：

- 将加入所选 `CLAUDE.md` / `AGENTS.md` 的 `## Agent skills` 块（文件选择见步骤 4）。
- `docs/agents/issue-tracker.md`、`docs/agents/domain.md`，以及只在安装 `triage-zh` 时才有的 `docs/agents/triage-labels.md`。

写入前允许用户修改。

### 4. 写入

**选择要编辑的文件：**有 `CLAUDE.md` 就编辑它；否则若有 `AGENTS.md` 就编辑它；两者都没有时询问用户创建哪一个，不代选。不能在已有 `CLAUDE.md` 时新建 `AGENTS.md`，反之亦然。若已有 `## Agent skills`，就地更新，不重复追加；保留其他章节中的用户改动。

区块形式：

```markdown
## Agent skills

### Issue tracker

[一行说明 Issue 跟踪位置]。参见 `docs/agents/issue-tracker.md`。

### Triage labels

[一行说明标签词汇]。参见 `docs/agents/triage-labels.md`。

### Domain docs

[一行说明是单上下文还是多上下文]。参见 `docs/agents/domain.md`。
```

**仅当已安装 `triage-zh` 且执行 B 节时**才包含 `### Triage labels` 子块并写 `docs/agents/triage-labels.md`，否则两者都省略。在 GitHub 或 GitLab 执行过 B 节后，用 `gh label create` / `glab label create` 创建尚不存在的已配置标签。

以本 Skill 目录的模板为起点，编写这些文档：

- [issue-tracker-github.md](./issue-tracker-github.md)：GitHub Issue tracker。
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md)：GitLab Issue tracker。
- [issue-tracker-local.md](./issue-tracker-local.md)：本地 Markdown Issue tracker。
- [triage-labels.md](./triage-labels.md)：标签映射。
- [domain.md](./domain.md)：领域文档读取规则与布局。

对于“其他” tracker，根据用户说明从头编写 `docs/agents/issue-tracker.md`。

### 5. 完成

告诉用户配置完成，说明哪些工程 Skill 会读取这些文件。用户之后可直接编辑 `docs/agents/*.md`；只有想换 tracker 或重头配置时才需重新运行此 Skill。
