# Matt Pocock 中文 skills 本地化

本仓库同时维护两套 Matt Pocock skills：

1. **Official mirror**：英文官方上游镜像，保留 Matt Pocock 原仓库的目录结构，用于持续同步上游。
2. **中文本地化版**：以 `-zh` 结尾的本地化 fork，可按中文团队习惯继续修改。

## 命名与目录

中文版本统一使用 `-zh` 后缀：

- `tdd` → `tdd-zh`
- `triage` → `triage-zh`
- `handoff` → `handoff-zh`
- `setup-matt-pocock-skills` → `setup-matt-pocock-skills-zh`

目录分组：

```text
skills/matt-zh-core/          # engineering + productivity 的中文主力版
skills/matt-zh-personal/      # personal 中文版
skills/matt-zh-misc/          # misc 中文版
skills/matt-zh-in-progress/   # in-progress 中文版
skills/matt-zh-deprecated/    # deprecated 中文版
```

## 本地化策略

- 第一版采用机器辅助的严格中文翻译基线：尽量保留上游流程、结构、检查点和文件约定。
- `SKILL.md` 的 `name` 改成 `<upstream-name>-zh`，避免与官方英文版冲突。
- `description` 用中文描述触发场景，方便 Codex 自动选择中文版本。
- 支持文件中的 Markdown 尽量翻译；脚本文件保持原样。
- 上游示例中的项目路径（例如 `./src/.../CONTEXT.md`）是说明性示例，不要求在本 skill 仓库内真实存在。
- 每个中文 skill 包含 `LOCALIZATION.md`，记录对应上游路径和维护策略。

## 维护规则

更新 Matt 上游时：

1. 先同步英文 official mirror。
2. 记录新的上游 commit。
3. 对比上游变化和当前中文 `*-zh` 版本。
4. 把上游新增或修改的流程合并进中文版本。
5. 如果中文版本已有本地优化，优先保留本地意图，再吸收上游变化。
6. 不要用英文上游直接覆盖中文版本。

## 当前中文版本清单

### Core

- `ask-matt-zh`
- `codebase-design-zh`
- `diagnosing-bugs-zh`
- `domain-modeling-zh`
- `grill-with-docs-zh`
- `implement-zh`
- `improve-codebase-architecture-zh`
- `prototype-zh`
- `resolving-merge-conflicts-zh`
- `setup-matt-pocock-skills-zh`
- `tdd-zh`
- `to-issues-zh`
- `to-prd-zh`
- `triage-zh`
- `grill-me-zh`
- `grilling-zh`
- `handoff-zh`
- `teach-zh`
- `writing-great-skills-zh`

### Personal

- `edit-article-zh`
- `obsidian-vault-zh`

### Misc

- `git-guardrails-claude-code-zh`
- `migrate-to-shoehorn-zh`
- `scaffold-exercises-zh`
- `setup-pre-commit-zh`

### In Progress

- `decision-mapping-zh`
- `loop-me-zh`
- `review-zh`
- `writing-beats-zh`
- `writing-fragments-zh`
- `writing-shape-zh`

### Deprecated

- `design-an-interface-zh`
- `qa-zh`
- `request-refactor-plan-zh`
- `ubiquitous-language-zh`
