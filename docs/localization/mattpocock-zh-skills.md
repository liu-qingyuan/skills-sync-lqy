# Matt Pocock 中文 baseline 与 LQY skills 维护

本仓库维护三层 Matt Pocock skills：

1. **Official mirror**：英文官方上游镜像，保留 Matt Pocock 原仓库的目录结构，放在 `upstream/mattpocock/skills/`，只用于持续同步上游，不参与安装展示。
2. **中文 baseline**：以 `-zh` 结尾的本地化基线，放在 `baselines/matt-zh/`，用于翻译、对比和合并上游变化，不参与安装展示。
3. **LQY 安装版**：以 `-lqy` 结尾的个人版，放在 `skills/matt-lqy-*/*-lqy`，是 `npx skills@latest add liu-qingyuan/skills-sync-lqy` 当前展示的 Matt 层。

当前来源：active 镜像和 baseline 对齐 `49dd158d1076134a641b33efb035946536778336`，LQY 本轮审阅同此 commit；8 个 Frozen legacy 仍来自 `d574778f94cf620fcc8ce741584093bc650a61d3`。镜像与 baseline 各 46（active 38 + legacy 8），安装 Matt LQY 38（原 35 + `pr`、`retro`、`writing-for-agents`）；全部可安装 53（另有本地/精选/UI 15）。以每项 mirror `UPSTREAM_MATTOCOCK.md` 的 Status/Source commit 为准。本轮复查晚到的 `8267225` 和 `49dd158`：仅涉及未安装的 Wizard 模板及 retro 的 out-of-scope 说明；安装版 retro 已始终加载 writing-for-agents。

## 命名与目录

命名链路：

- `tdd` → `tdd-zh` → `tdd-lqy`
- `triage` → `triage-zh` → `triage-lqy`
- `handoff` → `handoff-zh` → `handoff-lqy`
- `setup-matt-pocock-skills` → `setup-matt-pocock-skills-zh` → `setup-matt-pocock-skills-lqy`

目录分组：

```text
baselines/matt-zh/matt-zh-core/          # engineering + productivity 的中文 baseline
baselines/matt-zh/matt-zh-personal/      # personal 中文 baseline
baselines/matt-zh/matt-zh-misc/          # misc 中文 baseline
baselines/matt-zh/matt-zh-in-progress/   # in-progress 中文 baseline
baselines/matt-zh/matt-zh-deprecated/    # deprecated 中文 baseline

skills/matt-lqy-core/                    # engineering + productivity 的可安装 LQY 版
skills/matt-lqy-personal/                # personal 可安装 LQY 版
skills/matt-lqy-misc/                    # misc 可安装 LQY 版
skills/matt-lqy-in-progress/             # in-progress 可安装 LQY 版
skills/matt-lqy-deprecated/              # deprecated 可安装 LQY 版
```

## 本地化策略

- 中文 baseline 采用机器辅助的严格中文翻译基线：尽量保留上游流程、结构、检查点和文件约定。
- LQY 安装版从对应中文 baseline 起步，但必须完整自包含，安装后不能依赖 `baselines/`。
- `SKILL.md` 的 `name` 必须等于目录名：baseline 用 `<upstream-name>-zh`，安装版用 `<upstream-name>-lqy`。
- `description` 用中文描述触发场景；Pi 显式调用策略使用 `disable-model-invocation`，Codex 使用 `agents/openai.yaml` policy 并保持同步。本仓库 validator 支持这些 metadata，不能再以系统 `quick_validate.py` 为由省略 flags。
- 支持文件中的 Markdown 尽量翻译；脚本文件保持原样。
- 每个 LQY skill 的 `LOCALIZATION.md` 必须同时记录官方 upstream path 和中文 baseline path，并区分原始导入的 Source commit 与本轮 Upstream reviewed commit；后者不表示定制正文逐字来自新源。Frozen legacy 保留原 source，不自动删除；旧个人 skills 仍可显式调用。
- 新项目 `GLOSSARY.md` 是术语表；旧项目若已明确配置单一 `CONTEXT.md` 则保留该配置。Baseline 忠实翻译上游，不回填 LQY/Ralph 定制；安装版 `implement-lqy` 允许已授权的 Ralph worker 加载，但批量调度仍由 Ralph 负责。

## 维护规则

更新 Matt 上游时：

1. 先同步英文 official mirror。
2. 记录新的上游 commit。
3. 对比上游变化和当前中文 `*-zh` baseline。
4. 把上游新增或修改的流程合并进中文 baseline。
5. 再检查对应 `*-lqy` 安装版是否需要适配。
6. 如果 LQY 版本已有本地优化，优先保留本地意图，再吸收 upstream / baseline 变化。
7. 不要用英文上游直接覆盖中文 baseline 或 LQY 安装版。
8. 输出同步报告：上游哪些地方变了、中文 baseline 如何处理、LQY 安装版是否已适配或需要人工审核。

## 当前 LQY 安装版清单

### Core

- `ask-matt-lqy`
- `code-review-lqy`
- `codebase-design-lqy`
- `diagnosing-bugs-lqy`
- `domain-modeling-lqy`
- `grill-with-docs-lqy`
- `implement-lqy`
- `pr-lqy`
- `improve-codebase-architecture-lqy`
- `prototype-lqy`
- `retro-lqy`
- `resolving-merge-conflicts-lqy`
- `setup-matt-pocock-skills-lqy`
- `tdd-lqy`
- `to-tickets-lqy`
- `to-spec-lqy`
- `triage-lqy`
- `wayfinder-lqy`
- `grill-me-lqy`
- `grilling-lqy`
- `handoff-lqy`
- `teach-lqy`
- `writing-for-agents-lqy`
- `writing-great-skills-lqy`

### Personal

- `edit-article-lqy`
- `obsidian-vault-lqy`

### Misc

- `git-guardrails-claude-code-lqy`
- `migrate-to-shoehorn-lqy`
- `scaffold-exercises-lqy`
- `setup-pre-commit-lqy`

### In Progress

- `loop-me-lqy`
- `writing-beats-lqy`
- `writing-fragments-lqy`
- `writing-shape-lqy`

### Deprecated (Frozen legacy; explicitly invocable, never automatically deleted)

- `design-an-interface-lqy`
- `qa-lqy`
- `request-refactor-plan-lqy`
- `ubiquitous-language-lqy`

此外 `resolving-merge-conflicts-lqy`、`writing-great-skills-lqy`、`edit-article-lqy`、`obsidian-vault-lqy` 也是 Frozen legacy。`wizard` 的 mirror 位于 engineering、baseline 位于 core，但无 LQY 安装版；`chief-of-staff`、`implement-spec` 也不安装。