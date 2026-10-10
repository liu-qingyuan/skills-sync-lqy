---
name: setup-matt-pocock-skills-lqy
disable-model-invocation: true
description: 使用固定 LQY 默认值配置当前 GitHub 仓库的 issue tracker、triage labels、领域文档与 Feature 微文档门禁。首次使用其他工程 skills 前显式运行。
---

# 设置 Matt Pocock Skills

直接应用以下默认值，不访谈、不提供选项：

- GitHub Issues 是唯一 request、triage 和 Ralph backlog 入口；PR 只走正常 review。
- labels 固定为 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。
- 单 context：新项目根目录 `GLOSSARY.md` + `docs/adr/`；既有项目保留明确配置的同一份术语表。
- 使用中文文档和根目录 `AGENTS.md`。

需要其他 tracker、label、multi-context 或 Claude-first 布局时，停止并改用 upstream `setup-matt-pocock-skills`；不要扩展本 skill。

## 1. 验证仓库

读取 `git remote -v`、`.git/config`、`AGENTS.md`、`docs/agents/` 和 `.gitignore`。

- 没有 GitHub remote 时停止。
- 存在 `GLOSSARY-MAP.md` 或未迁移的 `CONTEXT-MAP.md` 时停止；它需要 multi-context setup。
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

单 context：根目录 `GLOSSARY.md` + `docs/adr/`。见 `docs/agents/domain.md`。

### Feature records

若已有 `.feature-docs/run`，任务开始先读 `./.feature-docs/run list`，再按需读相关页面；同步当前事实，交付前通过记录检查。见 `docs/agents/feature-docs.md`。

### Workflow

规划阶段结束后只提示下一步，等待用户明确调用；确认规划不等于授权实施。实施指定 Ticket 或启动 Ralph 须有用户明确授权；规划阶段的子 agent 仅可只读查证或审查，不能实施。
```

先读取既有 Domain docs pointer；若指定旧 `CONTEXT.md`，或未配置但仅有该文件，保留其路径并替换上述示例及 domain 模板中的默认路径。不得自动迁移或双写术语表。

从本 skill 的模板创建或更新以下 setup-owned 文档；保留无冲突的项目补充说明：

- [issue-tracker-github.md](issue-tracker-github.md) → `docs/agents/issue-tracker.md`
- [triage-labels.md](triage-labels.md) → `docs/agents/triage-labels.md`
- [domain.md](domain.md) → `docs/agents/domain.md`
- [feature-docs.md](feature-docs.md) → `docs/agents/feature-docs.md`

确保 `.gitignore` 包含以下规则。只追加缺失项，不重排现有内容：

```gitignore
.ralph/
AGENTS.md
.claude/
CLAUDE.md
```

## 3. Feature 记录门禁

读取并执行 [feature-docs.md](feature-docs.md)；用本 skill 的 [scripts/feature_docs.py](scripts/feature_docs.py) 在当前 worktree 显式安装。先选一个真实能力按代码/测试 globs 纳管，用 [templates/feature.md](templates/feature.md) 核对事实。保留项目记录；hooks 或安装资产冲突即停止并报告。

安装后 `list` / `check` 必须通过，确认 `core.hooksPath` 有效；代码、测试、记录和门禁资产一起提交。尚无可确认能力/测试入口或有冲突时明确报告门禁未启用，不捏造完成状态。业务测试仍运行项目已有命令，不强制 unittest。

## 4. 标签与验证

只有用户明确执行此 setup 时，读取 GitHub 现有标签并用 `gh label create` 补齐上述五个固定标签中缺失的项；不删除、重命名或覆盖已有标签，不顺手标记 issues 或启动 Ralph。创建失败时说明权限或错误，不擅自改 token / 凭据配置。

确认四个约定文档存在、`AGENTS.md` 只有一个 `## Agent skills` 区块、PR policy 为 Issues-only，且 `.gitignore` 包含四条规则。报告修改文件、门禁是否真正启用及其纳管范围；不将指纹一致报告成业务测试通过。
