---
name: setup-matt-pocock-skills-lqy
description: 使用固定 LQY 默认值配置当前 GitHub 仓库的 issue tracker、triage labels 和领域文档。首次使用其他工程 skills 前运行一次。
---

# 设置 Matt Pocock Skills

直接应用以下默认值，不访谈、不提供选项：

- GitHub Issues 是唯一 request、triage 和 Ralph backlog 入口；PR 只走正常 review。
- labels 固定为 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。
- 单 context：根目录 `CONTEXT.md` + `docs/adr/`。
- 使用中文文档和根目录 `AGENTS.md`。

需要其他 tracker、label、multi-context 或 Claude-first 布局时，停止并改用 upstream `setup-matt-pocock-skills`；不要扩展本 skill。

## 1. 验证仓库

读取 `git remote -v`、`.git/config`、`AGENTS.md`、`docs/agents/` 和 `.gitignore`。

- 没有 GitHub remote 时停止。
- 存在 `CONTEXT-MAP.md` 时停止；它需要 multi-context setup。
- 不要求用户确认默认值。

## 2. 写入配置

在根目录 `AGENTS.md` 中创建或就地更新唯一的 `## Agent skills` 区块，保留其他内容：

```markdown
## Agent skills

### Issue tracker

GitHub Issues only；PR 不进入 triage 或 Ralph。见 `docs/agents/issue-tracker.md`。

### Triage labels

使用 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。见 `docs/agents/triage-labels.md`。

### Domain docs

单 context：根目录 `CONTEXT.md` + `docs/adr/`。见 `docs/agents/domain.md`。
```

从本 skill 的模板创建或更新以下 setup-owned 文档；保留无冲突的项目补充说明：

- [issue-tracker-github.md](issue-tracker-github.md) → `docs/agents/issue-tracker.md`
- [triage-labels.md](triage-labels.md) → `docs/agents/triage-labels.md`
- [domain.md](domain.md) → `docs/agents/domain.md`

确保 `.gitignore` 包含以下规则。只追加缺失项，不重排现有内容：

```gitignore
.ralph/
AGENTS.md
.claude/
CLAUDE.md
```

## 3. 验证并报告

确认三个文档存在、`AGENTS.md` 只有一个 `## Agent skills` 区块、PR policy 为 Issues-only，且 `.gitignore` 包含四条规则。报告修改过的文件和已应用的默认值。
